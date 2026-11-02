"""RG-39 a) modifiée — prompt 56, R01-VAL03-03 (défaut latent révélé par la
preuve sur la session entière, docs/suivi/DECISIONS.md) : une séance se
place tant que le volume déjà programmé (base + lot) reste strictement
inférieur au prescrit, même si SA PROPRE durée fait dépasser ce prescrit.
Le dépassement final est donc toujours inférieur à la durée d'une séance.
Scindé de `test_contraintes_volume.py`/`test_contraintes_volume_par_
brigade.py` (G1 à G12, inchangés hors G10/G10bis/G12) : cinq tests
nouveaux, dédiés à la tolérance elle-même. Données entièrement fictives.
"""

import datetime

import pytest
from django.utils import timezone

from noyau.exceptions import ErreurValidation
from planification.models import LigneProgramme, ProgrammeHebdomadaire, Seance
from planification.selectors_ecart_volume import ecarts_volume_horaire
from planification.services.circuit import ServiceCircuitProgramme
from planification.services.contraintes import Candidate, ServiceContraintes
from planification.services.ecriture import ServiceEcritureSeance
from planification.statut_volume import DEPASSEMENT
from planification.tests.conftest import Cours, creer_element, instant, qualifier
from referentiel.models import Prerequis

SIGNATAIRE_ESSAI = "Signataire essai tolérance"


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


def _amener_a_affiche(prog, planificateur, pedagogique):
    ServiceCircuitProgramme.soumettre(planificateur, prog)
    ServiceCircuitProgramme.valider(pedagogique, prog)
    ServiceCircuitProgramme.enregistrer_signature(
        planificateur, prog, timezone.localdate(), SIGNATAIRE_ESSAI
    )
    ServiceCircuitProgramme.afficher(planificateur, prog)


def test_derniere_seance_acceptee_malgre_le_depassement(
    programme, formation, matiere, instructeur, brigade
):
    """Reste = 0,5 h (1,5 h déjà programmées sur 2 h prescrites), plus
    petit que la candidate de 1 h proposée — avant = 1,5 < 2 : acceptée,
    même si le total (2,5 h) dépasse le prescrit."""
    lundi = programme.lundi_de_semaine
    cours = Cours(creer_element(formation, matiere, volume=2), instructeur)
    qualifier(instructeur, matiere)
    autre_programme = _autre_programme(lundi)
    _seance_dans(
        autre_programme,
        cours,
        brigade,
        instant(autre_programme.lundi_de_semaine, 0, 8),
        duree_min=90,
    )
    candidate = _candidate(brigade, cours, instant(lundi, 0, 8), duree_min=60)

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    assert verdict.accepte


def test_seance_refusee_une_fois_le_prescrit_atteint(
    programme, formation, matiere, instructeur, brigade
):
    """Une fois le déjà-programmé AU-DELÀ du prescrit (2,5 h sur 2 h,
    dépassement précédent déjà toléré), plus aucune séance de cette
    matière — avant = 2,5 ≥ 2, origine « base »."""
    lundi = programme.lundi_de_semaine
    cours = Cours(creer_element(formation, matiere, volume=2), instructeur)
    qualifier(instructeur, matiere)
    autre_programme = _autre_programme(lundi)
    _seance_dans(
        autre_programme,
        cours,
        brigade,
        instant(autre_programme.lundi_de_semaine, 0, 8),
        duree_min=150,
    )
    candidate = _candidate(brigade, cours, instant(lundi, 0, 8), duree_min=30)

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    assert not verdict.accepte
    violation = next(v for v in verdict.violations if v["code"] == "RG-39")
    assert violation["origine"] == "base"


def _referentiel_prerequis_tolerance(formation, instructeur):
    from referentiel.models import Matiere

    matiere_prerequise = Matiere.objects.create(intitule="Prérequise tolérance", code="TOL-PRE")
    matiere_dependante = Matiere.objects.create(intitule="Dépendante tolérance", code="TOL-DEP")
    element_prerequis = creer_element(formation, matiere_prerequise, volume=2)
    element_dependant = creer_element(formation, matiere_dependante, volume=10)
    Prerequis.objects.create(element=element_dependant, element_prerequis=element_prerequis)
    qualifier(instructeur, matiere_prerequise)
    qualifier(instructeur, matiere_dependante)
    return element_prerequis, element_dependant


def _placer_et_afficher(cours_prerequis, brigade, acteurs, prog, duree_min):
    _seance_dans(prog, cours_prerequis, brigade, instant(prog.lundi_de_semaine, 0, 8), duree_min)
    _amener_a_affiche(prog, acteurs.planificateur, acteurs.pedagogique)


def _placer_prerequise_initiale(cours_prerequis, brigade, acteurs, lundi):
    """1,5 h, affichée — sous le prescrit (2 h) : le prérequis bloque
    encore."""
    semaine_moins_deux = _autre_programme(lundi, decalage_semaines=-2)
    _placer_et_afficher(cours_prerequis, brigade, acteurs, semaine_moins_deux, 90)


