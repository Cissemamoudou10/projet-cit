"""Indisponibilités d'instructeur — CU-P4-03, RG-23, RG-24, Prompt 27.

RG-24 : deux périodes sécantes d'un même instructeur ne sont JAMAIS
refusées — le système PROPOSE leur fusion (E2), l'inverse de RG-14
(`SalleAttitree`, US-SES-03) et du refus d'`IndisponibiliteLieu` : un
chevauchement ici n'est pas une erreur de saisie, c'est le signe que la
même absence arrive par deux canaux ou qu'une mission s'est prolongée. Voir
docs/suivi/DECISIONS.md pour pourquoi les deux règles voisines divergent.

Même figure qu'à US-SES-05/06 : une proposition qui n'écrit rien (§ 3,
point 2-3), une confirmation qui revalide intégralement et écrit en une
seule transaction (point 4) — la contrainte d'exclusion en base
(`ex_indispo_instructeur_chevauchement`) reste le juge final, cette
détection en amont ne sert qu'à produire un message exploitable (E2 exige
de nommer les périodes concernées).
"""

import datetime
from dataclasses import dataclass

from django.db import IntegrityError, transaction
from django.utils import timezone

from administration.habilitations import verifier_habilitation
from administration.models import TypeAction
from administration.services.journal import DonneesEntreeJournal, ServiceJournal
from noyau.exceptions import ErreurIntrouvable, ErreurValidation
from noyau.intervalles import filtre_recouvrement
from noyau.pagination import paginer
from noyau.services.base import ServiceBase
from ressources.models import IndisponibiliteInstructeur, Instructeur

OBJET_TYPE = "indisponibilite_instructeur"
PERMISSION_LECTURE = "noyau.lieux_calendrier_lecture"
PERMISSION_ECRITURE = "noyau.lieux_calendrier_ecriture"


@dataclass(frozen=True)
class PropositionFusion:
    debut: object
    fin: object
    motif: str
    absorbees: tuple
    sans_effet: bool


def _valider_periode(debut, fin, motif):
    if fin <= debut:
        raise ErreurValidation("La fin de l'indisponibilité doit être postérieure au début.")
    if not motif.strip():
        raise ErreurValidation("Le motif de l'indisponibilité est obligatoire.")


def _chevauchements(instructeur, debut, fin, *, exclut_pk=None):
    conflits = instructeur.indisponibilites.filter(filtre_recouvrement("debut", "fin", debut, fin))
    if exclut_pk is not None:
        conflits = conflits.exclude(pk=exclut_pk)
    return list(conflits.order_by("debut"))


def _capturer(indisponibilite):
    return {
        "debut": indisponibilite.debut.isoformat(),
        "fin": indisponibilite.fin.isoformat(),
        "motif": indisponibilite.motif,
    }


def _filtrer_periode(queryset, periode_du, periode_au):
    """Recouvrement avec la fenêtre demandée, jamais confinement : une
    indisponibilité à cheval sur une borne du filtre reste pertinente pour
    qui consulte cette période — même principe que la fenêtre de recherche,
    inverse de `ServiceLieu._filtrer_disponibilite` qui EXCLUT un lieu
    indisponible sur la fenêtre plutôt que de le montrer."""
    if periode_du:
        debut_fenetre = timezone.make_aware(
            datetime.datetime.combine(periode_du, datetime.time.min)
        )
        queryset = queryset.filter(fin__gt=debut_fenetre)
    if periode_au:
        fin_fenetre = timezone.make_aware(
            datetime.datetime.combine(periode_au + datetime.timedelta(days=1), datetime.time.min)
        )
        queryset = queryset.filter(debut__lt=fin_fenetre)
    return queryset


