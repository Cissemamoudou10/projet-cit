"""US-PLAN-09, cycle HTTP réel (prompt 42, partie 3). Données fictives."""

import datetime

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from planification.models import ProgrammeHebdomadaire
from planification.tests.aide_circuit import seance_dans
from planification.tests.conftest import instant, qualifier
from ressources.models import IndisponibiliteInstructeur

FORMAT_DATE_HEURE = "%Y-%m-%dT%H:%M"


def _programme(lundi):
    return ProgrammeHebdomadaire.objects.create(lundi_de_semaine=lundi)


def _url_declarer():
    return reverse("ressources:declarer_indisponibilite_instructeur")


def _indisponibilite_http(client, instructeur, debut, fin):
    reponse = client.post(
        _url_declarer(),
        {
            "instructeur": instructeur.pk,
            "debut": debut.strftime(FORMAT_DATE_HEURE),
            "fin": fin.strftime(FORMAT_DATE_HEURE),
            "motif": "Mission (essai HTTP).",
        },
        follow=True,
    )
    return reponse, IndisponibiliteInstructeur.objects.get(instructeur=instructeur)


def test_http_enregistrement_affiche_la_liste_des_seances_impactees(
    client, circuit, cours, brigade_formation
):
    seance = seance_dans(
        circuit.programme,
        cours,
        brigade_formation,
        instant(circuit.programme.lundi_de_semaine, 0, 8),
    )
    client.force_login(circuit.acteurs.planificateur)
    debut = seance.debut - datetime.timedelta(hours=1)
    fin = seance.fin + datetime.timedelta(hours=1)

    reponse, indisponibilite = _indisponibilite_http(client, cours.instructeur, debut, fin)

    assert reponse.status_code == 200
    assert reverse("planification:traiter_indisponibilite", args=[indisponibilite.pk]) in [
        r[0] for r in reponse.redirect_chain
    ]
    assert str(cours.element.matiere) in reponse.content.decode("utf-8")


def test_http_post_remplacement(client, circuit, cours, brigade_formation, autre_instructeur):
    qualifier(autre_instructeur, cours.element.matiere)
    seance = seance_dans(
        circuit.programme,
        cours,
        brigade_formation,
        instant(circuit.programme.lundi_de_semaine, 0, 8),
    )
    client.force_login(circuit.acteurs.planificateur)
    _, indisponibilite = _indisponibilite_http(client, cours.instructeur, seance.debut, seance.fin)

    reponse = client.post(
        reverse("planification:remplacer_seance", args=[indisponibilite.pk, seance.pk]),
        {
            "instructeur": autre_instructeur.pk,
            "confirmee": "",
            "nature_avenant": "",
            "motif_avenant": "",
        },
        follow=True,
    )

    seance.refresh_from_db()
    assert reponse.status_code == 200
    assert seance.instructeur == autre_instructeur


def test_http_post_lot(client, circuit, autre_brigade_formation, autre_instructeur):
    cours = circuit.cours
    qualifier(autre_instructeur, cours.element.matiere)
    lundi = circuit.programme.lundi_de_semaine
    programme_2 = _programme(lundi + datetime.timedelta(weeks=1))
    seance_1 = seance_dans(circuit.programme, cours, circuit.brigade, instant(lundi, 0, 8))
    seance_2 = seance_dans(
        programme_2,
        cours,
        autre_brigade_formation,
        instant(lundi + datetime.timedelta(weeks=1), 0, 8),
    )
    client.force_login(circuit.acteurs.planificateur)
    _, indisponibilite = _indisponibilite_http(
        client, cours.instructeur, seance_1.debut, seance_2.fin + datetime.timedelta(weeks=1)
    )

    reponse = client.post(
        reverse(
            "planification:lot_remplacement", args=[indisponibilite.pk, cours.element.matiere.pk]
        ),
        {
            "seances": [seance_1.pk, seance_2.pk],
            "instructeur": autre_instructeur.pk,
            "confirmee": "",
            "nature_avenant": "",
            "motif_avenant": "",
        },
        follow=True,
    )

    seance_1.refresh_from_db()
    seance_2.refresh_from_db()
    assert reponse.status_code == 200
    assert seance_1.instructeur == autre_instructeur
    assert seance_2.instructeur == autre_instructeur


def test_http_liste_des_remplacants_sans_instructeur_non_qualifie(
    client, circuit, cours, brigade_formation, autre_instructeur
):
    seance = seance_dans(
        circuit.programme,
        cours,
        brigade_formation,
        instant(circuit.programme.lundi_de_semaine, 0, 8),
    )
    client.force_login(circuit.acteurs.planificateur)
    _, indisponibilite = _indisponibilite_http(client, cours.instructeur, seance.debut, seance.fin)

    contenu = client.get(
        reverse("planification:remplacer_seance", args=[indisponibilite.pk, seance.pk])
    ).content.decode("utf-8")

    assert str(autre_instructeur) not in contenu


def test_http_nombre_de_requetes_de_la_liste_identique_avec_1_et_10_seances_impactees(
    client, circuit, cours, brigade_formation
):
    lundi = circuit.programme.lundi_de_semaine
    seance_dans(circuit.programme, cours, brigade_formation, instant(lundi, 0, 8))
    client.force_login(circuit.acteurs.planificateur)
    _, indisponibilite = _indisponibilite_http(
        client,
        cours.instructeur,
        instant(lundi, 0, 0),
        instant(lundi + datetime.timedelta(weeks=10), 0, 0),
    )
    url = reverse("planification:traiter_indisponibilite", args=[indisponibilite.pk])

    with CaptureQueriesContext(connection) as capture_une:
        client.get(url)
    nombre_avec_une = len(capture_une)

    for semaine in range(1, 10):
        programme = _programme(lundi + datetime.timedelta(weeks=semaine))
        seance_dans(
            programme,
            cours,
            brigade_formation,
            instant(lundi + datetime.timedelta(weeks=semaine), 0, 8),
        )

    with CaptureQueriesContext(connection) as capture_dix:
        client.get(url)
    nombre_avec_dix = len(capture_dix)

    assert nombre_avec_une == nombre_avec_dix


def test_http_post_par_la_pedagogique_403(
    client, circuit, cours, brigade_formation, autre_instructeur
):
    qualifier(autre_instructeur, cours.element.matiere)
    seance = seance_dans(
        circuit.programme,
        cours,
        brigade_formation,
        instant(circuit.programme.lundi_de_semaine, 0, 8),
    )
    client.force_login(circuit.acteurs.planificateur)
    _, indisponibilite = _indisponibilite_http(client, cours.instructeur, seance.debut, seance.fin)
    client.force_login(circuit.acteurs.pedagogique)

    reponse = client.post(
        reverse("planification:remplacer_seance", args=[indisponibilite.pk, seance.pk]),
        {"instructeur": autre_instructeur.pk, "confirmee": ""},
    )

    assert reponse.status_code == 403
