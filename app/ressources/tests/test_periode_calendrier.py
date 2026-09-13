"""US-PLAN-01, Groupes B et C — modèle `PeriodeCalendrier`, bornes,
granularité horaire, cibles et portée dérivée (RG-28, RG-30, Prompt 28).
Données entièrement fictives.
"""

import datetime

import pytest
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError

from administration.models import EntreeJournal, TypeAction
from noyau.exceptions import ErreurValidation
from ressources.models import PeriodeCalendrier
from ressources.services.periode_calendrier import DonneesPeriode, ServicePeriodeCalendrier


def _instant(jour, heure, minute=0):
    return datetime.datetime(2026, 11, jour, heure, minute, tzinfo=datetime.UTC)


def _donnees(nature, intitule, debut, fin, **supplement):
    base = {
        "nature": nature,
        "intitule": intitule,
        "debut": debut,
        "fin": fin,
        "effet": "",
        "sessions": [],
        "brigades": [],
    }
    base.update(supplement)
    return DonneesPeriode(**base)


# --- B1/B2 — création nominale, effet pré-rempli ou surchargé ---------------


def test_b1_creation_nominale_journalisee_effet_pre_rempli_depuis_la_nature(
    planificateur, nature_evenement
):
    periode = ServicePeriodeCalendrier.creer(
        planificateur,
        _donnees(nature_evenement, "Bivouac EXP1", _instant(2, 8), _instant(6, 8)),
    )

    assert periode.effet == nature_evenement.effet_par_defaut
    natures = list(
        EntreeJournal.objects.filter(objet_type="periode_calendrier").values_list(
            "type_action", flat=True
        )
    )
    assert TypeAction.CREATION_ELEMENT_GESTION in natures


def test_b2_surcharge_de_l_effet_sans_modifier_la_nature(planificateur, nature_evenement):
    assert nature_evenement.effet_par_defaut == "bloquant"

    periode = ServicePeriodeCalendrier.creer(
        planificateur,
        _donnees(
            nature_evenement,
            "Examen exceptionnel",
            _instant(2, 8),
            _instant(2, 10),
            effet="informatif",
        ),
    )

    periode.refresh_from_db()
    assert periode.effet == "informatif"
    nature_evenement.refresh_from_db()
    assert nature_evenement.effet_par_defaut == "bloquant"


# --- B3 — bornes : fin antérieure, puis égale au début ----------------------


def test_b3_fin_anterieure_au_debut_refusee_par_le_service(planificateur, nature_evenement):
    with pytest.raises(ErreurValidation):
        ServicePeriodeCalendrier.creer(
            planificateur, _donnees(nature_evenement, "Invalide", _instant(5, 8), _instant(2, 8))
        )


def test_b3_fin_egale_au_debut_refusee_par_le_service(planificateur, nature_evenement):
    with pytest.raises(ErreurValidation):
        ServicePeriodeCalendrier.creer(
            planificateur, _donnees(nature_evenement, "Invalide", _instant(5, 8), _instant(5, 8))
        )


def test_b3_bornes_invalides_refusees_par_insertion_directe(nature_evenement):
    with pytest.raises(IntegrityError), transaction.atomic():
        PeriodeCalendrier.objects.create(
            nature=nature_evenement,
            intitule="Invalide",
            debut=_instant(5, 8),
            fin=_instant(5, 8),
            effet="bloquant",
        )


def test_effet_hors_domaine_refuse_par_insertion_directe(nature_evenement):
    """`ck_periode_calendrier_effet` — même relecture de conception que
    `ck_nature_evenement_effet` : `EffetPeriode` porte une contrainte de
    vérification en base sur les deux modèles qui l'utilisent."""
    with pytest.raises(IntegrityError), transaction.atomic():
        PeriodeCalendrier.objects.create(
            nature=nature_evenement,
            intitule="Invalide",
            debut=_instant(5, 8),
            fin=_instant(5, 10),
            effet="autre",
        )


# --- B4 — A1 : granularité horaire native, aucun traitement particulier ----


def test_b4_periode_de_deux_heures_est_enregistree_sans_traitement_particulier(
    planificateur, nature_evenement
):
    periode = ServicePeriodeCalendrier.creer(
        planificateur,
        _donnees(nature_evenement, "Conférence courte", _instant(3, 8), _instant(3, 10)),
    )

    assert (periode.fin - periode.debut) == datetime.timedelta(hours=2)


# --- B5 — critère 3 : matin et après-midi, heures disjointes ---------------


