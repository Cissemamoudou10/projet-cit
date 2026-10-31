"""US-PLAN-03 — Groupe G : cycle HTTP réel. Prompt 31, § 12. G4 (refus
d'habilitation) et G6 (garde du sprint 1) sont couverts une fois pour toutes
par `tests/architecture/test_ecrans_ecriture.py` (entrée `planification:
lancement_generation`) — voir sa docstring. Données entièrement fictives.
"""

from django.urls import reverse

from planification.models import ProgrammeHebdomadaire, Seance
from planification.tests.conftest import qualifier


def test_g1_chemin_nominal_profil_planification(client, scenario, cours, brigade_formation):
    """C1 (correction de NC R00-GEN-03, prompt 53, Temps 3) : la génération
    atterrit sur la consultation du programme, résumé en tête — jamais une
    page de compte rendu à part."""
    qualifier(cours.instructeur, cours.element.matiere)
    client.force_login(scenario.planificateur)

    assert client.get(reverse("planification:lancement_generation")).status_code == 200

    reponse = client.post(
        reverse("planification:lancement_generation"),
        {"semaine": scenario.lundi.isoformat(), "brigades": [brigade_formation.pk]},
        follow=True,
    )

    assert reponse.status_code == 200
    assert reponse.redirect_chain[-1][0].startswith(
        reverse("planification:consultation_programme")
    )
    assert "placée" in reponse.content.decode("utf-8")
    programme = ProgrammeHebdomadaire.objects.get(lundi_de_semaine=scenario.lundi)
    assert Seance.objects.filter(programme=programme).exists()


def test_g1_bis_lancement_affiche_l_etat_existant_avant_soumission(
    client, scenario, cours, brigade_formation
):
    """Retour du 17/09 : l'agent doit savoir qu'il complète ou régénère
    AVANT de lancer (§ 9) — pas seulement à la confirmation qui suit
    l'envoi."""
    qualifier(cours.instructeur, cours.element.matiere)
    client.force_login(scenario.planificateur)
    client.post(
        reverse("planification:lancement_generation"),
        {"semaine": scenario.lundi.isoformat(), "brigades": [brigade_formation.pk]},
    )

    reponse = client.get(
        reverse("planification:lancement_generation"), {"semaine": scenario.lundi.isoformat()}
    )

    contenu = reponse.content.decode("utf-8")
    assert reponse.status_code == 200
    assert str(brigade_formation.session) in contenu
    assert "régénération" in contenu
    assert reverse("planification:consultation_programme") in contenu  # lien de retour


def test_g1_ter_lancement_conserve_la_selection_apres_erreur_de_validation(
    client, scenario, brigade_formation
):
    """Une soumission invalide (aucune brigade cochée) ne doit pas faire
    disparaître la semaine déjà choisie ni la liste des brigades."""
    client.force_login(scenario.planificateur)

    reponse = client.post(
        reverse("planification:lancement_generation"),
        {"semaine": scenario.lundi.isoformat(), "brigades": []},
    )

    contenu = reponse.content.decode("utf-8")
    assert reponse.status_code == 200
    assert str(brigade_formation.designation) in contenu


def test_g2_regeneration_avec_confirmation_nommant_les_brigades(
    client, scenario, cours, brigade_formation
):
    qualifier(cours.instructeur, cours.element.matiere)
    client.force_login(scenario.planificateur)
    client.post(
        reverse("planification:lancement_generation"),
        {"semaine": scenario.lundi.isoformat(), "brigades": [brigade_formation.pk]},
    )

    reponse = client.post(
        reverse("planification:lancement_generation"),
        {"semaine": scenario.lundi.isoformat(), "brigades": [brigade_formation.pk]},
    )

    contenu = reponse.content.decode("utf-8")
    assert reponse.status_code == 200
    assert str(brigade_formation) in contenu
    assert "égénér" in contenu  # « régénérer »/« Régénérer »

    confirmation = client.post(
        reverse("planification:lancement_generation"),
        {
            "semaine": scenario.lundi.isoformat(),
            "brigades": [brigade_formation.pk],
            "confirme": "on",
        },
        follow=True,
    )
    assert confirmation.status_code == 200
    assert confirmation.redirect_chain[-1][0].startswith(
        reverse("planification:consultation_programme")
    )
    assert "placée" in confirmation.content.decode("utf-8")


def test_g3_consultation_une_ligne_par_brigade_avec_ad_groupement(
    client, scenario, cours, brigade_formation
):
    """Volume prescrit bas : une seule case se pourvoit, les autres
    restent vides — sans quoi la brigade remplirait les dix cases
    ouvertes et aucun AD/GROUPEMENT ne serait jamais visible."""
    cours.element.volume_horaire_prescrit = 2
    cours.element.save()
    qualifier(cours.instructeur, cours.element.matiere)
    client.force_login(scenario.planificateur)
    client.post(
        reverse("planification:lancement_generation"),
        {"semaine": scenario.lundi.isoformat(), "brigades": [brigade_formation.pk]},
    )

    reponse = client.get(
        reverse("planification:consultation_programme"), {"semaine": scenario.lundi.isoformat()}
    )

    contenu = reponse.content.decode("utf-8")
    assert reponse.status_code == 200
    assert str(brigade_formation) in contenu
    assert "AD/GROUPEMENT" in contenu


