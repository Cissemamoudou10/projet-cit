#!/bin/sh
# Rôles de connexion PostgreSQL — développement ET production, un seul script.
#
# Deux rôles restreints, décidés au socle (voir docs/suivi/DECISIONS.md,
# D-19, D-61) :
#
#   $BASE_UTILISATEUR_MIGRATION : propriétaire de la base, exécute les
#     migrations. Non superutilisateur — btree_gist est une extension
#     « trusted » depuis PostgreSQL 13 : être propriétaire de la base
#     suffit pour la créer. CREATEDB reste nécessaire pour une raison
#     distincte : c'est ce qui permet à pytest-django de créer/détruire la
#     base de test en développement.
#
#   $BASE_UTILISATEUR : rôle applicatif, utilisé par Django en
#     fonctionnement normal. Aucun privilège de création — seulement
#     lecture/écriture sur les tables existantes, via les privilèges par
#     défaut ci-dessous.
#
# Les deux mots de passe viennent toujours de l'environnement, jamais en
# dur — y compris en développement, où `docker-compose.yml` leur donne des
# valeurs par défaut fixes (non secrètes, déjà versionnées en clair
# aujourd'hui) plutôt qu'un fichier `.env` à créer sur chaque poste :
# cloner le dépôt et lancer `docker compose up` continue de fonctionner
# sans étape de configuration locale supplémentaire.
#
# La révocation UPDATE/DELETE sur administration_entree_journal (RG-27)
# n'est PAS de ce script : la table n'existe qu'après les migrations
# Django (US-ADM-04) — voir docs/suivi/DECISIONS.md.
#
# Fichier .sh, pas .sql : docker-entrypoint-initdb.d ne fait pas de
# substitution de variables dans un .sql brut, seul un script shell peut
# lire l'environnement. Idempotent — rejouable sans effet de bord sur une
# base déjà initialisée (exécuté automatiquement une seule fois par Docker
# au premier démarrage du volume ; rejouable à la main via psql si besoin).
#
# Un seul script pour les deux piles (D-62, Prompt 19 bloc E) : la version
# précédente existait en deux copies quasi identiques
# (infra/postgres/init/01_roles.sql en développement, mots de passe fixes ;
# infra/postgres/init-production/01_roles.sh, mots de passe lus dans
# l'environnement) — la même classe de défaut que P-32
# (docs/suivi/PROBLEMES.md), où un correctif n'avait touché qu'une des deux
# copies d'un balisage dupliqué.
set -eu

: "${BASE_NOM:?BASE_NOM manquant}"
: "${BASE_UTILISATEUR_MIGRATION:?BASE_UTILISATEUR_MIGRATION manquant}"
: "${BASE_MOT_DE_PASSE_MIGRATION:?BASE_MOT_DE_PASSE_MIGRATION manquant}"
: "${BASE_UTILISATEUR:?BASE_UTILISATEUR manquant}"
: "${BASE_MOT_DE_PASSE:?BASE_MOT_DE_PASSE manquant}"

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '${BASE_UTILISATEUR_MIGRATION}') THEN
            CREATE ROLE ${BASE_UTILISATEUR_MIGRATION} LOGIN PASSWORD '${BASE_MOT_DE_PASSE_MIGRATION}' CREATEDB;
        END IF;
    END
    \$\$;

    DO \$\$
    BEGIN
        IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '${BASE_UTILISATEUR}') THEN
            CREATE ROLE ${BASE_UTILISATEUR} LOGIN PASSWORD '${BASE_MOT_DE_PASSE}';
        END IF;
    END
    \$\$;

    ALTER DATABASE ${BASE_NOM} OWNER TO ${BASE_UTILISATEUR_MIGRATION};

    GRANT USAGE ON SCHEMA public TO ${BASE_UTILISATEUR};

    ALTER DEFAULT PRIVILEGES FOR ROLE ${BASE_UTILISATEUR_MIGRATION} IN SCHEMA public
        GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO ${BASE_UTILISATEUR};

    ALTER DEFAULT PRIVILEGES FOR ROLE ${BASE_UTILISATEUR_MIGRATION} IN SCHEMA public
        GRANT USAGE, SELECT ON SEQUENCES TO ${BASE_UTILISATEUR};
EOSQL
