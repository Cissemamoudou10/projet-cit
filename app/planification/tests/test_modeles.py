"""US-PLAN-04, Groupe A — modèles `ProgrammeHebdomadaire`, `Seance`,
`LigneProgramme` (Prompt 30, § 2). Données entièrement fictives.
"""

import datetime

import pytest
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError

from planification.models import LigneProgramme, ProgrammeHebdomadaire, Seance
from planification.tests.conftest import instant


def _programme(lundi):
    return ProgrammeHebdomadaire.objects.create(lundi_de_semaine=lundi)


def _seance(programme, element_referentiel, instructeur, lundi, **supplement):
    donnees = {
        "programme": programme,
        "element_referentiel": element_referentiel,
        "instructeur": instructeur,
        "debut": instant(lundi, 0, 8),
        "fin": instant(lundi, 0, 9, 45),
    }
    donnees.update(supplement)
    return Seance.objects.create(**donnees)


# --- A1 — unicité de lundi_de_semaine -----------------------------------


def test_a1_deux_programmes_la_meme_semaine_refuse_par_insertion_directe(db, lundi_semaine):
    _programme(lundi_semaine)

    with pytest.raises(IntegrityError), transaction.atomic():
        _programme(lundi_semaine)


# --- A2 — lundi_de_semaine qui n'est pas un lundi -------------------------


def test_a2_lundi_de_semaine_qui_n_est_pas_un_lundi_refuse(db, lundi_semaine):
    mardi = lundi_semaine + datetime.timedelta(days=1)

    with pytest.raises(IntegrityError), transaction.atomic():
        _programme(mardi)


# --- A3 — ck_seance_bornes -------------------------------------------------


def test_a3_ck_seance_bornes_par_insertion_directe(
    programme, element_referentiel, instructeur, lundi_semaine
):
    with pytest.raises(IntegrityError), transaction.atomic():
        _seance(
            programme,
            element_referentiel,
            instructeur,
            lundi_semaine,
            debut=instant(lundi_semaine, 0, 10),
            fin=instant(lundi_semaine, 0, 10),
        )


# --- A4 — une séance à deux lignes de programme, acceptée -----------------


def test_a4_une_seance_portant_deux_lignes_de_programme_est_acceptee(
    programme, element_referentiel, instructeur, brigade, autre_brigade
):
    seance = _seance(programme, element_referentiel, instructeur, programme.lundi_de_semaine)
    LigneProgramme.objects.create(seance=seance, brigade=brigade)
    LigneProgramme.objects.create(seance=seance, brigade=autre_brigade)

    assert seance.lignes.count() == 2
    assert seance.est_regroupee is True


# --- A5 — unicité ligne : même brigade deux fois sur une séance -----------


def test_a5_meme_brigade_deux_fois_sur_une_seance_refuse(
    programme, element_referentiel, instructeur, brigade, lundi_semaine
):
    seance = _seance(programme, element_referentiel, instructeur, lundi_semaine)
    LigneProgramme.objects.create(seance=seance, brigade=brigade)

    with pytest.raises(IntegrityError), transaction.atomic():
        LigneProgramme.objects.create(seance=seance, brigade=brigade)


# --- A6 — creneau_type nul, accepté (RG-64) -------------------------------


def test_a6_creneau_type_nul_accepte(programme, element_referentiel, instructeur, lundi_semaine):
    seance = _seance(programme, element_referentiel, instructeur, lundi_semaine)

    assert seance.creneau_type is None


# --- A7 — lieu nul, accepté (matière sans lieu) ---------------------------


def test_a7_lieu_nul_accepte(programme, element_referentiel, instructeur, lundi_semaine):
    seance = _seance(programme, element_referentiel, instructeur, lundi_semaine)

    assert seance.lieu is None


# --- A8 — aucune colonne dérivée en base ----------------------------------


def test_a8_aucune_colonne_derivee_en_base():
    noms_champs_seance = {
        champ.name for champ in Seance._meta.get_fields() if hasattr(champ, "column")
    }
    noms_champs_ligne = {
        champ.name for champ in LigneProgramme._meta.get_fields() if hasattr(champ, "column")
    }
    assert "duree_heures" not in noms_champs_seance
    assert "est_regroupee" not in noms_champs_seance
    assert "volume_cumule" not in noms_champs_ligne


# --- A9 — PROTECT : suppression refusée avec énumération -------------------


def test_a9_suppression_instructeur_portant_une_seance_refusee(
    programme, element_referentiel, instructeur, lundi_semaine
):
    _seance(programme, element_referentiel, instructeur, lundi_semaine)

    with pytest.raises(ProtectedError):
        instructeur.delete()


def test_a9_suppression_lieu_portant_une_seance_refusee(
    programme, element_referentiel, instructeur, lieu_partage, lundi_semaine
):
    _seance(programme, element_referentiel, instructeur, lundi_semaine, lieu=lieu_partage)

    with pytest.raises(ProtectedError):
        lieu_partage.delete()


def test_a9_suppression_element_referentiel_portant_une_seance_refusee(
    programme, element_referentiel, instructeur, lundi_semaine
):
    _seance(programme, element_referentiel, instructeur, lundi_semaine)

    with pytest.raises(ProtectedError):
        element_referentiel.delete()


def test_a9_suppression_brigade_portant_une_ligne_refusee(
    programme, element_referentiel, instructeur, brigade, lundi_semaine
):
    seance = _seance(programme, element_referentiel, instructeur, lundi_semaine)
    LigneProgramme.objects.create(seance=seance, brigade=brigade)

    with pytest.raises(ProtectedError):
        brigade.delete()


def test_d83_suppression_brigade_au_programme_refusee_par_le_vrai_chemin_de_service(
    redacteur, programme, cours, brigade, autre_brigade
):
    """D-83 : `LigneProgramme.brigade` est en `PROTECT` depuis US-PLAN-04, mais
    rien ne prouvait que `ServiceBrigade.supprimer` (le chemin réellement
    emprunté par l'écran) traduit ce refus en `ErreurValidation` nommant
    l'opposant — leçon de D-50, la seule preuve valable est celle du chemin de
    service, pas la seule contrainte en base (déjà couverte ci-dessus).
    `redacteur` (Cellule pédagogique) : seul profil habilité en écriture sur
    `organisation` (matrice § 11.2). `autre_brigade` (même session que
    `brigade`) évite de tomber sur le refus "dernière brigade" (critère 2),
    qui interviendrait avant le PROTECT."""
    from noyau.exceptions import ErreurValidation
    from organisation.services.brigade import ServiceBrigade

    seance = _seance(programme, cours.element, cours.instructeur, programme.lundi_de_semaine)
    LigneProgramme.objects.create(seance=seance, brigade=brigade)

    with pytest.raises(ErreurValidation) as info:
        ServiceBrigade.supprimer(redacteur, brigade)

    assert brigade.designation in str(info.value)
