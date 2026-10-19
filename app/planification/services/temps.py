"""Conversion durée → heures, décimale — réutilisée par `regles_volume`,
`generation.tri` et `generation.compte_rendu` (.claude/rules/python.md,
duplication : trois occurrences, extraction).

`valider_lundi` : réutilisée par `generation.py` et `duplication.py`
(US-PLAN-11, prompt 48) — même règle, un seul endroit.
"""

from noyau.exceptions import ErreurValidation


def duree_heures(debut, fin):
    return (fin - debut).total_seconds() / 3600


def valider_lundi(lundi_de_semaine):
    if lundi_de_semaine.isoweekday() != 1:
        raise ErreurValidation(f"{lundi_de_semaine:%d/%m/%Y} n'est pas un lundi.")
