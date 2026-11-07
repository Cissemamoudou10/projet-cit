"""K8, prompt 59 (RECETTE-01 A2, D-310) — l'ajout et la modification
manuelle d'une séance imposent désormais un créneau de la grille active
(`forms_seance.py::FormulaireSeance`), et une séance déjà hors grille
(données anciennes, duplication depuis une autre grille, grille changée en
cours de semaine) ne redevient jamais invisible : elle s'affiche dans une
ligne « Hors grille » de son jour (`selectors_consultation.py`). Données
entièrement fictives.
"""

from django.urls import reverse

from planification.forms_seance import FormulaireAjoutSeance
from planification.selectors import grille_active_avec_creneaux
from planification.selectors_consultation import grille_consultation
from planification.tests.aide_circuit import seance_dans
from planification.tests.conftest import instant, qualifier


def _url_consultation(programme):
    return (
        reverse("planification:consultation_programme")
        + f"?semaine={programme.lundi_de_semaine.isoformat()}"
    )


def test_le_formulaire_d_ajout_ne_propose_que_les_creneaux_de_la_grille_active(
    circuit, grille_active
):
    """`grille_active` (conftest) porte deux créneaux (08:00-09:45,
    10:10-12:00) sur cinq jours ouvrés (lundi à vendredi, jamais le samedi
    ici) — dix choix au total, aucune heure libre."""
    formulaire = FormulaireAjoutSeance(programme=circuit.programme)

    choix = formulaire.fields["creneau"].choices
    assert len(choix) == 10
    _, creneaux = grille_active_avec_creneaux()
    pks_attendus = {str(creneau.pk) for creneau in creneaux}
    assert {valeur for valeur, _ in choix} == pks_attendus


def test_une_seance_hors_grille_apparait_dans_la_ligne_hors_grille_du_selecteur(
    circuit, grille_active
):
    """Une séance à 13:00 le lundi — aucun créneau de `grille_active` ne
    commence à cette heure : elle doit ressortir dans `hors_grille`, jamais
    dans `cellules` (où elle resterait invisible, RECETTE-01 A2)."""
    seance = seance_dans(
        circuit.programme,
        circuit.cours,
        circuit.brigade,
        instant(circuit.programme.lundi_de_semaine, 0, 13),
    )
    _, creneaux_semaine = grille_active_avec_creneaux()
    creneaux_du_lundi = [c for c in creneaux_semaine if c.jour_semaine == "lundi"]

    groupes = grille_consultation(circuit.programme, creneaux_du_lundi, [circuit.brigade], "lundi")

    lignes = groupes[0]["lignes"]
    hors_grille = lignes[0]["hors_grille"]
    assert [ligne.seance_id for ligne in hors_grille] == [seance.pk]
    assert all(cellule.ligne is None for cellule in lignes[0]["cellules"])


def test_une_seance_le_samedi_hors_grille_apparait_meme_sans_aucun_creneau_ce_jour(
    circuit, grille_active
):
    """`grille_active` ne porte aucun créneau le samedi (lundi à vendredi
    seulement) : `creneaux_du_jour` est alors VIDE pour ce jour, comme le
    calcule la vue — la ligne « Hors grille » doit malgré tout détecter la
    séance, `jour_iso` venant du jour consulté (« samedi »), jamais d'un
    premier créneau qui n'existe pas ce jour-là (relecture K8)."""
    seance = seance_dans(
        circuit.programme,
        circuit.cours,
        circuit.brigade,
        instant(circuit.programme.lundi_de_semaine, 5, 9),
    )

    groupes = grille_consultation(circuit.programme, [], [circuit.brigade], "samedi")

    hors_grille = groupes[0]["lignes"][0]["hors_grille"]
    assert [ligne.seance_id for ligne in hors_grille] == [seance.pk]


def test_http_une_seance_le_samedi_hors_grille_s_affiche_a_l_ecran(client, circuit, grille_active):
    qualifier(circuit.cours.instructeur, circuit.cours.element.matiere)
    seance_dans(
        circuit.programme,
        circuit.cours,
        circuit.brigade,
        instant(circuit.programme.lundi_de_semaine, 5, 9),
    )
    client.force_login(circuit.acteurs.planificateur)

    contenu = client.get(_url_consultation(circuit.programme) + "&jour=samedi").content.decode(
        "utf-8"
    )

    assert "Hors grille" in contenu


def test_http_une_seance_hors_grille_s_affiche_a_l_ecran(client, circuit, grille_active):
    qualifier(circuit.cours.instructeur, circuit.cours.element.matiere)
    seance_dans(
        circuit.programme,
        circuit.cours,
        circuit.brigade,
        instant(circuit.programme.lundi_de_semaine, 0, 13),
    )
    client.force_login(circuit.acteurs.planificateur)

    contenu = client.get(_url_consultation(circuit.programme)).content.decode("utf-8")

    assert "Hors grille" in contenu
    assert str(circuit.cours.element.matiere) in contenu


def test_http_sans_seance_hors_grille_aucune_ligne_hors_grille_ne_s_affiche(
    client, circuit, grille_active
):
    client.force_login(circuit.acteurs.planificateur)

    contenu = client.get(_url_consultation(circuit.programme)).content.decode("utf-8")

    assert "Hors grille" not in contenu
