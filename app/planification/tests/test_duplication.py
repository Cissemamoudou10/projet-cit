"""US-PLAN-11 — Dupliquer un programme hebdomadaire (prompt 48, Story 4).
Scénarios n'ayant besoin que de `planification`/`ressources`/`organisation` —
les scénarios de contrôle et de jour d'examen vivent dans
`app/evaluations/tests/test_plan11_duplication.py` (évaluations, couche la
plus haute). Données entièrement fictives.
"""

import datetime

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from organisation.services.brigade import ServiceBrigade
from organisation.tests.conftest import donnees_brigade
from planification.exceptions import TransitionProgrammeRefusee
from planification.models import EtatProgramme, LigneProgramme, ProgrammeHebdomadaire, Seance
from planification.services.circuit import ServiceCircuitProgramme
from planification.services.duplication import ServiceDuplication
from planification.tests.aide_circuit import seance_dans
from planification.tests.conftest import instant, qualifier
from ressources.models import IndisponibiliteInstructeur, NatureEvenement, PeriodeCalendrier

MOTIF_REJET = "À revoir."


def _lundi_cible(decalage_semaines=6):
    lundi = datetime.date.today() + datetime.timedelta(weeks=decalage_semaines)
    return lundi - datetime.timedelta(days=lundi.weekday())


def _periode_bloquante(lundi, heures=(7, 10), brigades=()):
    nature = NatureEvenement.objects.create(
        libelle=f"Blocage duplication {heures}", effet_par_defaut="bloquant"
    )
    periode = PeriodeCalendrier.objects.create(
        nature=nature,
        intitule="Blocage sur la cible",
        debut=instant(lundi, 0, heures[0]),
        fin=instant(lundi, 0, heures[1]),
        effet="bloquant",
    )
    if brigades:
        periode.brigades.set(brigades)
    return periode


def test_duplication_nominale(circuit):
    qualifier(circuit.cours.instructeur, circuit.cours.element.matiere)
    lundi_source = circuit.programme.lundi_de_semaine
    seance_dans(circuit.programme, circuit.cours, circuit.brigade, instant(lundi_source, 0, 8))
    lundi_cible = _lundi_cible()

    compte_rendu = ServiceDuplication.dupliquer(
        circuit.acteurs.planificateur, circuit.programme, lundi_cible, [circuit.brigade]
    )

    assert compte_rendu.nombre_creees == 1
    assert compte_rendu.exclues == []
    assert compte_rendu.refusees == []
    seance_cible = Seance.objects.get(programme=compte_rendu.programme_cible)
    assert seance_cible.instructeur == circuit.cours.instructeur
    assert seance_cible.verrouillee is False  # D5
    debut_local = instant(lundi_cible, 0, 8)
    assert seance_cible.debut == debut_local


@pytest.mark.parametrize("transition", ["soumettre", "valider", "afficher"])
def test_cible_non_brouillon_refusee(circuit, transition):
    lundi_source = circuit.programme.lundi_de_semaine
    seance_dans(circuit.programme, circuit.cours, circuit.brigade, instant(lundi_source, 0, 8))
    lundi_cible = _lundi_cible()
    cible = ProgrammeHebdomadaire.objects.create(lundi_de_semaine=lundi_cible)
    seance_dans(cible, circuit.cours, circuit.brigade, instant(lundi_cible, 0, 8))
    ServiceCircuitProgramme.soumettre(circuit.acteurs.planificateur, cible)
    if transition in ("valider", "afficher"):
        ServiceCircuitProgramme.valider(circuit.acteurs.pedagogique, cible)
    if transition == "afficher":
        ServiceCircuitProgramme.enregistrer_signature(
            circuit.acteurs.planificateur, cible, datetime.date.today(), "Signataire essai"
        )
        ServiceCircuitProgramme.afficher(circuit.acteurs.planificateur, cible)

    with pytest.raises(TransitionProgrammeRefusee):
        ServiceDuplication.dupliquer(
            circuit.acteurs.planificateur, circuit.programme, lundi_cible, [circuit.brigade]
        )


