"""US-PLAN-09, cycle HTTP réel (prompt 42, partie 3). Données fictives."""

import datetime

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from planification.models import EtatProgramme, ProgrammeHebdomadaire, Seance
from planification.tests.aide_circuit import amener_a, seance_dans
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


def test_http_y_aller_mene_a_la_consultation_avec_le_vrai_formulaire(client, circuit, cours):
    """K5, prompt 58 (RECETTE-01 A11) : le lien « Y aller » d'une séance
    bloquée par l'état du programme (soumis, ici) mène à la consultation
    du programme — jamais directement à l'URL de l'action de déblocage
    (POST seule, un lien en GET y valait un 405)."""
    programme = amener_a(EtatProgramme.SOUMIS, circuit)
    seance = Seance.objects.get(programme=programme)
    client.force_login(circuit.acteurs.planificateur)
    _, indisponibilite = _indisponibilite_http(client, cours.instructeur, seance.debut, seance.fin)
    url_attendue = (
        reverse("planification:consultation_programme")
        + f"?semaine={programme.lundi_de_semaine.isoformat()}"
    )

    reponse = client.get(reverse("planification:traiter_indisponibilite", args=[indisponibilite.pk]))
    assert url_attendue in reponse.content.decode("utf-8")

    reponse_y_aller = client.get(url_attendue)
    assert reponse_y_aller.status_code == 200


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


def test_http_substitution_propose_seulement_les_matieres_de_la_formation_de_la_brigade(
    client, circuit, cours, brigade_formation
):
    """K3, prompt 58 (RECETTE-01 A3) : l'écran de substitution ne propose
    que les éléments de la formation de la brigade impactée — jamais une
    matière homonyme d'une autre formation."""
    from referentiel.models import ElementReferentiel, Formation, TypeFormation

    seance = seance_dans(
        circuit.programme, cours, brigade_formation, instant(circuit.programme.lundi_de_semaine, 0, 8)
    )
    autre_formation = Formation.objects.create(
        intitule="Autre formation (homonyme, substitution)",
        specialite="Transmissions",
        duree_semaines=1,
        type_formation=TypeFormation.objects.create(intitule="Autre type substitution"),
    )
    element_homonyme = ElementReferentiel.objects.create(
        formation=autre_formation,
        matiere=cours.element.matiere,
        volume_horaire_prescrit=999,
        categorie_lieu=cours.element.categorie_lieu,
    )
    client.force_login(circuit.acteurs.planificateur)
    _, indisponibilite = _indisponibilite_http(client, cours.instructeur, seance.debut, seance.fin)

    reponse = client.get(
        reverse("planification:substituer_seance", args=[indisponibilite.pk, seance.pk])
    )

    contenu = reponse.content.decode("utf-8")
    assert f'value="{cours.element.pk}"' in contenu
    assert f'value="{element_homonyme.pk}"' not in contenu


def _url_lot(indisponibilite, matiere_pk, lundi_de_semaine):
    return (
        reverse("planification:lot_remplacement", args=[indisponibilite.pk, matiere_pk])
        + f"?semaine={lundi_de_semaine.isoformat()}"
    )


def test_http_deux_semaines_de_la_meme_matiere_forment_deux_lots_separes(
    client, circuit, autre_brigade_formation, autre_instructeur
):
    """K11, prompt 58 (RECETTE-01 A7) : `_groupes_lot` ne fusionne jamais
    deux semaines dans un seul lien « traiter en lot », même pour la même
    matière — deux liens distincts, chacun avec sa propre semaine."""
    cours = circuit.cours
    lundi = circuit.programme.lundi_de_semaine
    programme_2 = _programme(lundi + datetime.timedelta(weeks=1))
    seance_dans(circuit.programme, cours, circuit.brigade, instant(lundi, 0, 8))
    seance_dans(circuit.programme, cours, autre_brigade_formation, instant(lundi, 0, 10))
    seance_dans(programme_2, cours, circuit.brigade, instant(lundi + datetime.timedelta(weeks=1), 0, 8))
    seance_dans(
        programme_2,
        cours,
        autre_brigade_formation,
        instant(lundi + datetime.timedelta(weeks=1), 0, 10),
    )
    client.force_login(circuit.acteurs.planificateur)
    _, indisponibilite = _indisponibilite_http(
        client,
        cours.instructeur,
        instant(lundi, 0, 0),
        instant(lundi + datetime.timedelta(weeks=1), 6, 23),
    )

    contenu = client.get(
        reverse("planification:traiter_indisponibilite", args=[indisponibilite.pk])
    ).content.decode("utf-8")

    assert contenu.count("Traiter en lot") == 2
    assert f"semaine={lundi.isoformat()}" in contenu
    assert f"semaine={(lundi + datetime.timedelta(weeks=1)).isoformat()}" in contenu


