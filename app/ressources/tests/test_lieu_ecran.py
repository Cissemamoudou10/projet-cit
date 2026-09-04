"""US-PLAN-02 — écrans de gestion des lieux. Le modèle et le service sont
testés dans test_lieu.py.
"""

from django.urls import reverse

from ressources.models import CategorieLieu
from ressources.services.lieu import ServiceLieu
from ressources.tests.test_lieu import _donnees


def test_la_rubrique_lieux_apparait_pour_la_planification(client, planificateur):
    """P-26 : la rubrique « Ressources » (US-INS-01) ne portait qu'un lien
    vers les instructeurs — aucun chemin de navigation ne menait aux lieux,
    y compris pour un profil qui n'a que `lieux_calendrier_lecture`.
    """
    client.force_login(planificateur)

    reponse = client.get(reverse("noyau:accueil"))

    assert "Lieux" in reponse.content.decode()


def test_la_rubrique_lieux_apparait_pour_la_cellule_examens_sans_acces_instructeurs(
    client, cellule_examens
):
    """La cellule examens n'a pas `instructeurs_qualifications_lecture` (§ 4.1
    du Prompt 12) mais lit `lieux_calendrier` (matrice § 11.2) : elle doit
    voir la rubrique Lieux même sans voir « Ressources »."""
    client.force_login(cellule_examens)

    reponse = client.get(reverse("noyau:accueil")).content.decode()

    assert "Lieux" in reponse
    assert "Ressources" not in reponse


def test_la_rubrique_lieux_est_surlignee_active_sur_les_ecrans_de_lieux(client, planificateur):
    client.force_login(planificateur)

    reponse = client.get(reverse("ressources:liste_lieux"))

    assert reponse.context["rubrique_active"] == "lieux"


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
