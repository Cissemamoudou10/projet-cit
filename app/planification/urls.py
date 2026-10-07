from django.urls import path

from planification import views, views_circuit, views_periode, views_seance

app_name = "planification"

urlpatterns = [
    path("planification/generer/", views.vue_lancement_generation, name="lancement_generation"),
    path("planification/programme/", views.vue_consultation_programme, name="consultation_programme"),
    path(
        "planification/programmes/<int:pk>/seances/ajouter/",
        views_seance.ajouter_seance,
        name="ajouter_seance",
    ),
    path(
        "planification/periodes/<int:pk>/seances-impactees/",
        views_periode.seances_de_la_periode,
        name="seances_de_la_periode",
    ),
    path("planification/programmes/en-attente/", views_circuit.attente_validation, name="attente_validation"),
    path("planification/programmes/<int:pk>/soumettre/", views_circuit.soumettre, name="soumettre"),
    path("planification/programmes/<int:pk>/retirer-soumission/", views_circuit.retirer_soumission, name="retirer_soumission"),
    path("planification/programmes/<int:pk>/valider/", views_circuit.valider, name="valider"),
    path("planification/programmes/<int:pk>/rejeter/", views_circuit.rejeter, name="rejeter"),
    path("planification/programmes/<int:pk>/reprendre/", views_circuit.reprendre, name="reprendre"),
    path("planification/programmes/<int:pk>/signer/", views_circuit.signer, name="signer"),
    path("planification/programmes/<int:pk>/afficher/", views_circuit.afficher, name="afficher"),
    path("planification/programmes/<int:pk>/annuler-validation/", views_seance.annuler_validation, name="annuler_validation"),
    path("planification/seances/<int:pk>/modifier/", views_seance.modifier_seance, name="modifier_seance"),
    path("planification/seances/<int:pk>/supprimer/", views_seance.supprimer_seance, name="supprimer_seance"),
    path("planification/seances/<int:pk>/deverrouiller/", views_seance.deverrouiller_seance, name="deverrouiller_seance"),
    path("planification/seances/<int:pk>/brigades/", views_seance.gerer_brigades, name="gerer_brigades"),
    path(
        "planification/seances/<int:pk>/brigades/retirer/",
        views_seance.retirer_brigade,
        name="retirer_brigade",
    ),
]
