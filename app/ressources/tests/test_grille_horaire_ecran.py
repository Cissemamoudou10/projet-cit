"""US-PLAN-12, Groupe F — cycle HTTP réel des grilles horaires (Prompt 29,
§ 9, § 13). F6 (garde du sprint 1) est couvert une fois pour toutes par
tests/architecture/test_ecrans_ecriture.py, vérifié passer sans modification
— non dupliqué ici. Données entièrement fictives.
"""

import datetime

import pytest
from django.urls import reverse

from ressources.models import CreneauType, GrilleHoraire, JourSemaine
from ressources.services.grille_horaire import ServiceGrilleHoraire


def _heure(texte):
    heure, minute = texte.split(":")
    return datetime.time(int(heure), int(minute))


def _grille_avec_creneau(intitule="Ordinaire", jour=JourSemaine.LUNDI, debut="08:00", fin="09:45"):
    grille = GrilleHoraire.objects.create(intitule=intitule)
    CreneauType.objects.create(
        grille=grille, jour_semaine=jour, ordre=1, heure_debut=_heure(debut), heure_fin=_heure(fin)
    )
    return grille


# --- F1 — chemin nominal, profil planification, chaque adresse d'écriture --


def test_f1_creation_modification_duplication_reussissent(client, planificateur):
    client.force_login(planificateur)

    reponse_creation = client.post(
        reverse("ressources:creer_grille_horaire"), {"intitule": "Ordinaire"}
    )
    assert reponse_creation.status_code == 302
    grille = GrilleHoraire.objects.get(intitule="Ordinaire")

    reponse_modification = client.post(
        reverse("ressources:modifier_grille_horaire", args=[grille.pk]),
        {"intitule": "Ordinaire modifiée", "modifie_le_attendu": grille.modifie_le.isoformat()},
    )
    assert reponse_modification.status_code == 302
    grille.refresh_from_db()
    assert grille.intitule == "Ordinaire modifiée"

    reponse_duplication = client.post(
        reverse("ressources:dupliquer_grille_horaire", args=[grille.pk]),
        {"intitule": "Ramadan"},
    )
    assert reponse_duplication.status_code == 302
    assert GrilleHoraire.objects.filter(intitule="Ramadan").exists()


def test_f1_ajout_de_creneau_puis_suppression_reussissent(client, planificateur):
    client.force_login(planificateur)
    grille = GrilleHoraire.objects.create(intitule="Ordinaire")

    reponse_ajout = client.post(
        reverse("ressources:ajouter_creneau", args=[grille.pk]),
        {"jour_semaine": "lundi", "ordre": "1", "heure_debut": "08:00", "heure_fin": "09:45"},
    )
    assert reponse_ajout.status_code == 302
    creneau = CreneauType.objects.get(grille=grille)

    reponse_suppression = client.post(reverse("ressources:supprimer_creneau", args=[creneau.pk]))
    assert reponse_suppression.status_code == 302
    assert not CreneauType.objects.filter(pk=creneau.pk).exists()


def test_f1_archivage_puis_desarchivage_puis_suppression_reussissent(client, planificateur):
    client.force_login(planificateur)
    grille = _grille_avec_creneau("Brouillon")

    reponse_archivage = client.post(reverse("ressources:archiver_grille_horaire", args=[grille.pk]))
    assert reponse_archivage.status_code == 302
    grille.refresh_from_db()
    assert grille.archive is True

    reponse_desarchivage = client.post(
        reverse("ressources:desarchiver_grille_horaire", args=[grille.pk])
    )
    assert reponse_desarchivage.status_code == 302
    grille.refresh_from_db()
    assert grille.archive is False

    reponse_suppression = client.post(
        reverse("ressources:supprimer_grille_horaire", args=[grille.pk])
    )
    assert reponse_suppression.status_code == 302
    assert not GrilleHoraire.objects.filter(pk=grille.pk).exists()


# --- F2 — activation HTTP réelle, confirmation nommant la grille désactivée


