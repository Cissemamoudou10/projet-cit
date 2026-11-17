"""E-A1, prompt 65 (RECETTE-05, R05-IMP-01) — vrai navigateur : la vue
d'impression dédiée du programme hebdomadaire (`planification:
impression_programme`) ne contient QUE le programme, tient en A4 paysage
sans débordement horizontal, et imprime toute la semaine. Même limite que
`tests/navigateur/test_impression_trv07.py` et
`test_hors_grille_navigateur.py` : seul un vrai moteur de rendu le prouve,
pas le client de test Django (qui ne sait pas mesurer une largeur).
"""

import dataclasses
import os

import pypdf
import pytest
from django.urls import reverse

from organisation.services.brigade import ServiceBrigade
from planification.models import EtatProgramme
from planification.tests.aide_circuit import SIGNATAIRE, amener_a, seance_dans
from planification.tests.conftest import instant, qualifier

pytestmark = pytest.mark.navigateur

MOT_DE_PASSE = "x"

# A4 paysage, marges de `impression.css` (`@page paysage { margin: 12mm 14mm
# 14mm; }`) : largeur imprimable = 297 mm - 2*14 mm = 269 mm, soit
# 269 * 96 / 25.4 ≈ 1017 px à 96 px/pouce — même méthode de calcul que
# docs/suivi/IMPRESSION-ANALYSE.md § 1 (703 px, portrait).
LARGEUR_IMPRIMABLE_PAYSAGE_PX = 1017


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


def _url_impression(programme):
    return (
        reverse("planification:impression_programme")
        + f"?semaine={programme.lundi_de_semaine.isoformat()}"
    )


@dataclasses.dataclass(frozen=True)
class ProgrammeTroisBrigades:
    """Regroupe `circuit` et les trois brigades qu'il porte désormais —
    `.claude/rules/python.md`, § 5 paramètres max."""

    circuit: object
    brigades: list


@pytest.fixture
def trois_brigades(redacteur, session_formation, circuit, autre_brigade_formation):
    """Trois brigades de la même session, une séance chacune, trois jours
    distincts — « toute la semaine » (E-A1), jamais un seul jour comme
    l'onglet de l'écran de consultation."""
    troisieme_brigade = ServiceBrigade.creer(
        redacteur, session_formation, {"designation": "GEN3", "effectif_previsionnel": 20}
    )
    qualifier(circuit.cours.instructeur, circuit.cours.element.matiere)
    lundi = circuit.programme.lundi_de_semaine
    for brigade, jour_offset in (
        (circuit.brigade, 0),
        (autre_brigade_formation, 1),
        (troisieme_brigade, 2),
    ):
        seance_dans(circuit.programme, circuit.cours, brigade, instant(lundi, jour_offset, 8))
    return ProgrammeTroisBrigades(
        circuit=circuit, brigades=[circuit.brigade, autre_brigade_formation, troisieme_brigade]
    )


def _aucune_table_ne_deborde(page):
    """Largeur réelle (`scrollWidth`) de chaque `<table>` du document, à
    comparer au budget imprimable — même méthode que
    `docs/suivi/IMPRESSION-ANALYSE.md` § 1 (mesure DOM, pas la lecture du
    PDF produit, qui ne porte aucune information de mise en page)."""
    return page.evaluate(
        """() => Array.from(document.querySelectorAll('table'))
                     .map((t) => t.scrollWidth)
                     .filter((largeur) => largeur > 0)"""
    )


def _verifier_aucun_debordement(page):
    for largeur in _aucune_table_ne_deborde(page):
        assert largeur <= LARGEUR_IMPRIMABLE_PAYSAGE_PX + 2, (
            f"table de {largeur}px, budget imprimable {LARGEUR_IMPRIMABLE_PAYSAGE_PX}px "
            "(débordement horizontal, R05-IMP-01)"
        )


def _verifier_chrome_absent(texte, brigades):
    for brigade in brigades:
        assert brigade.designation in texte, f"{brigade.designation} absente de l'impression"
    for interdit in (
        "Imprimer",
        "Dupliquer",
        "Générer",
        "Historique",
        "Écarts de volume horaire",
        "Circuit du programme",
        "Modifier",
        "Ajouter une séance",
        "Programmes",
    ):
        assert interdit not in texte, f"« {interdit} » encore présent dans la vue dédiée (E-A1)"


def test_la_vue_dediee_ne_contient_que_le_programme_en_paysage_sans_debordement(
    navigateur_chromium, live_server, grille_active, trois_brigades, tmp_path
):
    circuit = trois_brigades.circuit
    page = navigateur_chromium.new_page()
    _connecter(page, live_server.url, circuit.acteurs.planificateur.username)
    page.set_viewport_size({"width": LARGEUR_IMPRIMABLE_PAYSAGE_PX, "height": 900})
    page.emulate_media(media="print")
    page.goto(f"{live_server.url}{_url_impression(circuit.programme)}")
    page.wait_for_load_state("networkidle")

    _verifier_aucun_debordement(page)

    chemin = tmp_path / "impression_programme_3_brigades.pdf"
    page.pdf(path=str(chemin), prefer_css_page_size=True)
    pages = pypdf.PdfReader(str(chemin)).pages
    boite = pages[0].mediabox
    assert boite.width > boite.height, "la vue d'impression n'est pas en paysage (E-A1)"

    texte = "\n".join(p.extract_text() for p in pages)
    _verifier_chrome_absent(texte, trois_brigades.brigades)
    # Relevé, pas un seuil bloquant (consigne du prompt) : nombre de pages
    # pour 3 brigades sur 3 jours — 2 pages à la mesure du 2026-11-17.
    assert len(pages) >= 1


def test_etat_signature_survivent_a_l_impression_reelle(
    navigateur_chromium, live_server, grille_active, circuit, tmp_path
):
    """En-tête minimal (E-A1) : semaine, état, signataire s'il est signé —
    rien d'autre. Programme amené à AFFICHÉ par le circuit réel
    (`amener_a`), jamais un état posé à la main sur le modèle
    (`.claude/rules/tests.md`, P-21). Vérifié dans le PDF réellement
    imprimé (`page.pdf`, média `print` émulé), jamais seulement dans le DOM
    brut (`page.content()`) — c'est précisément ce qui avait laissé passer
    le défaut relevé en relecture : un `<header>` enfant direct de
    `<body>` tombait sous la règle `body > header { display:none }`
    d'`impression.css`, invisible dans le DOM mais absent du PDF produit."""
    qualifier(circuit.cours.instructeur, circuit.cours.element.matiere)
    programme = amener_a(EtatProgramme.AFFICHE, circuit)

    page = navigateur_chromium.new_page()
    _connecter(page, live_server.url, circuit.acteurs.planificateur.username)
    page.emulate_media(media="print")
    page.goto(f"{live_server.url}{_url_impression(programme)}")
    page.wait_for_load_state("networkidle")

    chemin = tmp_path / "impression_entete_affiche.pdf"
    page.pdf(path=str(chemin), prefer_css_page_size=True)
    texte = pypdf.PdfReader(str(chemin)).pages[0].extract_text()
    assert "AFFICHÉ" in texte, "l'état ne survit pas à l'impression réelle (en-tête masqué ?)"
    assert SIGNATAIRE in texte, "le signataire ne survit pas à l'impression réelle"
