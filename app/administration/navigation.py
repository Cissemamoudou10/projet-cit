"""Onglets de la rubrique « Administration » — Comptes et Habilitations
exigent `administration_ecriture`, le Journal se contente de
`administration_lecture` (consultation seule, RG-26/RG-27). Seul le groupe
Administrateur détient aujourd'hui les deux (§ 11.2 du dossier des cas
d'utilisation), mais le filtrage suit la permission réelle plutôt que le
groupe, comme `ressources.navigation`. Voir docs/suivi/DECISIONS.md, D-58.
"""

from django.urls import reverse

from administration.services.comptes import PERMISSION_GESTION_COMPTES
from administration.services.journal import PERMISSION_CONSULTATION_JOURNAL
from noyau.habilitations import a_permission


def onglets_administration(utilisateur, actif):
    onglets = []
    if a_permission(utilisateur, PERMISSION_GESTION_COMPTES):
        onglets.append(
            {
                "slug": "comptes",
                "libelle": "Comptes",
                "url": reverse("administration:liste_comptes"),
            }
        )
        onglets.append(
            {
                "slug": "habilitations",
                "libelle": "Habilitations",
                "url": reverse("administration:habilitations"),
            }
        )
    if a_permission(utilisateur, PERMISSION_CONSULTATION_JOURNAL):
        onglets.append(
            {
                "slug": "journal",
                "libelle": "Journal",
                "url": reverse("administration:journal"),
            }
        )
    if len(onglets) < 2:
        return [], None
    return onglets, actif
