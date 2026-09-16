"""Conversion durée → heures, décimale — réutilisée par `regles_volume`,
`generation.tri` et `generation.compte_rendu` (.claude/rules/python.md,
duplication : trois occurrences, extraction)."""


def duree_heures(debut, fin):
    return (fin - debut).total_seconds() / 3600
