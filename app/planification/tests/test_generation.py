"""US-PLAN-03 — génération du programme hebdomadaire. Groupe A : portée et
unicité du programme. Prompt 31, § 12. Données entièrement fictives.
"""

from planification.models import EtatProgramme, ProgrammeHebdomadaire, Seance
from planification.services.generation import ServiceGeneration
from planification.tests.conftest import qualifier


def test_a1_generation_sur_une_semaine_vierge_cree_un_programme_brouillon(
    scenario, cours, brigade_formation
):
    qualifier(cours.instructeur, cours.element.matiere)

    compte_rendu = ServiceGeneration.generer(scenario.planificateur, scenario.lundi, [brigade_formation])

    programme = ProgrammeHebdomadaire.objects.get(lundi_de_semaine=scenario.lundi)
    assert compte_rendu.programme == programme
    assert programme.etat == EtatProgramme.BROUILLON
    seances = Seance.objects.filter(programme=programme)
    assert seances.exists()
    assert all(
        ligne.brigade_id == brigade_formation.pk for s in seances for ligne in s.lignes.all()
    )


def test_a2_generation_sur_d_autres_brigades_complete_le_meme_programme(
    scenario, cours, autre_instructeur, brigade_formation, autre_brigade_formation
):
    """§ 2 : le piège structurel — le test qui attrape le défaut."""
    qualifier(cours.instructeur, cours.element.matiere)
    qualifier(autre_instructeur, cours.element.matiere)

    ServiceGeneration.generer(scenario.planificateur, scenario.lundi, [brigade_formation])
    premieres_seances = set(Seance.objects.values_list("pk", flat=True))

    ServiceGeneration.generer(scenario.planificateur, scenario.lundi, [autre_brigade_formation])

    assert ProgrammeHebdomadaire.objects.filter(lundi_de_semaine=scenario.lundi).count() == 1
    programme = ProgrammeHebdomadaire.objects.get(lundi_de_semaine=scenario.lundi)
    assert set(Seance.objects.filter(pk__in=premieres_seances).values_list("programme", flat=True)) == {
        programme.pk
    }
    assert Seance.objects.filter(pk__in=premieres_seances).exists()
    assert Seance.objects.exclude(pk__in=premieres_seances).filter(
        lignes__brigade=autre_brigade_formation
    ).exists()


def test_a3_aucune_violation_d_unicite_apres_plusieurs_generations(
    scenario, cours, autre_instructeur, brigade_formation, autre_brigade_formation
):
    qualifier(cours.instructeur, cours.element.matiere)
    qualifier(autre_instructeur, cours.element.matiere)

    ServiceGeneration.generer(scenario.planificateur, scenario.lundi, [brigade_formation])
    ServiceGeneration.generer(scenario.planificateur, scenario.lundi, [autre_brigade_formation])
    ServiceGeneration.generer(
        scenario.planificateur, scenario.lundi, [brigade_formation, autre_brigade_formation]
    )

    assert ProgrammeHebdomadaire.objects.filter(lundi_de_semaine=scenario.lundi).count() == 1


def test_a4_instructeur_affecte_a_une_brigade_non_selectionnee_vu_comme_occupe(
    scenario, cours, brigade_formation, autre_brigade_formation
):
    """Résolution centre-entier : SEUL `cours.instructeur` est qualifié —
    la génération sur `autre_brigade_formation` doit le voir occupé par les
    séances déjà posées pour `brigade_formation`, qui n'est plus
    sélectionnée cette fois."""
    qualifier(cours.instructeur, cours.element.matiere)
    ServiceGeneration.generer(scenario.planificateur, scenario.lundi, [brigade_formation])

    compte_rendu = ServiceGeneration.generer(
        scenario.planificateur, scenario.lundi, [autre_brigade_formation]
    )

    assert compte_rendu.seances_par_brigade.get(autre_brigade_formation, 0) == 0
    motifs = [m for case in compte_rendu.cases_non_pourvues for m in case.motifs]
    assert any("RG-34" in motif for motif in motifs)


def test_a5_brigades_de_deux_sessions_differentes_dans_la_meme_selection_acceptee(
    scenario, cours, autre_instructeur, brigade_formation, brigade_autre_session
):
    qualifier(cours.instructeur, cours.element.matiere)
    matiere_autre = brigade_autre_session.session.formation.elements_referentiel.first().matiere
    qualifier(autre_instructeur, matiere_autre)

    compte_rendu = ServiceGeneration.generer(
        scenario.planificateur, scenario.lundi, [brigade_formation, brigade_autre_session]
    )

    assert compte_rendu.seances_par_brigade.get(brigade_formation, 0) > 0
    assert compte_rendu.seances_par_brigade.get(brigade_autre_session, 0) > 0
