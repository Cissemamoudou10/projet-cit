"""US-IHM-03, prompt 64 — critère « saisie des notes » : recherche et filtre
SANS PAGINATION ; preuve par un vrai navigateur qu'aucune note saisie n'est
perdue quand on filtre, puisque le filtre ne fait que masquer des lignes en
JavaScript (voir `evaluations/templates/evaluations/notes_saisie.html`),
sans jamais retirer un `<input>` du formulaire. Un test par cycle HTTP seul
ne le prouverait pas : il ne verrait que l'état final en base, pas le fait
que le navigateur a bien soumis les champs masqués. Même fixture
`navigateur_chromium` que `noyau.tests.test_navigation_navigateur`,
dupliquée ici pour ne pas coupler `evaluations` à ses fixtures.
"""

import os

import pytest
from django.urls import reverse

from evaluations.models import Note
from evaluations.tests.conftest import affecter_stagiaires

pytestmark = pytest.mark.navigateur

MOT_DE_PASSE = "x"


@pytest.fixture
def navigateur_chromium():
    playwright_sync = pytest.importorskip(
        "playwright.sync_api", reason="playwright non installé — voir requirements-dev.txt"
    )
    valeur_precedente = os.environ.get("DJANGO_ALLOW_ASYNC_UNSAFE")
    os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "1"
    try:
        with playwright_sync.sync_playwright() as p:
            try:
                navigateur = p.chromium.launch()
            except Exception as erreur:
                pytest.skip(
                    f"Chromium indisponible ({erreur}) — lancer `playwright install chromium`"
                )
            yield navigateur
            navigateur.close()
    finally:
        if valeur_precedente is None:
            os.environ.pop("DJANGO_ALLOW_ASYNC_UNSAFE", None)
        else:
            os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = valeur_precedente


def _connecter(page, url_base, identifiant):
    page.goto(f"{url_base}/connexion/")
    page.fill('input[name="identifiant"]', identifiant)
    page.fill('input[name="mot_de_passe"]', MOT_DE_PASSE)
    page.click('button[type="submit"]')
    page.wait_for_load_state("networkidle")


def test_le_filtre_ne_fait_perdre_aucune_note_saisie(navigateur_chromium, live_server, dossier_pv):
    stagiaires = affecter_stagiaires(dossier_pv.redacteur, dossier_pv.brigade, 3, prefixe="NAV")
    page = navigateur_chromium.new_page()
    _connecter(page, live_server.url, dossier_pv.examens.username)

    url_notes = reverse("evaluations:notes", args=[dossier_pv.certificative.pk])
    page.goto(f"{live_server.url}{url_notes}")
    page.wait_for_load_state("networkidle")

    for stagiaire in stagiaires:
        page.fill(f'input[name="valeur_{stagiaire.pk}"]', "15")

    # Un filtre qui ne garde visible qu'un seul stagiaire sur les trois.
    page.fill("#filtre-recherche-notes", str(stagiaires[0]))
    lignes_visibles = page.locator("#corps-notes tr:not([hidden])")
    assert lignes_visibles.count() == 1

    # Les deux lignes masquées restent dans le DOM, avec leur valeur.
    for stagiaire in stagiaires[1:]:
        assert page.input_value(f'input[name="valeur_{stagiaire.pk}"]') == "15"

    # `get_by_role` : `button[type="submit"]` seul est ambigu, le menu
    # déroulant du compte (US-IHM-02) en porte un autre (« Déconnexion »).
    page.get_by_role("button", name="Vérifier la saisie").click()
    page.wait_for_load_state("networkidle")
    page.get_by_role("button", name="Confirmer").click()
    page.wait_for_load_state("networkidle")

    for stagiaire in stagiaires:
        note = Note.objects.get(evaluation=dossier_pv.certificative, stagiaire=stagiaire)
        assert note.valeur == 15