def test_b5_deux_periodes_le_meme_jour_matin_et_apres_midi_sont_acceptees(
    planificateur, nature_evenement
):
    ServicePeriodeCalendrier.creer(
        planificateur, _donnees(nature_evenement, "Matin", _instant(3, 8), _instant(3, 10))
    )

    apres_midi = ServicePeriodeCalendrier.creer(
        planificateur, _donnees(nature_evenement, "Après-midi", _instant(3, 14), _instant(3, 16))
    )

    assert not apres_midi.avertissements
    assert PeriodeCalendrier.objects.count() == 2


# --- B6 — bornes contiguës, même comportement que IndisponibiliteInstructeur


def test_b6_bornes_contigues_acceptees_comme_pour_indisponibilite_instructeur(
    planificateur, nature_evenement
):
    ServicePeriodeCalendrier.creer(
        planificateur, _donnees(nature_evenement, "Première", _instant(3, 8), _instant(3, 12))
    )

    seconde = ServicePeriodeCalendrier.creer(
        planificateur, _donnees(nature_evenement, "Seconde", _instant(3, 12), _instant(3, 16))
    )

    assert not seconde.avertissements


# --- C1/C2/C3 — cibles et portée dérivée ------------------------------------


def test_c1_aucune_cible_la_portee_derivee_vaut_centre_entier(planificateur, nature_evenement):
    periode = ServicePeriodeCalendrier.creer(
        planificateur, _donnees(nature_evenement, "Congé général", _instant(2, 0), _instant(3, 0))
    )

    assert periode.portee == "Centre entier"


def test_c2_deux_sessions_ciblees_portee_derivee_en_toutes_lettres(
    planificateur, nature_evenement, session, autre_session
):
    periode = ServicePeriodeCalendrier.creer(
        planificateur,
        _donnees(
            nature_evenement,
            "Conférence inter-sessions",
            _instant(2, 8),
            _instant(2, 10),
            sessions=[session, autre_session],
        ),
    )

    assert session.intitule in periode.portee
    assert autre_session.intitule in periode.portee
    assert "sessions" in periode.portee.lower()


def test_c3_sessions_et_brigades_ciblees_simultanement_portee_correcte(
    planificateur, nature_evenement, session, brigade, autre_brigade
):
    """Jeu d'essai imposé (.claude/rules/tests.md) : « une période de
    calendrier visant deux sessions et une brigade » — ici une session et
    deux brigades, cas symétrique explicitement accepté par A2/§ 4."""
    periode = ServicePeriodeCalendrier.creer(
        planificateur,
        _donnees(
            nature_evenement,
            "Bivouac mixte",
            _instant(2, 8),
            _instant(6, 8),
            sessions=[session],
            brigades=[brigade, autre_brigade],
        ),
    )

    assert session.intitule in periode.portee
    assert brigade.designation in periode.portee
    assert autre_brigade.designation in periode.portee
    assert "session" in periode.portee.lower()
    assert "brigade" in periode.portee.lower()


# --- C4 — aucune colonne `portee` en base -----------------------------------


def test_c4_aucune_colonne_portee_n_existe_en_base():
    noms_colonnes = {
        champ.column for champ in PeriodeCalendrier._meta.get_fields() if hasattr(champ, "column")
    }

    assert "portee" not in noms_colonnes


# --- C5 — suppression d'une cible : jamais de bascule silencieuse ----------


def test_c5_suppression_de_la_session_ciblee_refusee_tant_qu_une_periode_la_cible(
    planificateur, nature_evenement, session
):
    periode = ServicePeriodeCalendrier.creer(
        planificateur,
        _donnees(
            nature_evenement,
            "Examen de session",
            _instant(2, 8),
            _instant(2, 10),
            sessions=[session],
        ),
    )

    with pytest.raises(ProtectedError):
        session.delete()

    periode.refresh_from_db()
    assert periode.portee != "Centre entier"
    assert list(periode.sessions.all()) == [session]


def test_c5_suppression_de_la_brigade_ciblee_refusee_tant_qu_une_periode_la_cible(
    planificateur, nature_evenement, brigade
):
    periode = ServicePeriodeCalendrier.creer(
        planificateur,
        _donnees(
            nature_evenement,
            "Bivouac de brigade",
            _instant(2, 8),
            _instant(6, 8),
            brigades=[brigade],
        ),
    )

    with pytest.raises(ProtectedError):
        brigade.delete()

    periode.refresh_from_db()
    assert periode.portee != "Centre entier"
