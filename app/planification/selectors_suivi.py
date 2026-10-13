"""Lectures du domaine suivi — US-SUI-05 (prompt 44, Temps 2) et US-SUI-01
(prompt 44, Temps 3, R6).

Séparé de `selectors.py` (déjà proche de la limite de taille) plutôt que d'y
ajouter une préoccupation de plus — `.claude/rules/python.md`.
"""

from django.utils import timezone

from planification.models import NonExecution
from planification.services.contraintes import volumes_realises_par_element_brigade


def non_executions_des_lignes(lignes_ids):
    """Ligne -> `NonExecution`, pour les lignes données, en UNE requête —
    jamais une par cellule affichée sur la grille de consultation
    (`.claude/rules/python.md`, aucune requête dans une boucle)."""
    if not lignes_ids:
        return {}
    return {
        non_execution.ligne_id: non_execution
        for non_execution in NonExecution.objects.filter(ligne_id__in=lignes_ids)
    }


def volume_realise_total_brigade(brigade):
    """R6 (US-SUI-01, D-108) : réalisé à l'instant de l'appel, toutes
    matières confondues, pour UNE brigade — fournisseur de
    `noyau.services.parametres.ResolveurVolumeRealiseBrigade`, installé par
    `planification.apps.PlanificationConfig.ready`."""
    par_element_brigade = volumes_realises_par_element_brigade(
        timezone.now(), brigade_ids=[brigade.pk]
    )
    return sum(par_element_brigade.values())
