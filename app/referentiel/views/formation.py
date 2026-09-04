"""Vues de gestion des formations — orchestrent, ne décident rien. Toute la
logique métier vit dans referentiel.services.formation via le patron
noyau.services.gestion.ServiceGestion.
"""

from django.contrib import messages
from django.http import Http404
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.html import format_html
from django.views.decorators.http import require_POST

from administration.habilitations import exige_habilitation
from noyau.exceptions import ErreurIntrouvable, ErreurModificationConcurrente, ErreurValidation
from noyau.forms import modifie_le_attendu_depuis_requete
from noyau.habilitations import a_permission
from referentiel.forms import FormulaireFormation
from referentiel.navigation import onglets_referentiel
from referentiel.services.formation import ServiceFormation
from referentiel.services.referentiel import ServiceReferentiel
from referentiel.services.type_formation import ServiceTypeFormation


def _formation_ou_404(pk):
    try:
        return ServiceFormation.obtenir(pk)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur


def _etat_tri(tri_actuel, colonne):
    """§ 3.09 : même patron que views/comptes.py::_etat_tri."""
    if tri_actuel == colonne:
        return {"aria": "ascending", "suivant": f"-{colonne}", "sens": "asc"}
    if tri_actuel == f"-{colonne}":
        return {"aria": "descending", "suivant": colonne, "sens": "desc"}
    return {"aria": "none", "suivant": colonne, "sens": None}


def _url_sans_parametre(request, nom):
    parametres = request.GET.copy()
    parametres.pop(nom, None)
    chaine = parametres.urlencode()
    return f"{request.path}?{chaine}" if chaine else request.path


def _filtres_actifs(request, type_formation_id):
    if not type_formation_id:
        return []
    try:
        type_formation = ServiceTypeFormation.obtenir(type_formation_id)
    except ErreurIntrouvable:
        return []
    return [
        {
            "libelle": f"Type : {type_formation}",
            "url_retrait": _url_sans_parametre(request, "type_formation"),
        }
    ]


def _filtres_champs(type_formation_id):
    return [
        {
            "nom": "type_formation",
            "libelle": "Type",
            "valeur": type_formation_id,
            "choix": [
                (type_formation.pk, type_formation.intitule)
                for type_formation in ServiceTypeFormation.disponibles_pour_selection()
            ],
        }
    ]


def _colonnes(tri_actuel):
    return [
        _colonne_intitule(tri_actuel),
        {"libelle": "Type", "cle_tri": None},
        {"libelle": "Spécialité", "cle_tri": None},
        {"libelle": "Durée", "cle_tri": None},
        {"libelle": "État", "cle_tri": None},
    ]


