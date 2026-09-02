"""Réglages de la suite de tests.

Pointe le rôle pfe_cit_migration : lui seul peut créer/détruire la base de
test (test_pfe_cit) et y jouer les migrations. Un rôle restreint comme
pfe_cit_app ne le peut pas — voir docs/suivi/DECISIONS.md.
"""

import os

from .base import *  # noqa: F403

DEBUG = False

SECRET_KEY = "cle-de-test-non-versionnee-en-production"

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("BASE_NOM", "pfe_cit"),
        "USER": os.environ.get("BASE_UTILISATEUR_MIGRATION", "pfe_cit_migration"),
        "PASSWORD": os.environ.get("BASE_MOT_DE_PASSE_MIGRATION", "developpement_local_migration"),
        "HOST": os.environ.get("BASE_HOTE", "localhost"),
        "PORT": os.environ.get("BASE_PORT", "5432"),
    }
}

PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
