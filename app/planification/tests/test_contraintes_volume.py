"""US-PLAN-04, Groupe G — RG-39 : volume programmé et prérequis. Deux
arbitrages exercés ici — volume programmé = tous les programmes non rejetés
SAUF celui évalué (Prompt 30 § 4, voir docs/suivi/DECISIONS.md) ; prérequis
achevé = volume RÉALISÉ (RG-60, US-SUI-01, prompt 44, R2 — remplace la
définition provisoire sur le programmé) de la matière prérequise, POUR
CETTE BRIGADE, avant le début de la semaine générée, atteignant son
prescrit. Données entièrement fictives.
"""

import datetime

from django.utils import timezone

from planification.models import EtatProgramme, LigneProgramme, ProgrammeHebdomadaire, Seance
from planification.services.circuit import ServiceCircuitProgramme
from planification.services.contraintes import Candidate, ServiceContraintes
from planification.tests.conftest import Cours, creer_element, instant, qualifier
from referentiel.models import Prerequis

SIGNATAIRE_ESSAI = "Signataire essai G"


def _amener_a_affiche(prog, planificateur, pedagogique):
    ServiceCircuitProgramme.soumettre(planificateur, prog)
    ServiceCircuitProgramme.valider(pedagogique, prog)
    ServiceCircuitProgramme.enregistrer_signature(
        planificateur, prog, timezone.localdate(), SIGNATAIRE_ESSAI
    )
    ServiceCircuitProgramme.afficher(planificateur, prog)


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


def test_g4_une_seance_d_un_programme_rejete_compte_dans_le_volume(
    programme, formation, matiere, instructeur, brigade
):
    """V7, US-VAL-03 (arbitrage A7) : aucun état n'exprime l'abandon, donc un
    programme rejeté compte comme les autres. L'ancien filtre les excluait.

    Exception à P-21 assumée : l'état est posé à la main parce que le test porte
    sur la règle de volume, pas sur le circuit (couvert par test_circuit_*).
    """
    lundi = programme.lundi_de_semaine
    cours = Cours(creer_element(formation, matiere, volume=2), instructeur)
    qualifier(instructeur, matiere)
    autre_programme = _autre_programme(lundi)
    _seance_dans(autre_programme, cours, brigade, instant(autre_programme.lundi_de_semaine, 0, 8))
    autre_programme.etat = EtatProgramme.REJETE
    autre_programme.date_soumission = timezone.now()
    autre_programme.motif_rejet = "Motif de test."
    autre_programme.save()
    candidate = _candidate(brigade, cours, instant(lundi, 0, 8), duree_min=30)

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    assert not verdict.accepte


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


def test_g6_prerequis_realise_et_affiche_avant_la_semaine_accepte(
    programme, cours, brigade, acteurs
):
    """R2 (US-SUI-01, prompt 44) : le prérequis se vérifie désormais sur le
    RÉALISÉ, avant le début de la semaine générée — la matière prérequise
    doit être affichée et terminée avant `lundi`, pas seulement programmée."""
    from referentiel.models import Matiere

    formation, matiere, instructeur, element = (
        cours.element.formation,
        cours.element.matiere,
        cours.instructeur,
        cours.element,
    )
    lundi = programme.lundi_de_semaine
    matiere_prerequise = Matiere.objects.create(intitule="Bases électroniques G6", code="BASE2")
    element_prerequis = creer_element(formation, matiere_prerequise, volume=2)
    Prerequis.objects.create(element=element, element_prerequis=element_prerequis)
    qualifier(instructeur, matiere)
    autre_programme = _autre_programme(lundi, decalage_semaines=-1)
    _seance_dans(
        autre_programme,
        Cours(element_prerequis, instructeur),
        brigade,
        instant(autre_programme.lundi_de_semaine, 0, 8),
    )
    _amener_a_affiche(autre_programme, acteurs.planificateur, acteurs.pedagogique)
    candidate = _candidate(brigade, Cours(element, instructeur), instant(lundi, 0, 8))

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    assert verdict.accepte


