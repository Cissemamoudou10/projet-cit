"""RG-27 : une entrée de journal est immuable — ni modifiable ni supprimable
par aucun profil, administrateur compris. Portée en base (BNF-11), pas
seulement par l'absence de vue ou de méthode d'édition — voir § 2.1 et 2.3
du Prompt 04. `pfe_cit_app` (rôle applicatif) perd UPDATE et DELETE sur la
table ; INSERT et SELECT restent. `pfe_cit_migration` (rôle des migrations)
n'est pas concerné, il doit pouvoir faire évoluer le schéma.

Distincte de la migration qui pose les champs (0006) : celle-ci ne doit
jamais être rejouée par mégarde avec une migration de schéma ordinaire —
voir docs/suivi/DECISIONS.md, D-02.
"""

from django.db import migrations

REVOQUER = "REVOKE UPDATE, DELETE ON administration_entree_journal FROM pfe_cit_app;"
RETABLIR = "GRANT UPDATE, DELETE ON administration_entree_journal TO pfe_cit_app;"


class Migration(migrations.Migration):
    dependencies = [
        ("administration", "0006_entree_journal_objet_valeurs_index"),
    ]

    operations = [
        migrations.RunSQL(sql=REVOQUER, reverse_sql=RETABLIR),
    ]
