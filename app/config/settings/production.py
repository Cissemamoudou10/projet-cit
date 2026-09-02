"""Réglages de production.

Aucune valeur par défaut permissive : toute variable d'environnement absente
fait échouer le démarrage plutôt que de retomber sur une valeur de
développement.
"""

import os

from django.core.exceptions import ImproperlyConfigured

from .base import *  # noqa: F403


def _variable_obligatoire(nom: str) -> str:
    valeur = os.environ.get(nom)
    if not valeur:
        raise ImproperlyConfigured(f"Variable d'environnement obligatoire absente : {nom}")
    return valeur


DEBUG = False

SECRET_KEY = _variable_obligatoire("SECRET_KEY")

ALLOWED_HOSTS = _variable_obligatoire("ALLOWED_HOSTS").split(",")

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": _variable_obligatoire("BASE_NOM"),
        "USER": _variable_obligatoire("BASE_UTILISATEUR"),
        "PASSWORD": _variable_obligatoire("BASE_MOT_DE_PASSE"),
        "HOST": _variable_obligatoire("BASE_HOTE"),
        "PORT": _variable_obligatoire("BASE_PORT"),
    }
}
