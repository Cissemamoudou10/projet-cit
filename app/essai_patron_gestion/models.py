"""Application réservée aux tests du patron `ServiceGestion` — Prompt 05,
§ 7 : « un patron testé à travers un seul usage n'est pas un patron ».

Jamais dans `INSTALLED_APPS` hors de `config/settings/test.py` : ce n'est
pas une application métier, seulement un support de test pour
`noyau/services/gestion.py`.
"""

from django.db import models
from django.db.models.functions import Upper

from noyau.models import ModeleArchivable, ModeleHorodate


class ElementGestionTest(ModeleHorodate, ModeleArchivable):
    intitule = models.CharField(max_length=100)

    class Meta:
        app_label = "essai_patron_gestion"
        constraints = [
            models.UniqueConstraint(Upper("intitule"), name="uq_element_gestion_test_intitule"),
        ]

    def __str__(self):
        return self.intitule


class DependantGestionTest(models.Model):
    """Référence protégée — prouve E3 (suppression refusée, élément
    opposant énuméré) sans dépendre d'un modèle métier réel.
    """

    element = models.ForeignKey(
        ElementGestionTest, on_delete=models.PROTECT, related_name="dependants"
    )

    class Meta:
        app_label = "essai_patron_gestion"

    def __str__(self):
        return f"Dépendant de {self.element}"
