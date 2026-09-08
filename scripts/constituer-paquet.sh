#!/usr/bin/env bash
# Constitution du paquet de déploiement hors ligne — Prompt 18.
#
# Phase 1 du protocole (§ 2) : s'exécute AVEC réseau, sur le poste de
# développement. Produit un paquet qui n'en a plus besoin. Rejouable :
# reconstruit entièrement paquet-deploiement/ à chaque exécution, jamais
# versionné (voir .gitignore).
#
# Usage : scripts/constituer-paquet.sh [version-application]
set -euo pipefail

RACINE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PAQUET="$RACINE/paquet-deploiement"
VERSION_APPLICATION="${1:-hors-ligne}"

# --- Versions épinglées explicitement — jamais "la dernière disponible" ---
VERSION_POSTGRES="16.15-bookworm"

# Docker Engine, Debian 12 (bookworm) — versions constatées le 2026-09-07 sur
# download.docker.com, à réviser explicitement si le paquet est reconstitué
# plus tard (§ 3 du Prompt 18 : reproductible, pas la dernière disponible).
DOCKER_CE_VERSION="5:29.8.0-1~debian.12~bookworm"
CONTAINERD_VERSION="2.3.4-2~debian.12~bookworm"
BUILDX_VERSION="0.37.0-1~debian.12~bookworm"
COMPOSE_PLUGIN_VERSION="5.5.1-1~debian.12~bookworm"

echo "== Nettoyage =="
rm -rf "$PAQUET"
mkdir -p "$PAQUET/images" "$PAQUET/moteur-docker/debian-12" "$PAQUET/compose/infra/postgres/init"

echo "== 1. Construction de l'image applicative (sans cache) =="
docker build --no-cache -t "pfe-cit-application:$VERSION_APPLICATION" -f "$RACINE/Dockerfile" "$RACINE"

echo "== 2. Récupération de l'image PostgreSQL épinglée =="
docker pull "postgres:$VERSION_POSTGRES"

echo "== 3. Export des images en archives =="
docker save "pfe-cit-application:$VERSION_APPLICATION" -o "$PAQUET/images/application.tar"
docker save "postgres:$VERSION_POSTGRES" -o "$PAQUET/images/postgres.tar"

echo "== 4. Paquets du moteur Docker pour Debian 12, avec toutes leurs dépendances =="
# Conteneur Debian 12 jetable — analogue le plus fidèle au serveur nu (§ 1
# du Prompt 18) — plutôt qu'une image de builder plus riche qui masquerait
# une dépendance absente sur un netinst. --download-only laisse apt calculer
# lui-même la fermeture transitive complète.
CONTENEUR_CONSTRUCTEUR=$(docker create debian:12-slim sh -c "
  set -e
  apt-get update -qq
  apt-get install -y -qq --no-install-recommends ca-certificates curl gnupg
  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
  chmod a+r /etc/apt/keyrings/docker.asc
  echo 'deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian bookworm stable' > /etc/apt/sources.list.d/docker.list
  apt-get update -qq
  apt-get install -y -qq --download-only --no-install-recommends \
    docker-ce=$DOCKER_CE_VERSION \
    docker-ce-cli=$DOCKER_CE_VERSION \
    containerd.io=$CONTAINERD_VERSION \
    docker-buildx-plugin=$BUILDX_VERSION \
    docker-compose-plugin=$COMPOSE_PLUGIN_VERSION
")
docker start --attach "$CONTENEUR_CONSTRUCTEUR"
docker cp "$CONTENEUR_CONSTRUCTEUR:/var/cache/apt/archives/." "$PAQUET/moteur-docker/debian-12/"
docker rm "$CONTENEUR_CONSTRUCTEUR" >/dev/null
find "$PAQUET/moteur-docker/debian-12" -type f ! -name "*.deb" -delete
find "$PAQUET/moteur-docker/debian-12" -mindepth 1 -type d -empty -delete

echo "== 5. Liste des paquets pour Ubuntu 24.04 — préparation, pas d'installation testée (§ 3) =="
SORTIE_UBUNTU_BRUTE=$(docker run --rm ubuntu:24.04 sh -c "
  set -e
  apt-get update -qq
  apt-get install -y -qq --no-install-recommends ca-certificates curl gnupg >/dev/null
  install -m 0755 -d /etc/apt/keyrings
  curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
  chmod a+r /etc/apt/keyrings/docker.asc
  echo 'deb [arch=amd64 signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu noble stable' > /etc/apt/sources.list.d/docker.list
  apt-get update -qq
  apt-cache policy docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
")
{
  echo "# Paquets du moteur Docker — Ubuntu 24.04 (noble)"
  echo "#"
  echo "# Liste seulement (§ 3 du Prompt 18) : pas d'installation testee sur cette"
  echo "# distribution dans ce passage. Candidats relatifs au depot officiel"
  echo "# download.docker.com/linux/ubuntu, noble/stable, releves a la constitution."
  echo
  echo "$SORTIE_UBUNTU_BRUTE" | awk '/^[a-z].*:$/{pkg=$0} /Candidate:/{print pkg " " $0}'
} > "$PAQUET/moteur-docker/ubuntu-24.04-liste.txt"

echo "== 6. Fichiers de composition, de rôles et d'installation =="
cp "$RACINE/docker-compose.production.yml" "$PAQUET/compose/"
cp "$RACINE/.env.exemple" "$PAQUET/compose/"
cp "$RACINE/infra/postgres/init/01_roles.sh" "$PAQUET/compose/infra/postgres/init/"
chmod +x "$PAQUET/compose/infra/postgres/init/01_roles.sh"
cp "$RACINE/infra/deploiement/installer.sh" "$PAQUET/installer.sh"
chmod +x "$PAQUET/installer.sh"

# Fixture de vérification PDF (§ 5 du protocole) — deux fichiers source
# seulement, jamais le demonstration.pdf généré localement (ignoré par
# .gitignore, ne doit pas être confondu avec le PDF produit sur la machine
# cible). Voir docs/exploitation/INSTALLATION.md.
mkdir -p "$PAQUET/verification-pdf"
cp "$RACINE/infra/verification-pdf/gabarit_demonstration.html" "$PAQUET/verification-pdf/"
cp "$RACINE/infra/verification-pdf/generer_pdf_demonstration.py" "$PAQUET/verification-pdf/"

echo
echo "== Poids du paquet =="
du -sh "$PAQUET"
du -sh "$PAQUET"/* "$PAQUET"/*/* 2>/dev/null | sort -k2
