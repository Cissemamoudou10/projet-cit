"""US-PLAN-04, Groupe E — RG-37 (et RG-40) : lieu de la séance. Prompt 30,
§ 4/§ 8. Données entièrement fictives.
"""

import datetime

import pytest

from planification.models import LigneProgramme, Seance
from planification.services.contraintes import Candidate, ServiceContraintes
from planification.tests.conftest import (
    Cours,
    affecter_stagiaires,
    creer_element,
    instant,
    qualifier,
)
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


def _seance_existante(programme, cours, brigade, debut, lieu=None):
    fin = debut + datetime.timedelta(minutes=DUREE_DEFAUT_MIN)
    seance = Seance.objects.create(
        programme=programme,
        element_referentiel=cours.element,
        instructeur=cours.instructeur,
        lieu=lieu,
        debut=debut,
        fin=fin,
    )
    LigneProgramme.objects.create(seance=seance, brigade=brigade)
    return seance


@pytest.fixture
def element_lieu_partage(formation, matiere):
    return creer_element(
        formation, matiere, categorie=CategorieLieu.LIEU_PARTAGE, type_lieu_partage="amphitheatre"
    )


@pytest.fixture
def element_salle_attitree(formation, matiere):
    return creer_element(formation, matiere, categorie=CategorieLieu.SALLE_ATTITREE)


@pytest.fixture
def cours_lieu_partage(element_lieu_partage, instructeur):
    return Cours(element_lieu_partage, instructeur)


@pytest.fixture
def cours_salle_attitree(element_salle_attitree, instructeur):
    return Cours(element_salle_attitree, instructeur)


# --- E1 — occupation, refus --------------------------------------------------


def test_e1_lieu_partage_occupe_par_une_autre_brigade_refus_seance_et_brigade_nommees(
    programme, cours_lieu_partage, brigade, autre_brigade, lieu_partage
):
    lundi = programme.lundi_de_semaine
    qualifier(cours_lieu_partage.instructeur, cours_lieu_partage.element.matiere)
    _seance_existante(
        programme, cours_lieu_partage, brigade, instant(lundi, 0, 8), lieu=lieu_partage
    )
    candidate = _candidate(
        autre_brigade, cours_lieu_partage, instant(lundi, 0, 8, 30), lieu=lieu_partage
    )

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    assert not verdict.accepte
    violation = next(v for v in verdict.violations if v["code"] == "RG-37")
    assert str(lieu_partage) in violation["message"]
    assert str(brigade) in violation["message"]
    assert violation["origine"] == "base"


# --- E2/E3 — capacité contre effectif réel (salle attitrée) -----------------


def test_e2_capacite_insuffisante_pour_l_effectif_reel_refus_ecart_chiffre(
    programme, planificateur, redacteur, cours_salle_attitree, brigade
):
    """`ServiceAffectation` refuse déjà, lui, de dépasser la capacité au
    moment d'affecter (RG-19, D-104) : l'effectif réel ne peut donc jamais
    la dépasser PAR CE CHEMIN. Le déficit vient ici d'un lieu dont la
    capacité a été RÉDUITE après coup (édition du lieu, hors périmètre de
    RG-19 qui ne surveille que l'affectation) — écriture directe en base,
    seul moyen de placer l'état, RG-37 n'a pas à savoir comment on y est
    arrivé."""
    qualifier(cours_salle_attitree.instructeur, cours_salle_attitree.element.matiere)
    lieu = Lieu.objects.create(intitule="Salle E2", capacite=20, categorie="salle_attitree")
    ServiceSalleAttitree.attribuer(planificateur, brigade, lieu)
    affecter_stagiaires(redacteur, brigade, 20, prefixe="E2")
    Lieu.objects.filter(pk=lieu.pk).update(capacite=18)
    candidate = _candidate(brigade, cours_salle_attitree, instant(programme.lundi_de_semaine, 0, 8))

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    assert not verdict.accepte
    violation = next(v for v in verdict.violations if v["code"] == "RG-37")
    assert "2" in violation["message"]


def test_e3_capacite_exactement_egale_a_l_effectif_acceptee(
    programme, planificateur, redacteur, cours_salle_attitree, brigade
):
    qualifier(cours_salle_attitree.instructeur, cours_salle_attitree.element.matiere)
    lieu = Lieu.objects.create(intitule="Salle E3", capacite=20, categorie="salle_attitree")
    ServiceSalleAttitree.attribuer(planificateur, brigade, lieu)
    affecter_stagiaires(redacteur, brigade, 20, prefixe="E3")
    candidate = _candidate(brigade, cours_salle_attitree, instant(programme.lundi_de_semaine, 0, 8))

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    assert verdict.accepte


# --- E4 — matière sans lieu, aucun contrôle ---------------------------------


def test_e4_matiere_sans_lieu_aucun_controle_meme_si_tous_les_lieux_sont_occupes(
    programme, cours, brigade
):
    """`cours.element` (fixture `element_referentiel`) est catégorie
    AUCUN_LIEU par défaut."""
    qualifier(cours.instructeur, cours.element.matiere)
    candidate = _candidate(brigade, cours, instant(programme.lundi_de_semaine, 0, 8), lieu=None)

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    assert verdict.accepte


# --- E5 — rattrapage de la limite consignée à US-SES-03 ---------------------


