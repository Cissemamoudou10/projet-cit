"""Habilitation — RG-02.

`verifier_habilitation` (lève et journalise) vit désormais dans
`administration` — voir docs/suivi/DECISIONS.md, D-09 — et se teste là-bas.
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command

from noyau.habilitations import a_permission


def test_initialiser_habilitations_est_idempotente(db):
    call_command("initialiser_habilitations")
    premier_etat = set(Group.objects.values_list("name", flat=True))

    call_command("initialiser_habilitations")
    second_etat = set(Group.objects.values_list("name", flat=True))

    assert premier_etat == second_etat
    assert Group.objects.count() == 5


def test_a_permission_est_silencieuse_et_retourne_un_booleen(db):
    modele_utilisateur = get_user_model()
    utilisateur = modele_utilisateur.objects.create_user(
        username="essai",
        password="x",
        grade="Lt",
        profil=modele_utilisateur.Profil.CELLULE_PEDAGOGIQUE,
    )
    assert a_permission(utilisateur, "noyau.permission_inexistante") is False
