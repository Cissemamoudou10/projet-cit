from django.urls import path

from referentiel import views

app_name = "referentiel"

urlpatterns = [
    path("types-formation/", views.vue_liste_types_formation, name="liste_types_formation"),
    path("types-formation/creer/", views.vue_creer_type_formation, name="creer_type_formation"),
    path(
        "types-formation/<int:pk>/modifier/",
        views.vue_modifier_type_formation,
        name="modifier_type_formation",
    ),
    path(
        "types-formation/<int:pk>/archiver/",
        views.vue_confirmer_archivage_type_formation,
        name="archiver_type_formation",
    ),
    path(
        "types-formation/<int:pk>/desarchiver/",
        views.vue_desarchiver_type_formation,
        name="desarchiver_type_formation",
    ),
]
