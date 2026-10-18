"""Écran du rapprochement prescrit/programmé/réalisé — US-SUI-01 (prompt 44,
Temps 3). Lecture seule : orchestre, ne décide rien (`.claude/rules/
vues.md`) — tout le calcul vit dans `ServiceSuivi.rapprochement`.
"""

import datetime

from django.shortcuts import render
from django.utils import timezone

from administration.habilitations import exige_habilitation
from noyau.pagination import paginer
from planification.selectors import brigades_pour_filtre
from planification.selectors_ecart_volume import decorer_rapprochement
from planification.selectors_rapprochement import formations_pour_filtre, sessions_pour_filtre
from planification.services.suivi import PERMISSION_LECTURE, ServiceSuivi

MESSAGE_SANS_PROGRAMME_AFFICHE = (
    "Aucun programme affiché pour cette brigade sur la période : le réalisé "
    "n'est pas encore connaissable, ce n'est pas un retard (E1)."
)


def _periode_fin(request):
    """R1 : T = maintenant, ou la fin de la période filtrée."""
    valeur = request.GET.get("jusquau")
    if not valeur:
        return None
    try:
        jour = datetime.date.fromisoformat(valeur)
    except ValueError:
        return None
    fin_du_jour = datetime.datetime.combine(jour, datetime.time.max)
    return timezone.make_aware(fin_du_jour)


@exige_habilitation(PERMISSION_LECTURE)
def vue_rapprochement(request):
    formation_id = request.GET.get("formation") or None
    session_id = request.GET.get("session") or None
    brigade_id = request.GET.get("brigade") or None
    periode_fin = _periode_fin(request)

    groupes = ServiceSuivi.rapprochement(
        request.user,
        formation_id=formation_id,
        session_id=session_id,
        brigade_id=brigade_id,
        periode_fin=periode_fin,
    )
    # US-PLAN-07, E2 : même mise en évidence des écarts de volume horaire
    # que sur la consultation du programme — aucune requête de plus, une
    # simple décoration des groupes déjà calculés.
    groupes = decorer_rapprochement(groupes)
    page = paginer(groupes, request.GET.get("page"))
    return render(
        request,
        "planification/rapprochement.html",
        {
            "page": page,
            "message_sans_programme_affiche": MESSAGE_SANS_PROGRAMME_AFFICHE,
            "formations": formations_pour_filtre(),
            "sessions": sessions_pour_filtre(),
            "brigades": brigades_pour_filtre(),
            "a_la_date": periode_fin or timezone.now(),
        },
    )
