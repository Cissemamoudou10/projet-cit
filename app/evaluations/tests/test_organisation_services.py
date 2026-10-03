"""US-EVAL-04 — services d'organisation : règles (bloc B), disponibilité P6 → P5
(bloc C), changement de date (bloc E). Prompt 38. Données entièrement fictives.
"""

import datetime

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from evaluations.models import Evaluation, OrganisationEpreuve, Surveillance
from evaluations.services.conflits import conflits
from evaluations.services.evaluation import ServiceEvaluation
from evaluations.services.organisation import ServiceOrganisationEpreuve as Service
from evaluations.services.organisation_lecture import LectureOrganisationEpreuve
from evaluations.services.sujet import ServiceSujet
from evaluations.tests.conftest import _enregistrer, affecter_stagiaires, creer_brigade
from noyau.exceptions import ErreurValidation
from noyau.intervalles import instant_de
from planification.models import ProgrammeHebdomadaire, Seance
from ressources.models import IndisponibiliteInstructeur, IndisponibiliteLieu, Lieu

H8, H10 = datetime.time(8, 0), datetime.time(10, 0)


@pytest.fixture
def epreuve(certificative, examens):
    """Certificative datée (dans 30 jours) au créneau 8 h – 10 h."""
    return Service.fixer_creneau(examens, certificative, H8, H10)


@pytest.fixture
def salle(db):
    return Lieu.objects.create(
        intitule="Salle organisation", capacite=30, categorie="salle_attitree"
    )


def _organiser(examens, epreuve, brigade, lieu, effectif=1):
    organisation = Service.ajouter_organisation(examens, epreuve, brigade, lieu, effectif)
    Service.ajouter_surveillant(examens, organisation, nom_libre="Surveillant externe")
    return organisation


# --- B — Règles et complétude --------------------------------------------------


def test_b1_organisation_d_une_formative_refusee(controle):
    from evaluations.services.evaluation import ServiceEvaluation as Eval

    formative = Eval.creer(
        controle.examens,
        {
            "element_referentiel": controle.element_referentiel,
            "type": "formative",
            "session": None,
            "brigade": controle.brigade,
            "date": controle.jour_creneau.jour,
            "creneau_type": controle.jour_creneau.creneau,
            "instructeur": controle.instructeur,
            "lieu": None,
            "motif_date_passee": "",
        },
    )
    with pytest.raises(ErreurValidation, match="certificative"):
        Service.ajouter_organisation(controle.examens, formative, controle.brigade, None, 1)


def test_b2_creneau_fixe_sur_une_date_passee_refuse(certificative, examens):
    Evaluation.objects.filter(pk=certificative.pk).update(
        date=timezone.localdate() - datetime.timedelta(days=1)
    )
    certificative.refresh_from_db()
    with pytest.raises(ErreurValidation, match="passée"):
        Service.fixer_creneau(examens, certificative, H8, H10)


def test_b3_brigade_hors_perimetre_refusee(epreuve, examens, redacteur, formation):
    from organisation.services.session import ServiceSession

    autre_session = ServiceSession.creer(
        redacteur,
        {
            "formation": formation,
            "intitule": "Autre session organisation",
            "date_debut": timezone.localdate(),
            "date_fin": timezone.localdate() + datetime.timedelta(days=60),
            "effectif_attendu": 10,
        },
    )
    hors = creer_brigade(redacteur, autre_session, "HORS-ORG")
    with pytest.raises(ErreurValidation, match="périmètre"):
        Service.ajouter_organisation(examens, epreuve, hors, None, 1)


def test_b4_capacite_insuffisante_nomme_l_ecart(epreuve, examens, brigade, salle):
    with pytest.raises(ErreurValidation, match="dépasse de 1"):
        Service.ajouter_organisation(examens, epreuve, brigade, salle, 31)


def test_b5_pratique_sans_lieu_admise_avec_un_surveillant(epreuve, examens, brigade):
    organisation = Service.ajouter_organisation(examens, epreuve, brigade, None, 1)
    surveillance = Service.ajouter_surveillant(examens, organisation, nom_libre="Surveillant")
    assert surveillance.pk is not None


def test_b6_complete_quand_chaque_brigade_est_organisee_et_surveillee(
    redacteur, epreuve, examens, brigade, salle
):
    affecter_stagiaires(redacteur, brigade, 2)
    assert "n'a pas d'organisation" in " ".join(LectureOrganisationEpreuve.incompletudes(epreuve))
    _organiser(examens, epreuve, brigade, salle, effectif=2)
    assert LectureOrganisationEpreuve.est_complete(epreuve)


def test_b7_repartition_qui_ne_couvre_pas_l_effectif_reel_est_incomplete(
    redacteur, epreuve, examens, brigade, salle
):
    affecter_stagiaires(redacteur, brigade, 2)
    _organiser(examens, epreuve, brigade, salle, effectif=1)
    assert any("≠ effectif réel" in manque for manque in LectureOrganisationEpreuve.incompletudes(epreuve))


