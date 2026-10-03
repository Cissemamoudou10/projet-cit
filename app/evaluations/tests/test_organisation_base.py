"""US-EVAL-04, bloc A — contraintes en base de l'organisation d'épreuve
(prompt 38, § 3 et § 5 A). Données entièrement fictives.
"""

import datetime

import pytest
from django.db import IntegrityError, transaction

from evaluations.models import OrganisationEpreuve, Surveillance
from evaluations.tests.conftest import creer_brigade

HEURE_8 = datetime.time(8, 0)
HEURE_10 = datetime.time(10, 0)


def _avec_creneau(evaluation, debut, fin):
    evaluation.heure_debut = debut
    evaluation.heure_fin = fin
    evaluation.save()
    return evaluation


def _erreur(nom_contrainte):
    return pytest.raises(IntegrityError, match=nom_contrainte)


def test_a1_une_heure_sans_l_autre_refusee(certificative):
    with _erreur("ck_evaluation_creneau_complet"), transaction.atomic():
        certificative.heure_debut = HEURE_8
        certificative.save()


def test_a2_fin_non_posterieure_au_debut_refusee(certificative):
    with _erreur("ck_evaluation_creneau_ordonne"), transaction.atomic():
        _avec_creneau(certificative, HEURE_10, HEURE_8)


def test_a3_heures_sur_une_formative_refusees(controle):
    from evaluations.services.evaluation import ServiceEvaluation

    formative = ServiceEvaluation.creer(
        controle.examens,
        {
            "element_referentiel": controle.element_referentiel,
            "type": "formative",
            "session": None,
            "brigade": controle.brigade,
            "date": controle.jour_creneau.jour,
            "creneau_type": controle.jour_creneau.creneau,
            "instructeur": controle.instructeur,
            "lieu": None,
            "motif_date_passee": "",
        },
    )
    with _erreur("ck_evaluation_creneau_certificative"), transaction.atomic():
        _avec_creneau(formative, HEURE_8, HEURE_10)


def test_a4_effectif_nul_refuse(certificative, redacteur, session, lieu):
    brigade = creer_brigade(redacteur, session, "ORG-A4")
    with _erreur("ck_organisation_effectif_positif"), transaction.atomic():
        OrganisationEpreuve.objects.create(
            evaluation=certificative, brigade=brigade, lieu=lieu, effectif_attendu=0
        )


def test_a5_meme_lieu_pour_deux_brigades_de_la_meme_epreuve_refuse(
    certificative, redacteur, session, lieu
):
    premiere = creer_brigade(redacteur, session, "ORG-A5a")
    seconde = creer_brigade(redacteur, session, "ORG-A5b")
    OrganisationEpreuve.objects.create(
        evaluation=certificative, brigade=premiere, lieu=lieu, effectif_attendu=5
    )
    with _erreur("uq_organisation_lieu_par_epreuve"), transaction.atomic():
        OrganisationEpreuve.objects.create(
            evaluation=certificative, brigade=seconde, lieu=lieu, effectif_attendu=5
        )


@pytest.fixture
def organisation(certificative, redacteur, session):
    brigade = creer_brigade(redacteur, session, "ORG-SURV")
    return OrganisationEpreuve.objects.create(
        evaluation=certificative, brigade=brigade, lieu=None, effectif_attendu=5
    )


def test_a6_surveillance_sans_nature_refusee(organisation):
    with _erreur("ck_surveillance_une_nature"), transaction.atomic():
        Surveillance.objects.create(organisation=organisation)


def test_a6_surveillance_avec_les_deux_natures_refusee(organisation, instructeur):
    with _erreur("ck_surveillance_une_nature"), transaction.atomic():
        Surveillance.objects.create(
            organisation=organisation, instructeur=instructeur, nom_libre="M. Dupont"
        )


def test_a6_nom_libre_fait_de_blancs_refuse(organisation):
    with _erreur("ck_surveillance_une_nature"), transaction.atomic():
        Surveillance.objects.create(organisation=organisation, nom_libre="   ")


def test_a7_meme_instructeur_deux_fois_refuse(organisation, instructeur):
    Surveillance.objects.create(organisation=organisation, instructeur=instructeur)
    with _erreur("uq_surveillance_instructeur"), transaction.atomic():
        Surveillance.objects.create(organisation=organisation, instructeur=instructeur)


def test_a7_meme_nom_libre_a_la_casse_pres_refuse(organisation):
    Surveillance.objects.create(organisation=organisation, nom_libre="Dupont")
    with _erreur("uq_surveillance_nom_libre"), transaction.atomic():
        Surveillance.objects.create(organisation=organisation, nom_libre="DUPONT")
