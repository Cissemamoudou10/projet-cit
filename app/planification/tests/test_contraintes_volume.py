"""US-PLAN-04, Groupe G — RG-39 : volume programmé et prérequis. Deux
arbitrages du Prompt 30 § 4 exercés ici (voir docs/suivi/DECISIONS.md) —
volume programmé = tous les programmes non rejetés SAUF celui évalué ;
prérequis achevé = volume programmé (provisoire, pas encore réalisé) de la
matière prérequise, POUR CETTE BRIGADE, atteignant son prescrit. Données
entièrement fictives.
"""

import datetime

from planification.models import EtatProgramme, LigneProgramme, ProgrammeHebdomadaire, Seance
from planification.services.contraintes import Candidate, ServiceContraintes
from planification.tests.conftest import Cours, creer_element, instant, qualifier
from referentiel.models import Prerequis


def _candidate(brigade, cours, debut, duree_min=120):
    fin = debut + datetime.timedelta(minutes=duree_min)
    return Candidate(
        brigade=brigade,
        element_referentiel=cours.element,
        instructeur=cours.instructeur,
        debut=debut,
        fin=fin,
    )


def _autre_programme(lundi, decalage_semaines=1):
    lundi_autre = lundi + datetime.timedelta(weeks=decalage_semaines)
    return ProgrammeHebdomadaire.objects.create(lundi_de_semaine=lundi_autre)


def _seance_dans(prog, cours, brigade, debut, duree_min=120):
    fin = debut + datetime.timedelta(minutes=duree_min)
    seance = Seance.objects.create(
        programme=prog,
        element_referentiel=cours.element,
        instructeur=cours.instructeur,
        debut=debut,
        fin=fin,
    )
    LigneProgramme.objects.create(seance=seance, brigade=brigade)
    return seance


# --- G1 — volume atteignant exactement le prescrit : refus, chiffré --------


def test_g1_volume_programme_atteignant_le_prescrit_refus_une_seance_de_plus(
    programme, formation, matiere, instructeur, brigade
):
    lundi = programme.lundi_de_semaine
    cours = Cours(creer_element(formation, matiere, volume=2), instructeur)
    qualifier(instructeur, matiere)
    autre_programme = _autre_programme(lundi)
    _seance_dans(autre_programme, cours, brigade, instant(autre_programme.lundi_de_semaine, 0, 8))
    candidate = _candidate(brigade, cours, instant(lundi, 0, 8), duree_min=30)

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    assert not verdict.accepte
    violation = next(v for v in verdict.violations if v["code"] == "RG-39")
    assert "2" in violation["message"]


# --- G2 — volume restant suffisant : accepté --------------------------------


def test_g2_volume_restant_suffisant_accepte(programme, formation, matiere, instructeur, brigade):
    lundi = programme.lundi_de_semaine
    cours = Cours(creer_element(formation, matiere, volume=2), instructeur)
    qualifier(instructeur, matiere)
    autre_programme = _autre_programme(lundi)
    _seance_dans(
        autre_programme,
        cours,
        brigade,
        instant(autre_programme.lundi_de_semaine, 0, 8),
        duree_min=60,
    )
    candidate = _candidate(brigade, cours, instant(lundi, 0, 8), duree_min=30)

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    assert verdict.accepte


# --- G3 — le programme en cours d'évaluation ne compte pas contre lui-même -


def test_g3_le_programme_en_cours_d_evaluation_n_est_pas_compte_contre_lui_meme(
    programme, formation, matiere, instructeur, brigade
):
    """Test du point (a) du § 4 — sans cette exclusion, une régénération
    verrait ses propres séances comme un dépassement."""
    lundi = programme.lundi_de_semaine
    cours = Cours(creer_element(formation, matiere, volume=2), instructeur)
    qualifier(instructeur, matiere)
    _seance_dans(programme, cours, brigade, instant(lundi, 0, 6))
    candidate = _candidate(brigade, cours, instant(lundi, 0, 10))

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    assert verdict.accepte


