"""Vues de composition des brigades d'une session — CU-P3-02. Orchestrent,
ne décident rien : toute la logique métier vit dans
organisation.services.brigade.ServiceBrigade.
"""

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from administration.habilitations import exige_habilitation
from noyau.exceptions import ErreurIntrouvable, ErreurValidation
from organisation.forms import FormulaireBrigade
from organisation.services.brigade import ServiceBrigade
from organisation.services.session import ServiceSession


def _session_ou_404(pk):
    try:
        return ServiceSession.obtenir(pk)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur


def _brigade_ou_404(pk):
    try:
        return ServiceBrigade.obtenir(pk)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur


def _rendre_page(request, session, *, formulaire_creation=None):
    contexte = {
        "session": session,
        "brigades": ServiceBrigade.lister(request.user, session),
        "indicateur": ServiceBrigade.indicateur_effectif(session),
        "formulaire_creation": formulaire_creation or FormulaireBrigade(),
        "url_creer": reverse("organisation:creer_brigade", args=[session.pk]),
    }
    return render(request, "organisation/brigade_liste.html", contexte)


@exige_habilitation(ServiceBrigade.PERMISSION_LECTURE)
def vue_brigades_session(request, session_pk):
    session = _session_ou_404(session_pk)
    return _rendre_page(request, session)


@require_POST
@exige_habilitation(ServiceBrigade.PERMISSION_ECRITURE)
def vue_creer_brigade(request, session_pk):
    session = _session_ou_404(session_pk)
    formulaire = FormulaireBrigade(request.POST)
    if formulaire.is_valid():
        try:
            brigade = ServiceBrigade.creer(request.user, session, formulaire.cleaned_data)
        except ErreurValidation as erreur:
            messages.error(request, str(erreur))
        else:
            messages.success(request, f"« {brigade.designation} » constituée.")
            for item in brigade.avertissements:
                messages.warning(request, item["message"])
            return redirect("organisation:brigades_session", session.pk)
    return _rendre_page(request, session, formulaire_creation=formulaire)


@require_POST
@exige_habilitation(ServiceBrigade.PERMISSION_ECRITURE)
def vue_modifier_brigade(request, session_pk, brigade_pk):
    session = _session_ou_404(session_pk)
    brigade = _brigade_ou_404(brigade_pk)
    formulaire = FormulaireBrigade(request.POST)
    if formulaire.is_valid():
        try:
            ServiceBrigade.modifier(request.user, brigade, formulaire.cleaned_data)
        except ErreurValidation as erreur:
            messages.error(request, str(erreur))
        else:
            messages.success(request, f"« {brigade.designation} » modifiée.")
    else:
        messages.error(request, "Désignation ou effectif non valide.")
    return redirect("organisation:brigades_session", session.pk)


@exige_habilitation(ServiceBrigade.PERMISSION_ECRITURE)
def vue_confirmer_suppression_brigade(request, session_pk, brigade_pk):
    session = _session_ou_404(session_pk)
    brigade = _brigade_ou_404(brigade_pk)
    if request.method == "POST":
        try:
            ServiceBrigade.supprimer(request.user, brigade)
        except ErreurValidation as erreur:
            messages.error(request, str(erreur))
        else:
            messages.success(request, f"« {brigade.designation} » supprimée.")
        return redirect("organisation:brigades_session", session.pk)
    return render(
        request,
        "noyau/gestion/confirmer_suppression.html",
        {
            "titre_dialogue": f"Supprimer « {brigade.designation} »",
            "texte_explication": f"« {brigade.designation} » sera supprimée définitivement.",
            "url_annuler": reverse("organisation:brigades_session", args=[session.pk]),
        },
    )
