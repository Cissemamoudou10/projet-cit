"""Contexte disponible dans tous les gabarits — voir docs/charte, § 2.4.

`rubrique_active` et `fil_ariane` retombent sur des listes/valeurs vides : la
navigation se remplira story par story, chaque vue pouvant surcharger ces
clés dans son propre contexte. `rubriques` porte désormais *Administration*
pour les utilisateurs habilités — la permission est une chaîne littérale,
pas un import de `administration` (`noyau` ne dépend d'aucune application) :
`has_perm` est une méthode native de tout modèle utilisateur Django.
"""

from django.conf import settings
from django.urls import reverse
from django.utils import timezone

PERMISSION_ADMINISTRATION = "administration.change_utilisateur"


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
    if not (request.user.is_authenticated and request.user.has_perm(PERMISSION_ADMINISTRATION)):
        return []
    return [
        {
            "slug": "administration",
            "libelle": "Administration",
            "url": reverse("administration:liste_comptes"),
        }
    ]
