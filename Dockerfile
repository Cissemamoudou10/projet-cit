# Image de production — Debian bookworm, alignée sur la VM cible (Debian 12) :
# les bibliothèques natives de WeasyPrint diffèrent selon la base.
#
# Version épinglée au patch : Python 3.14.4, vérifiée être celle du poste de
# développement (.venv/pyvenv.cfg) au moment de l'écriture — voir
# docs/suivi/INSTALLATION-HORS-LIGNE.md.
#
# Ne sert pas au développement : `docker compose up -d` (fichier racine)
# reste inchangé et tourne sans cette image.
FROM python:3.14.4-slim-bookworm

# Dépendances système de WeasyPrint 69 — Pango seulement. Depuis WeasyPrint
# 53, le rendu PDF ne passe plus par Cairo ni GDK-PixBuf (pydyf, backend PDF
# pur Python) : le paquet est plus léger que ce que la documentation plus
# ancienne laisse penser. Liste reprise du guide officiel « Debian ≥ 11,
# installation par roues précompilées » (docs.weasyprint.org).
RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        libpango-1.0-0 \
        libpangoft2-1.0-0 \
        libharfbuzz-subset0 \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd --system application \
    && useradd --system --create-home --gid application --home-dir /app application

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ .

# collectstatic à la construction — le CSS Tailwind est déjà précompilé et
# versionné (docs/charte), aucun outillage Node dans cette image. Valeurs
# ci-dessous : uniquement pour que le module de réglages s'importe (les
# variables obligatoires de production.py), jamais utilisées pour une
# connexion réelle — remplacées à l'exécution par docker-compose.production.yml.
# Vérifié après construction : aucune ne persiste dans l'image (ARG, jamais
# ENV) ni dans les fichiers de /app — voir docs/suivi/INSTALLATION-HORS-LIGNE.md.
# Nommage volontairement écarté de « SECRET_KEY » : un analyseur statique de
# Dockerfile signale toute variable ARG/ENV de ce nom comme fuite potentielle,
# même lorsque — comme ici — elle ne survit pas à sa seule commande RUN.
ARG CLE_CONSTRUCTION=cle-de-construction-non-utilisee-en-production
ARG ALLOWED_HOSTS=localhost
ARG BASE_NOM=constitution
ARG BASE_HOTE=localhost
ARG BASE_PORT=5432
ARG BASE_UTILISATEUR=constitution
ARG BASE_MOT_DE_PASSE=constitution

ENV DJANGO_SETTINGS_MODULE=config.settings.production

RUN SECRET_KEY=$CLE_CONSTRUCTION \
    ALLOWED_HOSTS=$ALLOWED_HOSTS \
    BASE_NOM=$BASE_NOM \
    BASE_HOTE=$BASE_HOTE \
    BASE_PORT=$BASE_PORT \
    BASE_UTILISATEUR=$BASE_UTILISATEUR \
    BASE_MOT_DE_PASSE=$BASE_MOT_DE_PASSE \
    python manage.py collectstatic --noinput

RUN chown -R application:application /app
USER application

EXPOSE 8000

# Nombre de processus sobre : quelques dizaines d'agents, pas un service
# public. Ajustable par variable d'environnement si le banc d'essai en
# décide autrement — voir docs/suivi/INSTALLATION-HORS-LIGNE.md.
CMD ["gunicorn", "config.wsgi:application", \
     "--bind", "0.0.0.0:8000", \
     "--workers", "3", "--threads", "2"]
