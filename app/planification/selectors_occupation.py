"""Occupation d'un lieu ou d'un instructeur sur un intervalle — extrait de
`selectors.py` (`.claude/rules/python.md`, 400 lignes) lors de l'ajout
d'US-SES-09 (prompt 47). Consommé par `evaluations.services.conflits` et
`planification.selectors_indisponibilite`.
"""

from noyau.intervalles import filtre_recouvrement
from planification.models import Seance


def seances_occupant_lieux(ids_lieux, debut, fin) -> dict:
    """Lieu -> séances occupant ce lieu sur `[debut, fin)` — une requête pour N lieux."""
    resultat = {}
    if not ids_lieux:
        return resultat
    requete = (
        Seance.objects.filter(
            filtre_recouvrement("debut", "fin", debut, fin), lieu_id__in=list(ids_lieux)
        )
        .select_related("element_referentiel__matiere", "instructeur", "lieu")
        .order_by("debut")
    )
    for seance in requete:
        resultat.setdefault(seance.lieu_id, []).append(seance)
    return resultat


def seances_occupant_instructeurs(ids_instructeurs, debut, fin) -> dict:
    """Instructeur -> séances de cet instructeur sur `[debut, fin)` — une requête pour N."""
    resultat = {}
    if not ids_instructeurs:
        return resultat
    requete = (
        Seance.objects.filter(
            filtre_recouvrement("debut", "fin", debut, fin),
            instructeur_id__in=list(ids_instructeurs),
        )
        .select_related("element_referentiel__matiere", "instructeur", "lieu")
        .order_by("debut")
    )
    for seance in requete:
        resultat.setdefault(seance.instructeur_id, []).append(seance)
    return resultat
