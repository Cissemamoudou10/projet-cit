"""Vues de gestion du catalogue des matières — orchestrent, ne décident
rien. Toute la logique métier vit dans referentiel.services.matiere via le
patron noyau.services.gestion.ServiceGestion.
"""

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_POST

from administration.habilitations import exige_habilitation
from noyau.exceptions import ErreurIntrouvable, ErreurModificationConcurrente, ErreurValidation
from noyau.forms import modifie_le_attendu_depuis_requete
from noyau.habilitations import a_permission
from referentiel.forms import FormulaireMatiere, FormulaireObjectifPedagogique
from referentiel.navigation import onglets_referentiel
from referentiel.services.matiere import ServiceMatiere
from referentiel.services.objectif_pedagogique import ServiceObjectifPedagogique


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


@exige_habilitation(ServiceMatiere.PERMISSION_LECTURE)
def vue_liste_matieres(request):
    tri_actuel = request.GET.get("tri", "")
    filtres = {
        "recherche": request.GET.get("recherche", ""),
        "etat": request.GET.get("etat", ""),
        "tri": tri_actuel,
    }
    page = ServiceMatiere.lister(request.user, filtres, request.GET.get("page"))
    peut_ecrire = a_permission(request.user, ServiceMatiere.PERMISSION_ECRITURE)
    onglets, onglet_actif = onglets_referentiel("matieres")
    contexte = {
        "titre": "Matières",
        "sous_titre": "Catalogue indépendant des formations — RG-05.",
        "onglets": onglets,
        "onglet_actif": onglet_actif,
        "url_creer": reverse("referentiel:creer_matiere") if peut_ecrire else "",
        "libelle_creer": "Créer une matière",
        "champ_recherche_libelle": "Intitulé",
        "filtres": filtres,
        "url_liste": reverse("referentiel:liste_matieres"),
        "colonnes": [
            _colonne_intitule(tri_actuel),
            {"libelle": "Code", "cle_tri": None},
            {"libelle": "Formations", "cle_tri": None},
            {"libelle": "Instructeurs", "cle_tri": None},
            {"libelle": "Objectifs", "cle_tri": None},
        ],
        "lignes": [_ligne(matiere, peut_ecrire) for matiere in page] if page else [],
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


def _ligne(matiere, peut_ecrire):
    lien_intitule = format_html(
        '<a href="{}" class="text-marine-900 no-underline hover:underline">{}</a>',
        reverse("referentiel:detail_matiere", args=[matiere.pk]),
        matiere.intitule,
    )
    ligne = {
        "cellules": [
            lien_intitule,
            matiere.code,
            format_html('<span class="tabular-nums">{}</span>', matiere.nombre_formations),
            _cellule_instructeurs_qualifies(matiere.nombre_instructeurs_qualifies),
            format_html('<span class="tabular-nums">{}</span>', matiere.nombre_objectifs),
        ],
        "libelle": matiere.intitule,
        "archive": matiere.archive,
    }
    if peut_ecrire:
        ligne["url_modifier"] = reverse("referentiel:modifier_matiere", args=[matiere.pk])
        ligne["url_archiver"] = reverse("referentiel:archiver_matiere", args=[matiere.pk])
        ligne["url_desarchiver"] = reverse("referentiel:desarchiver_matiere", args=[matiere.pk])
        ligne["url_supprimer"] = reverse("referentiel:supprimer_matiere", args=[matiere.pk])
    return ligne


def _cellule_instructeurs_qualifies(nombre):
    """Couleur doublée d'un mot, même signalement qu'à US-INS-02 critère 4
    (`ressources/couverture_qualifications.html`)."""
    if nombre:
        return format_html('<span class="tabular-nums">{}</span>', nombre)
    return mark_safe(
        '<span class="bg-etat-ecart px-2 py-px text-2xs font-semibold tracking-wide '
        'text-blanc">AUCUN</span>'
    )


@exige_habilitation(ServiceMatiere.PERMISSION_LECTURE)
def vue_detail_matiere(request, pk):
    matiere = _matiere_ou_404(pk)
    return render(
        request,
        "referentiel/matiere_detail.html",
        {
            "matiere": matiere,
            "url_modifier": reverse("referentiel:modifier_matiere", args=[matiere.pk]),
            "objectifs": ServiceObjectifPedagogique.lister_pour_matiere(request.user, matiere),
            "formulaire_objectif": FormulaireObjectifPedagogique(),
            "url_ajouter_objectif": reverse(
                "referentiel:ajouter_objectif_pedagogique", args=[matiere.pk]
            ),
            "nombre_instructeurs_qualifies": matiere.qualifications.count(),
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
    modifie_le_attendu = modifie_le_attendu_depuis_requete(request)
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


@exige_habilitation(ServiceMatiere.PERMISSION_ECRITURE)
def vue_confirmer_suppression_matiere(request, pk):
    matiere = _matiere_ou_404(pk)
    if request.method == "POST":
        try:
            ServiceMatiere.supprimer(request.user, pk)
        except ErreurValidation as erreur:
            messages.error(request, str(erreur))
        else:
            messages.success(request, "Matière supprimée.")
        return redirect("referentiel:liste_matieres")
    return render(
        request,
        "noyau/gestion/confirmer_suppression.html",
        {
            "titre_dialogue": f"Supprimer la matière « {matiere.intitule} »",
            "texte_explication": (
                f"La matière « {matiere.intitule} » sera supprimée définitivement du catalogue."
            ),
            "url_annuler": reverse("referentiel:liste_matieres"),
        },
    )
