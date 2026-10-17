"""US-EVAL-06 — écran dédié des moyennes et du classement (M8) : cycle HTTP
réel et nombre de requêtes constant. Jeu d'essai minimal, propre à ce
fichier — le jeu calculé à la main pour le calcul lui-même est dans
`test_moyennes.py`. Données entièrement fictives.
"""

import datetime

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from evaluations.models import Evaluation, Note, TypeEvaluation
from evaluations.tests.conftest import creer_brigade
from organisation.models import Stagiaire
from organisation.services.affectation import ServiceAffectation
from organisation.tests.conftest import donnees_stagiaire


def _brigade_notee(redacteur, session, element_referentiel, designation, valeur):
    """Une brigade, un stagiaire, une évaluation certificative notée —
    assez pour que l'écran affiche une ligne réelle, sans reprendre le jeu
    calculé à la main de `test_moyennes.py`."""
    brigade = creer_brigade(redacteur, session, designation)
    stagiaire = Stagiaire.objects.create(
        **donnees_stagiaire(session=session, matricule=f"{designation}0001")
    )
    ServiceAffectation.affecter(redacteur, stagiaire, brigade)
    evaluation = Evaluation.objects.create(
        element_referentiel=element_referentiel,
        brigade=brigade,
        type=TypeEvaluation.CERTIFICATIVE,
        date=datetime.date(2026, 1, 19),
        note_maximale=20,
    )
    Note.objects.create(evaluation=evaluation, stagiaire=stagiaire, valeur=valeur)
    return brigade


def test_ecran_rend_les_moyennes_pour_la_cellule_examens(
    client, examens, redacteur, session, element_referentiel
):
    _brigade_notee(redacteur, session, element_referentiel, "MOYE1", 14)
    client.force_login(examens)

    reponse = client.get(reverse("evaluations:moyennes_session", args=[session.pk]))

    assert reponse.status_code == 200
    contenu = reponse.content.decode("utf-8")
    assert "14,00" in contenu or "14.00" in contenu


def test_ecran_refuse_a_la_pedagogique(client, redacteur, session):
    client.force_login(redacteur)

    reponse = client.get(reverse("evaluations:moyennes_session", args=[session.pk]))

    assert reponse.status_code == 403


def test_ecran_refuse_a_la_direction(client, direction_formation, session):
    client.force_login(direction_formation)

    reponse = client.get(reverse("evaluations:moyennes_session", args=[session.pk]))

    assert reponse.status_code == 403


def test_requetes_constantes_avec_deux_et_dix_brigades(
    client, examens, redacteur, session, element_referentiel
):
    _brigade_notee(redacteur, session, element_referentiel, "MOYQA", 10)
    _brigade_notee(redacteur, session, element_referentiel, "MOYQB", 12)
    url = reverse("evaluations:moyennes_session", args=[session.pk])
    client.force_login(examens)

    client.get(url)  # appel de chauffe (P-39) : cache de permissions
    with CaptureQueriesContext(connection) as deux:
        client.get(url)

    for i in range(8):
        _brigade_notee(redacteur, session, element_referentiel, f"MOYQ{i}", 10 + i)

    with CaptureQueriesContext(connection) as dix:
        client.get(url)

    assert len(deux.captured_queries) == len(dix.captured_queries)
