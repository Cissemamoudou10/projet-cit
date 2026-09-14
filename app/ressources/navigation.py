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
from ressources.services.grille_horaire import ServiceGrilleHoraire
from ressources.services.indisponibilite_instructeur import ServiceIndisponibiliteInstructeur
from ressources.services.instructeur import ServiceInstructeur
from ressources.services.lieu import ServiceLieu
from ressources.services.periode_calendrier import ServicePeriodeCalendrier

_DOMAINES = [
    (ServiceInstructeur, "instructeurs", "Instructeurs", "ressources:liste_instructeurs"),
    (ServiceLieu, "lieux", "Lieux", "ressources:liste_lieux"),
    (
        ServiceIndisponibiliteInstructeur,
        "indisponibilites-instructeurs",
        "Indisponibilités",
        "ressources:liste_indisponibilites_instructeurs",
    ),
    (ServicePeriodeCalendrier, "calendrier", "Calendrier", "ressources:calendrier_annuel"),
    (
        ServiceGrilleHoraire,
        "grilles-horaires",
        "Grilles horaires",
        "ressources:liste_grilles_horaires",
    ),
]


def onglets_ressources(utilisateur, actif):
    onglets = [
        {"slug": slug, "libelle": libelle, "url": reverse(nom_url)}
        for service, slug, libelle, nom_url in _DOMAINES
        if a_permission(utilisateur, service.PERMISSION_LECTURE)
    ]
    if len(onglets) < 2:
        return [], None
    return onglets, actif
