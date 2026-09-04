"""Vues de gestion des lieux — orchestrent, ne décident rien. Toute la
logique métier vit dans ressources.services.lieu.ServiceLieu.
"""

import datetime

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
from ressources.forms import FormulaireLieu
from ressources.navigation import onglets_ressources
from ressources.services.indisponibilite_lieu import ServiceIndisponibiliteLieu
from ressources.services.lieu import ServiceLieu

CLASSES_BADGE_CATEGORIE = {
    "salle_attitree": "bg-marine-900 text-blanc",
    "lieu_partage": "border border-marine-700 text-marine-700",
}

GROUPES_FORMULAIRE = [
    {"legende": "Identification", "champs": ["intitule", "capacite"]},
    {"legende": "Nature", "champs": ["categorie", "type_partage"]},
]


def _lieu_ou_404(pk):
    try:
        return ServiceLieu.obtenir(pk)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur


def _etat_tri(tri_actuel, colonne):
    """§ 3.09 : même patron que views/instructeur.py::_etat_tri."""
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


def _date_du_parametre(request, nom):
    valeur = request.GET.get(nom)
    if not valeur:
        return None
    return datetime.date.fromisoformat(valeur) if _est_date_iso(valeur) else None


def _est_date_iso(valeur):
    try:
        datetime.date.fromisoformat(valeur)
    except ValueError:
        return False
    return True


def _filtres_champs(categorie, capacite_min, disponible_du, disponible_au):
    return [
        {
            "nom": "categorie",
            "libelle": "Catégorie",
            "valeur": categorie,
            "choix": ServiceLieu.choix_categorie(),
        },
        {
            "nom": "capacite_min",
            "libelle": "Capacité minimale",
            "valeur": capacite_min,
            "type": "numerique",
        },
        {
            "nom": "disponible_du",
            "libelle": "Disponible du",
            "valeur": disponible_du,
            "type": "date",
        },
        {
            "nom": "disponible_au",
            "libelle": "au",
            "valeur": disponible_au,
            "type": "date",
        },
    ]


def _filtres_actifs(request, categorie, capacite_min):
    actifs = []
    if categorie:
        actifs.append(
            {
                "libelle": f"Catégorie : {ServiceLieu.libelle_categorie(categorie)}",
                "url_retrait": _url_sans_parametre(request, "categorie"),
            }
        )
    if capacite_min:
        actifs.append(
            {
                "libelle": f"Capacité ≥ {capacite_min}",
                "url_retrait": _url_sans_parametre(request, "capacite_min"),
            }
        )
    return actifs


def _colonnes(tri_actuel):
    return [
        _colonne_tri(tri_actuel, "intitule", "Intitulé"),
        {"libelle": "Catégorie", "cle_tri": None},
        {"libelle": "Type", "cle_tri": None},
        _colonne_tri(tri_actuel, "capacite", "Capacité"),
        {"libelle": "Disponibilité", "cle_tri": None},
        {"libelle": "État", "cle_tri": None},
    ]


def _colonne_tri(tri_actuel, champ, libelle):
    etat = _etat_tri(tri_actuel, champ)
    return {
        "libelle": libelle,
        "cle_tri": champ,
        "tri_suivant": etat["suivant"],
        "sens": etat["sens"],
        "aria": etat["aria"],
    }


def _ligne(lieu, peut_ecrire):
    lien_intitule = format_html(
        '<a href="{}" class="text-marine-900 no-underline hover:underline">{}</a>',
        reverse("ressources:detail_lieu", args=[lieu.pk]),
        lieu.intitule,
    )
    ligne = {
        "cellules": [
            lien_intitule,
            _badge_categorie(lieu.categorie),
            lieu.get_type_partage_display() if lieu.type_partage else "—",
            format_html('<span class="tabular-nums">{}</span>', lieu.capacite),
            _badge_disponibilite(lieu.est_indisponible_maintenant),
            "Archivé" if lieu.archive else "Actif",
        ],
        "libelle": lieu.intitule,
        "archive": lieu.archive,
    }
    if peut_ecrire:
        ligne["url_modifier"] = reverse("ressources:modifier_lieu", args=[lieu.pk])
        ligne["url_archiver"] = reverse("ressources:archiver_lieu", args=[lieu.pk])
        ligne["url_desarchiver"] = reverse("ressources:desarchiver_lieu", args=[lieu.pk])
    return ligne


def _badge_categorie(categorie):
    """§ 1.2 de la charte : la couleur est doublée d'un mot."""
    return format_html(
        '<span class="{} px-2 py-px text-2xs font-semibold tracking-wide">{}</span>',
        CLASSES_BADGE_CATEGORIE[categorie],
        ServiceLieu.libelle_categorie(categorie).upper(),
    )


def _badge_disponibilite(est_indisponible):
    if est_indisponible:
        return mark_safe(
            '<span class="border border-etat-ecart px-2 py-px text-2xs font-semibold '
            'tracking-wide text-etat-ecart">INDISPONIBLE</span>'
        )
    return mark_safe(
        '<span class="border border-etat-conforme px-2 py-px text-2xs font-semibold '
        'tracking-wide text-etat-conforme">DISPONIBLE</span>'
    )


