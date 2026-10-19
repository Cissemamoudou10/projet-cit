"""Signaler les écarts de volume horaire — US-PLAN-07, BF-PLAN-07, `CU-P5-05`,
prompt 47.

E1 : aucun calcul nouveau pour le prescrit ni le programmé — réutilise
`volumes_programmes_par_element_brigade` (US-SUI-01,
`services/contraintes.py`) et `ElementReferentiel.volume_horaire_prescrit`
tels quels (`tests/architecture/test_calcul_unique_ecart_volume.py` le
vérifie). Ce module ne calcule jamais le réalisé ni le filtre « sans
programme affiché » du rapprochement (`selectors_rapprochement.py`) : ces
deux notions ne concernent que le réalisé, hors du périmètre de cette
story, qui ne compare que le prescrit et le programmé.

`RG-61` (§ 9.9 du dossier des cas d'utilisation, fiche `CU-P6-11`) :
« le seuil d'alerte est exprimé en pourcentage du volume prescrit et est
paramétrable au titre de BNF-13 ; l'alerte distingue les retards des
dépassements et disparaît lorsque l'écart repasse sous le seuil » —
exactement `statut_volume` (`planification/statut_volume.py`). Vocabulaire
repris de la charte, composant 3.33 (indicateur d'écart) : `conforme`,
`en_cours`, `retard` (sous-programmation), `depassement` (sur-programmation).

D-279 (fermée, prompt 48, Temps 0) : la mise en évidence sur l'écran du
rapprochement (US-SUI-01) — fondée sur le RÉALISÉ, pas le programmé — vit
désormais dans `selectors_alerte_ecart.py` (US-SUI-02), pas ici. Ce module
ne couvre plus que la consultation de la semaine, avant soumission (E2).
"""

import dataclasses

from django.conf import settings
from django.utils import timezone

from planification.services.contraintes import volumes_programmes_par_element_brigade
from planification.statut_volume import DEPASSEMENT, RETARD, statut_volume
from referentiel.models import ElementReferentiel


@dataclasses.dataclass(frozen=True)
class LigneEcartVolume:
    """E2/E3 : jamais stocké, recalculé à chaque consultation
    (`.claude/rules/modeles.md`)."""

    element_referentiel: object
    prescrit: float
    programme: float
    statut: str
    ecart_pourcent: float


@dataclasses.dataclass(frozen=True)
class GroupeEcartVolume:
    brigade: object
    lignes: list


def seuil_pourcent() -> float:
    return float(settings.SEUIL_ECART_VOLUME_HORAIRE)


def _elements_par_formation(formation_ids):
    elements_par_formation: dict = {}
    for element in ElementReferentiel.objects.filter(formation_id__in=formation_ids).select_related(
        "matiere"
    ):
        elements_par_formation.setdefault(element.formation_id, []).append(element)
    return elements_par_formation


def _lignes_en_ecart(brigade, elements_par_formation, programme_par_cle, termine, seuil):
    lignes = []
    for element in elements_par_formation.get(brigade.session.formation_id, []):
        programme = programme_par_cle.get((element.pk, brigade.pk), 0)
        statut, ecart_pourcent = statut_volume(
            element.volume_horaire_prescrit, programme, termine, seuil
        )
        if statut in (RETARD, DEPASSEMENT):
            lignes.append(
                LigneEcartVolume(
                    element_referentiel=element,
                    prescrit=element.volume_horaire_prescrit,
                    programme=programme,
                    statut=statut,
                    ecart_pourcent=ecart_pourcent,
                )
            )
    return lignes


def ecarts_volume_horaire(brigades, a_la_date=None) -> list:
    """E2, consultation de la semaine (avant soumission) : pour les
    brigades données, les matières EN ÉCART seulement (`retard` ou
    `depassement`) — `conforme` et `en_cours` restent silencieuses, c'est
    une liste d'alerte, pas un tableau de bord complet. Mêmes garanties de
    requêtes que R7 (US-SUI-01) : un seul appel à
    `volumes_programmes_par_element_brigade`, jamais une requête par
    brigade."""
    a_la_date = a_la_date or timezone.localdate()
    seuil = seuil_pourcent()
    brigades = list(brigades)
    brigade_ids = [brigade.pk for brigade in brigades]
    if not brigade_ids:
        return []
    elements_par_formation = _elements_par_formation({b.session.formation_id for b in brigades})
    programme_par_cle = volumes_programmes_par_element_brigade(brigade_ids=brigade_ids)

    groupes = []
    for brigade in brigades:
        termine = brigade.session.date_fin <= a_la_date
        lignes = _lignes_en_ecart(
            brigade, elements_par_formation, programme_par_cle, termine, seuil
        )
        if lignes:
            groupes.append(GroupeEcartVolume(brigade=brigade, lignes=lignes))
    return groupes
