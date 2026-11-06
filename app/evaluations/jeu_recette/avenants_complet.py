"""Avenants posés sur W0, après affichage — Prompt 51, § 2.4. Un avenant
« déplacement » (séance M6 d'EXP1) et un avenant « remplacement
d'instructeur » (M6, I6 -> I8). Posés lundi de W0, avant l'heure réelle de
début de la séance visée (`_refuser_si_commencee`, `planification.services.
modification`).

K6, prompt 58 (RECETTE-01 B1) : la case que l'avenant « déplacement »
occupera est décidée et, au besoin, libérée PENDANT que `programme_w0` est
encore BROUILLON (`preparer_deplacement_w0`, appelée depuis
`programme_complet.py` avant `_approuver`) — une suppression de séance
n'est admise qu'à ce moment-là (M4). L'avenant lui-même
(`poser_avenants_w0`, après affichage) n'est alors jamais qu'UNE seule
écriture sur M6 : jamais de créneau tampon hors grille, jamais de seconde
séance déplacée pour en libérer une autre."""

import datetime

from django.core.management.base import CommandError
from django.utils import timezone

from evaluations.jeu_recette.creneaux import creneau_libre
from evaluations.jeu_recette.semaines import jour_de_semaine, semaine
from planification.models import LigneProgramme, NatureAvenant
from planification.selectors import grille_active_avec_creneaux
from planification.services.ecriture import ServiceEcritureSeance
from planification.services.modification import Avenantage

LUNDI_ISO, MARDI_ISO, MERCREDI_ISO, JEUDI_ISO, VENDREDI_ISO, SAMEDI_ISO = 1, 2, 3, 4, 5, 6
JOURS_PREFERES = (JEUDI_ISO, VENDREDI_ISO, MERCREDI_ISO, MARDI_ISO, SAMEDI_ISO, LUNDI_ISO)
MOTIF_AVENANT_DEPLACEMENT = "Déplacement de séance (recette, § 2.4)."
MOTIF_AVENANT_REMPLACEMENT = "Remplacement d'instructeur (recette, § 2.4)."
AVERTISSEMENT_SANS_M6 = (
    "  AVERTISSEMENT : aucune séance M6 d'EXP1 cette semaine — avenants du § 2.4 "
    "non posés, à signaler (voir docs/recette/JEUX-DE-DONNEES-PHASE-6.md)."
)
ERREUR_SANS_CRENEAU = (
    "Aucun créneau libre en W0 pour EXP1, sur aucun des six jours de la grille, et "
    "aucune autre séance d'EXP1 cette semaine-là à supprimer pour en libérer un — "
    "avenant « déplacement » impossible à poser sans sortir de W0, ce que "
    "RECETTE-03 exige (K6, prompt 58). Desserrez le jeu de données de l'état "
    "complet plutôt que d'ignorer cet échec."
)


def _lignes_m6_exp1(programme_w0, exp1, element_m6):
    return list(
        LigneProgramme.objects.filter(
            seance__programme=programme_w0, brigade=exp1, seance__element_referentiel=element_m6
        )
        .select_related("seance")
        .order_by("seance__debut")
    )


def _lignes_autres_exp1(programme_w0, exp1, element_m6):
    return list(
        LigneProgramme.objects.filter(seance__programme=programme_w0, brigade=exp1)
        .exclude(seance__element_referentiel=element_m6)
        .select_related("seance")
        .order_by("seance__debut")
    )


def _premier_jour_libre(programme_w0, exp1, date_reference, creneaux):
    """Jeudi préféré (§ 2.4, « lundi -> jeudi ») mais la semaine peut être
    densément remplie : retient le premier autre jour qui offre réellement
    un créneau libre pour EXP1, plutôt que d'échouer tout le chargement
    pour un jour précis que rien n'impose absolument. Les six jours
    opérationnels de la grille sont essayés (lundi compris depuis le K6,
    prompt 58 — RECETTE-01 B1 : jeudi seul omettait lundi sans raison et
    faisait échouer l'avenant alors qu'un créneau y restait libre). Rend
    `(jour, creneau)` ou `(None, None)` si vraiment aucun des six n'en a."""
    for jour_iso, jour_date in (
        (JEUDI_ISO, jour_de_semaine(date_reference, 0, JEUDI_ISO)),
        (VENDREDI_ISO, jour_de_semaine(date_reference, 0, VENDREDI_ISO)),
        (MERCREDI_ISO, jour_de_semaine(date_reference, 0, MERCREDI_ISO)),
        (MARDI_ISO, jour_de_semaine(date_reference, 0, MARDI_ISO)),
        (SAMEDI_ISO, jour_de_semaine(date_reference, 0, SAMEDI_ISO)),
        (LUNDI_ISO, jour_de_semaine(date_reference, 0, LUNDI_ISO)),
    ):
        creneau = creneau_libre(programme_w0, exp1, jour_iso, creneaux)
        if creneau is not None:
            return jour_date, creneau
    return None, None


