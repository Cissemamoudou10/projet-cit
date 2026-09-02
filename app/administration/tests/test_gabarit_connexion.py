"""Gabarits de connexion et d'accueil — Prompt 01, § 7.1 et critère 1."""

import pytest
from django.urls import reverse

from administration.models import Profil


def test_page_de_connexion_rend_sans_session_ni_exception(client):
    reponse = client.get(reverse("administration:connexion"))
    assert reponse.status_code == 200


def test_page_de_connexion_sans_en_tete_ni_fil_ariane(client):
    contenu = client.get(reverse("administration:connexion")).content.decode()
    assert "CENTRE D'INSTRUCTION" not in contenu
    assert "Fil d'Ariane" not in contenu


def test_page_de_connexion_sans_largeur_minimale_imposee(client):
    contenu = client.get(reverse("administration:connexion")).content.decode()
    assert "min-w-[1280px]" not in contenu


@pytest.mark.parametrize("profil", list(Profil))
def test_chaque_profil_atteint_l_accueil_avec_un_contenu_distinct(
    client, django_user_model, profil
):
    utilisateur = django_user_model.objects.create_user(
        username=f"essai-{profil.value}", password="x", grade="Lt", profil=profil
    )
    utilisateur.doit_changer_mot_de_passe = False  # sans quoi l'intergiciel (US-ADM-02) redirige
    utilisateur.save()
    client.force_login(utilisateur)

    reponse = client.get(reverse("noyau:accueil"))

    assert reponse.status_code == 200
    assert profil.label in reponse.content.decode()