def test_b8_organisation_sans_surveillant_incomplete(redacteur, epreuve, examens, brigade, salle):
    affecter_stagiaires(redacteur, brigade, 1)
    Service.ajouter_organisation(examens, epreuve, brigade, salle, 1)
    assert any("aucun surveillant" in manque for manque in LectureOrganisationEpreuve.incompletudes(epreuve))


def test_b9_prete_seulement_avec_un_sujet_retenu(redacteur, epreuve, examens, brigade, salle):
    affecter_stagiaires(redacteur, brigade, 1)
    _organiser(examens, epreuve, brigade, salle, effectif=1)
    assert LectureOrganisationEpreuve.est_complete(epreuve) and not LectureOrganisationEpreuve.est_prete(epreuve)

    sujet = _enregistrer(examens, epreuve, "Pli prete")
    ServiceSujet.retenir(examens, sujet, confirmation=True)
    assert LectureOrganisationEpreuve.est_prete(epreuve)


def test_b10_modification_refusee_apres_le_debut(redacteur, epreuve, examens, brigade, salle):
    organisation = _organiser(examens, epreuve, brigade, salle, effectif=1)
    Evaluation.objects.filter(pk=epreuve.pk).update(
        date=timezone.localdate(),
        heure_debut=datetime.time(0, 0),
        heure_fin=datetime.time(23, 59),
    )
    epreuve.refresh_from_db()
    with pytest.raises(ErreurValidation, match="a commencé"):
        Service.modifier_organisation(examens, organisation, None, 1)


def test_b10_modification_admise_avant_le_debut(redacteur, epreuve, examens, brigade, salle):
    organisation = _organiser(examens, epreuve, brigade, salle, effectif=1)
    Evaluation.objects.filter(pk=epreuve.pk).update(
        date=timezone.localdate() + datetime.timedelta(days=1),
        heure_debut=datetime.time(23, 0),
        heure_fin=datetime.time(23, 59),
    )
    epreuve.refresh_from_db()
    assert Service.modifier_organisation(examens, organisation, None, 1).lieu is None


# --- C — Disponibilité, sens P6 → P5 (A5) ----------------------------------------


def test_c1_lieu_en_indisponibilite_nomme_l_indisponibilite(epreuve, examens, brigade, salle):
    IndisponibiliteLieu.objects.create(
        lieu=salle,
        debut=instant_de(epreuve.date, H8),
        fin=instant_de(epreuve.date, H10),
        motif="Maintenance",
    )
    with pytest.raises(ErreurValidation, match="indisponible.*Maintenance"):
        Service.ajouter_organisation(examens, epreuve, brigade, salle, 1)


def test_c2_lieu_occupe_par_une_seance_secante_nomme_la_seance(
    epreuve, examens, brigade, salle, instructeur
):
    programme = ProgrammeHebdomadaire.objects.create(
        lundi_de_semaine=epreuve.date - datetime.timedelta(days=epreuve.date.weekday())
    )
    Seance.objects.create(
        programme=programme,
        element_referentiel=epreuve.element_referentiel,
        instructeur=instructeur,
        lieu=salle,
        debut=instant_de(epreuve.date, datetime.time(9, 0)),
        fin=instant_de(epreuve.date, datetime.time(11, 0)),
    )
    with pytest.raises(ErreurValidation, match="occupé par la séance"):
        Service.ajouter_organisation(examens, epreuve, brigade, salle, 1)


def test_c3_lieu_occupe_par_une_autre_epreuve_secante_nomme_l_epreuve(
    epreuve, examens, brigade, salle, redacteur
):
    autre = ServiceEvaluation.creer(
        examens,
        {
            "element_referentiel": epreuve.element_referentiel,
            "type": "certificative",
            "session": epreuve.session,
            "brigade": None,
            "date": epreuve.date,
            "creneau_type": None,
            "instructeur": None,
            "lieu": None,
            "motif_date_passee": "",
        },
    )
    Service.fixer_creneau(examens, autre, datetime.time(9, 0), datetime.time(11, 0))
    autre_brigade = creer_brigade(redacteur, epreuve.session, "AUTRE-ORG")
    Service.ajouter_organisation(examens, autre, autre_brigade, salle, 1)
    with pytest.raises(ErreurValidation, match="déjà pris par"):
        Service.ajouter_organisation(examens, epreuve, brigade, salle, 1)


def test_c4_surveillant_referentiel_indisponible_refuse(epreuve, examens, brigade, instructeur):
    IndisponibiliteInstructeur.objects.create(
        instructeur=instructeur,
        debut=instant_de(epreuve.date, H8),
        fin=instant_de(epreuve.date, H10),
        motif="Mission",
    )
    organisation = Service.ajouter_organisation(examens, epreuve, brigade, None, 1)
    with pytest.raises(ErreurValidation, match="indisponible.*Mission"):
        Service.ajouter_surveillant(examens, organisation, instructeur=instructeur)


