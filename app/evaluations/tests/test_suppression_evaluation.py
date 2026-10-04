"""US-PLAN-05, groupe D — séance de contrôle et suppression d'une évaluation
(prompt 41, M7 et M8). Données fictives. Les montages réutilisent les fixtures
et la fabrique de formative de `conftest.py`.
"""

import datetime

import pytest

from evaluations.models import Evaluation, OrganisationEpreuve, Sujet
from evaluations.services.evaluation import ServiceEvaluation
from evaluations.tests.conftest import _formative
from noyau.exceptions import ErreurValidation
from planification.models import Seance
from planification.services.ecriture import ServiceEcritureSeance


def _seance_de_controle(controle):
    evaluation = _formative(controle)
    return evaluation, Seance.objects.get(pk=evaluation.seance_id)


# --- D1 — séance de contrôle : ni déverrouillage, ni suppression directe ----


def test_d1_la_seance_de_controle_ne_se_deverrouille_pas(controle, planificateur):
    _, seance = _seance_de_controle(controle)
    with pytest.raises(ErreurValidation, match="ne se déverrouille pas"):
        ServiceEcritureSeance.deverrouiller_seance(planificateur, seance)
    seance.refresh_from_db()
    assert seance.verrouillee is True


def test_d1_la_seance_de_controle_ne_se_supprime_pas_directement(controle, planificateur):
    _, seance = _seance_de_controle(controle)
    with pytest.raises(ErreurValidation, match="ne se supprime pas"):
        ServiceEcritureSeance.supprimer_seance(planificateur, seance)
    assert Seance.objects.filter(pk=seance.pk).exists()


def test_d1_le_deplacement_de_la_seance_de_controle_admis_et_la_date_suit(controle, planificateur):
    """Une formative lit sa date sur sa séance (A2) : déplacer la séance déplace
    la date de l'évaluation, sans qu'aucune date ne soit recopiée."""
    evaluation, seance = _seance_de_controle(controle)
    attendu = seance.debut + datetime.timedelta(days=1)
    ServiceEcritureSeance.modifier_seance(
        planificateur,
        seance,
        {"debut": attendu, "fin": seance.fin + datetime.timedelta(days=1)},
    )
    evaluation.refresh_from_db()
    assert evaluation.seance_id == seance.pk
    assert Seance.objects.get(pk=seance.pk).debut == attendu
    assert evaluation.date is None


# --- D2 — suppression d'une formative avec séance ---------------------------


def test_d2_suppression_d_une_formative_avec_seance_supprime_les_deux(controle):
    evaluation, seance = _seance_de_controle(controle)
    evaluation_pk, seance_pk = evaluation.pk, seance.pk

    ServiceEvaluation.supprimer(controle.examens, evaluation)

    assert not Evaluation.objects.filter(pk=evaluation_pk).exists()
    assert not Seance.objects.filter(pk=seance_pk).exists()


# --- D3 — organisée ou sujet retenu : refus ---------------------------------


def test_d3_evaluation_organisee_ne_se_supprime_pas(controle, brigade, lieu):
    evaluation, seance = _seance_de_controle(controle)
    OrganisationEpreuve.objects.create(evaluation=evaluation, brigade=brigade, lieu=lieu, effectif_attendu=1)

    with pytest.raises(ErreurValidation, match="organisée"):
        ServiceEvaluation.supprimer(controle.examens, evaluation)
    assert Evaluation.objects.filter(pk=evaluation.pk).exists()
    assert Seance.objects.filter(pk=seance.pk).exists()


def test_d3_evaluation_a_sujet_retenu_ne_se_supprime_pas(controle):
    evaluation, seance = _seance_de_controle(controle)
    Sujet.objects.create(evaluation=evaluation, rang=1, reference="Sujet essai", date_depot="2026-01-15", retenu=True)

    with pytest.raises(ErreurValidation, match="sujet est retenu"):
        ServiceEvaluation.supprimer(controle.examens, evaluation)
    assert Evaluation.objects.filter(pk=evaluation.pk).exists()
