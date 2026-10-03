"""US-EVAL-04 — cycle HTTP réel de l'organisation d'épreuve (blocs F et G, Prompt 38).
Passe par `reverse()` et le client de test. Données entièrement fictives.
"""

import datetime

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from administration.models import EntreeJournal, TypeAction
from evaluations.models import Evaluation, OrganisationEpreuve, Surveillance
from evaluations.services.organisation import ServiceOrganisationEpreuve as Service
from evaluations.services.sujet import ServiceSujet
from evaluations.tests.conftest import _enregistrer, affecter_stagiaires, creer_brigade
from noyau.intervalles import instant_de
from ressources.models import IndisponibiliteInstructeur, Lieu

H8, H10 = datetime.time(8, 0), datetime.time(10, 0)


@pytest.fixture
def epreuve_creneau(certificative, examens):
    return Service.fixer_creneau(examens, certificative, H8, H10)


def _post(client, nom, args, donnees=None):
    return client.post(reverse(nom, args=args), donnees or {}, follow=False)


def test_g1_parcours_complet_puis_prete_apres_sujet_retenu(
    client, examens, redacteur, epreuve_creneau, brigade
):
    client.force_login(examens)
    lieu = Lieu.objects.create(intitule="Salle G1", capacite=30, categorie="salle_attitree")
    affecter_stagiaires(redacteur, brigade, 2)

    _post(
        client,
        "evaluations:ajouter_organisation",
        [epreuve_creneau.pk],
        {"brigade": brigade.pk, "lieu": lieu.pk, "effectif_attendu": 2},
    )
    organisation = OrganisationEpreuve.objects.get(evaluation=epreuve_creneau)
    _post(
        client,
        "evaluations:ajouter_surveillant",
        [organisation.pk],
        {"nom_libre": "Surveillant G1", "instructeur": ""},
    )

    detail = client.get(
        reverse("evaluations:organisation", args=[epreuve_creneau.pk])
    ).content.decode()
    assert "Non prête" in detail

    sujet = _enregistrer(examens, epreuve_creneau, "Pli G1")
    ServiceSujet.retenir(examens, sujet, confirmation=True)
    detail = client.get(
        reverse("evaluations:organisation", args=[epreuve_creneau.pk])
    ).content.decode()
    assert "Prête" in detail and "Non prête" not in detail


def test_g2_lieu_occupe_redirige_avec_le_nom_de_l_occupant_sans_rien_en_base(
    client, examens, redacteur, epreuve_creneau, brigade
):
    client.force_login(examens)
    lieu = Lieu.objects.create(intitule="Salle G2", capacite=30, categorie="salle_attitree")
    autre = creer_brigade(redacteur, epreuve_creneau.session, "G2-AUTRE")
    occupant = Service.ajouter_organisation(examens, epreuve_creneau, autre, lieu, 1)
    avant = OrganisationEpreuve.objects.count()

    reponse = _post(
        client,
        "evaluations:ajouter_organisation",
        [epreuve_creneau.pk],
        {"brigade": brigade.pk, "lieu": lieu.pk, "effectif_attendu": 1},
    )
    assert reponse.status_code == 302
    assert OrganisationEpreuve.objects.count() == avant
    suivi = client.get(
        reverse("evaluations:organisation", args=[epreuve_creneau.pk])
    ).content.decode()
    assert "déjà pris" in suivi or "déjà attribué" in suivi
    assert occupant.pk


def test_g3_surveillant_indisponible_refuse_sans_ecriture(
    client, examens, epreuve_creneau, brigade, instructeur
):
    client.force_login(examens)
    IndisponibiliteInstructeur.objects.create(
        instructeur=instructeur,
        debut=instant_de(epreuve_creneau.date, H8),
        fin=instant_de(epreuve_creneau.date, H10),
        motif="Stage G3",
    )
    organisation = Service.ajouter_organisation(examens, epreuve_creneau, brigade, None, 1)

    _post(
        client,
        "evaluations:ajouter_surveillant",
        [organisation.pk],
        {"instructeur": instructeur.pk, "nom_libre": ""},
    )
    assert not Surveillance.objects.filter(organisation=organisation).exists()


def test_g4_convocation_lisible_par_la_direction_sans_sujet(
    client, direction_formation, examens, epreuve_creneau, brigade
):
    organisation = Service.ajouter_organisation(examens, epreuve_creneau, brigade, None, 1)
    Service.ajouter_surveillant(examens, organisation, nom_libre="Surveillant G4")
    sujet = _enregistrer(examens, epreuve_creneau, "Pli confidentiel G4")
    ServiceSujet.retenir(examens, sujet, confirmation=True)

    client.force_login(direction_formation)
    reponse = client.get(reverse("evaluations:convocation", args=[epreuve_creneau.pk]))

    assert reponse.status_code == 200
    contenu = reponse.content.decode()
    assert "Pli confidentiel G4" not in contenu
    assert "Surveillant G4" in contenu


