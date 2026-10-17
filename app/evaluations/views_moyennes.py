"""Écran dédié des moyennes et du classement — US-EVAL-06, M8 : visibilité
réservée à `evaluations_ecriture`, même confidentialité que les notes.
Orchestre, ne décide rien : toute la logique vit dans
`evaluations.services.moyenne.ServiceMoyenne`.
"""

from django.http import Http404
from django.shortcuts import render

from administration.habilitations import exige_habilitation
from evaluations.services.moyenne import PERMISSION_ECRITURE, ServiceMoyenne
from noyau.exceptions import ErreurIntrouvable
from organisation.services.session import ServiceSession


def _session_ou_404(pk):
    try:
        return ServiceSession.obtenir(pk)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur


def _regrouper_resultats(resultats):
    par_brigade: dict = {}
    for resultat in resultats:
        par_brigade.setdefault(resultat.brigade, []).append(resultat)
    for resultats_brigade in par_brigade.values():
        resultats_brigade.sort(key=lambda resultat: resultat.rang_brigade)
    return par_brigade


def _regrouper_manquants(manquants):
    """M5 : par module, puis par brigade — à l'affichage seulement,
    aucune règle métier dans cette vue."""
    par_module: dict = {}
    for manquant in manquants:
        par_brigade = par_module.setdefault(manquant.module, {})
        par_brigade.setdefault(manquant.brigade, []).append(manquant.stagiaire)
    return par_module


@exige_habilitation(PERMISSION_ECRITURE)
def vue_moyennes(request, session_pk):
    session = _session_ou_404(session_pk)
    rapport = ServiceMoyenne.calculer(request.user, session)
    return render(
        request,
        "evaluations/moyennes.html",
        {
            "session": session,
            "par_brigade": _regrouper_resultats(rapport.resultats),
            "manquants_par_module": _regrouper_manquants(rapport.manquants),
            "modules_ignores": rapport.modules_ignores,
        },
    )
