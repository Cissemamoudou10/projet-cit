"""US-VAL-03, groupes C et E — garde de modification (V3) et relecture sous
verrou (V4). Les chemins d'écriture réels : porte unique, génération,
insertion d'un contrôle. Données fictives.
"""

import pytest

from administration.models import EntreeJournal, TypeAction
from planification.exceptions import TransitionProgrammeRefusee
from planification.models import EtatProgramme, ProgrammeHebdomadaire, Seance
from planification.services.circuit import ServiceCircuitProgramme
from planification.services.ecriture import ServiceEcritureSeance
from planification.services.generation import ServiceGeneration
from planification.tests.aide_circuit import amener_a, candidature
from planification.tests.conftest import instant, qualifier

BLOQUANTS = [
    (EtatProgramme.SOUMIS, "retirez la soumission (t3)"),
    (EtatProgramme.VALIDE, "annulez la validation (t9)"),
    (EtatProgramme.AFFICHE, "portez un avenant (t10)"),
]


def _pks_seances(programme):
    return set(Seance.objects.filter(programme=programme).values_list("pk", flat=True))


def _journal(programme):
    return list(
        EntreeJournal.objects.filter(
            objet_type="programme", objet_identifiant=str(programme.pk)
        ).order_by("pk")
    )


# --- C1 — creer_seance refusée hors brouillon, avec la marche à suivre -------


@pytest.mark.parametrize("cas", BLOQUANTS, ids=[etat.value for etat, _ in BLOQUANTS])
def test_c1_creer_seance_refusee_avec_la_marche_a_suivre(cas, circuit):
    etat, marche = cas
    programme, acteurs = circuit.programme, circuit.acteurs
    amener_a(etat, circuit)
    avant = _pks_seances(programme)
    candidate = candidature(
        circuit.brigade, circuit.cours, instant(programme.lundi_de_semaine, 2, 9)
    )

    with pytest.raises(TransitionProgrammeRefusee) as erreur:
        ServiceEcritureSeance.creer_seance(acteurs.planificateur, programme, [candidate])

    assert marche in str(erreur.value).lower()
    assert _pks_seances(programme) == avant


# --- C2 à C5 — génération et régénération ------------------------------------


def test_c2_generation_sur_semaine_soumise_refusee_sans_rien_creer_ni_supprimer(scenario, circuit):
    programme, cours, acteurs = circuit.programme, circuit.cours, circuit.acteurs
    qualifier(cours.instructeur, cours.element.matiere)
    amener_a(EtatProgramme.SOUMIS, circuit)
    avant = _pks_seances(programme)

    with pytest.raises(TransitionProgrammeRefusee, match="(?i)retirez la soumission"):
        ServiceGeneration.generer(acteurs.planificateur, scenario.lundi, [circuit.brigade])

    assert _pks_seances(programme) == avant


def test_c3_generation_sur_semaine_rejetee_reprend_puis_genere(scenario, circuit):
    programme, cours, acteurs = circuit.programme, circuit.cours, circuit.acteurs
    qualifier(cours.instructeur, cours.element.matiere)
    amener_a(EtatProgramme.REJETE, circuit)

    ServiceGeneration.generer(acteurs.planificateur, scenario.lundi, [circuit.brigade])

    programme.refresh_from_db()
    assert programme.etat == EtatProgramme.BROUILLON
    assert Seance.objects.filter(programme=programme).exists()
    journal = _journal(programme)
    indice_reprise = next(
        i
        for i, entree in enumerate(journal)
        if "implicite" in entree.detail and "T6" in entree.detail
    )
    indice_generation = next(
        i
        for i, entree in enumerate(journal)
        if entree.type_action == TypeAction.GENERATION_PROGRAMME
    )
    assert indice_reprise < indice_generation


def test_c4_insertion_de_controle_refusee_sur_un_programme_soumis(scenario, circuit):
    programme, cours, acteurs = circuit.programme, circuit.cours, circuit.acteurs
    qualifier(cours.instructeur, cours.element.matiere)
    amener_a(EtatProgramme.SOUMIS, circuit)
    candidate = candidature(circuit.brigade, cours, instant(programme.lundi_de_semaine, 3, 9))

    with pytest.raises(TransitionProgrammeRefusee, match="(?i)retirez la soumission"):
        ServiceEcritureSeance.inserer_seance_de_controle(acteurs.examens, programme, [candidate])

    programme.refresh_from_db()
    assert programme.etat == EtatProgramme.SOUMIS


def test_c4_insertion_de_controle_sur_un_programme_rejete_reprend_puis_insere(scenario, circuit):
    programme, cours, acteurs = circuit.programme, circuit.cours, circuit.acteurs
    qualifier(cours.instructeur, cours.element.matiere)
    amener_a(EtatProgramme.REJETE, circuit)
    candidate = candidature(circuit.brigade, cours, instant(programme.lundi_de_semaine, 3, 9))

    seance = ServiceEcritureSeance.inserer_seance_de_controle(
        acteurs.examens, programme, [candidate]
    )

    programme.refresh_from_db()
    assert programme.etat == EtatProgramme.BROUILLON
    assert seance.verrouillee is True
    assert any(
        "insertion d'un contrôle" in entree.detail for entree in _journal(programme)
    ), "la reprise implicite doit nommer son déclencheur"


def test_c5_regeneration_d_un_programme_valide_ne_supprime_aucune_seance(scenario, circuit):
    programme, cours, acteurs = circuit.programme, circuit.cours, circuit.acteurs
    qualifier(cours.instructeur, cours.element.matiere)
    amener_a(EtatProgramme.VALIDE, circuit)
    avant = _pks_seances(programme)

    with pytest.raises(TransitionProgrammeRefusee):
        ServiceGeneration.generer(acteurs.planificateur, scenario.lundi, [circuit.brigade])

    assert _pks_seances(programme) == avant


# --- E — relecture sous verrou (V4) ------------------------------------------


def test_e_deux_validations_successives_une_seule_reussit(circuit):
    """Une seconde cellule tient une copie lue avant la première validation :
    la transition relit l'état sous verrou et refuse, sans écrire deux fois."""
    programme, acteurs = circuit.programme, circuit.acteurs
    amener_a(EtatProgramme.SOUMIS, circuit)
    copie_perimee = ProgrammeHebdomadaire.objects.get(pk=programme.pk)
    ServiceCircuitProgramme.valider(acteurs.pedagogique, programme)

    with pytest.raises(
        TransitionProgrammeRefusee, match="n'est pas possible sur un programme validé"
    ):
        ServiceCircuitProgramme.valider(acteurs.pedagogique, copie_perimee)

    entrees = EntreeJournal.objects.filter(type_action=TypeAction.VALIDATION_PROGRAMME)
    assert entrees.count() == 1


def test_e_creer_seance_avec_une_copie_perimee_est_refusee_apres_validation(circuit):
    programme, acteurs = circuit.programme, circuit.acteurs
    amener_a(EtatProgramme.SOUMIS, circuit)
    copie_perimee = ProgrammeHebdomadaire.objects.get(pk=programme.pk)
    ServiceCircuitProgramme.valider(acteurs.pedagogique, programme)
    candidate = candidature(
        circuit.brigade, circuit.cours, instant(programme.lundi_de_semaine, 2, 9)
    )

    with pytest.raises(TransitionProgrammeRefusee, match="(?i)annulez la validation"):
        ServiceEcritureSeance.creer_seance(acteurs.planificateur, copie_perimee, [candidate])
