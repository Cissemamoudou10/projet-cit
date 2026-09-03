"""Vues de gestion du catalogue des matières — orchestrent, ne décident
rien. Toute la logique métier vit dans referentiel.services.matiere via le
patron noyau.services.gestion.ServiceGestion.
"""

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.html import format_html
from django.views.decorators.http import require_POST

from administration.habilitations import exige_habilitation
from noyau.exceptions import ErreurIntrouvable, ErreurModificationConcurrente, ErreurValidation
from referentiel.forms import FormulaireMatiere
from referentiel.services.matiere import ServiceMatiere


def _matiere_ou_404(pk):
    try:
        return ServiceMatiere.obtenir(pk)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur


def _etat_tri(tri_actuel, colonne):
    """§ 3.09 : même patron que views/comptes.py::_etat_tri."""
    if tri_actuel == colonne:
        return {"aria": "ascending", "suivant": f"-{colonne}", "sens": "asc"}
    if tri_actuel == f"-{colonne}":
        return {"aria": "descending", "suivant": colonne, "sens": "desc"}
    return {"aria": "none", "suivant": colonne, "sens": None}


def _liens_associes():
    return [
        {"libelle": "Types de formation", "url": reverse("referentiel:liste_types_formation")},
        {"libelle": "Formations", "url": reverse("referentiel:liste_formations")},
    ]


@exige_habilitation(ServiceMatiere.PERMISSION_LECTURE)
def vue_liste_matieres(request):
    tri_actuel = request.GET.get("tri", "")
    filtres = {
        "recherche": request.GET.get("recherche", ""),
        "etat": request.GET.get("etat", ""),
        "tri": tri_actuel,
    }
    page = ServiceMatiere.lister(request.user, filtres, request.GET.get("page"))
    contexte = {
        "titre": "Matières",
        "sous_titre": "Catalogue indépendant des formations — RG-05.",
        "liens_associes": _liens_associes(),
        "url_creer": reverse("referentiel:creer_matiere"),
        "libelle_creer": "Créer une matière",
        "champ_recherche_libelle": "Intitulé",
        "filtres": filtres,
        "url_liste": reverse("referentiel:liste_matieres"),
        "colonnes": [
            _colonne_intitule(tri_actuel),
            {"libelle": "Code", "cle_tri": None},
        ],
        "lignes": [_ligne(matiere) for matiere in page] if page else [],
        "libelle_vide": "Aucune matière ne correspond aux filtres",
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


def _ligne(matiere):
    lien_intitule = format_html(
        '<a href="{}" class="text-marine-900 no-underline hover:underline">{}</a>',
        reverse("referentiel:detail_matiere", args=[matiere.pk]),
        matiere.intitule,
    )
    return {
        "cellules": [lien_intitule, matiere.code],
        "libelle": matiere.intitule,
        "url_modifier": reverse("referentiel:modifier_matiere", args=[matiere.pk]),
        "url_archiver": reverse("referentiel:archiver_matiere", args=[matiere.pk]),
        "url_desarchiver": reverse("referentiel:desarchiver_matiere", args=[matiere.pk]),
        "archive": matiere.archive,
    }


@exige_habilitation(ServiceMatiere.PERMISSION_LECTURE)
def vue_detail_matiere(request, pk):
    matiere = _matiere_ou_404(pk)
    return render(
        request,
        "referentiel/matiere_detail.html",
        {
            "matiere": matiere,
            "url_modifier": reverse("referentiel:modifier_matiere", args=[matiere.pk]),
        },
    )


@exige_habilitation(ServiceMatiere.PERMISSION_ECRITURE)
def vue_creer_matiere(request):
    if request.method == "POST":
        formulaire = FormulaireMatiere(request.POST)
        if formulaire.is_valid():
            try:
                ServiceMatiere.creer(request.user, formulaire.cleaned_data)
            except ErreurValidation as erreur:
                messages.error(request, str(erreur))
            else:
                messages.success(request, "Matière créée.")
                return redirect("referentiel:liste_matieres")
    else:
        formulaire = FormulaireMatiere()
    return render(
        request,
        "noyau/gestion/formulaire.html",
        {
            "titre": "Créer une matière",
            "legende": "Matière",
            "form": formulaire,
            "url_annuler": reverse("referentiel:liste_matieres"),
            "libelle_bouton": "Créer la matière",
        },
    )


@exige_habilitation(ServiceMatiere.PERMISSION_ECRITURE)
def vue_modifier_matiere(request, pk):
    matiere = _matiere_ou_404(pk)
    if request.method == "POST":
        return _traiter_modification(request, matiere)
    formulaire = FormulaireMatiere(instance=matiere)
    return render(
        request, "noyau/gestion/formulaire.html", _contexte_modification(matiere, formulaire)
    )


def _traiter_modification(request, matiere):
    formulaire = FormulaireMatiere(request.POST, instance=matiere)
    modifie_le_attendu = request.POST.get("modifie_le_attendu")
    if formulaire.is_valid():
        try:
            ServiceMatiere.modifier(
                request.user, matiere.pk, formulaire.cleaned_data, modifie_le_attendu
            )
        except (ErreurValidation, ErreurModificationConcurrente) as erreur:
            messages.error(request, str(erreur))
        else:
            messages.success(request, "Matière modifiée.")
            return redirect("referentiel:liste_matieres")
    return render(
        request, "noyau/gestion/formulaire.html", _contexte_modification(matiere, formulaire)
    )


def _contexte_modification(matiere, formulaire):
    return {
        "titre": f"Modifier la matière « {matiere.intitule} »",
        "legende": "Matière",
        "form": formulaire,
        "url_annuler": reverse("referentiel:liste_matieres"),
        "libelle_bouton": "Enregistrer",
        "modifie_le_attendu": matiere.modifie_le,
    }


@exige_habilitation(ServiceMatiere.PERMISSION_ECRITURE)
def vue_confirmer_archivage_matiere(request, pk):
    matiere = _matiere_ou_404(pk)
    if request.method == "POST":
        try:
            ServiceMatiere.archiver(request.user, pk)
        except ErreurValidation as erreur:
            messages.error(request, str(erreur))
        else:
            messages.success(request, "Matière archivée.")
        return redirect("referentiel:liste_matieres")
    return render(
        request,
        "noyau/gestion/confirmer_archivage.html",
        {
            "titre_dialogue": f"Archiver la matière « {matiere.intitule} »",
            "texte_explication": (
                f"La matière « {matiere.intitule} » ne sera plus proposée au rattachement "
                "à un référentiel."
            ),
            "url_annuler": reverse("referentiel:liste_matieres"),
        },
    )


@require_POST
@exige_habilitation(ServiceMatiere.PERMISSION_ECRITURE)
def vue_desarchiver_matiere(request, pk):
    _matiere_ou_404(pk)
    ServiceMatiere.desarchiver(request.user, pk)
    messages.success(request, "Matière désarchivée.")
    return redirect("referentiel:liste_matieres")
