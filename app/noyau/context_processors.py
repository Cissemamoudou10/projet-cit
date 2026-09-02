"""Contexte disponible dans tous les gabarits — voir docs/charte, § 2.4.

`rubrique_active` et `fil_ariane` retombent sur des listes/valeurs vides : la
navigation se remplira story par story, chaque vue pouvant surcharger ces
clés dans son propre contexte. `rubriques` porte désormais *Administration*
pour les utilisateurs habilités, filtrée par `a_permission` — silencieuse,
aucune tentative refusée à journaliser pour un simple masquage de menu
(Prompt 03, § 2.2).
"""

from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from noyau.habilitations import a_permission

PERMISSION_ADMINISTRATION = "noyau.administration_ecriture"


def contexte_application(request):
    return {
        "application": {
            "nom": settings.APPLICATION_NOM,
            "version": settings.APPLICATION_VERSION,
        },
        "maintenant": timezone.now(),
        "rubriques": _rubriques(request),
        "rubrique_active": None,
        "fil_ariane": [],
    }


def _rubriques(request):
    if not a_permission(request.user, PERMISSION_ADMINISTRATION):
        return []
    return [
        {
            "slug": "administration",
            "libelle": "Administration",
            "url": reverse("administration:liste_comptes"),
        }
    ]
