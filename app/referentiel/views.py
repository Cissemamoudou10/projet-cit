"""Vues de gestion des types de formation — orchestrent, ne décident rien.
Toute la logique métier vit dans referentiel.services.type_formation via le
patron noyau.services.gestion.ServiceGestion.
"""

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from administration.habilitations import exige_habilitation
from noyau.exceptions import ErreurIntrouvable, ErreurModificationConcurrente, ErreurValidation
from referentiel.forms import FormulaireTypeFormation
from referentiel.services.type_formation import ServiceTypeFormation


def _type_formation_ou_404(pk):
    try:
        return ServiceTypeFormation.obtenir(pk)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur


def _etat_tri(tri_actuel, colonne):
    """§ 3.09 : même patron que views/comptes.py::_etat_tri."""
    if tri_actuel == colonne:
        return {"aria": "ascending", "suivant": f"-{colonne}", "sens": "asc"}
    if tri_actuel == f"-{colonne}":
        return {"aria": "descending", "suivant": colonne, "sens": "desc"}
    return {"aria": "none", "suivant": colonne, "sens": None}


@exige_habilitation(ServiceTypeFormation.PERMISSION_LECTURE)
def vue_liste_types_formation(request):
    tri_actuel = request.GET.get("tri", "")
    filtres = {
        "recherche": request.GET.get("recherche", ""),
        "etat": request.GET.get("etat", ""),
        "tri": tri_actuel,
    }
    page = ServiceTypeFormation.lister(request.user, filtres, request.GET.get("page"))
    contexte = {
        "titre": "Types de formation",
        "sous_titre": "Classent les formations selon le public auquel elles s'adressent.",
        "url_creer": reverse("referentiel:creer_type_formation"),
        "libelle_creer": "Créer un type",
        "champ_recherche_libelle": "Intitulé",
        "filtres": filtres,
        "url_liste": reverse("referentiel:liste_types_formation"),
        "colonnes": [
            _colonne_intitule(tri_actuel),
            {"libelle": "Formations rattachées", "cle_tri": None},
        ],
        "lignes": [_ligne(type_formation) for type_formation in page] if page else [],
        "libelle_vide": "Aucun type de formation ne correspond aux filtres",
        "texte_vide": "Ajustez la recherche ou réinitialisez les filtres.",
        "page": page,
    }
    return render(request, "noyau/gestion/liste.html", contexte)


def _colonne_intitule(tri_actuel):
    etat = _etat_tri(tri_actuel, "intitule")
    return {
        "libelle": "Intitulé",
        "cle_tri": "intitule",
        "tri_suivant": etat["suivant"],
        "sens": etat["sens"],
        "aria": etat["aria"],
    }


def _ligne(type_formation):
    return {
        "cellules": [type_formation.intitule, ""],
        "url_modifier": reverse("referentiel:modifier_type_formation", args=[type_formation.pk]),
        "url_archiver": reverse("referentiel:archiver_type_formation", args=[type_formation.pk]),
        "url_desarchiver": reverse(
            "referentiel:desarchiver_type_formation", args=[type_formation.pk]
        ),
        "archive": type_formation.archive,
    }


@exige_habilitation(ServiceTypeFormation.PERMISSION_ECRITURE)
def vue_creer_type_formation(request):
    if request.method == "POST":
        formulaire = FormulaireTypeFormation(request.POST)
        if formulaire.is_valid():
            try:
                ServiceTypeFormation.creer(request.user, formulaire.cleaned_data)
            except ErreurValidation as erreur:
                messages.error(request, str(erreur))
            else:
                messages.success(request, "Type de formation créé.")
                return redirect("referentiel:liste_types_formation")
    else:
        formulaire = FormulaireTypeFormation()
    return render(
        request,
        "noyau/gestion/formulaire.html",
        {
            "titre": "Créer un type de formation",
            "legende": "Type de formation",
            "form": formulaire,
            "url_annuler": reverse("referentiel:liste_types_formation"),
            "libelle_bouton": "Créer le type",
        },
    )


@exige_habilitation(ServiceTypeFormation.PERMISSION_ECRITURE)
def vue_modifier_type_formation(request, pk):
    type_formation = _type_formation_ou_404(pk)
    if request.method == "POST":
        return _traiter_modification(request, type_formation)
    formulaire = FormulaireTypeFormation(instance=type_formation)
    return render(
        request, "noyau/gestion/formulaire.html", _contexte_modification(type_formation, formulaire)
    )


def _traiter_modification(request, type_formation):
    formulaire = FormulaireTypeFormation(request.POST, instance=type_formation)
    modifie_le_attendu = request.POST.get("modifie_le_attendu")
    if formulaire.is_valid():
        try:
            ServiceTypeFormation.modifier(
                request.user, type_formation.pk, formulaire.cleaned_data, modifie_le_attendu
            )
        except (ErreurValidation, ErreurModificationConcurrente) as erreur:
            messages.error(request, str(erreur))
        else:
            messages.success(request, "Type de formation modifié.")
            return redirect("referentiel:liste_types_formation")
    return render(
        request, "noyau/gestion/formulaire.html", _contexte_modification(type_formation, formulaire)
    )


def _contexte_modification(type_formation, formulaire):
    return {
        "titre": f"Modifier le type « {type_formation.intitule} »",
        "legende": "Type de formation",
        "form": formulaire,
        "url_annuler": reverse("referentiel:liste_types_formation"),
        "libelle_bouton": "Enregistrer",
        "modifie_le_attendu": type_formation.modifie_le,
    }


@exige_habilitation(ServiceTypeFormation.PERMISSION_ECRITURE)
def vue_confirmer_archivage_type_formation(request, pk):
    type_formation = _type_formation_ou_404(pk)
    if request.method == "POST":
        try:
            ServiceTypeFormation.archiver(request.user, pk)
        except ErreurValidation as erreur:
            messages.error(request, str(erreur))
        else:
            messages.success(request, "Type de formation archivé.")
        return redirect("referentiel:liste_types_formation")
    return render(
        request,
        "noyau/gestion/confirmer_archivage.html",
        {
            "titre_dialogue": f"Archiver le type « {type_formation.intitule} »",
            "texte_explication": (
                f"Le type « {type_formation.intitule} » ne sera plus proposé à la création "
                "d'une nouvelle formation."
            ),
            "url_annuler": reverse("referentiel:liste_types_formation"),
        },
    )


@require_POST
@exige_habilitation(ServiceTypeFormation.PERMISSION_ECRITURE)
def vue_desarchiver_type_formation(request, pk):
    _type_formation_ou_404(pk)
    ServiceTypeFormation.desarchiver(request.user, pk)
    messages.success(request, "Type de formation désarchivé.")
    return redirect("referentiel:liste_types_formation")
