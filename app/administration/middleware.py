"""Intergiciels d'authentification — Prompt 02, § 2.2, et confort de
session.

Vivent dans `administration`, pas `noyau` : la règle que le premier consulte
(`ServiceCompte.doit_changer_mot_de_passe`) est un service d'administration,
et `noyau` ne dépend d'aucune application — voir docs/suivi/DECISIONS.md, D-08.

Les deux intergiciels redirigent, ils ne décident pas : la règle vient d'un
service ou de `request.user.is_authenticated`, jamais d'une logique propre.
"""

from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.shortcuts import redirect
from django.urls import Resolver404, resolve

from administration.services.comptes import ServiceCompte

VUES_LAISSEES_PASSER = {
    "administration:changer_mot_de_passe",
    "administration:deconnexion",
}

VUES_PUBLIQUES = {
    "administration:connexion",
    "administration:deconnexion",
}


def _nom_vue(chemin):
    """`None` si l'URL ne résout vers aucune vue — un 404 franc, pas une
    raison de rediriger vers quoi que ce soit.
    """
    try:
        correspondance = resolve(chemin)
    except Resolver404:
        return None
    if correspondance.namespace:
        return f"{correspondance.namespace}:{correspondance.url_name}"
    return correspondance.url_name


def _chemin_statique(request):
    prefixe_statique = "/" + settings.STATIC_URL.lstrip("/")
    return request.path.startswith(prefixe_statique)


class ConnexionObligatoireMiddleware:
    """Sans cet intergiciel, une session expirée (ou tout accès anonyme)
    tombe sur le 403 levé par `administration.habilitations.
    exige_habilitation` — `ErreurHabilitation` ne distingue pas « non
    connecté » de « connecté sans le droit demandé » — au lieu de proposer
    de se reconnecter, comme le fait déjà `noyau.views.accueil` via
    `@login_required`. Généralise ce même comportement à tout l'applicatif,
    plutôt que de décorer une à une les vues des cinq applications
    métier — l'admin Django (`/admin/`) gère sa propre authentification et
    reste hors du périmètre de cet intergiciel.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self._doit_rediriger(request):
            return redirect_to_login(request.get_full_path(), login_url=settings.LOGIN_URL)
        return self.get_response(request)

    def _doit_rediriger(self, request):
        if request.user.is_authenticated:
            return False
        if _chemin_statique(request):
            return False
        if request.path.startswith("/admin/"):
            return False
        nom_vue = _nom_vue(request.path)
        return nom_vue is not None and nom_vue not in VUES_PUBLIQUES


class ChangementMotDePasseObligatoireMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if self._doit_intercepter(request):
            return redirect("administration:changer_mot_de_passe")
        return self.get_response(request)

    def _doit_intercepter(self, request):
        if not request.user.is_authenticated:
            return False
        if _chemin_statique(request):
            return False
        if _nom_vue(request.path) in VUES_LAISSEES_PASSER:
            return False
        return ServiceCompte.doit_changer_mot_de_passe(request.user)
