"""US-EVAL-12 (prompt 64) — écran de détail d'une moyenne : cycle HTTP réel.
Fixtures partagées avec test_moyennes.py/test_moyennes_ecran.py dans
`evaluations/tests/conftest.py`. Données entièrement fictives.
"""

import dataclasses

import pytest
from django.urls import reverse

from administration.models import EntreeJournal, TypeAction
from evaluations.services.note import ServiceNote
from evaluations.tests.conftest import affecter_stagiaires


@dataclasses.dataclass(frozen=True)
class ScenarioDetail:
    """Un module noté dans les deux types pour une même brigade —
    `.claude/rules/python.md`, § 5 paramètres max : un seul objet plutôt que
    quatre fixtures injectées séparément dans chaque test."""

    redacteur: object
    controle: object
    formative: object
    certificative: object


@pytest.fixture
def scenario_detail(redacteur, controle, formative, certificative):
    return ScenarioDetail(
        redacteur=redacteur, controle=controle, formative=formative, certificative=certificative
    )


def _noter_les_deux_types(scenario):
    stagiaires = affecter_stagiaires(
        scenario.redacteur, scenario.controle.brigade, 1, prefixe="DETM"
    )
    stagiaire = stagiaires[0]
    examens = scenario.controle.examens
    ServiceNote.confirmer(
        examens, scenario.formative, {str(stagiaire.pk): {"valeur": "12", "absent": False}}
    )
    ServiceNote.confirmer(
        examens, scenario.certificative, {str(stagiaire.pk): {"valeur": "16", "absent": False}}
    )
    return stagiaire


def _url_detail(scenario, stagiaire):
    return reverse(
        "evaluations:detail_moyenne", args=[scenario.controle.brigade.session.pk, stagiaire.pk]
    )


def test_detail_affiche_les_notes_par_type_le_poids_la_note_et_le_coefficient(
    client, scenario_detail
):
    stagiaire = _noter_les_deux_types(scenario_detail)
    client.force_login(scenario_detail.controle.examens)

    reponse = client.get(_url_detail(scenario_detail, stagiaire))

    assert reponse.status_code == 200
    contenu = reponse.content.decode("utf-8")
    assert "12,00/20" in contenu or "12.00/20" in contenu  # note formative
    assert "16,00/20" in contenu or "16.00/20" in contenu  # note certificative
    assert "poids 1" in contenu  # poids formatif/certificatif (1,00 ou 1.00)
    assert "Coefficient 1" in contenu
    # Moyenne du module (poids égaux, (12+16)/2 = 14) visible quelque part.
    assert "14,00/20" in contenu or "14.00/20" in contenu


def test_moyenne_generale_et_rang_sont_affiches(client, scenario_detail):
    stagiaire = _noter_les_deux_types(scenario_detail)
    client.force_login(scenario_detail.controle.examens)

    reponse = client.get(_url_detail(scenario_detail, stagiaire))

    assert reponse.status_code == 200
    contexte_detail = reponse.context["detail"]
    assert contexte_detail.moyenne is not None
    assert contexte_detail.rang_session == 1
    assert contexte_detail.rang_brigade == 1
    contenu = reponse.content.decode("utf-8")
    assert "14,00" in contenu or "14.00" in contenu


def test_refuse_a_la_pedagogique(client, scenario_detail):
    stagiaire = affecter_stagiaires(
        scenario_detail.redacteur, scenario_detail.controle.brigade, 1, prefixe="DETR"
    )[0]
    client.force_login(scenario_detail.redacteur)

    reponse = client.get(_url_detail(scenario_detail, stagiaire))

    assert reponse.status_code == 403


def test_chaque_consultation_est_journalisee(client, scenario_detail):
    stagiaire = _noter_les_deux_types(scenario_detail)
    client.force_login(scenario_detail.controle.examens)
    url = _url_detail(scenario_detail, stagiaire)
    avant = EntreeJournal.objects.filter(type_action=TypeAction.CONSULTATION_MOYENNES).count()

    client.get(url)
    client.get(url)

    apres = EntreeJournal.objects.filter(type_action=TypeAction.CONSULTATION_MOYENNES).count()
    assert apres - avant == 2
