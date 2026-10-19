"""Écran du tableau de bord des formations — US-SUI-03 (prompt 48).

Lecture seule : orchestre, ne décide rien (`.claude/rules/vues.md`) — tout
le calcul vit dans `selectors_tableau_bord.tableau_de_bord`.
"""

from django.shortcuts import render

from administration.habilitations import exige_habilitation
from planification.selectors_tableau_bord import tableau_de_bord
from planification.services.suivi import PERMISSION_LECTURE


@exige_habilitation(PERMISSION_LECTURE)
def vue_tableau_bord(request):
    """B6 : la matrice fait foi pour la lecture du domaine « suivi » —
    quatre profils, pas seulement les deux cités par le critère (D-284)."""
    return render(
        request,
        "planification/tableau_bord.html",
        {"groupes": tableau_de_bord()},
    )
