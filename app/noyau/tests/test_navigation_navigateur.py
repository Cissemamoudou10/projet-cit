"""US-IHM-02, prompt 64 — critère 3 : la barre de navigation ne se déforme
pas d'une rubrique à l'autre. Vrai navigateur, seul moyen de voir une
déformation de mise en page (le client de test ne rend jamais le CSS) —
même fixture `navigateur_chromium` que `planification.tests.
test_filtres_seance_navigateur`/`test_hors_grille_navigateur`, dupliquée
ici pour ne pas coupler `noyau` à leurs fixtures de circuit.

Compte Direction de formation : seul profil dont la matrice d'habilitation
couvre à la fois Référentiel, Sessions, Ressources, Planification et
Évaluations — de quoi visiter plusieurs rubriques réelles dans un seul
test, sans toucher à Administration (hors de son profil, inutile ici)."""

import os

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.urls import reverse

pytestmark = pytest.mark.navigateur

MOT_DE_PASSE = "un-mot-de-passe-suffisamment-long"

RUBRIQUES_A_VISITER = (
    "referentiel:liste_types_formation",
    "organisation:liste_sessions",
    "ressources:liste_instructeurs",
    "planification:consultation_programme",
    "evaluations:liste_evaluations",
    "planification:tableau_bord",
)


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


@pytest.fixture
def utilisateur_direction(db):
    call_command("initialiser_habilitations")
    modele = get_user_model()
    compte = modele.objects.create_user(
        username="dir-essai",
        password=MOT_DE_PASSE,
        grade="Col",
        profil=modele.Profil.DIRECTION_FORMATION,
    )
    compte.groups.add(Group.objects.get(name="Direction de formation"))
    compte.doit_changer_mot_de_passe = False
    compte.save()
    return compte


def _connecter(page, url_base, identifiant):
    page.goto(f"{url_base}/connexion/")
    page.fill('input[name="identifiant"]', identifiant)
    page.fill('input[name="mot_de_passe"]', MOT_DE_PASSE)
    page.click('button[type="submit"]')
    page.wait_for_load_state("networkidle")


def test_la_barre_ne_se_deforme_pas_entre_les_rubriques(
    navigateur_chromium, live_server, utilisateur_direction
):
    page = navigateur_chromium.new_page()
    _connecter(page, live_server.url, utilisateur_direction.username)

    hauteurs = {}
    for url_nom in RUBRIQUES_A_VISITER:
        page.goto(f"{live_server.url}{reverse(url_nom)}")
        page.wait_for_load_state("networkidle")
        boite = page.locator("header").first.bounding_box()
        hauteurs[url_nom] = boite["height"]

    valeurs = set(hauteurs.values())
    assert len(valeurs) == 1, f"hauteurs de la barre selon la rubrique : {hauteurs}"
