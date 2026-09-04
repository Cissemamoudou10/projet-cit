"""Vues de gestion des instructeurs — orchestrent, ne décident rien. Toute
la logique métier vit dans ressources.services.instructeur.ServiceInstructeur.
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
from ressources.forms import FormulaireInstructeur
from ressources.services.instructeur import ServiceInstructeur

CLASSES_BADGE_STATUT = {
    "militaire_du_centre": "bg-marine-900 text-blanc",
    "vacataire": "border border-marine-700 text-marine-700",
    "civil": "border border-gris-trait text-gris-lecture",
}

GROUPES_FORMULAIRE = [
    {"legende": "Identité", "champs": ["nom", "prenom", "matricule", "grade"]},
    {"legende": "Rattachement", "champs": ["specialite", "statut"]},
]


def _instructeur_ou_404(pk):
    try:
        return ServiceInstructeur.obtenir(pk)
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


def _filtres_champs(statut, specialite):
    return [
        {
            "nom": "statut",
            "libelle": "Statut",
            "valeur": statut,
            "choix": ServiceInstructeur.choix_statut(),
        },
        {
            "nom": "specialite",
            "libelle": "Spécialité",
            "valeur": specialite,
            "choix": [(v, v) for v in ServiceInstructeur.valeurs_specialite_distinctes()],
        },
    ]


def _filtres_actifs(request, statut, specialite):
    actifs = []
    if statut:
        actifs.append(
            {
                "libelle": f"Statut : {ServiceInstructeur.libelle_statut(statut)}",
                "url_retrait": _url_sans_parametre(request, "statut"),
            }
        )
    if specialite:
        actifs.append(
            {
                "libelle": f"Spécialité : {specialite}",
                "url_retrait": _url_sans_parametre(request, "specialite"),
            }
        )
    return actifs


def _colonnes(tri_actuel):
    return [
        _colonne_tri(tri_actuel, "matricule", "Matricule"),
        {"libelle": "Grade", "cle_tri": None},
        _colonne_tri(tri_actuel, "nom", "Nom et prénom"),
        {"libelle": "Spécialité", "cle_tri": None},
        {"libelle": "Statut", "cle_tri": None},
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


def _ligne(instructeur, peut_ecrire):
    lien_nom = format_html(
        '<a href="{}" class="text-marine-900 no-underline hover:underline">{} {}</a>',
        reverse("ressources:detail_instructeur", args=[instructeur.pk]),
        instructeur.nom,
        instructeur.prenom,
    )
    ligne = {
        "cellules": [
            format_html('<span class="font-mono">{}</span>', instructeur.matricule or "—"),
            instructeur.grade,
            lien_nom,
            instructeur.specialite,
            _badge_statut(instructeur.statut),
            "Archivé" if instructeur.archive else "Actif",
        ],
        "libelle": f"{instructeur.nom} {instructeur.prenom}",
        "archive": instructeur.archive,
    }
    if peut_ecrire:
        ligne["url_modifier"] = reverse("ressources:modifier_instructeur", args=[instructeur.pk])
        ligne["url_archiver"] = reverse("ressources:archiver_instructeur", args=[instructeur.pk])
        ligne["url_desarchiver"] = reverse(
            "ressources:desarchiver_instructeur", args=[instructeur.pk]
        )
    return ligne


def _badge_statut(statut):
    """§ 8 du Prompt 12 : trois états neutres, jamais les couleurs `etat.*`
    (jugement de conformité, inadapté à un statut d'emploi) — amendement
    docs/suivi/CHARTE-INTEGRATION.md.
    """
    return format_html(
        '<span class="{} px-2 py-px text-2xs font-semibold tracking-wide">{}</span>',
        CLASSES_BADGE_STATUT[statut],
        ServiceInstructeur.libelle_statut(statut).upper(),
    )


@exige_habilitation(ServiceInstructeur.PERMISSION_LECTURE)
def vue_liste_instructeurs(request):
    tri_actuel = request.GET.get("tri", "")
    statut = request.GET.get("statut", "")
    specialite = request.GET.get("specialite", "")
    filtres = {
        "recherche": request.GET.get("recherche", ""),
        "etat": request.GET.get("etat", ""),
        "statut": statut,
        "specialite": specialite,
        "tri": tri_actuel,
    }
    page = ServiceInstructeur.lister(request.user, filtres, request.GET.get("page"))
    peut_ecrire = a_permission(request.user, ServiceInstructeur.PERMISSION_ECRITURE)
    contexte = {
        "titre": "Instructeurs",
        "sous_titre": "Annuaire du corps enseignant du centre.",
        "url_creer": reverse("ressources:creer_instructeur") if peut_ecrire else "",
        "libelle_creer": "Créer un instructeur",
        "champ_recherche_libelle": "Nom, prénom ou matricule",
        "filtres": filtres,
        "filtres_champs": _filtres_champs(statut, specialite),
        "filtres_actifs": _filtres_actifs(request, statut, specialite),
        "url_liste": reverse("ressources:liste_instructeurs"),
        "colonnes": _colonnes(tri_actuel),
        "lignes": [_ligne(instructeur, peut_ecrire) for instructeur in page] if page else [],
        "libelle_vide": "Aucun instructeur ne correspond aux filtres",
        "texte_vide": "Ajustez la recherche ou réinitialisez les filtres.",
        "page": page,
    }
    return render(request, "noyau/gestion/liste.html", contexte)


@exige_habilitation(ServiceInstructeur.PERMISSION_LECTURE)
def vue_detail_instructeur(request, pk):
    instructeur = _instructeur_ou_404(pk)
    return render(
        request,
        "ressources/instructeur_detail.html",
        {
            "instructeur": instructeur,
            "url_modifier": reverse("ressources:modifier_instructeur", args=[instructeur.pk]),
        },
    )


@exige_habilitation(ServiceInstructeur.PERMISSION_ECRITURE)
def vue_creer_instructeur(request):
    if request.method == "POST":
        formulaire = FormulaireInstructeur(request.POST)
        if formulaire.is_valid():
            try:
                ServiceInstructeur.creer(request.user, formulaire.cleaned_data)
            except ErreurValidation as erreur:
                messages.error(request, str(erreur))
            else:
                messages.success(request, "Instructeur créé.")
                return redirect("ressources:liste_instructeurs")
    else:
        formulaire = FormulaireInstructeur()
    return render(
        request,
        "noyau/gestion/formulaire.html",
        {
            "titre": "Créer un instructeur",
            "groupes": GROUPES_FORMULAIRE,
            "form": formulaire,
            "url_annuler": reverse("ressources:liste_instructeurs"),
            "libelle_bouton": "Créer l'instructeur",
        },
    )


@exige_habilitation(ServiceInstructeur.PERMISSION_ECRITURE)
def vue_modifier_instructeur(request, pk):
    instructeur = _instructeur_ou_404(pk)
    if request.method == "POST":
        return _traiter_modification(request, instructeur)
    formulaire = FormulaireInstructeur(instance=instructeur)
    return render(
        request, "noyau/gestion/formulaire.html", _contexte_modification(instructeur, formulaire)
    )


def _traiter_modification(request, instructeur):
    formulaire = FormulaireInstructeur(request.POST, instance=instructeur)
    modifie_le_attendu = modifie_le_attendu_depuis_requete(request)
    if formulaire.is_valid():
        try:
            ServiceInstructeur.modifier(
                request.user, instructeur.pk, formulaire.cleaned_data, modifie_le_attendu
            )
        except (ErreurValidation, ErreurModificationConcurrente) as erreur:
            messages.error(request, str(erreur))
        else:
            messages.success(request, "Instructeur modifié.")
            return redirect("ressources:liste_instructeurs")
    return render(
        request, "noyau/gestion/formulaire.html", _contexte_modification(instructeur, formulaire)
    )


def _contexte_modification(instructeur, formulaire):
    return {
        "titre": f"Modifier « {instructeur} »",
        "groupes": GROUPES_FORMULAIRE,
        "form": formulaire,
        "url_annuler": reverse("ressources:liste_instructeurs"),
        "libelle_bouton": "Enregistrer",
        "modifie_le_attendu": instructeur.modifie_le,
    }


@exige_habilitation(ServiceInstructeur.PERMISSION_ECRITURE)
def vue_confirmer_archivage_instructeur(request, pk):
    instructeur = _instructeur_ou_404(pk)
    if request.method == "POST":
        try:
            ServiceInstructeur.archiver(request.user, pk)
        except ErreurValidation as erreur:
            messages.error(request, str(erreur))
        else:
            messages.success(request, "Instructeur archivé.")
        return redirect("ressources:liste_instructeurs")
    return render(
        request,
        "noyau/gestion/confirmer_archivage.html",
        {
            "titre_dialogue": f"Archiver « {instructeur} »",
            "texte_explication": (
                f"« {instructeur} » ne sera plus proposé pour une nouvelle affectation. "
                "L'historique de ses affectations passées est préservé."
            ),
            "url_annuler": reverse("ressources:liste_instructeurs"),
        },
    )


@require_POST
@exige_habilitation(ServiceInstructeur.PERMISSION_ECRITURE)
def vue_desarchiver_instructeur(request, pk):
    _instructeur_ou_404(pk)
    ServiceInstructeur.desarchiver(request.user, pk)
    messages.success(request, "Instructeur désarchivé.")
    return redirect("ressources:liste_instructeurs")
