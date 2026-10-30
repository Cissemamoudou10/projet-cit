"""Évolution du prompt 53, Temps 2 — écran de suppression d'un brouillon,
cycle HTTP réel (`.claude/rules/tests.md`). Données fictives."""

from django.urls import reverse

from planification.models import EtatProgramme, ProgrammeHebdomadaire
from planification.tests.aide_circuit import amener_a, seance_dans
from planification.tests.conftest import instant

LIBELLE_SUPPRIMER = "Supprimer ce brouillon"


def _url_suppression(programme):
    return reverse("planification:supprimer_brouillon", args=[programme.pk])


def _consultation(circuit):
    return reverse("planification:consultation_programme") + (
        f"?semaine={circuit.programme.lundi_de_semaine.isoformat()}"
    )


def test_bouton_visible_pour_la_planification_sur_un_brouillon_jamais_soumis(client, circuit):
    seance_dans(
        circuit.programme, circuit.cours, circuit.brigade, instant(circuit.programme.lundi_de_semaine, 0, 8)
    )
    client.force_login(circuit.acteurs.planificateur)

    reponse = client.get(_consultation(circuit))

    assert LIBELLE_SUPPRIMER in reponse.content.decode("utf-8")


def test_bouton_absent_pour_la_cellule_pedagogique(client, circuit):
    seance_dans(
        circuit.programme, circuit.cours, circuit.brigade, instant(circuit.programme.lundi_de_semaine, 0, 8)
    )
    client.force_login(circuit.acteurs.pedagogique)

    reponse = client.get(_consultation(circuit))

    assert LIBELLE_SUPPRIMER not in reponse.content.decode("utf-8")


def test_bouton_absent_sur_un_programme_soumis(client, circuit):
    amener_a(EtatProgramme.SOUMIS, circuit)
    client.force_login(circuit.acteurs.planificateur)

    reponse = client.get(_consultation(circuit))

    assert LIBELLE_SUPPRIMER not in reponse.content.decode("utf-8")


def test_suppression_confirmee_redirige_et_le_programme_disparait(client, circuit):
    programme = circuit.programme
    seance_dans(programme, circuit.cours, circuit.brigade, instant(programme.lundi_de_semaine, 0, 8))
    client.force_login(circuit.acteurs.planificateur)

    reponse = client.post(_url_suppression(programme), {"confirmee": "on"}, follow=True)

    assert reponse.status_code == 200
    assert not ProgrammeHebdomadaire.objects.filter(pk=programme.pk).exists()
    assert "Brouillon supprimé" in reponse.content.decode("utf-8")


def test_adresse_directe_refusee_pour_la_cellule_pedagogique(client, circuit):
    programme = circuit.programme
    seance_dans(programme, circuit.cours, circuit.brigade, instant(programme.lundi_de_semaine, 0, 8))
    client.force_login(circuit.acteurs.pedagogique)

    reponse = client.post(_url_suppression(programme), {"confirmee": "on"})

    assert reponse.status_code == 403
    assert ProgrammeHebdomadaire.objects.filter(pk=programme.pk).exists()