def test_cible_rejetee_ramenee_au_brouillon(circuit):
    qualifier(circuit.cours.instructeur, circuit.cours.element.matiere)
    lundi_source = circuit.programme.lundi_de_semaine
    seance_dans(circuit.programme, circuit.cours, circuit.brigade, instant(lundi_source, 0, 8))
    lundi_cible = _lundi_cible()
    cible = ProgrammeHebdomadaire.objects.create(lundi_de_semaine=lundi_cible)
    # Un créneau DIFFÉRENT de celui visé par la duplication (jour 0) — sinon
    # cette séance de confort (A9, programme non vide pour soumettre) entre
    # en conflit RG-34 avec la candidate dupliquée, faussant le test.
    seance_dans(cible, circuit.cours, circuit.brigade, instant(lundi_cible, 4, 8))
    ServiceCircuitProgramme.soumettre(circuit.acteurs.planificateur, cible)
    ServiceCircuitProgramme.rejeter(circuit.acteurs.pedagogique, cible, MOTIF_REJET)

    compte_rendu = ServiceDuplication.dupliquer(
        circuit.acteurs.planificateur, circuit.programme, lundi_cible, [circuit.brigade]
    )

    compte_rendu.programme_cible.refresh_from_db()
    assert compte_rendu.programme_cible.etat == EtatProgramme.BROUILLON
    assert compte_rendu.nombre_creees == 1


def test_refus_instructeur_indisponible_sur_la_cible(circuit):
    qualifier(circuit.cours.instructeur, circuit.cours.element.matiere)
    lundi_source = circuit.programme.lundi_de_semaine
    seance_dans(circuit.programme, circuit.cours, circuit.brigade, instant(lundi_source, 0, 8))
    lundi_cible = _lundi_cible()
    IndisponibiliteInstructeur.objects.create(
        instructeur=circuit.cours.instructeur,
        debut=instant(lundi_cible, 0, 7),
        fin=instant(lundi_cible, 0, 10),
        motif="Mission extérieure",
    )

    compte_rendu = ServiceDuplication.dupliquer(
        circuit.acteurs.planificateur, circuit.programme, lundi_cible, [circuit.brigade]
    )

    assert compte_rendu.nombre_creees == 0
    assert len(compte_rendu.refusees) == 1
    assert any(v["code"] == "RG-36" for v in compte_rendu.refusees[0].violations)


def test_refus_periode_bloquee_sur_la_cible(circuit):
    qualifier(circuit.cours.instructeur, circuit.cours.element.matiere)
    lundi_source = circuit.programme.lundi_de_semaine
    seance_dans(circuit.programme, circuit.cours, circuit.brigade, instant(lundi_source, 0, 8))
    lundi_cible = _lundi_cible()
    _periode_bloquante(lundi_cible, brigades=[circuit.brigade])

    compte_rendu = ServiceDuplication.dupliquer(
        circuit.acteurs.planificateur, circuit.programme, lundi_cible, [circuit.brigade]
    )

    assert compte_rendu.nombre_creees == 0
    assert len(compte_rendu.refusees) == 1
    assert any(v["code"] == "RG-38" for v in compte_rendu.refusees[0].violations)


