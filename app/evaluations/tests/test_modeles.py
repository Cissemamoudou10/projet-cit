"""US-EVAL-01, bloc A — contraintes en base. Écriture DIRECTE (hors
`ServiceEvaluation`), `IntegrityError` attendue : `.claude/rules/tests.md`,
« vérifier une absence » — ces contraintes sont le dernier filet, pas le
premier contrôle (couche services, `test_service.py`).
"""

import datetime

import pytest
from django.db import IntegrityError, transaction
from django.utils import timezone

from evaluations.models import Evaluation, TypeEvaluation


def test_a1_perimetre_deux_rattachements_renseignes_refuse(element_referentiel, session, brigade):
    with pytest.raises(IntegrityError), transaction.atomic():
        Evaluation.objects.create(
            element_referentiel=element_referentiel,
            session=session,
            brigade=brigade,
            type=TypeEvaluation.CERTIFICATIVE,
            date=timezone.localdate() + datetime.timedelta(days=30),
        )


def test_a2_perimetre_aucun_rattachement_refuse(element_referentiel):
    with pytest.raises(IntegrityError), transaction.atomic():
        Evaluation.objects.create(
            element_referentiel=element_referentiel,
            type=TypeEvaluation.CERTIFICATIVE,
            date=timezone.localdate() + datetime.timedelta(days=30),
        )


def test_a3_date_et_seance_refuse(element_referentiel, session, seance):
    with pytest.raises(IntegrityError), transaction.atomic():
        Evaluation.objects.create(
            element_referentiel=element_referentiel,
            session=session,
            type=TypeEvaluation.FORMATIVE,
            date=timezone.localdate() + datetime.timedelta(days=30),
            seance=seance,
        )


def test_a4_ni_date_ni_seance_refuse(element_referentiel, session):
    with pytest.raises(IntegrityError), transaction.atomic():
        Evaluation.objects.create(
            element_referentiel=element_referentiel,
            session=session,
            type=TypeEvaluation.CERTIFICATIVE,
        )


def test_a5_certificative_portant_une_seance_refuse(element_referentiel, session, seance):
    with pytest.raises(IntegrityError), transaction.atomic():
        Evaluation.objects.create(
            element_referentiel=element_referentiel,
            session=session,
            type=TypeEvaluation.CERTIFICATIVE,
            seance=seance,
        )


def test_a6_motif_renseigne_sur_une_certificative_refuse(element_referentiel, session):
    with pytest.raises(IntegrityError), transaction.atomic():
        Evaluation.objects.create(
            element_referentiel=element_referentiel,
            session=session,
            type=TypeEvaluation.CERTIFICATIVE,
            date=timezone.localdate() + datetime.timedelta(days=30),
            motif_date_passee="motif non attendu",
        )


def test_a7_motif_renseigne_sur_une_formative_avec_seance_refuse(
    element_referentiel, session, seance
):
    with pytest.raises(IntegrityError), transaction.atomic():
        Evaluation.objects.create(
            element_referentiel=element_referentiel,
            session=session,
            type=TypeEvaluation.FORMATIVE,
            seance=seance,
            motif_date_passee="motif non attendu",
        )


def test_a8_aucune_colonne_perimetre_ni_date_recopiee_sur_la_seance(element_referentiel, session):
    """Constat du schéma (A1/A2, D-175/D-176) : `perimetre` n'est pas une
    colonne, `Seance` ne porte aucune colonne de date recopiée depuis une
    évaluation."""
    from planification.models import Seance

    champs_evaluation = {champ.name for champ in Evaluation._meta.get_fields()}
    assert "perimetre" not in champs_evaluation

    champs_seance = {champ.name for champ in Seance._meta.get_fields()}
    assert not any(
        nom.startswith("date_evaluation") or nom == "evaluation_date" for nom in champs_seance
    )
