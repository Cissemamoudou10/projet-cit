"""US-SES-09 — Clôturer une session (prompt 47, Temps 4). Données
entièrement fictives.

Les tests qui exigent une évaluation/un procès-verbal vivent dans
`evaluations/tests/test_cloture_session.py` : `organisation` ne peut pas
importer `evaluations` (sens de dépendance interdit,
`tests/architecture/test_couches.py`), y compris dans ses propres tests.
"""

import pytest
from django.urls import reverse
from django.utils import timezone

from noyau.exceptions import ErreurValidation
from organisation.models import EtatSession
from organisation.services.affectation import ServiceAffectation
from organisation.services.cloture import ServiceClotureSession
from organisation.services.session import ServiceSession


def test_cloture_admise_sans_aucune_evaluation(redacteur, session):
    """C2 : aucune évaluation dans le périmètre, rien à verrouiller."""
    cloturee = ServiceClotureSession.cloturer(redacteur, session)

    assert cloturee.etat == EtatSession.CLOTUREE
    assert cloturee.date_cloture == timezone.localdate()


def test_deja_cloturee_refusee(redacteur, session):
    ServiceClotureSession.cloturer(redacteur, session)

    with pytest.raises(ErreurValidation, match="déjà clôturée"):
        ServiceClotureSession.cloturer(redacteur, session)


# --- C3 — disparaît des trois sélections actives ----------------------------


def test_absente_des_sessions_disponibles_pour_selection(redacteur, session):
    ServiceClotureSession.cloturer(redacteur, session)

    assert session.pk not in ServiceSession.disponibles_pour_selection().values_list(
        "pk", flat=True
    )


def test_affectation_refusee_sur_brigade_d_une_session_cloturee(
    redacteur, session, brigade, stagiaire
):
    ServiceClotureSession.cloturer(redacteur, session)

    with pytest.raises(ErreurValidation, match="clôturée"):
        ServiceAffectation.affecter(redacteur, stagiaire, brigade)


# --- Données toujours consultables ------------------------------------------


def test_brigade_et_stagiaire_restent_consultables_apres_cloture(redacteur, session, brigade):
    ServiceClotureSession.cloturer(redacteur, session)

    relue = ServiceSession.obtenir(session.pk)
    assert relue.etat == EtatSession.CLOTUREE
    assert brigade in relue.brigades.all()


# --- HTTP --------------------------------------------------------------


def test_http_cloture_ecrit_reellement(client, redacteur, session):
    client.force_login(redacteur)

    reponse = client.post(reverse("organisation:cloturer_session", args=[session.pk]), follow=True)

    assert reponse.status_code == 200
    session.refresh_from_db()
    assert session.etat == EtatSession.CLOTUREE


def test_http_cloture_refusee_a_la_cellule_examens(client, lecteur, session):
    client.force_login(lecteur)

    reponse = client.post(reverse("organisation:cloturer_session", args=[session.pk]))

    assert reponse.status_code == 403
    session.refresh_from_db()
    assert session.etat == EtatSession.OUVERTE
