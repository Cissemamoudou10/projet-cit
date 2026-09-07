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

# Fichiers statiques servis par l'application elle-même (WhiteNoise) — aucun
# serveur frontal à emporter ni à maintenir sur le poste du centre.
#
# Sans manifeste (empreinte dans le nom de fichier) : css/polices.css
# référence ../polices/*.woff2 en chemin relatif, et le manifeste de Django
# ne réécrit que les urls découvertes dans les fichiers qu'il traite si
# leur extension est reconnue — sur un intranet de quelques dizaines
# d'agents, le cache longue durée du manifeste n'apporte rien qui justifie
# ce risque. Compression seule.
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}

# Doit suivre SecurityMiddleware — recommandation WhiteNoise. Copie de la
# liste de base.py : ne mute pas MIDDLEWARE en place, pour ne pas affecter
# les autres environnements qui importent le même module.
MIDDLEWARE = [
    *MIDDLEWARE[:1],
    "whitenoise.middleware.WhiteNoiseMiddleware",
    *MIDDLEWARE[1:],
]
