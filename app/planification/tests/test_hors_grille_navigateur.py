"""K8, prompt 59 (RECETTE-01 A2) — vrai navigateur : la ligne « Hors grille »
(`selectors_consultation.py::_hors_grille_de_la_brigade`, D-310) survit à
l'impression, pas seulement au rendu HTML lu par les tests de gabarit
ordinaires — même limite que R00B-TRV-07
(`tests/navigateur/test_impression_trv07.py`), même fixture, dupliquée ici
pour réutiliser les fixtures de circuit de `planification.tests.conftest`
plutôt que de reconstruire une session à la main.
"""

import os

import pypdf
import pytest

from planification.tests.aide_circuit import seance_dans
from planification.tests.conftest import instant, qualifier

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


def _pdf_impression(page, url, chemin):
    page.goto(url)
    page.wait_for_load_state("networkidle")
    page.emulate_media(media="print")
    page.pdf(path=str(chemin), prefer_css_page_size=True)


def _url_consultation(programme):
    from django.urls import reverse

    return (
        reverse("planification:consultation_programme")
        + f"?semaine={programme.lundi_de_semaine.isoformat()}"
    )


def test_k8_la_ligne_hors_grille_s_imprime(
    navigateur_chromium, live_server, grille_active, circuit, tmp_path
):
    """Une séance à 13:00 le lundi — aucun créneau de `grille_active`
    (08:00-09:45, 10:10-12:00) ne commence à cette heure : elle doit
    apparaître dans la ligne « Hors grille », à l'écran comme à
    l'impression (même gabarit, `consultation_programme.html`)."""
    qualifier(circuit.cours.instructeur, circuit.cours.element.matiere)
    seance_dans(
        circuit.programme,
        circuit.cours,
        circuit.brigade,
        instant(circuit.programme.lundi_de_semaine, 0, 13),
    )

    page = navigateur_chromium.new_page()
    _connecter(page, live_server.url, circuit.acteurs.planificateur.username)
    chemin = tmp_path / "consultation_hors_grille.pdf"
    _pdf_impression(page, f"{live_server.url}{_url_consultation(circuit.programme)}", chemin)

    texte = pypdf.PdfReader(str(chemin)).pages[0].extract_text()
    assert "Hors grille" in texte, "la ligne « Hors grille » ne survit pas à l'impression (K8)"
    assert str(circuit.cours.element.matiere) in texte
