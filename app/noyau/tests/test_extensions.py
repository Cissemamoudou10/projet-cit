"""Extension PostgreSQL `btree_gist` — RG-24, migration 0001_extensions."""

import pytest
from django.db import connection


@pytest.mark.django_db
def test_extension_btree_gist_presente():
    with connection.cursor() as curseur:
        curseur.execute("SELECT 1 FROM pg_extension WHERE extname = %s", ["btree_gist"])
        assert curseur.fetchone() is not None
