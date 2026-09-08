"""Reproduit dans `test_pfe_cit` les privilèges du rôle applicatif de
production — voir Prompt 04, § 2.1 et 2.2.

`ALTER DEFAULT PRIVILEGES` (posé dans `infra/postgres/init/01_roles.sh`) ne
s'applique qu'à la base où il s'exécute (`pfe_cit`) : il ne se propage pas à
`test_pfe_cit`, une base distincte créée après coup par `pfe_cit_migration`.
Sans ce correctif, `pfe_cit_app` n'a strictement aucun privilège sur
`test_pfe_cit` — un test qui prétendrait prouver la révocation RG-27 y
prouverait en réalité l'absence totale de droits, INSERT et SELECT compris.

Regreffe donc les mêmes privilèges qu'en production une fois la base de test
migrée, puis rejoue la révocation ciblée de la migration 0007 — l'état final
de `test_pfe_cit` reproduit exactement celui de `pfe_cit`.
"""

import pytest
from django.db import connection

REGREFFER_PRIVILEGES = """
    GRANT USAGE ON SCHEMA public TO pfe_cit_app;
    GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO pfe_cit_app;
    GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO pfe_cit_app;
"""
REVOQUER_ECRITURE_JOURNAL = (
    "REVOKE UPDATE, DELETE ON administration_entree_journal FROM pfe_cit_app;"
)


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):  # noqa: ARG001 — patron pytest-django : surcharge par redéclaration du même nom
    with django_db_blocker.unblock(), connection.cursor() as curseur:
        curseur.execute(REGREFFER_PRIVILEGES)
        curseur.execute(REVOQUER_ECRITURE_JOURNAL)
    yield
