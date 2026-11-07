"""A4 (RECETTE-01, prompt 61, L3) — catégorie réelle d'un lieu partagé.

Scindé de `test_contraintes_lieu.py` qui dépassait 400 lignes
(.claude/rules/python.md) après cette correction. Données entièrement
fictives.
"""

import datetime

import pytest

from planification.services.contraintes import Candidate, ServiceContraintes
from planification.tests.conftest import Cours, creer_element, instant, qualifier
from referentiel.models import CategorieLieu
from ressources.models import Lieu, ModePartage
from ressources.services.salle_attitree import ServiceSalleAttitree

DUREE_DEFAUT_MIN = 105


def _candidate(brigade, cours, debut, lieu=None, duree_min=DUREE_DEFAUT_MIN, **kw):
    fin = debut + datetime.timedelta(minutes=duree_min)
    return Candidate(
        brigade=brigade,
        element_referentiel=cours.element,
        instructeur=cours.instructeur,
        debut=debut,
        fin=fin,
        lieu=lieu,
        **kw,
    )


@pytest.fixture
def element_lieu_partage(formation, matiere):
    return creer_element(
        formation, matiere, categorie=CategorieLieu.LIEU_PARTAGE, type_lieu_partage="amphitheatre"
    )


@pytest.fixture
def cours_lieu_partage(element_lieu_partage, instructeur):
    return Cours(element_lieu_partage, instructeur)


@pytest.fixture
def element_lieu_partage_laboratoire(formation, matiere):
    """M2 (RECETTE-01/02, prompt 61 bis) : une matière en lieu partagé de
    type laboratoire, jamais amphithéâtre — distincte de
    `element_lieu_partage` (amphithéâtre) pour exercer le refus de TYPE,
    pas seulement de catégorie."""
    return creer_element(
        formation, matiere, categorie=CategorieLieu.LIEU_PARTAGE, type_lieu_partage="laboratoire"
    )


@pytest.fixture
def cours_lieu_partage_laboratoire(element_lieu_partage_laboratoire, instructeur):
    return Cours(element_lieu_partage_laboratoire, instructeur)


@pytest.fixture
def amphitheatre(db):
    return Lieu.objects.create(
        intitule="Amphithéâtre PLAN",
        capacite=60,
        categorie="lieu_partage",
        type_partage="amphitheatre",
        mode_partage=ModePartage.SIMULTANE,
    )


@pytest.fixture
def laboratoire(db):
    return Lieu.objects.create(
        intitule="Laboratoire PLAN",
        capacite=20,
        categorie="lieu_partage",
        type_partage="laboratoire",
        mode_partage=ModePartage.SEQUENTIEL,
    )


def test_a4_matiere_lieu_partage_en_salle_attitree_refusee(
    programme, planificateur, cours_lieu_partage, brigade
):
    """K2 (prompt 58) ne comparait `candidate.lieu` à la salle ATTENDUE que
    dans la branche `_verifier_salle_attitree` — jamais dans
    `_verifier_lieu_partage`, qui ne vérifiait que l'occupation et la
    capacité du lieu donné, jamais sa catégorie réelle. Une matière « lieu
    partagé » (M7) placée dans une salle attitrée (L1, même celle de sa
    propre brigade) passait donc sans être refusée."""
    salle = Lieu.objects.create(intitule="L1", capacite=20, categorie="salle_attitree")
    ServiceSalleAttitree.attribuer(planificateur, brigade, salle)
    qualifier(cours_lieu_partage.instructeur, cours_lieu_partage.element.matiere)
    candidate = _candidate(
        brigade, cours_lieu_partage, instant(programme.lundi_de_semaine, 0, 8), lieu=salle
    )

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    assert not verdict.accepte
    violation = next(v for v in verdict.violations if v["code"] == "RG-37")
    assert str(salle) in violation["message"]


