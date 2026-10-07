"""Séances recouvertes par une période de calendrier bloquante (D-121 E2,
prompt 42). Lecture seule : l'arbitrage (modifier, déplacer, laisser en
l'état) reste humain, rien n'est supprimé ni déplacé d'office.

Vit dans `planification`, qui peut dépendre de `ressources` — pas l'inverse :
`ressources` ne peut pas appeler `seances_recouvertes`, propre à
`planification` (`tests/architecture/test_couches.py`). C'est pourquoi le
lien part du gabarit de `ressources` (`{% url %}`, aucun import Python) vers
cette vue, qui relit la période par le service de `ressources`.
"""

from django.http import Http404
from django.shortcuts import render

from administration.habilitations import exige_habilitation
from noyau.exceptions import ErreurIntrouvable
from planification.selectors import brigades_de_la_periode, seances_recouvertes
from ressources.services.periode_calendrier import ServicePeriodeCalendrier

PERMISSION_LECTURE = "noyau.programme_lecture"


@exige_habilitation(PERMISSION_LECTURE)
def seances_de_la_periode(request, pk):
    try:
        periode = ServicePeriodeCalendrier.obtenir(pk)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur
    brigades = brigades_de_la_periode(periode)
    seances = seances_recouvertes(brigades, periode.debut, periode.fin)
    return render(
        request,
        "planification/seances_de_la_periode.html",
        {"periode": periode, "seances": seances},
    )
