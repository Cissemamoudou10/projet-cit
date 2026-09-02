"""`ck_utilisateur_profil` — la contrainte doit être portée par PostgreSQL,
pas par la validation Python.

Écrit directement en SQL, en contournant l'ORM et `full_clean()` : un test
qui passerait par le formulaire ou par `full_clean()` ne prouverait rien sur
ce point — voir PROMPT_00_socle_technique.md, étape 9.
"""

import pytest
from django.db import IntegrityError, connection, transaction


@pytest.mark.django_db
def test_contrainte_refuse_un_profil_hors_enumeration():
    with pytest.raises(IntegrityError), transaction.atomic(), connection.cursor() as curseur:
        curseur.execute(
            """
                INSERT INTO administration_utilisateur
                    (password, is_superuser, username, first_name, last_name,
                     email, is_staff, is_active, date_joined,
                     grade, profil, echecs_consecutifs, verrouille_jusqu_a,
                     doit_changer_mot_de_passe)
                VALUES
                    (%s, false, %s, '', '', '', false, true, now(),
                     %s, %s, 0, NULL, true)
                """,
            ["x", "intrus", "Lt", "profil_qui_n_existe_pas"],
        )


@pytest.mark.django_db
def test_contrainte_accepte_un_profil_valide():
    with transaction.atomic(), connection.cursor() as curseur:
        curseur.execute(
            """
            INSERT INTO administration_utilisateur
                (password, is_superuser, username, first_name, last_name,
                 email, is_staff, is_active, date_joined,
                 grade, profil, echecs_consecutifs, verrouille_jusqu_a,
                 doit_changer_mot_de_passe)
            VALUES
                (%s, false, %s, '', '', '', false, true, now(),
                 %s, %s, 0, NULL, true)
            """,
            ["x", "conforme", "Lt", "administrateur"],
        )
