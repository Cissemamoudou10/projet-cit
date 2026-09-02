"""Intergiciel de changement de mot de passe obligatoire — Prompt 02, § 2.2.

Vit dans `administration`, pas `noyau` : la règle qu'il consulte
(`ServiceCompte.doit_changer_mot_de_passe`) est un service d'administration,
et `noyau` ne dépend d'aucune application — voir docs/suivi/DECISIONS.md, D-08.

L'intergiciel redirige, il ne décide pas : la règle est une méthode du
service.
"""

from django.conf import settings
from django.shortcuts import redirect
from django.urls import Resolver404, resolve

from administration.services.comptes import ServiceCompte

VUES_LAISSEES_PASSER = {
    "administration:changer_mot_de_passe",
    "administration:deconnexion",
}


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
        prefixe_statique = "/" + settings.STATIC_URL.lstrip("/")
        if request.path.startswith(prefixe_statique):
            return False
        if self._vue_demandee_est_laissee_passer(request.path):
            return False
        return ServiceCompte.doit_changer_mot_de_passe(request.user)

    @staticmethod
    def _vue_demandee_est_laissee_passer(chemin):
        try:
            correspondance = resolve(chemin)
        except Resolver404:
            return False
        nom_vue = (
            f"{correspondance.namespace}:{correspondance.url_name}"
            if correspondance.namespace
            else correspondance.url_name
        )
        return nom_vue in VUES_LAISSEES_PASSER
