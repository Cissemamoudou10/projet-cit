"""Vue d'accueil technique — pas un écran métier. US-ADM-01 n'en construit
aucun ; elle sert uniquement de cible à LOGIN_REDIRECT_URL le temps que les
rubriques métier existent.
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def accueil(request):
    return render(request, "noyau/accueil.html")
