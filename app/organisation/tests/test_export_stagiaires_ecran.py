"""US-SES-07 — cycle HTTP réel de la liste et de l'export (Prompt 26, § 10,
Groupe D). PRÉEXISTAIENT (US-SES-05, non dupliqués ici) : lecture accordée
aux quatre profils et refusée à l'administrateur sur `liste_stagiaires`
(`test_stagiaire_ecran.py::test_e5_*`). Le test de garde du sprint 1
(D8, aucune adresse d'écriture ajoutée) est couvert par
`tests/architecture/test_ecrans_ecriture.py`, vérifié passer sans
modification. Données entièrement fictives.
"""

import csv
import io

from django.urls import reverse

from organisation.services.brigade import ServiceBrigade
from organisation.services.stagiaire import ServiceStagiaire
from organisation.tests.conftest import donnees_brigade, donnees_stagiaire


def test_d1_get_liste_par_chacun_des_quatre_profils(client, request, session):
    for nom in ("redacteur", "lecteur", "planificateur", "direction_formation"):
        client.force_login(request.getfixturevalue(nom))
        reponse = client.get(reverse("organisation:liste_stagiaires", args=[session.pk]))
        assert reponse.status_code == 200


def test_d2_export_csv_puis_xlsx_entetes_nom_de_fichier_contenu_corrects(
    redacteur, client, session
):
    ServiceStagiaire.creer(redacteur, session, donnees_stagiaire())
    client.force_login(redacteur)

    reponse_csv = client.get(reverse("organisation:exporter_stagiaires", args=[session.pk, "csv"]))
    reponse_xlsx = client.get(
        reverse("organisation:exporter_stagiaires", args=[session.pk, "xlsx"])
    )

    assert reponse_csv["Content-Type"] == "text/csv"
    assert ".csv" in reponse_csv["Content-Disposition"]
    lignes = list(csv.reader(io.StringIO(reponse_csv.content.decode("utf-8-sig")), delimiter=";"))
    assert len(lignes) == 2

    assert "spreadsheetml" in reponse_xlsx["Content-Type"]
    assert ".xlsx" in reponse_xlsx["Content-Disposition"]


def test_d3_examens_atteint_filtre_et_exporte(redacteur, lecteur, client, session):
    brigade = ServiceBrigade.creer(redacteur, session, donnees_brigade())
    client.force_login(lecteur)

    reponse_session = client.get(reverse("organisation:detail_session", args=[session.pk]))
    assert (
        reverse("organisation:liste_stagiaires", args=[session.pk])
        in reponse_session.content.decode()
    )

    reponse_filtree = client.get(
        reverse("organisation:liste_stagiaires", args=[session.pk]), {"brigade": brigade.pk}
    )
    assert reponse_filtree.status_code == 200

    reponse_export = client.get(
        reverse("organisation:exporter_stagiaires", args=[session.pk, "csv"]),
        {"brigade": brigade.pk},
    )
    assert reponse_export.status_code == 200


def test_d4_aucune_commande_d_ecriture_pour_direction_formation(
    direction_formation, client, session
):
    client.force_login(direction_formation)

    reponse = client.get(reverse("organisation:liste_stagiaires", args=[session.pk]))
    contenu = reponse.content.decode()

    assert "Enregistrer un stagiaire" not in contenu
    assert "Importer un fichier" not in contenu
    assert reverse("organisation:creer_stagiaire", args=[session.pk]) not in contenu


def test_d5_liens_ecriture_pour_pedagogique_absents_pour_les_autres(
    redacteur, planificateur, client, session
):
    client.force_login(redacteur)
    reponse_pedagogique = client.get(reverse("organisation:liste_stagiaires", args=[session.pk]))
    assert "Enregistrer un stagiaire" in reponse_pedagogique.content.decode()

    client.force_login(planificateur)
    reponse_planification = client.get(reverse("organisation:liste_stagiaires", args=[session.pk]))
    assert "Enregistrer un stagiaire" not in reponse_planification.content.decode()


def test_d6_administrateur_refuse_sur_la_liste_et_sur_l_export(administrateur, client, session):
    client.force_login(administrateur)

    reponse_liste = client.get(reverse("organisation:liste_stagiaires", args=[session.pk]))
    reponse_export = client.get(
        reverse("organisation:exporter_stagiaires", args=[session.pk, "csv"])
    )

    assert reponse_liste.status_code == 403
    assert reponse_export.status_code == 403


def test_d7_rappel_du_filtre_en_toutes_lettres_reellement_present(redacteur, client, session):
    brigade = ServiceBrigade.creer(redacteur, session, donnees_brigade(designation="EXP1"))
    client.force_login(redacteur)

    reponse = client.get(
        reverse("organisation:liste_stagiaires", args=[session.pk]),
        {"brigade": brigade.pk, "etat": "actifs"},
    )
    contenu = reponse.content.decode()

    assert session.intitule in contenu
    assert "EXP1" in contenu
    assert "actifs" in contenu.lower()