@exige_habilitation(ServiceLieu.PERMISSION_LECTURE)
def vue_liste_lieux(request):
    tri_actuel = request.GET.get("tri", "")
    categorie = request.GET.get("categorie", "")
    capacite_min = request.GET.get("capacite_min", "")
    disponible_du = _date_du_parametre(request, "disponible_du")
    disponible_au = _date_du_parametre(request, "disponible_au")
    filtres = {
        "recherche": request.GET.get("recherche", ""),
        "etat": request.GET.get("etat", ""),
        "categorie": categorie,
        "capacite_min": capacite_min,
        "disponible_du": disponible_du,
        "disponible_au": disponible_au,
        "tri": tri_actuel,
    }
    page = ServiceLieu.lister(request.user, filtres, request.GET.get("page"))
    peut_ecrire = a_permission(request.user, ServiceLieu.PERMISSION_ECRITURE)
    onglets, onglet_actif = onglets_ressources(request.user, "lieux")
    contexte = {
        "titre": "Lieux",
        "sous_titre": "Inventaire des salles et lieux partagés du centre.",
        "onglets": onglets,
        "onglet_actif": onglet_actif,
        "url_creer": reverse("ressources:creer_lieu") if peut_ecrire else "",
        "libelle_creer": "Créer un lieu",
        "champ_recherche_libelle": "Intitulé",
        "filtres": filtres,
        "filtres_champs": _filtres_champs(categorie, capacite_min, disponible_du, disponible_au),
        "filtres_actifs": _filtres_actifs(request, categorie, capacite_min),
        "url_liste": reverse("ressources:liste_lieux"),
        "colonnes": _colonnes(tri_actuel),
        "lignes": [_ligne(lieu, peut_ecrire) for lieu in page] if page else [],
        "libelle_vide": "Aucun lieu ne correspond aux filtres",
        "texte_vide": "Ajustez la recherche ou réinitialisez les filtres.",
        "page": page,
    }
    return render(request, "noyau/gestion/liste.html", contexte)


@exige_habilitation(ServiceLieu.PERMISSION_LECTURE)
def vue_detail_lieu(request, pk):
    lieu = _lieu_ou_404(pk)
    return render(
        request,
        "ressources/lieu_detail.html",
        {
            "lieu": lieu,
            "url_modifier": reverse("ressources:modifier_lieu", args=[lieu.pk]),
            "indisponibilites": ServiceIndisponibiliteLieu.lister_pour_lieu(request.user, lieu),
        },
    )


@exige_habilitation(ServiceLieu.PERMISSION_ECRITURE)
def vue_creer_lieu(request):
    if request.method == "POST":
        formulaire = FormulaireLieu(request.POST)
        if formulaire.is_valid():
            try:
                ServiceLieu.creer(request.user, formulaire.cleaned_data)
            except ErreurValidation as erreur:
                messages.error(request, str(erreur))
            else:
                messages.success(request, "Lieu créé.")
                return redirect("ressources:liste_lieux")
    else:
        formulaire = FormulaireLieu()
    return render(
        request,
        "noyau/gestion/formulaire.html",
        {
            "titre": "Créer un lieu",
            "groupes": GROUPES_FORMULAIRE,
            "form": formulaire,
            "url_annuler": reverse("ressources:liste_lieux"),
            "libelle_bouton": "Créer le lieu",
        },
    )


@exige_habilitation(ServiceLieu.PERMISSION_ECRITURE)
def vue_modifier_lieu(request, pk):
    lieu = _lieu_ou_404(pk)
    if request.method == "POST":
        return _traiter_modification(request, lieu)
    formulaire = FormulaireLieu(instance=lieu)
    return render(
        request, "noyau/gestion/formulaire.html", _contexte_modification(lieu, formulaire)
    )


def _traiter_modification(request, lieu):
    formulaire = FormulaireLieu(request.POST, instance=lieu)
    modifie_le_attendu = modifie_le_attendu_depuis_requete(request)
    if formulaire.is_valid():
        try:
            ServiceLieu.modifier(request.user, lieu.pk, formulaire.cleaned_data, modifie_le_attendu)
        except (ErreurValidation, ErreurModificationConcurrente) as erreur:
            messages.error(request, str(erreur))
        else:
            messages.success(request, "Lieu modifié.")
            return redirect("ressources:liste_lieux")
    return render(
        request, "noyau/gestion/formulaire.html", _contexte_modification(lieu, formulaire)
    )


def _contexte_modification(lieu, formulaire):
    return {
        "titre": f"Modifier « {lieu} »",
        "groupes": GROUPES_FORMULAIRE,
        "form": formulaire,
        "url_annuler": reverse("ressources:liste_lieux"),
        "libelle_bouton": "Enregistrer",
        "modifie_le_attendu": lieu.modifie_le,
    }


@exige_habilitation(ServiceLieu.PERMISSION_ECRITURE)
def vue_confirmer_archivage_lieu(request, pk):
    lieu = _lieu_ou_404(pk)
    if request.method == "POST":
        try:
            ServiceLieu.archiver(request.user, pk)
        except ErreurValidation as erreur:
            messages.error(request, str(erreur))
        else:
            messages.success(request, "Lieu archivé.")
        return redirect("ressources:liste_lieux")
    return render(
        request,
        "noyau/gestion/confirmer_archivage.html",
        {
            "titre_dialogue": f"Archiver « {lieu} »",
            "texte_explication": (
                f"« {lieu} » ne sera plus proposé pour une nouvelle affectation. "
                "L'historique de ses affectations passées est préservé."
            ),
            "url_annuler": reverse("ressources:liste_lieux"),
        },
    )


@require_POST
@exige_habilitation(ServiceLieu.PERMISSION_ECRITURE)
def vue_desarchiver_lieu(request, pk):
    _lieu_ou_404(pk)
    ServiceLieu.desarchiver(request.user, pk)
    messages.success(request, "Lieu désarchivé.")
    return redirect("ressources:liste_lieux")
