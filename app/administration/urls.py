from django.urls import path

from administration.views import authentification, comptes, habilitations, journal

app_name = "administration"

urlpatterns = [
    path("connexion/", authentification.vue_connexion, name="connexion"),
    path("deconnexion/", authentification.vue_deconnexion, name="deconnexion"),
    path(
        "mot-de-passe/changer/",
        comptes.vue_changer_mot_de_passe,
        name="changer_mot_de_passe",
    ),
    path("comptes/", comptes.vue_liste_comptes, name="liste_comptes"),
    path("comptes/creer/", comptes.vue_creer_compte, name="creer_compte"),
    path("comptes/<int:pk>/modifier/", comptes.vue_modifier_compte, name="modifier_compte"),
    path("comptes/<int:pk>/desactiver/", comptes.vue_desactiver_compte, name="desactiver_compte"),
    path("comptes/<int:pk>/reactiver/", comptes.vue_reactiver_compte, name="reactiver_compte"),
    path("habilitations/", habilitations.vue_habilitations, name="habilitations"),
    path("journal/", journal.vue_journal, name="journal"),
]