def test_prerequis_acheve_apres_la_derniere_seance_malgre_le_depassement(
    programme, formation, instructeur, brigade, acteurs
):
    """RG-39 b) (inchangée, réalisé ≥ prescrit) redevient atteignable grâce
    à RG-39 a) modifiée : sans la tolérance, le réalisé de la prérequise
    plafonnerait sous 2 h et le prérequis ne s'achèverait jamais. Avec la
    tolérance, la seconde séance (1 h) se place malgré le dépassement
    (1,5 + 1 = 2,5 > 2, avant = 1,5 < 2), et le réalisé total achève le
    prérequis pour la matière dépendante."""
    element_prerequis, element_dependant = _referentiel_prerequis_tolerance(formation, instructeur)
    cours_prerequis = Cours(element_prerequis, instructeur)
    lundi = programme.lundi_de_semaine
    candidate_dependante = _candidate(brigade, Cours(element_dependant, instructeur), instant(lundi, 0, 8))

    _placer_prerequise_initiale(cours_prerequis, brigade, acteurs, lundi)
    verdict_avant = ServiceContraintes.verifier(
        candidate_dependante, ServiceContraintes.contexte(programme)
    )
    assert not verdict_avant.accepte, "réalisé = 1,5 h < 2 h prescrites : le prérequis bloque encore"

    semaine_moins_une = _autre_programme(lundi, decalage_semaines=-1)
    candidate_prerequis_2 = _candidate(
        brigade, cours_prerequis, instant(semaine_moins_une.lundi_de_semaine, 0, 8), duree_min=60
    )
    verdict_prerequis_2 = ServiceContraintes.verifier(
        candidate_prerequis_2, ServiceContraintes.contexte(semaine_moins_une)
    )
    assert verdict_prerequis_2.accepte, "le dépassement de la seconde séance reste toléré"
    _placer_et_afficher(cours_prerequis, brigade, acteurs, semaine_moins_une, 60)

    verdict_apres = ServiceContraintes.verifier(
        candidate_dependante, ServiceContraintes.contexte(programme)
    )
    assert verdict_apres.accepte, "réalisé = 2,5 h ≥ 2 h prescrites : le prérequis est achevé"


def _lignes_pour_element(groupes, element):
    return [
        ligne
        for groupe in groupes
        for ligne in groupe.lignes
        if ligne.element_referentiel.pk == element.pk
    ]


def test_indicateur_sans_faux_signalement_pour_le_depassement_tolere(
    scenario, formation, matiere, instructeur, brigade_formation
):
    """US-PLAN-07 : le dépassement qu'une séance générée peut causer (borné
    par le plus long créneau de la grille active, § RG-39 a)) n'est pas
    signalé comme sur-programmation ; un dépassement dû à autre chose (ici
    un prescrit réduit après coup, comme R04-PLAN07-03) l'est toujours."""
    element = creer_element(formation, matiere, volume=2)
    qualifier(instructeur, matiere)
    prog = ProgrammeHebdomadaire.objects.create(lundi_de_semaine=scenario.lundi)
    _seance_dans(
        prog,
        Cours(element, instructeur),
        brigade_formation,
        instant(prog.lundi_de_semaine, 0, 8),
        duree_min=180,
    )

    lignes_toleres = _lignes_pour_element(ecarts_volume_horaire([brigade_formation]), element)
    assert lignes_toleres == [], (
        "dépassement de 1 h (3 h programmées sur 2 h prescrites), sous le plus long "
        "créneau de la grille (1h50) : pas une sur-programmation"
    )

    element.volume_horaire_prescrit = 1
    element.save()

    lignes_reelles = _lignes_pour_element(ecarts_volume_horaire([brigade_formation]), element)
    assert len(lignes_reelles) == 1, "prescrit réduit après coup : un vrai dépassement, signalé"
    assert lignes_reelles[0].statut == DEPASSEMENT


def test_modification_manuelle_soumise_a_la_meme_regle(
    scenario, formation, matiere, instructeur, brigade_formation
):
    """Une seule implantation (`regles_volume._verifier_volume`) : la
    saisie manuelle (`ServiceEcritureSeance.creer_seance`, US-PLAN-05)
    tolère le même dépassement que la génération, et refuse de la même
    façon une fois le prescrit atteint."""
    element = creer_element(formation, matiere, volume=2)
    qualifier(instructeur, matiere)
    cours = Cours(element, instructeur)
    lundi = scenario.lundi
    programme = ProgrammeHebdomadaire.objects.create(lundi_de_semaine=lundi)
    autre_programme = _autre_programme(lundi, decalage_semaines=-1)
    _seance_dans(
        autre_programme, cours, brigade_formation, instant(autre_programme.lundi_de_semaine, 0, 8),
        duree_min=90,
    )

    candidate_tolere = _candidate(brigade_formation, cours, instant(lundi, 0, 8), duree_min=60)
    seance = ServiceEcritureSeance.creer_seance(
        scenario.planificateur, programme, [candidate_tolere]
    )
    assert Seance.objects.filter(pk=seance.pk).exists()

    candidate_refusee = _candidate(brigade_formation, cours, instant(lundi, 2, 8), duree_min=30)
    with pytest.raises(ErreurValidation, match="RG-39"):
        ServiceEcritureSeance.creer_seance(scenario.planificateur, programme, [candidate_refusee])
