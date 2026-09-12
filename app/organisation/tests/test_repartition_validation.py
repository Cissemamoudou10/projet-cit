"""US-SES-06 — validation transactionnelle de la répartition (Prompt 25,
§ 12, Groupe D). Données entièrement fictives.
"""

import datetime
from unittest.mock import patch

import pytest
from django.db import IntegrityError

from administration.models import EntreeJournal
from noyau.exceptions import ErreurValidation
from organisation.models import AffectationBrigade
from organisation.repartition.proposition import proposer
from organisation.repartition.validation import valider
from organisation.services.brigade import ServiceBrigade
from organisation.services.stagiaire import ServiceStagiaire
from organisation.tests.conftest import donnees_brigade, donnees_stagiaire


def _creer_stagiaires(redacteur, session, nombre):
    return [
        ServiceStagiaire.creer(
            redacteur, session, donnees_stagiaire(matricule=f"M{i:03d}", nom=f"Nom{i:03d}")
        )
        for i in range(nombre)
    ]


def test_d1_validation_nominale_toutes_les_affectations_enregistrees_journalisees(
    redacteur, session
):
    _creer_stagiaires(redacteur, session, 3)
    ServiceBrigade.creer(redacteur, session, donnees_brigade(effectif_previsionnel=3))
    proposition = proposer(session)

    rapport = valider(redacteur, session, proposition)

    assert len(rapport.enregistrees) == 3
    assert not rapport.refusees
    assert AffectationBrigade.objects.count() == 3
    assert EntreeJournal.objects.filter(objet_type="repartition").exists()


def test_d2_tout_ou_rien_echec_au_milieu_aucune_affectation_ecrite(redacteur, session):
    _creer_stagiaires(redacteur, session, 3)
    ServiceBrigade.creer(redacteur, session, donnees_brigade(effectif_previsionnel=3))
    proposition = proposer(session)
    appels = {"n": 0}
    original_save = AffectationBrigade.save

    def save_qui_echoue_a_la_deuxieme(self, *args, **kwargs):
        appels["n"] += 1
        if appels["n"] == 2:
            raise IntegrityError("échec simulé au milieu du lot")
        return original_save(self, *args, **kwargs)

    with (
        patch.object(AffectationBrigade, "save", save_qui_echoue_a_la_deuxieme),
        pytest.raises(ErreurValidation),
    ):
        valider(redacteur, session, proposition)

    assert AffectationBrigade.objects.count() == 0


def test_d3_revalidation_stagiaire_radie_entre_temps_ligne_refusee_jamais_enregistree(
    redacteur, session
):
    stagiaires = _creer_stagiaires(redacteur, session, 3)
    ServiceBrigade.creer(redacteur, session, donnees_brigade(effectif_previsionnel=3))
    proposition = proposer(session)
    ServiceStagiaire.radier(redacteur, stagiaires[0], "Fin anticipée", datetime.date.today())

    rapport = valider(redacteur, session, proposition)

    assert len(rapport.enregistrees) == 2
    assert len(rapport.refusees) == 1
    assert rapport.refusees[0].stagiaire_id == stagiaires[0].pk
    assert not AffectationBrigade.objects.filter(stagiaire=stagiaires[0]).exists()


def test_d4_bis_revalidation_stagiaire_affecte_ailleurs_entre_temps_ligne_refusee(
    redacteur, session
):
    """Volet organisation du principe de revalidation (§ 5) : entre la
    proposition et la validation, un autre chemin affecte déjà le stagiaire
    à une brigade — RG-20 la refuse à la validation, jamais une erreur
    technique brute. D4 au sens strict du prompt (capacité RÉELLE d'une
    salle réduite entre-temps) est dans
    `app/ressources/tests/test_affectation_capacite.py` — `organisation` ne
    peut pas construire de `SalleAttitree` (D-85)."""
    stagiaires = _creer_stagiaires(redacteur, session, 2)
    brigade = ServiceBrigade.creer(redacteur, session, donnees_brigade(effectif_previsionnel=2))
    proposition = proposer(session)
    AffectationBrigade.objects.create(
        stagiaire=stagiaires[0], brigade=brigade, date_effet=datetime.date.today()
    )

    rapport = valider(redacteur, session, proposition)

    refus = [r for r in rapport.refusees if r.stagiaire_id == stagiaires[0].pk]
    assert refus
    assert "déjà affecté" in refus[0].motif.lower()
