"""US-PLAN-03 — Groupe C : l'heuristique. Prompt 31, § 12. Données
entièrement fictives.
"""

import datetime

from planification.models import Seance
from planification.services.generation import ServiceGeneration
from planification.tests.conftest import activer_grille, creer_element, qualifier
from referentiel.models import Matiere
from ressources.models import Instructeur, Statut


def _instructeur(matricule):
    return Instructeur.objects.create(
        nom="Test",
        prenom=matricule,
        matricule=matricule,
        grade="Lt",
        specialite="Transmissions",
        statut=Statut.MILITAIRE_DU_CENTRE,
    )


def test_c1_determinisme_deux_generations_produisent_le_meme_programme(
    scenario, cours, brigade_formation
):
    qualifier(cours.instructeur, cours.element.matiere)
    ServiceGeneration.generer(scenario.planificateur, scenario.lundi, [brigade_formation])
    premiere = set(
        Seance.objects.values_list("element_referentiel", "instructeur", "lieu", "debut", "fin")
    )

    ServiceGeneration.generer(scenario.planificateur, scenario.lundi, [brigade_formation])
    seconde = set(
        Seance.objects.values_list("element_referentiel", "instructeur", "lieu", "debut", "fin")
    )

    assert premiere == seconde


def test_c2_matiere_moins_qualifiee_placee_avant_matiere_tres_qualifiee(
    planificateur, redacteur, formation, lundi_semaine, brigade_formation
):
    """Règle du plus contraint d'abord : une seule case ouverte, deux
    matières concurrentes — celle à deux instructeurs qualifiés (rare)
    l'emporte sur celle à dix (abondante)."""
    activer_grille(planificateur, "Une case C2", [(datetime.time(8, 0), datetime.time(9, 45))])
    matiere_rare = Matiere.objects.create(intitule="Matière rare C2", code="RAR2")
    matiere_abondante = Matiere.objects.create(intitule="Matière abondante C2", code="ABO10")
    element_rare = creer_element(formation, matiere_rare, volume=40)
    element_abondant = creer_element(formation, matiere_abondante, volume=40)
    for i in range(2):
        qualifier(_instructeur(f"RAR{i}"), matiere_rare)
    for i in range(10):
        qualifier(_instructeur(f"ABO{i}"), matiere_abondante)

    ServiceGeneration.generer(planificateur, lundi_semaine, [brigade_formation])

    assert Seance.objects.filter(element_referentiel=element_rare).exists()
    assert not Seance.objects.filter(element_referentiel=element_abondant).exists()
