from django.urls import path

from evaluations import views, views_moyennes, views_notes, views_organisation, views_sujets

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
    path(
        "evaluations/sessions/<int:session_pk>/moyennes/",
        views_moyennes.vue_moyennes,
        name="moyennes_session",
    ),
    path("evaluations/<int:pk>/notes/", views_notes.vue_notes, name="notes"),
    path(
        "evaluations/<int:pk>/notes/confirmer/",
        views_notes.vue_confirmer_notes,
        name="confirmer_notes",
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
    path(
        "evaluations/<int:pk>/organisation/",
        views_organisation.vue_organisation,
        name="organisation",
    ),
    path(
        "evaluations/<int:pk>/organisation/creneau/",
        views_organisation.vue_fixer_creneau,
        name="fixer_creneau",
    ),
    path(
        "evaluations/<int:pk>/organisation/ajouter/",
        views_organisation.vue_ajouter_organisation,
        name="ajouter_organisation",
    ),
    path(
        "evaluations/organisations/<int:pk>/retirer/",
        views_organisation.vue_retirer_organisation,
        name="retirer_organisation",
    ),
    path(
        "evaluations/organisations/<int:pk>/surveillant/",
        views_organisation.vue_ajouter_surveillant,
        name="ajouter_surveillant",
    ),
    path(
        "evaluations/surveillances/<int:pk>/retirer/",
        views_organisation.vue_retirer_surveillant,
        name="retirer_surveillant",
    ),
    path(
        "evaluations/<int:pk>/convocation/", views_organisation.vue_convocation, name="convocation"
    ),
]
