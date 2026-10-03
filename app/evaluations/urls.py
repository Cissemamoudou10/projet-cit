from django.urls import path

from evaluations import views, views_sujets

app_name = "evaluations"

urlpatterns = [
    path("evaluations/", views.vue_liste_evaluations, name="liste_evaluations"),
    path("evaluations/creer/", views.vue_creer_evaluation, name="creer_evaluation"),
    path("evaluations/<int:pk>/", views.vue_detail_evaluation, name="detail_evaluation"),
    path(
        "evaluations/<int:pk>/modifier-date/",
        views.vue_modifier_date_certificative,
        name="modifier_date_certificative",
    ),
    path("evaluations/<int:pk>/sujets/", views_sujets.vue_sujets, name="sujets"),
    path(
        "evaluations/sujets/<int:pk>/corriger/",
        views_sujets.vue_corriger_sujet,
        name="corriger_sujet",
    ),
    path(
        "evaluations/sujets/<int:pk>/supprimer/",
        views_sujets.vue_supprimer_sujet,
        name="supprimer_sujet",
    ),
    path(
        "evaluations/sujets/<int:pk>/retenir/",
        views_sujets.vue_retenir_sujet,
        name="retenir_sujet",
    ),
    path(
        "evaluations/sujets/<int:pk>/changer-retenu/",
        views_sujets.vue_changer_retenu_sujet,
        name="changer_retenu_sujet",
    ),
]
