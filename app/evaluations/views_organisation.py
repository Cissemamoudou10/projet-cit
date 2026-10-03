"""Écrans de l'organisation d'épreuve — US-EVAL-04, Prompt 38. Orchestrent : toute
la logique vit dans `evaluations.services.organisation.ServiceOrganisationEpreuve`.
La convocation (A11) n'affiche jamais de sujet : elle ne consulte aucun service de sujet.
"""

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from administration.habilitations import exige_habilitation
from evaluations.forms_organisation import (
    FormulaireCreneau,
    FormulaireOrganisation,
    FormulaireSurveillant,
)
from evaluations.services.evaluation import (
    PERMISSION_ECRITURE,
    PERMISSION_LECTURE,
    ServiceEvaluation,
)
from evaluations.services.organisation import ServiceOrganisationEpreuve
from evaluations.services.organisation_lecture import LectureOrganisationEpreuve
from noyau.exceptions import ErreurIntrouvable, ErreurValidation
from noyau.habilitations import a_permission


def _evaluation_ou_404(pk):
    try:
        return ServiceEvaluation.obtenir(pk)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur


def _organisation_ou_404(pk):
    try:
        return ServiceOrganisationEpreuve.obtenir_organisation(pk)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur


def _surveillance_ou_404(pk):
    try:
        return ServiceOrganisationEpreuve.obtenir_surveillance(pk)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur


def _url_organisation(evaluation_pk):
    return reverse("evaluations:organisation", args=[evaluation_pk])


@exige_habilitation(PERMISSION_LECTURE)
def vue_organisation(request, pk):
    evaluation = _evaluation_ou_404(pk)
    peut_ecrire = a_permission(request.user, PERMISSION_ECRITURE)
    return render(
        request,
        "evaluations/organisation.html",
        {
            "evaluation": evaluation,
            "synthese": LectureOrganisationEpreuve.synthese(evaluation),
            "peut_ecrire": peut_ecrire,
            "formulaire_creneau": FormulaireCreneau(
                initial={"heure_debut": evaluation.heure_debut, "heure_fin": evaluation.heure_fin}
            ),
            "formulaire_organisation": FormulaireOrganisation(),
            "formulaire_surveillant": FormulaireSurveillant(),
            "url_retour": reverse("evaluations:detail_evaluation", args=[pk]),
        },
    )


@exige_habilitation(PERMISSION_ECRITURE)
@require_POST
def vue_fixer_creneau(request, pk):
    evaluation = _evaluation_ou_404(pk)
    formulaire = FormulaireCreneau(request.POST)
    if formulaire.is_valid():
        try:
            evaluation = ServiceOrganisationEpreuve.fixer_creneau(
                request.user,
                evaluation,
                formulaire.cleaned_data["heure_debut"],
                formulaire.cleaned_data["heure_fin"],
            )
        except ErreurValidation as erreur:
            messages.error(request, str(erreur))
        else:
            messages.success(request, "Créneau enregistré.")
            for item in evaluation.avertissements:
                messages.warning(request, item)
    else:
        messages.error(request, "Heures de créneau invalides.")
    return redirect(_url_organisation(pk))


@exige_habilitation(PERMISSION_ECRITURE)
@require_POST
def vue_ajouter_organisation(request, pk):
    evaluation = _evaluation_ou_404(pk)
    formulaire = FormulaireOrganisation(request.POST)
    if formulaire.is_valid():
        try:
            ServiceOrganisationEpreuve.ajouter_organisation(
                request.user,
                evaluation,
                formulaire.cleaned_data["brigade"],
                formulaire.cleaned_data["lieu"],
                formulaire.cleaned_data["effectif_attendu"],
            )
        except ErreurValidation as erreur:
            messages.error(request, str(erreur))
        else:
            messages.success(request, "Organisation ajoutée.")
    else:
        messages.error(request, "Brigade, lieu ou effectif invalide.")
    return redirect(_url_organisation(pk))


@exige_habilitation(PERMISSION_ECRITURE)
@require_POST
def vue_retirer_organisation(request, pk):
    organisation = _organisation_ou_404(pk)
    try:
        ServiceOrganisationEpreuve.retirer_organisation(request.user, organisation)
    except ErreurValidation as erreur:
        messages.error(request, str(erreur))
    else:
        messages.success(request, "Organisation retirée.")
    return redirect(_url_organisation(organisation.evaluation_id))


@exige_habilitation(PERMISSION_ECRITURE)
@require_POST
def vue_ajouter_surveillant(request, pk):
    organisation = _organisation_ou_404(pk)
    formulaire = FormulaireSurveillant(request.POST)
    if formulaire.is_valid():
        try:
            ServiceOrganisationEpreuve.ajouter_surveillant(
                request.user,
                organisation,
                instructeur=formulaire.cleaned_data["instructeur"],
                nom_libre=formulaire.cleaned_data["nom_libre"],
            )
        except ErreurValidation as erreur:
            messages.error(request, str(erreur))
        else:
            messages.success(request, "Surveillant ajouté.")
    else:
        messages.error(request, "Surveillant invalide.")
    return redirect(_url_organisation(organisation.evaluation_id))


@exige_habilitation(PERMISSION_ECRITURE)
@require_POST
def vue_retirer_surveillant(request, pk):
    surveillance = _surveillance_ou_404(pk)
    try:
        ServiceOrganisationEpreuve.retirer_surveillant(request.user, surveillance)
    except ErreurValidation as erreur:
        messages.error(request, str(erreur))
    else:
        messages.success(request, "Surveillant retiré.")
    return redirect(_url_organisation(surveillance.organisation.evaluation_id))


@exige_habilitation(PERMISSION_LECTURE)
def vue_convocation(request, pk):
    """A11 : page imprimable, sans aucun sujet. Lisible par la Direction de Formation."""
    evaluation = _evaluation_ou_404(pk)
    return render(
        request,
        "evaluations/convocation.html",
        {
            "evaluation": evaluation,
            "organisations": LectureOrganisationEpreuve.organisations_convocation(evaluation),
            "url_retour": _url_organisation(pk),
        },
    )
