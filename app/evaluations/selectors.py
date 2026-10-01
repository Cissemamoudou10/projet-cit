"""Lectures complexes séparées des services — .claude/rules/python.md.

`seances_de_controle_parmi` est installée comme fournisseur de
`noyau.services.parametres.ResolveurSeancesDeControle` au démarrage de
l'application (`evaluations.apps.EvaluationsConfig.ready`) — A9, Prompt 35.
"""

from evaluations.models import Evaluation


def seances_de_controle_parmi(ids_seances) -> frozenset:
    """Une seule requête pour tout l'ensemble reçu (E2, Prompt 35) : jamais
    une par séance affichée."""
    if not ids_seances:
        return frozenset()
    return frozenset(
        Evaluation.objects.filter(seance_id__in=ids_seances).values_list("seance_id", flat=True)
    )
