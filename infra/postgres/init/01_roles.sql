-- Rôles de connexion PostgreSQL — développement.
--
-- Deux rôles distincts, décidés au socle (voir docs/suivi/DECISIONS.md) :
--
--   pfe_cit_migration : propriétaire de la base « pfe_cit », exécute les
--     migrations. Non superutilisateur — btree_gist est une extension
--     « trusted » depuis PostgreSQL 13 : être propriétaire de la base
--     suffit pour la créer, aucune concession à demander sur le poste du
--     CIT. CREATEDB reste nécessaire, mais pour une raison distincte :
--     c'est ce qui permet à pytest-django de créer/détruire la base de
--     test (test_pfe_cit).
--
--   pfe_cit_app : rôle applicatif, utilisé par Django en fonctionnement
--     normal. Aucun privilège de création — seulement lecture/écriture sur
--     les tables existantes, via les privilèges par défaut ci-dessous.
--
-- La révocation UPDATE/DELETE sur administration_entree_journal (RG-27)
-- n'est PAS de ce script : la table n'existe pas encore. Elle viendra avec
-- US-ADM-04 — voir docs/suivi/DECISIONS.md pour la dette identifiée.
--
-- Idempotent : peut être rejoué sans effet de bord sur une base déjà
-- initialisée (exécuté automatiquement une seule fois par Docker au premier
-- démarrage du volume ; rejouable à la main via psql si besoin).

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'pfe_cit_migration') THEN
        CREATE ROLE pfe_cit_migration LOGIN PASSWORD 'developpement_local_migration' CREATEDB;
    END IF;
END
$$;

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'pfe_cit_app') THEN
        CREATE ROLE pfe_cit_app LOGIN PASSWORD 'developpement_local_app';
    END IF;
END
$$;

ALTER DATABASE pfe_cit OWNER TO pfe_cit_migration;

GRANT USAGE ON SCHEMA public TO pfe_cit_app;

-- S'applique aux tables et séquences que pfe_cit_migration créera ensuite
-- via les migrations Django — pas aux objets déjà existants au moment où
-- ce script s'exécute (il n'y en a aucun, la base est neuve).
ALTER DEFAULT PRIVILEGES FOR ROLE pfe_cit_migration IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO pfe_cit_app;

ALTER DEFAULT PRIVILEGES FOR ROLE pfe_cit_migration IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO pfe_cit_app;
