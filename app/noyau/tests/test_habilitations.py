"""Habilitation — RG-02."""

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command

from noyau.exceptions import ErreurHabilitation
from noyau.habilitations import verifier_habilitation


def test_initialiser_habilitations_est_idempotente(db):
    call_command("initialiser_habilitations")
    premier_etat = set(Group.objects.values_list("name", flat=True))

    call_command("initialiser_habilitations")
    second_etat = set(Group.objects.values_list("name", flat=True))

    assert premier_etat == second_etat
    assert Group.objects.count() == 5


def test_verifier_habilitation_leve_erreur_habilitation(db):
    modele_utilisateur = get_user_model()
    utilisateur = modele_utilisateur.objects.create_user(
        username="essai",
        password="x",
        grade="Lt",
        profil=modele_utilisateur.Profil.ADMINISTRATEUR,
    )
    with pytest.raises(ErreurHabilitation):
        verifier_habilitation(utilisateur, "administration.permission_inexistante")
