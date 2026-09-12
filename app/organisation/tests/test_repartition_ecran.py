"""US-SES-06 — cycle HTTP réel de l'écran de répartition (Prompt 25, § 12,
Groupe F). Le refus d'habilitation exhaustif et le test de garde mécanique
sont couverts une fois pour toutes par
tests/architecture/test_ecrans_ecriture.py — non dupliqués ici pour chaque
adresse. Données entièrement fictives.
"""

import datetime

import pytest
from django.urls import reverse

from organisation.models import AffectationBrigade
from organisation.services.affectation import ServiceAffectation
from organisation.services.brigade import ServiceBrigade
from organisation.services.stagiaire import ServiceStagiaire
from organisation.tests.conftest import donnees_brigade, donnees_stagiaire


def _creer_stagiaires(redacteur, session, nombre):
    return [
        ServiceStagiaire.creer(
            redacteur, session, donnees_stagiaire(matricule=f"M{i:03d}", nom=f"Nom{i:03d}")
        )
        for i in range(nombre)
    ]


# --- F1 — chemin nominal sur chaque adresse d'écriture ---------------------


def test_f1_proposer_par_l_ecran_produit_une_proposition_sans_ecriture(
    client, redacteur, session, brigade
):
    _creer_stagiaires(redacteur, session, 5)
    client.force_login(redacteur)

    reponse = client.post(reverse("organisation:proposer_repartition", args=[session.pk]))

    assert reponse.status_code == 200
    assert AffectationBrigade.objects.count() == 0


def test_f1_affecter_par_l_ecran_cree_reellement_l_affectation(
    client, redacteur, session, stagiaire, brigade
):
    client.force_login(redacteur)

    reponse = client.post(
        reverse("organisation:affecter_stagiaire", args=[session.pk, stagiaire.pk]),
        {"brigade_id": brigade.pk},
    )

    assert reponse.status_code == 302
    assert AffectationBrigade.objects.filter(stagiaire=stagiaire, brigade=brigade).exists()


def test_f1_deplacer_par_l_ecran_deplace_reellement(client, redacteur, session, stagiaire, brigade):
    autre_brigade = ServiceBrigade.creer(redacteur, session, donnees_brigade(designation="EXP2"))
    ServiceAffectation.affecter(redacteur, stagiaire, brigade, date_effet=datetime.date(2026, 1, 1))
    client.force_login(redacteur)

    reponse = client.post(
        reverse("organisation:deplacer_stagiaire", args=[session.pk, stagiaire.pk]),
        {"brigade": autre_brigade.pk, "date_effet": "2026-02-01"},
    )

    assert reponse.status_code == 302
    assert ServiceAffectation.affectation_ouverte(stagiaire).brigade == autre_brigade


def test_f1_retirer_par_l_ecran_retire_reellement(client, redacteur, session, stagiaire, brigade):
    ServiceAffectation.affecter(redacteur, stagiaire, brigade, date_effet=datetime.date(2026, 1, 1))
    client.force_login(redacteur)

    reponse = client.post(
        reverse("organisation:retirer_affectation", args=[session.pk, stagiaire.pk]),
        {"date_fin": "2026-02-01"},
    )

    assert reponse.status_code == 302
    assert ServiceAffectation.affectation_ouverte(stagiaire) is None


def test_f1_valider_par_l_ecran_enregistre_reellement(client, redacteur, session, brigade):
    _creer_stagiaires(redacteur, session, 3)
    client.force_login(redacteur)
    reponse_proposition = client.post(
        reverse("organisation:proposer_repartition", args=[session.pk])
    )
    proposition_b64 = reponse_proposition.context["proposition_b64"]

    reponse = client.post(
        reverse("organisation:valider_repartition", args=[session.pk]),
        {"proposition_b64": proposition_b64},
    )

    assert reponse.status_code == 302
    assert AffectationBrigade.objects.count() == 3


def test_avertissement_identique_repete_n_fois_affiche_une_seule_fois(client, redacteur, session):
    """Découvert en vérification navigateur (§ 11, Prompt 25) : sans
    déduplication, une brigade sans salle attitrée produisait un
    avertissement identique par stagiaire proposé (58 messages pour 58
    stagiaires) — inexploitable à l'écran."""
    _creer_stagiaires(redacteur, session, 5)
    ServiceBrigade.creer(redacteur, session, donnees_brigade(effectif_previsionnel=5))
    client.force_login(redacteur)
    reponse_proposition = client.post(reverse("organisation:proposer_repartition", args=[session.pk]))
    proposition_b64 = reponse_proposition.context["proposition_b64"]

    reponse = client.post(
        reverse("organisation:valider_repartition", args=[session.pk]),
        {"proposition_b64": proposition_b64},
        follow=True,
    )

    textes_avertissement = [str(m) for m in reponse.context["messages"] if m.tags == "warning"]
    assert textes_avertissement.count("« EXP1 » n'a pas encore de salle attitrée : le contrôle "
                                       "de capacité (RG-19) ne peut pas s'appliquer.") == 1