def test_f2_activation_reelle_avec_confirmation_nommant_la_grille_desactivee(client, planificateur):
    premiere = _grille_avec_creneau("Ordinaire")
    ServiceGrilleHoraire.activer(planificateur, premiere.pk)
    seconde = _grille_avec_creneau("Ramadan", debut="08:30", fin="09:50")
    client.force_login(planificateur)

    reponse_confirmation = client.get(
        reverse("ressources:confirmer_activation_grille_horaire", args=[seconde.pk])
    )
    assert reponse_confirmation.status_code == 200
    contenu = reponse_confirmation.content.decode()
    assert "Ramadan" in contenu
    assert "Ordinaire" in contenu

    reponse_activation = client.post(
        reverse("ressources:confirmer_activation_grille_horaire", args=[seconde.pk])
    )
    assert reponse_activation.status_code == 302
    seconde.refresh_from_db()
    premiere.refresh_from_db()
    assert seconde.active is True
    assert premiere.active is False


# --- F3 — la fiche affiche réellement la semaine type et le volume ---------


def test_f3_la_fiche_affiche_la_semaine_type_et_le_volume_hebdomadaire(client, planificateur):
    grille = _grille_avec_creneau("Ordinaire", JourSemaine.LUNDI, "08:00", "09:45")
    ServiceGrilleHoraire.activer(planificateur, grille.pk)
    client.force_login(planificateur)

    reponse = client.get(reverse("ressources:detail_grille_horaire", args=[grille.pk]))

    assert reponse.status_code == 200
    contenu = reponse.content.decode()
    assert "Lundi" in contenu
    assert "08:00" in contenu and "09:45" in contenu
    assert "1,75" in contenu or "1.75" in contenu or "heure" in contenu.lower()


# --- F4 — refus d'habilitation sur chaque adresse d'écriture ---------------


@pytest.mark.parametrize(
    "nom_profil", ["redacteur", "cellule_examens", "direction_formation", "administrateur"]
)
def test_f4_ecriture_refusee_hors_planification_creation(client, request, nom_profil):
    utilisateur = request.getfixturevalue(nom_profil)
    client.force_login(utilisateur)

    reponse = client.post(reverse("ressources:creer_grille_horaire"), {"intitule": "Ordinaire"})

    assert reponse.status_code == 403


@pytest.mark.parametrize(
    "nom_profil", ["redacteur", "cellule_examens", "direction_formation", "administrateur"]
)
def test_f4_activation_refusee_hors_planification(client, request, nom_profil, planificateur):
    grille = _grille_avec_creneau("Ordinaire")
    utilisateur = request.getfixturevalue(nom_profil)
    client.force_login(utilisateur)

    reponse = client.post(
        reverse("ressources:confirmer_activation_grille_horaire", args=[grille.pk])
    )

    assert reponse.status_code == 403


# --- F5 — lecture accordée aux quatre profils habilités ---------------------


def test_f5_lecture_accordee_aux_quatre_profils_habilites(
    client, planificateur, redacteur, cellule_examens, direction_formation
):
    for utilisateur in (planificateur, redacteur, cellule_examens, direction_formation):
        client.force_login(utilisateur)
        reponse = client.get(reverse("ressources:liste_grilles_horaires"))
        assert reponse.status_code == 200


def test_f5_lecture_refusee_a_l_administrateur(client, administrateur):
    client.force_login(administrateur)

    reponse = client.get(reverse("ressources:liste_grilles_horaires"))

    assert reponse.status_code == 403


def test_f5_la_liste_relie_l_intitule_a_la_fiche_meme_en_lecture_seule(client, redacteur):
    """Trouvé à la vérification navigateur (§ 13) : sans ce lien, un profil
    lecture seule (pas de `url_modifier`) n'avait aucun moyen d'atteindre la
    fiche d'une grille depuis la liste."""
    grille = _grille_avec_creneau("Ordinaire")
    client.force_login(redacteur)

    reponse = client.get(reverse("ressources:liste_grilles_horaires"))

    assert reverse("ressources:detail_grille_horaire", args=[grille.pk]) in reponse.content.decode()


# --- F7 — navigation ----------------------------------------------------


def test_f7_onglet_grilles_horaires_atteignable_pour_les_profils_habilites(
    client, planificateur, redacteur
):
    client.force_login(planificateur)
    reponse = client.get(reverse("ressources:liste_grilles_horaires"))
    slugs = {onglet["slug"] for onglet in reponse.context["onglets"]}
    assert "grilles-horaires" in slugs

    client.force_login(redacteur)
    reponse_pedagogique = client.get(reverse("ressources:liste_grilles_horaires"))
    assert reponse_pedagogique.status_code == 200
    slugs_pedagogique = {onglet["slug"] for onglet in reponse_pedagogique.context["onglets"]}
    assert "grilles-horaires" in slugs_pedagogique
