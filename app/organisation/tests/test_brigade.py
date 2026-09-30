"""US-SES-02 — couche services, CU-P3-02. Groupe A (Prompt 21, § 10)."""

import datetime

import pytest
from django.db import IntegrityError, transaction

from administration.models import EntreeJournal, TypeAction
from noyau.exceptions import ErreurHabilitation, ErreurValidation
from organisation.models import Brigade
from organisation.services.brigade import ServiceBrigade
from organisation.services.session import ServiceSession
from organisation.tests.conftest import donnees_brigade, donnees_session


def test_creation_nominale_rattachee_et_journalisee(redacteur, session):
    brigade = ServiceBrigade.creer(redacteur, session, donnees_brigade())

    assert brigade.session == session
    assert EntreeJournal.objects.filter(
        type_action=TypeAction.CREATION_ELEMENT_GESTION, auteur=redacteur
    ).exists()


def test_a2_effectif_nul_refuse(redacteur, session):
    with pytest.raises(ErreurValidation):
        ServiceBrigade.creer(redacteur, session, donnees_brigade(effectif_previsionnel=0))


def test_a2_effectif_negatif_refuse(redacteur, session):
    with pytest.raises(ErreurValidation):
        ServiceBrigade.creer(redacteur, session, donnees_brigade(effectif_previsionnel=-5))


def test_a3_doublon_meme_session_casse_indifferente_refuse(redacteur, session):
    ServiceBrigade.creer(redacteur, session, donnees_brigade(designation="EXP1"))

    with pytest.raises(ErreurValidation) as info:
        ServiceBrigade.creer(redacteur, session, donnees_brigade(designation="exp1"))

    assert "EXP1" in str(info.value)


def test_a4_meme_designation_autre_session_meme_formation_acceptee(redacteur, formation):
    """Porte l'écart du § 3 : unicité au sein de la session, pas du type de
    formation — deux sessions successives de la même formation peuvent
    réutiliser la désignation EXP1."""
    session_2026 = ServiceSession.creer(
        redacteur, donnees_session(formation, intitule="Session 2026")
    )
    session_2027 = ServiceSession.creer(
        redacteur,
        donnees_session(
            formation,
            intitule="Session 2027",
            date_debut=session_2026.date_debut + datetime.timedelta(days=365),
            date_fin=session_2026.date_fin + datetime.timedelta(days=365),
        ),
    )
    ServiceBrigade.creer(redacteur, session_2026, donnees_brigade(designation="EXP1"))

    brigade_2027 = ServiceBrigade.creer(
        redacteur, session_2027, donnees_brigade(designation="EXP1")
    )

    assert brigade_2027.pk is not None


def test_a5_somme_inferieure_enregistree_avec_ecart_signale(redacteur, session):
    ServiceBrigade.creer(redacteur, session, donnees_brigade(effectif_previsionnel=10))

    indicateur = ServiceBrigade.indicateur_effectif(session)

    assert Brigade.objects.filter(session=session).count() == 1
    assert indicateur["ecart"] == 10 - session.effectif_attendu
    assert indicateur["ecart"] != 0


def test_a5_somme_egale_aucun_ecart(redacteur, session):
    ServiceBrigade.creer(
        redacteur, session, donnees_brigade(effectif_previsionnel=session.effectif_attendu)
    )

    indicateur = ServiceBrigade.indicateur_effectif(session)

    assert indicateur["ecart"] == 0


def test_a5_somme_superieure_enregistree_avec_ecart_signale(redacteur, session):
    ServiceBrigade.creer(
        redacteur, session, donnees_brigade(effectif_previsionnel=session.effectif_attendu + 15)
    )

    indicateur = ServiceBrigade.indicateur_effectif(session)

    assert Brigade.objects.filter(session=session).count() == 1
    assert indicateur["ecart"] == 15
    assert indicateur["ecart"] != 0


