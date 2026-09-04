"""Contexte disponible dans tous les gabarits — voir docs/charte, § 2.4.

`rubrique_active` se déduit de l'URL résolue (`request.resolver_match.
app_name`), jamais renseigné vue par vue : le nom d'application Django
d'une URL `referentiel:...`/`administration:...` vaut déjà « referentiel »/
« administration », identique aux `slug` de `_rubriques()`. Vingt vues
environ auraient dû, sinon, chacune surcharger la clé dans son propre
contexte — un oubli sur l'une d'elles cassait silencieusement le
surlignement, sans qu'aucun test ne le voie.

Exception : `ressources` porte deux rubriques de navigation distinctes
(Instructeurs et Lieux, US-INS-01 et US-PLAN-02) pour deux permissions
différentes, alors que `app_name` vaut « ressources » pour les deux. Départagé
par le préfixe du chemin (`/lieux/`) plutôt que par l'URL name, qui varierait
vue par vue.

`fil_ariane` retombe sur une liste vide : la navigation se remplira story
par story. `rubriques` porte désormais *Administration* pour les
utilisateurs habilités, filtrée par `a_permission` — silencieuse, aucune
tentative refusée à journaliser pour un simple masquage de menu
(Prompt 03, § 2.2).
"""

from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from noyau.habilitations import a_permission

PERMISSION_ADMINISTRATION = "noyau.administration_ecriture"
PERMISSION_REFERENTIEL = "noyau.referentiel_lecture"
PERMISSION_RESSOURCES = "noyau.instructeurs_qualifications_lecture"
PERMISSION_LIEUX = "noyau.lieux_calendrier_lecture"


def contexte_application(request):
    return {
        "application": {
            "nom": settings.APPLICATION_NOM,
            "version": settings.APPLICATION_VERSION,
        },
        "maintenant": timezone.now(),
        "rubriques": _rubriques(request),
        "rubrique_active": _rubrique_active(request),
        "fil_ariane": [],
    }


def _rubrique_active(request):
    correspondance = getattr(request, "resolver_match", None)
    if not correspondance:
        return None
    if correspondance.app_name == "ressources" and request.path.startswith("/lieux/"):
        return "lieux"
    return correspondance.app_name


def _rubriques(request):
    rubriques = []
    if a_permission(request.user, PERMISSION_ADMINISTRATION):
        rubriques.append(
            {
                "slug": "administration",
                "libelle": "Administration",
                "url": reverse("administration:liste_comptes"),
            }
        )
    if a_permission(request.user, PERMISSION_REFERENTIEL):
        rubriques.append(
            {
                "slug": "referentiel",
                "libelle": "Référentiel",
                "url": reverse("referentiel:liste_types_formation"),
            }
        )
    if a_permission(request.user, PERMISSION_RESSOURCES):
        rubriques.append(
            {
                "slug": "ressources",
                "libelle": "Ressources",
                "url": reverse("ressources:liste_instructeurs"),
            }
        )
    if a_permission(request.user, PERMISSION_LIEUX):
        rubriques.append(
            {
                "slug": "lieux",
                "libelle": "Lieux",
                "url": reverse("ressources:liste_lieux"),
            }
        )
    return rubriques
