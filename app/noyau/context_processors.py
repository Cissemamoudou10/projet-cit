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
PERMISSION_PLANIFICATION = "noyau.programme_lecture"
PERMISSION_EVALUATIONS = "noyau.evaluations_lecture"
PERMISSION_SUIVI = "noyau.suivi_lecture"


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


RUBRIQUES_SIMPLES = [
    ("administration", "Administration", PERMISSION_ADMINISTRATION, "administration:liste_comptes"),
    ("referentiel", "Référentiel", PERMISSION_REFERENTIEL, "referentiel:liste_types_formation"),
    ("organisation", "Sessions", PERMISSION_ORGANISATION, "organisation:liste_sessions"),
    ("planification", "Planification", PERMISSION_PLANIFICATION, "planification:consultation_programme"),
    # Deux dernières rubriques du menu de référence (docs/conception/
    # 16-maquettes.md, MAQ-01 à MAQ-05 : « … | Planification | Évaluations
    # | Suivi »). Ni l'une ni l'autre n'avait de rubrique propre : le
    # domaine Évaluations n'était lié depuis AUCUN écran du site (aucune
    # entrée, même pas la fiche session) ; le tableau de bord de Suivi
    # n'était atteint que par la cellule pédagogique, via le badge
    # « Alertes » (suivi_ecriture, pas suivi_lecture).
    ("evaluations", "Évaluations", PERMISSION_EVALUATIONS, "evaluations:liste_evaluations"),
    ("suivi", "Suivi", PERMISSION_SUIVI, "planification:tableau_bord"),
]


def _rubrique_si_habilite(request, slug, libelle, permission, url_nom):
    if not a_permission(request.user, permission):
        return None
    return {"slug": slug, "libelle": libelle, "url": reverse(url_nom)}


def _rubrique_ressources(request):
    a_instructeurs = a_permission(request.user, PERMISSION_INSTRUCTEURS)
    a_lieux = a_permission(request.user, PERMISSION_LIEUX)
    if not (a_instructeurs or a_lieux):
        return None
    url = "ressources:liste_instructeurs" if a_instructeurs else "ressources:liste_lieux"
    return {"slug": "ressources", "libelle": "Ressources", "url": reverse(url)}


def _rubriques(request):
    rubriques = [
        _rubrique_si_habilite(request, slug, libelle, permission, url_nom)
        for slug, libelle, permission, url_nom in RUBRIQUES_SIMPLES
    ]
    # "Ressources" n'est pas dans RUBRIQUES_SIMPLES (double permission) —
    # réinséré ici entre Sessions et Planification, l'ordre du menu (D-57).
    rubriques.insert(3, _rubrique_ressources(request))
    return [rubrique for rubrique in rubriques if rubrique]
