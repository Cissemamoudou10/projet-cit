"""US-PLAN-02 — écrans de gestion des lieux. Le modèle et le service sont
testés dans test_lieu.py.
"""

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from ressources.models import CategorieLieu, Lieu
from ressources.services.lieu import ServiceLieu
from ressources.tests.test_lieu import _donnees


def test_l_onglet_lieux_permet_d_atteindre_les_lieux_depuis_les_instructeurs(client, planificateur):
    """D-57 : P-26 signalait qu'aucun chemin de navigation ne menait aux
    lieux depuis la rubrique « Ressources ». Corrigé par un onglet — pas par
    une seconde rubrique, qui s'écartait de la maquette de référence
    (`docs/conception/16-maquettes.md`)."""
    client.force_login(planificateur)

    reponse = client.get(reverse("ressources:liste_instructeurs")).content.decode()

    assert reverse("ressources:liste_lieux") in reponse


def test_quatre_onglets_pour_la_cellule_examens_jamais_instructeurs(client, cellule_examens):
    """DECISIONS.md D-115/D-120 : la cellule examens gagne les onglets du
    domaine `lieux_calendrier` qu'elle détient (Lieux, Indisponibilités,
    Calendrier — US-PLAN-01, Grilles horaires — US-PLAN-12) sans jamais
    gagner l'onglet Instructeurs, elle n'a toujours pas
    `instructeurs_qualifications_lecture` (§ 4.1 du Prompt 12)."""
    client.force_login(cellule_examens)

    reponse = client.get(reverse("ressources:liste_lieux"))

    slugs = {onglet["slug"] for onglet in reponse.context["onglets"]}
    assert slugs == {"lieux", "indisponibilites-instructeurs", "calendrier", "grilles-horaires"}
    assert "Instructeurs" not in reponse.content.decode()


def test_la_rubrique_ressources_est_surlignee_active_sur_les_ecrans_de_lieux(client, planificateur):
    client.force_login(planificateur)

    reponse = client.get(reverse("ressources:liste_lieux"))

    assert reponse.context["rubrique_active"] == "ressources"
    assert reponse.context["onglet_actif"] == "lieux"


def test_acces_direct_a_la_liste_ouvert_a_la_cellule_pedagogique(client, redacteur):
    """Matrice § 11.2 : inversion des habilitations par rapport aux
    stories précédentes — la cellule pédagogique lit ici, elle n'écrit pas.
    """
    client.force_login(redacteur)

    reponse = client.get(reverse("ressources:liste_lieux"))

    assert reponse.status_code == 200


def test_planification_consulte_la_liste_et_la_fiche(client, planificateur, redacteur):
    lieu = ServiceLieu.creer(planificateur, _donnees())
    client.force_login(planificateur)

    reponse_liste = client.get(reverse("ressources:liste_lieux"))
    reponse_fiche = client.get(reverse("ressources:detail_lieu", args=[lieu.pk]))

    assert reponse_liste.status_code == 200
    assert reponse_fiche.status_code == 200
    assert "Salle 101" in reponse_fiche.content.decode()


def test_pedagogie_ne_voit_ni_creer_ni_modifier_ni_archiver(client, planificateur, redacteur):
    """Matrice § 11.2 : la cellule pédagogique lit seulement."""
    lieu = ServiceLieu.creer(planificateur, _donnees())
    client.force_login(redacteur)

    reponse_liste = client.get(reverse("ressources:liste_lieux")).content.decode()
    reponse_fiche = client.get(reverse("ressources:detail_lieu", args=[lieu.pk])).content.decode()

    assert "Créer un lieu" not in reponse_liste
    assert 'title="Modifier"' not in reponse_liste
    assert "Modifier" not in reponse_fiche


def test_pedagogie_ne_peut_pas_creer_par_appel_direct(client, redacteur):
    client.force_login(redacteur)

    reponse = client.post(reverse("ressources:creer_lieu"), _donnees())

    assert reponse.status_code == 403


def test_examens_et_direction_lisent_seulement(client, cellule_examens, direction_formation):
    for utilisateur in (cellule_examens, direction_formation):
        client.force_login(utilisateur)
        reponse_liste = client.get(reverse("ressources:liste_lieux"))
        assert reponse_liste.status_code == 200

        reponse_creation = client.post(reverse("ressources:creer_lieu"), _donnees())
        assert reponse_creation.status_code == 403


