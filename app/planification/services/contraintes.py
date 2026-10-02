"""Contrôle des six contraintes dures — CU-P5-02, RG-34 à RG-39, Prompt 30.

`ServiceContraintes` est l'implantation UNIQUE de ces six règles
(.claude/rules/services.md) : appelé par la modification manuelle, la
génération, le regroupement et la duplication (tous à venir, US-PLAN-03 et
suivantes) — jamais par un utilisateur (§ 6, Prompt 30), donc aucune
habilitation à vérifier ici, contrairement aux services qui répondent à un
écran.

DEUX PROPRIÉTÉS NON NÉGOCIABLES (§ 3, Prompt 30) : le service N'ÉCRIT RIEN
— aucun `.save()`, aucun `.delete()`, nulle part dans ce module ni dans
`regles_*.py` — et il retourne TOUTES les violations, jamais la première
(E2).

CONTRAINTE MUTUELLE D'UN LOT — le point technique central de la story
(§ 3/§ 12) : `verifier_lot` construit le contexte une seule fois puis plie
les candidates dans l'ordre de soumission, chacune contrôlée contre le
contexte ET contre les candidates du même lot DÉJÀ ACCEPTÉES avant elle.
Une candidate refusée n'entre jamais dans cet ensemble provisoire, mais le
lot continue : chaque candidate reçoit son propre verdict, jamais un rejet
en cascade. Ce mécanisme est donc SENSIBLE À L'ORDRE par construction
(le premier arrivé retient le créneau) — à respecter par tout appelant
futur, documenté ici pour que US-PLAN-03 n'ait pas à le redécouvrir.

Limite assumée : RG-38 reste évaluée contre le contexte chargé une fois,
jamais contre le cumul provisoire du lot — un blocage calendaire ne dépend
d'aucun autre placement. RG-34, le sous-cas « lieu occupé/séquentiel » de
RG-37, ET LE VOLET PLAFOND (pas le volet prérequis) de RG-39 tiennent compte
des candidates déjà acceptées du même lot (Prompt 31 § 0.2/point 1 : la
génération place plusieurs séances de la même matière dans la même semaine,
et le plafond doit voir leur cumul provisoire, sans quoi il devient
décoratif — voir `planification.services.regles_volume` et
docs/suivi/DECISIONS.md, D-135).

CONTEXTE PROVISOIRE POUR `verifier` (Prompt 31 § 0.2) : `verifier` accepte un
paramètre `provisoires`, une séquence de `Candidate` déjà retenues par
l'appelant mais pas encore écrites — même mécanisme que `lot_acceptees`,
exposé pour une stratégie qui essaie plusieurs candidates par case avant de
retenir la bonne (contrairement à `verifier_lot`, qui reçoit une liste déjà
tranchée). `verifier(candidate, contexte)` reste valide, `provisoires` vaut
`()` par défaut.
"""

import dataclasses
import datetime

from django.db.models import Count, Q
from django.utils import timezone

from noyau.services.parametres import ResolveurJoursExamen
from organisation.models import Brigade
from planification.models import EtatProgramme, LigneProgramme, ProgrammeHebdomadaire, Seance
from planification.services import regles_calendrier, regles_instructeur, regles_lieu, regles_volume
from referentiel.models import ElementReferentiel, Prerequis
from ressources.models import (
    IndisponibiliteInstructeur,
    IndisponibiliteLieu,
    Instructeur,
    Lieu,
    PeriodeCalendrier,
    Qualification,
)

# Programmes non rejetés : contribuent tous au volume programmé (RG-39 a),
# arbitrage du Prompt 30 § 4 — voir docs/suivi/DECISIONS.md.
ETATS_COMPTABILISES = [etat for etat in EtatProgramme.values if etat != EtatProgramme.REJETE]


