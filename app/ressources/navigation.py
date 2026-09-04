"""Onglets internes à la rubrique « Ressources » — Instructeurs et Lieux
partagent le même `app_name` Django pour deux permissions distinctes
(US-INS-01, US-PLAN-02). Voir docs/suivi/DECISIONS.md, D-57.

Pas d'onglet affiché si l'utilisateur n'a accès qu'à un seul des deux
domaines : rien à choisir, la barre n'ajoute aucune information.
"""

from django.urls import reverse

from noyau.habilitations import a_permission
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
    if len(onglets) < 2:
        return [], None
    return onglets, actif
