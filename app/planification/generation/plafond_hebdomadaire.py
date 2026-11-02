"""Plafond hebdomadaire de volume par matière et par brigade — RG-66,
exigence manquante découverte en recette (RECETTE-01, R01-VAL03-03,
prompt 56). Limite ce qu'UNE SEMAINE de génération automatique peut placer
d'une même matière pour une même brigade, à (volume restant ÷ semaines
restantes de la session) × `settings.PLAFOND_HEBDOMADAIRE_COEFFICIENT`,
arrondi au créneau supérieur — recalculé à CHAQUE génération, jamais figé.

Génération SEULEMENT (prompt 56, § 1) : jamais une contrainte dure, jamais
`ServiceContraintes` — une modification manuelle, une substitution ou une
duplication n'est jamais freinée par ce module, qui n'est appelé que par
`generation.gloutonne`. Les séances déjà verrouillées de la semaine
(contrôle ou saisie manuelle) comptent dans le plafond — posées avant la
génération, elles n'empruntent jamais `matieres_programmables`/ce module,
donc ne peuvent structurellement jamais en être refusées.
"""

import dataclasses
import datetime
import math

from django.conf import settings

from planification.generation.candidats import periode_bloquante, projeter_creneaux, volume_restant
from planification.services.contraintes import charger_periodes_bloquantes
from planification.services.temps import duree_creneau_minimale, duree_heures
from referentiel.models import Prerequis


def coefficient() -> float:
    return float(settings.PLAFOND_HEBDOMADAIRE_COEFFICIENT)


def _semaine_entierement_bloquee(brigade, lundi_de_semaine, creneaux, periodes_bloquantes):
    creneaux_projetes = projeter_creneaux(creneaux, lundi_de_semaine)
    return all(
        periode_bloquante(brigade, debut, fin, periodes_bloquantes) is not None
        for debut, fin in creneaux_projetes
    )


def semaines_restantes(brigade, lundi_de_semaine, creneaux, periodes_bloquantes, echeance=None):
    """Nombre de semaines, celle-ci incluse, jusqu'à `echeance` (ou la fin
    de la session de la brigade) — les semaines ENTIÈREMENT bloquées pour
    cette brigade (congé centre entier, bivouac) n'offrent aucune
    opportunité de progression, elles ne comptent pas. Plancher à 1 :
    dernière semaine de la session, génération après sa fin, ou échéance
    déjà dépassée (matière prérequise d'une autre, § 6) — jamais une
    division par zéro ni par un nombre négatif."""
    fin = echeance or brigade.session.date_fin
    semaine, compte = lundi_de_semaine, 0
    while semaine <= fin:
        if not _semaine_entierement_bloquee(brigade, semaine, creneaux, periodes_bloquantes):
            compte += 1
        semaine += datetime.timedelta(weeks=1)
    return max(compte, 1)


def _duree_session_semaines(brigade) -> float:
    jours = (brigade.session.date_fin - brigade.session.date_debut).days
    return max(jours / 7, 1)


def _dependantes_par_element(elements):
    """Matières dont `element` est un prérequis (sens inverse de
    `Contexte.prerequis_par_element`) — `related_name="requis_par"`,
    `.claude/rules/modeles.md`, classe d'association `Prerequis`."""
    ids = [e.pk for e in elements]
    liens = Prerequis.objects.filter(element_prerequis_id__in=ids).select_related("element")
    resultat = {}
    for lien in liens:
        resultat.setdefault(lien.element_prerequis_id, []).append(lien.element)
    return resultat


def _semaines_reservees(element, dependantes, duree_session_semaines):
    """§ 6, prompt 56 : réserve, à la fin de la session, un nombre de
    semaines proportionnel au volume des matières que `element`
    conditionne — une dépendante au volume ÉGAL OU SUPÉRIEUR à celui de sa
    prérequise réserve la session ENTIÈRE (ratio ≥ 1), ce qui fait tomber
    le plafond de la prérequise à reste × coefficient dès la première
    semaine (`semaines_restantes` plafonne à 1 — comportement assumé,
    voir `test_prerequis_ratio_superieur_reserve_toute_la_session`)."""
    if not dependantes or element.volume_horaire_prescrit <= 0:
        return 0
    ratio = sum(d.volume_horaire_prescrit for d in dependantes) / element.volume_horaire_prescrit
    return math.ceil(ratio * duree_session_semaines)


def _echeance_element(element, dependantes, brigade, duree_session_semaines):
    reserve = _semaines_reservees(element, dependantes, duree_session_semaines)
    if reserve <= 0:
        return None
    return brigade.session.date_fin - datetime.timedelta(weeks=reserve)


