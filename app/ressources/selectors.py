"""Indisponibilités en lecture groupée — sélecteurs publics (prompt 38, A5 révisé,
D-210). Une requête par fonction, pour N ressources à la fois, sur `[debut, fin)`.
"""

from noyau.intervalles import filtre_recouvrement
from ressources.models import IndisponibiliteInstructeur, IndisponibiliteLieu


def indisponibilites_des_lieux(ids_lieux, debut, fin) -> dict:
    """Lieu -> liste de ses indisponibilités recouvrant `[debut, fin)`, triées."""
    resultat = {}
    if not ids_lieux:
        return resultat
    requete = IndisponibiliteLieu.objects.filter(
        filtre_recouvrement("debut", "fin", debut, fin), lieu_id__in=list(ids_lieux)
    ).select_related("lieu").order_by("debut")
    for indisponibilite in requete:
        resultat.setdefault(indisponibilite.lieu_id, []).append(indisponibilite)
    return resultat


def indisponibilites_des_instructeurs(ids_instructeurs, debut, fin) -> dict:
    """Instructeur -> liste de ses indisponibilités recouvrant `[debut, fin)`, triées."""
    resultat = {}
    if not ids_instructeurs:
        return resultat
    requete = IndisponibiliteInstructeur.objects.filter(
        filtre_recouvrement("debut", "fin", debut, fin),
        instructeur_id__in=list(ids_instructeurs),
    ).select_related("instructeur").order_by("debut")
    for indisponibilite in requete:
        resultat.setdefault(indisponibilite.instructeur_id, []).append(indisponibilite)
    return resultat
