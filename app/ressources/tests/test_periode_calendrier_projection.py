"""US-PLAN-01, Groupe E — RG-30 bis : les dates des sessions sont
PROJETÉES depuis `organisation.Session`, jamais saisies au calendrier.
Données entièrement fictives.
"""

import datetime

from django.urls import reverse

from organisation.services.session import ServiceSession
from ressources.models import PeriodeCalendrier
from ressources.services.periode_calendrier import ServicePeriodeCalendrier

# --- E1 — l'ouverture d'une session ne crée aucune période -----------------


def test_e1_ouverture_d_une_session_ne_cree_aucune_periode_de_calendrier(session):
    assert PeriodeCalendrier.objects.count() == 0


# --- E2 — la vue annuelle affiche les bandes de session, lues depuis Session


def test_e2_vue_annuelle_affiche_les_bandes_de_session_lues_depuis_session(
    client, planificateur, session
):
    client.force_login(planificateur)
    annee = (
        session.date_debut.year if session.date_debut.month >= 9 else session.date_debut.year - 1
    )

    reponse = client.get(reverse("ressources:calendrier_annuel"), {"annee": annee})

    assert reponse.status_code == 200
    assert session.intitule.encode() in reponse.content


# --- E3 — modifier les dates d'une session déplace sa bande, jamais une période


def test_e3_modification_des_dates_de_session_ne_touche_aucune_periode(
    redacteur, planificateur, session
):
    nouvelle_date_debut = session.date_debut + datetime.timedelta(days=5)
    nouvelle_date_fin = session.date_fin + datetime.timedelta(days=5)

    ServiceSession.modifier(
        redacteur,
        session.pk,
        {
            "formation": session.formation,
            "intitule": session.intitule,
            "date_debut": nouvelle_date_debut,
            "date_fin": nouvelle_date_fin,
            "effectif_attendu": session.effectif_attendu,
        },
        session.modifie_le,
    )

    assert PeriodeCalendrier.objects.count() == 0
    bandes = ServicePeriodeCalendrier.bandes_sessions(
        planificateur, nouvelle_date_debut, nouvelle_date_debut
    )
    assert session.pk in [bande.pk for bande in bandes]
