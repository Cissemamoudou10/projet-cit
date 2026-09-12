"""US-SES-05 — couche services, CU-P3-05. Groupes A et D (Prompt 24, § 12)."""

import datetime

import pytest
from django.db import IntegrityError, transaction

from administration.models import EntreeJournal, TypeAction
from noyau.exceptions import ErreurHabilitation, ErreurValidation
from organisation.models import Stagiaire
from organisation.services.session import ServiceSession
from organisation.services.stagiaire import ServiceStagiaire
from organisation.tests.conftest import donnees_session, donnees_stagiaire


def test_a1_creation_nominale_journalisee(redacteur, session):
    stagiaire = ServiceStagiaire.creer(redacteur, session, donnees_stagiaire())

    assert stagiaire.session == session
    assert not stagiaire.radie
    assert EntreeJournal.objects.filter(
        type_action=TypeAction.CREATION_ELEMENT_GESTION, auteur=redacteur
    ).exists()


def test_a2_rg17_meme_matricule_meme_session_casse_indifferente_refuse(redacteur, session):
    ServiceStagiaire.creer(redacteur, session, donnees_stagiaire(matricule="M001"))

    with pytest.raises(ErreurValidation) as info:
        ServiceStagiaire.creer(redacteur, session, donnees_stagiaire(matricule="m001", nom="Autre"))

    assert "M001" in str(info.value)


def test_a3_meme_matricule_autre_session_accepte(redacteur, session, formation):
    """Porte la conséquence de modèle du § 2 : RG-17 n'unicise le matricule
    qu'au sein d'une session — un même militaire suivant deux formations
    existe deux fois dans la base, sans lien entre ses enregistrements."""
    ServiceStagiaire.creer(redacteur, session, donnees_stagiaire(matricule="M001"))
    autre_session = ServiceSession.creer(
        redacteur, donnees_session(formation, intitule="Autre session")
    )

    stagiaire_2 = ServiceStagiaire.creer(
        redacteur, autre_session, donnees_stagiaire(matricule="M001")
    )

    assert stagiaire_2.pk is not None


@pytest.mark.parametrize("champ", ["matricule", "nom", "prenom", "grade", "unite"])
def test_a4_champ_obligatoire_manquant_refuse_message_nomme_le_champ(redacteur, session, champ):
    donnees = donnees_stagiaire(**{champ: ""})

    with pytest.raises(ErreurValidation) as info:
        ServiceStagiaire.creer(redacteur, session, donnees)

    assert "obligatoire" in str(info.value)


def test_a5_ck_stagiaire_radiation_radie_sans_motif_refuse_en_base(session):
    with pytest.raises(IntegrityError), transaction.atomic():
        Stagiaire.objects.create(
            session=session,
            **donnees_stagiaire(),
            radie=True,
            motif_radiation=None,
            date_radiation=datetime.date.today(),
        )


def test_a5_ck_stagiaire_radiation_radie_sans_date_refuse_en_base(session):
    with pytest.raises(IntegrityError), transaction.atomic():
        Stagiaire.objects.create(
            session=session,
            **donnees_stagiaire(),
            radie=True,
            motif_radiation="Fin anticipée",
            date_radiation=None,
        )


def test_a5_ck_stagiaire_radiation_motif_sans_radiation_refuse_en_base(session):
    with pytest.raises(IntegrityError), transaction.atomic():
        Stagiaire.objects.create(
            session=session,
            **donnees_stagiaire(),
            radie=False,
            motif_radiation="Motif orphelin",
            date_radiation=None,
        )


def test_a6_uq_stagiaire_session_matricule_en_base(session):
    Stagiaire.objects.create(session=session, **donnees_stagiaire(matricule="Doublon"))
    with pytest.raises(IntegrityError), transaction.atomic():
        Stagiaire.objects.create(session=session, **donnees_stagiaire(matricule="DOUBLON"))


def test_habilitation_insuffisante_refuse(lecteur, session):
    with pytest.raises(ErreurHabilitation):
        ServiceStagiaire.creer(lecteur, session, donnees_stagiaire())


# --- Groupe D — radiation -------------------------------------------------


def test_d1_radiation_nominale_journalisee_stagiaire_present_en_base(redacteur, stagiaire):
    ServiceStagiaire.radier(redacteur, stagiaire, "Fin de mission anticipée", datetime.date.today())

    stagiaire.refresh_from_db()
    assert stagiaire.radie
    assert stagiaire.motif_radiation == "Fin de mission anticipée"
    assert stagiaire.date_radiation == datetime.date.today()
    assert Stagiaire.objects.filter(pk=stagiaire.pk).exists()
    assert EntreeJournal.objects.filter(type_action=TypeAction.MODIFICATION_ELEMENT_GESTION).exists()


def test_d1_radiation_sans_motif_refusee(redacteur, stagiaire):
    with pytest.raises(ErreurValidation):
        ServiceStagiaire.radier(redacteur, stagiaire, "", datetime.date.today())


def test_d2_stagiaire_radie_disparait_des_listes_actives_reste_consultable_avec_filtre(
    redacteur, session, stagiaire
):
    ServiceStagiaire.radier(redacteur, stagiaire, "Radiation", datetime.date.today())

    page_actifs = ServiceStagiaire.lister(redacteur, session, {"etat": "actifs"}, None)
    page_radies = ServiceStagiaire.lister(redacteur, session, {"etat": "radies"}, None)

    assert stagiaire.pk not in [s.pk for s in page_actifs]
    assert stagiaire.pk in [s.pk for s in page_radies]


def test_d3_deradiation_defait_la_radiation(redacteur, stagiaire):
    """§ 7 (Prompt 24) : la dé-radiation est offerte, pour qu'une radiation
    saisie par erreur ne force pas à supprimer le stagiaire."""
    ServiceStagiaire.radier(redacteur, stagiaire, "Erreur de saisie", datetime.date.today())

    ServiceStagiaire.deradier(redacteur, stagiaire)

    stagiaire.refresh_from_db()
    assert not stagiaire.radie
    assert stagiaire.motif_radiation is None
    assert stagiaire.date_radiation is None


def test_d4_suppression_sans_affectation_ni_note_acceptee_journalisee(redacteur, stagiaire):
    ServiceStagiaire.supprimer(redacteur, stagiaire)

    assert not Stagiaire.objects.filter(pk=stagiaire.pk).exists()
    assert EntreeJournal.objects.filter(type_action=TypeAction.SUPPRESSION_ELEMENT_GESTION).exists()


def test_d5_supprimer_et_radier_sont_deux_operations_independantes(redacteur, session):
    """Un stagiaire supprimé n'a jamais été radié : les deux actes ne
    passent jamais par le même chemin de code (§ 7, Prompt 24)."""
    stagiaire_supprime = ServiceStagiaire.creer(
        redacteur, session, donnees_stagiaire(matricule="SUPP1")
    )
    stagiaire_radie = ServiceStagiaire.creer(redacteur, session, donnees_stagiaire(matricule="RAD1"))

    ServiceStagiaire.supprimer(redacteur, stagiaire_supprime)
    ServiceStagiaire.radier(redacteur, stagiaire_radie, "Radiation", datetime.date.today())

    assert not Stagiaire.objects.filter(pk=stagiaire_supprime.pk).exists()
    assert Stagiaire.objects.filter(pk=stagiaire_radie.pk, radie=True).exists()
