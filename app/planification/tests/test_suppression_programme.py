"""Évolution du prompt 53, Temps 2 — suppression d'un programme en brouillon
jamais soumis (S1 à S7). Données fictives."""

import pytest

from administration.models import EntreeJournal, TypeAction
from noyau.exceptions import ErreurHabilitation
from planification.exceptions import SuppressionProgrammeRefusee
from planification.models import EtatProgramme, LigneProgramme, ProgrammeHebdomadaire, Seance
from planification.selectors_circuit import peut_supprimer_brouillon
from planification.services.circuit import ServiceCircuitProgramme
from planification.services.generation import ServiceGeneration
from planification.tests.aide_circuit import amener_a, seance_dans
from planification.tests.conftest import instant

ETATS_BLOQUANTS = (
    EtatProgramme.SOUMIS,
    EtatProgramme.VALIDE,
    EtatProgramme.REJETE,
    EtatProgramme.AFFICHE,
)


def _journal_suppression(pk):
    return EntreeJournal.objects.filter(
        objet_type="programme", objet_cle=str(pk), type_action=TypeAction.SUPPRESSION_PROGRAMME
    )


def _une_seance(circuit):
    return seance_dans(
        circuit.programme, circuit.cours, circuit.brigade, instant(circuit.programme.lundi_de_semaine, 0, 8)
    )


def test_s4_suppression_sans_confirmation_est_refusee(circuit):
    programme, acteurs = circuit.programme, circuit.acteurs
    _une_seance(circuit)

    with pytest.raises(SuppressionProgrammeRefusee, match="(?i)confirmation"):
        ServiceGeneration.supprimer_brouillon(acteurs.planificateur, programme, False)

    assert ProgrammeHebdomadaire.objects.filter(pk=programme.pk).exists()


def test_s5_s6_suppression_efface_programme_seances_lignes_et_journalise(circuit):
    programme, acteurs = circuit.programme, circuit.acteurs
    seance = _une_seance(circuit)
    pk = programme.pk

    ServiceGeneration.supprimer_brouillon(acteurs.planificateur, programme, True)

    assert not ProgrammeHebdomadaire.objects.filter(pk=pk).exists()
    assert not Seance.objects.filter(pk=seance.pk).exists()
    assert not LigneProgramme.objects.filter(seance_id=seance.pk).exists()
    entree = _journal_suppression(pk).get()
    assert entree.auteur == acteurs.planificateur
    assert str(circuit.brigade) in entree.detail
    assert "1 séance(s) supprimée(s)" in entree.detail


@pytest.mark.parametrize("etat", ETATS_BLOQUANTS, ids=[e.value for e in ETATS_BLOQUANTS])
def test_s2_refus_hors_brouillon(etat, circuit):
    programme, acteurs = circuit.programme, circuit.acteurs
    amener_a(etat, circuit)

    with pytest.raises(SuppressionProgrammeRefusee, match="(?i)brouillon"):
        ServiceGeneration.supprimer_brouillon(acteurs.planificateur, programme, True)

    assert ProgrammeHebdomadaire.objects.filter(pk=programme.pk).exists()


def test_s2_refus_brouillon_avec_histoire_apres_retrait_de_soumission(circuit):
    programme, acteurs = circuit.programme, circuit.acteurs
    amener_a(EtatProgramme.SOUMIS, circuit)
    ServiceCircuitProgramme.retirer_soumission(acteurs.planificateur, programme)
    programme.refresh_from_db()
    assert programme.etat == EtatProgramme.BROUILLON
    assert not peut_supprimer_brouillon(programme)

    with pytest.raises(SuppressionProgrammeRefusee, match="histoire de circuit"):
        ServiceGeneration.supprimer_brouillon(acteurs.planificateur, programme, True)

    assert ProgrammeHebdomadaire.objects.filter(pk=programme.pk).exists()


def test_s2_refus_brouillon_repris_apres_rejet(circuit):
    programme, acteurs = circuit.programme, circuit.acteurs
    amener_a(EtatProgramme.REJETE, circuit)
    ServiceCircuitProgramme.reprendre(acteurs.planificateur, programme)
    programme.refresh_from_db()
    assert programme.etat == EtatProgramme.BROUILLON

    with pytest.raises(SuppressionProgrammeRefusee, match="histoire de circuit"):
        ServiceGeneration.supprimer_brouillon(acteurs.planificateur, programme, True)


def test_s1_refus_pour_la_cellule_pedagogique(circuit):
    programme, acteurs = circuit.programme, circuit.acteurs
    _une_seance(circuit)

    with pytest.raises(ErreurHabilitation):
        ServiceGeneration.supprimer_brouillon(acteurs.pedagogique, programme, True)

    assert ProgrammeHebdomadaire.objects.filter(pk=programme.pk).exists()


def test_s7_regeneration_apres_suppression_cree_un_nouveau_brouillon_supprimable(scenario, circuit):
    """Garantit que le nouveau programme (nouvelle clé primaire) n'hérite
    d'aucune histoire de l'ancien, jamais soumis lui non plus — ce que
    `a_une_histoire_de_circuit` doit prouver par l'identité technique du
    programme (objet_cle), pas par la semaine."""
    programme, acteurs = circuit.programme, circuit.acteurs
    ancien_pk = programme.pk
    _une_seance(circuit)
    ServiceGeneration.supprimer_brouillon(acteurs.planificateur, programme, True)

    ServiceGeneration.generer(acteurs.planificateur, scenario.lundi, [circuit.brigade])

    nouveau = ProgrammeHebdomadaire.objects.get(lundi_de_semaine=scenario.lundi)
    assert nouveau.pk != ancien_pk
    assert peut_supprimer_brouillon(nouveau)
    ServiceGeneration.supprimer_brouillon(acteurs.planificateur, nouveau, True)
    assert not ProgrammeHebdomadaire.objects.filter(pk=nouveau.pk).exists()
