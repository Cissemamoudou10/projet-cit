"""US-EVAL-02, bloc E — cycle HTTP réel pour la date d'un examen final."""

import datetime

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from evaluations.services.evaluation import ServiceEvaluation
from evaluations.tests.conftest import creer_brigade


def _certificative(examens, element_referentiel, brigade, jours=30, date=None):
    """`date` l'emporte sur `jours` quand fourni — P-43 : un appelant qui a
    besoin d'une date dans un mois précis (test_e4, lié au calendrier) ne
    doit jamais la faire dépendre de `timezone.localdate()`, seule source
    de dérive une fois une borne de mois franchie depuis l'écriture du test."""
    donnees = {
        "element_referentiel": element_referentiel,
        "type": "certificative",
        "session": None,
        "brigade": brigade,
        "date": date or timezone.localdate() + datetime.timedelta(days=jours),
        "creneau_type": None,
        "instructeur": None,
        "lieu": None,
        "motif_date_passee": "",
    }
    return ServiceEvaluation.creer(examens, donnees)


def test_e1_post_modification_redirection_date_affichee_imposee(client, controle):
    evaluation = _certificative(controle.examens, controle.element_referentiel, controle.brigade)
    nouvelle_date = evaluation.date + datetime.timedelta(days=5)
    client.force_login(controle.examens)
    reponse = client.post(
        reverse("evaluations:modifier_date_certificative", args=[evaluation.pk]),
        {"nouvelle_date": nouvelle_date.isoformat(), "motif": "Report notifié par le 3e bureau."},
    )
    assert reponse.status_code == 302
    assert reponse.url == reverse("evaluations:detail_evaluation", args=[evaluation.pk])
    suivi = client.get(reponse.url)
    contenu = suivi.content.decode()
    assert nouvelle_date.strftime("%d/%m/%Y") in contenu
    assert "imposée" in contenu.lower()


def test_e2_post_sans_motif_reaffiche_rien_change_en_base(client, controle):
    evaluation = _certificative(controle.examens, controle.element_referentiel, controle.brigade)
    ancienne_date = evaluation.date
    client.force_login(controle.examens)
    reponse = client.post(
        reverse("evaluations:modifier_date_certificative", args=[evaluation.pk]),
        {"nouvelle_date": (ancienne_date + datetime.timedelta(days=1)).isoformat(), "motif": ""},
    )
    assert reponse.status_code == 200
    evaluation.refresh_from_db()
    assert evaluation.date == ancienne_date


def test_e3_post_creation_jour_occupe_redirection_avertissement_affiche(
    client, controle, redacteur, session
):
    from planification.models import LigneProgramme, ProgrammeHebdomadaire, Seance

    jour = controle.jour_creneau.jour
    lundi = jour - datetime.timedelta(days=jour.weekday())
    programme = ProgrammeHebdomadaire.objects.create(lundi_de_semaine=lundi)
    debut = timezone.make_aware(datetime.datetime.combine(jour, datetime.time(8, 0)))
    seance = Seance.objects.create(
        programme=programme,
        element_referentiel=controle.element_referentiel,
        instructeur=controle.instructeur,
        debut=debut,
        fin=debut + datetime.timedelta(hours=1, minutes=45),
        verrouillee=False,
    )
    LigneProgramme.objects.create(seance=seance, brigade=controle.brigade)

    client.force_login(controle.examens)
    reponse = client.post(
        reverse("evaluations:creer_evaluation"),
        {
            "element_referentiel": controle.element_referentiel.pk,
            "type": "certificative",
            "session": "",
            "brigade": controle.brigade.pk,
            "date": jour.isoformat(),
            "creneau_type": "",
            "instructeur": "",
            "lieu": "",
            "motif_date_passee": "",
        },
    )
    assert reponse.status_code == 302
    suivi = client.get(reponse.url)
    assert "programme" in suivi.content.decode().lower()


def test_e4_vue_annuelle_et_mensuelle_jour_d_examen_affiche_requetes_stables(
    client, planificateur, controle, redacteur, session
):
    """P-43 : la date de l'examen doit tomber dans le même mois que `jour`,
    celui qu'interroge `url_mensuel` — jamais dérivée de `timezone.
    localdate()` (`jours=`), qui peut tomber dans un autre mois que `jour`
    une fois une borne de mois franchie entre l'écriture du test et son
    exécution (`jour` vient de `lundi_semaine`, toujours 14 à 20 jours dans
    le futur ; +5 jours depuis aujourd'hui ne l'est pas forcément)."""
    jour = controle.jour_creneau.jour
    annee_formation = jour.year if jour.month >= 9 else jour.year - 1
    url_mensuel = reverse("ressources:calendrier_mensuel") + f"?annee={jour.year}&mois={jour.month}"
    url_annuel = reverse("ressources:calendrier_annuel") + f"?annee={annee_formation}"
    client.force_login(planificateur)

    _certificative(controle.examens, controle.element_referentiel, controle.brigade, date=jour)
    with CaptureQueriesContext(connection) as mensuel_un:
        reponse_mensuel = client.get(url_mensuel)
    assert reponse_mensuel.status_code == 200
    assert "Examen final" in reponse_mensuel.content.decode()

    for i in range(9):
        brigade_i = creer_brigade(redacteur, session, f"E4-{i}")
        _certificative(controle.examens, controle.element_referentiel, brigade_i, date=jour)
    with CaptureQueriesContext(connection) as mensuel_dix:
        reponse_dix = client.get(url_mensuel)
    assert reponse_dix.status_code == 200
    assert len(mensuel_un.captured_queries) == len(mensuel_dix.captured_queries)

    reponse_annuel = client.get(url_annuel)
    assert reponse_annuel.status_code == 200
    assert "EXAMEN" in reponse_annuel.content.decode()


def test_e5_post_modification_par_planification_403_date_inchangee(client, planificateur, controle):
    evaluation = _certificative(controle.examens, controle.element_referentiel, controle.brigade)
    ancienne_date = evaluation.date
    client.force_login(planificateur)
    reponse = client.post(
        reverse("evaluations:modifier_date_certificative", args=[evaluation.pk]),
        {
            "nouvelle_date": (ancienne_date + datetime.timedelta(days=1)).isoformat(),
            "motif": "Report notifié par le 3e bureau.",
        },
    )
    assert reponse.status_code == 403
    evaluation.refresh_from_db()
    assert evaluation.date == ancienne_date
