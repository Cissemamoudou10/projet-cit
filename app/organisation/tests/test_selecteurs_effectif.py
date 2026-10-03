"""Effectifs réels groupés (prompt 38, D-210) : une seule définition, égale à
`ServiceBrigade.effectif_reel` sur un jeu avec stagiaires radiés ; une requête
quel que soit le nombre de brigades. Données entièrement fictives.
"""

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from organisation.models import Stagiaire
from organisation.selectors import effectifs_reels
from organisation.services.affectation import ServiceAffectation
from organisation.services.brigade import ServiceBrigade
from organisation.services.stagiaire import ServiceStagiaire


def _stagiaire(session, matricule):
    return Stagiaire.objects.create(
        session=session,
        matricule=matricule,
        nom="Essai",
        prenom="Effectif",
        grade="Sgt",
        unite="Unité de test",
    )


def test_effectif_groupe_egal_au_service_avec_stagiaires_radies(redacteur, session, brigade):
    affectes = [_stagiaire(session, f"SEL-A{i}") for i in range(3)]
    for stagiaire in affectes:
        ServiceAffectation.affecter(redacteur, stagiaire, brigade)
    ServiceStagiaire.radier(redacteur, affectes[0], "Mutation", timezone.localdate())

    groupe = effectifs_reels([brigade.pk])

    assert groupe[brigade.pk] == ServiceBrigade.effectif_reel(brigade) == 2


def test_effectif_requete_unique_quel_que_soit_le_nombre_de_brigades(redacteur, session):
    un = [
        ServiceBrigade.creer(
            redacteur, session, {"designation": "SEL-1", "effectif_previsionnel": 20}
        ).pk
    ]
    dix = [
        ServiceBrigade.creer(
            redacteur, session, {"designation": f"SEL-D{i}", "effectif_previsionnel": 20}
        ).pk
        for i in range(10)
    ]

    with CaptureQueriesContext(connection) as capture_un:
        effectifs_reels(un)
    with CaptureQueriesContext(connection) as capture_dix:
        groupe = effectifs_reels(dix)

    assert len(capture_un) == len(capture_dix) == 1
    assert groupe == {pk: 0 for pk in dix}