@dataclasses.dataclass(frozen=True)
class _DonneesCalcul:
    """`.claude/rules/python.md`, § 5 paramètres max : ce que `calculer_
    plafonds` charge UNE FOIS (I3, Prompt 31) voyage groupé jusqu'à
    `_plafond_element`, plutôt que cinq paramètres de plus."""

    creneaux: list
    lundi_de_semaine: object
    periodes_bloquantes: list
    dependantes_par_element: dict
    duree_creneau: float


def _plafond_element(element, brigade, contexte, donnees):
    reste = volume_restant(element, brigade, contexte)
    if reste <= 0:
        return 0.0
    duree_session = _duree_session_semaines(brigade)
    dependantes = donnees.dependantes_par_element.get(element.pk, [])
    echeance = _echeance_element(element, dependantes, brigade, duree_session)
    semaines = semaines_restantes(
        brigade, donnees.lundi_de_semaine, donnees.creneaux, donnees.periodes_bloquantes, echeance
    )
    brut = (reste / semaines) * coefficient()
    return math.ceil(brut / donnees.duree_creneau) * donnees.duree_creneau if brut > 0 else 0.0


def _charger_donnees_calcul(matieres_par_brigade, brigades, creneaux, lundi_de_semaine):
    tous_elements = {e.pk: e for liste in matieres_par_brigade.values() for e in liste}
    fin_max = max((b.session.date_fin for b in brigades), default=lundi_de_semaine)
    debut = datetime.datetime.combine(lundi_de_semaine, datetime.time.min)
    fin = datetime.datetime.combine(fin_max + datetime.timedelta(weeks=1), datetime.time.min)
    return _DonneesCalcul(
        creneaux=creneaux,
        lundi_de_semaine=lundi_de_semaine,
        periodes_bloquantes=charger_periodes_bloquantes(debut, fin),
        dependantes_par_element=_dependantes_par_element(tous_elements.values()),
        duree_creneau=duree_creneau_minimale(creneaux),
    )


def calculer_plafonds(matieres_par_brigade, brigades, contexte, creneaux, lundi_de_semaine):
    """Un plafond en heures par (`element.pk`, `brigade.pk`) — même ordre de
    clé que `Contexte.volume_programme_par_element_brigade` (prompt 55),
    pour composer sans inversion. Calculé UNE FOIS par génération (I3,
    Prompt 31) : la semaine en cours ne le recalcule jamais en cours de
    placement, seulement le lancement suivant."""
    donnees = _charger_donnees_calcul(matieres_par_brigade, brigades, creneaux, lundi_de_semaine)
    plafonds = {}
    for brigade in brigades:
        for element in matieres_par_brigade.get(brigade.pk, []):
            plafonds[(element.pk, brigade.pk)] = _plafond_element(
                element, brigade, contexte, donnees
            )
    return plafonds


def motif_plafond(element, plafond):
    return (
        f"Plafond hebdomadaire atteint pour {element.matiere} "
        f"({plafond:.2f} h cette semaine, RG-66)."
    )


def filtrer_sous_plafond(brigade, elements, plafonds, volume_semaine):
    """Écarte les matières ayant atteint leur plafond hebdomadaire CETTE
    semaine — `volume_semaine` : déjà posé (épinglées comprises) plus ce
    que le lot de cette génération a accepté jusqu'ici, même clé que
    `plafonds`. `ecartees` porte des `MatiereEcartee` (même type que
    `candidats._ecartee`, jamais une seconde classe) : les créneaux
    libérés reviennent naturellement aux autres matières candidates (§ 4),
    cette fonction ne fait que raccourcir la liste, la boucle de placement
    existante s'occupe du reste."""
    from planification.generation.strategie import MatiereEcartee

    programmables, ecartees = [], []
    for element in elements:
        cle = (element.pk, brigade.pk)
        plafond = plafonds.get(cle)
        if plafond is not None and volume_semaine.get(cle, 0) >= plafond:
            ecartees.append(
                MatiereEcartee(
                    brigade=brigade, element=element, motif=motif_plafond(element, plafond)
                )
            )
            continue
        programmables.append(element)
    return programmables, ecartees


def incrementer_volume_semaine(volume_semaine, candidates):
    for candidate in candidates:
        cle = (candidate.element_referentiel.pk, candidate.brigade.pk)
        volume_semaine[cle] = volume_semaine.get(cle, 0) + duree_heures(
            candidate.debut, candidate.fin
        )
