"""US-SES-05 — cycle HTTP réel, Groupe E (Prompt 24, § 12). Le refus
d'habilitation exhaustif sur chaque adresse d'écriture (E4) et le test de
garde mécanique (E6) sont couverts une fois pour toutes par
tests/architecture/test_ecrans_ecriture.py — vérifié séparément, non dupliqué
ici pour chaque adresse. Données entièrement fictives.
"""

import base64
import datetime

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse

from organisation.import_stagiaires.analyse import analyser
from organisation.models import Stagiaire
from organisation.services.stagiaire import ServiceStagiaire
from organisation.tests.conftest import donnees_stagiaire
from organisation.tests.fichiers_stagiaires import construire_csv

LIGNES = [
    ["M001", "Ziani", "Karim", "Lt", "1er RTR"],
    ["M002", "Bennani", "Yasmine", "Cne", "2e RTR"],
]


def _fichier_upload(contenu=None, nom="stagiaires.csv"):
    return SimpleUploadedFile(nom, contenu or construire_csv(LIGNES), content_type="text/csv")


# --- E1 — chemin nominal, profil pédagogique -----------------------------


def test_e1_creer_stagiaire_par_l_ecran_cree_reellement_le_stagiaire(client, redacteur, session):
    client.force_login(redacteur)

    reponse = client.post(
        reverse("organisation:creer_stagiaire", args=[session.pk]), donnees_stagiaire()
    )

    assert reponse.status_code == 302
    assert Stagiaire.objects.filter(session=session, matricule="M001").exists()


def test_e1_modifier_stagiaire_par_l_ecran_modifie_reellement(
    client, redacteur, session, stagiaire
):
    client.force_login(redacteur)

    reponse = client.post(
        reverse("organisation:modifier_stagiaire", args=[session.pk, stagiaire.pk]),
        donnees_stagiaire(nom="Nouveau nom"),
    )

    assert reponse.status_code == 302
    stagiaire.refresh_from_db()
    assert stagiaire.nom == "Nouveau nom"


def test_e1_radier_stagiaire_par_l_ecran_radie_reellement(client, redacteur, session, stagiaire):
    client.force_login(redacteur)

    reponse = client.post(
        reverse("organisation:radier_stagiaire", args=[session.pk, stagiaire.pk]),
        {"motif": "Fin anticipée", "date_radiation": "2026-09-12"},
    )

    assert reponse.status_code == 302
    stagiaire.refresh_from_db()
    assert stagiaire.radie


def test_e1_deradier_stagiaire_par_l_ecran_deradie_reellement(
    client, redacteur, session, stagiaire
):
    """Bloc F, Prompt 33 : `deradier_stagiaire` avait une adresse, une vue,
    aucun test — ni nominal ni HTTP (R2-SES05-26 du cahier de recette :
    « constater que ce n'est pas offert » aurait été la réponse fausse)."""
    ServiceStagiaire.radier(redacteur, stagiaire, "Fin anticipée", datetime.date(2026, 9, 12))
    client.force_login(redacteur)

    reponse = client.post(
        reverse("organisation:deradier_stagiaire", args=[session.pk, stagiaire.pk])
    )

    assert reponse.status_code == 302
    stagiaire.refresh_from_db()
    assert not stagiaire.radie


def test_e1_supprimer_stagiaire_par_l_ecran_supprime_reellement(
    client, redacteur, session, stagiaire
):
    client.force_login(redacteur)

    reponse = client.post(
        reverse("organisation:supprimer_stagiaire", args=[session.pk, stagiaire.pk])
    )

    assert reponse.status_code == 302
    assert not Stagiaire.objects.filter(pk=stagiaire.pk).exists()


def test_e1_importer_analyse_par_l_ecran_n_ecrit_rien(client, redacteur, session):
    client.force_login(redacteur)

    reponse = client.post(
        reverse("organisation:importer_stagiaires", args=[session.pk]),
        {"fichier": _fichier_upload()},
    )

    assert reponse.status_code == 200
    assert Stagiaire.objects.filter(session=session).count() == 0


def test_e1_confirmer_import_par_l_ecran_enregistre_reellement(client, redacteur, session):
    client.force_login(redacteur)
    contenu = construire_csv(LIGNES)

    reponse = client.post(
        reverse("organisation:confirmer_import_stagiaires", args=[session.pk]),
        {
            "fichier_b64": base64.b64encode(contenu).decode("ascii"),
            "nom_fichier": "stagiaires.csv",
        },
    )

    assert reponse.status_code == 302
    assert Stagiaire.objects.filter(session=session).count() == 2


def test_e1_telecharger_le_modele_par_l_ecran(client, redacteur, session):
    client.force_login(redacteur)

    reponse = client.get(reverse("organisation:modele_import_stagiaires", args=[session.pk]))

    assert reponse.status_code == 200
    assert reponse["Content-Disposition"].startswith("attachment")


# --- E2 — import complet par le vrai cycle HTTP, dépôt de fichier compris -