def test_c5_surveillant_exterieur_ne_fait_l_objet_d_aucun_controle(epreuve, examens, brigade):
    organisation = Service.ajouter_organisation(examens, epreuve, brigade, None, 1)
    surveillance = Service.ajouter_surveillant(
        examens, organisation, nom_libre="Personne extérieure"
    )
    assert surveillance.instructeur is None


def test_c6_meme_instructeur_sur_deux_salles_de_la_meme_epreuve_refuse(
    epreuve, examens, redacteur, instructeur
):
    premiere = creer_brigade(redacteur, epreuve.session, "C6-A")
    seconde = creer_brigade(redacteur, epreuve.session, "C6-B")
    org_a = Service.ajouter_organisation(examens, epreuve, premiere, None, 1)
    org_b = Service.ajouter_organisation(examens, epreuve, seconde, None, 1)
    Service.ajouter_surveillant(examens, org_a, instructeur=instructeur)
    with pytest.raises(ErreurValidation, match="déjà une salle"):
        Service.ajouter_surveillant(examens, org_b, instructeur=instructeur)


def test_c7_creneaux_contigus_non_secants_admis(epreuve, examens, brigade, salle, redacteur):
    autre = ServiceEvaluation.creer(
        examens,
        {
            "element_referentiel": epreuve.element_referentiel,
            "type": "certificative",
            "session": epreuve.session,
            "brigade": None,
            "date": epreuve.date,
            "creneau_type": None,
            "instructeur": None,
            "lieu": None,
            "motif_date_passee": "",
        },
    )
    Service.fixer_creneau(examens, autre, datetime.time(6, 0), H8)
    autre_brigade = creer_brigade(redacteur, epreuve.session, "C7-AUTRE")
    Service.ajouter_organisation(examens, autre, autre_brigade, salle, 1)
    assert Service.ajouter_organisation(examens, epreuve, brigade, salle, 1).pk is not None


def test_c8_nombre_de_requetes_des_conflits_independant_du_nombre_de_lieux(epreuve):
    petits = {999_001}
    grands = set(range(999_001, 999_011))

    with CaptureQueriesContext(connection) as un:
        conflits(epreuve, petits, set())
    with CaptureQueriesContext(connection) as dix:
        conflits(epreuve, grands, set())

    assert len(un) == len(dix)


# --- E — Changement de date (A9, ferme D-193) ------------------------------------


def test_e1_date_changee_vers_un_jour_ou_le_lieu_est_occupe_signale_le_conflit(
    epreuve, examens, brigade, salle, redacteur
):
    affecter_stagiaires(redacteur, brigade, 1)
    _organiser(examens, epreuve, brigade, salle, effectif=1)
    autre = ServiceEvaluation.creer(
        examens,
        {
            "element_referentiel": epreuve.element_referentiel,
            "type": "certificative",
            "session": epreuve.session,
            "brigade": None,
            "date": epreuve.date + datetime.timedelta(days=5),
            "creneau_type": None,
            "instructeur": None,
            "lieu": None,
            "motif_date_passee": "",
        },
    )
    Service.fixer_creneau(examens, autre, H8, H10)
    autre_brigade = creer_brigade(redacteur, epreuve.session, "E1-AUTRE")
    Service.ajouter_organisation(examens, autre, autre_brigade, salle, 1)

    cible = epreuve.date + datetime.timedelta(days=5)
    avertissements = ServiceEvaluation.modifier_date_certificative(
        examens, epreuve, cible, "Notification du 3e bureau."
    ).avertissements

    assert any("déjà pris" in item for item in avertissements)
    assert not LectureOrganisationEpreuve.est_complete(epreuve) or any(
        "conflits" in m for m in LectureOrganisationEpreuve.incompletudes(epreuve)
    )


def test_e2_date_changee_vers_un_jour_libre_sans_conflit(epreuve, examens, brigade, salle):
    organisation = _organiser(examens, epreuve, brigade, salle, effectif=1)
    avertissements = ServiceEvaluation.modifier_date_certificative(
        examens, epreuve, epreuve.date + datetime.timedelta(days=6), "Notification du 3e bureau."
    ).avertissements
    organisation.refresh_from_db()
    assert not any("déjà pris" in item or "indisponible" in item for item in avertissements)
    assert OrganisationEpreuve.objects.filter(pk=organisation.pk, lieu=salle).exists()
    assert Surveillance.objects.filter(organisation=organisation).exists()


def test_lieu_archive_refuse_pour_une_organisation(epreuve, examens, brigade, salle):
    salle.archive = True
    salle.save()
    with pytest.raises(ErreurValidation, match="archivé"):
        Service.ajouter_organisation(examens, epreuve, brigade, salle, 1)
