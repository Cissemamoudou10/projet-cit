"""L8, prompt 61 (B-A1, RECETTE-02) — vrai navigateur : le script qui fait
suivre le périmètre par défaut (brigade/session) au changement de type
fonctionne réellement dans Chromium, pas seulement dans le rendu HTML lu par
les tests sans navigateur. Même fixture `navigateur_chromium` que
`planification.tests.test_hors_grille_navigateur` (prompt 59), dupliquée ici
pour réutiliser les fixtures d'`evaluations.tests.conftest` plutôt que de
reconstruire un compte à la main.
"""

import os

import pytest
from django.urls import reverse

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
            except Exception as erreur:  # binaire Chromium absent — jamais une suite cassée
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


def test_b_a1_le_perimetre_suit_le_type_choisi_dans_un_vrai_navigateur(
    navigateur_chromium, live_server, examens
):
    page = navigateur_chromium.new_page()
    _connecter(page, live_server.url, examens.username)
    page.goto(f"{live_server.url}{reverse('evaluations:creer_evaluation')}")

    bloc_brigade = page.locator('[data-perimetre="brigade"]')
    bloc_session = page.locator('[data-perimetre="session"]')
    assert bloc_brigade.is_visible()
    assert not bloc_session.is_visible()

    page.select_option("#id_type", "certificative")

    assert not bloc_brigade.is_visible()
    assert bloc_session.is_visible()

    page.select_option("#id_type", "formative")

    assert bloc_brigade.is_visible()
    assert not bloc_session.is_visible()