def _analyser(instructeur, debut, fin, motif, *, exclut_pk=None):
    """Pure : ne vérifie aucune habilitation, n'écrit rien. Partagée par
    `proposer` (lecture des droits en amont) et `confirmer` (revalide sans
    faire confiance à la proposition du temps 1)."""
    _valider_periode(debut, fin, motif)
    absorbees = tuple(_chevauchements(instructeur, debut, fin, exclut_pk=exclut_pk))
    if not absorbees:
        return PropositionFusion(debut=debut, fin=fin, motif=motif, absorbees=(), sans_effet=False)
    resultante_debut = min(debut, *(a.debut for a in absorbees))
    resultante_fin = max(fin, *(a.fin for a in absorbees))
    # Sans effet seulement si la nouvelle période est contenue dans UNE
    # SEULE existante (§ 3) — fusionner deux périodes jusque-là distinctes
    # en une seule EST un effet réel, même si les bornes extrêmes ne
    # bougent pas (elles passent de deux lignes à une).
    sans_effet = (
        len(absorbees) == 1
        and resultante_debut == absorbees[0].debut
        and resultante_fin == absorbees[0].fin
    )
    return PropositionFusion(
        debut=resultante_debut,
        fin=resultante_fin,
        motif=motif,
        absorbees=absorbees,
        sans_effet=sans_effet,
    )


class ServiceIndisponibiliteInstructeur:
    DOMAINE = "lieux_calendrier"
    PERMISSION_LECTURE = PERMISSION_LECTURE
    PERMISSION_ECRITURE = PERMISSION_ECRITURE

    @staticmethod
    def obtenir(pk):
        try:
            return IndisponibiliteInstructeur.objects.select_related("instructeur").get(pk=pk)
        except IndisponibiliteInstructeur.DoesNotExist as erreur:
            raise ErreurIntrouvable(f"Indisponibilité introuvable (identifiant {pk}).") from erreur

    @staticmethod
    def lister(agissant, filtres, page):
        """Écran autonome (DECISIONS.md, D-115) : la donnée relève de
        `lieux_calendrier`, cette liste en est l'unique lecture — jamais une
        seconde sur la fiche instructeur (raisonnement D-32/D-111)."""
        verifier_habilitation(agissant, PERMISSION_LECTURE)
        queryset = IndisponibiliteInstructeur.objects.select_related("instructeur").order_by(
            "-debut"
        )
        if filtres.get("instructeur"):
            queryset = queryset.filter(instructeur_id=filtres["instructeur"])
        if filtres.get("motif"):
            queryset = queryset.filter(motif__icontains=filtres["motif"])
        queryset = _filtrer_periode(queryset, filtres.get("periode_du"), filtres.get("periode_au"))
        return paginer(queryset, page)

    @staticmethod
    def choix_instructeurs():
        """Pour le filtre et le champ de sélection de l'écran autonome —
        n'est PAS une lecture du domaine `instructeurs_qualifications` : le
        nom de l'instructeur concerné fait partie de la donnée
        d'indisponibilité elle-même, comme `IndisponibiliteLieu` porte le
        nom du lieu. Voir DECISIONS.md, D-115."""
        return [
            (instructeur.pk, str(instructeur))
            for instructeur in Instructeur.objects.order_by("nom", "prenom")
        ]

    @staticmethod
    def proposer(agissant, instructeur, debut, fin, motif):
        """TEMPS 1 (§ 3) : rien n'est écrit. A4 : aucune borne minimale sur
        `debut` — une période entièrement passée est un cas normal."""
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        if instructeur.archive:
            raise ErreurValidation(
                f"« {instructeur} » est archivé : désarchivez-le avant de saisir une "
                "indisponibilité."
            )
        return _analyser(instructeur, debut, fin, motif)

    @staticmethod
    def confirmer(agissant, instructeur, debut, fin, motif):
        """TEMPS 2 (§ 3, point 4) : revalide intégralement, jamais de
        confiance dans la proposition du temps 1 — une autre saisie a pu
        survenir entre-temps. Tout ou rien : périodes absorbées supprimées,
        période résultante écrite, dans la même transaction."""
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        if instructeur.archive:
            raise ErreurValidation(
                f"« {instructeur} » est archivé : désarchivez-le avant de saisir une "
                "indisponibilité."
            )
        proposition = _analyser(instructeur, debut, fin, motif)
        if proposition.sans_effet:
            raise ErreurValidation(
                "Cette période est déjà entièrement couverte par une indisponibilité "
                "existante : rien à enregistrer."
            )
        try:
            with transaction.atomic():
                for absorbee in proposition.absorbees:
                    _journaliser_absorption(agissant, absorbee)
                    absorbee.delete()
                resultante = IndisponibiliteInstructeur(
                    instructeur=instructeur,
                    debut=proposition.debut,
                    fin=proposition.fin,
                    motif=proposition.motif,
                )
                ServiceBase.creer(resultante, agissant)
                _journaliser_creation(agissant, resultante, fusionnee=bool(proposition.absorbees))
        except IntegrityError as erreur:
            raise ErreurValidation(
                f"« {instructeur} » porte déjà une période qui recouvre celle saisie : "
                "reprenez depuis la proposition."
            ) from erreur
        return resultante

    @staticmethod
    def modifier(agissant, indisponibilite, debut, fin, motif):
        """Modification d'une période existante — bornes et motif, exclue
        d'elle-même dans la recherche de chevauchement. Refuse sur conflit
        avec une AUTRE période plutôt que de proposer une fusion : le
        déroulé de fusion (§ 3) décrit une nouvelle saisie, pas une
        modification ; un chevauchement provoqué par une modification reste
        un cas rare, traité comme `IndisponibiliteLieu.modifier`."""
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        _valider_periode(debut, fin, motif)
        conflits = _chevauchements(
            indisponibilite.instructeur, debut, fin, exclut_pk=indisponibilite.pk
        )
        if conflits:
            conflit = conflits[0]
            raise ErreurValidation(
                f"« {indisponibilite.instructeur} » a déjà une période du "
                f"{conflit.debut:%d/%m/%Y %H:%M} au {conflit.fin:%d/%m/%Y %H:%M} "
                f"({conflit.motif}). Modifiez les bornes saisies."
            )
        avant = _capturer(indisponibilite)
        indisponibilite.debut = debut
        indisponibilite.fin = fin
        indisponibilite.motif = motif
        try:
            with transaction.atomic():
                ServiceBase.modifier(indisponibilite, agissant)
                _journaliser_modification(agissant, indisponibilite, avant)
        except IntegrityError as erreur:
            raise ErreurValidation(
                f"« {indisponibilite.instructeur} » porte déjà une période qui recouvre "
                "celle saisie."
            ) from erreur
        return indisponibilite

    @staticmethod
    def supprimer(agissant, indisponibilite):
        """A2 : la période est supprimée, journalisée — les séances
        antérieurement remplacées NE SONT PAS rétablies automatiquement
        (§ 6, Prompt 27), aucun mécanisme aujourd'hui ne le ferait de toute
        façon (le traitement des séances impactées est hors périmètre,
        US-PLAN-09)."""
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        with transaction.atomic():
            ServiceJournal.enregistrer_detaillee(
                DonneesEntreeJournal(
                    type_action=TypeAction.SUPPRESSION_ELEMENT_GESTION,
                    identifiant_saisi=str(indisponibilite),
                    auteur=agissant,
                    objet_type=OBJET_TYPE,
                    objet_identifiant=str(indisponibilite.pk),
                )
            )
            indisponibilite.delete()


