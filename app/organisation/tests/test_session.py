"""US-SES-01 — couche services, CU-P3-01. Groupe A (Prompt 20, § 11)."""

import datetime

import pytest
from django.db import IntegrityError, transaction

from administration.models import EntreeJournal, TypeAction
from noyau.exceptions import ErreurHabilitation, ErreurValidation
from organisation.models import EtatSession, Session
from organisation.services.session import ServiceSession
from organisation.tests.conftest import donnees_session
from referentiel.models import CategorieLieu, ElementReferentiel, Formation, Matiere


def test_creation_nominale_ouverte_rattachee_et_journalisee(redacteur, formation):
    session = ServiceSession.creer(redacteur, donnees_session(formation))

    assert session.etat == EtatSession.OUVERTE
    assert session.formation == formation
    assert EntreeJournal.objects.filter(
        type_action=TypeAction.CREATION_ELEMENT_GESTION, auteur=redacteur
    ).exists()


def test_e1_date_fin_anterieure_a_date_debut_refusee(redacteur, formation):
    with pytest.raises(ErreurValidation):
        ServiceSession.creer(
            redacteur,
            donnees_session(
                formation,
                date_debut=datetime.date(2026, 3, 1),
                date_fin=datetime.date(2026, 1, 1),
            ),
        )


def test_e1_date_fin_egale_a_date_debut_refusee(redacteur, formation):
    meme_date = datetime.date(2026, 3, 1)
    with pytest.raises(ErreurValidation):
        ServiceSession.creer(
            redacteur, donnees_session(formation, date_debut=meme_date, date_fin=meme_date)
        )


def test_e3_effectif_nul_refuse(redacteur, formation):
    with pytest.raises(ErreurValidation):
        ServiceSession.creer(redacteur, donnees_session(formation, effectif_attendu=0))


def test_e3_effectif_negatif_refuse(redacteur, formation):
    with pytest.raises(ErreurValidation):
        ServiceSession.creer(redacteur, donnees_session(formation, effectif_attendu=-3))


def test_critere_4_formation_archivee_refusee_avec_action_corrective(redacteur, formation_archivee):
    with pytest.raises(ErreurValidation) as info:
        ServiceSession.creer(redacteur, donnees_session(formation_archivee))

    assert "archivée" in str(info.value)
    assert "désarchivez" in str(info.value)


def test_e4_referentiel_vide_refuse(redacteur, formation_vide):
    with pytest.raises(ErreurValidation):
        ServiceSession.creer(redacteur, donnees_session(formation_vide))


def test_critere_3_deux_sessions_periodes_disjointes_acceptees(redacteur, formation):
    premiere = ServiceSession.creer(
        redacteur,
        donnees_session(
            formation,
            intitule="Session A",
            date_debut=datetime.date(2026, 1, 5),
            date_fin=datetime.date(2026, 3, 27),
        ),
    )
    seconde = ServiceSession.creer(
        redacteur,
        donnees_session(
            formation,
            intitule="Session B",
            date_debut=datetime.date(2026, 4, 5),
            date_fin=datetime.date(2026, 6, 27),
        ),
    )

    assert premiere.pk and seconde.pk


def test_a1_deux_sessions_periodes_chevauchantes_acceptees_absence_de_contrainte(
    redacteur, formation
):
    """A1 de la fiche CU-P3-01 : aucune contrainte de non-chevauchement, ni
    en base ni en services — les deux créations réussissent."""
    premiere = ServiceSession.creer(
        redacteur,
        donnees_session(
            formation,
            intitule="Session A",
            date_debut=datetime.date(2026, 1, 5),
            date_fin=datetime.date(2026, 4, 30),
        ),
    )
    seconde = ServiceSession.creer(
        redacteur,
        donnees_session(
            formation,
            intitule="Session B",
            date_debut=datetime.date(2026, 3, 1),
            date_fin=datetime.date(2026, 6, 27),
        ),
    )

    assert premiere.pk and seconde.pk


def test_critere_5_ouverture_sans_periodicite_imposee(redacteur, formation):
    """Formations ouvertes sur ordre : dates arbitraires, aucun rythme
    régulier n'est exigé."""
    premiere = ServiceSession.creer(
        redacteur,
        donnees_session(
            formation,
            intitule="Session ordre 1",
            date_debut=datetime.date(2026, 1, 5),
            date_fin=datetime.date(2026, 1, 20),
        ),
    )
    seconde = ServiceSession.creer(
        redacteur,
        donnees_session(
            formation,
            intitule="Session ordre 2",
            date_debut=datetime.date(2026, 8, 1),
            date_fin=datetime.date(2026, 8, 9),
        ),
    )

    assert premiere.pk and seconde.pk


def test_critere_2_resume_du_referentiel_de_la_session_reflete_une_modification_ulterieure(
    redacteur, formation
):
    """Le test qui compte : aucune copie n'a été faite si le résumé de LA
    SESSION reflète une modification faite après coup sur le référentiel de
    sa formation."""
    session = ServiceSession.creer(redacteur, donnees_session(formation))
    avant = ServiceSession.referentiel_resume(redacteur, session)

    element = ElementReferentiel.objects.get(formation=formation)
    element.volume_horaire_prescrit = 999
    element.save()

    apres = ServiceSession.referentiel_resume(redacteur, session)

    assert avant["volume_total"] == 40
    assert apres["volume_total"] == 999


