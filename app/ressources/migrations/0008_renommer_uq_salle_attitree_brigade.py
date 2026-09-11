"""Renomme la contrainte d'unicité implicite du `OneToOneField` pour suivre
la convention `uq_` (.claude/rules/migrations.md, § Nommage) — Django nomme
cette contrainte lui-même (`<table>_<colonne>_key`), sans offrir de moyen
déclaratif de la nommer autrement pour un `OneToOneField` : renommage
explicite, réversible, plutôt qu'un doublon de contrainte.
"""

from django.db import migrations

RENOMMER = """
    ALTER TABLE ressources_salle_attitree
    RENAME CONSTRAINT ressources_salle_attitree_brigade_id_key
    TO uq_salle_attitree_brigade;
"""

RETABLIR = """
    ALTER TABLE ressources_salle_attitree
    RENAME CONSTRAINT uq_salle_attitree_brigade
    TO ressources_salle_attitree_brigade_id_key;
"""


class Migration(migrations.Migration):

    dependencies = [
        ("ressources", "0007_salleattitree"),
    ]

    operations = [
        migrations.RunSQL(RENOMMER, reverse_sql=RETABLIR),
    ]