def _journaliser_modification(agissant, indisponibilite, avant):
    ServiceJournal.enregistrer_detaillee(
        DonneesEntreeJournal(
            type_action=TypeAction.MODIFICATION_ELEMENT_GESTION,
            identifiant_saisi=str(indisponibilite),
            auteur=agissant,
            objet_type=OBJET_TYPE,
            objet_identifiant=str(indisponibilite.pk),
            valeur_avant=avant,
            valeur_apres=_capturer(indisponibilite),
        )
    )


def _journaliser_absorption(agissant, absorbee):
    """RG-24 détruit de l'information (les bornes et le motif de la période
    absorbée) : le journal est le seul endroit où elle survit (§ 3)."""
    ServiceJournal.enregistrer_detaillee(
        DonneesEntreeJournal(
            type_action=TypeAction.SUPPRESSION_ELEMENT_GESTION,
            identifiant_saisi=f"Absorbée par fusion — {absorbee}",
            auteur=agissant,
            objet_type=OBJET_TYPE,
            objet_identifiant=str(absorbee.pk),
            valeur_avant=_capturer(absorbee),
        )
    )


def _journaliser_creation(agissant, indisponibilite, *, fusionnee):
    ServiceJournal.enregistrer_detaillee(
        DonneesEntreeJournal(
            type_action=TypeAction.CREATION_ELEMENT_GESTION,
            identifiant_saisi=str(indisponibilite),
            auteur=agissant,
            objet_type=OBJET_TYPE,
            objet_identifiant=str(indisponibilite.pk),
            valeur_apres={**_capturer(indisponibilite), "fusionnee": fusionnee},
        )
    )
