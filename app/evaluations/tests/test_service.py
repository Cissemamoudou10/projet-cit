"""US-EVAL-01, bloc B — règles du service, hors insertion de séance (bloc C,
`test_insertion_seance.py`)."""

import datetime

import pytest
from django.utils import timezone

from evaluations.models import TypeEvaluation
from evaluations.services.evaluation import ServiceEvaluation
from noyau.exceptions import ErreurValidation


def _donnees(**kwargs):
    base = {
        "element_referentiel": None,
        "type": TypeEvaluation.CERTIFICATIVE,
        "session": None,
        "brigade": None,
        "date": None,
        "creneau_type": None,
        "instructeur": None,
        "lieu": None,
        "motif_date_passee": "",
    }
    base.update(kwargs)
    return base


def test_b1_module_hors_referentiel_de_la_formation_visee_refuse(
    examens, session, autre_element_referentiel
):
    donnees = _donnees(
        element_referentiel=autre_element_referentiel,
        session=session,
        date=timezone.localdate() + datetime.timedelta(days=30),
    )
    with pytest.raises(ErreurValidation, match="référentiel"):
        ServiceEvaluation.creer(examens, donnees)


def test_b2_date_hors_des_bornes_de_la_session_refuse(examens, session, element_referentiel):
    hors_bornes = session.date_fin + datetime.timedelta(days=10)
    donnees = _donnees(element_referentiel=element_referentiel, session=session, date=hors_bornes)
    with pytest.raises(ErreurValidation, match="hors des bornes"):
        ServiceEvaluation.creer(examens, donnees)


def test_b3_certificative_a_date_passee_refuse(examens, session, element_referentiel):
    donnees = _donnees(
        element_referentiel=element_referentiel,
        session=session,
        date=timezone.localdate() - datetime.timedelta(days=1),
    )
    with pytest.raises(ErreurValidation, match="RG-49"):
        ServiceEvaluation.creer(examens, donnees)


def test_b4_formative_date_passee_sans_motif_refuse(examens, session, element_referentiel):
    donnees = _donnees(
        element_referentiel=element_referentiel,
        type=TypeEvaluation.FORMATIVE,
        session=session,
        date=timezone.localdate() - datetime.timedelta(days=1),
    )
    with pytest.raises(ErreurValidation, match="motif"):
        ServiceEvaluation.creer(examens, donnees)


def test_b4_formative_date_passee_motif_blanc_refuse(examens, session, element_referentiel):
    donnees = _donnees(
        element_referentiel=element_referentiel,
        type=TypeEvaluation.FORMATIVE,
        session=session,
        date=timezone.localdate() - datetime.timedelta(days=1),
        motif_date_passee="   ",
    )
    with pytest.raises(ErreurValidation, match="motif"):
        ServiceEvaluation.creer(examens, donnees)


def test_b4_formative_date_passee_avec_motif_creee_sans_seance(
    examens, session, element_referentiel
):
    donnees = _donnees(
        element_referentiel=element_referentiel,
        type=TypeEvaluation.FORMATIVE,
        session=session,
        date=timezone.localdate() - datetime.timedelta(days=1),
        motif_date_passee="Contrôle tenu, saisie après coup.",
    )
    evaluation = ServiceEvaluation.creer(examens, donnees)
    assert evaluation.pk is not None
    assert evaluation.seance_id is None
    assert evaluation.motif_date_passee == "Contrôle tenu, saisie après coup."


def test_b5_perimetre_session_retourne_un_avertissement_non_bloquant(
    examens, session, element_referentiel
):
    """C9 (A8, forme simplifiée) : systématique, non bloquant, sur tout
    périmètre session."""
    donnees = _donnees(
        element_referentiel=element_referentiel,
        session=session,
        date=timezone.localdate() + datetime.timedelta(days=30),
    )
    evaluation = ServiceEvaluation.creer(examens, donnees)
    assert evaluation.avertissements
    assert evaluation.avertissements[0]["code"] == "A8"


def test_b5_perimetre_brigade_ne_retourne_aucun_avertissement(
    examens, brigade, element_referentiel
):
    donnees = _donnees(
        element_referentiel=element_referentiel,
        brigade=brigade,
        date=timezone.localdate() + datetime.timedelta(days=30),
    )
    evaluation = ServiceEvaluation.creer(examens, donnees)
    assert evaluation.avertissements == []


def test_b6_actions_disponibles_differe_selon_le_type(
    examens, session, brigade, element_referentiel
):
    certificative = ServiceEvaluation.creer(
        examens,
        _donnees(
            element_referentiel=element_referentiel,
            session=session,
            date=timezone.localdate() + datetime.timedelta(days=30),
        ),
    )
    formative_passee = ServiceEvaluation.creer(
        examens,
        _donnees(
            element_referentiel=element_referentiel,
            type=TypeEvaluation.FORMATIVE,
            brigade=brigade,
            date=timezone.localdate() - datetime.timedelta(days=1),
            motif_date_passee="Séance tenue, saisie après coup.",
        ),
    )
    assert ServiceEvaluation.actions_disponibles(
        certificative
    ) != ServiceEvaluation.actions_disponibles(formative_passee)


def test_b7_aucune_methode_de_modification_type_et_perimetre_immuables():
    """A7 : une erreur se corrige par suppression et recréation, jamais par
    une modification du type ou du périmètre."""
    assert not hasattr(ServiceEvaluation, "modifier")
