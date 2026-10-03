"""Recouvrement d'intervalles à bornes semi-ouvertes `[début, fin)` — D-116.

Une seule définition du prédicat, sous deux formes : en mémoire
(`se_recouvrent`) et en requête (`filtre_recouvrement`). Deux intervalles
contigus, dont la fin de l'un égale le début de l'autre, ne se recouvrent
pas. Chaque application l'importe d'ici : aucune copie locale.
"""

from django.db.models import Q


def se_recouvrent(debut_a, fin_a, debut_b, fin_b):
    return debut_a < fin_b and debut_b < fin_a


def filtre_recouvrement(champ_debut, champ_fin, debut, fin):
    """Q des enregistrements dont `[champ_debut, champ_fin)` recouvre `[debut, fin)`."""
    return Q(**{f"{champ_debut}__lt": fin, f"{champ_fin}__gt": debut})
