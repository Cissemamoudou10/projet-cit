"""Calendrier et indisponibilités ajoutés par l'état `socle-planif` —
Prompt 53, Temps 1. Domaine `lieux_calendrier`, propre à la cellule
planification (`agissant_plan`, u_plan) — même répartition que l'état
`complet` (`ressources_complet.py`)."""

import datetime

from django.utils import timezone

from evaluations.jeu_recette.donnees_socle_planif import (
    DECALAGE_SEMAINE_CONFERENCE,
    DECALAGE_SEMAINE_CONGE,
    HEURE_DEBUT_CONFERENCE,
    HEURE_FIN_CONFERENCE,
    INTITULE_CONFERENCE,
    INTITULE_CONGE,
    MOTIF_INDISPONIBILITE_I1,
    MOTIF_INDISPONIBILITE_L5,
    NATURE_CONFERENCE,
    NATURE_CONGE,
)
from evaluations.jeu_recette.semaines import jour_de_semaine
from ressources.models import NatureEvenement
from ressources.services.indisponibilite_instructeur import ServiceIndisponibiliteInstructeur
from ressources.services.indisponibilite_lieu import ServiceIndisponibiliteLieu
from ressources.services.periode_calendrier import DonneesPeriode, ServicePeriodeCalendrier

LUNDI_ISO, MARDI_ISO, JEUDI_ISO, VENDREDI_ISO = 1, 2, 4, 5


def _instant(jour, heure=None):
    heure = heure or datetime.time.min
    return timezone.make_aware(datetime.datetime.combine(jour, heure))


def _lendemain_minuit(jour):
    return _instant(jour + datetime.timedelta(days=1))


def charger_calendrier_socle_planif(agissant_plan, date_reference, stdout):
    """Conférence bloquante (mardi de W+1, 08:00-09:45) et congé (vendredi de
    W+3, journée entière) — centre entier dans les deux cas (`sessions` et
    `brigades` vides), effet par défaut de la nature (déjà « bloquant »)."""
    mardi_w1 = jour_de_semaine(date_reference, DECALAGE_SEMAINE_CONFERENCE, MARDI_ISO)
    heure_debut, heure_fin = HEURE_DEBUT_CONFERENCE, HEURE_FIN_CONFERENCE
    ServicePeriodeCalendrier.creer(
        agissant_plan,
        DonneesPeriode(
            nature=NatureEvenement.objects.get(libelle=NATURE_CONFERENCE),
            intitule=INTITULE_CONFERENCE,
            debut=_instant(mardi_w1, datetime.time(*heure_debut)),
            fin=_instant(mardi_w1, datetime.time(*heure_fin)),
            effet="",
            sessions=[],
            brigades=[],
        ),
    )
    vendredi_w3 = jour_de_semaine(date_reference, DECALAGE_SEMAINE_CONGE, VENDREDI_ISO)
    ServicePeriodeCalendrier.creer(
        agissant_plan,
        DonneesPeriode(
            nature=NatureEvenement.objects.get(libelle=NATURE_CONGE),
            intitule=INTITULE_CONGE,
            debut=_instant(vendredi_w3),
            fin=_lendemain_minuit(vendredi_w3),
            effet="",
            sessions=[],
            brigades=[],
        ),
    )
    stdout.write("  2 périodes de calendrier ajoutées (conférence W+1, congé W+3).")


def charger_indisponibilites_socle_planif(agissant_plan, instructeurs, lieux, date_reference, stdout):
    """I1 : jeudi de W+1 au lundi de W+2 inclus (motif « mission », période
    fusionnée de R00-RES-08). L5 : lundi et mardi de W+2 inclus."""
    jeudi_w1 = jour_de_semaine(date_reference, 1, JEUDI_ISO)
    lundi_w2 = jour_de_semaine(date_reference, 2, LUNDI_ISO)
    ServiceIndisponibiliteInstructeur.confirmer(
        agissant_plan,
        instructeurs["I1"],
        _instant(jeudi_w1),
        _lendemain_minuit(lundi_w2),
        MOTIF_INDISPONIBILITE_I1,
    )
    mardi_w2 = jour_de_semaine(date_reference, 2, MARDI_ISO)
    ServiceIndisponibiliteLieu.declarer(
        agissant_plan,
        lieux["L5"],
        _instant(lundi_w2),
        _lendemain_minuit(mardi_w2),
        MOTIF_INDISPONIBILITE_L5,
    )
    stdout.write("  2 indisponibilités ajoutées (I1 jeudi-lundi W+1/W+2, L5 lundi-mardi W+2).")
