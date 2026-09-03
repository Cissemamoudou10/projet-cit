from django.urls import path

from referentiel.views import formation, type_formation

app_name = "referentiel"

urlpatterns = [
    path(
        "types-formation/", type_formation.vue_liste_types_formation, name="liste_types_formation"
    ),
    path(
        "types-formation/creer/",
        type_formation.vue_creer_type_formation,
        name="creer_type_formation",
    ),
    path(
        "types-formation/<int:pk>/modifier/",
        type_formation.vue_modifier_type_formation,
        name="modifier_type_formation",
    ),
    path(
        "types-formation/<int:pk>/archiver/",
        type_formation.vue_confirmer_archivage_type_formation,
        name="archiver_type_formation",
    ),
    path(
        "types-formation/<int:pk>/desarchiver/",
        type_formation.vue_desarchiver_type_formation,
        name="desarchiver_type_formation",
    ),
    path("formations/", formation.vue_liste_formations, name="liste_formations"),
    path("formations/creer/", formation.vue_creer_formation, name="creer_formation"),
    path("formations/<int:pk>/", formation.vue_detail_formation, name="detail_formation"),
    path(
        "formations/<int:pk>/modifier/", formation.vue_modifier_formation, name="modifier_formation"
    ),
    path(
        "formations/<int:pk>/archiver/",
        formation.vue_confirmer_archivage_formation,
        name="archiver_formation",
    ),
    path(
        "formations/<int:pk>/desarchiver/",
        formation.vue_desarchiver_formation,
        name="desarchiver_formation",
    ),
]
