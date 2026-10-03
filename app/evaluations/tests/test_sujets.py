"""US-EVAL-03 — enregistrer les sujets transmis, sélectionner celui retenu :
contraintes en base (bloc A) et règles de service (bloc B). RG-50, RG-50 bis,
RG-51, CLS-05, Prompt 37. Confidentialité et cycle HTTP : voir
`test_sujets_ecran.py`. Fixtures partagées dans `conftest.py`. Données
entièrement fictives.
"""

import datetime

import pytest
from django.db import IntegrityError, transaction
from django.utils import timezone

from administration.models import EntreeJournal, TypeAction
from evaluations.models import Sujet
from evaluations.services.evaluation import ServiceEvaluation
from evaluations.services.sujet import ServiceSujet
from evaluations.tests.conftest import _enregistrer
from noyau.exceptions import ErreurValidation

# --- A — Base, contraintes en base -----------------------------------------


def test_a1_troisieme_sujet_rang_refuse(certificative, examens):
    _enregistrer(examens, certificative, "Sujet A")
    _enregistrer(examens, certificative, "Sujet B")
    with pytest.raises(IntegrityError, match="ck_sujet_rang"), transaction.atomic():
        Sujet.objects.create(
            evaluation=certificative, rang=3, reference="Sujet C", date_depot=timezone.localdate()
        )


def test_a2_deux_sujets_meme_rang_refuse(certificative, examens):
    _enregistrer(examens, certificative, "Sujet A")
    with pytest.raises(IntegrityError, match="uq_sujet_evaluation_rang"), transaction.atomic():
        Sujet.objects.create(
            evaluation=certificative, rang=1, reference="Sujet B", date_depot=timezone.localdate()
        )


def test_a3_deux_sujets_retenus_refuse(certificative, examens):
    sujet_a = _enregistrer(examens, certificative, "Sujet A")
    sujet_b = _enregistrer(examens, certificative, "Sujet B")
    Sujet.objects.filter(pk=sujet_a.pk).update(retenu=True)
    with pytest.raises(IntegrityError, match="uq_sujet_un_seul_retenu"), transaction.atomic():
        Sujet.objects.filter(pk=sujet_b.pk).update(retenu=True)


def test_a4_reference_blanche_refuse(certificative):
    with pytest.raises(IntegrityError, match="ck_sujet_reference_non_vide"), transaction.atomic():
        Sujet.objects.create(
            evaluation=certificative, rang=1, reference="   ", date_depot=timezone.localdate()
        )


def test_a5_meme_reference_casse_differente_refuse(certificative, examens):
    _enregistrer(examens, certificative, "Sujet Alpha")
    with pytest.raises(IntegrityError, match="uq_sujet_reference"), transaction.atomic():
        Sujet.objects.create(
            evaluation=certificative,
            rang=2,
            reference="SUJET ALPHA",
            date_depot=timezone.localdate(),
        )


def test_a6_aucune_colonne_retenu_le_ou_retenu_par(certificative):
    noms = {champ.name for champ in Sujet._meta.get_fields()}
    assert "retenu_le" not in noms
    assert "retenu_par" not in noms


# --- B — Règles -------------------------------------------------------------


def test_b1_certificative_deux_sujets_un_retenu_journal_sans_reference(certificative, examens):
    sujet_a = _enregistrer(examens, certificative, "Pli numéro 12")
    _enregistrer(examens, certificative, "Pli numéro 13")
    ServiceSujet.retenir(examens, sujet_a)

    entree = EntreeJournal.objects.filter(type_action=TypeAction.SELECTION_SUJET).latest("cree_le")
    assert entree.auteur == examens
    assert entree.cree_le is not None
    assert "n° 1" in entree.detail
    assert "Pli numéro 12" not in entree.detail
    assert "Pli numéro 12" not in entree.identifiant_saisi


def test_b2_formative_second_sujet_et_retenue_refuses(formative, examens):
    _enregistrer(examens, formative, "Sujet unique")
    with pytest.raises(ErreurValidation, match="RG-50"):
        _enregistrer(examens, formative, "Second sujet")
    sujet = formative.sujets.get()
    with pytest.raises(ErreurValidation, match="RG-50"):
        ServiceSujet.retenir(examens, sujet, confirmation=True)


