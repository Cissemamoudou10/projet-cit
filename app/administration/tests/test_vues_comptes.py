"""Intergiciel de changement de mot de passe obligatoire et vues de gestion
des comptes.
"""

import pytest
from django.contrib.auth import get_user_model
from django.urls import NoReverseMatch, reverse

from administration.models import Profil


def test_la_rubrique_administration_est_surlignee_sur_ses_propres_pages(client, administrateur):
    """`rubrique_active` se déduit de l'URL résolue, jamais renseigné par la
    vue — voir noyau/context_processors.py. Une page d'administration doit
    donc surligner la rubrique « Administration », pas rester neutre.
    """
    client.force_login(administrateur)

    reponse = client.get(reverse("administration:liste_comptes"))
    contenu = reponse.content.decode()

    assert 'aria-current="page"' in contenu
    index = contenu.index('aria-current="page"')
    assert "Administration" in contenu[index : index + 200]


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


def test_lien_mot_de_passe_present_dans_l_en_tete_hors_contrainte(client, administrateur):
    """Correctif de navigation, prompt 49 (hors backlog) : l'écran de
    changement de mot de passe n'était atteint que par redirection forcée
    (drapeau levé) — aucun lien volontaire pour un changement hors
    contrainte, décision du chef de projet (2026-10-25)."""
    client.force_login(administrateur)

    reponse = client.get(reverse("noyau:accueil"))

    assert reverse("administration:changer_mot_de_passe") in reponse.content.decode()


def test_ecran_hors_contrainte_n_affiche_pas_le_texte_obligatoire(client, administrateur):
    client.force_login(administrateur)

    reponse = client.get(reverse("administration:changer_mot_de_passe"))
    contenu = reponse.content.decode()

    assert "Changer mon mot de passe" in contenu
    assert "obligatoire" not in contenu
    assert "Retour à l'accueil" in contenu


def test_ecran_sous_contrainte_affiche_bien_le_texte_obligatoire(client, administrateur):
    administrateur.doit_changer_mot_de_passe = True
    administrateur.save()
    client.force_login(administrateur)

    reponse = client.get(reverse("administration:changer_mot_de_passe"))
    contenu = reponse.content.decode()

    assert "obligatoire" in contenu
    assert "Retour à l'accueil" not in contenu


def test_changement_volontaire_hors_contrainte_ecrit_reellement(client, administrateur, mot_de_passe):
    client.force_login(administrateur)

    reponse = client.post(
        reverse("administration:changer_mot_de_passe"),
        {
            "ancien_mot_de_passe": mot_de_passe,
            "nouveau_mot_de_passe": "un-nouveau-mot-de-passe-correct",
            "confirmation": "un-nouveau-mot-de-passe-correct",
        },
    )

    assert reponse.status_code == 302
    client.logout()
    assert client.login(username=administrateur.username, password="un-nouveau-mot-de-passe-correct")


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


# Bloc D.2 du Prompt 19 — priorité 2 : trois écrans sans aucun test HTTP réel
# avant ce prompt (ni écriture, ni refus), révélé par l'audit
# docs/suivi/COUVERTURE-HTTP.md. Chaque test prouve un effet réel en base,
# pas seulement un code de retour (leçon de P-21).


def test_le_compte_existe_reellement_apres_creation_par_l_ecran(client, administrateur):
    client.force_login(administrateur)

    client.post(
        reverse("administration:creer_compte"),
        {
            "identifiant": "cree-par-ecran",
            "grade": "Sgt",
            "prenom": "Amine",
            "nom": "Test",
            "profil": Profil.CELLULE_PLANIFICATION,
            "mot_de_passe": "un-mot-de-passe-suffisamment-long",
        },
    )

    compte = get_user_model().objects.get(username="cree-par-ecran")
    assert compte.profil == Profil.CELLULE_PLANIFICATION
    assert compte.groups.filter(name="Cellule planification").exists()


def test_modifier_par_l_ecran_change_reellement_le_compte(client, administrateur):
    cible = get_user_model().objects.create_user(
        username="a-modifier", password="x", grade="Sgt", profil=Profil.CELLULE_PEDAGOGIQUE
    )
    client.force_login(administrateur)

    client.post(
        reverse("administration:modifier_compte", args=[cible.pk]),
        {
            "identifiant": "a-modifier",
            "grade": "Cne",
            "prenom": "",
            "nom": "Nom modifié",
            "profil": Profil.CELLULE_PLANIFICATION,
        },
    )

    cible.refresh_from_db()
    assert cible.grade == "Cne"
    assert cible.last_name == "Nom modifié"
    assert cible.profil == Profil.CELLULE_PLANIFICATION
    assert cible.groups.filter(name="Cellule planification").exists()
    assert not cible.groups.filter(name="Cellule pédagogique").exists()


def test_desactiver_par_l_ecran_desactive_reellement_le_compte(client, administrateur):
    cible = get_user_model().objects.create_user(
        username="a-desactiver", password="x", grade="Sgt", profil=Profil.CELLULE_PEDAGOGIQUE
    )
    client.force_login(administrateur)
    assert cible.is_active

    client.post(reverse("administration:desactiver_compte", args=[cible.pk]))

    cible.refresh_from_db()
    assert not cible.is_active


def test_reactiver_par_l_ecran_reactive_reellement_le_compte(client, administrateur):
    cible = get_user_model().objects.create_user(
        username="a-reactiver", password="x", grade="Sgt", profil=Profil.CELLULE_PEDAGOGIQUE
    )
    cible.is_active = False
    cible.save()
    client.force_login(administrateur)

    client.post(reverse("administration:reactiver_compte", args=[cible.pk]))

    cible.refresh_from_db()
    assert cible.is_active
