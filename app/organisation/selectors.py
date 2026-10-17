"""Effectifs réels groupés — sélecteur public (prompt 38, D-210). Une seule
définition de l'effectif réel : `ServiceBrigade.effectif_reel` s'appuie dessus.
"""

from django.db.models import Count

from organisation.models import AffectationBrigade, Stagiaire


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


def stagiaires_actifs_des_brigades(ids_brigades):
    """Mêmes lignes que `effectifs_reels` compte — non radiés, affectation
    ouverte — pour un appelant qui a besoin des stagiaires eux-mêmes
    (US-EVAL-05, N2), pas seulement de leur nombre. Une requête, quel que
    soit le nombre de brigades."""
    ids = list(ids_brigades)
    if not ids:
        return Stagiaire.objects.none()
    return (
        Stagiaire.objects.filter(
            affectations__brigade_id__in=ids,
            affectations__date_fin__isnull=True,
            radie=False,
        )
        .distinct()
        .order_by("nom", "prenom")
    )
