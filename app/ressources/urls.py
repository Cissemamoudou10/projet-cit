from django.urls import path

from ressources.views import (
    calendrier_lecture,
    grille_horaire,
    indisponibilite_instructeur,
    indisponibilite_lieu,
    instructeur,
    lieu,
    nature_evenement,
    periode_calendrier,
    qualification,
    salle_attitree,
)

app_name = "ressources"

urlpatterns = [
    path(
        "brigades/<int:brigade_pk>/salle/",
        salle_attitree.vue_affecter_salle,
        name="affecter_salle",
    ),
    path(
        "brigades/<int:brigade_pk>/salle/soumettre/",
        salle_attitree.vue_soumettre_salle,
        name="soumettre_salle",
    ),
    path(
        "brigades/<int:brigade_pk>/salle/retirer/",
        salle_attitree.vue_retirer_salle,
        name="retirer_salle",
    ),
    path("lieux/", lieu.vue_liste_lieux, name="liste_lieux"),
    path("lieux/creer/", lieu.vue_creer_lieu, name="creer_lieu"),
    path("lieux/<int:pk>/", lieu.vue_detail_lieu, name="detail_lieu"),
    path("lieux/<int:pk>/modifier/", lieu.vue_modifier_lieu, name="modifier_lieu"),
    path("lieux/<int:pk>/archiver/", lieu.vue_confirmer_archivage_lieu, name="archiver_lieu"),
    path("lieux/<int:pk>/desarchiver/", lieu.vue_desarchiver_lieu, name="desarchiver_lieu"),
    path("lieux/<int:pk>/supprimer/", lieu.vue_confirmer_suppression_lieu, name="supprimer_lieu"),
    path(
        "lieux/<int:lieu_pk>/indisponibilites/declarer/",
        indisponibilite_lieu.vue_declarer_indisponibilite,
        name="declarer_indisponibilite_lieu",
    ),
    path(
        "indisponibilites/<int:pk>/modifier/",
        indisponibilite_lieu.vue_modifier_indisponibilite,
        name="modifier_indisponibilite_lieu",
    ),
    path(
        "indisponibilites/<int:pk>/supprimer/",
        indisponibilite_lieu.vue_confirmer_suppression_indisponibilite,
        name="supprimer_indisponibilite_lieu",
    ),
    path(
        "indisponibilites-instructeurs/",
        indisponibilite_instructeur.vue_liste_indisponibilites_instructeurs,
        name="liste_indisponibilites_instructeurs",
    ),
    path(
        "indisponibilites-instructeurs/declarer/",
        indisponibilite_instructeur.vue_declarer_indisponibilite_instructeur,
        name="declarer_indisponibilite_instructeur",
    ),
    path(
        "indisponibilites-instructeurs/confirmer-fusion/",
        indisponibilite_instructeur.vue_confirmer_fusion_indisponibilite,
        name="confirmer_fusion_indisponibilite",
    ),
    path(
        "indisponibilites-instructeurs/<int:pk>/modifier/",
        indisponibilite_instructeur.vue_modifier_indisponibilite_instructeur,
        name="modifier_indisponibilite_instructeur",
    ),
    path(
        "indisponibilites-instructeurs/<int:pk>/supprimer/",
        indisponibilite_instructeur.vue_confirmer_suppression_indisponibilite_instructeur,
        name="supprimer_indisponibilite_instructeur",
    ),
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
    path(
        "instructeurs/<int:pk>/qualifications/",
        qualification.vue_qualifications_instructeur,
        name="qualifications_instructeur",
    ),
    path(
        "instructeurs/<int:instructeur_pk>/qualifications/<int:matiere_pk>/ajouter/",
        qualification.vue_ajouter_qualification,
        {"origine": "instructeur"},
        name="ajouter_qualification_instructeur",
    ),
    path(
        "qualifications/matieres/<int:pk>/",
        qualification.vue_qualifications_matiere,
        name="qualifications_matiere",
    ),
    path(
        "qualifications/matieres/<int:matiere_pk>/instructeurs/<int:instructeur_pk>/ajouter/",
        qualification.vue_ajouter_qualification,
        {"origine": "matiere"},
        name="ajouter_qualification_matiere",
    ),
    path(
        "qualifications/<int:pk>/retirer/depuis-instructeur/",
        qualification.vue_confirmer_retrait_qualification,
        {"origine": "instructeur"},
        name="retirer_qualification_instructeur",
    ),
    path(
        "qualifications/<int:pk>/retirer/depuis-matiere/",
        qualification.vue_confirmer_retrait_qualification,
        {"origine": "matiere"},
        name="retirer_qualification_matiere",
    ),
    path(
        "qualifications/formations/<int:formation_pk>/couverture/",
        qualification.vue_couverture_qualifications,
        name="couverture_qualifications",
    ),
    path("calendrier/", calendrier_lecture.vue_calendrier_annuel, name="calendrier_annuel"),
    path("calendrier/mois/", calendrier_lecture.vue_calendrier_mensuel, name="calendrier_mensuel"),
    path(
        "calendrier/declarer/",
        periode_calendrier.vue_declarer_periode_calendrier,
        name="declarer_periode_calendrier",
    ),
    path(
        "calendrier/<int:pk>/",
        periode_calendrier.vue_detail_periode_calendrier,
        name="detail_periode_calendrier",
    ),
    path(
        "calendrier/<int:pk>/modifier/",
        periode_calendrier.vue_modifier_periode_calendrier,
        name="modifier_periode_calendrier",
    ),
    path(
        "calendrier/<int:pk>/supprimer/",
        periode_calendrier.vue_confirmer_suppression_periode_calendrier,
        name="supprimer_periode_calendrier",
    ),
    path(
        "natures-evenement/",
        nature_evenement.vue_liste_natures_evenement,
        name="liste_natures_evenement",
    ),
    path(
        "natures-evenement/creer/",
        nature_evenement.vue_creer_nature_evenement,
        name="creer_nature_evenement",
    ),
    path(
        "natures-evenement/<int:pk>/modifier/",
        nature_evenement.vue_modifier_nature_evenement,
        name="modifier_nature_evenement",
    ),
    path(
        "natures-evenement/<int:pk>/supprimer/",
        nature_evenement.vue_confirmer_suppression_nature_evenement,
        name="supprimer_nature_evenement",
    ),
    path(
        "grilles-horaires/",
        grille_horaire.vue_liste_grilles_horaires,
        name="liste_grilles_horaires",
    ),
    path(
        "grilles-horaires/creer/",
        grille_horaire.vue_creer_grille_horaire,
        name="creer_grille_horaire",
    ),
    path(
        "grilles-horaires/<int:pk>/",
        grille_horaire.vue_detail_grille_horaire,
        name="detail_grille_horaire",
    ),
    path(
        "grilles-horaires/<int:pk>/modifier/",
        grille_horaire.vue_modifier_grille_horaire,
        name="modifier_grille_horaire",
    ),
    path(
        "grilles-horaires/<int:pk>/dupliquer/",
        grille_horaire.vue_dupliquer_grille_horaire,
        name="dupliquer_grille_horaire",
    ),
    path(
        "grilles-horaires/<int:pk>/archiver/",
        grille_horaire.vue_confirmer_archivage_grille_horaire,
        name="archiver_grille_horaire",
    ),
    path(
        "grilles-horaires/<int:pk>/desarchiver/",
        grille_horaire.vue_desarchiver_grille_horaire,
        name="desarchiver_grille_horaire",
    ),
    path(
        "grilles-horaires/<int:pk>/supprimer/",
        grille_horaire.vue_confirmer_suppression_grille_horaire,
        name="supprimer_grille_horaire",
    ),
    path(
        "grilles-horaires/<int:pk>/activer/",
        grille_horaire.vue_confirmer_activation_grille_horaire,
        name="confirmer_activation_grille_horaire",
    ),
    path(
        "grilles-horaires/<int:grille_pk>/creneaux/ajouter/",
        grille_horaire.vue_ajouter_creneau,
        name="ajouter_creneau",
    ),
    path(
        "creneaux/<int:pk>/supprimer/",
        grille_horaire.vue_confirmer_suppression_creneau,
        name="supprimer_creneau",
    ),
]
