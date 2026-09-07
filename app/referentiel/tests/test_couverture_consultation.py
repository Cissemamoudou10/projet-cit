"""Prompt 17, § 2.2 — le nombre d'instructeurs qualifiés apparaît par
matière dans la vue consolidée du référentiel (`formation_consultation.html`,
US-REF-07), pas seulement sur l'écran dédié de couverture
(`ressources:couverture_qualifications`, lié depuis l'écran de composition,
pas depuis celui-ci). La donnée existe déjà (`ServiceReferentiel.lister`
annote `nombre_instructeurs_qualifies`) : seul le gabarit manquait la
colonne.

Le cas « au moins un instructeur qualifié » vit dans `ressources/tests/` :
`referentiel` ne peut pas importer `ressources` (ordre des dépendances).
"""

from django.urls import reverse

from referentiel.services.referentiel import ServiceReferentiel
from referentiel.tests.conftest import donnees_element_referentiel as _donnees


def test_aucun_instructeur_qualifie_affiche_le_signalement(
    client, redacteur, direction_formation, formation, matiere
):
    ServiceReferentiel.rattacher(redacteur, formation, matiere, _donnees())
    client.force_login(direction_formation)

    reponse = client.get(reverse("referentiel:consultation_formation", args=[formation.pk]))

    assert "AUCUN" in reponse.content.decode()
