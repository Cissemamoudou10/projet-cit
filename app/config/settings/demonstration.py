"""Réglages de la démonstration J2 — Prompt 43.

Identiques à `local.py`, sauf la base : `pfe_cit_demo_j2`, jamais `pfe_cit`
(poste de développement) ni `pfe_cit_recette` (jalon C2, sprint 2 — § A3 du
prompt : « ne pas la toucher »). Nom de base fixé en dur, même raison que
`recette.py` : une variable d'environnement oubliée ne doit jamais
reconnecter silencieusement sur une autre base.

Usage : `python manage.py runserver --settings=config.settings.demonstration`
(et pour toute sous-commande visée par la démonstration — `shell`,
`preparer_demonstration`, etc.)
"""

from .local import *  # noqa: F403

DATABASES["default"]["NAME"] = "pfe_cit_demo_j2"  # noqa: F405
