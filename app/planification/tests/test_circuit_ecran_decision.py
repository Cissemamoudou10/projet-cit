"""US-VAL-02, cycle HTTP réel (prompt 40 § 2) — validation, rejet, reprise. Données fictives."""

from django.urls import reverse

from planification.models import EtatProgramme
from planification.tests.aide_circuit import MOTIF_REJET, amener_a

LIBELLE_VALIDER = "Valider le programme"
LIBELLE_REJETER = "Rejeter le programme"


def _url(nom, programme):
    return reverse(nom, args=[programme.pk])


def _consultation(circuit):
    return reverse("planification:consultation_programme") + (
        f"?semaine={circuit.programme.lundi_de_semaine.isoformat()}"
    )


def test_consultation_d_un_programme_soumis_par_la_pedagogique_repond_200(client, circuit):
    amener_a(EtatProgramme.SOUMIS, circuit)
    client.force_login(circuit.acteurs.pedagogique)

    reponse = client.get(_consultation(circuit))

    assert reponse.status_code == 200
    contenu = reponse.content.decode("utf-8")
    assert LIBELLE_VALIDER in contenu
    assert LIBELLE_REJETER in contenu


def test_validation_par_la_pedagogique_enregistre_validateur_et_date(client, circuit):
    programme = circuit.programme
    amener_a(EtatProgramme.SOUMIS, circuit)
    client.force_login(circuit.acteurs.pedagogique)

    client.post(_url("planification:valider", programme))

    programme.refresh_from_db()
    assert programme.etat == EtatProgramme.VALIDE
    assert programme.valide_par == circuit.acteurs.pedagogique
    assert programme.date_validation is not None
    client.force_login(circuit.acteurs.pedagogique)
    reponse = client.get(reverse("planification:attente_validation"))
    assert reponse.context["validation_en_attente"]["compte"] == 0


def test_validation_par_la_planification_est_refusee_403(client, circuit):
    programme = circuit.programme
    amener_a(EtatProgramme.SOUMIS, circuit)
    client.force_login(circuit.acteurs.planificateur)

    reponse = client.post(_url("planification:valider", programme))

    assert reponse.status_code == 403
    programme.refresh_from_db()
    assert programme.etat == EtatProgramme.SOUMIS


def test_rejet_sans_motif_ou_avec_des_blancs_affiche_l_erreur_et_garde_l_etat(client, circuit):
    programme = circuit.programme
    amener_a(EtatProgramme.SOUMIS, circuit)
    client.force_login(circuit.acteurs.pedagogique)

    for motif in ("", "   "):
        reponse = client.post(
            _url("planification:rejeter", programme), {"motif": motif}, follow=True
        )
        assert "exige un motif" in reponse.content.decode("utf-8")

    programme.refresh_from_db()
    assert programme.etat == EtatProgramme.SOUMIS


def test_rejet_avec_motif_est_lisible_par_la_planification(client, circuit):
    programme = circuit.programme
    amener_a(EtatProgramme.SOUMIS, circuit)
    client.force_login(circuit.acteurs.pedagogique)
    client.post(_url("planification:rejeter", programme), {"motif": MOTIF_REJET})

    programme.refresh_from_db()
    assert programme.etat == EtatProgramme.REJETE
    client.force_login(circuit.acteurs.planificateur)
    reponse = client.get(_consultation(circuit))
    assert f"Motif du rejet : {MOTIF_REJET}" in reponse.content.decode("utf-8")


def test_reprise_garde_le_motif_puis_la_nouvelle_soumission_l_efface(client, circuit):
    programme = circuit.programme
    amener_a(EtatProgramme.REJETE, circuit)
    client.force_login(circuit.acteurs.planificateur)

    client.post(_url("planification:reprendre", programme))

    programme.refresh_from_db()
    assert programme.etat == EtatProgramme.BROUILLON
    contenu_reprise = client.get(_consultation(circuit)).content.decode("utf-8")
    assert f"Motif du rejet : {MOTIF_REJET}" in contenu_reprise

    client.post(_url("planification:soumettre", programme))

    programme.refresh_from_db()
    assert programme.etat == EtatProgramme.SOUMIS
    contenu_soumis = client.get(_consultation(circuit)).content.decode("utf-8")
    assert "Motif du rejet" not in contenu_soumis


def test_la_direction_voit_le_programme_sans_bouton_de_decision(
    client, circuit, direction_formation
):
    amener_a(EtatProgramme.SOUMIS, circuit)
    client.force_login(direction_formation)

    reponse = client.get(_consultation(circuit))

    assert reponse.status_code == 200
    contenu = reponse.content.decode("utf-8")
    assert LIBELLE_VALIDER not in contenu
    assert LIBELLE_REJETER not in contenu


def test_les_examens_ne_lisent_pas_le_programme_403(client, circuit):
    amener_a(EtatProgramme.SOUMIS, circuit)
    client.force_login(circuit.acteurs.examens)

    reponse = client.get(_consultation(circuit))

    assert reponse.status_code == 403
