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


def test_page_de_connexion_porte_le_logo(client):
    """US-IHM-02, critère 1 (prompt 64) : le logo figure sur la page de
    connexion — jamais un chemin en dur, toujours via {% static %}."""
    contenu = client.get(reverse("administration:connexion")).content.decode()
    assert "images/logo.png" in contenu


def test_favicon_pointe_sur_le_logo(client):
    """US-IHM-02, critère 1 : l'onglet du navigateur aussi — vérifié sur une
    page publique (connexion), `base.html` ET `base_public.html` le posent."""
    contenu = client.get(reverse("administration:connexion")).content.decode()
    assert '<link rel="icon" href="/static/images/logo.png">' in contenu


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


def test_le_menu_du_compte_regroupe_deconnexion_et_mot_de_passe(client, django_user_model):
    """US-IHM-02, critère 2 (prompt 64) : les deux actions sont dans le MÊME
    menu déroulant (`<details>`, sans JavaScript) — vérifié par cycle HTTP
    réel, pas seulement en apparence dans le gabarit."""
    utilisateur = django_user_model.objects.create_user(
        username="essai-menu-compte", password="x", grade="Lt", profil=Profil.ADMINISTRATEUR
    )
    utilisateur.doit_changer_mot_de_passe = False
    utilisateur.save()
    client.force_login(utilisateur)

    contenu = client.get(reverse("noyau:accueil")).content.decode()
    debut_menu = contenu.index("<details")
    fin_menu = contenu.index("</details>", debut_menu)
    bloc_menu = contenu[debut_menu:fin_menu]

    assert reverse("administration:changer_mot_de_passe") in bloc_menu
    assert reverse("administration:deconnexion") in bloc_menu
    assert "<script" not in bloc_menu.lower()
