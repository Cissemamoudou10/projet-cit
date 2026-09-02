from django.contrib.postgres.operations import BtreeGistExtension
from django.db import migrations


class Migration(migrations.Migration):
    """Extension PostgreSQL `btree_gist`.

    Sert la contrainte d'exclusion `ex_indispo_chevauchement` (RG-24) qui
    garantit qu'un même instructeur n'a pas deux indisponibilités aux
    intervalles sécants — cette contrainte n'existe pas encore au socle,
    elle vient avec l'application `ressources`.

    Doit être posée ici, avant toute autre migration : `btree_gist` ne peut
    pas être ajoutée plus tard sans réappliquer une migration sur une base
    déjà en production, ce qui est exactement le geste que le socle cherche
    à éviter. Réversible — `BtreeGistExtension` sait défaire ce qu'elle
    fait.

    Toute migration future posant une contrainte d'exclusion doit déclarer
    une dépendance explicite sur `("noyau", "0001_extensions")` — voir
    .claude/rules/migrations.md.
    """

    initial = True

    dependencies = []

    operations = [
        BtreeGistExtension(),
    ]
