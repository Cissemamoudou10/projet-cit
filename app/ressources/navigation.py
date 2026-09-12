"""Onglets internes à la rubrique « Ressources » — Instructeurs, Lieux et
Indisponibilités des instructeurs partagent le même `app_name` Django pour
des permissions distinctes (US-INS-01, US-PLAN-02, US-INS-03). Voir
docs/suivi/DECISIONS.md, D-57 et D-115.

Pas d'onglet affiché si l'utilisateur n'a accès qu'à un seul domaine : rien
à choisir, la barre n'ajoute aucune information.
"""

from django.urls import reverse

from noyau.habilitations import a_permission
from ressources.services.indisponibilite_instructeur import ServiceIndisponibiliteInstructeur
from ressources.services.instructeur import ServiceInstructeur
from ressources.services.lieu import ServiceLieu


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
    if len(onglets) < 2:
        return [], None
    return onglets, actif
