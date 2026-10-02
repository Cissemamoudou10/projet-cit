from django.urls import path

from evaluations import views

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
]
