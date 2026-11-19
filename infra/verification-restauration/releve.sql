-- Relevé de vérification de restauration — prompt 66, § 4.
--
-- Sortie stable et triée, pour un `diff` direct entre avant et après une
-- restauration : une ligne « table|nombre_de_lignes » par table du schéma
-- public (comptage exact — jamais les statistiques de `pg_stat_user_tables`,
-- qui ne reflètent que le dernier VACUUM/ANALYSE et peuvent mentir juste
-- après une restauration) ; puis les deux privilèges RG-27 sur la table du
-- journal pour le rôle applicatif ; puis le nombre de migrations appliquées.
--
-- Lecture seule : aucune commande n'écrit ni ne modifie quoi que ce soit.
--
-- Le rôle applicatif est passé en variable psql (-v app_role=...), jamais en
-- dur : la migration 0007_revoquer_ecriture_journal fixe la révocation sur
-- le nom littéral `pfe_cit_app`, mais `.env.exemple` laisse `BASE_UTILISATEUR`
-- techniquement modifiable par installation. Ce relevé doit rester correct
-- même si le rôle a été renommé — il vérifie l'état réel, pas une hypothèse
-- sur son nom.
\set ON_ERROR_STOP on

-- 1) comptage exact, par table, trié par nom de table
SELECT table_name || '|' || (xpath(
    '/row/c/text()',
    query_to_xml(format('SELECT count(*) AS c FROM %I.%I', table_schema, table_name), false, true, '')
))[1]::text::bigint
FROM information_schema.tables
WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
ORDER BY table_name;

-- 2) immuabilité du journal (RG-27) — attendu : f (false) dans les deux cas
SELECT 'administration_entree_journal.update|' || has_table_privilege(:'app_role', 'administration_entree_journal', 'UPDATE')::text;
SELECT 'administration_entree_journal.delete|' || has_table_privilege(:'app_role', 'administration_entree_journal', 'DELETE')::text;

-- 3) nombre de migrations appliquées
SELECT 'migrations_appliquees|' || count(*)::text FROM django_migrations;