def test_http_post_lot(client, circuit, autre_brigade_formation, autre_instructeur):
    """Les deux séances du lot sont de la MÊME semaine (K11, prompt 58) —
    `test_http_lot_d_une_semaine_ne_propose_pas_la_seance_d_une_autre_semaine`
    couvre le cas contraire, qui ne forme plus un seul lot."""
    cours = circuit.cours
    qualifier(autre_instructeur, cours.element.matiere)
    lundi = circuit.programme.lundi_de_semaine
    seance_1 = seance_dans(circuit.programme, cours, circuit.brigade, instant(lundi, 0, 8))
    seance_2 = seance_dans(
        circuit.programme, cours, autre_brigade_formation, instant(lundi, 0, 10)
    )
    client.force_login(circuit.acteurs.planificateur)
    _, indisponibilite = _indisponibilite_http(
        client, cours.instructeur, seance_1.debut, seance_2.fin
    )

    reponse = client.post(
        _url_lot(indisponibilite, cours.element.matiere.pk, lundi),
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


def _deux_semaines_de_la_meme_matiere(client, circuit, autre_brigade_formation, autre_instructeur):
    """Partagé par les deux tests K11 ci-dessous : deux séances de la même
    matière, une par semaine, sous la même indisponibilité. Rend
    `(lundi, seance_semaine_1, seance_semaine_2, indisponibilite)`."""
    cours = circuit.cours
    qualifier(autre_instructeur, cours.element.matiere)
    lundi = circuit.programme.lundi_de_semaine
    programme_2 = _programme(lundi + datetime.timedelta(weeks=1))
    seance_semaine_1 = seance_dans(circuit.programme, cours, circuit.brigade, instant(lundi, 0, 8))
    seance_semaine_2 = seance_dans(
        programme_2,
        cours,
        autre_brigade_formation,
        instant(lundi + datetime.timedelta(weeks=1), 0, 8),
    )
    client.force_login(circuit.acteurs.planificateur)
    _, indisponibilite = _indisponibilite_http(
        client,
        cours.instructeur,
        seance_semaine_1.debut,
        seance_semaine_2.fin + datetime.timedelta(weeks=1),
    )
    return lundi, seance_semaine_1, seance_semaine_2, indisponibilite


def test_http_lot_d_une_semaine_ne_propose_pas_la_seance_d_une_autre_semaine(
    client, circuit, autre_brigade_formation, autre_instructeur
):
    """K11, prompt 58 (RECETTE-01 A7) : le lot d'une semaine donnée ne
    propose jamais la séance de la même matière d'une AUTRE semaine."""
    lundi, seance_semaine_1, seance_semaine_2, indisponibilite = _deux_semaines_de_la_meme_matiere(
        client, circuit, autre_brigade_formation, autre_instructeur
    )

    contenu = client.get(
        _url_lot(indisponibilite, circuit.cours.element.matiere.pk, lundi)
    ).content.decode("utf-8")

    assert f'value="{seance_semaine_1.pk}"' in contenu
    assert f'value="{seance_semaine_2.pk}"' not in contenu


def test_http_post_lot_ne_modifie_pas_une_autre_semaine(
    client, circuit, autre_brigade_formation, autre_instructeur
):
    """K11, prompt 58 (RECETTE-01 A7) : traiter le lot d'une semaine
    n'affecte jamais la séance de la même matière d'une AUTRE semaine —
    chaque semaine forme son propre lot (I4 : un remplaçant libre sur UNE
    semaine, pas sur l'étendue cumulée de plusieurs)."""
    lundi, seance_semaine_1, seance_semaine_2, indisponibilite = _deux_semaines_de_la_meme_matiere(
        client, circuit, autre_brigade_formation, autre_instructeur
    )
    cours = circuit.cours

    reponse = client.post(
        _url_lot(indisponibilite, cours.element.matiere.pk, lundi),
        {
            "seances": [seance_semaine_1.pk],
            "instructeur": autre_instructeur.pk,
            "confirmee": "",
            "nature_avenant": "",
            "motif_avenant": "",
        },
        follow=True,
    )

    seance_semaine_1.refresh_from_db()
    seance_semaine_2.refresh_from_db()
    assert reponse.status_code == 200
    assert seance_semaine_1.instructeur == autre_instructeur
    assert seance_semaine_2.instructeur == cours.instructeur


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
