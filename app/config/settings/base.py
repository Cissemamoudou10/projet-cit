"""Réglages communs à tous les environnements.

Ce module ne définit ni SECRET_KEY, ni DATABASES : chaque environnement
(local, test, production) choisit son rôle de connexion PostgreSQL et sa
clé secrète — voir docs/suivi/DECISIONS.md pour le partage des rôles
pfe_cit_migration / pfe_cit_app.
"""

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.postgres",
    "noyau",
    "administration",
    "referentiel",
    "ressources",
    "organisation",
    "planification",
    "evaluations",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    # Après AuthenticationMiddleware : a besoin de request.user. § 2.2.
    "administration.middleware.ChangementMotDePasseObligatoireMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "noyau.context_processors.contexte_application",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

AUTH_USER_MODEL = "administration.Utilisateur"
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

USE_TZ = True
TIME_ZONE = "Africa/Casablanca"
LANGUAGE_CODE = "fr-fr"
USE_I18N = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

# BNF-13 : taille de page paramétrable, jamais en dur — voir noyau/pagination.py
TAILLE_PAGE_DEFAUT = int(os.environ.get("TAILLE_PAGE_DEFAUT", "20"))

# Pied de page — voir noyau/context_processors.py et docs/charte, § 2.4
APPLICATION_NOM = "Gestion des activités de formation"
APPLICATION_VERSION = "0.1.0"

# Authentification — RG-03, BNF-13. Valeurs par défaut à confirmer auprès du
# chef de bureau pédagogique ; voir administration/services/authentification.py
AUTH_SEUIL_ECHECS = int(os.environ.get("AUTH_SEUIL_ECHECS", "5"))
AUTH_DUREE_VERROUILLAGE_MINUTES = int(os.environ.get("AUTH_DUREE_VERROUILLAGE_MINUTES", "15"))

# Session — critère 4 (US-ADM-01) : trente minutes d'inactivité.
# SESSION_SAVE_EVERY_REQUEST n'est pas un détail : sans lui, les trente
# minutes courent depuis la connexion et non depuis la dernière action.
SESSION_COOKIE_AGE = int(os.environ.get("SESSION_COOKIE_AGE", "1800"))
SESSION_SAVE_EVERY_REQUEST = True

LOGIN_URL = "administration:connexion"
LOGIN_REDIRECT_URL = "noyau:accueil"
LOGOUT_REDIRECT_URL = "administration:connexion"
