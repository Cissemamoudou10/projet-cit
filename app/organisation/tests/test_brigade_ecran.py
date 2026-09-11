"""US-SES-02 — cycle HTTP réel (`reverse()` + `client`), Groupe C (Prompt 21,
§ 10). Le refus d'habilitation en écriture (C2) et le test de garde
mécanique (C4) sont couverts une fois pour toutes par
tests/architecture/test_ecrans_ecriture.py.
"""

import datetime

import pytest
from django.urls import reverse

from organisation.models import Brigade
from organisation.services.brigade import ServiceBrigade
from organisation.services.session import ServiceSession
from organisation.tests.conftest import donnees_brigade, donnees_session


@pytest.fixture
def brigade(redacteur, session):
    return ServiceBrigade.creer(redacteur, session, donnees_brigade())


def test_c1_creer_par_l_ecran_cree_reellement_la_brigade(client, redacteur, session):
    client.force_login(redacteur)

    assert client.get(reverse("organisation:brigades_session", args=[session.pk])).status_code == 200

    reponse = client.post(
        reverse("organisation:creer_brigade", args=[session.pk]),
        {"designation": "EXP1", "effectif_previsionnel": 20},
    )

    assert reponse.status_code == 302
    assert Brigade.objects.filter(session=session, designation="EXP1").exists()


def test_c1_modifier_par_l_ecran_modifie_reellement_la_brigade(client, redacteur, session, brigade):
    client.force_login(redacteur)

    reponse = client.post(
        reverse("organisation:modifier_brigade", args=[session.pk, brigade.pk]),
        {"designation": "EXP1 modifiée", "effectif_previsionnel": 22},
    )

    assert reponse.status_code == 302
    brigade.refresh_from_db()
    assert brigade.designation == "EXP1 modifiée"
    assert brigade.effectif_previsionnel == 22


def test_c1_supprimer_par_l_ecran_supprime_reellement_la_brigade(client, redacteur, session):
    """Deux brigades : la suppression de la dernière est un refus distinct
    (C8), testé séparément."""
    premiere = ServiceBrigade.creer(redacteur, session, donnees_brigade(designation="EXP1"))
    ServiceBrigade.creer(redacteur, session, donnees_brigade(designation="EXP2"))
    client.force_login(redacteur)

    reponse = client.post(
        reverse("organisation:supprimer_brigade", args=[session.pk, premiere.pk])
    )

    assert reponse.status_code == 302
    assert not Brigade.objects.filter(pk=premiere.pk).exists()


@pytest.mark.parametrize(
    "nom_utilisateur", ["redacteur", "lecteur", "planificateur", "direction_formation"]
)
def test_c3_lecture_accordee_aux_quatre_profils_habilites(
    client, request, session, nom_utilisateur
):
    client.force_login(request.getfixturevalue(nom_utilisateur))

    reponse = client.get(reverse("organisation:brigades_session", args=[session.pk]))

    assert reponse.status_code == 200


def test_c3_lecture_refusee_a_l_administrateur(client, administrateur, session):
    client.force_login(administrateur)

    reponse = client.get(reverse("organisation:brigades_session", args=[session.pk]))

    assert reponse.status_code == 403


def test_c5_lien_atteignable_depuis_la_fiche_de_session(client, redacteur, session):
    client.force_login(redacteur)

    reponse = client.get(reverse("organisation:detail_session", args=[session.pk]))

    assert reverse("organisation:brigades_session", args=[session.pk]) in reponse.content.decode()


def test_c6_indicateur_d_ecart_visible_avec_les_deux_nombres_et_le_mot(
    client, redacteur, session
):
    ServiceBrigade.creer(
        redacteur, session, donnees_brigade(effectif_previsionnel=session.effectif_attendu + 7)
    )
    client.force_login(redacteur)

    reponse = client.get(reverse("organisation:brigades_session", args=[session.pk]))
    contenu = reponse.content.decode()

    assert "Écart d'effectif" in contenu
    assert str(session.effectif_attendu) in contenu
    assert str(session.effectif_attendu + 7) in contenu


def test_c7_signalement_session_sans_brigade_sur_l_ecran_des_brigades(client, redacteur, session):
    client.force_login(redacteur)

    reponse = client.get(reverse("organisation:brigades_session", args=[session.pk]))

    assert "Aucune brigade constituée" in reponse.content.decode()


def test_c7_signalement_session_sans_brigade_sur_la_liste_des_sessions(client, redacteur, session):
    client.force_login(redacteur)

    reponse = client.get(reverse("organisation:liste_sessions"))

    assert "AUCUNE BRIGADE" in reponse.content.decode()


def test_c8_refus_de_suppression_de_la_derniere_brigade_par_le_vrai_cycle_http(
    client, redacteur, session, brigade
):
    client.force_login(redacteur)

    reponse = client.post(
        reverse("organisation:supprimer_brigade", args=[session.pk, brigade.pk]), follow=True
    )

    assert reponse.status_code == 200
    assert Brigade.objects.filter(pk=brigade.pk).exists()
    assert brigade.designation in reponse.content.decode()