def test_le_badge_de_categorie_distingue_les_deux_valeurs_par_le_mot(client, planificateur):
    """§ 1.2 de la charte : la couleur est doublée d'un mot."""
    ServiceLieu.creer(planificateur, _donnees())
    ServiceLieu.creer(
        planificateur,
        _donnees(
            intitule="Amphi A",
            categorie=CategorieLieu.LIEU_PARTAGE,
            type_partage="amphitheatre",
        ),
    )
    client.force_login(planificateur)

    contenu = client.get(reverse("ressources:liste_lieux")).content.decode()

    assert "SALLE ATTITRABLE" in contenu
    assert "LIEU PARTAGÉ" in contenu


def test_modifier_par_le_vrai_formulaire_html_ne_declenche_pas_a_tort_e5(client, planificateur):
    lieu = ServiceLieu.creer(planificateur, _donnees())
    client.force_login(planificateur)

    reponse_get = client.get(reverse("ressources:modifier_lieu", args=[lieu.pk]))
    modifie_le_attendu = reponse_get.context["modifie_le_attendu"]

    reponse_post = client.post(
        reverse("ressources:modifier_lieu", args=[lieu.pk]),
        {**_donnees(), "capacite": 45, "modifie_le_attendu": modifie_le_attendu.isoformat()},
    )

    assert reponse_post.status_code == 302
    lieu.refresh_from_db()
    assert lieu.capacite == 45


def test_suppression_d_un_lieu_jamais_utilise_reussit_depuis_l_ecran(client, planificateur):
    """Prompt 16, cause racine n° 3 : aucune route de suppression n'existait
    pour les lieux."""
    lieu = ServiceLieu.creer(planificateur, _donnees())
    client.force_login(planificateur)

    reponse_get = client.get(reverse("ressources:supprimer_lieu", args=[lieu.pk]))
    assert reponse_get.status_code == 200

    reponse_post = client.post(reverse("ressources:supprimer_lieu", args=[lieu.pk]))

    assert reponse_post.status_code == 302
    assert not Lieu.objects.filter(pk=lieu.pk).exists()


# Bloc D.2 du Prompt 19 — priorité 3 : preuve d'un effet réel, pas d'un
# code de retour (P-21).


def test_creer_par_l_ecran_cree_reellement_le_lieu(client, planificateur):
    client.force_login(planificateur)

    client.post(reverse("ressources:creer_lieu"), _donnees())

    assert Lieu.objects.filter(intitule="Salle 101").exists()


def test_archiver_par_l_ecran_le_retire_reellement_de_la_selection(client, planificateur):
    lieu = ServiceLieu.creer(planificateur, _donnees())
    client.force_login(planificateur)

    client.post(reverse("ressources:archiver_lieu", args=[lieu.pk]))

    assert lieu.pk not in [ligne.pk for ligne in ServiceLieu.disponibles_pour_selection()]


def test_desarchiver_par_l_ecran_le_rend_reellement_a_la_selection(client, planificateur):
    lieu = ServiceLieu.creer(planificateur, _donnees())
    ServiceLieu.archiver(planificateur, lieu.pk)
    client.force_login(planificateur)

    client.post(reverse("ressources:desarchiver_lieu", args=[lieu.pk]))

    assert lieu.pk in [ligne.pk for ligne in ServiceLieu.disponibles_pour_selection()]


def test_declarer_une_indisponibilite_par_le_formulaire(client, planificateur, lieu):
    client.force_login(planificateur)

    reponse = client.post(
        reverse("ressources:declarer_indisponibilite_lieu", args=[lieu.pk]),
        {
            "debut": "2027-01-04T08:00",
            "fin": "2027-01-04T12:00",
            "motif": "Réfection du sol",
        },
    )

    assert reponse.status_code == 302
    assert lieu.indisponibilites.count() == 1


def test_declarer_une_indisponibilite_refusee_a_la_cellule_pedagogique(client, redacteur, lieu):
    client.force_login(redacteur)

    reponse = client.post(
        reverse("ressources:declarer_indisponibilite_lieu", args=[lieu.pk]),
        {"debut": "2027-01-04T08:00", "fin": "2027-01-04T12:00", "motif": "Réfection du sol"},
    )

    assert reponse.status_code == 403


def test_nombre_de_requetes_de_la_liste_des_lieux_ne_depend_pas_du_nombre_de_lignes(
    client, planificateur
):
    """Prompt 17, § 2.6 — le test obligatoire."""
    client.force_login(planificateur)
    url = reverse("ressources:liste_lieux")
    for i in range(5):
        ServiceLieu.creer(planificateur, _donnees(intitule=f"Salle {i:02d}"))
    with CaptureQueriesContext(connection) as capture_cinq:
        client.get(url)

    for i in range(5, 20):
        ServiceLieu.creer(planificateur, _donnees(intitule=f"Salle {i:02d}"))
    with CaptureQueriesContext(connection) as capture_vingt:
        client.get(url)

    assert len(capture_vingt) == len(capture_cinq)
