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
from evaluations.tests.conftest import affecter_stagiaires, creer_brigade


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


def _noter_dans_brigade(dossier, brigade, prefixe, valeur):
    stagiaire = affecter_stagiaires(dossier.redacteur, brigade, 1, prefixe=prefixe)[0]
    ServiceNote.confirmer(
        dossier.examens,
        dossier.certificative,
        {str(stagiaire.pk): {"valeur": str(valeur), "absent": False}},
    )
    return stagiaire


def test_recherche_filtre_et_tri_restreignent_les_lignes_de_l_apercu(client, dossier_pv):
    """US-IHM-03, critère 1 (prompt 64) : même composant que les autres
    listes — recherche, filtre (brigade) et tri sur la liste des
    stagiaires de l'aperçu du procès-verbal."""
    autre_brigade = creer_brigade(dossier_pv.redacteur, dossier_pv.session, "PVF2")
    stagiaire_bas = _noter_dans_brigade(dossier_pv, dossier_pv.brigade, "PVFA", 8)
    stagiaire_haut = _noter_dans_brigade(dossier_pv, autre_brigade, "PVFB", 18)
    client.force_login(dossier_pv.examens)
    url = reverse("evaluations:apercu_proces_verbal", args=[dossier_pv.session.pk])
    base = {"type_pv": "fin_de_formation", "evaluation_pk": "", "numero": ""}

    reponse = client.get(url, {**base, "recherche": str(stagiaire_bas)})
    contenu = reponse.content.decode("utf-8")
    assert str(stagiaire_bas) in contenu
    assert str(stagiaire_haut) not in contenu

    reponse = client.get(url, {**base, "brigade": str(autre_brigade)})
    contenu = reponse.content.decode("utf-8")
    assert str(stagiaire_haut) in contenu
    assert str(stagiaire_bas) not in contenu

    # Tri par défaut (rang_session croissant) : la meilleure moyenne (rang 1) d'abord.
    reponse_croissant = client.get(url, {**base, "tri": "rang_session"})
    contenu_croissant = reponse_croissant.content.decode("utf-8")
    assert contenu_croissant.index(str(stagiaire_haut)) < contenu_croissant.index(str(stagiaire_bas))

    reponse_decroissant = client.get(url, {**base, "tri": "-rang_session"})
    contenu_decroissant = reponse_decroissant.content.decode("utf-8")
    assert contenu_decroissant.index(str(stagiaire_bas)) < contenu_decroissant.index(str(stagiaire_haut))


def test_apercu_http_affiche_les_decisions(client, dossier_pv):
    """1.2 (prompt 47) ; GET depuis le prompt 64 (US-IHM-03) : l'aperçu ne
    fait qu'afficher, jamais une écriture — voir evaluations.views_
    proces_verbal._evaluation_depuis_requete."""
    _noter(dossier_pv, "PVH1")
    client.force_login(dossier_pv.examens)

    reponse = client.get(
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

    reponse = client.get(
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