def test_a6_brigade_creee_apres_le_debut_enregistree_avec_avertissement_de_decalage(
    redacteur, formation
):
    session_demarree = ServiceSession.creer(
        redacteur,
        donnees_session(
            formation,
            date_debut=datetime.date.today() - datetime.timedelta(days=5),
            date_fin=datetime.date.today() + datetime.timedelta(days=60),
        ),
    )

    brigade = ServiceBrigade.creer(redacteur, session_demarree, donnees_brigade())

    assert brigade.pk is not None
    assert len(brigade.avertissements) == 1
    assert brigade.avertissements[0]["code"] == "brigade_ouverte_en_decalage"


def test_a7_suppression_de_la_derniere_brigade_refusee(redacteur, session):
    brigade = ServiceBrigade.creer(redacteur, session, donnees_brigade())

    with pytest.raises(ErreurValidation) as info:
        ServiceBrigade.supprimer(redacteur, brigade)

    assert brigade.designation in str(info.value)
    assert Brigade.objects.filter(pk=brigade.pk).exists()


def test_a8_suppression_parmi_plusieurs_acceptee_et_journalisee(redacteur, session):
    premiere = ServiceBrigade.creer(redacteur, session, donnees_brigade(designation="EXP1"))
    ServiceBrigade.creer(redacteur, session, donnees_brigade(designation="EXP2"))

    ServiceBrigade.supprimer(redacteur, premiere)

    assert not Brigade.objects.filter(pk=premiere.pk).exists()
    assert EntreeJournal.objects.filter(type_action=TypeAction.SUPPRESSION_ELEMENT_GESTION).exists()


def test_a9_suppression_de_session_portant_des_brigades_refusee_avec_enumeration(
    redacteur, session
):
    brigade = ServiceBrigade.creer(redacteur, session, donnees_brigade())

    with pytest.raises(ErreurValidation) as info:
        ServiceSession.supprimer(redacteur, session.pk)

    assert brigade.designation in str(info.value)


def test_critere_5_suppression_sans_programme_toujours_acceptee(redacteur, session):
    """Critère 5 (« brigade au programme en cours ») est refermé par
    US-PLAN-04 (D-83) : `LigneProgramme.brigade` est en `PROTECT` — voir
    `planification.tests.test_modeles::test_d83_suppression_brigade_au_
    programme_refusee_par_le_vrai_chemin_de_service` pour le refus lui-même
    (ce module ne dépend pas de `planification`, sens interdit). Ici, seul le
    cas SANS programme reste à couvrir : une brigade jamais programmée se
    supprime toujours normalement."""
    ServiceBrigade.creer(redacteur, session, donnees_brigade(designation="EXP1"))
    brigade = ServiceBrigade.creer(redacteur, session, donnees_brigade(designation="EXP2"))

    ServiceBrigade.supprimer(redacteur, brigade)

    assert not Brigade.objects.filter(pk=brigade.pk).exists()


def test_a10_aucune_valeur_par_defaut_n_est_proposee_rg12(redacteur, session):
    with pytest.raises(ErreurValidation):
        ServiceBrigade.creer(redacteur, session, {"designation": "EXP1"})


def test_habilitation_insuffisante_refuse(lecteur, session):
    with pytest.raises(ErreurHabilitation):
        ServiceBrigade.creer(lecteur, session, donnees_brigade())


# --- Groupe B — contraintes réellement en base --------------------------


def test_ck_brigade_effectif_en_base(session):
    with pytest.raises(IntegrityError), transaction.atomic():
        Brigade.objects.create(
            session=session, designation="Contournement", effectif_previsionnel=0
        )


def test_uq_brigade_session_designation_en_base(session):
    Brigade.objects.create(session=session, designation="Doublon base", effectif_previsionnel=20)
    with pytest.raises(IntegrityError), transaction.atomic():
        Brigade.objects.create(
            session=session, designation="DOUBLON BASE", effectif_previsionnel=15
        )