def test_g5_modification_apres_le_debut_refusee_sans_ecriture(
    client, examens, epreuve_creneau, brigade
):
    organisation = Service.ajouter_organisation(examens, epreuve_creneau, brigade, None, 1)
    Evaluation.objects.filter(pk=epreuve_creneau.pk).update(
        date=timezone.localdate(), heure_debut=datetime.time(0, 0), heure_fin=datetime.time(23, 59)
    )
    client.force_login(examens)

    _post(client, "evaluations:retirer_organisation", [organisation.pk])
    assert OrganisationEpreuve.objects.filter(pk=organisation.pk).exists()


def test_g6_liste_nombre_de_requetes_identique_avec_un_et_dix_epreuves(
    client, examens, session, element_referentiel
):
    from evaluations.services.evaluation import ServiceEvaluation

    client.force_login(examens)

    def _creer(decalage):
        return ServiceEvaluation.creer(
            examens,
            {
                "element_referentiel": element_referentiel,
                "type": "certificative",
                "session": session,
                "brigade": None,
                "date": timezone.localdate() + datetime.timedelta(days=decalage),
                "creneau_type": None,
                "instructeur": None,
                "lieu": None,
                "motif_date_passee": "",
            },
        )

    _creer(30)
    with CaptureQueriesContext(connection) as un:
        client.get(reverse("evaluations:liste_evaluations"))
    for indice in range(9):
        _creer(31 + indice)
    with CaptureQueriesContext(connection) as dix:
        client.get(reverse("evaluations:liste_evaluations"))

    assert len(un) == len(dix)


def test_f2_organisation_et_convocation_n_ouvrent_aucun_journal_de_consultation_de_sujet(
    client, direction_formation, examens, epreuve_creneau, brigade
):
    Service.ajouter_organisation(examens, epreuve_creneau, brigade, None, 1)
    avant = EntreeJournal.objects.filter(type_action=TypeAction.CONSULTATION_SUJETS).count()
    client.force_login(direction_formation)
    client.get(reverse("evaluations:organisation", args=[epreuve_creneau.pk]))
    client.get(reverse("evaluations:convocation", args=[epreuve_creneau.pk]))
    assert EntreeJournal.objects.filter(type_action=TypeAction.CONSULTATION_SUJETS).count() == avant


def test_f3_direction_formation_lit_et_ne_modifie_rien(
    client, direction_formation, examens, epreuve_creneau, brigade
):
    organisation = Service.ajouter_organisation(examens, epreuve_creneau, brigade, None, 1)
    client.force_login(direction_formation)

    assert (
        client.get(reverse("evaluations:organisation", args=[epreuve_creneau.pk])).status_code
        == 200
    )
    assert (
        client.get(reverse("evaluations:convocation", args=[epreuve_creneau.pk])).status_code == 200
    )
    reponse = client.post(reverse("evaluations:retirer_organisation", args=[organisation.pk]))
    assert reponse.status_code == 403
    assert OrganisationEpreuve.objects.filter(pk=organisation.pk).exists()


def test_h2_un_get_sur_une_ecriture_repond_405_et_ne_supprime_rien(
    client, examens, epreuve_creneau, brigade
):
    organisation = Service.ajouter_organisation(examens, epreuve_creneau, brigade, None, 1)
    surveillance = Service.ajouter_surveillant(examens, organisation, nom_libre="Surveillant H2")
    client.force_login(examens)

    assert (
        client.get(reverse("evaluations:retirer_organisation", args=[organisation.pk])).status_code
        == 405
    )
    assert (
        client.get(reverse("evaluations:retirer_surveillant", args=[surveillance.pk])).status_code
        == 405
    )
    assert OrganisationEpreuve.objects.filter(pk=organisation.pk).exists()
    assert Surveillance.objects.filter(pk=surveillance.pk).exists()


def test_f1_la_convocation_ne_consulte_aucune_requete_sur_les_sujets(
    client, direction_formation, examens, epreuve_creneau, brigade
):
    from django.db import connection
    from django.test.utils import CaptureQueriesContext

    organisation = Service.ajouter_organisation(examens, epreuve_creneau, brigade, None, 1)
    Service.ajouter_surveillant(examens, organisation, nom_libre="Surveillant F1")
    sujet = _enregistrer(examens, epreuve_creneau, "Pli F1")
    ServiceSujet.retenir(examens, sujet, confirmation=True)

    client.force_login(direction_formation)
    with CaptureQueriesContext(connection) as capture:
        reponse = client.get(reverse("evaluations:convocation", args=[epreuve_creneau.pk]))

    assert reponse.status_code == 200
    assert not [q for q in capture.captured_queries if "evaluations_sujet" in q["sql"]]
    assert "Pli F1" not in reponse.content.decode()
