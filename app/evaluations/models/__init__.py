"""Évaluations — CU-P6-01 à CU-P6-07, CLS-05.

Scindé en modules dès qu'`models.py` a dépassé 400 lignes (US-EVAL-07,
prompt 46, point 3) : un fichier par agrégat, ré-exporté ici pour que
`from evaluations.models import X` continue de fonctionner sans changement
ailleurs dans le projet — même patron que `ressources.models`.
"""

from evaluations.models.evaluation import (
    Evaluation,
    Note,
    OrganisationEpreuve,
    Sujet,
    Surveillance,
    TypeEvaluation,
)
from evaluations.models.proces_verbal import ProcesVerbal, TypeProcesVerbal

__all__ = [
    "Evaluation",
    "Note",
    "OrganisationEpreuve",
    "ProcesVerbal",
    "Sujet",
    "Surveillance",
    "TypeEvaluation",
    "TypeProcesVerbal",
]