@exige_habilitation(ServiceFormation.PERMISSION_LECTURE)
def vue_liste_formations(request):
    tri_actuel = request.GET.get("tri", "")
    type_formation_id = request.GET.get("type_formation", "")
    filtres = {
        "recherche": request.GET.get("recherche", ""),
        "etat": request.GET.get("etat", ""),
        "type_formation": type_formation_id,
        "tri": tri_actuel,
    }
    page = ServiceFormation.lister(request.user, filtres, request.GET.get("page"))
    peut_ecrire = a_permission(request.user, ServiceFormation.PERMISSION_ECRITURE)
    onglets, onglet_actif = onglets_referentiel("formations")
    contexte = {
        "titre": "Formations",
        "sous_titre": "Catalogue des formations dispensées par le centre.",
        "onglets": onglets,
        "onglet_actif": onglet_actif,
        "url_creer": reverse("referentiel:creer_formation") if peut_ecrire else "",
        "libelle_creer": "Créer une formation",
        "champ_recherche_libelle": "Intitulé ou spécialité",
        "filtres": filtres,
        "filtres_champs": _filtres_champs(type_formation_id),
        "filtres_actifs": _filtres_actifs(request, type_formation_id),
        "url_liste": reverse("referentiel:liste_formations"),
        "colonnes": _colonnes(tri_actuel),
        "lignes": [_ligne(formation, peut_ecrire) for formation in page] if page else [],
        "libelle_vide": "Aucune formation ne correspond aux filtres",
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


def _ligne(formation, peut_ecrire):
    lien_intitule = format_html(
        '<a href="{}" class="text-marine-900 no-underline hover:underline">{}</a>',
        reverse("referentiel:detail_formation", args=[formation.pk]),
        formation.intitule,
    )
    ligne = {
        "cellules": [
            lien_intitule,
            formation.type_formation.intitule,
            formation.specialite,
            f"{formation.duree_semaines} sem.",
            "Archivée" if formation.archive else "Active",
        ],
        "libelle": formation.intitule,
        "archive": formation.archive,
    }
    if peut_ecrire:
        ligne["url_modifier"] = reverse("referentiel:modifier_formation", args=[formation.pk])
        ligne["url_archiver"] = reverse("referentiel:archiver_formation", args=[formation.pk])
        ligne["url_desarchiver"] = reverse("referentiel:desarchiver_formation", args=[formation.pk])
    return ligne


@exige_habilitation(ServiceFormation.PERMISSION_LECTURE)
def vue_detail_formation(request, pk):
    formation = _formation_ou_404(pk)
    elements = ServiceReferentiel.lister(request.user, formation)
    return render(
        request,
        "referentiel/formation_detail.html",
        {
            "formation": formation,
            "url_modifier": reverse("referentiel:modifier_formation", args=[formation.pk]),
            "url_referentiel": reverse("referentiel:referentiel_formation", args=[formation.pk]),
            "nombre_elements_referentiel": len(elements),
            "total_volume_referentiel": ServiceReferentiel.total_volume(formation),
        },
    )


@exige_habilitation(ServiceFormation.PERMISSION_ECRITURE)
def vue_creer_formation(request):
    if request.method == "POST":
        formulaire = FormulaireFormation(request.POST)
        if formulaire.is_valid():
            try:
                ServiceFormation.creer(request.user, formulaire.cleaned_data)
            except ErreurValidation as erreur:
                messages.error(request, str(erreur))
            else:
                messages.success(request, "Formation créée.")
                return redirect("referentiel:liste_formations")
    else:
        formulaire = FormulaireFormation()
    return render(
        request,
        "referentiel/formation_formulaire.html",
        {
            "titre": "Créer une formation",
            "form": formulaire,
            "url_annuler": reverse("referentiel:liste_formations"),
            "libelle_bouton": "Créer la formation",
        },
    )


@exige_habilitation(ServiceFormation.PERMISSION_ECRITURE)
def vue_modifier_formation(request, pk):
    formation = _formation_ou_404(pk)
    if request.method == "POST":
        return _traiter_modification(request, formation)
    formulaire = FormulaireFormation(instance=formation)
    return render(
        request,
        "referentiel/formation_formulaire.html",
        _contexte_modification(formation, formulaire),
    )


def _traiter_modification(request, formation):
    formulaire = FormulaireFormation(request.POST, instance=formation)
    modifie_le_attendu = modifie_le_attendu_depuis_requete(request)
    if formulaire.is_valid():
        try:
            ServiceFormation.modifier(
                request.user, formation.pk, formulaire.cleaned_data, modifie_le_attendu
            )
        except (ErreurValidation, ErreurModificationConcurrente) as erreur:
            messages.error(request, str(erreur))
        else:
            messages.success(request, "Formation modifiée.")
            return redirect("referentiel:liste_formations")
    return render(
        request,
        "referentiel/formation_formulaire.html",
        _contexte_modification(formation, formulaire),
    )


def _contexte_modification(formation, formulaire):
    return {
        "titre": f"Modifier la formation « {formation.intitule} »",
        "form": formulaire,
        "url_annuler": reverse("referentiel:liste_formations"),
        "libelle_bouton": "Enregistrer",
        "modifie_le_attendu": formation.modifie_le,
    }


@exige_habilitation(ServiceFormation.PERMISSION_ECRITURE)
def vue_confirmer_archivage_formation(request, pk):
    formation = _formation_ou_404(pk)
    if request.method == "POST":
        try:
            ServiceFormation.archiver(request.user, pk)
        except ErreurValidation as erreur:
            messages.error(request, str(erreur))
        else:
            messages.success(request, "Formation archivée.")
        return redirect("referentiel:liste_formations")
    return render(
        request,
        "noyau/gestion/confirmer_archivage.html",
        {
            "titre_dialogue": f"Archiver la formation « {formation.intitule} »",
            "texte_explication": (
                f"La formation « {formation.intitule} » ne sera plus proposée à la "
                "création d'une nouvelle session."
            ),
            "url_annuler": reverse("referentiel:liste_formations"),
        },
    )


@require_POST
@exige_habilitation(ServiceFormation.PERMISSION_ECRITURE)
def vue_desarchiver_formation(request, pk):
    _formation_ou_404(pk)
    ServiceFormation.desarchiver(request.user, pk)
    messages.success(request, "Formation désarchivée.")
    return redirect("referentiel:liste_formations")