@dataclasses.dataclass(frozen=True)
class Candidate:
    """Affectation candidate — § 3, Prompt 30. `cle_regroupement` identifie
    les candidates d'UN MÊME LOT destinées à devenir une seule séance
    regroupée (plusieurs lignes de programme) : deux candidates qui
    partagent cette clé ne se contraignent jamais mutuellement pour RG-34
    ni pour le sous-cas « lieu occupé » de RG-37 — c'est la même figure
    qu'une séance existante à plusieurs lignes (`Seance.est_regroupee`),
    avant que la séance n'existe. `None` (par défaut) signifie « candidate
    isolée », jamais regroupée avec une autre du même lot.
    """

    brigade: Brigade
    element_referentiel: ElementReferentiel
    instructeur: Instructeur
    debut: datetime.datetime
    fin: datetime.datetime
    lieu: Lieu | None = None
    cle_regroupement: object | None = None


@dataclasses.dataclass(frozen=True)
class Contexte:
    """Chargé UNE FOIS par semaine (§ 3, Prompt 30) — jamais une requête
    par règle ni par candidate. Voir `ServiceContraintes.contexte`."""

    programme: ProgrammeHebdomadaire
    semaine_debut: datetime.datetime
    semaine_fin: datetime.datetime
    seances_existantes: list
    qualifications: frozenset
    indisponibilites_instructeur: dict
    indisponibilites_lieu: dict
    periodes_bloquantes: list
    jours_examen: list
    salles_attitrees: dict
    effectifs_reels: dict
    volume_programme_par_element: dict
    volume_programme_par_element_brigade: dict
    prerequis_par_element: dict


@dataclasses.dataclass(frozen=True)
class Verdict:
    accepte: bool
    violations: list


def _semaine(lundi_de_semaine):
    debut = timezone.make_aware(datetime.datetime.combine(lundi_de_semaine, datetime.time.min))
    return debut, debut + datetime.timedelta(days=7)


def _charger_indisponibilites(modele, champ_cible, debut, fin):
    lignes = modele.objects.filter(debut__lt=fin, fin__gt=debut).values_list(
        champ_cible, "debut", "fin"
    )
    resultat = {}
    for cible_id, indispo_debut, indispo_fin in lignes:
        resultat.setdefault(cible_id, []).append((indispo_debut, indispo_fin))
    return resultat


def _charger_periodes_bloquantes(debut, fin):
    periodes = (
        PeriodeCalendrier.objects.filter(effet="bloquant", debut__lt=fin, fin__gt=debut)
        .prefetch_related("sessions", "brigades")
        .distinct()
    )
    resultat = []
    for periode in periodes:
        sessions = {s.pk for s in periode.sessions.all()}
        brigades = {b.pk for b in periode.brigades.all()}
        resultat.append(
            {
                "periode": periode,
                "sessions": sessions,
                "brigades": brigades,
                "centre_entier": not sessions and not brigades,
            }
        )
    return resultat


def _charger_volumes(programme):
    """RG-39 a) : tous les programmes NON REJETÉS, à l'EXCLUSION du
    programme évalué — sans quoi une régénération verrait ses propres
    séances comme un dépassement (arbitrage du Prompt 30 § 4, docs/suivi/
    DECISIONS.md)."""
    lignes = (
        LigneProgramme.objects.filter(seance__programme__etat__in=ETATS_COMPTABILISES)
        .exclude(seance__programme=programme)
        .values("brigade_id", "seance__element_referentiel_id", "seance__debut", "seance__fin")
    )
    par_element: dict = {}
    par_element_brigade: dict = {}
    for ligne in lignes:
        duree = ligne["seance__fin"] - ligne["seance__debut"]
        element_id = ligne["seance__element_referentiel_id"]
        par_element[element_id] = par_element.get(element_id, datetime.timedelta()) + duree
        cle = (element_id, ligne["brigade_id"])
        par_element_brigade[cle] = par_element_brigade.get(cle, datetime.timedelta()) + duree
    return (_en_heures(par_element), _en_heures(par_element_brigade))


def _en_heures(table):
    return {cle: valeur / datetime.timedelta(hours=1) for cle, valeur in table.items()}


def _charger_seances_existantes(programme):
    return list(
        Seance.objects.filter(programme=programme)
        .select_related("instructeur", "lieu", "element_referentiel__matiere")
        .prefetch_related("lignes__brigade")
    )


