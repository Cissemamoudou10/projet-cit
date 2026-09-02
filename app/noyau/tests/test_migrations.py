"""Ordre des migrations sur une base neuve — point d'irréversibilité du
socle. Si l'ordre n'était pas garanti, ce test échouerait sur une base
neuve, jamais en local où l'ordre accidentel a de bonnes chances d'être le
bon — exactement le piège que `("noyau", "0001_extensions")` en dépendance
explicite (.claude/rules/migrations.md) évite.
"""

import pytest
from django.db import connection


@pytest.mark.django_db
def test_migrate_sur_base_vide_pose_extension_puis_table_utilisateur():
    tables = connection.introspection.table_names()
    assert "administration_utilisateur" in tables
    with connection.cursor() as curseur:
        curseur.execute("SELECT 1 FROM pg_extension WHERE extname = %s", ["btree_gist"])
        assert curseur.fetchone() is not None
