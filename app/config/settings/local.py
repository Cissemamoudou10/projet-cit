"""Réglages du poste de développement.

Pointe par défaut le rôle applicatif pfe_cit_app (lecture/écriture, aucun
privilège de création). Pour lancer `migrate`, surcharger BASE_UTILISATEUR
et BASE_MOT_DE_PASSE avec les identifiants du rôle pfe_cit_migration —
commande documentée dans docs/suivi/.
"""

import os

from .base import *  # noqa: F403

DEBUG = True

SECRET_KEY = "cle-de-developpement-non-versionnee-en-production"

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("BASE_NOM", "pfe_cit"),
        "USER": os.environ.get("BASE_UTILISATEUR", "pfe_cit_app"),
        "PASSWORD": os.environ.get("BASE_MOT_DE_PASSE", "developpement_local_app"),
        "HOST": os.environ.get("BASE_HOTE", "localhost"),
        "PORT": os.environ.get("BASE_PORT", "5432"),
    }
}
