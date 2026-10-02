"""US-EVAL-02, bloc A — projection de la date certificative (A1) et nouvelle
source de RG-38 (A3), par le contexte réel de `ServiceContraintes`."""

import datetime

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from evaluations.services.evaluation import ServiceEvaluation
from evaluations.tests.conftest import creer_brigade
from planification.models import ProgrammeHebdomadaire, Seance
from planification.services.contraintes import Candidate, ServiceContraintes
from planification.services.generation import ServiceGeneration
from ressources.models import PeriodeCalendrier


def _certificative(examens, element_referentiel, jour, *, session=None, brigade=None):
    donnees = {
        "element_referentiel": element_referentiel,
        "type": "certificative",
        "session": session,
        "brigade": brigade,
        "date": jour,
        "creneau_type": None,
        "instructeur": None,
        "lieu": None,
        "motif_date_passee": "",
    }
    return ServiceEvaluation.creer(examens, donnees)


def _candidate_du_jour(controle):
    jour_creneau = controle.jour_creneau
    debut = timezone.make_aware(
        datetime.datetime.combine(jour_creneau.jour, jour_creneau.creneau.heure_debut)
    )
    fin = timezone.make_aware(
        datetime.datetime.combine(jour_creneau.jour, jour_creneau.creneau.heure_fin)
    )
    return Candidate(
        brigade=controle.brigade,
        element_referentiel=controle.element_referentiel,
        instructeur=controle.instructeur,
        debut=debut,
        fin=fin,
    )


def _programme_de(jour):
    lundi = jour - datetime.timedelta(days=jour.weekday())
    return ProgrammeHebdomadaire.objects.create(lundi_de_semaine=lundi)


def test_a1_certificative_brigade_rg38_refuse_candidate_meme_jour(controle):
    _certificative(
        controle.examens,
        controle.element_referentiel,
        controle.jour_creneau.jour,
        brigade=controle.brigade,
    )
    programme = _programme_de(controle.jour_creneau.jour)
    contexte = ServiceContraintes.contexte(programme)
    verdict = ServiceContraintes.verifier(_candidate_du_jour(controle), contexte)
    assert not verdict.accepte
    assert any(v["code"] == "RG-38" for v in verdict.violations)
    assert any("examen" in v["message"].lower() for v in verdict.violations)


def test_a2_meme_jour_autre_brigade_de_la_meme_session_acceptee(controle, redacteur, session):
    _certificative(
        controle.examens,
        controle.element_referentiel,
        controle.jour_creneau.jour,
        brigade=controle.brigade,
    )
    autre_brigade = creer_brigade(redacteur, session, "EXP2")
    programme = _programme_de(controle.jour_creneau.jour)
    contexte = ServiceContraintes.contexte(programme)
    jour_creneau = controle.jour_creneau
    debut = timezone.make_aware(
        datetime.datetime.combine(jour_creneau.jour, jour_creneau.creneau.heure_debut)
    )
    fin = timezone.make_aware(
        datetime.datetime.combine(jour_creneau.jour, jour_creneau.creneau.heure_fin)
    )
    candidate = Candidate(
        brigade=autre_brigade,
        element_referentiel=controle.element_referentiel,
        instructeur=controle.instructeur,
        debut=debut,
        fin=fin,
    )
    verdict = ServiceContraintes.verifier(candidate, contexte)
    assert verdict.accepte


def test_a3_perimetre_session_toutes_les_brigades_fermees_aucune_autre(
    controle, redacteur, session
):
    brigade2 = creer_brigade(redacteur, session, "EXP2")
    _certificative(
        controle.examens, controle.element_referentiel, controle.jour_creneau.jour, session=session
    )
    programme = _programme_de(controle.jour_creneau.jour)
    contexte = ServiceContraintes.contexte(programme)
    jour_creneau = controle.jour_creneau
    debut = timezone.make_aware(
        datetime.datetime.combine(jour_creneau.jour, jour_creneau.creneau.heure_debut)
    )
    fin = timezone.make_aware(
        datetime.datetime.combine(jour_creneau.jour, jour_creneau.creneau.heure_fin)
    )
    for brigade in (controle.brigade, brigade2):
        candidate = Candidate(
            brigade=brigade,
            element_referentiel=controle.element_referentiel,
            instructeur=controle.instructeur,
            debut=debut,
            fin=fin,
        )
        verdict = ServiceContraintes.verifier(candidate, contexte)
        assert not verdict.accepte


