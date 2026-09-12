from django.urls import path

from organisation.views import brigade, import_stagiaires, session, stagiaire

app_name = "organisation"

urlpatterns = [
    path("sessions/", session.vue_liste_sessions, name="liste_sessions"),
    path("sessions/creer/", session.vue_creer_session, name="creer_session"),
    path("sessions/<int:pk>/", session.vue_detail_session, name="detail_session"),
    path("sessions/<int:pk>/modifier/", session.vue_modifier_session, name="modifier_session"),
    path(
        "sessions/<int:pk>/supprimer/",
        session.vue_confirmer_suppression_session,
        name="supprimer_session",
    ),
    path(
        "sessions/<int:session_pk>/brigades/",
        brigade.vue_brigades_session,
        name="brigades_session",
    ),
    path(
        "sessions/<int:session_pk>/brigades/creer/",
        brigade.vue_creer_brigade,
        name="creer_brigade",
    ),
    path(
        "sessions/<int:session_pk>/brigades/<int:brigade_pk>/modifier/",
        brigade.vue_modifier_brigade,
        name="modifier_brigade",
    ),
    path(
        "sessions/<int:session_pk>/brigades/<int:brigade_pk>/supprimer/",
        brigade.vue_confirmer_suppression_brigade,
        name="supprimer_brigade",
    ),
    path(
        "sessions/<int:session_pk>/stagiaires/",
        stagiaire.vue_liste_stagiaires,
        name="liste_stagiaires",
    ),
    path(
        "sessions/<int:session_pk>/stagiaires/creer/",
        stagiaire.vue_creer_stagiaire,
        name="creer_stagiaire",
    ),
    path(
        "sessions/<int:session_pk>/stagiaires/<int:pk>/modifier/",
        stagiaire.vue_modifier_stagiaire,
        name="modifier_stagiaire",
    ),
    path(
        "sessions/<int:session_pk>/stagiaires/<int:pk>/radier/",
        stagiaire.vue_confirmer_radiation_stagiaire,
        name="radier_stagiaire",
    ),
    path(
        "sessions/<int:session_pk>/stagiaires/<int:pk>/deradier/",
        stagiaire.vue_deradier_stagiaire,
        name="deradier_stagiaire",
    ),
    path(
        "sessions/<int:session_pk>/stagiaires/<int:pk>/supprimer/",
        stagiaire.vue_confirmer_suppression_stagiaire,
        name="supprimer_stagiaire",
    ),
    path(
        "sessions/<int:session_pk>/stagiaires/importer/",
        import_stagiaires.vue_importer_stagiaires,
        name="importer_stagiaires",
    ),
    path(
        "sessions/<int:session_pk>/stagiaires/importer/confirmer/",
        import_stagiaires.vue_confirmer_import_stagiaires,
        name="confirmer_import_stagiaires",
    ),
    path(
        "sessions/<int:session_pk>/stagiaires/modele/",
        import_stagiaires.vue_telecharger_modele,
        name="modele_import_stagiaires",
    ),
]
