"""US-VAL-03, groupe F — volume programmé et programmes rejetés (V7).

Un programme rejeté compte au volume programmé : aucun état n'exprime
l'abandon (arbitrage A7). Une génération sur une autre semaine qui dépasserait
le prescrit à cause de ce programme ne place pas la matière.
"""

import datetime

from planification.models import EtatProgramme, ProgrammeHebdomadaire, Seance
from planification.services.generation import ServiceGeneration
from planification.tests.aide_circuit import amener_a
from planification.tests.conftest import qualifier


def _circuit_de_volume_deux_heures(circuit):
    """Même circuit : l'élément existant ne compte que 2 h prescrites. Un second
    élément pour le même couple formation-matière violerait l'unicité en base."""
    element = circuit.cours.element
    element.volume_horaire_prescrit = 2
    element.save()
    qualifier(circuit.cours.instructeur, element.matiere)
    return circuit


def _matiere_programmee(cours, lundi):
    return Seance.objects.filter(
        element_referentiel=cours.element, programme__lundi_de_semaine=lundi
    ).exists()


def test_f_un_programme_rejete_compte_et_la_generation_suivante_ne_place_pas_la_matiere(
    scenario, circuit
):
    """Volume prescrit de 2 h, déjà programmé (2 h) dans la semaine rejetée."""
    court = _circuit_de_volume_deux_heures(circuit)
    amener_a(EtatProgramme.REJETE, court)
    semaine_suivante = scenario.lundi + datetime.timedelta(weeks=1)

    ServiceGeneration.generer(court.acteurs.planificateur, semaine_suivante, [court.brigade])

    assert not _matiere_programmee(court.cours, semaine_suivante)


def test_f_temoin_sans_programme_rejete_la_generation_place_la_matiere(scenario, circuit):
    """Témoin : sans le programme rejeté, la même génération place la matière.
    Sans ce témoin, le test précédent passerait même si la génération ne
    plaçait jamais rien."""
    court = _circuit_de_volume_deux_heures(circuit)
    semaine_suivante = scenario.lundi + datetime.timedelta(weeks=1)

    ServiceGeneration.generer(court.acteurs.planificateur, semaine_suivante, [court.brigade])

    assert ProgrammeHebdomadaire.objects.filter(lundi_de_semaine=semaine_suivante).exists()
    assert _matiere_programmee(court.cours, semaine_suivante)
