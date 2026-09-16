"""US-PLAN-03 — Groupe G : cycle HTTP réel. Prompt 31, § 12. G4 (refus
d'habilitation) et G6 (garde du sprint 1) sont couverts une fois pour toutes
par `tests/architecture/test_ecrans_ecriture.py` (entrée `planification:
lancement_generation`) — voir sa docstring. Données entièrement fictives.
"""

from django.urls import reverse

from planification.models import ProgrammeHebdomadaire, Seance
from planification.tests.conftest import qualifier


def test_g1_chemin_nominal_profil_planification(client, scenario, cours, brigade_formation):
    qualifier(cours.instructeur, cours.element.matiere)
    client.force_login(scenario.planificateur)

    assert client.get(reverse("planification:lancement_generation")).status_code == 200

    reponse = client.post(
        reverse("planification:lancement_generation"),
        {"semaine": scenario.lundi.isoformat(), "brigades": [brigade_formation.pk]},
    )

    assert reponse.status_code == 200
    assert "Compte rendu" in reponse.content.decode("utf-8")
    programme = ProgrammeHebdomadaire.objects.get(lundi_de_semaine=scenario.lundi)
    assert Seance.objects.filter(programme=programme).exists()


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
    )
    assert confirmation.status_code == 200
    assert "Compte rendu" in confirmation.content.decode("utf-8")


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
