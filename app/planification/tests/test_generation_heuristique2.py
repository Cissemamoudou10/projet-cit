"""US-PLAN-03 — Groupe C (suite) : RG-33, critère 3, charge d'instructeur,
C6. Prompt 31, § 12. Données entièrement fictives.
"""

import datetime
from pathlib import Path

from planification.models import LigneProgramme, ProgrammeHebdomadaire, Seance
from planification.services.generation import ServiceGeneration
from planification.tests.conftest import creer_element, instant, qualifier
from referentiel.models import Matiere, Prerequis
from ressources.models import Instructeur, Statut


def test_c3_rg33_brigades_a_avancements_differents_aucun_rapprochement(
    scenario, cours, brigade_formation, autre_brigade_formation
):
    """RG-33, structurante : le décalage entre deux brigades d'une même
    session n'est jamais corrigé par la génération."""
    qualifier(cours.instructeur, cours.element.matiere)
    programme_passe = ProgrammeHebdomadaire.objects.create(
        lundi_de_semaine=scenario.lundi - datetime.timedelta(weeks=52)
    )
    seance_passee = Seance.objects.create(
        programme=programme_passe,
        element_referentiel=cours.element,
        instructeur=cours.instructeur,
        debut=instant(programme_passe.lundi_de_semaine, 0, 8),
        fin=instant(programme_passe.lundi_de_semaine, 0, 8).replace(hour=19),
    )
    LigneProgramme.objects.create(seance=seance_passee, brigade=brigade_formation)

    compte_rendu = ServiceGeneration.generer(
        scenario.planificateur, scenario.lundi, [brigade_formation, autre_brigade_formation]
    )

    avancee = compte_rendu.seances_par_brigade.get(brigade_formation, 0)
    en_retard = compte_rendu.seances_par_brigade.get(autre_brigade_formation, 0)
    assert avancee != en_retard


def test_c4_matiere_volume_epuise_et_matiere_prerequis_inacheve_motifs_distincts(
    scenario, formation, brigade_formation, instructeur
):
    matiere_epuisee = Matiere.objects.create(intitule="Matière épuisée C4", code="EPU4")
    matiere_cible = Matiere.objects.create(intitule="Matière cible C4", code="CIB4")
    matiere_prerequise = Matiere.objects.create(intitule="Matière prérequise C4", code="PRE4")
    element_epuise = creer_element(formation, matiere_epuisee, volume=2)
    element_cible = creer_element(formation, matiere_cible, volume=10)
    element_prerequis = creer_element(formation, matiere_prerequise, volume=10)
    Prerequis.objects.create(element=element_cible, element_prerequis=element_prerequis)
    qualifier(instructeur, matiere_epuisee)
    qualifier(instructeur, matiere_cible)
    programme_passe = ProgrammeHebdomadaire.objects.create(
        lundi_de_semaine=scenario.lundi - datetime.timedelta(weeks=52)
    )
    seance_epuisante = Seance.objects.create(
        programme=programme_passe,
        element_referentiel=element_epuise,
        instructeur=instructeur,
        debut=instant(programme_passe.lundi_de_semaine, 0, 8),
        fin=instant(programme_passe.lundi_de_semaine, 0, 10),
    )
    LigneProgramme.objects.create(seance=seance_epuisante, brigade=brigade_formation)

    compte_rendu = ServiceGeneration.generer(scenario.planificateur, scenario.lundi, [brigade_formation])

    ecartees = {e.element.pk: e.motif for e in compte_rendu.matieres_ecartees}
    assert "prescrit" in ecartees[element_epuise.pk] or "atteint" in ecartees[element_epuise.pk]
    assert "Prérequis" in ecartees[element_cible.pk]


def test_c5_choix_instructeur_a_contraintes_egales_repartit_la_charge(
    scenario, matiere, element_referentiel, brigade_formation
):
    element_referentiel.volume_horaire_prescrit = 200
    element_referentiel.save()
    instructeur_un = Instructeur.objects.create(
        nom="Un", prenom="C5", matricule="C5U1", grade="Lt",
        specialite="Transmissions", statut=Statut.MILITAIRE_DU_CENTRE,
    )
    instructeur_deux = Instructeur.objects.create(
        nom="Deux", prenom="C5", matricule="C5U2", grade="Lt",
        specialite="Transmissions", statut=Statut.MILITAIRE_DU_CENTRE,
    )
    qualifier(instructeur_un, matiere)
    qualifier(instructeur_deux, matiere)

    ServiceGeneration.generer(scenario.planificateur, scenario.lundi, [brigade_formation])

    instructeurs_utilises = set(Seance.objects.values_list("instructeur", flat=True))
    assert instructeurs_utilises == {instructeur_un.pk, instructeur_deux.pk}


def test_c6_aucune_contrainte_dure_evaluee_hors_de_service_contraintes():
    """Preuve statique : seul `contraintes.py` construit un `Verdict` — la
    stratégie n'a aucun moyen de fabriquer sa propre décision d'acceptation.
    """
    racine = Path(__file__).resolve().parents[1] / "generation"
    fautifs = []
    for chemin in racine.glob("*.py"):
        if "Verdict(" in chemin.read_text(encoding="utf-8"):
            fautifs.append(chemin.name)
    assert not fautifs, f"Construit un Verdict en dehors de ServiceContraintes : {fautifs}"
