"""US-EVAL-01, bloc E — cycle HTTP réel (leçon D-50) : `reverse()` et le
client de test, jamais un appel direct au service pour ces cas-là."""

import datetime

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from evaluations.models import Evaluation, TypeEvaluation
from evaluations.tests.conftest import creer_brigade
from planification.models import LigneProgramme, Seance
from planification.models import ProgrammeHebdomadaire as Programme


def _donnees_certificative(element_referentiel, session, jours=30):
    return {
        "element_referentiel": element_referentiel.pk,
        "type": "certificative",
        "session": session.pk,
        "brigade": "",
        "date": (timezone.localdate() + datetime.timedelta(days=jours)).isoformat(),
        "creneau_type": "",
        "instructeur": "",
        "lieu": "",
        "motif_date_passee": "",
    }


def _donnees_formative_future(element_referentiel, brigade, jour_creneau, instructeur):
    return {
        "element_referentiel": element_referentiel.pk,
        "type": "formative",
        "session": "",
        "brigade": brigade.pk,
        "date": jour_creneau.jour.isoformat(),
        "creneau_type": jour_creneau.creneau.pk,
        "instructeur": instructeur.pk,
        "lieu": "",
        "motif_date_passee": "",
    }


def test_e1_post_formative_future_redirection_seance_au_programme(client, controle):
    client.force_login(controle.examens)
    reponse = client.post(
        reverse("evaluations:creer_evaluation"),
        _donnees_formative_future(
            controle.element_referentiel,
            controle.brigade,
            controle.jour_creneau,
            controle.instructeur,
        ),
    )
    evaluation = Evaluation.objects.get()
    assert reponse.status_code == 302
    assert reponse.url == reverse("evaluations:detail_evaluation", args=[evaluation.pk])
    assert evaluation.seance_id is not None
    lundi = controle.jour_creneau.jour - datetime.timedelta(
        days=controle.jour_creneau.jour.weekday()
    )
    assert evaluation.seance.programme.lundi_de_semaine == lundi


def _dix_seances(redacteur, session, controle):
    jour_creneau = controle.jour_creneau
    lundi = jour_creneau.jour - datetime.timedelta(days=jour_creneau.jour.weekday())
    programme = Programme.objects.create(lundi_de_semaine=lundi)
    debut = timezone.make_aware(
        datetime.datetime.combine(jour_creneau.jour, jour_creneau.creneau.heure_debut)
    )
    fin = timezone.make_aware(
        datetime.datetime.combine(jour_creneau.jour, jour_creneau.creneau.heure_fin)
    )
    paires = []
    for i in range(10):
        brigade_i = creer_brigade(redacteur, session, f"E2-{i}", effectif=10)
        seance = Seance.objects.create(
            programme=programme,
            element_referentiel=controle.element_referentiel,
            instructeur=controle.instructeur,
            debut=debut,
            fin=fin,
            verrouillee=True,
        )
        LigneProgramme.objects.create(seance=seance, brigade=brigade_i)
        paires.append((brigade_i, seance))
    return paires, lundi


def test_e2_consultation_programme_marque_controle_nombre_requetes_stable(
    client, planificateur, redacteur, session, controle
):
    paires, lundi = _dix_seances(redacteur, session, controle)
    url = (
        reverse("planification:consultation_programme") + f"?semaine={lundi.isoformat()}&jour=lundi"
    )
    client.force_login(planificateur)

    Evaluation.objects.create(
        element_referentiel=controle.element_referentiel,
        brigade=paires[0][0],
        seance=paires[0][1],
        type=TypeEvaluation.FORMATIVE,
    )
    with CaptureQueriesContext(connection) as captees_une:
        reponse_une = client.get(url)
    assert reponse_une.status_code == 200
    assert "Contrôle" in reponse_une.content.decode()

    for brigade_i, seance_i in paires[1:]:
        Evaluation.objects.create(
            element_referentiel=controle.element_referentiel,
            brigade=brigade_i,
            seance=seance_i,
            type=TypeEvaluation.FORMATIVE,
        )
    with CaptureQueriesContext(connection) as captees_dix:
        reponse_dix = client.get(url)
    assert reponse_dix.status_code == 200
    assert len(captees_une.captured_queries) == len(captees_dix.captured_queries)


def test_e3_post_formative_date_passee_sans_motif_reaffiche_rien_en_base(
    client, examens, brigade, element_referentiel
):
    client.force_login(examens)
    donnees = {
        "element_referentiel": element_referentiel.pk,
        "type": "formative",
        "session": "",
        "brigade": brigade.pk,
        "date": (timezone.localdate() - datetime.timedelta(days=1)).isoformat(),
        "creneau_type": "",
        "instructeur": "",
        "lieu": "",
        "motif_date_passee": "",
    }
    reponse = client.post(reverse("evaluations:creer_evaluation"), donnees)
    assert reponse.status_code == 200
    assert "motif" in reponse.content.decode().lower()
    assert Evaluation.objects.count() == 0


def test_e4_post_controle_sur_creneau_occupe_reaffiche_le_motif_rien_en_base(
    client, controle, redacteur, session
):
    from evaluations.services.evaluation import ServiceEvaluation

    brigade2 = creer_brigade(redacteur, session, "EXP2")
    ServiceEvaluation.creer(
        controle.examens,
        {
            "element_referentiel": controle.element_referentiel,
            "type": TypeEvaluation.FORMATIVE,
            "session": None,
            "brigade": controle.brigade,
            "date": controle.jour_creneau.jour,
            "creneau_type": controle.jour_creneau.creneau,
            "instructeur": controle.instructeur,
            "lieu": None,
            "motif_date_passee": "",
        },
    )
    client.force_login(controle.examens)
    reponse = client.post(
        reverse("evaluations:creer_evaluation"),
        _donnees_formative_future(
            controle.element_referentiel, brigade2, controle.jour_creneau, controle.instructeur
        ),
    )
    assert reponse.status_code == 200
    assert "RG-34" in reponse.content.decode()
    assert Evaluation.objects.count() == 1
    assert Seance.objects.count() == 1


def test_e5_post_creation_par_planification_403_rien_en_base(
    client, planificateur, brigade, element_referentiel
):
    client.force_login(planificateur)
    reponse = client.post(
        reverse("evaluations:creer_evaluation"),
        _donnees_certificative(element_referentiel, brigade.session),
    )
    assert reponse.status_code == 403
    assert Evaluation.objects.count() == 0


def test_e6_formulaire_aucun_troisieme_type_propose(client, examens):
    client.force_login(examens)
    reponse = client.get(reverse("evaluations:creer_evaluation"))
    formulaire = reponse.context["form"]
    valeurs = {valeur for valeur, _ in formulaire.fields["type"].choices}
    assert valeurs == {"formative", "certificative"}
