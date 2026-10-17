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
    # Les deux ont besoin de request.user, donc après AuthenticationMiddleware.
    # ConnexionObligatoireMiddleware avant l'autre : une session expirée doit
    # atteindre l'écran de connexion, pas celui de changement de mot de passe.
    "administration.middleware.ConnexionObligatoireMiddleware",
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
                "planification.context_processors.validation_en_attente",
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

# Référentiel — BNF-13. Deux paramètres provisoires, à confirmer auprès du
# chef de bureau pédagogique — voir docs/suivi/DECISIONS.md et
# referentiel/services/referentiel.py::ServiceReferentiel.ecart.
#
# VOLUME_HORAIRE_HEBDOMADAIRE_REFERENCE convertit la durée d'une formation
# (Formation.duree_semaines, en semaines — arbitrage D-25) en un volume total
# attendu, en heures, comparable à la somme des volumes prescrits du
# référentiel (critère 5, US-REF-03). Rien, dans aucun livrable, ne dit
# combien d'heures d'instruction compte une semaine au CIT — la grille
# horaire (US-RES, sprint 2) portera la vraie réponse et remplacera ce
# paramètre provisoire.
VOLUME_HORAIRE_HEBDOMADAIRE_REFERENCE = int(
    os.environ.get("VOLUME_HORAIRE_HEBDOMADAIRE_REFERENCE", "30")
)

# Seuil, en pourcentage du volume attendu, au-delà duquel l'écart entre le
# total prescrit et la durée de la formation déclenche l'avertissement non
# bloquant du critère 5. Un pourcentage plutôt qu'un nombre d'heures absolu :
# reste pertinent aussi bien sur une formation de deux semaines que de
# cinquante-deux.
SEUIL_ECART_VOLUME_REFERENTIEL_POURCENT = int(
    os.environ.get("SEUIL_ECART_VOLUME_REFERENTIEL_POURCENT", "10")
)

# Bornes de l'import de stagiaires (US-SES-05, § 4, Prompt 24) : une session
# du CIT compte quelques dizaines de stagiaires, jamais des milliers — un
# fichier de cent mille lignes est une erreur ou une attaque, pas un cas
# d'usage. Paramétrable (BNF-13), jamais codé en dur.
IMPORT_STAGIAIRES_TAILLE_MAX_OCTETS = int(
    os.environ.get("IMPORT_STAGIAIRES_TAILLE_MAX_OCTETS", str(300 * 1024))
)
IMPORT_STAGIAIRES_LIGNES_MAX = int(os.environ.get("IMPORT_STAGIAIRES_LIGNES_MAX", "500"))

# Calendrier académique (US-PLAN-01, § 6, Prompt 28) : rien, dans aucun
# livrable, ne fixe la borne de l'« année de formation » du critère 1 — ni
# janvier, ni un cycle propre au CIT. Réponse de terrain confirmée : le mois
# de septembre. Paramétrable (BNF-13), jamais codé en dur dans les vues du
# calendrier — voir docs/suivi/DECISIONS.md.
MOIS_DEBUT_ANNEE_FORMATION = int(os.environ.get("MOIS_DEBUT_ANNEE_FORMATION", "9"))

# Génération du programme hebdomadaire (US-PLAN-03, § 3/§ 6, Prompt 31).
# GENERATION_STRATEGIE : le choix de stratégie est un paramètre, jamais une
# branche de code — même avec une seule implantation disponible aujourd'hui
# (« gloutonne »). GENERATION_BORNE_TEMPS_SECONDES : BNF-04 borne la
# génération à cinq minutes ; la borne appartient à l'interface de stratégie
# et protège d'un défaut qui ferait boucler la génération, même si une
# heuristique gloutonne (temps proportionnel au nombre de cases) ne
# l'atteint jamais en pratique.
GENERATION_STRATEGIE = os.environ.get("GENERATION_STRATEGIE", "gloutonne")
GENERATION_BORNE_TEMPS_SECONDES = int(os.environ.get("GENERATION_BORNE_TEMPS_SECONDES", "300"))

# Moyennes (US-EVAL-06, N6, prompt 46). Traitement d'une absence au calcul :
# « zero » compte l'évaluation comme une note de zéro (valeur par défaut, la
# plus défavorable — ne peut jamais avantager un stagiaire par erreur) ;
# « exclusion » retire l'évaluation du calcul du module pour ce seul
# stagiaire. Question ajoutée au terrain, réponse non reçue à ce jour — voir
# docs/suivi/DECISIONS.md. Les deux valeurs admises sont nommées dans
# evaluations/constantes.py, jamais en dur dans le service.
TRAITEMENT_ABSENCE_NOTE = os.environ.get("TRAITEMENT_ABSENCE_NOTE", "zero")

# Procès-verbaux (US-EVAL-07, V6, prompt 46). Seuil d'admission, sur 20 :
# « Admis » si la moyenne (ou la note du module, selon le type de
# procès-verbal) est supérieure ou égale à ce seuil. Chaîne plutôt qu'un
# entier : parsée en `decimal.Decimal` au point d'usage, pour rester
# cohérente avec les moyennes elles-mêmes (jamais de flottant sur une note,
# `.claude/rules/modeles.md`).
SEUIL_ADMISSION_PROCES_VERBAL = os.environ.get("SEUIL_ADMISSION_PROCES_VERBAL", "10")

LOGIN_URL = "administration:connexion"
LOGIN_REDIRECT_URL = "noyau:accueil"
LOGOUT_REDIRECT_URL = "administration:connexion"