# --- G4 — comportement des brouillons, testé dans les deux sens ------------


def test_g4_une_seance_d_un_programme_brouillon_compte_dans_le_volume(
    programme, formation, matiere, instructeur, brigade
):
    """Arbitrage retenu : compter tous les programmes NON REJETÉS, brouillon
    inclus — un brouillon abandonné bloquerait sinon le volume à tort dans
    l'autre sens, mais l'inverse (l'ignorer) laisserait une génération
    dépasser le prescrit sans le voir."""
    lundi = programme.lundi_de_semaine
    cours = Cours(creer_element(formation, matiere, volume=2), instructeur)
    qualifier(instructeur, matiere)
    autre_programme = _autre_programme(lundi)
    assert autre_programme.etat == EtatProgramme.BROUILLON
    _seance_dans(autre_programme, cours, brigade, instant(autre_programme.lundi_de_semaine, 0, 8))
    candidate = _candidate(brigade, cours, instant(lundi, 0, 8), duree_min=30)

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    assert not verdict.accepte


def test_g4_une_seance_d_un_programme_rejete_ne_compte_pas_dans_le_volume(
    programme, formation, matiere, instructeur, brigade
):
    lundi = programme.lundi_de_semaine
    cours = Cours(creer_element(formation, matiere, volume=2), instructeur)
    qualifier(instructeur, matiere)
    autre_programme = _autre_programme(lundi)
    _seance_dans(autre_programme, cours, brigade, instant(autre_programme.lundi_de_semaine, 0, 8))
    autre_programme.etat = EtatProgramme.REJETE
    autre_programme.save()
    candidate = _candidate(brigade, cours, instant(lundi, 0, 8), duree_min=30)

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    assert verdict.accepte


# --- G5/G6/G7 — prérequis ----------------------------------------------------


def test_g5_prerequis_non_acheve_refus_matiere_prerequise_nommee(
    programme, formation, matiere, instructeur, brigade
):
    from referentiel.models import Matiere

    matiere_prerequise = Matiere.objects.create(intitule="Bases électroniques", code="BASE1")
    element_prerequis = creer_element(formation, matiere_prerequise, volume=4)
    element = creer_element(formation, matiere, volume=10)
    Prerequis.objects.create(element=element, element_prerequis=element_prerequis)
    qualifier(instructeur, matiere)
    candidate = _candidate(
        brigade, Cours(element, instructeur), instant(programme.lundi_de_semaine, 0, 8)
    )

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    assert not verdict.accepte
    violation = next(
        v for v in verdict.violations if v["code"] == "RG-39" and "prérequise" in v["message"]
    )
    assert str(matiere_prerequise) in violation["message"]


def test_g6_prerequis_acheve_accepte(programme, formation, matiere, instructeur, brigade):
    from referentiel.models import Matiere

    lundi = programme.lundi_de_semaine
    matiere_prerequise = Matiere.objects.create(intitule="Bases électroniques G6", code="BASE2")
    element_prerequis = creer_element(formation, matiere_prerequise, volume=2)
    element = creer_element(formation, matiere, volume=10)
    Prerequis.objects.create(element=element, element_prerequis=element_prerequis)
    qualifier(instructeur, matiere)
    autre_programme = _autre_programme(lundi)
    _seance_dans(
        autre_programme,
        Cours(element_prerequis, instructeur),
        brigade,
        instant(autre_programme.lundi_de_semaine, 0, 8),
    )
    candidate = _candidate(brigade, Cours(element, instructeur), instant(lundi, 0, 8))

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    assert verdict.accepte


def test_g7_matiere_sans_prerequis_acceptee_sans_controle(programme, cours, brigade):
    qualifier(cours.instructeur, cours.element.matiere)
    candidate = _candidate(brigade, cours, instant(programme.lundi_de_semaine, 0, 8))

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    assert verdict.accepte
