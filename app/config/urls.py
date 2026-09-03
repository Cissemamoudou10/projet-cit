"""URLconf racine."""

from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("noyau.urls")),
    path("", include("administration.urls")),
    path("", include("referentiel.urls")),
]
