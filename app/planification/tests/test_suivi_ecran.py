"""US-SUI-05, cycle HTTP réel (prompt 44, Temps 2). Données fictives."""

import datetime

import pytest
from django.urls import reverse

from planification.models import EtatProgramme, NonExecution
from planification.tests.aide_circuit import amener_a, seance_dans
from planification.tests.conftest import instant

MOTIF = "Salle indisponible, contrordre (essai HTTP)."
# Avant 2018 : le Maroc n'observait pas encore l'heure d'été permanente
# (`Africa/Casablanca`, zoneinfo) — un lundi de cette période garde un
# décalage nul, l'heure UTC posée ici tombe donc exactement sur l'heure
# locale attendue par la grille (`creneau.heure_debut`), sans quoi
# `timezone.localtime` la décale et aucune cellule ne correspond plus.
LUNDI_PASSE = datetime.date(2010, 1, 4)


def _ligne_passee(programme, circuit):
    """Créneau 2 (10:10), jamais celui où `amener_a` pose déjà sa propre
    séance (créneau 1, 08:00) pour la même brigade — même jour de la
    semaine (lundi) et même heure colliderait sur la même cellule de la
    grille (`grille_consultation`, clé (brigade, jour ISO, heure))."""
    seance = seance_dans(programme, circuit.cours, circuit.brigade, instant(LUNDI_PASSE, 0, 10, 10))
    return seance.lignes.get()


def _url_declarer(ligne):
    return reverse("planification:declarer_non_execution", args=[ligne.pk])


def _url_annuler(ligne):
    return reverse("planification:annuler_non_execution", args=[ligne.pk])


def _url_consultation(programme):
    return (
        reverse("planification:consultation_programme")
        + f"?semaine={programme.lundi_de_semaine.isoformat()}"
    )


def test_declaration_puis_affichage_de_la_mention(client, circuit, grille_active):
    affiche = amener_a(EtatProgramme.AFFICHE, circuit)
    ligne = _ligne_passee(affiche, circuit)
    client.force_login(circuit.acteurs.planificateur)

    reponse = client.post(_url_declarer(ligne), {"motif": MOTIF}, follow=True)

    assert reponse.status_code == 200
    assert NonExecution.objects.filter(ligne=ligne).exists()
    page = client.get(_url_consultation(affiche)).content.decode("utf-8")
    assert "Non exécutée" in page
    assert MOTIF in page
    assert "Annuler la déclaration" in page


def test_post_sans_motif_refuse_rien_n_est_ecrit(client, circuit):
    affiche = amener_a(EtatProgramme.AFFICHE, circuit)
    ligne = _ligne_passee(affiche, circuit)
    client.force_login(circuit.acteurs.planificateur)

    reponse = client.post(_url_declarer(ligne), {"motif": ""}, follow=True)

    assert reponse.status_code == 200
    assert not NonExecution.objects.filter(ligne=ligne).exists()


def test_post_sur_une_seance_future_forgee_refuse(client, circuit):
    """La séance posée par `amener_a` reste dans le futur (`lundi_semaine`) :
    un POST forgé directement sur son identifiant, en contournant l'écran,
    doit être refusé par le service — jamais par le seul gabarit."""
    affiche = amener_a(EtatProgramme.AFFICHE, circuit)
    ligne_future = affiche.seances.get().lignes.get()
    client.force_login(circuit.acteurs.planificateur)

    reponse = client.post(_url_declarer(ligne_future), {"motif": MOTIF}, follow=True)

    assert reponse.status_code == 200
    assert not NonExecution.objects.filter(ligne=ligne_future).exists()


def test_annulation_par_le_vrai_cycle_http(client, circuit):
    affiche = amener_a(EtatProgramme.AFFICHE, circuit)
    ligne = _ligne_passee(affiche, circuit)
    client.force_login(circuit.acteurs.planificateur)
    client.post(_url_declarer(ligne), {"motif": MOTIF}, follow=True)

    reponse = client.post(_url_annuler(ligne), follow=True)

    assert reponse.status_code == 200
    assert not NonExecution.objects.filter(ligne=ligne).exists()


@pytest.mark.parametrize("profil", ["pedagogique", "examens", "direction_formation"])
def test_habilitation_refusee_en_http(client, circuit, profil, direction_formation):
    affiche = amener_a(EtatProgramme.AFFICHE, circuit)
    ligne = _ligne_passee(affiche, circuit)
    acteur = {
        "pedagogique": circuit.acteurs.pedagogique,
        "examens": circuit.acteurs.examens,
        "direction_formation": direction_formation,
    }[profil]
    client.force_login(acteur)

    reponse = client.post(_url_declarer(ligne), {"motif": MOTIF})

    assert reponse.status_code == 403
    assert not NonExecution.objects.filter(ligne=ligne).exists()