def test_a4_brigade_constituee_apres_la_saisie_est_fermee_aussi(controle, redacteur, session):
    _certificative(
        controle.examens, controle.element_referentiel, controle.jour_creneau.jour, session=session
    )
    brigade_tardive = creer_brigade(redacteur, session, "EXP-TARDIVE")
    programme = _programme_de(controle.jour_creneau.jour)
    contexte = ServiceContraintes.contexte(programme)
    jour_creneau = controle.jour_creneau
    debut = timezone.make_aware(
        datetime.datetime.combine(jour_creneau.jour, jour_creneau.creneau.heure_debut)
    )
    fin = timezone.make_aware(
        datetime.datetime.combine(jour_creneau.jour, jour_creneau.creneau.heure_fin)
    )
    candidate = Candidate(
        brigade=brigade_tardive,
        element_referentiel=controle.element_referentiel,
        instructeur=controle.instructeur,
        debut=debut,
        fin=fin,
    )
    verdict = ServiceContraintes.verifier(candidate, contexte)
    assert not verdict.accepte


def test_a5_generation_sur_la_semaine_aucune_seance_a_j_autres_jours_remplis(
    controle, planificateur
):
    jour = controle.jour_creneau.jour
    _certificative(controle.examens, controle.element_referentiel, jour, brigade=controle.brigade)
    lundi = jour - datetime.timedelta(days=jour.weekday())
    compte_rendu = ServiceGeneration.generer(planificateur, lundi, [controle.brigade])
    seances = Seance.objects.filter(lignes__brigade=controle.brigade)
    assert not seances.filter(debut__date=jour).exists()
    assert compte_rendu is not None


def test_a6_modification_j_vers_j_prime_j_rouvert_j_prime_ferme(controle, redacteur, session):
    jour = controle.jour_creneau.jour
    evaluation = _certificative(
        controle.examens, controle.element_referentiel, jour, brigade=controle.brigade
    )
    jour_prime = jour + datetime.timedelta(days=1)
    ServiceEvaluation.modifier_date_certificative(
        controle.examens, evaluation, jour_prime, "Report notifié par le 3e bureau."
    )
    programme = _programme_de(jour)
    contexte = ServiceContraintes.contexte(programme)
    debut_j = timezone.make_aware(datetime.datetime.combine(jour, datetime.time(8, 0)))
    fin_j = debut_j + datetime.timedelta(hours=1, minutes=45)
    candidate_j = Candidate(
        brigade=controle.brigade,
        element_referentiel=controle.element_referentiel,
        instructeur=controle.instructeur,
        debut=debut_j,
        fin=fin_j,
    )
    assert ServiceContraintes.verifier(candidate_j, contexte).accepte
    debut_jp = timezone.make_aware(datetime.datetime.combine(jour_prime, datetime.time(8, 0)))
    fin_jp = debut_jp + datetime.timedelta(hours=1, minutes=45)
    candidate_jp = Candidate(
        brigade=controle.brigade,
        element_referentiel=controle.element_referentiel,
        instructeur=controle.instructeur,
        debut=debut_jp,
        fin=fin_jp,
    )
    assert not ServiceContraintes.verifier(candidate_jp, contexte).accepte


def test_a7_aucune_periode_calendrier_creee_par_la_saisie_ni_la_modification(controle):
    avant = PeriodeCalendrier.objects.count()
    evaluation = _certificative(
        controle.examens,
        controle.element_referentiel,
        controle.jour_creneau.jour,
        brigade=controle.brigade,
    )
    ServiceEvaluation.modifier_date_certificative(
        controle.examens,
        evaluation,
        controle.jour_creneau.jour + datetime.timedelta(days=1),
        "Report notifié par le 3e bureau.",
    )
    assert PeriodeCalendrier.objects.count() == avant


def test_a8_sans_fournisseur_installe_liste_vide_service_contraintes_fonctionne(
    monkeypatch, controle
):
    from noyau.services.parametres import ResolveurJoursExamen

    _certificative(
        controle.examens,
        controle.element_referentiel,
        controle.jour_creneau.jour,
        brigade=controle.brigade,
    )
    monkeypatch.setattr(ResolveurJoursExamen, "_fournisseur", None)
    programme = _programme_de(controle.jour_creneau.jour)
    contexte = ServiceContraintes.contexte(programme)
    assert contexte.jours_examen == []
    verdict = ServiceContraintes.verifier(_candidate_du_jour(controle), contexte)
    assert verdict.accepte


def test_f1_requetes_verifier_lot_identiques_0_et_10_examens(redacteur, session, controle):
    programme = _programme_de(controle.jour_creneau.jour)
    for i in range(10):
        brigade = creer_brigade(redacteur, session, f"F1-{i}")
        _certificative(
            controle.examens,
            controle.element_referentiel,
            controle.jour_creneau.jour + datetime.timedelta(days=1),
            brigade=brigade,
        )
    with CaptureQueriesContext(connection) as avec_dix:
        contexte = ServiceContraintes.contexte(programme)
        ServiceContraintes.verifier_lot([_candidate_du_jour(controle)], contexte)

    from evaluations.models import Evaluation

    Evaluation.objects.all().delete()
    with CaptureQueriesContext(connection) as sans_examen:
        contexte = ServiceContraintes.contexte(programme)
        ServiceContraintes.verifier_lot([_candidate_du_jour(controle)], contexte)

    assert len(avec_dix.captured_queries) == len(sans_examen.captured_queries)
