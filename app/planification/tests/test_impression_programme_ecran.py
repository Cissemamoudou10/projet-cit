"""E-A1, prompt 65 (RECETTE-05, R05-IMP-01) — cycle HTTP réel de la vue
d'impression dédiée (`.claude/rules/tests.md`) : chemin nominal en lecture
et refus d'habilitation. Les preuves de mise en page (paysage, absence de
débordement, nombre de pages) vivent dans
`test_impression_programme_navigateur.py`, marqué `navigateur` — un client
de test Django ne sait ni mesurer une largeur ni dire si une page est
paysage."""

from django.urls import reverse

from planification.tests.aide_circuit import seance_dans
from planification.tests.conftest import instant, qualifier


def _preparer_trois_jours(circuit, autre_brigade_formation):
    qualifier(circuit.cours.instructeur, circuit.cours.element.matiere)
    lundi = circuit.programme.lundi_de_semaine
    seance_dans(circuit.programme, circuit.cours, circuit.brigade, instant(lundi, 0, 8))
    seance_dans(circuit.programme, circuit.cours, autre_brigade_formation, instant(lundi, 2, 8))


def test_http_impression_programme_accessible_en_lecture(
    client, grille_active, circuit, autre_brigade_formation
):
    _preparer_trois_jours(circuit, autre_brigade_formation)
    client.force_login(circuit.acteurs.planificateur)

    reponse = client.get(
        reverse("planification:impression_programme"),
        {"semaine": circuit.programme.lundi_de_semaine.isoformat()},
    )

    assert reponse.status_code == 200


def test_http_impression_programme_refusee_a_la_cellule_examens(client, examens, circuit):
    """Même permission que l'écran de consultation (`noyau.programme_lecture`)
    — la Cellule examens ne la porte pas (§ 11.2)."""
    client.force_login(examens)

    reponse = client.get(reverse("planification:impression_programme"))

    assert reponse.status_code == 403


def test_impression_contient_toute_la_semaine_pas_seulement_un_jour(
    client, grille_active, circuit, autre_brigade_formation
):
    """Contrairement à l'écran de consultation (un seul jour par onglet,
    § 9), la vue d'impression porte TOUS les jours qui ont un créneau ou une
    séance — ici lundi ET mercredi, jamais filtré au seul jour « actif »."""
    _preparer_trois_jours(circuit, autre_brigade_formation)
    client.force_login(circuit.acteurs.planificateur)

    reponse = client.get(
        reverse("planification:impression_programme"),
        {"semaine": circuit.programme.lundi_de_semaine.isoformat()},
    )

    contenu = reponse.content.decode("utf-8")
    assert circuit.brigade.designation in contenu
    assert autre_brigade_formation.designation in contenu
    assert "Lundi" in contenu
    assert "Mercredi" in contenu


def test_impression_ne_contient_pas_le_chrome_de_l_ecran(
    client, grille_active, circuit, autre_brigade_formation
):
    """Constat du recetteur (R05-IMP-01) : aucun bouton, aucun menu, aucune
    rubrique d'écart ni d'historique — le gabarit dédié ne les porte même
    pas dans son code source, pas seulement masqués par du CSS."""
    _preparer_trois_jours(circuit, autre_brigade_formation)
    client.force_login(circuit.acteurs.planificateur)

    reponse = client.get(
        reverse("planification:impression_programme"),
        {"semaine": circuit.programme.lundi_de_semaine.isoformat()},
    )

    contenu = reponse.content.decode("utf-8")
    for interdit in (
        "Dupliquer",
        "Générer",
        "Historique",
        "Écarts de volume horaire",
        "Circuit du programme",
        "Ajouter une séance",
        "Progression réalisée",
    ):
        assert interdit not in contenu, f"« {interdit} » présent dans la vue d'impression"


def test_lien_imprimer_de_l_ecran_pointe_vers_la_vue_dediee(
    client, grille_active, circuit, autre_brigade_formation
):
    _preparer_trois_jours(circuit, autre_brigade_formation)
    client.force_login(circuit.acteurs.planificateur)

    reponse = client.get(
        reverse("planification:consultation_programme"),
        {"semaine": circuit.programme.lundi_de_semaine.isoformat()},
    )

    contenu = reponse.content.decode("utf-8")
    assert reverse("planification:impression_programme") in contenu