def test_g3_bis_consultation_par_jour_isole_un_seul_jour(
    client, scenario, cours, brigade_formation
):
    """Retour du 17/09 : la semaine entière dans une seule table était trop
    encombrée — un onglet par jour, un seul jour affiché à la fois."""
    qualifier(cours.instructeur, cours.element.matiere)
    client.force_login(scenario.planificateur)
    client.post(
        reverse("planification:lancement_generation"),
        {"semaine": scenario.lundi.isoformat(), "brigades": [brigade_formation.pk]},
    )

    reponse_lundi = client.get(
        reverse("planification:consultation_programme"),
        {"semaine": scenario.lundi.isoformat(), "jour": "lundi"},
    )
    reponse_mardi = client.get(
        reverse("planification:consultation_programme"),
        {"semaine": scenario.lundi.isoformat(), "jour": "mardi"},
    )

    assert reponse_lundi.status_code == reponse_mardi.status_code == 200
    contenu_lundi = reponse_lundi.content.decode("utf-8")
    contenu_mardi = reponse_mardi.content.decode("utf-8")
    assert "Mardi" in contenu_lundi  # l'onglet reste visible
    assert contenu_lundi.count("Créneau 1") == 1
    assert contenu_mardi.count("Créneau 1") == 1


def test_g3_ter_consultation_groupee_par_type_de_formation_avec_progression(
    client, scenario, cours, brigade_formation
):
    """§ 9 : la grille regroupe par type de formation et porte la
    progression (volume cumulé / prescrit), pas seulement matière/lieu."""
    qualifier(cours.instructeur, cours.element.matiere)
    client.force_login(scenario.planificateur)
    client.post(
        reverse("planification:lancement_generation"),
        {"semaine": scenario.lundi.isoformat(), "brigades": [brigade_formation.pk]},
    )
    type_formation = brigade_formation.session.formation.type_formation

    reponse = client.get(
        reverse("planification:consultation_programme"),
        {"semaine": scenario.lundi.isoformat(), "jour": "lundi"},
    )

    contenu = reponse.content.decode("utf-8")
    assert str(type_formation) in contenu
    duree = cours.element.volume_horaire_prescrit
    assert f"/{duree}" in contenu


def test_g3_quater_onglet_samedi_atteignable_dimanche_absent(
    client, scenario, cours, brigade_formation
):
    """Retour du 17/09 : le samedi et le dimanche restaient invisibles — les
    onglets ne portaient que les jours déjà pourvus de créneaux dans la
    grille active (cinq jours ouvrés dans le jeu de démonstration). Le
    samedi doit rester atteignable même sans créneau standard ce jour-là
    (`.claude/rules/tests.md` : une séance hors grille peut y exister),
    jamais le dimanche."""
    qualifier(cours.instructeur, cours.element.matiere)
    client.force_login(scenario.planificateur)
    client.post(
        reverse("planification:lancement_generation"),
        {"semaine": scenario.lundi.isoformat(), "brigades": [brigade_formation.pk]},
    )

    reponse = client.get(
        reverse("planification:consultation_programme"), {"semaine": scenario.lundi.isoformat()}
    )

    contenu = reponse.content.decode("utf-8")
    assert "Samedi" in contenu
    assert "Dimanche" not in contenu

    reponse_samedi = client.get(
        reverse("planification:consultation_programme"),
        {"semaine": scenario.lundi.isoformat(), "jour": "samedi"},
    )
    assert reponse_samedi.status_code == 200
    assert "Aucun créneau" in reponse_samedi.content.decode("utf-8")


def test_g5_lecture_accordee_aux_profils_reellement_habilites(
    client, scenario, direction_formation
):
    """Deux profils portent `programme_lecture` dans la matrice actuelle
    (Cellule planification, Direction de formation) — pas quatre, malgré la
    formulation du § 12 du Prompt 31 ; voir docs/suivi/DECISIONS.md."""
    for utilisateur in (scenario.planificateur, direction_formation):
        client.force_login(utilisateur)
        reponse = client.get(reverse("planification:consultation_programme"))
        assert reponse.status_code == 200


def test_g7_navigation_atteignable_pour_un_profil_planification(client, scenario):
    client.force_login(scenario.planificateur)

    reponse = client.get(reverse("noyau:accueil"))

    assert reponse.status_code == 200
    assert reverse("planification:consultation_programme") in reponse.content.decode("utf-8")
