"""Vue d'accueil — US-ADM-01 (cible de LOGIN_REDIRECT_URL) puis US-IHM-01
(prompt 64, tableau de bord). `noyau` ne peut importer aucune application
métier (`tests/architecture/test_couches.py`) : le tableau de bord lui-même
est résolu par `noyau.services.parametres.ResolveurTableauBordAccueil`,
dont `evaluations` installe le fournisseur réel au démarrage — cette vue ne
fait qu'appeler le résolveur et afficher ce qu'il rend.
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from noyau.services.parametres import ResolveurTableauBordAccueil


@login_required
def accueil(request):
    tableau = ResolveurTableauBordAccueil.resoudre(request.user)
    return render(request, "noyau/accueil.html", {"tableau": tableau})