def test_g6_bis_prerequis_programme_mais_pas_affiche_reste_non_acheve(
    programme, formation, matiere, instructeur, brigade
):
    """R2 : une semaine dont le programme n'est pas encore affiché ne
    fournit aucun prérequis à la suivante — conséquence assumée, même
    volume que g6, jamais affiché cette fois."""
    from referentiel.models import Matiere

    lundi = programme.lundi_de_semaine
    matiere_prerequise = Matiere.objects.create(intitule="Bases électroniques G6bis", code="BASE2B")
    element_prerequis = creer_element(formation, matiere_prerequise, volume=2)
    element = creer_element(formation, matiere, volume=10)
    Prerequis.objects.create(element=element, element_prerequis=element_prerequis)
    qualifier(instructeur, matiere)
    autre_programme = _autre_programme(lundi, decalage_semaines=-1)
    _seance_dans(
        autre_programme,
        Cours(element_prerequis, instructeur),
        brigade,
        instant(autre_programme.lundi_de_semaine, 0, 8),
    )
    candidate = _candidate(brigade, Cours(element, instructeur), instant(lundi, 0, 8))

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    assert not verdict.accepte


def test_g6_ter_prerequis_retombe_si_non_execution_declaree(programme, cours, brigade, acteurs):
    """R1 : le réalisé exclut les lignes portant une non-exécution — une
    matière prérequise déclarée non exécutée retombe sous le prescrit,
    même affichée et terminée avant la semaine générée."""
    from planification.models import NonExecution
    from referentiel.models import Matiere

    formation, matiere, instructeur, element = (
        cours.element.formation,
        cours.element.matiere,
        cours.instructeur,
        cours.element,
    )
    lundi = programme.lundi_de_semaine
    matiere_prerequise = Matiere.objects.create(intitule="Bases électroniques G6ter", code="BASE2T")
    element_prerequis = creer_element(formation, matiere_prerequise, volume=2)
    Prerequis.objects.create(element=element, element_prerequis=element_prerequis)
    qualifier(instructeur, matiere)
    autre_programme = _autre_programme(lundi, decalage_semaines=-1)
    seance_prerequise = _seance_dans(
        autre_programme,
        Cours(element_prerequis, instructeur),
        brigade,
        instant(autre_programme.lundi_de_semaine, 0, 8),
    )
    _amener_a_affiche(autre_programme, acteurs.planificateur, acteurs.pedagogique)
    NonExecution.objects.create(ligne=seance_prerequise.lignes.get(), motif="Essai G6ter.")
    candidate = _candidate(brigade, Cours(element, instructeur), instant(lundi, 0, 8))

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    assert not verdict.accepte


def test_g7_matiere_sans_prerequis_acceptee_sans_controle(programme, cours, brigade):
    qualifier(cours.instructeur, cours.element.matiere)
    candidate = _candidate(brigade, cours, instant(programme.lundi_de_semaine, 0, 8))

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    assert verdict.accepte


# --- G8 — plafond de volume et cumul provisoire du lot (point 1, Prompt 31) -


def test_g8_deux_candidates_du_meme_lot_meme_matiere_la_seconde_refusee_par_effet_de_lot(
    programme, formation, matiere, instructeur, brigade
):
    """Sans cumul provisoire, chaque candidate ne verrait que le volume déjà
    en base (zéro ici) et les deux passeraient — la génération dépasserait
    le prescrit sans jamais le détecter. Motif chiffré, origine « lot »."""
    lundi = programme.lundi_de_semaine
    cours = Cours(creer_element(formation, matiere, volume=2), instructeur)
    qualifier(instructeur, matiere)
    premiere = _candidate(brigade, cours, instant(lundi, 0, 8), duree_min=120)
    seconde = _candidate(brigade, cours, instant(lundi, 0, 14), duree_min=60)

    verdicts = ServiceContraintes.verifier_lot(
        [premiere, seconde], ServiceContraintes.contexte(programme)
    )

    assert verdicts[0].accepte
    assert not verdicts[1].accepte
    violation = next(v for v in verdicts[1].violations if v["code"] == "RG-39")
    assert violation["origine"] == "lot"
    assert "2" in violation["message"]
