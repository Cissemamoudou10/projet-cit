"""Vue de déclaration d'une indisponibilité de lieu — § 8 du Prompt 14.
Toute la logique métier vit dans
ressources.services.indisponibilite_lieu.ServiceIndisponibiliteLieu.
"""

from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse

from administration.habilitations import exige_habilitation
from noyau.exceptions import ErreurValidation
from ressources.forms import FormulaireDeclarationIndisponibilite
from ressources.services.indisponibilite_lieu import ServiceIndisponibiliteLieu
from ressources.views.lieu import _lieu_ou_404


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
