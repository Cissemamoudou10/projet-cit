"""US-PLAN-03 — Groupe B : régénération chirurgicale. Prompt 31, § 12.
Données entièrement fictives.
"""

from unittest.mock import patch

import pytest

from planification.models import LigneProgramme, ProgrammeHebdomadaire, Seance
from planification.services.generation import ServiceGeneration
from planification.tests.conftest import instant, qualifier


def test_b1_regeneration_supprime_et_reconstruit_les_seances_non_verrouillees(
    scenario, cours, brigade_formation
):
    qualifier(cours.instructeur, cours.element.matiere)
    ServiceGeneration.generer(scenario.planificateur, scenario.lundi, [brigade_formation])
    premieres = set(Seance.objects.values_list("pk", flat=True))

    ServiceGeneration.generer(scenario.planificateur, scenario.lundi, [brigade_formation])
    secondes = set(Seance.objects.values_list("pk", flat=True))

    assert premieres.isdisjoint(secondes)
    assert secondes


def test_b2_seances_verrouillees_des_brigades_selectionnees_preservees(
    scenario, cours, brigade_formation
):
    qualifier(cours.instructeur, cours.element.matiere)
    ServiceGeneration.generer(scenario.planificateur, scenario.lundi, [brigade_formation])
    verrouillee = Seance.objects.filter(programme__lundi_de_semaine=scenario.lundi).first()
    verrouillee.verrouillee = True
    verrouillee.save()

    ServiceGeneration.generer(scenario.planificateur, scenario.lundi, [brigade_formation])

    assert Seance.objects.filter(pk=verrouillee.pk).exists()


def test_b3_seances_des_brigades_non_selectionnees_intactes(
    scenario, cours, autre_instructeur, brigade_formation, autre_brigade_formation
):
    qualifier(cours.instructeur, cours.element.matiere)
    qualifier(autre_instructeur, cours.element.matiere)
    ServiceGeneration.generer(scenario.planificateur, scenario.lundi, [brigade_formation])
    ServiceGeneration.generer(scenario.planificateur, scenario.lundi, [autre_brigade_formation])
    seances_autre = set(
        Seance.objects.filter(lignes__brigade=autre_brigade_formation).values_list("pk", flat=True)
    )

    ServiceGeneration.generer(scenario.planificateur, scenario.lundi, [brigade_formation])

    assert set(
        Seance.objects.filter(lignes__brigade=autre_brigade_formation).values_list("pk", flat=True)
    ) == seances_autre


def test_b4_transaction_echec_au_milieu_ne_supprime_ni_ne_cree_rien(
    scenario, cours, brigade_formation
):
    qualifier(cours.instructeur, cours.element.matiere)
    ServiceGeneration.generer(scenario.planificateur, scenario.lundi, [brigade_formation])
    avant_seances = set(Seance.objects.values_list("pk", flat=True))
    avant_lignes = set(LigneProgramme.objects.values_list("pk", flat=True))

    with patch(
        "planification.services.generation.ServiceJournal.enregistrer_detaillee",
        side_effect=RuntimeError("panne simulée"),
    ):
        with pytest.raises(RuntimeError):
            ServiceGeneration.generer(scenario.planificateur, scenario.lundi, [brigade_formation])

    assert set(Seance.objects.values_list("pk", flat=True)) == avant_seances
    assert set(LigneProgramme.objects.values_list("pk", flat=True)) == avant_lignes


def test_b5_seance_regroupee_a_cheval_preservee_et_signalee(
    scenario, cours, brigade_formation, autre_brigade_formation
):
    """Séance verrouillée EXCLUE du champ ici — à cheval sur une brigade
    sélectionnée (`brigade_formation`) et une non sélectionnée
    (`autre_brigade_formation`), NON verrouillée : préservée intégralement
    (§ 2, arbitrage retenu), signalée au compte rendu."""
    qualifier(cours.instructeur, cours.element.matiere)
    programme = ProgrammeHebdomadaire.objects.create(lundi_de_semaine=scenario.lundi)
    debut = instant(scenario.lundi, 0, 8)
    seance = Seance.objects.create(
        programme=programme,
        element_referentiel=cours.element,
        instructeur=cours.instructeur,
        debut=debut,
        fin=instant(scenario.lundi, 0, 9, 45),
    )
    LigneProgramme.objects.create(seance=seance, brigade=brigade_formation)
    LigneProgramme.objects.create(seance=seance, brigade=autre_brigade_formation)

    compte_rendu = ServiceGeneration.generer(scenario.planificateur, scenario.lundi, [brigade_formation])

    assert Seance.objects.filter(pk=seance.pk).exists()
    assert seance in compte_rendu.seances_regroupees_a_cheval_preservees
