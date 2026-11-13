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


def test_recherche_filtre_et_tri_restreignent_les_lignes_affichees(
    client, examens, redacteur, session, element_referentiel
):
    """US-IHM-03, critère 1 (prompt 64) : même composant que les autres
    listes — recherche, filtre (brigade) et tri sur la liste des stagiaires."""
    brigade_a = _brigade_notee(redacteur, session, element_referentiel, "MOYFA", 10)
    _brigade_notee(redacteur, session, element_referentiel, "MOYFB", 16)
    client.force_login(examens)
    url = reverse("evaluations:moyennes_session", args=[session.pk])

    reponse = client.get(url, {"recherche": "MOYFA0001"})
    contenu = reponse.content.decode("utf-8")
    assert "MOYFA0001" in contenu
    assert "MOYFB0001" not in contenu

    reponse = client.get(url, {"brigade": str(brigade_a.pk)})
    contenu = reponse.content.decode("utf-8")
    assert "MOYFA0001" in contenu
    assert "MOYFB0001" not in contenu

    reponse_croissant = client.get(url, {"tri": "moyenne"})
    contenu_croissant = reponse_croissant.content.decode("utf-8")
    assert contenu_croissant.index("MOYFA0001") < contenu_croissant.index("MOYFB0001")

    reponse_decroissant = client.get(url, {"tri": "-moyenne"})
    contenu_decroissant = reponse_decroissant.content.decode("utf-8")
    assert contenu_decroissant.index("MOYFB0001") < contenu_decroissant.index("MOYFA0001")


def test_pagination_limite_le_nombre_de_lignes_par_page(
    client, examens, redacteur, session, element_referentiel
):
    """US-IHM-03, critère 1 : pagination — `settings.TAILLE_PAGE_DEFAUT`
    (20) lignes sur la première page, le reste sur la seconde."""
    for i in range(23):
        _brigade_notee(redacteur, session, element_referentiel, f"MOYP{i:02d}", 10)
    client.force_login(examens)
    url = reverse("evaluations:moyennes_session", args=[session.pk])

    premiere_page = client.get(url)
    deuxieme_page = client.get(url, {"page": 2})

    assert len(list(premiere_page.context["page"])) == 20
    assert len(list(deuxieme_page.context["page"])) == 3
    assert premiere_page.context["page"].paginator.count == 23


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
