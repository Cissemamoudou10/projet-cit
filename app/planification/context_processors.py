"""Compteurs de la navigation — attente de validation (US-VAL-01 c.3) et
alertes d'écart significatif (US-SUI-02, A3, prompt 48).

Placé ici et non dans `noyau` : `noyau` ne peut pas importer une application.
Une requête par page, et seulement pour les profils qui voient l'écran visé.
"""

from django.urls import reverse

from noyau.habilitations import a_permission
from planification.selectors_alerte_ecart import compte_alertes
from planification.selectors_circuit import compte_en_attente

# Écriture, et non lecture : la planification lit ce domaine (§ 11.2) mais ne
# valide pas ; le compteur est celui de la cellule pédagogique (US-VAL-01 c.3).
PERMISSION_PEDAGOGIQUE = "noyau.programme_validation_ecriture"

# A3 : « comme le compteur des programmes en attente » — même critère, une
# permission d'écriture exclusive à la cellule pédagogique dans `MATRICE`,
# utilisée ici comme marqueur de profil, pas pour un contrôle d'écriture.
PERMISSION_SUIVI_ECRITURE = "noyau.suivi_ecriture"


def validation_en_attente(request):
    utilisateur = getattr(request, "user", None)
    if utilisateur is None or not utilisateur.is_authenticated:
        return {}
    if not a_permission(utilisateur, PERMISSION_PEDAGOGIQUE):
        return {}
    return {
        "validation_en_attente": {
            "compte": compte_en_attente(),
            "url": reverse("planification:attente_validation"),
        }
    }


def alertes_en_attente(request):
    utilisateur = getattr(request, "user", None)
    if utilisateur is None or not utilisateur.is_authenticated:
        return {}
    if not a_permission(utilisateur, PERMISSION_SUIVI_ECRITURE):
        return {}
    return {
        "alertes_en_attente": {
            "compte": compte_alertes(),
            "url": reverse("planification:alertes_ecart"),
        }
    }
