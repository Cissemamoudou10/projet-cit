from django.urls import path

from noyau import views

app_name = "noyau"

urlpatterns = [
    path("accueil/", views.accueil, name="accueil"),
]
