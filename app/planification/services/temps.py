"""Conversion durée → heures, décimale — réutilisée par `regles_volume`,
`generation.tri` et `generation.compte_rendu` (.claude/rules/python.md,
duplication : trois occurrences, extraction).

`valider_lundi` : réutilisée par `generation.py` et `duplication.py`
(US-PLAN-11, prompt 48) — même règle, un seul endroit.

`duree_creneau_minimale`/`duree_creneau_maximale` (prompt 56) : durée d'un
créneau type, sans date réelle — seule la durée compte, un lundi arbitraire
sert de support. Minimale réutilisée par `generation.plafond_hebdomadaire`
(RG-66, unité d'arrondi) ; maximale par `selectors_ecart_volume` (RG-39 a)
modifiée, prompt 56 : borne du dépassement qu'une séance générée peut
causer — une seule implantation du calcul « durée d'un créneau type »,
jamais recopiée pour chaque borne.
"""

import datetime

from noyau.exceptions import ErreurValidation

_JOUR_ARBITRAIRE = datetime.date(2000, 1, 3)  # lundi, seule la durée des créneaux compte


def duree_heures(debut, fin):
    return (fin - debut).total_seconds() / 3600


def valider_lundi(lundi_de_semaine):
    if lundi_de_semaine.isoweekday() != 1:
        raise ErreurValidation(f"{lundi_de_semaine:%d/%m/%Y} n'est pas un lundi.")


def _durees_creneaux(creneaux):
    return [
        duree_heures(
            datetime.datetime.combine(_JOUR_ARBITRAIRE, c.heure_debut),
            datetime.datetime.combine(_JOUR_ARBITRAIRE, c.heure_fin),
        )
        for c in creneaux
    ]


def duree_creneau_minimale(creneaux) -> float:
    durees = _durees_creneaux(creneaux)
    return min(durees) if durees else 1.0


def duree_creneau_maximale(creneaux) -> float:
    durees = _durees_creneaux(creneaux)
    return max(durees) if durees else 1.0
