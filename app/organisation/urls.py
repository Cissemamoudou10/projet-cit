from django.urls import path

from organisation.views import session

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
]
