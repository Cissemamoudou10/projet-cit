"""US-SES-06 — contraintes en base d'`AffectationBrigade` (Prompt 25, § 12,
Groupe C). Insertion directe, court-circuitant le service — RG-20 et
`ck_affectation_dates` doivent tenir même si un chemin d'écriture futur
oublie le contrôle applicatif. Données entièrement fictives.
"""

import datetime

import pytest
from django.db import IntegrityError, transaction

from organisation.models import AffectationBrigade
from organisation.services.brigade import ServiceBrigade
from organisation.tests.conftest import donnees_brigade


@pytest.fixture
def brigade_2(redacteur, session):
    return ServiceBrigade.creer(redacteur, session, donnees_brigade(designation="EXP2"))


def test_c1_deux_affectations_ouvertes_meme_stagiaire_rejetees(db, stagiaire, brigade, brigade_2):
    AffectationBrigade.objects.create(
        stagiaire=stagiaire, brigade=brigade, date_effet=datetime.date.today()
    )

    with (
        pytest.raises(IntegrityError, match="uq_affectation_ouverte"),
        transaction.atomic(),
    ):
        AffectationBrigade.objects.create(
            stagiaire=stagiaire, brigade=brigade_2, date_effet=datetime.date.today()
        )


def test_c2_deux_lignes_historiques_dont_les_periodes_se_recouvrent_non_rejetees_en_base(
    db, stagiaire, brigade, brigade_2
):
    """Aucune contrainte d'exclusion en base sur l'historique (§ 3, Prompt 25) :
    l'index unique partiel ne porte que sur l'affectation OUVERTE. Le
    chevauchement entre deux lignes FERMÉES reste un contrôle applicatif, non
    exercé par une insertion directe — mention explicite de ce que la base ne
    garantit pas, comme le § 10 l'autorise."""
    AffectationBrigade.objects.create(
        stagiaire=stagiaire,
        brigade=brigade,
        date_effet=datetime.date(2026, 1, 1),
        date_fin=datetime.date(2026, 6, 1),
    )

    AffectationBrigade.objects.create(
        stagiaire=stagiaire,
        brigade=brigade_2,
        date_effet=datetime.date(2026, 3, 1),
        date_fin=datetime.date(2026, 9, 1),
    )

    assert stagiaire.affectations.count() == 2


def test_c3_ck_affectation_dates_date_fin_anterieure_ou_egale_refusee(db, stagiaire, brigade):
    with (
        pytest.raises(IntegrityError, match="ck_affectation_dates"),
        transaction.atomic(),
    ):
        AffectationBrigade.objects.create(
            stagiaire=stagiaire,
            brigade=brigade,
            date_effet=datetime.date(2026, 6, 1),
            date_fin=datetime.date(2026, 6, 1),
        )


def test_c4_une_affectation_fermee_et_une_ouverte_meme_stagiaire_periodes_disjointes_acceptees(
    db, stagiaire, brigade, brigade_2
):
    AffectationBrigade.objects.create(
        stagiaire=stagiaire,
        brigade=brigade,
        date_effet=datetime.date(2026, 1, 1),
        date_fin=datetime.date(2026, 6, 1),
    )

    ouverte = AffectationBrigade.objects.create(
        stagiaire=stagiaire, brigade=brigade_2, date_effet=datetime.date(2026, 6, 1)
    )

    assert ouverte.date_fin is None
    assert stagiaire.affectations.count() == 2
