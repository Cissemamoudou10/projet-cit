"""Écran dédié des procès-verbaux — US-EVAL-07, V9/V10. Orchestre, ne
décide rien : toute la logique vit dans
`evaluations.services.proces_verbal.ServiceProcesVerbal`.
"""

from django.contrib import messages
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from administration.habilitations import exige_habilitation
from evaluations.models import TypeProcesVerbal
from evaluations.services.evaluation import ServiceEvaluation
from evaluations.services.proces_verbal import (
    PERMISSION_ECRITURE,
    PERMISSION_LECTURE,
    ServiceProcesVerbal,
)
from noyau.exceptions import ErreurIntrouvable, ErreurValidation
from noyau.habilitations import a_permission
from organisation.services.session import ServiceSession


def _session_ou_404(pk):
    try:
        return ServiceSession.obtenir(pk)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur


def _evaluation_depuis_post(request):
    evaluation_pk = request.POST.get("evaluation_pk")
    return ServiceEvaluation.obtenir(evaluation_pk) if evaluation_pk else None


def _url_proces_verbaux(pk):
    return reverse("evaluations:proces_verbaux", args=[pk])


@exige_habilitation(PERMISSION_LECTURE)
def vue_proces_verbaux(request, session_pk):
    session = _session_ou_404(session_pk)
    proces_verbaux = ServiceProcesVerbal.lister(request.user, session)
    peut_generer = a_permission(request.user, PERMISSION_ECRITURE)
    evaluations = (
        ServiceProcesVerbal.evaluations_disponibles(request.user, session) if peut_generer else []
    )
    return render(
        request,
        "evaluations/proces_verbaux.html",
        {
            "session": session,
            "proces_verbaux": proces_verbaux,
            "evaluations": evaluations,
            "peut_generer": peut_generer,
            "url_apercu": reverse("evaluations:apercu_proces_verbal", args=[session.pk]),
        },
    )


@exige_habilitation(PERMISSION_ECRITURE)
def vue_apercu_proces_verbal(request, session_pk):
    session = _session_ou_404(session_pk)
    type_pv = request.POST.get("type_pv", TypeProcesVerbal.FIN_DE_FORMATION)
    try:
        evaluation = _evaluation_depuis_post(request)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur
    numero = request.POST.get("numero", "")
    apercu = ServiceProcesVerbal.apercu(request.user, session, evaluation)
    return render(
        request,
        "evaluations/proces_verbal_apercu.html",
        {
            "session": session,
            "evaluation": evaluation,
            "type_pv": type_pv,
            "numero": numero,
            "apercu": apercu,
            "url_generer": reverse("evaluations:generer_proces_verbal", args=[session.pk]),
            "url_annuler": _url_proces_verbaux(session.pk),
        },
    )


@exige_habilitation(PERMISSION_ECRITURE)
def vue_generer_proces_verbal(request, session_pk):
    session = _session_ou_404(session_pk)
    type_pv = request.POST.get("type_pv", TypeProcesVerbal.FIN_DE_FORMATION)
    try:
        evaluation = _evaluation_depuis_post(request)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur
    numero = request.POST.get("numero", "")
    try:
        ServiceProcesVerbal.generer(request.user, session, type_pv, evaluation, numero)
    except ErreurValidation as erreur:
        messages.error(request, str(erreur))
    else:
        messages.success(request, "Procès-verbal généré.")
    return redirect(_url_proces_verbaux(session.pk))


@exige_habilitation(PERMISSION_LECTURE)
def vue_telecharger_proces_verbal(request, pk):
    try:
        proces_verbal = ServiceProcesVerbal.obtenir(pk)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur
    pdf = ServiceProcesVerbal.telecharger(request.user, proces_verbal)
    reponse = HttpResponse(pdf, content_type="application/pdf")
    nom = f"proces_verbal_{proces_verbal.pk}_v{proces_verbal.version}.pdf"
    reponse["Content-Disposition"] = f'attachment; filename="{nom}"'
    return reponse