def test_e5_salle_attitree_capacite_devenue_insuffisante_apres_croissance_effectif_detectee(
    programme, planificateur, redacteur, cours_salle_attitree, brigade
):
    """La capacité suffisait à l'attribution (RG-13, US-SES-03) ; devenue
    insuffisante depuis (édition du lieu — RG-19 ne surveille que
    l'affectation, jamais une modification ultérieure du lieu lui-même,
    limite déjà consignée à US-SES-03/D-90) — ce rattrapage n'existait pas
    avant cette story."""
    qualifier(cours_salle_attitree.instructeur, cours_salle_attitree.element.matiere)
    lieu = Lieu.objects.create(intitule="Salle E5", capacite=20, categorie="salle_attitree")
    ServiceSalleAttitree.attribuer(planificateur, brigade, lieu)
    affecter_stagiaires(redacteur, brigade, 20, prefixe="E5A")
    candidate = _candidate(brigade, cours_salle_attitree, instant(programme.lundi_de_semaine, 0, 8))
    assert ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme)).accepte

    Lieu.objects.filter(pk=lieu.pk).update(capacite=18)

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))
    assert not verdict.accepte
    assert any(v["code"] == "RG-37" for v in verdict.violations)


# --- E6 — capacité non renseignée : REFUS, message correctif ---------------


def test_e6_capacite_non_renseignee_refus_message_correctif(
    programme, cours_lieu_partage, brigade, lieu_partage
):
    """RG-37, § 4 (directive utilisateur) : une capacité vide signifie
    « on ne sait pas », jamais « illimité » — objet non persisté, comme
    D-88 (la base elle-même refuse ce cas pour un lieu réellement créé,
    `ck_lieu_capacite_positive`)."""
    qualifier(cours_lieu_partage.instructeur, cours_lieu_partage.element.matiere)
    lieu_partage.capacite = None
    candidate = _candidate(
        brigade, cours_lieu_partage, instant(programme.lundi_de_semaine, 0, 8), lieu=lieu_partage
    )

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    assert not verdict.accepte
    violation = next(v for v in verdict.violations if v["code"] == "RG-37")
    assert "capacité" in violation["message"].lower()
    assert "renseign" in violation["message"].lower()
    assert str(lieu_partage) in violation["message"]


# --- E7 — mode séquentiel : refus même regroupé -----------------------------


def test_e7_mode_sequentiel_deux_brigades_meme_lieu_meme_creneau_refus_meme_regroupe(
    programme, cours_lieu_partage, brigade, autre_brigade
):
    lieu_sequentiel = Lieu.objects.create(
        intitule="Labo séquentiel",
        capacite=50,
        categorie="lieu_partage",
        type_partage="laboratoire",
        mode_partage=ModePartage.SEQUENTIEL,
    )
    qualifier(cours_lieu_partage.instructeur, cours_lieu_partage.element.matiere)
    debut = instant(programme.lundi_de_semaine, 0, 8)
    candidates = [
        _candidate(b, cours_lieu_partage, debut, lieu=lieu_sequentiel, cle_regroupement="groupe-e7")
        for b in (brigade, autre_brigade)
    ]

    verdicts = ServiceContraintes.verifier_lot(candidates, ServiceContraintes.contexte(programme))

    assert verdicts[0].accepte
    assert not verdicts[1].accepte
    assert any(v["code"] == "RG-37" for v in verdicts[1].violations)


# --- E8 — regroupement simultané : capacité sur la somme --------------------


def test_e8_regroupement_simultane_capacite_couvrant_la_somme_accepte(
    programme, redacteur, cours_lieu_partage, brigade, autre_brigade
):
    lieu = Lieu.objects.create(
        intitule="Amphi E8",
        capacite=40,
        categorie="lieu_partage",
        type_partage="amphitheatre",
        mode_partage=ModePartage.SIMULTANE,
    )
    qualifier(cours_lieu_partage.instructeur, cours_lieu_partage.element.matiere)
    affecter_stagiaires(redacteur, brigade, 20, prefixe="E8A")
    affecter_stagiaires(redacteur, autre_brigade, 20, prefixe="E8B")
    debut = instant(programme.lundi_de_semaine, 0, 8)
    candidates = [
        _candidate(b, cours_lieu_partage, debut, lieu=lieu, cle_regroupement="groupe-e8")
        for b in (brigade, autre_brigade)
    ]

    verdicts = ServiceContraintes.verifier_lot(candidates, ServiceContraintes.contexte(programme))

    assert all(verdict.accepte for verdict in verdicts)


def test_e8_regroupement_simultane_capacite_insuffisante_pour_la_somme_refus(
    programme, redacteur, cours_lieu_partage, brigade, autre_brigade
):
    lieu = Lieu.objects.create(
        intitule="Amphi E8 bis",
        capacite=30,
        categorie="lieu_partage",
        type_partage="amphitheatre",
        mode_partage=ModePartage.SIMULTANE,
    )
    qualifier(cours_lieu_partage.instructeur, cours_lieu_partage.element.matiere)
    affecter_stagiaires(redacteur, brigade, 20, prefixe="E8C")
    affecter_stagiaires(redacteur, autre_brigade, 20, prefixe="E8D")
    debut = instant(programme.lundi_de_semaine, 0, 8)
    candidates = [
        _candidate(b, cours_lieu_partage, debut, lieu=lieu, cle_regroupement="groupe-e8b")
        for b in (brigade, autre_brigade)
    ]

    verdicts = ServiceContraintes.verifier_lot(candidates, ServiceContraintes.contexte(programme))

    assert verdicts[0].accepte
    assert not verdicts[1].accepte
    assert any(v["code"] == "RG-37" for v in verdicts[1].violations)
