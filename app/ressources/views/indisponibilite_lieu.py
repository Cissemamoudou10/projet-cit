"""Vue de déclaration d'une indisponibilité de lieu — § 8 du Prompt 14.
Toute la logique métier vit dans
ressources.services.indisponibilite_lieu.ServiceIndisponibiliteLieu.
"""

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse

from administration.habilitations import exige_habilitation
from noyau.exceptions import ErreurIntrouvable, ErreurValidation
from ressources.forms import FormulaireDeclarationIndisponibilite
from ressources.services.indisponibilite_lieu import ServiceIndisponibiliteLieu
from ressources.views.lieu import _lieu_ou_404


def _indisponibilite_ou_404(pk):
    try:
        return ServiceIndisponibiliteLieu.obtenir(pk)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur


@exige_habilitation(ServiceIndisponibiliteLieu.PERMISSION_ECRITURE)
def vue_declarer_indisponibilite(request, lieu_pk):
    lieu = _lieu_ou_404(lieu_pk)
    if request.method == "POST":
        formulaire = FormulaireDeclarationIndisponibilite(request.POST)
        if formulaire.is_valid():
            try:
                ServiceIndisponibiliteLieu.declarer(
                    request.user,
                    lieu,
                    formulaire.cleaned_data["debut"],
                    formulaire.cleaned_data["fin"],
                    formulaire.cleaned_data["motif"],
                )
            except ErreurValidation as erreur:
                messages.error(request, str(erreur))
            else:
                messages.success(request, "Indisponibilité déclarée.")
                return redirect("ressources:detail_lieu", pk=lieu.pk)
    else:
        formulaire = FormulaireDeclarationIndisponibilite()
    return render(
        request,
        "noyau/gestion/formulaire.html",
        {
            "titre": f"Déclarer une indisponibilité — {lieu}",
            "legende": "Période et motif",
            "form": formulaire,
            "url_annuler": reverse("ressources:detail_lieu", args=[lieu.pk]),
            "libelle_bouton": "Déclarer l'indisponibilité",
        },
    )


@exige_habilitation(ServiceIndisponibiliteLieu.PERMISSION_ECRITURE)
def vue_modifier_indisponibilite(request, pk):
    indisponibilite = _indisponibilite_ou_404(pk)
    if request.method == "POST":
        formulaire = FormulaireDeclarationIndisponibilite(request.POST)
        if formulaire.is_valid():
            try:
                ServiceIndisponibiliteLieu.modifier(
                    request.user,
                    indisponibilite,
                    formulaire.cleaned_data["debut"],
                    formulaire.cleaned_data["fin"],
                    formulaire.cleaned_data["motif"],
                )
            except ErreurValidation as erreur:
                messages.error(request, str(erreur))
            else:
                messages.success(request, "Indisponibilité modifiée.")
                return redirect("ressources:detail_lieu", pk=indisponibilite.lieu_id)
    else:
        formulaire = FormulaireDeclarationIndisponibilite(
            initial={
                "debut": indisponibilite.debut,
                "fin": indisponibilite.fin,
                "motif": indisponibilite.motif,
            }
        )
    return render(
        request,
        "noyau/gestion/formulaire.html",
        {
            "titre": f"Modifier l'indisponibilité — {indisponibilite.lieu}",
            "legende": "Période et motif",
            "form": formulaire,
            "url_annuler": reverse("ressources:detail_lieu", args=[indisponibilite.lieu_id]),
            "libelle_bouton": "Enregistrer",
        },
    )


@exige_habilitation(ServiceIndisponibiliteLieu.PERMISSION_ECRITURE)
def vue_confirmer_suppression_indisponibilite(request, pk):
    indisponibilite = _indisponibilite_ou_404(pk)
    url_retour = reverse("ressources:detail_lieu", args=[indisponibilite.lieu_id])
    if request.method == "POST":
        try:
            ServiceIndisponibiliteLieu.supprimer(request.user, indisponibilite)
        except ErreurValidation as erreur:
            messages.error(request, str(erreur))
        else:
            messages.success(request, "Indisponibilité supprimée.")
        return redirect(url_retour)
    return render(
        request,
        "noyau/gestion/confirmer_suppression.html",
        {
            "titre_dialogue": f"Supprimer l'indisponibilité de « {indisponibilite.lieu} »",
            "texte_explication": (
                f"La période du {indisponibilite.debut:%d/%m/%Y %H:%M} au "
                f"{indisponibilite.fin:%d/%m/%Y %H:%M} sera supprimée définitivement."
            ),
            "url_annuler": url_retour,
        },
    )