def test_a4_matiere_lieu_partage_en_salle_attitree_d_une_autre_brigade_refusee(
    programme, planificateur, cours_lieu_partage, brigade, autre_brigade
):
    """Même défaut, pour la salle attitrée d'une AUTRE brigade (EXP2 visant
    L1, salle d'EXP1) — la catégorie réelle du lieu, jamais l'identité de
    sa brigade, est ce qui doit refuser."""
    salle = Lieu.objects.create(intitule="L1", capacite=20, categorie="salle_attitree")
    ServiceSalleAttitree.attribuer(planificateur, brigade, salle)
    qualifier(cours_lieu_partage.instructeur, cours_lieu_partage.element.matiere)
    candidate = _candidate(
        autre_brigade, cours_lieu_partage, instant(programme.lundi_de_semaine, 0, 8), lieu=salle
    )

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    assert not verdict.accepte
    violation = next(v for v in verdict.violations if v["code"] == "RG-37")
    assert str(salle) in violation["message"]


def test_a4_matiere_lieu_partage_en_lieu_partage_acceptee(
    programme, cours_lieu_partage, brigade, lieu_partage
):
    """Un lieu réellement de catégorie `lieu_partage` (L9) reste accepté —
    la correction ne doit pas refuser le cas valable."""
    qualifier(cours_lieu_partage.instructeur, cours_lieu_partage.element.matiere)
    candidate = _candidate(
        brigade, cours_lieu_partage, instant(programme.lundi_de_semaine, 0, 8), lieu=lieu_partage
    )

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    assert verdict.accepte


def test_a4_matiere_lieu_partage_laboratoire_en_amphitheatre_refusee(
    programme, cours_lieu_partage_laboratoire, brigade, amphitheatre
):
    """Décision du chef de projet après RECETTE-01/02 (prompt 61 bis) : le
    type de lieu exigé par une matière est une obligation, pas un confort
    d'écran — M2 (laboratoire) doit être refusée dans un amphithéâtre (L4),
    même si les deux sont bien des lieux partagés."""
    qualifier(
        cours_lieu_partage_laboratoire.instructeur, cours_lieu_partage_laboratoire.element.matiere
    )
    candidate = _candidate(
        brigade,
        cours_lieu_partage_laboratoire,
        instant(programme.lundi_de_semaine, 0, 8),
        lieu=amphitheatre,
    )

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    assert not verdict.accepte
    violation = next(v for v in verdict.violations if v["code"] == "RG-37")
    assert "Laboratoire" in violation["message"]
    assert "Amphithéâtre" in violation["message"]


def test_a4_matiere_lieu_partage_laboratoire_dans_un_second_amphitheatre_refusee(
    programme, cours_lieu_partage_laboratoire, brigade
):
    """Même refus pour un second lieu amphithéâtre (L9) — ce n'est pas
    l'identité du lieu qui compte, mais son type."""
    autre_amphitheatre = Lieu.objects.create(
        intitule="Amphithéâtre PLAN 2",
        capacite=60,
        categorie="lieu_partage",
        type_partage="amphitheatre",
        mode_partage=ModePartage.SIMULTANE,
    )
    qualifier(
        cours_lieu_partage_laboratoire.instructeur, cours_lieu_partage_laboratoire.element.matiere
    )
    candidate = _candidate(
        brigade,
        cours_lieu_partage_laboratoire,
        instant(programme.lundi_de_semaine, 0, 8),
        lieu=autre_amphitheatre,
    )

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    assert not verdict.accepte
    violation = next(v for v in verdict.violations if v["code"] == "RG-37")
    assert "Laboratoire" in violation["message"]
    assert "Amphithéâtre" in violation["message"]


def test_a4_matiere_lieu_partage_laboratoire_en_laboratoire_acceptee(
    programme, cours_lieu_partage_laboratoire, brigade, laboratoire
):
    """M2 (laboratoire) reste acceptée dans un lieu réellement de type
    laboratoire (L5) — la correction ne doit pas refuser le cas valable."""
    qualifier(
        cours_lieu_partage_laboratoire.instructeur, cours_lieu_partage_laboratoire.element.matiere
    )
    candidate = _candidate(
        brigade,
        cours_lieu_partage_laboratoire,
        instant(programme.lundi_de_semaine, 0, 8),
        lieu=laboratoire,
    )

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    assert verdict.accepte
