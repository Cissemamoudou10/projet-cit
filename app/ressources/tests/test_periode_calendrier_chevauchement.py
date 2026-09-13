"""US-PLAN-01, Groupe D (RG-29, § 2 du Prompt 28, arbitrage confirmé) et
Groupe F (E3, § 7) — chevauchement de périodes et avertissement de bornes
hors des dates d'une session ciblée. Données entièrement fictives.
"""

import datetime

import pytest

from noyau.exceptions import ErreurValidation
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


# --- D1 — doublon exact : mêmes bornes, mêmes cibles, même nature ----------


def test_d1_doublon_exact_refuse_et_designe_la_periode_en_conflit(planificateur, nature_evenement):
    ServicePeriodeCalendrier.creer(
        planificateur, _donnees(nature_evenement, "Congé initial", _instant(2, 8), _instant(5, 8))
    )

    with pytest.raises(ErreurValidation, match="Congé initial"):
        ServicePeriodeCalendrier.creer(
            planificateur,
            _donnees(nature_evenement, "Congé dupliqué", _instant(2, 8), _instant(5, 8)),
        )


# --- D2 — mêmes bornes, ensembles de cibles différents : avertissement ----


def test_d2_memes_bornes_cibles_differentes_accepte_avec_avertissement(
    planificateur, nature_evenement, session
):
    ServicePeriodeCalendrier.creer(
        planificateur,
        _donnees(nature_evenement, "Centre entier", _instant(2, 8), _instant(5, 8)),
    )

    ciblee = ServicePeriodeCalendrier.creer(
        planificateur,
        _donnees(
            nature_evenement, "Ciblée session", _instant(2, 8), _instant(5, 8), sessions=[session]
        ),
    )

    assert any(a["code"] == "periode_chevauchement" for a in ciblee.avertissements)


# --- D3 — cibles identiques, bornes partiellement sécantes : avertissement -


def test_d3_cibles_identiques_bornes_partiellement_secantes_avertissement(
    planificateur, nature_evenement, session
):
    ServicePeriodeCalendrier.creer(
        planificateur,
        _donnees(nature_evenement, "Première", _instant(2, 8), _instant(6, 8), sessions=[session]),
    )

    seconde = ServicePeriodeCalendrier.creer(
        planificateur,
        _donnees(nature_evenement, "Seconde", _instant(4, 8), _instant(8, 8), sessions=[session]),
    )

    assert any(a["code"] == "periode_chevauchement" for a in seconde.avertissements)


# --- D4 — intersection partielle des ensembles de cibles -------------------


def test_d4_intersection_partielle_des_cibles_avertissement_nomme_l_intersection(
    planificateur, nature_evenement, session, autre_session, troisieme_session
):
    """A et B contre B et C : la session commune est B (`autre_session`)."""
    ServicePeriodeCalendrier.creer(
        planificateur,
        _donnees(
            nature_evenement,
            "Conférence AB",
            _instant(2, 8),
            _instant(6, 8),
            sessions=[session, autre_session],
        ),
    )

    periode_bc = ServicePeriodeCalendrier.creer(
        planificateur,
        _donnees(
            nature_evenement,
            "Conférence BC",
            _instant(4, 8),
            _instant(8, 8),
            sessions=[autre_session, troisieme_session],
        ),
    )

    avertissements = [
        a["message"] for a in periode_bc.avertissements if a["code"] == "periode_chevauchement"
    ]
    assert any("Conférence AB" in message for message in avertissements)
    assert any(autre_session.intitule in message for message in avertissements)
    assert not any(session.intitule in message for message in avertissements)
    assert not any(troisieme_session.intitule in message for message in avertissements)


# --- D5 — portées disjointes, bornes sécantes : aucun avertissement --------


def test_d5_portees_disjointes_bornes_secantes_acceptees_sans_avertissement(
    planificateur, nature_evenement, session, autre_session
):
    ServicePeriodeCalendrier.creer(
        planificateur,
        _donnees(nature_evenement, "Bivouac A", _instant(2, 8), _instant(6, 8), sessions=[session]),
    )

    bivouac_b = ServicePeriodeCalendrier.creer(
        planificateur,
        _donnees(
            nature_evenement, "Bivouac B", _instant(4, 8), _instant(8, 8), sessions=[autre_session]
        ),
    )

    assert not [a for a in bivouac_b.avertissements if a["code"] == "periode_chevauchement"]


# --- F1/F2 — E3 : bornes hors des dates d'une session ciblée ---------------


def test_f1_periode_ciblant_une_session_bornes_hors_dates_accepte_avec_avertissement(
    planificateur, nature_evenement, session
):
    hors_dates_debut = datetime.datetime.combine(
        session.date_fin + datetime.timedelta(days=10), datetime.time(8, 0), tzinfo=datetime.UTC
    )
    hors_dates_fin = hors_dates_debut + datetime.timedelta(hours=2)

    periode = ServicePeriodeCalendrier.creer(
        planificateur,
        _donnees(
            nature_evenement, "Examen tardif", hors_dates_debut, hors_dates_fin, sessions=[session]
        ),
    )

    assert any(a["code"] == "periode_hors_dates_session" for a in periode.avertissements)


def test_f2_deux_sessions_ciblees_une_seule_hors_dates_avertissement_la_nomme(
    planificateur, nature_evenement, session, autre_session
):
    debut_commun = datetime.datetime.combine(
        autre_session.date_debut, datetime.time(8, 0), tzinfo=datetime.UTC
    )
    fin_commune = debut_commun + datetime.timedelta(hours=2)
    assert debut_commun.date() < session.date_debut or fin_commune.date() > session.date_fin

    periode = ServicePeriodeCalendrier.creer(
        planificateur,
        _donnees(
            nature_evenement,
            "Conférence décalée",
            debut_commun,
            fin_commune,
            sessions=[session, autre_session],
        ),
    )

    messages_hors_dates = [
        a["message"] for a in periode.avertissements if a["code"] == "periode_hors_dates_session"
    ]
    assert any(session.intitule in message for message in messages_hors_dates)
    assert not any(autre_session.intitule in message for message in messages_hors_dates)
