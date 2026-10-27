"""Suivi ajouté par l'état `complet` — Prompt 51, § 2.6. Aucune horloge
simulée nécessaire ici : les séances de W-2/W-1 sont déjà réellement passées
par rapport à la date de référence (elle vit dans W0), et `editer_progression`
ne regarde que l'état du programme (AFFICHÉ), jamais une date."""

from planification.models import LigneProgramme
from planification.services.suivi import ServiceSuivi

MOTIF_NON_EXECUTION_W2 = "Instructeur en mission."
MOTIF_NON_EXECUTION_W1_EXP2 = "Brigade de garde."


def _declarer_non_execution_w2(contexte, programme_w2):
    ligne = (
        LigneProgramme.objects.filter(seance__programme=programme_w2, brigade=contexte.exp2)
        .select_related("seance")
        .order_by("seance__debut")
        .first()
    )
    if ligne is None:
        contexte.stdout.write(
            "  AVERTISSEMENT : aucune ligne d'EXP2 en W-2 — non-exécution (a) non posée."
        )
        return
    ServiceSuivi.declarer_non_execution(contexte.agissant_plan, ligne, MOTIF_NON_EXECUTION_W2)
    contexte.stdout.write(
        "  Non-exécution déclarée sur une séance d'EXP2 en W-2 (instructeur en mission)."
    )


def _declarer_non_execution_w1(contexte, programme_w1):
    ligne = LigneProgramme.objects.filter(
        seance__programme=programme_w1,
        brigade=contexte.exp2,
        seance__element_referentiel=contexte.elements_f6["M2"],
    ).first()
    if ligne is None:
        contexte.stdout.write(
            "  AVERTISSEMENT : pas de ligne EXP2 sur la séance M2 regroupée de W-1 — "
            "non-exécution (b) non posée."
        )
        return
    ServiceSuivi.declarer_non_execution(contexte.agissant_plan, ligne, MOTIF_NON_EXECUTION_W1_EXP2)
    contexte.stdout.write(
        "  Non-exécution déclarée sur la ligne d'EXP2 de la séance M2 regroupée de W-1 "
        "(brigade de garde) — EXP1 reste exécutée."
    )


def charger_non_executions_complet(contexte, programme_w2, programme_w1):
    """(a) une séance d'EXP2 en W-2 ; (b) sur la séance M2 regroupée de
    W-1, la ligne d'EXP2 SEULEMENT (EXP1 reste déclarée exécutée)."""
    _declarer_non_execution_w2(contexte, programme_w2)
    _declarer_non_execution_w1(contexte, programme_w1)


def charger_progression_realisee_complet(contexte, programme_w2):
    """Une édition de W-2, par `u_plan`, jamais signée (§ 2.6 : `--etat
    complet` ne couvre pas la signature de la progression)."""
    ServiceSuivi.editer_progression(contexte.agissant_plan, programme_w2)
    contexte.stdout.write("  Progression réalisée de W-2 éditée (non signée).")
