"""Écran dédié des sujets — US-EVAL-03, A5 : visibilité réservée à
`evaluations_ecriture`, jamais la permission de lecture séparée des
évaluations. Orchestrent, ne décident rien : toute la logique vit dans
`evaluations.services.sujet.ServiceSujet`.
"""

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse

from administration.habilitations import exige_habilitation
from evaluations.forms import FormulaireChangerRetenu, FormulaireRetenirSujet, FormulaireSujet
from evaluations.services.evaluation import ServiceEvaluation
from evaluations.services.sujet import PERMISSION_ECRITURE, ServiceSujet
from noyau.exceptions import ErreurIntrouvable, ErreurValidation


def _evaluation_ou_404(pk):
    try:
        return ServiceEvaluation.obtenir(pk)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur


def _sujet_ou_404(agissant, pk):
    try:
        return ServiceSujet.obtenir(agissant, pk)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur


def _url_sujets(evaluation_pk):
    return reverse("evaluations:sujets", args=[evaluation_pk])


@exige_habilitation(PERMISSION_ECRITURE)
def vue_sujets(request, pk):
    """C7, A6 : seul écran qui affiche la référence et le rang du sujet
    retenu — chaque GET réussi journalise une consultation
    (`ServiceSujet.consulter`). Un POST, qu'il réussisse ou soit refusé,
    redirige TOUJOURS vers ce même GET (jamais de rendu direct après un
    POST) : la journalisation reste exclusivement liée au GET, jamais
    déclenchée en cascade par une écriture — trouvé en relecture
    (`relecteur-conception`), A6 ne mentionne qu'un GET."""
    evaluation = _evaluation_ou_404(pk)
    if request.method == "POST":
        formulaire = FormulaireSujet(request.POST)
        if formulaire.is_valid():
            try:
                ServiceSujet.enregistrer(request.user, evaluation, formulaire.cleaned_data)
            except ErreurValidation as erreur:
                messages.error(request, str(erreur))
            else:
                messages.success(request, "Sujet enregistré.")
        else:
            messages.error(request, "Référence ou date de dépôt invalide.")
        return redirect(_url_sujets(pk))
    sujets = ServiceSujet.consulter(request.user, evaluation)
    return render(
        request,
        "evaluations/sujets.html",
        {
            "evaluation": evaluation,
            "sujets": sujets,
            "form": FormulaireSujet(),
            "formulaire_retenir": FormulaireRetenirSujet(),
            "formulaire_changer": FormulaireChangerRetenu(),
            "url_liste": reverse("evaluations:detail_evaluation", args=[pk]),
        },
    )


@exige_habilitation(PERMISSION_ECRITURE)
def vue_corriger_sujet(request, pk):
    sujet = _sujet_ou_404(request.user, pk)
    formulaire = FormulaireSujet(request.POST)
    if formulaire.is_valid():
        try:
            ServiceSujet.corriger(request.user, sujet, formulaire.cleaned_data)
        except ErreurValidation as erreur:
            messages.error(request, str(erreur))
        else:
            messages.success(request, "Sujet corrigé.")
    else:
        messages.error(request, "Correction refusée : référence ou date de dépôt invalide.")
    return redirect(_url_sujets(sujet.evaluation_id))


@exige_habilitation(PERMISSION_ECRITURE)
def vue_supprimer_sujet(request, pk):
    sujet = _sujet_ou_404(request.user, pk)
    evaluation_pk = sujet.evaluation_id
    try:
        ServiceSujet.supprimer(request.user, sujet)
    except ErreurValidation as erreur:
        messages.error(request, str(erreur))
    else:
        messages.success(request, "Sujet supprimé.")
    return redirect(_url_sujets(evaluation_pk))


@exige_habilitation(PERMISSION_ECRITURE)
def vue_retenir_sujet(request, pk):
    sujet = _sujet_ou_404(request.user, pk)
    formulaire = FormulaireRetenirSujet(request.POST)
    confirmation = formulaire.is_valid() and formulaire.cleaned_data["confirmation"]
    try:
        ServiceSujet.retenir(request.user, sujet, confirmation=confirmation)
    except ErreurValidation as erreur:
        messages.error(request, str(erreur))
    else:
        messages.success(request, "Sujet retenu.")
    return redirect(_url_sujets(sujet.evaluation_id))


@exige_habilitation(PERMISSION_ECRITURE)
def vue_changer_retenu_sujet(request, pk):
    sujet = _sujet_ou_404(request.user, pk)
    formulaire = FormulaireChangerRetenu(request.POST)
    motif = formulaire.cleaned_data["motif"] if formulaire.is_valid() else ""
    try:
        ServiceSujet.changer_retenu(request.user, sujet, motif)
    except ErreurValidation as erreur:
        messages.error(request, str(erreur))
    else:
        messages.success(request, "Sujet retenu changé.")
    return redirect(_url_sujets(sujet.evaluation_id))