def test_e2_volume_excessif_accepte_avec_avertissement(redacteur, type_officiers):
    """Les deux assertions dans le même test : la session EST créée, ET un
    avertissement est retourné."""
    formation = Formation.objects.create(
        intitule="Formation intensive",
        specialite="Transmissions",
        duree_semaines=1,
        type_formation=type_officiers,
    )
    matiere = Matiere.objects.create(intitule="Cryptographie", code="CRY01")
    ElementReferentiel.objects.create(
        formation=formation,
        matiere=matiere,
        volume_horaire_prescrit=200,
        categorie_lieu=CategorieLieu.SALLE_ATTITREE,
        type_lieu_partage=None,
    )

    session = ServiceSession.creer(
        redacteur,
        donnees_session(
            formation,
            date_debut=datetime.date(2026, 1, 5),
            date_fin=datetime.date(2026, 1, 12),
        ),
    )

    assert session.pk is not None
    assert len(session.avertissements) == 1
    assert session.avertissements[0]["code"] == "volume_excede_heures_ouvrables"


def test_unicite_composite_doublon_meme_formation_refuse_casse_indifferente(redacteur, formation):
    ServiceSession.creer(redacteur, donnees_session(formation, intitule="Session Alpha"))

    with pytest.raises(ErreurValidation):
        ServiceSession.creer(redacteur, donnees_session(formation, intitule="session alpha"))


def test_unicite_composite_meme_intitule_autre_formation_accepte(
    redacteur, formation, type_officiers
):
    autre_formation = Formation.objects.create(
        intitule="Autre formation",
        specialite="Transmissions",
        duree_semaines=10,
        type_formation=type_officiers,
    )
    ElementReferentiel.objects.create(
        formation=autre_formation,
        matiere=Matiere.objects.create(intitule="Antennes", code="ANT01"),
        volume_horaire_prescrit=30,
        categorie_lieu=CategorieLieu.SALLE_ATTITREE,
        type_lieu_partage=None,
    )
    ServiceSession.creer(redacteur, donnees_session(formation, intitule="Session commune"))

    autre = ServiceSession.creer(
        redacteur, donnees_session(autre_formation, intitule="Session commune")
    )

    assert autre.pk is not None


def test_habilitation_insuffisante_refuse(lecteur, formation):
    with pytest.raises(ErreurHabilitation):
        ServiceSession.creer(lecteur, donnees_session(formation))


# --- Groupe B — contraintes réellement en base --------------------------


def test_ck_session_dates_en_base(formation):
    with pytest.raises(IntegrityError), transaction.atomic():
        Session.objects.create(
            formation=formation,
            intitule="Contournement dates",
            date_debut=datetime.date(2026, 3, 1),
            date_fin=datetime.date(2026, 1, 1),
            effectif_attendu=20,
        )


def test_ck_session_effectif_en_base(formation):
    with pytest.raises(IntegrityError), transaction.atomic():
        Session.objects.create(
            formation=formation,
            intitule="Contournement effectif",
            date_debut=datetime.date(2026, 1, 5),
            date_fin=datetime.date(2026, 3, 27),
            effectif_attendu=0,
        )


def test_ck_session_etat_en_base(formation):
    with pytest.raises(IntegrityError), transaction.atomic():
        Session.objects.create(
            formation=formation,
            intitule="Contournement état",
            date_debut=datetime.date(2026, 1, 5),
            date_fin=datetime.date(2026, 3, 27),
            effectif_attendu=20,
            etat="invalide",
        )


def test_uq_session_formation_intitule_en_base(formation):
    Session.objects.create(
        formation=formation,
        intitule="Doublon base",
        date_debut=datetime.date(2026, 1, 5),
        date_fin=datetime.date(2026, 3, 27),
        effectif_attendu=20,
    )
    with pytest.raises(IntegrityError), transaction.atomic():
        Session.objects.create(
            formation=formation,
            intitule="DOUBLON BASE",
            date_debut=datetime.date(2026, 4, 1),
            date_fin=datetime.date(2026, 6, 1),
            effectif_attendu=20,
        )


def test_aucune_contrainte_de_non_chevauchement_en_base(formation):
    """§ 3 : preuve directe, court-circuitant le service — deux insertions
    à périodes chevauchantes réussissent toutes les deux."""
    Session.objects.create(
        formation=formation,
        intitule="Chevauchement A",
        date_debut=datetime.date(2026, 1, 5),
        date_fin=datetime.date(2026, 4, 30),
        effectif_attendu=20,
    )
    Session.objects.create(
        formation=formation,
        intitule="Chevauchement B",
        date_debut=datetime.date(2026, 3, 1),
        date_fin=datetime.date(2026, 6, 27),
        effectif_attendu=20,
    )

    assert Session.objects.count() == 2
