"""R00B-TRV-07, vrai navigateur (prompt 54 bis) — les tests de gabarit du
prompt 54 (`noyau/tests/test_gabarits.py`,
`ressources/tests/test_instructeur_ecran.py`) ne lisent que le HTML rendu :
ils ne pouvaient pas voir qu'aucune règle `@page` nommée n'existait pour le
paysage, ni qu'un filet décoratif nu sous `<body>` (hors de `<header>`)
forçait une rupture de page parasite — seul un vrai moteur de rendu, sur un
vrai PDF paginé, le révèle. Voir `docs/suivi/PROBLEMES.md` pour la cause
complète.

Marqueur `navigateur` : jamais lancé par la suite par défaut (conftest.py
racine), ni par `pytest -m pdf`. Lancer avec :
  pytest -m navigateur                              (poste Windows ou Linux)
  docker run ... pytest -m navigateur                (conteneur, si Chromium
                                                       y est installé — voir
                                                       PROBLEMES.md)
Ignoré avec un message clair si Playwright ou Chromium sont absents —
jamais une suite cassée pour qui n'a pas lancé `playwright install chromium`
(requirements-dev.txt, dépendance de poste de développement uniquement).
"""

import os

import pypdf
import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command

pytestmark = pytest.mark.navigateur

MOT_DE_PASSE = "x"
BOUTONS_FICHE_SESSION = [
    "Modifier",
    "Clôturer",
    "Constituer les brigades",
    "Voir les stagiaires",
    "Répartir les stagiaires",
    "Voir le référentiel de la formation",
]


@pytest.fixture
def navigateur_chromium():
    """Le pilote synchrone de Playwright installe une boucle asyncio dans le
    thread courant (greenlet) : l'ORM Django, appelé ensuite dans ce même
    test, s'y croit à tort en contexte async et refuse toute requête
    (`SynchronousOnlyOperation`) — aucun accès concurrent réel, seule
    l'heuristique de détection se trompe. Échappatoire documentée par
    Django lui-même, restreinte à ces tests seulement."""
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
def utilisateur_pedagogique(db):
    call_command("initialiser_habilitations")
    modele = get_user_model()
    utilisateur = modele.objects.create_user(
        username="nav-ped",
        password=MOT_DE_PASSE,
        grade="Lt",
        profil=modele.Profil.CELLULE_PEDAGOGIQUE,
    )
    utilisateur.groups.add(Group.objects.get(name="Cellule pédagogique"))
    utilisateur.doit_changer_mot_de_passe = False
    utilisateur.save()
    return utilisateur


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


def _session_s0(redacteur):
    from organisation.services.session import ServiceSession
    from organisation.tests.conftest import donnees_session
    from referentiel.models import (
        CategorieLieu,
        ElementReferentiel,
        Formation,
        Matiere,
        TypeFormation,
    )

    type_formation = TypeFormation.objects.create(intitule="Officiers")
    formation = Formation.objects.create(
        intitule="Formation initiale",
        specialite="Transmissions",
        duree_semaines=10,
        type_formation=type_formation,
    )
    matiere = Matiere.objects.create(intitule="Électronique numérique", code="ELN01")
    ElementReferentiel.objects.create(
        formation=formation,
        matiere=matiere,
        volume_horaire_prescrit=40,
        categorie_lieu=CategorieLieu.SALLE_ATTITREE,
        type_lieu_partage=None,
    )
    return ServiceSession.creer(redacteur, donnees_session(formation))


def test_r00b_trv07_aucun_bouton_imprime_sur_la_fiche_de_composition(
    navigateur_chromium, live_server, utilisateur_pedagogique, tmp_path
):
    session = _session_s0(utilisateur_pedagogique)

    page = navigateur_chromium.new_page()
    _connecter(page, live_server.url, utilisateur_pedagogique.username)
    chemin = tmp_path / "fiche_composition.pdf"
    _pdf_impression(page, f"{live_server.url}/sessions/{session.pk}/", chemin)

    texte = pypdf.PdfReader(str(chemin)).pages[0].extract_text()
    for bouton in BOUTONS_FICHE_SESSION:
        assert bouton not in texte, f"bouton « {bouton} » encore imprimé (R00B-TRV-07)"


def test_r00b_trv07_liste_des_instructeurs_s_imprime_en_une_page_paysage(
    navigateur_chromium, live_server, utilisateur_pedagogique, tmp_path
):
    from ressources.models import Instructeur, Statut

    Instructeur.objects.create(
        nom="Zalbrok",
        prenom="Kelvar",
        matricule="M12345",
        grade="Lt",
        specialite="Transmissions",
        statut=Statut.MILITAIRE_DU_CENTRE,
    )

    page = navigateur_chromium.new_page()
    _connecter(page, live_server.url, utilisateur_pedagogique.username)
    chemin = tmp_path / "liste_instructeurs.pdf"
    _pdf_impression(page, f"{live_server.url}/instructeurs/", chemin)

    pages = pypdf.PdfReader(str(chemin)).pages
    assert len(pages) == 1, f"{len(pages)} pages — devrait tenir sur une seule (filet parasite ?)"
    boite = pages[0].mediabox
    assert boite.width > boite.height, "liste des instructeurs toujours en portrait (R00B-TRV-07)"
