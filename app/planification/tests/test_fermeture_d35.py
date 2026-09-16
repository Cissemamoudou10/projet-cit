"""D-35 (RG-07, critère 6 US-REF-03) — volet SÉANCE refermé par cette story,
vérifié par un test qui exerce réellement `ServiceReferentiel.retirer`, pas
seulement le `on_delete=PROTECT` en base (leçon de D-50/D-51 : une fermeture
se prouve, elle ne se déclare pas). Vit ici, jamais côté `referentiel`, qui
ne peut pas construire de `Seance` (sens de dépendance interdit). Le volet
ÉVALUATION de D-35 reste ouvert, sprint 4. Données entièrement fictives.
"""

import pytest

from noyau.exceptions import ErreurValidation
from planification.models import ProgrammeHebdomadaire, Seance
from planification.tests.conftest import instant
from referentiel.services.referentiel import ServiceReferentiel


def test_retrait_d_un_element_de_referentiel_porteur_d_une_seance_refuse(
    redacteur, element_referentiel, instructeur, lundi_semaine
):
    programme = ProgrammeHebdomadaire.objects.create(lundi_de_semaine=lundi_semaine)
    seance = Seance.objects.create(
        programme=programme,
        element_referentiel=element_referentiel,
        instructeur=instructeur,
        debut=instant(lundi_semaine, 0, 8),
        fin=instant(lundi_semaine, 0, 9, 45),
    )

    with pytest.raises(ErreurValidation) as info:
        ServiceReferentiel.retirer(redacteur, element_referentiel)

    assert str(seance) in str(info.value) or str(element_referentiel) in str(info.value)
    assert type(element_referentiel).objects.filter(pk=element_referentiel.pk).exists()
