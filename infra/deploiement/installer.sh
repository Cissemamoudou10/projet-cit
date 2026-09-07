#!/bin/sh
# Installation hors ligne — Phases 2 et 3 du protocole (Prompt 18, § 2).
#
# S'exécute SANS réseau, sur la machine cible, depuis la racine du paquet de
# déploiement (là où ce script a été copié) : images/, moteur-docker/,
# compose/. Rien ici ne doit émettre une requête réseau — un `apt-get` ou un
# `docker compose` qui irait chercher une ressource manquante est justement
# le défaut que ce test cherche à révéler (§ 2, Phase 3).
#
# S'arrête volontairement au démarrage de la pile : migrations et création
# du premier compte administrateur restent des commandes explicites,
# documentées à part (docs/exploitation/INSTALLATION.md) — elles modifient
# le schéma et créent un accès, elles ne doivent pas se déclencher seules.
set -eu

if [ "$(id -u)" -ne 0 ]; then
    echo "Ce script s'exécute en superutilisateur (sudo)." >&2
    exit 1
fi

RACINE_PAQUET="$(cd "$(dirname "$0")" && pwd)"
ENV_FICHIER="$RACINE_PAQUET/compose/.env"

echo "== Phase 2 — installation du moteur Docker (paquets locaux) =="
cd "$RACINE_PAQUET/moteur-docker/debian-12"
apt-get install -y ./*.deb
cd "$RACINE_PAQUET"
systemctl enable --now docker

echo
echo "== Phase 3 — chargement des images =="
if [ -n "$(docker images -q)" ]; then
    echo "ATTENTION : des images sont déjà présentes sur cette machine — l'instantané" >&2
    echo "« serveur nu » n'est peut-être pas respecté (§ 1.1 du Prompt 18)." >&2
fi
docker load -i "$RACINE_PAQUET/images/postgres.tar"
docker load -i "$RACINE_PAQUET/images/application.tar"

if [ ! -f "$ENV_FICHIER" ]; then
    echo >&2
    echo "Fichier d'environnement absent : $ENV_FICHIER" >&2
    echo "Copier compose/.env.exemple vers compose/.env, renseigner SECRET_KEY," >&2
    echo "ALLOWED_HOSTS et les mots de passe (jamais versionnés), puis relancer ce" >&2
    echo "script." >&2
    exit 1
fi
chmod 600 "$ENV_FICHIER"

echo
echo "== Démarrage de la pile =="
docker compose -f "$RACINE_PAQUET/compose/docker-compose.production.yml" --env-file "$ENV_FICHIER" up -d

echo
echo "== Attente de la base de données =="
i=0
while [ "$i" -lt 30 ]; do
    ETAT="$(docker inspect -f '{{.State.Health.Status}}' pfe_cit_base 2>/dev/null || echo absent)"
    [ "$ETAT" = "healthy" ] && break
    i=$((i + 1))
    sleep 2
done
if [ "$ETAT" != "healthy" ]; then
    echo "La base de données n'est pas passée « healthy » après soixante secondes." >&2
    echo "Voir : docker compose -f \"$RACINE_PAQUET/compose/docker-compose.production.yml\" logs base" >&2
    exit 1
fi

echo
echo "=================================================================="
echo "Pile démarrée. Ce script s'arrête ici, volontairement (§ 4 du Prompt 18) :"
echo "migrations et création du premier compte administrateur restent des"
echo "commandes explicites, documentées à part dans"
echo "docs/exploitation/INSTALLATION.md."
echo
echo "Vérifier l'état :"
echo "  docker compose -f \"$RACINE_PAQUET/compose/docker-compose.production.yml\" ps"
echo "=================================================================="
