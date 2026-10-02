"""US-EVAL-02, bloc C — signalement des séances recouvertes (A7), jamais une
suppression (C3 : la date s'enregistre quoi qu'il arrive)."""

import datetime

from django.utils import timezone

from evaluations.services.evaluation import ServiceEvaluation
from evaluations.tests.conftest import creer_brigade
from planification.models import ProgrammeHebdomadaire, Seance


def _programme_et_deux_seances(controle, brigade=None):
    brigade = brigade or controle.brigade
    jour = controle.jour_creneau.jour
    lundi = jour - datetime.timedelta(days=jour.weekday())
    programme = ProgrammeHebdomadaire.objects.create(lundi_de_semaine=lundi)
    debut1 = timezone.make_aware(datetime.datetime.combine(jour, datetime.time(8, 0)))
    seance1 = Seance.objects.create(
        programme=programme,
        element_referentiel=controle.element_referentiel,
        instructeur=controle.instructeur,
        debut=debut1,
        fin=debut1 + datetime.timedelta(hours=1, minutes=45),
        verrouillee=False,
    )
    debut2 = timezone.make_aware(datetime.datetime.combine(jour, datetime.time(10, 10)))
    seance2 = Seance.objects.create(
        programme=programme,
        element_referentiel=controle.element_referentiel,
        instructeur=controle.instructeur,
        debut=debut2,
        fin=debut2 + datetime.timedelta(hours=1, minutes=50),
        verrouillee=False,
    )
    from planification.models import LigneProgramme

    LigneProgramme.objects.create(seance=seance1, brigade=brigade)
    LigneProgramme.objects.create(seance=seance2, brigade=brigade)
    return seance1, seance2


def test_c1_creation_certificative_seances_existantes_enumerees_avec_etat(controle):
    seance1, seance2 = _programme_et_deux_seances(controle)
    donnees = {
        "element_referentiel": controle.element_referentiel,
        "type": "certificative",
        "session": None,
        "brigade": controle.brigade,
        "date": controle.jour_creneau.jour,
        "creneau_type": None,
        "instructeur": None,
        "lieu": None,
        "motif_date_passee": "",
    }
    evaluation = ServiceEvaluation.creer(controle.examens, donnees)
    assert evaluation.pk is not None
    assert evaluation.avertissements
    message = evaluation.avertissements[0]["message"]
    assert "programme" in message.lower()
    assert str(seance1.element_referentiel.matiere) in message
    assert str(seance2.element_referentiel.matiere) in message


def test_c2_aucune_seance_supprimee_ni_modifiee(controle):
    seance1, seance2 = _programme_et_deux_seances(controle)
    debut1_avant, debut2_avant = seance1.debut, seance2.debut
    donnees = {
        "element_referentiel": controle.element_referentiel,
        "type": "certificative",
        "session": None,
        "brigade": controle.brigade,
        "date": controle.jour_creneau.jour,
        "creneau_type": None,
        "instructeur": None,
        "lieu": None,
        "motif_date_passee": "",
    }
    avant = Seance.objects.count()
    ServiceEvaluation.creer(controle.examens, donnees)
    assert Seance.objects.count() == avant
    seance1.refresh_from_db()
    seance2.refresh_from_db()
    assert seance1.debut == debut1_avant
    assert seance2.debut == debut2_avant


def test_c3_modification_vers_jour_occupe_meme_signalement(controle):
    jour_initial = controle.jour_creneau.jour
    evaluation = ServiceEvaluation.creer(
        controle.examens,
        {
            "element_referentiel": controle.element_referentiel,
            "type": "certificative",
            "session": None,
            "brigade": controle.brigade,
            "date": jour_initial + datetime.timedelta(days=10),
            "creneau_type": None,
            "instructeur": None,
            "lieu": None,
            "motif_date_passee": "",
        },
    )
    _programme_et_deux_seances(controle)
    evaluation = ServiceEvaluation.modifier_date_certificative(
        controle.examens, evaluation, jour_initial, "Report notifié par le 3e bureau."
    )
    assert evaluation.avertissements


def test_c4_seance_d_une_brigade_hors_perimetre_non_enumeree(controle, redacteur, session):
    autre_brigade = creer_brigade(redacteur, session, "HORS-PERIMETRE")
    _programme_et_deux_seances(controle, brigade=autre_brigade)
    donnees = {
        "element_referentiel": controle.element_referentiel,
        "type": "certificative",
        "session": None,
        "brigade": controle.brigade,
        "date": controle.jour_creneau.jour,
        "creneau_type": None,
        "instructeur": None,
        "lieu": None,
        "motif_date_passee": "",
    }
    evaluation = ServiceEvaluation.creer(controle.examens, donnees)
    assert evaluation.avertissements == []
