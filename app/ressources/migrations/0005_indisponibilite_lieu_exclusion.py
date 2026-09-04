"""Contrainte d'exclusion `ex_indispo_lieu_chevauchement` — § 3.1 du Prompt 14.

Deux indisponibilités du même lieu ne peuvent pas porter des intervalles
`[debut, fin)` sécants. Sans expression déclarative dans l'ORM au même titre
que les index uniques partiels — voir docs/conception/14-note-implementation.md
§ 10.1 — donc écrite en SQL explicite, comme le sera `ex_indispo_chevauchement`
sur les instructeurs à US-INS-03, pour que les deux se lisent pareil.

Intervalle semi-ouvert (`tstzrange` par défaut, borne `[)`) : deux périodes
contiguës (la fin de l'une égale au début de l'autre) ne se recouvrent pas.
`tstzrange`, pas `tsrange` : `debut`/`fin` sont des `timestamptz` (BNF-14).

Dépend explicitement de `("noyau", "0001_extensions")` — `btree_gist` permet
de combiner l'égalité sur `lieu_id` et le recouvrement sur l'intervalle dans
un même index GiST — voir .claude/rules/migrations.md.
"""

from django.db import migrations

POSER = """
ALTER TABLE ressources_indisponibilite_lieu
    ADD CONSTRAINT ex_indispo_lieu_chevauchement
    EXCLUDE USING gist (
        lieu_id WITH =,
        tstzrange(debut, fin) WITH &&
    );
"""

DEFAIRE = """
ALTER TABLE ressources_indisponibilite_lieu
    DROP CONSTRAINT ex_indispo_lieu_chevauchement;
"""


class Migration(migrations.Migration):
    dependencies = [
        ("ressources", "0004_indisponibilite_lieu"),
        ("noyau", "0001_extensions"),
    ]

    operations = [
        migrations.RunSQL(sql=POSER, reverse_sql=DEFAIRE),
    ]
