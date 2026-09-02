"""Intergiciel de changement de mot de passe obligatoire et vues de gestion
des comptes.
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import NoReverseMatch, reverse

from administration.models import Profil


def test_drapeau_leve_redirige_n_importe_quelle_url(client, administrateur):
    administrateur.doit_changer_mot_de_passe = True
    administrateur.save()
    client.force_login(administrateur)

    reponse = client.get(reverse("noyau:accueil"))

    assert reponse.status_code == 302
    assert reponse.url == reverse("administration:changer_mot_de_passe")


def test_drapeau_leve_sur_l_ecran_de_changement_n_est_pas_redirige(client, administrateur):
    administrateur.doit_changer_mot_de_passe = True
    administrateur.save()
    client.force_login(administrateur)

    reponse = client.get(reverse("administration:changer_mot_de_passe"))

    assert reponse.status_code == 200


def test_drapeau_leve_demandant_la_deconnexion_n_est_pas_redirige(client, administrateur):
    administrateur.doit_changer_mot_de_passe = True
    administrateur.save()
    client.force_login(administrateur)

    reponse = client.post(reverse("administration:deconnexion"))

    assert reponse.status_code == 302
    assert reponse.url == reverse("administration:connexion")


def test_apres_changement_reussi_acces_normal(client, administrateur, mot_de_passe):
    administrateur.doit_changer_mot_de_passe = True
    administrateur.save()
    client.force_login(administrateur)

    client.post(
        reverse("administration:changer_mot_de_passe"),
        {
            "ancien_mot_de_passe": mot_de_passe,
            "nouveau_mot_de_passe": "un-nouveau-mot-de-passe-correct",
            "confirmation": "un-nouveau-mot-de-passe-correct",
        },
    )

    reponse = client.get(reverse("noyau:accueil"))
    assert reponse.status_code == 200


def test_non_administrateur_atteignant_la_liste_est_refuse(client, non_administrateur):
    client.force_login(non_administrateur)

    reponse = client.get(reverse("administration:liste_comptes"))

    assert reponse.status_code == 403


def test_liste_au_dela_de_vingt_comptes_est_paginee(client, administrateur, settings):
    modele = get_user_model()
    for i in range(21):
        modele.objects.create_user(
            username=f"compte-{i}", password="x", grade="Sgt", profil=Profil.CELLULE_PEDAGOGIQUE
        )
    client.force_login(administrateur)

    reponse = client.get(reverse("administration:liste_comptes"))

    assert len(reponse.context["page"].object_list) == settings.TAILLE_PAGE_DEFAUT
    assert reponse.context["page"].paginator.num_pages >= 2


def test_tri_par_identifiant_est_inversable(client, administrateur):
    modele = get_user_model()
    modele.objects.create_user(
        username="aaa-premier", password="x", grade="Sgt", profil=Profil.CELLULE_PEDAGOGIQUE
    )
    modele.objects.create_user(
        username="zzz-dernier", password="x", grade="Sgt", profil=Profil.CELLULE_PEDAGOGIQUE
    )
    client.force_login(administrateur)

    croissant = client.get(reverse("administration:liste_comptes"), {"tri": "identifiant"})
    decroissant = client.get(reverse("administration:liste_comptes"), {"tri": "-identifiant"})

    identifiants_croissant = [c.username for c in croissant.context["page"].object_list]
    identifiants_decroissant = [c.username for c in decroissant.context["page"].object_list]
    assert identifiants_croissant == sorted(identifiants_croissant)
    assert identifiants_decroissant == list(reversed(identifiants_croissant))
    assert croissant.context["tri_identifiant"]["aria"] == "ascending"
    assert decroissant.context["tri_identifiant"]["aria"] == "descending"


def test_recherche_filtre_sur_identifiant_nom_et_grade(client, administrateur):
    modele = get_user_model()
    modele.objects.create_user(
        username="findable-un",
        password="x",
        grade="Sgt",
        last_name="Kadiri",
        profil=Profil.CELLULE_PEDAGOGIQUE,
    )
    modele.objects.create_user(
        username="autre",
        password="x",
        grade="Cne",
        last_name="Alaoui",
        profil=Profil.CELLULE_PEDAGOGIQUE,
    )
    client.force_login(administrateur)

    reponse = client.get(reverse("administration:liste_comptes"), {"recherche": "Kadiri"})

    identifiants = [compte.username for compte in reponse.context["page"].object_list]
    assert "findable-un" in identifiants
    assert "autre" not in identifiants


def test_aucune_vue_ni_url_de_suppression_n_existe():
    with pytest.raises(NoReverseMatch):
        reverse("administration:supprimer_compte")


def test_mot_de_passe_initial_absent_de_toute_reponse_apres_creation(client, administrateur):
    client.force_login(administrateur)
    secret = "un-mot-de-passe-initial-tres-particulier"

    reponse = client.post(
        reverse("administration:creer_compte"),
        {
            "identifiant": "nouveau-vue",
            "grade": "Sgt",
            "prenom": "",
            "nom": "Test",
            "profil": Profil.CELLULE_PEDAGOGIQUE,
            "mot_de_passe": secret,
        },
        follow=True,
    )

    assert secret not in reponse.content.decode()
