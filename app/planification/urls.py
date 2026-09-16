from django.urls import path

from planification import views

app_name = "planification"

urlpatterns = [
    path("planification/generer/", views.vue_lancement_generation, name="lancement_generation"),
    path("planification/programme/", views.vue_consultation_programme, name="consultation_programme"),
]
