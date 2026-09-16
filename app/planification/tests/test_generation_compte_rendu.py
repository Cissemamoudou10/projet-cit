"""US-PLAN-03 — Groupe F : le compte rendu. Prompt 31, § 7/§ 12. Données
entièrement fictives.
"""

from administration.models import EntreeJournal, TypeAction
from planification.models import Seance
from planification.services.generation import ServiceGeneration
from planification.tests.conftest import qualifier


def test_f1_nombre_de_seances_placees_par_brigade_exact(
    scenario, cours, autre_instructeur, brigade_formation, autre_brigade_formation
):
    qualifier(cours.instructeur, cours.element.matiere)
    qualifier(autre_instructeur, cours.element.matiere)

    compte_rendu = ServiceGeneration.generer(
        scenario.planificateur, scenario.lundi, [brigade_formation, autre_brigade_formation]
    )

    assert compte_rendu.seances_par_brigade[brigade_formation] == 10
    assert compte_rendu.seances_par_brigade[autre_brigade_formation] == 10


def test_f2_volume_programme_et_restant_par_matiere_et_par_brigade_exacts(
    scenario, cours, brigade_formation
):
    qualifier(cours.instructeur, cours.element.matiere)

    compte_rendu = ServiceGeneration.generer(scenario.planificateur, scenario.lundi, [brigade_formation])

    total_reel = sum(
        (s.fin - s.debut).total_seconds() / 3600
        for s in Seance.objects.filter(element_referentiel=cours.element)
    )
    ligne = next(
        v for v in compte_rendu.volumes if v.brigade == brigade_formation and v.element == cours.element
    )
    assert ligne.heures_cette_semaine == total_reel
    assert ligne.volume_restant_element == cours.element.volume_horaire_prescrit - total_reel


def test_f3_motifs_distincts_conflit_existant_versus_conflit_du_meme_lot(
    scenario, cours, brigade_formation, autre_brigade_formation
):
    """Deux brigades sélectionnées à la même génération, un seul instructeur
    qualifié : la seconde à réclamer le même créneau porte un motif « lot »,
    distinct d'un conflit avec une séance déjà en base (« base »)."""
    qualifier(cours.instructeur, cours.element.matiere)

    compte_rendu = ServiceGeneration.generer(
        scenario.planificateur, scenario.lundi, [brigade_formation, autre_brigade_formation]
    )

    motifs = [m for case in compte_rendu.cases_non_pourvues for m in case.motifs]
    assert any("(lot)" in m and "RG-34" in m for m in motifs)


def test_f4_le_compte_rendu_n_est_pas_enregistre_en_base(scenario, cours, brigade_formation):
    from planification.models import ProgrammeHebdomadaire

    qualifier(cours.instructeur, cours.element.matiere)

    ServiceGeneration.generer(scenario.planificateur, scenario.lundi, [brigade_formation])

    colonnes = {f.name for f in ProgrammeHebdomadaire._meta.get_fields()}
    assert "compte_rendu" not in colonnes
    assert "cases_non_pourvues" not in colonnes


def test_f5_journalisation_porte_l_acte_pas_le_detail(scenario, cours, brigade_formation):
    qualifier(cours.instructeur, cours.element.matiere)

    ServiceGeneration.generer(scenario.planificateur, scenario.lundi, [brigade_formation])

    entree = EntreeJournal.objects.get(type_action=TypeAction.GENERATION_PROGRAMME)
    assert entree.auteur == scenario.planificateur
    assert str(brigade_formation) in entree.detail
    assert "créée(s)" in entree.detail
    assert "08:" not in entree.detail
