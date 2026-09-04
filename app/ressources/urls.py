from django.urls import path

from ressources.views import indisponibilite_lieu, instructeur, lieu, qualification

app_name = "ressources"

urlpatterns = [
    path("lieux/", lieu.vue_liste_lieux, name="liste_lieux"),
    path("lieux/creer/", lieu.vue_creer_lieu, name="creer_lieu"),
    path("lieux/<int:pk>/", lieu.vue_detail_lieu, name="detail_lieu"),
    path("lieux/<int:pk>/modifier/", lieu.vue_modifier_lieu, name="modifier_lieu"),
    path("lieux/<int:pk>/archiver/", lieu.vue_confirmer_archivage_lieu, name="archiver_lieu"),
    path("lieux/<int:pk>/desarchiver/", lieu.vue_desarchiver_lieu, name="desarchiver_lieu"),
    path(
        "lieux/<int:lieu_pk>/indisponibilites/declarer/",
        indisponibilite_lieu.vue_declarer_indisponibilite,
        name="declarer_indisponibilite_lieu",
    ),
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
