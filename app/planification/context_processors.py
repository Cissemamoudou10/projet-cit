"""Compteur de la page d'attente de validation, dans la navigation (US-VAL-01 c.3).

Placé ici et non dans `noyau` : `noyau` ne peut pas importer une application.
Une requête par page, et seulement pour les profils qui voient la page d'attente.
"""

from django.urls import reverse

from noyau.habilitations import a_permission
from planification.selectors_circuit import compte_en_attente

# Écriture, et non lecture : la planification lit ce domaine (§ 11.2) mais ne
# valide pas ; le compteur est celui de la cellule pédagogique (US-VAL-01 c.3).
PERMISSION_PEDAGOGIQUE = "noyau.programme_validation_ecriture"


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
