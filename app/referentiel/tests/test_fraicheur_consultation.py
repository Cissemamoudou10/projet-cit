"""US-REF-07, critère 4 — toute modification du référentiel par la cellule
pédagogique est immédiatement visible par les autres cellules. Satisfait par
construction dès lors que la consultation lit la base (Prompt 11, § 2.2) :
ce test échouerait si un cache, une vue matérialisée ou une copie de travail
s'interposait.
"""

from django.urls import reverse

from referentiel.services.referentiel import ServiceReferentiel
from referentiel.tests.conftest import donnees_element_referentiel as _donnees


def test_une_modification_pedagogique_est_immediatement_visible_en_planification(
    client, redacteur, planificateur, formation, matiere
):
    element = ServiceReferentiel.rattacher(
        redacteur, formation, matiere, _donnees(volume_horaire_prescrit=40)
    )
    client.force_login(planificateur)
    url = reverse("referentiel:referentiel_formation", args=[formation.pk])

    avant = client.get(url).content.decode()
    assert "40 h" in avant

    ServiceReferentiel.modifier_volume(redacteur, element, _donnees(volume_horaire_prescrit=55))

    apres = client.get(url).content.decode()
    assert "55 h" in apres
    assert "40 h" not in apres


def test_la_fraicheur_vaut_aussi_pour_l_ecran_consolide(
    client, redacteur, direction_formation, formation, matiere
):
    element = ServiceReferentiel.rattacher(
        redacteur, formation, matiere, _donnees(volume_horaire_prescrit=40)
    )
    client.force_login(direction_formation)
    url = reverse("referentiel:consultation_formation", args=[formation.pk])

    assert "40 h" in client.get(url).content.decode()

    ServiceReferentiel.modifier_volume(redacteur, element, _donnees(volume_horaire_prescrit=55))

    apres = client.get(url).content.decode()
    assert "55 h" in apres
    assert "40 h" not in apres
