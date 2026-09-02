"""Vues d'authentification — orchestrent, ne décident rien. Toute la
logique métier vit dans administration.services.authentification.
"""

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from administration.forms import FormulaireConnexion
from administration.services.authentification import ServiceAuthentification
from noyau.exceptions import ErreurAuthentification, ErreurCompteDesactive, ErreurCompteVerrouille


def vue_connexion(request):
    if request.user.is_authenticated:
        return redirect(_destination(request))  # A1 — session déjà ouverte

    formulaire = FormulaireConnexion(request.POST or None)

    if request.method == "POST" and formulaire.is_valid():
        try:
            utilisateur = ServiceAuthentification.authentifier(
                formulaire.cleaned_data["identifiant"],
                formulaire.cleaned_data["mot_de_passe"],
            )
        except (ErreurAuthentification, ErreurCompteDesactive, ErreurCompteVerrouille) as erreur:
            messages.error(request, str(erreur))
        else:
            login(request, utilisateur)
            return redirect(_destination(request))

    return render(request, "administration/connexion.html", {"form": formulaire})


@require_POST
def vue_deconnexion(request):
    logout(request)
    return redirect(settings.LOGOUT_REDIRECT_URL)


def _destination(request):
    """Le paramètre `next` est validé avant toute redirection — sans quoi
    l'écran de connexion devient une redirection ouverte (E4).
    """
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url and url_has_allowed_host_and_scheme(
        next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return next_url
    return settings.LOGIN_REDIRECT_URL