def _choisir_seance_a_liberer(autres_lignes, jour_actuel_m6_iso):
    """K6, prompt 58 (RECETTE-01 B1) : quand aucun créneau n'est naturellement
    libre (semaine saturée), choisit une AUTRE séance d'EXP1 cette semaine-là
    à supprimer pour libérer son créneau — jamais M6 elle-même. Jour préféré
    (jeudi) d'abord, en excluant le jour actuel de M6 (sinon le déplacement
    n'en serait pas un) ; à défaut, n'importe quel jour fait l'affaire. Rend
    la `Seance` à supprimer, ou `None` s'il n'y en a aucune."""
    par_jour = {}
    for ligne in autres_lignes:
        jour_iso = timezone.localtime(ligne.seance.debut).isoweekday()
        par_jour.setdefault(jour_iso, ligne.seance)
    for jour_iso in JOURS_PREFERES:
        if jour_iso != jour_actuel_m6_iso and jour_iso in par_jour:
            return par_jour[jour_iso]
    for jour_iso in JOURS_PREFERES:
        if jour_iso in par_jour:
            return par_jour[jour_iso]
    return None


def _cible_sur_jour_libre(jour_cible, creneau):
    debut = timezone.make_aware(datetime.datetime.combine(jour_cible, creneau.heure_debut))
    fin = timezone.make_aware(datetime.datetime.combine(jour_cible, creneau.heure_fin))
    return debut, fin


def _liberer_par_suppression(contexte, programme_w0, seance_m6):
    """Supprime une AUTRE séance d'EXP1 de la semaine — admis seulement
    pendant que `programme_w0` est encore BROUILLON (M4) — et rend la case
    ainsi libérée, destinée à M6 une fois le programme affiché."""
    autres_lignes = _lignes_autres_exp1(programme_w0, contexte.exp1, contexte.elements_f6["M6"])
    a_liberer = _choisir_seance_a_liberer(
        autres_lignes, timezone.localtime(seance_m6.debut).isoweekday()
    )
    if a_liberer is None:
        raise CommandError(ERREUR_SANS_CRENEAU)
    cible = (a_liberer.debut, a_liberer.fin)
    jour_libere = timezone.localtime(a_liberer.debut).date()
    ServiceEcritureSeance.supprimer_seance(contexte.agissant_plan, a_liberer)
    contexte.stdout.write(
        f"  Séance d'EXP1 du {jour_libere.isoformat()} supprimée (programme encore "
        "brouillon) pour libérer, pour M6, un créneau dans W0 (semaine saturée — "
        "K6, prompt 58)."
    )
    return cible


def preparer_deplacement_w0(contexte, programme_w0):
    """Pendant que `programme_w0` est encore BROUILLON (K6, prompt 58) :
    détermine la case où l'avenant « déplacement » posera M6 après
    affichage, en la libérant dès maintenant par suppression si aucun
    créneau n'est naturellement libre. Rend `None` si EXP1 n'a aucune
    séance M6 cette semaine (§ 2.4 ne s'applique pas), sinon
    `(lignes_m6_exp1, cible)` — `cible` un couple `(debut, fin)` aware."""
    lignes_m6_exp1 = _lignes_m6_exp1(programme_w0, contexte.exp1, contexte.elements_f6["M6"])
    if not lignes_m6_exp1:
        return None
    seance_m6 = lignes_m6_exp1[0].seance
    _, creneaux = grille_active_avec_creneaux()
    jour_cible, creneau = _premier_jour_libre(
        programme_w0, contexte.exp1, contexte.date_reference, creneaux
    )
    if creneau is not None:
        return lignes_m6_exp1, _cible_sur_jour_libre(jour_cible, creneau)
    return lignes_m6_exp1, _liberer_par_suppression(contexte, programme_w0, seance_m6)


def _poser_deplacement(contexte, seance, nouveau_debut, nouveau_fin):
    ServiceEcritureSeance.modifier_seance(
        contexte.agissant_plan,
        seance,
        {"debut": nouveau_debut, "fin": nouveau_fin},
        avenant=Avenantage(motif=MOTIF_AVENANT_DEPLACEMENT, nature=NatureAvenant.DEPLACEMENT),
    )
    contexte.stdout.write(
        "  Avenant « déplacement » posé sur une séance M6 d'EXP1 "
        f"(-> {timezone.localtime(nouveau_debut).strftime('%Y-%m-%d %H:%M')})."
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


def poser_avenants_w0(contexte, preparation):
    """Appelée APRÈS affichage, avec la `preparation` rendue par
    `preparer_deplacement_w0` (appelée, elle, pendant que le programme était
    encore brouillon — voir le docstring du module)."""
    from freezegun import freeze_time

    if preparation is None:
        contexte.stdout.write(AVERTISSEMENT_SANS_M6)
        return
    lignes_m6_exp1, cible = preparation
    lundi_w0 = semaine(contexte.date_reference, 0)
    with freeze_time(timezone.make_aware(datetime.datetime.combine(lundi_w0, datetime.time(6, 0)))):
        _poser_deplacement(contexte, lignes_m6_exp1[0].seance, *cible)
        seance_remplacement = (
            lignes_m6_exp1[1].seance if len(lignes_m6_exp1) > 1 else lignes_m6_exp1[0].seance
        )
        _poser_remplacement(contexte, seance_remplacement)
