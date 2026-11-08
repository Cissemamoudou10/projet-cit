"""Onglets internes à la rubrique « Suivi » — Tableau de bord, Alertes et
Rapprochement (US-SUI-01 à US-SUI-03, prompt 61 ter, ergonomie RECETTE-04).

Avant cette correction, chaque écran ne menait qu'au suivant d'un lien de
circonstance (le tableau de bord vers les alertes, les alertes vers le
tableau de bord et — par brigade seulement — vers le rapprochement) : aucun
accès direct au rapprochement complet depuis le tableau de bord, ni retour
direct au tableau de bord depuis le rapprochement. Même patron que
`ressources.navigation.onglets_ressources` (D-57, D-115) : pas d'onglet
affiché si l'utilisateur n'a accès qu'à un seul domaine.
"""

from django.urls import reverse

from noyau.habilitations import a_permission
from planification.services.suivi import PERMISSION_LECTURE

_ECRANS = [
    ("tableau-bord", "Tableau de bord", "planification:tableau_bord"),
    ("alertes", "Alertes", "planification:alertes_ecart"),
    ("rapprochement", "Rapprochement", "planification:rapprochement"),
]


def onglets_suivi(utilisateur, actif):
    if not a_permission(utilisateur, PERMISSION_LECTURE):
        return [], None
    onglets = [
        {"slug": slug, "libelle": libelle, "url": reverse(nom_url)}
        for slug, libelle, nom_url in _ECRANS
    ]
    if len(onglets) < 2:
        return [], None
    return onglets, actif
