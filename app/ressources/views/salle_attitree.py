"""Vues d'affectation d'une salle attitrée à une brigade — CU-P3-03.
Orchestrent, ne décident rien : toute la logique métier vit dans
ressources.services.salle_attitree.ServiceSalleAttitree.

GET et POST sont deux vues distinctes, chacune décorée de la permission qui
lui revient (lecture/écriture) — même patron que `referentiel.views.
referentiel.vue_referentiel_formation`/`vue_rattacher_matiere` : un décorateur
unique posé sur une vue qui bifurque selon la méthode aurait exigé l'écriture
même pour un GET, empêchant les trois profils en lecture seule (pédagogique,
examens, Direction de Formation) de seulement consulter l'écran.
"""

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from administration.habilitations import exige_habilitation
from noyau.exceptions import ErreurIntrouvable, ErreurValidation
from organisation.services.brigade import ServiceBrigade
from ressources.forms import FormulaireAttitrerSalle
from ressources.services.salle_attitree import ServiceSalleAttitree


def _brigade_ou_404(pk):
    try:
        return ServiceBrigade.obtenir(pk)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur


def _rendre_page(request, brigade, salle_actuelle, *, formulaire=None):
    candidats = ServiceSalleAttitree.salles_candidates(request.user, brigade)
    if formulaire is None:
        formulaire = FormulaireAttitrerSalle(salles_candidates=candidats)
    return render(
        request,
        "ressources/salle_attitree_affecter.html",
        {
            "brigade": brigade,
            "session": brigade.session,
            "salle_actuelle": salle_actuelle,
            "form": formulaire,
            "url_soumettre": reverse("ressources:soumettre_salle", args=[brigade.pk]),
            "url_retirer": reverse("ressources:retirer_salle", args=[brigade.pk]),
            "url_brigades_session": reverse(
                "organisation:brigades_session", args=[brigade.session.pk]
            ),
        },
    )


@exige_habilitation(ServiceSalleAttitree.PERMISSION_LECTURE)
def vue_affecter_salle(request, brigade_pk):
    brigade = _brigade_ou_404(brigade_pk)
    salle_actuelle = ServiceSalleAttitree.obtenir_pour_brigade(brigade)
    return _rendre_page(request, brigade, salle_actuelle)


@require_POST
@exige_habilitation(ServiceSalleAttitree.PERMISSION_ECRITURE)
def vue_soumettre_salle(request, brigade_pk):
    brigade = _brigade_ou_404(brigade_pk)
    salle_actuelle = ServiceSalleAttitree.obtenir_pour_brigade(brigade)
    candidats = ServiceSalleAttitree.salles_candidates(request.user, brigade)
    formulaire = FormulaireAttitrerSalle(request.POST, salles_candidates=candidats)
    if formulaire.is_valid():
        lieu = formulaire.cleaned_data["lieu"]
        try:
            if salle_actuelle is None:
                salle = ServiceSalleAttitree.attribuer(request.user, brigade, lieu)
            else:
                salle = ServiceSalleAttitree.modifier(request.user, salle_actuelle, lieu)
        except ErreurValidation as erreur:
            messages.error(request, str(erreur))
        else:
            messages.success(request, f"« {brigade} » attitrée à « {lieu} ».")
            for item in salle.avertissements:
                messages.warning(request, item["message"])
            return redirect("ressources:affecter_salle", brigade.pk)
    return _rendre_page(request, brigade, salle_actuelle, formulaire=formulaire)


@require_POST
@exige_habilitation(ServiceSalleAttitree.PERMISSION_ECRITURE)
def vue_retirer_salle(request, brigade_pk):
    brigade = _brigade_ou_404(brigade_pk)
    salle = ServiceSalleAttitree.obtenir_pour_brigade(brigade)
    if salle is not None:
        ServiceSalleAttitree.retirer(request.user, salle)
        messages.success(request, f"Salle retirée de « {brigade} ».")
    return redirect("ressources:affecter_salle", brigade.pk)
