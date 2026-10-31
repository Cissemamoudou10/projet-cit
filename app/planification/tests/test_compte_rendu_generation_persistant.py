"""Correction de NC R00-GEN-03 (évolution du prompt 53, Temps 3) — compte
rendu de génération persistant et condensé (C1 à C4). Données fictives.
"""

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from planification.generation.condensation import LIBELLES_CODES_VIOLATION
from planification.models import CompteRenduGeneration, ProgrammeHebdomadaire
from planification.selectors_compte_rendu import derniere_generation
from planification.services.generation import ServiceGeneration
from planification.tests.aide_circuit import seance_dans
from planification.tests.conftest import instant, qualifier

CRENEAUX_SEMAINE = [(jour, heure) for jour in range(5) for heure in (8, 10)]


def _consultation(lundi):
    return reverse("planification:consultation_programme") + f"?semaine={lundi.isoformat()}"


def _occuper_instructeur_partout(programme, cours, autre_brigade):
    """Occupe l'unique instructeur qualifié sur les dix créneaux de la
    semaine, pour une AUTRE brigade : RG-34 se répète sur chaque case de
    la brigade générée, toujours la même matière."""
    for jour, heure in CRENEAUX_SEMAINE:
        seance_dans(programme, cours, autre_brigade, instant(programme.lundi_de_semaine, jour, heure))


def test_c2_consultable_apres_navigation_ailleurs(
    client, scenario, cours, brigade_formation
):
    qualifier(cours.instructeur, cours.element.matiere)
    client.force_login(scenario.planificateur)
    client.post(
        reverse("planification:lancement_generation"),
        {"semaine": scenario.lundi.isoformat(), "brigades": [brigade_formation.pk]},
    )

    client.get(reverse("planification:liste_programmes"))
    reponse = client.get(_consultation(scenario.lundi))

    assert "Dernière génération" in reponse.content.decode("utf-8")


def test_c2_remplace_par_une_nouvelle_generation(
    client, scenario, cours, brigade_formation, autre_brigade_formation
):
    qualifier(cours.instructeur, cours.element.matiere)
    client.force_login(scenario.planificateur)
    client.post(
        reverse("planification:lancement_generation"),
        {"semaine": scenario.lundi.isoformat(), "brigades": [brigade_formation.pk]},
    )
    programme = ProgrammeHebdomadaire.objects.get(lundi_de_semaine=scenario.lundi)
    premier = derniere_generation(programme)
    assert premier.resume["brigades_traitees"] == [str(brigade_formation)]

    client.post(
        reverse("planification:lancement_generation"),
        {
            "semaine": scenario.lundi.isoformat(),
            "brigades": [autre_brigade_formation.pk],
            "confirme": "on",
        },
    )

    assert CompteRenduGeneration.objects.filter(programme=programme).count() == 1
    second = derniere_generation(programme)
    assert second.resume["brigades_traitees"] == [str(autre_brigade_formation)]
    assert second.pk == premier.pk  # même ligne, écrasée — pas une de plus


def test_c3_regroupement_et_decompte_corrects_sur_plusieurs_motifs(
    scenario, cours, brigade_formation, autre_brigade_formation
):
    qualifier(cours.instructeur, cours.element.matiere)
    programme = ProgrammeHebdomadaire.objects.create(lundi_de_semaine=scenario.lundi)
    _occuper_instructeur_partout(programme, cours, autre_brigade_formation)

    ServiceGeneration.generer(scenario.planificateur, scenario.lundi, [brigade_formation])

    resume = derniere_generation(programme).resume
    groupe = next(
        g
        for g in resume["groupes_non_places"]
        if g["brigade"] == str(brigade_formation) and g["matiere"] == str(cours.element.matiere)
    )
    assert groupe["motif_libelle"] == LIBELLES_CODES_VIOLATION["RG-34"]
    assert groupe["nombre"] == len(CRENEAUX_SEMAINE)
    assert len(groupe["details"]) == len(CRENEAUX_SEMAINE)
    assert resume["nombre_cases_non_placees"] == len(CRENEAUX_SEMAINE)


def test_c3_nombre_de_requetes_de_la_page_constant_avec_le_contenu_du_resume(
    client, circuit
):
    """§ Temps 3 : la page du programme ne doit pas multiplier ses requêtes
    avec la taille du condensé (brigades traitées, groupes de motifs) — un
    seul `JSONField`, jamais une ligne par brigade ou par motif."""
    programme = circuit.programme
    seance_dans(
        programme, circuit.cours, circuit.brigade, instant(programme.lundi_de_semaine, 0, 8)
    )
    client.force_login(circuit.acteurs.planificateur)
    url = _consultation(programme.lundi_de_semaine)

    CompteRenduGeneration.objects.create(programme=programme, resume=_resume(nombre_groupes=1))
    client.get(url)  # chauffe (compilation des gabarits, etc.)
    with CaptureQueriesContext(connection) as petit:
        client.get(url)

    CompteRenduGeneration.objects.filter(programme=programme).update(
        resume=_resume(nombre_groupes=50)
    )
    with CaptureQueriesContext(connection) as grand:
        client.get(url)

    assert len(petit.captured_queries) == len(grand.captured_queries)


def _resume(nombre_groupes):
    return {
        "auteur": "u_plan",
        "brigades_traitees": [f"BRIGADE-{i}" for i in range(nombre_groupes)],
        "nombre_seances_placees": 1,
        "nombre_cases_non_placees": nombre_groupes,
        "interrompu_par_la_borne": False,
        "groupes_non_places": [
            {
                "motif_libelle": "RG-34",
                "brigade": f"BRIGADE-{i}",
                "matiere": "M1",
                "nombre": 1,
                "details": [f"détail {i}"],
            }
            for i in range(nombre_groupes)
        ],
        "matieres_ecartees": [],
    }
