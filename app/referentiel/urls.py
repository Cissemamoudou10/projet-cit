from django.urls import path

from referentiel.views import formation, matiere, referentiel, type_formation

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
    path("matieres/", matiere.vue_liste_matieres, name="liste_matieres"),
    path("matieres/creer/", matiere.vue_creer_matiere, name="creer_matiere"),
    path("matieres/<int:pk>/", matiere.vue_detail_matiere, name="detail_matiere"),
    path("matieres/<int:pk>/modifier/", matiere.vue_modifier_matiere, name="modifier_matiere"),
    path(
        "matieres/<int:pk>/archiver/",
        matiere.vue_confirmer_archivage_matiere,
        name="archiver_matiere",
    ),
    path(
        "matieres/<int:pk>/desarchiver/",
        matiere.vue_desarchiver_matiere,
        name="desarchiver_matiere",
    ),
    path(
        "formations/<int:formation_pk>/referentiel/",
        referentiel.vue_referentiel_formation,
        name="referentiel_formation",
    ),
    path(
        "formations/<int:formation_pk>/referentiel/rattacher/",
        referentiel.vue_rattacher_matiere,
        name="rattacher_matiere",
    ),
    path(
        "formations/<int:formation_pk>/referentiel/creer-matiere/",
        referentiel.vue_creer_matiere_depuis_referentiel,
        name="creer_matiere_depuis_referentiel",
    ),
    path(
        "formations/<int:formation_pk>/referentiel/<int:element_pk>/modifier/",
        referentiel.vue_modifier_element_referentiel,
        name="modifier_element_referentiel",
    ),
    path(
        "formations/<int:formation_pk>/referentiel/<int:element_pk>/retirer/",
        referentiel.vue_confirmer_retrait_element_referentiel,
        name="retirer_element_referentiel",
    ),
]
