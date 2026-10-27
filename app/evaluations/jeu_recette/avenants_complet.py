"""Avenants posés sur W0, après affichage — Prompt 51, § 2.4. Un avenant
« déplacement » (séance M6 d'EXP1) et un avenant « remplacement
d'instructeur » (M6, I6 -> I8). Posés lundi de W0, avant l'heure réelle de
début de la séance visée (`_refuser_si_commencee`, `planification.services.
modification`)."""

import datetime

from django.utils import timezone

from evaluations.jeu_recette.creneaux import creneau_libre
from evaluations.jeu_recette.semaines import jour_de_semaine, semaine
from planification.models import LigneProgramme, NatureAvenant
from planification.selectors import grille_active_avec_creneaux
from planification.services.ecriture import ServiceEcritureSeance
from planification.services.modification import Avenantage

LUNDI_ISO, MARDI_ISO, MERCREDI_ISO, JEUDI_ISO, VENDREDI_ISO, SAMEDI_ISO = 1, 2, 3, 4, 5, 6
MOTIF_AVENANT_DEPLACEMENT = "Déplacement de séance (recette, § 2.4)."
MOTIF_AVENANT_REMPLACEMENT = "Remplacement d'instructeur (recette, § 2.4)."
AVERTISSEMENT_SANS_M6 = (
    "  AVERTISSEMENT : aucune séance M6 d'EXP1 cette semaine — avenants du § 2.4 "
    "non posés, à signaler (voir docs/recette/JEUX-DE-DONNEES-PHASE-6.md)."
)
AVERTISSEMENT_SANS_CRENEAU = (
    "  AVERTISSEMENT : aucun créneau libre cette semaine pour EXP1, quel que soit "
    "le jour — avenant « déplacement » non posé, à signaler (voir docs/recette/"
    "JEUX-DE-DONNEES-PHASE-6.md)."
)


def _lignes_m6_exp1(programme_w0, exp1, element_m6):
    return list(
        LigneProgramme.objects.filter(
            seance__programme=programme_w0, brigade=exp1, seance__element_referentiel=element_m6
        )
        .select_related("seance")
        .order_by("seance__debut")
    )


def _premier_jour_libre(programme_w0, exp1, date_reference, creneaux):
    """Jeudi préféré (§ 2.4, « lundi -> jeudi ») mais la semaine peut être
    densément remplie : retient le premier autre jour qui offre réellement
    un créneau libre pour EXP1, plutôt que d'échouer tout le chargement
    pour un jour précis que rien n'impose absolument. Rend `(jour, creneau)`
    ou `(None, None)`."""
    for jour_iso, jour_date in (
        (JEUDI_ISO, jour_de_semaine(date_reference, 0, JEUDI_ISO)),
        (VENDREDI_ISO, jour_de_semaine(date_reference, 0, VENDREDI_ISO)),
        (MERCREDI_ISO, jour_de_semaine(date_reference, 0, MERCREDI_ISO)),
        (MARDI_ISO, jour_de_semaine(date_reference, 0, MARDI_ISO)),
        (SAMEDI_ISO, jour_de_semaine(date_reference, 0, SAMEDI_ISO)),
    ):
        creneau = creneau_libre(programme_w0, exp1, jour_iso, creneaux)
        if creneau is not None:
            return jour_date, creneau
    return None, None


def _poser_deplacement(contexte, seance, jour_cible, creneau):
    nouveau_debut = timezone.make_aware(datetime.datetime.combine(jour_cible, creneau.heure_debut))
    nouvelle_fin = timezone.make_aware(datetime.datetime.combine(jour_cible, creneau.heure_fin))
    ServiceEcritureSeance.modifier_seance(
        contexte.agissant_plan,
        seance,
        {"debut": nouveau_debut, "fin": nouvelle_fin},
        avenant=Avenantage(motif=MOTIF_AVENANT_DEPLACEMENT, nature=NatureAvenant.DEPLACEMENT),
    )
    contexte.stdout.write(
        f"  Avenant « déplacement » posé sur une séance M6 d'EXP1 (-> {jour_cible.isoformat()})."
    )


def _poser_remplacement(contexte, seance):
    seance.refresh_from_db()
    ServiceEcritureSeance.modifier_seance(
        contexte.agissant_plan,
        seance,
        {"instructeur": contexte.instructeurs["I8"]},
        avenant=Avenantage(
            motif=MOTIF_AVENANT_REMPLACEMENT, nature=NatureAvenant.REMPLACEMENT_INSTRUCTEUR
        ),
    )
    contexte.stdout.write(
        "  Avenant « remplacement d'instructeur » posé sur une séance M6 d'EXP1 (I6 -> I8)."
    )


def poser_avenants_w0(contexte, programme_w0):
    from freezegun import freeze_time

    lignes_m6_exp1 = _lignes_m6_exp1(programme_w0, contexte.exp1, contexte.elements_f6["M6"])
    if not lignes_m6_exp1:
        contexte.stdout.write(AVERTISSEMENT_SANS_M6)
        return

    lundi_w0 = semaine(contexte.date_reference, 0)
    _, creneaux = grille_active_avec_creneaux()
    with freeze_time(timezone.make_aware(datetime.datetime.combine(lundi_w0, datetime.time(6, 0)))):
        jour_cible, creneau = _premier_jour_libre(
            programme_w0, contexte.exp1, contexte.date_reference, creneaux
        )
        if creneau is None:
            contexte.stdout.write(AVERTISSEMENT_SANS_CRENEAU)
        else:
            _poser_deplacement(contexte, lignes_m6_exp1[0].seance, jour_cible, creneau)

        seance_remplacement = (
            lignes_m6_exp1[1].seance if len(lignes_m6_exp1) > 1 else lignes_m6_exp1[0].seance
        )
        _poser_remplacement(contexte, seance_remplacement)
