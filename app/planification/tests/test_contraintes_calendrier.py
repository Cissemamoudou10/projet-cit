"""US-PLAN-04, Groupe F — RG-38 : créneau ouvert, aucune période bloquante
dont la portée couvre la brigade. Prompt 30, § 4/§ 8. Données entièrement
fictives.
"""

import datetime

from planification.services.contraintes import Candidate, ServiceContraintes
from planification.tests.conftest import instant, qualifier
from ressources.models import NatureEvenement, PeriodeCalendrier


def _candidate(brigade, cours, debut, duree_min=105):
    fin = debut + datetime.timedelta(minutes=duree_min)
    return Candidate(
        brigade=brigade,
        element_referentiel=cours.element,
        instructeur=cours.instructeur,
        debut=debut,
        fin=fin,
    )


def _periode(lundi, effet, *, heures=(7, 11), sessions=(), brigades=()):
    heure_debut, heure_fin = heures
    nature = NatureEvenement.objects.create(
        libelle=f"Nature {effet} {heure_debut}", effet_par_defaut=effet
    )
    periode = PeriodeCalendrier.objects.create(
        nature=nature,
        intitule="Période RG-38",
        debut=instant(lundi, 0, heure_debut),
        fin=instant(lundi, 0, heure_fin),
        effet=effet,
    )
    if sessions:
        periode.sessions.set(sessions)
    if brigades:
        periode.brigades.set(brigades)
    return periode


# --- F1 — portée centre entier, refus ---------------------------------------


def test_f1_periode_bloquante_centre_entier_refus(programme, cours, brigade):
    lundi = programme.lundi_de_semaine
    qualifier(cours.instructeur, cours.element.matiere)
    _periode(lundi, "bloquant")
    candidate = _candidate(brigade, cours, instant(lundi, 0, 8))

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    assert not verdict.accepte
    assert any(v["code"] == "RG-38" for v in verdict.violations)


# --- F2 — portée ciblant la session de la brigade, refus -------------------


def test_f2_periode_bloquante_ciblant_sa_session_refus(programme, cours, brigade):
    lundi = programme.lundi_de_semaine
    qualifier(cours.instructeur, cours.element.matiere)
    _periode(lundi, "bloquant", sessions=[brigade.session])
    candidate = _candidate(brigade, cours, instant(lundi, 0, 8))

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    assert not verdict.accepte
    assert any(v["code"] == "RG-38" for v in verdict.violations)


# --- F3 — portée ciblant sa brigade, refus ----------------------------------


def test_f3_periode_bloquante_ciblant_sa_brigade_refus(programme, cours, brigade):
    lundi = programme.lundi_de_semaine
    qualifier(cours.instructeur, cours.element.matiere)
    _periode(lundi, "bloquant", brigades=[brigade])
    candidate = _candidate(brigade, cours, instant(lundi, 0, 8))

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    assert not verdict.accepte
    assert any(v["code"] == "RG-38" for v in verdict.violations)


# --- F4 — portée ciblant une AUTRE brigade, acceptée (RG-30) ----------------


def test_f4_periode_bloquante_ciblant_une_autre_brigade_acceptee(
    programme, cours, brigade, autre_brigade
):
    """« EXAMEN FIN STAGE CAT/1 » du terrain : RG-30/RG-38, l'exemple qui
    fonde l'exigence de portée précise."""
    lundi = programme.lundi_de_semaine
    qualifier(cours.instructeur, cours.element.matiere)
    _periode(lundi, "bloquant", brigades=[autre_brigade])
    candidate = _candidate(brigade, cours, instant(lundi, 0, 8))

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    assert verdict.accepte


# --- F5 — période informative, sans effet -----------------------------------


def test_f5_periode_informative_recouvrant_le_creneau_acceptee(programme, cours, brigade):
    lundi = programme.lundi_de_semaine
    qualifier(cours.instructeur, cours.element.matiere)
    _periode(lundi, "informatif")
    candidate = _candidate(brigade, cours, instant(lundi, 0, 8))

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    assert verdict.accepte


# --- F6 — recouvrement partiel, refus ---------------------------------------


def test_f6_recouvrement_partiel_de_la_periode_et_du_creneau_refus(programme, cours, brigade):
    lundi = programme.lundi_de_semaine
    qualifier(cours.instructeur, cours.element.matiere)
    _periode(lundi, "bloquant", heures=(9, 10))
    candidate = _candidate(brigade, cours, instant(lundi, 0, 8), duree_min=105)

    verdict = ServiceContraintes.verifier(candidate, ServiceContraintes.contexte(programme))

    assert not verdict.accepte
    assert any(v["code"] == "RG-38" for v in verdict.violations)
