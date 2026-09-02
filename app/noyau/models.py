"""Classe de base d'horodatage — BNF-14.

Aucune entité métier dans cette application : voir docs/conception/
15-dossier-architecture.md §3.3.
"""

from django.conf import settings
from django.db import models


class ModeleHorodate(models.Model):
    """Abstraite : n'engendre aucune table, aucune migration.

    L'auteur est renseigné par la couche services, jamais par un signal —
    voir noyau/services/base.py. Impérativement `settings.AUTH_USER_MODEL`,
    jamais un import direct de `administration.models.Utilisateur` : cet
    import inverserait le sens des couches, noyau ne dépendant de rien.
    """

    cree_le = models.DateTimeField(auto_now_add=True, verbose_name="créé le")
    modifie_le = models.DateTimeField(auto_now=True, verbose_name="modifié le")
    cree_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        related_name="+",
        verbose_name="créé par",
    )
    modifie_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        related_name="+",
        verbose_name="modifié par",
    )

    class Meta:
        abstract = True