def test_e2_import_complet_depot_analyse_confirmation_stagiaires_en_base(
    client, redacteur, session
):
    client.force_login(redacteur)

    reponse_analyse = client.post(
        reverse("organisation:importer_stagiaires", args=[session.pk]),
        {"fichier": _fichier_upload()},
    )
    assert reponse_analyse.status_code == 200
    assert Stagiaire.objects.filter(session=session).count() == 0

    fichier_b64 = reponse_analyse.context["fichier_b64"]
    nom_fichier = reponse_analyse.context["nom_fichier"]

    reponse_confirmation = client.post(
        reverse("organisation:confirmer_import_stagiaires", args=[session.pk]),
        {"fichier_b64": fichier_b64, "nom_fichier": nom_fichier},
    )

    assert reponse_confirmation.status_code == 302
    assert Stagiaire.objects.filter(session=session).count() == 2


# --- E3 — le compte rendu affiche réellement numéros de ligne et motifs --


def test_e3_compte_rendu_affiche_reellement_numeros_de_ligne_et_motifs(client, redacteur, session):
    client.force_login(redacteur)
    contenu = construire_csv([["", "Ziani", "Karim", "Lt", "1er RTR"]])

    reponse = client.post(
        reverse("organisation:importer_stagiaires", args=[session.pk]),
        {"fichier": _fichier_upload(contenu)},
    )
    contenu_html = reponse.content.decode()

    assert "2" in contenu_html
    assert "matricule" in contenu_html.lower()
    assert "absent" in contenu_html.lower()


# --- E4 (représentatif) — refus d'habilitation --------------------------


def test_e4_planification_ne_peut_pas_creer_de_stagiaire(client, planificateur, session):
    client.force_login(planificateur)

    reponse = client.post(
        reverse("organisation:creer_stagiaire", args=[session.pk]), donnees_stagiaire()
    )

    assert reponse.status_code == 403
    assert not Stagiaire.objects.filter(session=session).exists()


# --- E5 — lecture accordée aux quatre profils, refusée à l'administrateur -


@pytest.mark.parametrize(
    "nom_utilisateur", ["redacteur", "lecteur", "planificateur", "direction_formation"]
)
def test_e5_lecture_accordee_aux_quatre_profils_habilites(
    client, request, session, nom_utilisateur
):
    client.force_login(request.getfixturevalue(nom_utilisateur))

    reponse = client.get(reverse("organisation:liste_stagiaires", args=[session.pk]))

    assert reponse.status_code == 200


def test_e5_lecture_refusee_a_l_administrateur(client, administrateur, session):
    client.force_login(administrateur)

    reponse = client.get(reverse("organisation:liste_stagiaires", args=[session.pk]))

    assert reponse.status_code == 403


def test_e5_examens_lit_mais_n_ecrit_pas(client, lecteur, session):
    """`lecteur` (conftest) est la cellule examens (§ 10, Prompt 24) : lit
    cette liste pour la saisie des notes, ne l'écrit jamais — les deux
    assertions dans le même test."""
    client.force_login(lecteur)

    reponse_lecture = client.get(reverse("organisation:liste_stagiaires", args=[session.pk]))
    reponse_ecriture = client.post(
        reverse("organisation:creer_stagiaire", args=[session.pk]), donnees_stagiaire()
    )

    assert reponse_lecture.status_code == 200
    assert reponse_ecriture.status_code == 403


# --- E7 — le modèle réellement servi correspond au format attendu --------


def test_e7_modele_telecharge_par_http_accepte_par_l_analyse(client, redacteur, session):
    client.force_login(redacteur)

    reponse = client.get(reverse("organisation:modele_import_stagiaires", args=[session.pk]))
    contenu_modele = b"".join(reponse.streaming_content) if reponse.streaming else reponse.content

    rapport = analyser(session, contenu_modele, "modele_import_stagiaires.xlsx")

    assert rapport.lignes_valides == []
    assert rapport.anomalies == []


def test_d5_radiation_et_suppression_sont_deux_adresses_distinctes(client, redacteur, session):
    """Deux confirmations distinctes (BNF-09, § 7, Prompt 24) : radier un
    stagiaire ne le supprime jamais, et réciproquement."""
    stagiaire = ServiceStagiaire.creer(redacteur, session, donnees_stagiaire())
    client.force_login(redacteur)

    client.post(
        reverse("organisation:radier_stagiaire", args=[session.pk, stagiaire.pk]),
        {"motif": "Radiation", "date_radiation": datetime.date.today().isoformat()},
    )

    stagiaire.refresh_from_db()
    assert stagiaire.radie
    assert Stagiaire.objects.filter(pk=stagiaire.pk).exists()

    url_radier = reverse("organisation:radier_stagiaire", args=[session.pk, stagiaire.pk])
    url_supprimer = reverse("organisation:supprimer_stagiaire", args=[session.pk, stagiaire.pk])
    assert url_radier != url_supprimer
