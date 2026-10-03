"""Effectifs réels groupés — sélecteur public (prompt 38, D-210). Une seule
définition de l'effectif réel : `ServiceBrigade.effectif_reel` s'appuie dessus.
"""

from django.db.models import Count

from organisation.models import AffectationBrigade


def effectifs_reels(ids_brigades) -> dict:
    """Brigade -> stagiaires non radiés à affectation ouverte, une requête pour N brigades."""
    ids = list(ids_brigades)
    if not ids:
        return {}
    comptes = dict(
        AffectationBrigade.objects.filter(
            brigade_id__in=ids, date_fin__isnull=True, stagiaire__radie=False
        )
        .values("brigade_id")
        .annotate(total=Count("pk"))
        .values_list("brigade_id", "total")
    )
    return {pk: comptes.get(pk, 0) for pk in ids}
