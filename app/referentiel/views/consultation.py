"""Écran de consultation consolidée du référentiel — US-REF-07, CU-P2-08.

Accessible en lecture seule aux quatre profils habilités (`referentiel_lecture`)
— pédagogique compris, une vue d'ensemble lui sert aussi (Prompt 11, § 3).
N'écrit jamais rien : orchestre la même lecture que les quatre écrans de
composition, sans mise en cache (Prompt 11, § 2.2).
"""

from django.http import Http404
from django.shortcuts import render

from administration.habilitations import exige_habilitation
from noyau.exceptions import ErreurIntrouvable
from referentiel.services.formation import ServiceFormation
from referentiel.services.referentiel import ServiceReferentiel
from referentiel.views.prerequis import preparer_donnees_prerequis


def _formation_ou_404(pk):
    try:
        return ServiceFormation.obtenir(pk)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur


@exige_habilitation(ServiceReferentiel.PERMISSION_LECTURE)
def vue_consultation_formation(request, pk):
    formation = _formation_ou_404(pk)
    contexte = preparer_donnees_prerequis(request, formation)
    contexte.update(
        {
            "formation": formation,
            "ecart": ServiceReferentiel.ecart(formation),
        }
    )
    return render(request, "referentiel/formation_consultation.html", contexte)
