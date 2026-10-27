"""Réglages du jeu volumineux — Prompt 51, Temps 1.

Identiques à `local.py`, sauf la base : `pfe_cit_volume`, jamais `pfe_cit` ni
`pfe_cit_recette` — coexistence interdite avec le jeu de démonstration et avec
le jeu de recette (même garde-fou que `config.settings.recette`, voir
`docs/suivi/JEU-RECETTE.md`). Nom de base fixé en dur, pas lu depuis
`BASE_NOM`.

Usage : `python manage.py runserver --settings=config.settings.volume` (ou sur
toute autre sous-commande visée par le jeu volumineux — `shell`,
`charger_jeu_volume`, etc.)
"""

from .local import *  # noqa: F403

DATABASES["default"]["NAME"] = "pfe_cit_volume"  # noqa: F405
