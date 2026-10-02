"""US-EVAL-02, bloc B — modification de la date d'un examen final (A6)."""

import datetime

import pytest
from django.utils import timezone

from administration.models import EntreeJournal
from evaluations.models import Evaluation, TypeEvaluation
from evaluations.services.evaluation import ServiceEvaluation
from noyau.exceptions import ErreurValidation


def _certificative(examens, element_referentiel, brigade, jours=30):
    donnees = {
        "element_referentiel": element_referentiel,
        "type": "certificative",
        "session": None,
        "brigade": brigade,
        "date": timezone.localdate() + datetime.timedelta(days=jours),
        "creneau_type": None,
        "instructeur": None,
        "lieu": None,
        "motif_date_passee": "",
    }
    return ServiceEvaluation.creer(examens, donnees)


def test_b1_modification_avec_motif_journal_porte_ancienne_et_nouvelle_date(controle):
    evaluation = _certificative(controle.examens, controle.element_referentiel, controle.brigade)
    ancienne_date = evaluation.date
    nouvelle_date = ancienne_date + datetime.timedelta(days=5)
    ServiceEvaluation.modifier_date_certificative(
        controle.examens, evaluation, nouvelle_date, "Report notifié par le 3e bureau."
    )
    evaluation.refresh_from_db()
    assert evaluation.date == nouvelle_date

    entree = EntreeJournal.objects.filter(
        objet_type="evaluation", objet_identifiant=str(evaluation.pk)
    ).latest("cree_le")
    assert entree.valeur_avant["date"] == str(ancienne_date)
    assert entree.valeur_apres["date"] == str(nouvelle_date)
    assert "notifié" in entree.valeur_apres["motif"]
    assert entree.auteur == controle.examens


def test_b2_motif_vide_puis_blanc_refuse_date_inchangee(controle):
    evaluation = _certificative(controle.examens, controle.element_referentiel, controle.brigade)
    ancienne_date = evaluation.date
    with pytest.raises(ErreurValidation, match="motif"):
        ServiceEvaluation.modifier_date_certificative(
            controle.examens, evaluation, ancienne_date + datetime.timedelta(days=1), ""
        )
    with pytest.raises(ErreurValidation, match="motif"):
        ServiceEvaluation.modifier_date_certificative(
            controle.examens, evaluation, ancienne_date + datetime.timedelta(days=1), "   "
        )
    evaluation.refresh_from_db()
    assert evaluation.date == ancienne_date


def test_b3_nouvelle_date_hors_des_bornes_de_la_session_refuse(controle):
    evaluation = _certificative(controle.examens, controle.element_referentiel, controle.brigade)
    hors_bornes = controle.brigade.session.date_fin + datetime.timedelta(days=10)
    with pytest.raises(ErreurValidation, match="hors des bornes"):
        ServiceEvaluation.modifier_date_certificative(
            controle.examens, evaluation, hors_bornes, "Report notifié par le 3e bureau."
        )


def test_b4_nouvelle_date_passee_refuse(controle):
    evaluation = _certificative(controle.examens, controle.element_referentiel, controle.brigade)
    with pytest.raises(ErreurValidation, match="RG-49"):
        ServiceEvaluation.modifier_date_certificative(
            controle.examens,
            evaluation,
            timezone.localdate() - datetime.timedelta(days=1),
            "Report notifié par le 3e bureau.",
        )


def test_b4_examen_echu_refuse(controle):
    evaluation = _certificative(controle.examens, controle.element_referentiel, controle.brigade)
    Evaluation.objects.filter(pk=evaluation.pk).update(
        date=timezone.localdate() - datetime.timedelta(days=1)
    )
    evaluation.refresh_from_db()
    with pytest.raises(ErreurValidation, match="échue|échu"):
        ServiceEvaluation.modifier_date_certificative(
            controle.examens,
            evaluation,
            timezone.localdate() + datetime.timedelta(days=10),
            "Report notifié par le 3e bureau.",
        )


def test_b5_formative_avec_seance_refuse_nommant_us_plan_05(controle):
    evaluation = ServiceEvaluation.creer(
        controle.examens,
        {
            "element_referentiel": controle.element_referentiel,
            "type": TypeEvaluation.FORMATIVE,
            "session": None,
            "brigade": controle.brigade,
            "date": controle.jour_creneau.jour,
            "creneau_type": controle.jour_creneau.creneau,
            "instructeur": controle.instructeur,
            "lieu": None,
            "motif_date_passee": "",
        },
    )
    with pytest.raises(ErreurValidation, match="US-PLAN-05"):
        ServiceEvaluation.modifier_date_certificative(
            controle.examens,
            evaluation,
            controle.jour_creneau.jour + datetime.timedelta(days=1),
            "motif",
        )


def test_b5_formative_declaree_apres_coup_refuse(controle):
    evaluation = ServiceEvaluation.creer(
        controle.examens,
        {
            "element_referentiel": controle.element_referentiel,
            "type": TypeEvaluation.FORMATIVE,
            "session": None,
            "brigade": controle.brigade,
            "date": timezone.localdate() - datetime.timedelta(days=1),
            "creneau_type": None,
            "instructeur": None,
            "lieu": None,
            "motif_date_passee": "Séance tenue, saisie après coup.",
        },
    )
    with pytest.raises(ErreurValidation, match="figée"):
        ServiceEvaluation.modifier_date_certificative(
            controle.examens,
            evaluation,
            timezone.localdate() + datetime.timedelta(days=10),
            "motif",
        )


def test_b6_libelle_date_imposee_calcule_sans_champ_stocke():
    champs = {champ.name for champ in Evaluation._meta.get_fields()}
    assert not any("imposee" in nom or "impose" in nom for nom in champs)
