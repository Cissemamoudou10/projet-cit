"""US-EVAL-07 — écran dédié des procès-verbaux : cycle HTTP réel (V9/V10).
Fixtures partagées avec test_proces_verbal.py dans
`evaluations/tests/conftest.py`. Données entièrement fictives.
"""

import pytest
from django.urls import reverse

from administration.models import EntreeJournal, TypeAction
from evaluations.models import TypeProcesVerbal
from evaluations.services.note import ServiceNote
from evaluations.services.proces_verbal import ServiceProcesVerbal
from evaluations.tests.conftest import affecter_stagiaires


@pytest.fixture(autouse=True)
def _pdf_simule(monkeypatch):
    monkeypatch.setattr(
        "evaluations.services.proces_verbal.ServiceDocument.produire", lambda *a, **k: b"%PDF-essai"
    )


def _noter(dossier, prefixe):
    stagiaire = affecter_stagiaires(dossier.redacteur, dossier.brigade, 1, prefixe=prefixe)[0]
    ServiceNote.confirmer(
        dossier.examens,
        dossier.certificative,
        {str(stagiaire.pk): {"valeur": "15", "absent": False}},
    )
    return stagiaire


def test_apercu_http_affiche_les_decisions(client, dossier_pv):
    _noter(dossier_pv, "PVH1")
    client.force_login(dossier_pv.examens)

    reponse = client.post(
        reverse("evaluations:apercu_proces_verbal", args=[dossier_pv.session.pk]),
        {"type_pv": "fin_de_formation", "evaluation_pk": "", "numero": ""},
    )

    assert reponse.status_code == 200
    assert "Admis" in reponse.content.decode("utf-8")


def test_apercu_http_d_une_evaluation_n_affiche_aucune_decision(client, dossier_pv):
    """1.2 (prompt 47) : CU-P6-07 A1 — ni « Admis » ni « Ajourné » à
    l'aperçu du procès-verbal d'une seule évaluation."""
    _noter(dossier_pv, "PVH5")
    client.force_login(dossier_pv.examens)

    reponse = client.post(
        reverse("evaluations:apercu_proces_verbal", args=[dossier_pv.session.pk]),
        {
            "type_pv": "evaluation",
            "evaluation_pk": dossier_pv.certificative.pk,
            "numero": "",
        },
    )

    contenu = reponse.content.decode("utf-8")
    assert reponse.status_code == 200
    assert "Admis" not in contenu
    assert "Ajourné" not in contenu


def test_generation_http_ecrit_reellement(client, dossier_pv):
    _noter(dossier_pv, "PVH2")
    client.force_login(dossier_pv.examens)

    reponse = client.post(
        reverse("evaluations:generer_proces_verbal", args=[dossier_pv.session.pk]),
        {"type_pv": "fin_de_formation", "evaluation_pk": "", "numero": ""},
        follow=True,
    )

    assert reponse.status_code == 200
    assert ServiceProcesVerbal.lister(dossier_pv.examens, dossier_pv.session).exists()


def test_telechargement_par_la_direction(client, dossier_pv, direction_formation):
    _noter(dossier_pv, "PVH3")
    pv = ServiceProcesVerbal.generer(
        dossier_pv.examens, dossier_pv.session, TypeProcesVerbal.FIN_DE_FORMATION
    )
    client.force_login(direction_formation)

    reponse = client.get(reverse("evaluations:telecharger_proces_verbal", args=[pv.pk]))

    assert reponse.status_code == 200
    assert reponse["Content-Type"] == "application/pdf"
    assert reponse.content[:4] == b"%PDF"


def test_generation_refusee_a_la_planification(client, planificateur, session):
    client.force_login(planificateur)

    reponse = client.post(
        reverse("evaluations:generer_proces_verbal", args=[session.pk]),
        {"type_pv": "fin_de_formation", "evaluation_pk": "", "numero": ""},
    )

    assert reponse.status_code == 403


def test_generation_refusee_a_la_pedagogique(client, redacteur, session):
    client.force_login(redacteur)

    reponse = client.post(
        reverse("evaluations:generer_proces_verbal", args=[session.pk]),
        {"type_pv": "fin_de_formation", "evaluation_pk": "", "numero": ""},
    )

    assert reponse.status_code == 403


def test_une_entree_de_journal_par_telechargement(client, dossier_pv, direction_formation):
    _noter(dossier_pv, "PVH4")
    pv = ServiceProcesVerbal.generer(
        dossier_pv.examens, dossier_pv.session, TypeProcesVerbal.FIN_DE_FORMATION
    )
    client.force_login(direction_formation)
    url = reverse("evaluations:telecharger_proces_verbal", args=[pv.pk])
    avant = EntreeJournal.objects.filter(
        type_action=TypeAction.TELECHARGEMENT_PROCES_VERBAL
    ).count()

    client.get(url)
    client.get(url)

    apres = EntreeJournal.objects.filter(
        type_action=TypeAction.TELECHARGEMENT_PROCES_VERBAL
    ).count()
    assert apres - avant == 2
