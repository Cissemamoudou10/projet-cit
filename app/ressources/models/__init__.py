"""Ressources humaines et matérielles du centre, et calendrier académique —
CU-P4-01 à CU-P4-06, CLS-03.

Scindé en modules dès que `models.py` a dépassé 400 lignes
(.claude/rules/python.md) : un fichier par agrégat, ré-exporté ici pour que
`from ressources.models import X` continue de fonctionner sans changement
ailleurs dans le projet.
"""

from ressources.models.calendrier import (
    EffetPeriode,
    NatureEvenement,
    PeriodeCalendrier,
    PeriodeCalendrierBrigade,
    PeriodeCalendrierSession,
    decrire_cibles,
)
from ressources.models.grille_horaire import CreneauType, GrilleHoraire, JourSemaine
from ressources.models.instructeur import (
    IndisponibiliteInstructeur,
    Instructeur,
    Qualification,
    Statut,
    _PeriodeTstz,  # noqa: F401 — migration 0009 y référence `ressources.models._PeriodeTstz`
)
from ressources.models.lieu import (
    CategorieLieu,
    IndisponibiliteLieu,
    Lieu,
    ModePartage,
    SalleAttitree,
    TypeLieuPartage,
)

__all__ = [
    "CategorieLieu",
    "CreneauType",
    "EffetPeriode",
    "decrire_cibles",
    "GrilleHoraire",
    "IndisponibiliteInstructeur",
    "IndisponibiliteLieu",
    "Instructeur",
    "JourSemaine",
    "Lieu",
    "ModePartage",
    "NatureEvenement",
    "PeriodeCalendrier",
    "PeriodeCalendrierBrigade",
    "PeriodeCalendrierSession",
    "Qualification",
    "SalleAttitree",
    "Statut",
    "TypeLieuPartage",
]
