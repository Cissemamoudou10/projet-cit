"""Recouvrement d'intervalles — une seule définition, deux granularités.

Instants (DateTimeField) : `[début, fin)`, bornes semi-ouvertes, la fin est
exclue (D-116). Deux séances contiguës, dont la fin de l'une égale le début de
l'autre, ne se recouvrent pas.

Dates (DateField) : jours inclus `[d1, d2]`, équivalents à `[d1, d2 + 1 jour)`.
`bandes_sessions` (`ressources/services/periode_calendrier.py`) raisonne ainsi :
ce n'est pas une divergence à harmoniser. Un sélecteur qui doit comparer les
deux granularités passe par une fonction nommée de ce module, qui convertit les
jours en instants, jamais par un `+ 1 jour` écrit à la main.

Chaque application importe ce module : aucune copie locale du prédicat.
"""

import datetime

from django.db.models import Q
from django.utils import timezone


def se_recouvrent(debut_a, fin_a, debut_b, fin_b):
    return debut_a < fin_b and debut_b < fin_a


def filtre_recouvrement(champ_debut, champ_fin, debut, fin):
    """Q des enregistrements dont `[champ_debut, champ_fin)` recouvre `[debut, fin)`."""
    return Q(**{f"{champ_debut}__lt": fin, f"{champ_fin}__gt": debut})


def instant_de(jour, heure):
    """Instant local d'une heure posée sur un jour (créneau d'une évaluation)."""
    return timezone.make_aware(datetime.datetime.combine(jour, heure))
