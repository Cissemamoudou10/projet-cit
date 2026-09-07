#!/bin/sh
# Rôles de connexion PostgreSQL — production.
#
# Même schéma que infra/postgres/init/01_roles.sql (développement) : deux
# rôles restreints, pfe_cit_migration (CREATEDB, propriétaire de la base,
# non superutilisateur) et pfe_cit_app (lecture/écriture seule). La seule
# différence est la source des mots de passe : ici, l'environnement — jamais
# en dur, contrairement au script de développement où des mots de passe
# fixes sont acceptés en local.
#
# Fichier .sh, pas .sql : docker-entrypoint-initdb.d ne fait pas de
# substitution de variables dans un .sql brut, seul un script shell peut lire
# l'environnement. Idempotent, comme son équivalent de développement.
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
