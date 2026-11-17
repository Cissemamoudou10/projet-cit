"""E-A2, prompt 65 (RECETTE-05) — vrai navigateur : les rubriques
« Historique » et « Écarts de volume horaire » de l'écran de consultation du
programme sont repliées par défaut, se déplient au clic, et le programme
devient visible sans défiler sur un écran de 1366 × 768 avec trois
brigades. Le client de test Django rend le HTML mais ne sait pas dire si un
élément est visible à l'écran ni mesurer sa position — seul un vrai
navigateur le prouve (même limite que les autres tests `navigateur` du
projet).
"""

import os

import pytest
from django.urls import reverse

from organisation.services.brigade import ServiceBrigade
from planification.services.circuit import ServiceCircuitProgramme
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


def _url_consultation(programme):
    return (
        reverse("planification:consultation_programme")
        + f"?semaine={programme.lundi_de_semaine.isoformat()}"
    )


@pytest.fixture
def programme_avec_historique_et_ecarts(
    redacteur, session_formation, circuit, autre_brigade_formation
):
    _construire_historique_et_ecarts(redacteur, session_formation, circuit, autre_brigade_formation)
    return circuit


def _construire_historique_et_ecarts(
    redacteur, session_formation, circuit, autre_brigade_formation
):
    """Trois brigades (§ prompt), au moins une entrée d'historique (le
    circuit réel : soumettre puis rejeter en produit une, RG-du circuit) et
    au moins un écart de volume horaire (volume prescrit très bas, dépassé
    par la séance posée) — pour que les DEUX rubriques existent et portent
    un résumé non vide."""
    troisieme_brigade = ServiceBrigade.creer(
        redacteur, session_formation, {"designation": "GEN3", "effectif_previsionnel": 20}
    )
    qualifier(circuit.cours.instructeur, circuit.cours.element.matiere)
    circuit.cours.element.volume_horaire_prescrit = 1
    circuit.cours.element.save(update_fields=["volume_horaire_prescrit"])
    lundi = circuit.programme.lundi_de_semaine
    for brigade, jour_offset in (
        (circuit.brigade, 0),
        (autre_brigade_formation, 1),
        (troisieme_brigade, 2),
    ):
        seance_dans(circuit.programme, circuit.cours, brigade, instant(lundi, jour_offset, 8))
    # Une seconde séance pour `circuit.brigade` : une seule (2 h programmées
    # contre 1 h prescrite) reste TOLÉRÉE (RG-39 a, écart < durée du plus
    # long créneau de la grille, ~1h50) — deux séances (4 h) dépassent la
    # tolérance, un vrai écart « dépassement » apparaît.
    seance_dans(circuit.programme, circuit.cours, circuit.brigade, instant(lundi, 3, 8))
    ServiceCircuitProgramme.soumettre(circuit.acteurs.planificateur, circuit.programme)
    ServiceCircuitProgramme.rejeter(circuit.acteurs.pedagogique, circuit.programme, "Motif.")


def _verifier_repliees_par_defaut(page):
    historique = page.locator("details[aria-label='Historique']")
    ecarts = page.locator("details[aria-label='Écarts de volume horaire — prescrit / programmé']")
    assert historique.count() == 1, "rubrique Historique absente"
    assert ecarts.count() == 1, "rubrique Écarts absente"
    assert historique.get_attribute("open") is None, "Historique ouverte au chargement (E-A2)"
    assert ecarts.get_attribute("open") is None, "Écarts ouverte au chargement (E-A2)"
    return historique, ecarts


def _verifier_resumes(historique, ecarts):
    resume_historique = historique.locator("summary span").last.inner_text()
    resume_ecarts = ecarts.locator("summary span").last.inner_text()
    assert "entrée" in resume_historique, f"résumé Historique inattendu : {resume_historique!r}"
    assert "écart" in resume_ecarts, f"résumé Écarts inattendu : {resume_ecarts!r}"


def test_rubriques_repliees_par_defaut_et_programme_visible_sans_defilement(
    navigateur_chromium, live_server, grille_active, programme_avec_historique_et_ecarts
):
    circuit = programme_avec_historique_et_ecarts
    page = navigateur_chromium.new_page()
    page.set_viewport_size({"width": 1366, "height": 768})
    _connecter(page, live_server.url, circuit.acteurs.planificateur.username)
    page.goto(f"{live_server.url}{_url_consultation(circuit.programme)}")
    page.wait_for_load_state("networkidle")

    historique, ecarts = _verifier_repliees_par_defaut(page)
    _verifier_resumes(historique, ecarts)

    boite_programme = page.locator("table.table-fixed").first.bounding_box()
    assert boite_programme is not None, "le tableau du programme n'est pas rendu"
    assert boite_programme["y"] < 768, (
        f"programme visible seulement après défilement (y={boite_programme['y']}, E-A2)"
    )

    historique.locator("summary").click()
    assert historique.get_attribute("open") == "", "Historique ne s'ouvre pas au clic (E-A2)"
    ecarts.locator("summary").click()
    assert ecarts.get_attribute("open") == "", "Écarts ne s'ouvre pas au clic (E-A2)"
