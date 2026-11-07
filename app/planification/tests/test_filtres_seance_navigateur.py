"""L10, prompt 61 (listes filtrées) — vrai navigateur : le script qui filtre
les options instructeur/lieu selon la matière choisie fonctionne réellement
dans Chromium. Même fixture `navigateur_chromium` que
`test_hors_grille_navigateur` (prompt 59), dupliquée ici pour réutiliser les
fixtures de circuit de `planification.tests.conftest`.
"""

import os

import pytest
from django.urls import reverse

from planification.tests.conftest import creer_element, qualifier
from referentiel.models import Matiere

pytestmark = pytest.mark.navigateur


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
    page.fill('input[name="mot_de_passe"]', "x")
    page.click('button[type="submit"]')
    page.wait_for_load_state("networkidle")


def test_l_instructeur_non_qualifie_est_masque_au_changement_de_matiere(
    navigateur_chromium, live_server, circuit, autre_instructeur
):
    matiere_seule = Matiere.objects.create(intitule="Guerre électronique", code="GE01")
    element_seul = creer_element(circuit.cours.element.formation, matiere_seule)
    qualifier(circuit.cours.instructeur, circuit.cours.element.matiere)
    qualifier(autre_instructeur, matiere_seule)
    # circuit.cours.instructeur qualifié seulement de circuit.cours.element.matiere,
    # autre_instructeur seulement de matiere_seule — jamais l'un pour l'autre.

    page = navigateur_chromium.new_page()
    _connecter(page, live_server.url, circuit.acteurs.planificateur.username)
    page.goto(f"{live_server.url}{reverse('planification:ajouter_seance', args=[circuit.programme.pk])}")

    option_autre = f'#id_instructeur option[value="{autre_instructeur.pk}"]'
    page.select_option("#id_element_referentiel", str(circuit.cours.element.pk))
    assert page.eval_on_selector(option_autre, "el => el.hidden") is True

    page.select_option("#id_element_referentiel", str(element_seul.pk))
    assert page.eval_on_selector(option_autre, "el => el.hidden") is False
