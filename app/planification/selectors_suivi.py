"""Lectures du domaine suivi — US-SUI-05 (prompt 44, Temps 2).

Séparé de `selectors.py` (déjà proche de la limite de taille) plutôt que d'y
ajouter une préoccupation de plus — `.claude/rules/python.md`.
"""

from planification.models import NonExecution


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
