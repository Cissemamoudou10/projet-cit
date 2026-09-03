"""URLconf racine."""

from django.contrib import admin
from django.urls import include, path
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    # Racine sans écran propre : redirige vers l'accueil, qui redirige
    # lui-même vers la connexion si la session n'est pas ouverte
    # (ConnexionObligatoireMiddleware) — jamais d'erreur sur "/".
    path("", RedirectView.as_view(pattern_name="noyau:accueil", permanent=False)),
    path("", include("noyau.urls")),
    path("", include("administration.urls")),
    path("", include("referentiel.urls")),
]
