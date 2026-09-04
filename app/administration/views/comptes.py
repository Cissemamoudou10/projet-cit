"""Vues de gestion des comptes — orchestrent, ne décident rien. Toute la
logique métier vit dans administration.services.comptes. Aucun import de
`administration.models` : la vue passe par le service, y compris pour
retrouver un compte par identifiant technique (`ServiceCompte.obtenir`).
"""

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.http import Http404
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from administration.forms import (
    FormulaireChangementMotDePasse,
    FormulaireCompte,
    FormulaireCreationCompte,
)
from administration.habilitations import exige_habilitation
from administration.navigation import onglets_administration
from administration.services.comptes import PERMISSION_GESTION_COMPTES, ServiceCompte
from noyau.exceptions import ErreurIntrouvable, ErreurValidation


def _compte_ou_404(pk):
    try:
        return ServiceCompte.obtenir(pk)
    except ErreurIntrouvable as erreur:
        raise Http404 from erreur


@exige_habilitation(PERMISSION_GESTION_COMPTES)
def vue_liste_comptes(request):
    tri_actuel = request.GET.get("tri", "")
    filtres = {
        "recherche": request.GET.get("recherche", ""),
        "profil": request.GET.get("profil", ""),
        "etat": request.GET.get("etat", ""),
        "tri": tri_actuel,
    }
    page = ServiceCompte.lister(request.user, filtres, request.GET.get("page"))
    onglets, onglet_actif = onglets_administration(request.user, "comptes")
    contexte = {
        "page": page,
        "filtres": filtres,
        "profils": ServiceCompte.profils_disponibles(),
        "tri_identifiant": _etat_tri(tri_actuel, "identifiant"),
        "tri_derniere_connexion": _etat_tri(tri_actuel, "derniere_connexion"),
        "onglets": onglets,
        "onglet_actif": onglet_actif,
    }
    return render(request, "administration/liste_comptes.html", contexte)


def _etat_tri(tri_actuel, colonne):
    """§ 3.09 : construit l'état d'affichage d'un en-tête triable — pas une
    règle métier, seulement la traduction d'un paramètre d'URL en attribut
    `aria-sort` et en cible de bascule. Le gabarit ne calcule rien lui-même.
    """
    if tri_actuel == colonne:
        return {"aria": "ascending", "suivant": f"-{colonne}", "sens": "asc"}
    if tri_actuel == f"-{colonne}":
        return {"aria": "descending", "suivant": colonne, "sens": "desc"}
    return {"aria": "none", "suivant": colonne, "sens": None}


@exige_habilitation(PERMISSION_GESTION_COMPTES)
def vue_creer_compte(request):
    formulaire = FormulaireCreationCompte(request.POST or None)

    if request.method == "POST" and formulaire.is_valid():
        try:
            ServiceCompte.creer(request.user, formulaire.cleaned_data)
        except ErreurValidation as erreur:
            formulaire.add_error(None, str(erreur))
        else:
            messages.success(request, "Compte créé. Un mot de passe initial a été défini.")
            return redirect("administration:liste_comptes")

    return render(
        request, "administration/formulaire_compte.html", {"form": formulaire, "creation": True}
    )


@exige_habilitation(PERMISSION_GESTION_COMPTES)
def vue_modifier_compte(request, pk):
    compte = _compte_ou_404(pk)
    formulaire = FormulaireCompte(
        request.POST or None,
        initial={
            "identifiant": compte.username,
            "grade": compte.grade,
            "prenom": compte.first_name,
            "nom": compte.last_name,
            "profil": compte.profil,
        },
    )

    if request.method == "POST" and formulaire.is_valid():
        try:
            ServiceCompte.modifier(request.user, compte, formulaire.cleaned_data)
        except ErreurValidation as erreur:
            formulaire.add_error(None, str(erreur))
        else:
            messages.success(request, "Compte modifié.")
            return redirect("administration:liste_comptes")

    return render(
        request,
        "administration/formulaire_compte.html",
        {"form": formulaire, "creation": False, "compte": compte},
    )


@exige_habilitation(PERMISSION_GESTION_COMPTES)
def vue_desactiver_compte(request, pk):
    compte = _compte_ou_404(pk)

    if request.method == "POST":
        try:
            ServiceCompte.desactiver(request.user, compte)
        except ErreurValidation as erreur:
            messages.error(request, str(erreur))
        else:
            messages.success(request, "Compte désactivé.")
        return redirect("administration:liste_comptes")

    return render(request, "administration/confirmer_desactivation.html", {"compte": compte})


@require_POST
@exige_habilitation(PERMISSION_GESTION_COMPTES)
def vue_reactiver_compte(request, pk):
    compte = _compte_ou_404(pk)
    ServiceCompte.reactiver(request.user, compte)
    messages.success(request, "Compte réactivé.")
    return redirect("administration:liste_comptes")


def vue_changer_mot_de_passe(request):
    """Aucune habilitation à vérifier ici : tout utilisateur authentifié
    change son propre mot de passe, quel que soit son profil.
    """
    formulaire = FormulaireChangementMotDePasse(request.POST or None)

    if request.method == "POST" and formulaire.is_valid():
        try:
            ServiceCompte.changer_mot_de_passe(
                request.user,
                formulaire.cleaned_data["ancien_mot_de_passe"],
                formulaire.cleaned_data["nouveau_mot_de_passe"],
            )
        except ErreurValidation as erreur:
            formulaire.add_error(None, str(erreur))
        else:
            # Sans ceci, la session courante serait invalidée par le
            # changement de condensat — l'utilisateur se retrouverait
            # déconnecté juste après avoir changé son mot de passe.
            update_session_auth_hash(request, request.user)
            messages.success(request, "Mot de passe modifié.")
            return redirect(settings.LOGIN_REDIRECT_URL)

    return render(request, "administration/changer_mot_de_passe.html", {"form": formulaire})