def test_regroupement_partiellement_reporte(circuit, autre_brigade_formation):
    qualifier(circuit.cours.instructeur, circuit.cours.element.matiere)
    lundi_source = circuit.programme.lundi_de_semaine
    seance_regroupee = seance_dans(
        circuit.programme, circuit.cours, circuit.brigade, instant(lundi_source, 0, 8)
    )
    LigneProgramme.objects.create(seance=seance_regroupee, brigade=autre_brigade_formation)
    lundi_cible = _lundi_cible()
    _periode_bloquante(lundi_cible, brigades=[autre_brigade_formation])

    compte_rendu = ServiceDuplication.dupliquer(
        circuit.acteurs.planificateur,
        circuit.programme,
        lundi_cible,
        [circuit.brigade, autre_brigade_formation],
    )

    assert compte_rendu.nombre_creees == 1
    seance_cible = Seance.objects.get(programme=compte_rendu.programme_cible)
    assert list(seance_cible.lignes.values_list("brigade_id", flat=True)) == [circuit.brigade.pk]
    assert len(compte_rendu.refusees) == 1
    assert compte_rendu.refusees[0].brigade == autre_brigade_formation
    assert any(v["code"] == "RG-38" for v in compte_rendu.refusees[0].violations)


def test_depassement_de_volume_signale(circuit):
    """RG-39 compte le volume programmé PAR ÉLÉMENT (toutes brigades, tous
    programmes hors la cible elle-même) — les deux séances source comptent
    déjà 4 h avant toute duplication ; un prescrit à 6 h laisse passer la
    première candidate dupliquée (4 + 2 = 6) mais refuse la seconde
    (4 + 2 + 2 = 8 > 6), une fois la première retenue dans le lot."""
    qualifier(circuit.cours.instructeur, circuit.cours.element.matiere)
    element = circuit.cours.element
    element.volume_horaire_prescrit = 6
    element.save()
    lundi_source = circuit.programme.lundi_de_semaine
    seance_dans(circuit.programme, circuit.cours, circuit.brigade, instant(lundi_source, 0, 8))
    seance_dans(circuit.programme, circuit.cours, circuit.brigade, instant(lundi_source, 1, 8))
    lundi_cible = _lundi_cible()

    compte_rendu = ServiceDuplication.dupliquer(
        circuit.acteurs.planificateur, circuit.programme, lundi_cible, [circuit.brigade]
    )

    assert compte_rendu.nombre_creees == 1
    assert len(compte_rendu.refusees) == 1
    assert any(v["code"] == "RG-39" for v in compte_rendu.refusees[0].violations)


def test_requetes_constantes_avec_deux_et_dix_brigades(circuit, redacteur):
    """D7 : une seule séance regroupée, dix brigades — duplication filtrée
    sur 2 puis sur les 10 brigades. Des séances isolées et distinctes sur
    le même créneau se seraient mutuellement refusées (RG-34), faussant la
    mesure ; une séance regroupée n'a pas ce défaut (exception à RG-34)."""
    qualifier(circuit.cours.instructeur, circuit.cours.element.matiere)
    lundi_source = circuit.programme.lundi_de_semaine
    brigades = [circuit.brigade]
    for i in range(9):
        brigades.append(
            ServiceBrigade.creer(
                redacteur, circuit.brigade.session, donnees_brigade(designation=f"DUPQ{i}")
            )
        )
    seance_regroupee = seance_dans(
        circuit.programme, circuit.cours, circuit.brigade, instant(lundi_source, 0, 8)
    )
    for brigade in brigades[1:]:
        LigneProgramme.objects.create(seance=seance_regroupee, brigade=brigade)

    # Chauffe : la première résolution d'une relation peut peupler un cache
    # indépendant du nombre de brigades (même précaution que P-39) — sur
    # une semaine cible jetée, jamais mesurée.
    ServiceDuplication.dupliquer(
        circuit.acteurs.planificateur, circuit.programme, _lundi_cible(5), brigades[:1]
    )

    with CaptureQueriesContext(connection) as deux:
        ServiceDuplication.dupliquer(
            circuit.acteurs.planificateur, circuit.programme, _lundi_cible(6), brigades[:2]
        )

    with CaptureQueriesContext(connection) as dix:
        ServiceDuplication.dupliquer(
            circuit.acteurs.planificateur, circuit.programme, _lundi_cible(7), brigades
        )

    assert len(deux.captured_queries) == len(dix.captured_queries)
