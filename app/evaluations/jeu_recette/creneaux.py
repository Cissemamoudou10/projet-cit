"""Recherche d'un créneau libre pour une brigade, un jour donné — utilisée à
la fois par la chronologie simulée des programmes (`programme_complet.py` :
avenant de déplacement) et par l'insertion de contrôles formatifs
(`evaluations_complet.py` : E1, E2, E5). Même patron que la démonstration J2
(`tests/scenarios/test_demonstration_j2.py::_premier_creneau_libre`),
restreint à un seul jour au lieu de toute la semaine."""

from django.utils import timezone

from planification.models import LigneProgramme
from planification.selectors import JOUR_SEMAINE_PAR_ISO


def creneau_libre(programme, brigade, jour_iso, creneaux):
    occupes = {
        (
            timezone.localtime(ligne.seance.debut).isoweekday(),
            timezone.localtime(ligne.seance.debut).time(),
        )
        for ligne in LigneProgramme.objects.filter(
            seance__programme=programme, brigade=brigade
        ).select_related("seance")
    }
    for creneau in creneaux:
        if JOUR_SEMAINE_PAR_ISO[creneau.jour_semaine] != jour_iso:
            continue
        if (jour_iso, creneau.heure_debut) not in occupes:
            return creneau
    return None
