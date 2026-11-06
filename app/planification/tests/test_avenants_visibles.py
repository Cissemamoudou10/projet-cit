"""K9, prompt 59 (RECETTE-01 A5) — un programme affiché ne laissait nulle
part consulter l'avenant d'une séance (remplacement I6 → I8 introuvable
depuis l'écran). Désormais : (1) l'avenant est visible sur l'écran de la
séance (nature, motif, auteur, date, valeur avant/après) ; (2) la liste des
avenants du programme nomme sa séance (jour, créneau, brigade, matière) ;
(3) une séance qui porte un avenant est repérée dans la grille par une
marque discrète. Données entièrement fictives.
"""

import datetime

from django.urls import reverse

from planification.models import EtatProgramme, NatureAvenant, Seance
from planification.services.ecriture import ServiceEcritureSeance
from planification.services.modification import Avenantage
from planification.tests.aide_circuit import amener_a
from planification.tests.conftest import instant, qualifier

MOTIF = "Changement de créneau demandé par le lieu."


def _url_modifier(seance):
    return reverse("planification:modifier_seance", args=[seance.pk])


def _url_consultation(programme):
    return (
        reverse("planification:consultation_programme")
        + f"?semaine={programme.lundi_de_semaine.isoformat()}"
    )


def _seance_avec_avenant(circuit):
    qualifier(circuit.cours.instructeur, circuit.cours.element.matiere)
    programme = amener_a(EtatProgramme.AFFICHE, circuit)
    seance = Seance.objects.get(programme=programme)
    nouveau_debut = instant(programme.lundi_de_semaine, 0, 10, 10)
    nouveau_fin = nouveau_debut + datetime.timedelta(hours=1, minutes=50)
    ServiceEcritureSeance.modifier_seance(
        circuit.acteurs.planificateur,
        seance,
        {"debut": nouveau_debut, "fin": nouveau_fin},
        avenant=Avenantage(motif=MOTIF, nature=NatureAvenant.DEPLACEMENT),
        confirmee=False,
    )
    seance.refresh_from_db()
    return seance


def test_l_avenant_est_visible_sur_l_ecran_de_la_seance(client, circuit):
    seance = _seance_avec_avenant(circuit)
    client.force_login(circuit.acteurs.planificateur)

    contenu = client.get(_url_modifier(seance)).content.decode("utf-8")

    assert "Avenants de cette séance" in contenu
    assert "Déplacement" in contenu
    assert MOTIF in contenu
    assert "planificateur-plan" in contenu  # auteur (cree_par)
    assert "debut :" in contenu  # détail — valeur avant/après
    assert "08:00" in contenu and "10:10" in contenu


def test_aucune_section_avenant_si_la_seance_n_en_porte_pas(client, circuit):
    qualifier(circuit.cours.instructeur, circuit.cours.element.matiere)
    programme = amener_a(EtatProgramme.BROUILLON, circuit)
    seance = Seance.objects.get(programme=programme)
    client.force_login(circuit.acteurs.planificateur)

    contenu = client.get(_url_modifier(seance)).content.decode("utf-8")

    assert "Avenants de cette séance" not in contenu


def test_la_liste_des_avenants_du_programme_nomme_sa_seance(client, circuit):
    seance = _seance_avec_avenant(circuit)
    client.force_login(circuit.acteurs.planificateur)

    contenu = client.get(_url_consultation(circuit.programme)).content.decode("utf-8")

    assert "lundi" in contenu.lower()
    assert "10:10" in contenu and "12:00" in contenu
    assert str(circuit.brigade) in contenu
    assert str(seance.element_referentiel.matiere) in contenu


def test_la_grille_marque_discretement_la_seance_qui_porte_un_avenant(client, grille_active, circuit):
    """`grille_active` (conftest) porte un créneau 10:10-12:00 le lundi —
    exactement l'heure où `_seance_avec_avenant` déplace la séance : la
    marque s'affiche dans une cellule normale de la grille, pas dans la
    ligne « Hors grille »."""
    _seance_avec_avenant(circuit)
    client.force_login(circuit.acteurs.planificateur)

    contenu = client.get(_url_consultation(circuit.programme)).content.decode("utf-8")

    assert "#avenant" in contenu
