"""Réglages de la recette du sprint 2 — Prompt 34.

Identiques à `local.py`, sauf la base : `pfe_cit_recette`, jamais `pfe_cit`
(où vit le jeu de démonstration du sprint 1 — coexistence interdite par le
garde-fou de `charger_jeu_recette`). Nom de base fixé en dur, pas lu depuis
`BASE_NOM` : une variable d'environnement oubliée dans un nouveau terminal ne
doit plus jamais reconnecter silencieusement sur `pfe_cit`.

Usage : `python manage.py runserver --settings=config.settings.recette`
(ou `--settings=config.settings.recette` sur toute autre sous-commande visée
par la recette — `shell`, `charger_jeu_recette`, etc.)
"""

from .local import *  # noqa: F403

DATABASES["default"]["NAME"] = "pfe_cit_recette"  # noqa: F405
