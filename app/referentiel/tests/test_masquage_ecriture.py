"""US-REF-07, critère 2 — masquage des commandes d'écriture. Paramétré sur
les quatre profils et les huit écrans du paquetage (Prompt 11, § 6). Le
refus côté serveur (critère 3) est testé dans test_refus_ecriture_direct.py ;
ici on vérifie uniquement le balisage rendu.
"""

import pytest
from django.urls import reverse

from referentiel.services.objectif_pedagogique import ServiceObjectifPedagogique
from referentiel.tests.conftest import creer_element

PROFILS = [
    pytest.param("redacteur", True, id="pedagogique"),
    pytest.param("lecteur", False, id="examens"),
    pytest.param("planificateur", False, id="planification"),
    pytest.param("direction_formation", False, id="direction_formation"),
]


@pytest.fixture
def deux_elements(formation):
    return [
        creer_element(formation, "Électronique numérique", "ELN01"),
        creer_element(formation, "Radiocommunications", "RAD01"),
    ]


def _contenu(client, utilisateur, url):
    client.force_login(utilisateur)
    reponse = client.get(url)
    assert reponse.status_code == 200
    return reponse.content.decode()


@pytest.mark.parametrize("profil, peut_ecrire", PROFILS)
def test_masquage_liste_formations(client, request, profil, peut_ecrire, formation):
    utilisateur = request.getfixturevalue(profil)
    contenu = _contenu(client, utilisateur, reverse("referentiel:liste_formations"))

    assert ("Créer une formation" in contenu) is peut_ecrire
    assert ('title="Modifier"' in contenu) is peut_ecrire


@pytest.mark.parametrize("profil, peut_ecrire", PROFILS)
def test_masquage_liste_matieres(client, request, profil, peut_ecrire, matiere):
    utilisateur = request.getfixturevalue(profil)
    contenu = _contenu(client, utilisateur, reverse("referentiel:liste_matieres"))

    assert ("Créer une matière" in contenu) is peut_ecrire
    assert ('title="Modifier"' in contenu) is peut_ecrire


@pytest.mark.parametrize("profil, peut_ecrire", PROFILS)
def test_masquage_liste_types_formation(client, request, profil, peut_ecrire, type_officiers):
    utilisateur = request.getfixturevalue(profil)
    contenu = _contenu(client, utilisateur, reverse("referentiel:liste_types_formation"))

    assert ("Créer un type" in contenu) is peut_ecrire
    assert ('title="Modifier"' in contenu) is peut_ecrire


@pytest.mark.parametrize("profil, peut_ecrire", PROFILS)
def test_masquage_detail_formation(client, request, profil, peut_ecrire, formation):
    utilisateur = request.getfixturevalue(profil)
    contenu = _contenu(
        client, utilisateur, reverse("referentiel:detail_formation", args=[formation.pk])
    )

    assert ("Modifier" in contenu) is peut_ecrire
    assert "Vue consolidée du référentiel" in contenu


@pytest.mark.parametrize("profil, peut_ecrire", PROFILS)
def test_masquage_detail_matiere(client, request, profil, peut_ecrire, matiere):
    ServiceObjectifPedagogique.ajouter(
        request.getfixturevalue("redacteur"), matiere, "Analyser un schéma électronique"
    )
    utilisateur = request.getfixturevalue(profil)
    contenu = _contenu(
        client, utilisateur, reverse("referentiel:detail_matiere", args=[matiere.pk])
    )

    assert ("Modifier" in contenu) is peut_ecrire
    assert ("<textarea" in contenu) is peut_ecrire
    assert ("Ajouter" in contenu) is peut_ecrire
    assert "Analyser un schéma électronique" in contenu


@pytest.mark.parametrize("profil, peut_ecrire", PROFILS)
def test_masquage_referentiel_formation(client, request, profil, peut_ecrire, deux_elements):
    formation = deux_elements[0].formation
    utilisateur = request.getfixturevalue(profil)
    contenu = _contenu(
        client, utilisateur, reverse("referentiel:referentiel_formation", args=[formation.pk])
    )

    assert ('name="volume_horaire_prescrit"' in contenu) is peut_ecrire
    assert ("Rattacher une matière" in contenu) is peut_ecrire
    assert "Électronique numérique" in contenu


@pytest.mark.parametrize("profil, peut_ecrire", PROFILS)
def test_masquage_prerequis_formation(client, request, profil, peut_ecrire, deux_elements):
    formation = deux_elements[0].formation
    utilisateur = request.getfixturevalue(profil)
    contenu = _contenu(
        client, utilisateur, reverse("referentiel:prerequis_formation", args=[formation.pk])
    )

    assert ('name="element_prerequis"' in contenu) is peut_ecrire
    assert "Prérequis directs" in contenu


@pytest.mark.parametrize("profil, _peut_ecrire", PROFILS)
def test_ecran_consolide_sans_aucune_ecriture_pour_aucun_profil(
    client, request, profil, _peut_ecrire, deux_elements
):
    """Écart § 2.1 : lecture seule sans exception, y compris pour la cellule
    pédagogique — voir la note de conception dans _fragments/tableau_prerequis.html."""
    formation = deux_elements[0].formation
    utilisateur = request.getfixturevalue(profil)
    contenu = _contenu(
        client, utilisateur, reverse("referentiel:consultation_formation", args=[formation.pk])
    )

    assert "Modifier" not in contenu
    assert "<textarea" not in contenu
    assert 'name="volume_horaire_prescrit"' not in contenu
    assert "Rattacher une matière" not in contenu
    assert 'name="element_prerequis"' not in contenu
    assert "Retirer le prérequis" not in contenu
    assert "Électronique numérique" in contenu
