"""Programme hebdomadaire, séances, lignes de programme et leur compte
rendu de génération — CU-P5-01, CU-P5-02, RG-31 à RG-40. Paquetage P5.

Scindé en modules dès que `models.py` a dépassé 400 lignes
(.claude/rules/python.md) : un fichier par agrégat, ré-exporté ici pour que
`from planification.models import X` continue de fonctionner sans
changement ailleurs dans le projet — même patron que `ressources/models/`.
"""

from planification.models.compte_rendu import CompteRenduGeneration
from planification.models.programme import (
    Avenant,
    EditionProgression,
    EtatProgramme,
    LigneProgramme,
    NatureAvenant,
    NonExecution,
    ProgrammeHebdomadaire,
    Seance,
)

__all__ = [
    "Avenant",
    "CompteRenduGeneration",
    "EditionProgression",
    "EtatProgramme",
    "LigneProgramme",
    "NatureAvenant",
    "NonExecution",
    "ProgrammeHebdomadaire",
    "Seance",
]
