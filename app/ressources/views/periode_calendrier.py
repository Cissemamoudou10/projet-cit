"""Vues de saisie et de consultation d'une période de calendrier —
CU-P4-05, Prompt 28. Orchestrent, ne décident rien : toute la logique vit
dans ressources.services.periode_calendrier.ServicePeriodeCalendrier.
"""

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse

from administration.habilitations import exige_habilitation
from noyau.exceptions import ErreurIntrouvable, ErreurModificationConcurrente, ErreurValidation
from noyau.forms import modifie_le_attendu_depuis_requete
from ressources.forms import FormulaireDeclarationPeriodeCalendrier
from ressources.services.periode_calendrier import DonneesPeriode, ServicePeriodeCalendrier


def _periode_ou_404(pk):
    try:
        return ServicePeriodeCalendrier.obtenir(pk)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur


def _donnees_depuis_formulaire(formulaire):
    return DonneesPeriode(
        nature=formulaire.cleaned_data["nature"],
        intitule=formulaire.cleaned_data["intitule"],
        debut=formulaire.cleaned_data["debut"],
        fin=formulaire.cleaned_data["fin"],
        effet=formulaire.cleaned_data["effet"],
        sessions=list(formulaire.cleaned_data["sessions"]),
        brigades=list(formulaire.cleaned_data["brigades"]),
    )


def _emettre_avertissements(request, periode):
    for item in periode.avertissements:
        messages.warning(request, item["message"])


@exige_habilitation(ServicePeriodeCalendrier.PERMISSION_LECTURE)
def vue_detail_periode_calendrier(request, pk):
    periode = _periode_ou_404(pk)
    return render(
        request,
        "ressources/periode_calendrier_detail.html",
        {
            "periode": periode,
            "url_annuel": reverse("ressources:calendrier_annuel"),
            "url_modifier": reverse("ressources:modifier_periode_calendrier", args=[periode.pk]),
            "url_supprimer": reverse("ressources:supprimer_periode_calendrier", args=[periode.pk]),
        },
    )


@exige_habilitation(ServicePeriodeCalendrier.PERMISSION_ECRITURE)
def vue_declarer_periode_calendrier(request):
    if request.method == "POST":
        formulaire = FormulaireDeclarationPeriodeCalendrier(request.POST)
        if formulaire.is_valid():
            try:
                periode = ServicePeriodeCalendrier.creer(
                    request.user, _donnees_depuis_formulaire(formulaire)
                )
            except ErreurValidation as erreur:
                messages.error(request, str(erreur))
            else:
                messages.success(request, "Période de calendrier déclarée.")
                _emettre_avertissements(request, periode)
                return redirect("ressources:detail_periode_calendrier", pk=periode.pk)
    else:
        formulaire = FormulaireDeclarationPeriodeCalendrier()
    return render(
        request,
        "noyau/gestion/formulaire.html",
        {
            "titre": "Déclarer une période de calendrier",
            "legende": "Nature, période, cibles",
            "form": formulaire,
            "url_annuler": reverse("ressources:calendrier_annuel"),
            "libelle_bouton": "Déclarer la période",
        },
    )


@exige_habilitation(ServicePeriodeCalendrier.PERMISSION_ECRITURE)
def vue_modifier_periode_calendrier(request, pk):
    periode = _periode_ou_404(pk)
    if request.method == "POST":
        return _traiter_modification(request, periode)
    formulaire = FormulaireDeclarationPeriodeCalendrier(
        initial={
            "nature": periode.nature_id,
            "intitule": periode.intitule,
            "debut": periode.debut,
            "fin": periode.fin,
            "effet": periode.effet,
            "sessions": [s.pk for s in periode.sessions.all()],
            "brigades": [b.pk for b in periode.brigades.all()],
        }
    )
    return render(
        request, "noyau/gestion/formulaire.html", _contexte_modification(periode, formulaire)
    )


def _traiter_modification(request, periode):
    formulaire = FormulaireDeclarationPeriodeCalendrier(request.POST)
    modifie_le_attendu = modifie_le_attendu_depuis_requete(request)
    if formulaire.is_valid():
        try:
            periode_modifiee = ServicePeriodeCalendrier.modifier(
                request.user, periode.pk, _donnees_depuis_formulaire(formulaire), modifie_le_attendu
            )
        except (ErreurValidation, ErreurModificationConcurrente) as erreur:
            messages.error(request, str(erreur))
        else:
            messages.success(request, "Période de calendrier modifiée.")
            _emettre_avertissements(request, periode_modifiee)
            return redirect("ressources:detail_periode_calendrier", pk=periode.pk)
    return render(
        request, "noyau/gestion/formulaire.html", _contexte_modification(periode, formulaire)
    )


def _contexte_modification(periode, formulaire):
    return {
        "titre": f"Modifier « {periode.intitule} »",
        "legende": "Nature, période, cibles",
        "form": formulaire,
        "url_annuler": reverse("ressources:detail_periode_calendrier", args=[periode.pk]),
        "libelle_bouton": "Enregistrer",
        "modifie_le_attendu": periode.modifie_le,
    }


@exige_habilitation(ServicePeriodeCalendrier.PERMISSION_ECRITURE)
def vue_confirmer_suppression_periode_calendrier(request, pk):
    periode = _periode_ou_404(pk)
    if request.method == "POST":
        try:
            ServicePeriodeCalendrier.supprimer(request.user, pk)
        except ErreurValidation as erreur:
            messages.error(request, str(erreur))
        else:
            messages.success(request, "Période de calendrier supprimée.")
        return redirect("ressources:calendrier_annuel")
    return render(
        request,
        "noyau/gestion/confirmer_suppression.html",
        {
            "titre_dialogue": f"Supprimer « {periode.intitule} »",
            "texte_explication": (
                f"La période du {periode.debut:%d/%m/%Y %H:%M} au {periode.fin:%d/%m/%Y %H:%M} "
                "sera supprimée définitivement. Les séances déjà replacées pendant cette "
                "période ne sont pas rétablies automatiquement."
            ),
            "url_annuler": reverse("ressources:detail_periode_calendrier", args=[periode.pk]),
        },
    )
