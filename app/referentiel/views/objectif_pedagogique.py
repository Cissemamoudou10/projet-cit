"""Vues des objectifs pédagogiques d'une matière — CU-P2-06. Orchestrent, ne
décident rien : toute la logique métier vit dans
referentiel.services.objectif_pedagogique.ServiceObjectifPedagogique.
"""

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from administration.habilitations import exige_habilitation
from noyau.exceptions import ErreurIntrouvable, ErreurValidation
from referentiel.forms import FormulaireObjectifPedagogique
from referentiel.services.matiere import ServiceMatiere
from referentiel.services.objectif_pedagogique import ServiceObjectifPedagogique


def _matiere_ou_404(pk):
    try:
        return ServiceMatiere.obtenir(pk)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur


def _objectif_ou_404(pk):
    try:
        return ServiceObjectifPedagogique.obtenir(pk)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur


@require_POST
@exige_habilitation(ServiceObjectifPedagogique.PERMISSION_ECRITURE)
def vue_ajouter_objectif_pedagogique(request, matiere_pk):
    matiere = _matiere_ou_404(matiere_pk)
    formulaire = FormulaireObjectifPedagogique(request.POST)
    if formulaire.is_valid():
        try:
            ServiceObjectifPedagogique.ajouter(
                request.user, matiere, formulaire.cleaned_data["libelle"]
            )
        except ErreurValidation as erreur:
            messages.error(request, str(erreur))
        else:
            messages.success(request, "Objectif pédagogique ajouté.")
    else:
        messages.error(request, "Libellé non valide.")
    return redirect("referentiel:detail_matiere", matiere.pk)


@require_POST
@exige_habilitation(ServiceObjectifPedagogique.PERMISSION_ECRITURE)
def vue_modifier_objectif_pedagogique(request, matiere_pk, objectif_pk):
    matiere = _matiere_ou_404(matiere_pk)
    objectif = _objectif_ou_404(objectif_pk)
    formulaire = FormulaireObjectifPedagogique(request.POST)
    if formulaire.is_valid():
        try:
            ServiceObjectifPedagogique.modifier_libelle(
                request.user, objectif, formulaire.cleaned_data["libelle"]
            )
        except ErreurValidation as erreur:
            messages.error(request, str(erreur))
        else:
            messages.success(request, "Objectif pédagogique modifié.")
    else:
        messages.error(request, "Libellé non valide.")
    return redirect("referentiel:detail_matiere", matiere.pk)


@require_POST
@exige_habilitation(ServiceObjectifPedagogique.PERMISSION_ECRITURE)
def vue_monter_objectif_pedagogique(request, matiere_pk, objectif_pk):
    matiere = _matiere_ou_404(matiere_pk)
    objectif = _objectif_ou_404(objectif_pk)
    ServiceObjectifPedagogique.monter(request.user, objectif)
    return redirect("referentiel:detail_matiere", matiere.pk)


@require_POST
@exige_habilitation(ServiceObjectifPedagogique.PERMISSION_ECRITURE)
def vue_descendre_objectif_pedagogique(request, matiere_pk, objectif_pk):
    matiere = _matiere_ou_404(matiere_pk)
    objectif = _objectif_ou_404(objectif_pk)
    ServiceObjectifPedagogique.descendre(request.user, objectif)
    return redirect("referentiel:detail_matiere", matiere.pk)


@exige_habilitation(ServiceObjectifPedagogique.PERMISSION_ECRITURE)
def vue_confirmer_suppression_objectif_pedagogique(request, matiere_pk, objectif_pk):
    matiere = _matiere_ou_404(matiere_pk)
    objectif = _objectif_ou_404(objectif_pk)
    if request.method == "POST":
        ServiceObjectifPedagogique.supprimer(request.user, objectif.pk)
        messages.success(request, "Objectif pédagogique supprimé.")
        return redirect("referentiel:detail_matiere", matiere.pk)
    return render(
        request,
        "referentiel/objectif_pedagogique_confirmer_suppression.html",
        {
            "objectif": objectif,
            "url_annuler": reverse("referentiel:detail_matiere", args=[matiere.pk]),
        },
    )
