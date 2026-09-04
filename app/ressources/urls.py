from django.urls import path

from ressources.views import instructeur, qualification

app_name = "ressources"

urlpatterns = [
    path("instructeurs/", instructeur.vue_liste_instructeurs, name="liste_instructeurs"),
    path("instructeurs/creer/", instructeur.vue_creer_instructeur, name="creer_instructeur"),
    path("instructeurs/<int:pk>/", instructeur.vue_detail_instructeur, name="detail_instructeur"),
    path(
        "instructeurs/<int:pk>/modifier/",
        instructeur.vue_modifier_instructeur,
        name="modifier_instructeur",
    ),
    path(
        "instructeurs/<int:pk>/archiver/",
        instructeur.vue_confirmer_archivage_instructeur,
        name="archiver_instructeur",
    ),
    path(
        "instructeurs/<int:pk>/desarchiver/",
        instructeur.vue_desarchiver_instructeur,
        name="desarchiver_instructeur",
    ),
    path(
        "instructeurs/<int:pk>/qualifications/",
        qualification.vue_qualifications_instructeur,
        name="qualifications_instructeur",
    ),
    path(
        "instructeurs/<int:instructeur_pk>/qualifications/<int:matiere_pk>/ajouter/",
        qualification.vue_ajouter_qualification,
        {"origine": "instructeur"},
        name="ajouter_qualification_instructeur",
    ),
    path(
        "qualifications/matieres/<int:pk>/",
        qualification.vue_qualifications_matiere,
        name="qualifications_matiere",
    ),
    path(
        "qualifications/matieres/<int:matiere_pk>/instructeurs/<int:instructeur_pk>/ajouter/",
        qualification.vue_ajouter_qualification,
        {"origine": "matiere"},
        name="ajouter_qualification_matiere",
    ),
    path(
        "qualifications/<int:pk>/retirer/depuis-instructeur/",
        qualification.vue_confirmer_retrait_qualification,
        {"origine": "instructeur"},
        name="retirer_qualification_instructeur",
    ),
    path(
        "qualifications/<int:pk>/retirer/depuis-matiere/",
        qualification.vue_confirmer_retrait_qualification,
        {"origine": "matiere"},
        name="retirer_qualification_matiere",
    ),
    path(
        "qualifications/formations/<int:formation_pk>/couverture/",
        qualification.vue_couverture_qualifications,
        name="couverture_qualifications",
    ),
]