def test_b3_certificative_un_seul_sujet_confirmation_requise(certificative, examens):
    sujet = _enregistrer(examens, certificative, "Pli unique")
    with pytest.raises(ErreurValidation, match="RG-50"):
        ServiceSujet.retenir(examens, sujet, confirmation=False)
    assert not Sujet.objects.get(pk=sujet.pk).retenu

    ServiceSujet.retenir(examens, sujet, confirmation=True)
    entree = EntreeJournal.objects.filter(type_action=TypeAction.SELECTION_SUJET).latest("cree_le")
    assert "RG-50" in entree.detail


def test_b4_changement_retenu_motif_obligatoire(certificative, examens):
    sujet_a = _enregistrer(examens, certificative, "Pli 1")
    sujet_b = _enregistrer(examens, certificative, "Pli 2")
    ServiceSujet.retenir(examens, sujet_a)

    with pytest.raises(ErreurValidation, match="motif"):
        ServiceSujet.changer_retenu(examens, sujet_b, "")

    ServiceSujet.changer_retenu(examens, sujet_b, "Décision de la commission du 02/10.")
    entree = EntreeJournal.objects.filter(type_action=TypeAction.SELECTION_SUJET).latest("cree_le")
    assert "n° 1" in entree.detail and "n° 2" in entree.detail


def test_b5_selection_changement_suppression_refuses_le_jour_de_l_epreuve(
    certificative_echue, examens
):
    sujet_a = _enregistrer(examens, certificative_echue, "Pli 1")
    sujet_b = _enregistrer(examens, certificative_echue, "Pli 2")
    with pytest.raises(ErreurValidation, match="RG-51"):
        ServiceSujet.retenir(examens, sujet_a)
    sujet_a.retenu = True
    sujet_a.save()
    with pytest.raises(ErreurValidation, match="RG-51"):
        ServiceSujet.changer_retenu(examens, sujet_b, "Motif.")
    with pytest.raises(ErreurValidation, match="RG-51"):
        ServiceSujet.supprimer(examens, sujet_b)


def test_b6_date_depot_future_refusee(certificative, examens):
    with pytest.raises(ErreurValidation, match="future"):
        _enregistrer(
            examens, certificative, "Sujet A", timezone.localdate() + datetime.timedelta(days=1)
        )


def test_b7_suppression_retenu_refuse_non_retenu_admise(certificative, examens):
    sujet_a = _enregistrer(examens, certificative, "Pli 1")
    sujet_b = _enregistrer(examens, certificative, "Pli 2")
    ServiceSujet.retenir(examens, sujet_a)

    with pytest.raises(ErreurValidation, match="retenu"):
        ServiceSujet.supprimer(examens, sujet_a)

    ServiceSujet.supprimer(examens, sujet_b)
    assert not Sujet.objects.filter(pk=sujet_b.pk).exists()


def test_b8_formative_declaree_apres_coup_sujet_admis(controle):
    jour_passe = controle.jour_creneau.jour - datetime.timedelta(days=200)
    evaluation = ServiceEvaluation.creer(
        controle.examens,
        {
            "element_referentiel": controle.element_referentiel,
            "type": "formative",
            "session": None,
            "brigade": controle.brigade,
            "date": jour_passe,
            "creneau_type": None,
            "instructeur": None,
            "lieu": None,
            "motif_date_passee": "Contrôle inopiné non déclaré sur le moment.",
        },
    )
    sujet = _enregistrer(controle.examens, evaluation, "Sujet après coup")
    assert sujet.pk is not None


def test_b9_sujet_retenu_predicat(certificative, examens):
    assert ServiceSujet.sujet_retenu(certificative) is None
    sujet = _enregistrer(examens, certificative, "Pli 1")
    ServiceSujet.retenir(examens, sujet, confirmation=True)
    assert ServiceSujet.sujet_retenu(certificative) == sujet


def test_b10_correction_non_retenu_avant_epreuve_admise_apres_refusee(
    certificative, certificative_echue, examens
):
    sujet = _enregistrer(examens, certificative, "Pli brouillon")
    ServiceSujet.corriger(
        examens, sujet, {"reference": "Pli corrigé", "date_depot": timezone.localdate()}
    )
    assert Sujet.objects.get(pk=sujet.pk).reference == "Pli corrigé"

    sujet_echu = _enregistrer(examens, certificative_echue, "Pli échu")
    with pytest.raises(ErreurValidation, match="RG-51"):
        ServiceSujet.corriger(
            examens, sujet_echu, {"reference": "Trop tard", "date_depot": timezone.localdate()}
        )
