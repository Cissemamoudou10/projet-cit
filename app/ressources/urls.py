from django.urls import path

from ressources.views import instructeur

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
]
