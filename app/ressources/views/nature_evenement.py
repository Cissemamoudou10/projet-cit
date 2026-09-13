"""Vues de gestion des natures d'événement — orchestrent, ne décident rien.
Toute la logique métier vit dans ressources.services.nature_evenement via le
patron noyau.services.gestion.ServiceGestion.
"""

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse

from administration.habilitations import exige_habilitation
from noyau.exceptions import ErreurIntrouvable, ErreurModificationConcurrente, ErreurValidation
from noyau.forms import modifie_le_attendu_depuis_requete
from noyau.habilitations import a_permission
from ressources.forms import FormulaireNatureEvenement
from ressources.services.nature_evenement import ServiceNatureEvenement


def _nature_ou_404(pk):
    try:
        return ServiceNatureEvenement.obtenir(pk)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur


@exige_habilitation(ServiceNatureEvenement.PERMISSION_LECTURE)
def vue_liste_natures_evenement(request):
    filtres = {"recherche": request.GET.get("recherche", ""), "tri": request.GET.get("tri", "")}
    page = ServiceNatureEvenement.lister(request.user, filtres, request.GET.get("page"))
    peut_ecrire = a_permission(request.user, ServiceNatureEvenement.PERMISSION_ECRITURE)
    contexte = {
        "titre": "Natures d'événement",
        "sous_titre": "Paramétrage du calendrier — chaque nature porte un effet par défaut.",
        "url_retour": reverse("ressources:calendrier_annuel"),
        "libelle_retour": "Retour au calendrier",
        "url_creer": reverse("ressources:creer_nature_evenement") if peut_ecrire else "",
        "libelle_creer": "Créer une nature",
        "champ_recherche_libelle": "Libellé",
        "masquer_filtre_archive": True,
        "filtres": filtres,
        "url_liste": reverse("ressources:liste_natures_evenement"),
        "colonnes": [
            {"libelle": "Libellé", "cle_tri": None},
            {"libelle": "Effet par défaut", "cle_tri": None},
        ],
        "lignes": [_ligne(nature, peut_ecrire) for nature in page] if page else [],
        "libelle_vide": "Aucune nature ne correspond aux filtres",
        "texte_vide": "Ajustez la recherche ou réinitialisez les filtres.",
        "page": page,
    }
    return render(request, "noyau/gestion/liste.html", contexte)


def _ligne(nature, peut_ecrire):
    ligne = {
        "cellules": [nature.libelle, nature.get_effet_par_defaut_display()],
        "libelle": nature.libelle,
    }
    if peut_ecrire:
        ligne["url_modifier"] = reverse("ressources:modifier_nature_evenement", args=[nature.pk])
        ligne["url_supprimer"] = reverse("ressources:supprimer_nature_evenement", args=[nature.pk])
    return ligne


@exige_habilitation(ServiceNatureEvenement.PERMISSION_ECRITURE)
def vue_creer_nature_evenement(request):
    if request.method == "POST":
        formulaire = FormulaireNatureEvenement(request.POST)
        if formulaire.is_valid():
            try:
                ServiceNatureEvenement.creer(request.user, formulaire.cleaned_data)
            except ErreurValidation as erreur:
                messages.error(request, str(erreur))
            else:
                messages.success(request, "Nature d'événement créée.")
                return redirect("ressources:liste_natures_evenement")
    else:
        formulaire = FormulaireNatureEvenement()
    return render(
        request,
        "noyau/gestion/formulaire.html",
        {
            "titre": "Créer une nature d'événement",
            "legende": "Nature",
            "form": formulaire,
            "url_annuler": reverse("ressources:liste_natures_evenement"),
            "libelle_bouton": "Créer la nature",
        },
    )


@exige_habilitation(ServiceNatureEvenement.PERMISSION_ECRITURE)
def vue_modifier_nature_evenement(request, pk):
    nature = _nature_ou_404(pk)
    if request.method == "POST":
        return _traiter_modification(request, nature)
    formulaire = FormulaireNatureEvenement(instance=nature)
    return render(
        request, "noyau/gestion/formulaire.html", _contexte_modification(nature, formulaire)
    )


def _traiter_modification(request, nature):
    formulaire = FormulaireNatureEvenement(request.POST, instance=nature)
    modifie_le_attendu = modifie_le_attendu_depuis_requete(request)
    if formulaire.is_valid():
        try:
            ServiceNatureEvenement.modifier(
                request.user, nature.pk, formulaire.cleaned_data, modifie_le_attendu
            )
        except (ErreurValidation, ErreurModificationConcurrente) as erreur:
            messages.error(request, str(erreur))
        else:
            messages.success(request, "Nature d'événement modifiée.")
            return redirect("ressources:liste_natures_evenement")
    return render(
        request, "noyau/gestion/formulaire.html", _contexte_modification(nature, formulaire)
    )


def _contexte_modification(nature, formulaire):
    return {
        "titre": f"Modifier la nature « {nature.libelle} »",
        "legende": "Nature",
        "form": formulaire,
        "url_annuler": reverse("ressources:liste_natures_evenement"),
        "libelle_bouton": "Enregistrer",
        "modifie_le_attendu": nature.modifie_le,
    }


@exige_habilitation(ServiceNatureEvenement.PERMISSION_ECRITURE)
def vue_confirmer_suppression_nature_evenement(request, pk):
    nature = _nature_ou_404(pk)
    if request.method == "POST":
        try:
            ServiceNatureEvenement.supprimer(request.user, pk)
        except ErreurValidation as erreur:
            messages.error(request, str(erreur))
        else:
            messages.success(request, "Nature d'événement supprimée.")
        return redirect("ressources:liste_natures_evenement")
    return render(
        request,
        "noyau/gestion/confirmer_suppression.html",
        {
            "titre_dialogue": f"Supprimer la nature « {nature.libelle} »",
            "texte_explication": (f"La nature « {nature.libelle} » sera supprimée définitivement."),
            "url_annuler": reverse("ressources:liste_natures_evenement"),
        },
    )
