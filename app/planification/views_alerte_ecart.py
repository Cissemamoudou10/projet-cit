"""Écran des alertes d'écart significatif — US-SUI-02, A3 (prompt 48).

Lecture seule : orchestre, ne décide rien (`.claude/rules/vues.md`) — tout le
calcul vit dans `selectors_alerte_ecart.alertes`.
"""

from django.shortcuts import render

from administration.habilitations import exige_habilitation
from noyau.pagination import paginer
from planification.selectors import brigades_pour_filtre
from planification.selectors_alerte_ecart import alertes
from planification.selectors_rapprochement import sessions_pour_filtre
from planification.services.suivi import PERMISSION_LECTURE


@exige_habilitation(PERMISSION_LECTURE)
def vue_alertes(request):
    """A3 : filtrable par session et par brigade, chaque ligne mène au
    détail de la matière dans le rapprochement — jamais un second filtre
    de brigades recopié, `brigades_pour_filtre` est déjà partagé avec
    l'écran du rapprochement (US-SUI-01)."""
    session_id = request.GET.get("session") or None
    brigade_id = request.GET.get("brigade") or None
    groupes = alertes(session_id=session_id, brigade_id=brigade_id)
    page = paginer(groupes, request.GET.get("page"))
    return render(
        request,
        "planification/alertes_ecart.html",
        {
            "page": page,
            "sessions": sessions_pour_filtre(),
            "brigades": brigades_pour_filtre(),
        },
    )
