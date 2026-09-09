"""Contexte disponible dans tous les gabarits — voir docs/charte, § 2.4.

`rubrique_active` se déduit de l'URL résolue (`request.resolver_match.
app_name`), jamais renseigné vue par vue : le nom d'application Django
d'une URL `referentiel:...`/`administration:...` vaut déjà « referentiel »/
« administration », identique aux `slug` de `_rubriques()`. Vingt vues
environ auraient dû, sinon, chacune surcharger la clé dans son propre
contexte — un oubli sur l'une d'elles cassait silencieusement le
surlignement, sans qu'aucun test ne le voie.

`ressources` porte deux domaines (Instructeurs et Lieux, US-INS-01 et
US-PLAN-02) sous une seule rubrique — c'est la maquette de référence
(`docs/conception/16-maquettes.md`) qui fixe un menu à six entrées, sans
« Lieux » séparé. Le choix de l'onglet actif entre les deux, lui, est propre
aux vues de `ressources` (voir `ressources.navigation`) : il ne regarde pas
ce processeur de contexte, qui reste générique. Voir docs/suivi/DECISIONS.md,
D-57.

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
PERMISSION_ORGANISATION = "noyau.organisation_lecture"
PERMISSION_INSTRUCTEURS = "noyau.instructeurs_qualifications_lecture"
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
    return correspondance.app_name if correspondance else None


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
    if a_permission(request.user, PERMISSION_ORGANISATION):
        rubriques.append(
            {
                "slug": "organisation",
                "libelle": "Sessions",
                "url": reverse("organisation:liste_sessions"),
            }
        )
    a_instructeurs = a_permission(request.user, PERMISSION_INSTRUCTEURS)
    a_lieux = a_permission(request.user, PERMISSION_LIEUX)
    if a_instructeurs or a_lieux:
        url = "ressources:liste_instructeurs" if a_instructeurs else "ressources:liste_lieux"
        rubriques.append(
            {
                "slug": "ressources",
                "libelle": "Ressources",
                "url": reverse(url),
            }
        )
    return rubriques
