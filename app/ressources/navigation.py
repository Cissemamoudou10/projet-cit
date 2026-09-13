"""Onglets internes à la rubrique « Ressources » — Instructeurs, Lieux,
Indisponibilités des instructeurs et Calendrier partagent le même
`app_name` Django pour des permissions distinctes (US-INS-01, US-PLAN-02,
US-INS-03, US-PLAN-01). Voir docs/suivi/DECISIONS.md, D-57, D-115 et D-120
et suivants.

Pas d'onglet affiché si l'utilisateur n'a accès qu'à un seul domaine : rien
à choisir, la barre n'ajoute aucune information.
"""

from django.urls import reverse

from noyau.habilitations import a_permission
from ressources.services.indisponibilite_instructeur import ServiceIndisponibiliteInstructeur
from ressources.services.instructeur import ServiceInstructeur
from ressources.services.lieu import ServiceLieu
from ressources.services.periode_calendrier import ServicePeriodeCalendrier


def onglets_ressources(utilisateur, actif):
    onglets = []
    if a_permission(utilisateur, ServiceInstructeur.PERMISSION_LECTURE):
        onglets.append(
            {
                "slug": "instructeurs",
                "libelle": "Instructeurs",
                "url": reverse("ressources:liste_instructeurs"),
            }
        )
    if a_permission(utilisateur, ServiceLieu.PERMISSION_LECTURE):
        onglets.append(
            {
                "slug": "lieux",
                "libelle": "Lieux",
                "url": reverse("ressources:liste_lieux"),
            }
        )
    if a_permission(utilisateur, ServiceIndisponibiliteInstructeur.PERMISSION_LECTURE):
        onglets.append(
            {
                "slug": "indisponibilites-instructeurs",
                "libelle": "Indisponibilités",
                "url": reverse("ressources:liste_indisponibilites_instructeurs"),
            }
        )
    if a_permission(utilisateur, ServicePeriodeCalendrier.PERMISSION_LECTURE):
        onglets.append(
            {
                "slug": "calendrier",
                "libelle": "Calendrier",
                "url": reverse("ressources:calendrier_annuel"),
            }
        )
    if len(onglets) < 2:
        return [], None
    return onglets, actif
