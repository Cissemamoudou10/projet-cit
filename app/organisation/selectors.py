"""Effectifs réels groupés — sélecteur public (prompt 38, D-210). Une seule
définition de l'effectif réel : `ServiceBrigade.effectif_reel` s'appuie dessus.
"""

from django.db.models import Count

from organisation.models import AffectationBrigade, Stagiaire


def _affectations_ouvertes_non_radiees(ids_brigades):
    """Le filtre unique de l'effectif réel — non radiés, affectation
    ouverte (CLS-00 § 9) — troisième appelant (US-EVAL-06, M7) : extrait ici
    plutôt que recopié une troisième fois (`.claude/rules/python.md`,
    « deux occurrences tolérées, trois c'est déjà trop tard »)."""
    ids = list(ids_brigades)
    if not ids:
        return AffectationBrigade.objects.none()
    return AffectationBrigade.objects.filter(
        brigade_id__in=ids, date_fin__isnull=True, stagiaire__radie=False
    )


def effectifs_reels(ids_brigades) -> dict:
    """Brigade -> stagiaires non radiés à affectation ouverte, une requête pour N brigades."""
    ids = list(ids_brigades)
    if not ids:
        return {}
    comptes = dict(
        _affectations_ouvertes_non_radiees(ids)
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


def affectations_actives_des_brigades(ids_brigades):
    """Mêmes lignes encore, groupées par brigade cette fois (US-EVAL-06,
    M7 : rang en brigade a besoin du rattachement, pas seulement de la
    liste à plat). Une requête, quel que soit le nombre de brigades."""
    return _affectations_ouvertes_non_radiees(ids_brigades).select_related("stagiaire", "brigade")