# --- F2 — parcours complet par le vrai cycle --------------------------------


def test_f2_parcours_complet_get_proposer_ajuster_valider_affectations_en_base(
    client, redacteur, session
):
    stagiaires = _creer_stagiaires(redacteur, session, 2)
    ServiceBrigade.creer(redacteur, session, donnees_brigade(designation="EXP1"))
    brigade_2 = ServiceBrigade.creer(redacteur, session, donnees_brigade(designation="EXP2"))
    client.force_login(redacteur)

    reponse_get = client.get(reverse("organisation:repartition_session", args=[session.pk]))
    assert reponse_get.status_code == 200

    reponse_proposition = client.post(
        reverse("organisation:proposer_repartition", args=[session.pk])
    )
    proposition_b64 = reponse_proposition.context["proposition_b64"]

    reponse_ajustement = client.post(
        reverse("organisation:ajuster_repartition", args=[session.pk]),
        {
            "proposition_b64": proposition_b64,
            "stagiaire_id": stagiaires[0].pk,
            "brigade_id": brigade_2.pk,
        },
    )
    assert reponse_ajustement.status_code == 200
    proposition_ajustee_b64 = reponse_ajustement.context["proposition_b64"]

    reponse_validation = client.post(
        reverse("organisation:valider_repartition", args=[session.pk]),
        {"proposition_b64": proposition_ajustee_b64},
    )

    assert reponse_validation.status_code == 302
    assert AffectationBrigade.objects.filter(stagiaire=stagiaires[0], brigade=brigade_2).exists()
    assert AffectationBrigade.objects.count() == 2


# --- F3 — les trois nombres réellement présents sur l'écran ----------------


def test_f3_effectif_reel_declare_capacite_presents_sur_l_ecran_de_repartition(
    client, redacteur, session, brigade
):
    client.force_login(redacteur)

    reponse = client.get(reverse("organisation:repartition_session", args=[session.pk]))
    contenu = reponse.content.decode()

    assert "effectif réel 0" in contenu.lower()
    assert f"déclaré {brigade.effectif_previsionnel}" in contenu


# --- F5 — refus représentatif d'habilitation --------------------------------


def test_f5_planification_ne_peut_pas_valider_la_repartition(client, planificateur, session):
    client.force_login(planificateur)

    reponse = client.post(
        reverse("organisation:valider_repartition", args=[session.pk]), {"proposition_b64": ""}
    )

    assert reponse.status_code == 403


# --- F6 — lecture accordée aux quatre profils, refusée à l'administrateur --


@pytest.mark.parametrize(
    "nom_utilisateur", ["redacteur", "lecteur", "planificateur", "direction_formation"]
)
def test_f6_lecture_accordee_aux_quatre_profils_habilites(
    client, request, session, nom_utilisateur
):
    client.force_login(request.getfixturevalue(nom_utilisateur))

    reponse = client.get(reverse("organisation:repartition_session", args=[session.pk]))

    assert reponse.status_code == 200


def test_f6_lecture_refusee_a_l_administrateur(client, administrateur, session):
    client.force_login(administrateur)

    reponse = client.get(reverse("organisation:repartition_session", args=[session.pk]))

    assert reponse.status_code == 403


# --- F8 — navigation depuis la fiche de session -----------------------------


def test_f8_lien_repartition_present_pour_pedagogique_absent_pour_lecture_seule(
    client, redacteur, lecteur, session
):
    client.force_login(redacteur)
    reponse_ecriture = client.get(reverse("organisation:detail_session", args=[session.pk]))
    assert (
        reverse("organisation:repartition_session", args=[session.pk])
        in reponse_ecriture.content.decode()
    )

    client.force_login(lecteur)
    reponse_lecture = client.get(reverse("organisation:detail_session", args=[session.pk]))
    assert (
        reverse("organisation:repartition_session", args=[session.pk])
        not in reponse_lecture.content.decode()
    )