def _charger_brigades():
    """Salles attitrées et effectifs réels, en une requête chacun — jamais
    une requête par candidate évaluée ensuite."""
    salles_attitrees = {
        brigade.pk: brigade.salle_attitree.lieu
        for brigade in Brigade.objects.filter(salle_attitree__isnull=False).select_related(
            "salle_attitree__lieu"
        )
    }
    effectifs_reels = dict(
        Brigade.objects.annotate(
            effectif_reel=Count(
                "affectations",
                filter=Q(affectations__date_fin__isnull=True, affectations__stagiaire__radie=False),
                distinct=True,
            )
        ).values_list("pk", "effectif_reel")
    )
    return salles_attitrees, effectifs_reels


def _charger_prerequis():
    """Table entière, sans filtrer par élément : le référentiel du centre
    compte quelques dizaines de matières (même hypothèse d'échelle que
    `referentiel.services.prerequis`), la charger en une requête coûte
    moins qu'un filtrage qui risquerait d'oublier un élément."""
    liens = Prerequis.objects.select_related("element_prerequis__matiere")
    resultat: dict = {}
    for lien in liens:
        resultat.setdefault(lien.element_id, []).append(lien.element_prerequis)
    return resultat


class ServiceContraintes:
    DOMAINE = "programme"

    @staticmethod
    def contexte(programme: ProgrammeHebdomadaire) -> Contexte:
        """Un jeu de requêtes borné, indépendant du nombre de candidates
        évaluées ensuite (H6, § 3 Prompt 30)."""
        debut, fin = _semaine(programme.lundi_de_semaine)
        seances_existantes = _charger_seances_existantes(programme)
        qualifications = frozenset(
            Qualification.objects.values_list("instructeur_id", "matiere_id")
        )
        salles_attitrees, effectifs_reels = _charger_brigades()
        volume_par_element, volume_par_element_brigade = _charger_volumes(programme)
        return Contexte(
            programme=programme,
            semaine_debut=debut,
            semaine_fin=fin,
            seances_existantes=seances_existantes,
            qualifications=qualifications,
            indisponibilites_instructeur=_charger_indisponibilites(
                IndisponibiliteInstructeur, "instructeur_id", debut, fin
            ),
            indisponibilites_lieu=_charger_indisponibilites(
                IndisponibiliteLieu, "lieu_id", debut, fin
            ),
            periodes_bloquantes=_charger_periodes_bloquantes(debut, fin),
            jours_examen=ResolveurJoursExamen.resoudre(debut.date(), fin.date()),
            salles_attitrees=salles_attitrees,
            effectifs_reels=effectifs_reels,
            volume_programme_par_element=volume_par_element,
            volume_programme_par_element_brigade=volume_par_element_brigade,
            prerequis_par_element=_charger_prerequis(),
        )

    @staticmethod
    def verifier(candidate: Candidate, contexte: Contexte, provisoires: tuple = ()) -> Verdict:
        """`provisoires` : candidates déjà retenues par l'appelant, pas
        encore écrites (Prompt 31 § 0.2) — une stratégie qui essaie
        plusieurs candidates pour UNE case les y ajoute au fur et à mesure
        de ses acceptations, avant de passer à la case suivante."""
        return ServiceContraintes._verifier_une(candidate, contexte, tuple(provisoires))

    @staticmethod
    def _verifier_une(candidate, contexte, lot_acceptees):
        violations = []
        violations += regles_instructeur.verifier_rg34(candidate, contexte, lot_acceptees)
        violations += regles_instructeur.verifier_rg35(candidate, contexte)
        violations += regles_instructeur.verifier_rg36(candidate, contexte)
        violations += regles_lieu.verifier_rg37(candidate, contexte, lot_acceptees)
        violations += regles_calendrier.verifier_rg38(candidate, contexte)
        violations += regles_volume.verifier_rg39(candidate, contexte, lot_acceptees)
        return Verdict(accepte=not violations, violations=violations)

    @staticmethod
    def verifier_lot(candidates, contexte: Contexte) -> list:
        """A1 : les candidates se contraignent MUTUELLEMENT (voir docstring
        du module). Résultat dans l'ordre de `candidates`."""
        verdicts = []
        lot_acceptees = []
        for candidate in candidates:
            verdict = ServiceContraintes._verifier_une(candidate, contexte, tuple(lot_acceptees))
            verdicts.append(verdict)
            if verdict.accepte:
                lot_acceptees.append(candidate)
        return verdicts
