"""US-REF-07, critère 3 — journalisation du refus et non-divulgation d'un
identifiant inexistant. Le refus HTTP lui-même, pour toute adresse
d'écriture du système (pas seulement de ce paquetage), est couvert une
fois pour toutes par tests/architecture/test_ecrans_ecriture.py (bloc D.2
du Prompt 19) — l'ancienne liste locale de 23 adresses, propre à ce
fichier, y a été reprise et étendue à administration et ressources. Le
masquage du balisage est testé dans test_masquage_ecriture.py.
"""

import pytest
from django.urls import reverse

from administration.models import EntreeJournal, TypeAction
from referentiel.models import ElementReferentiel
from referentiel.services.objectif_pedagogique import ServiceObjectifPedagogique
from referentiel.services.prerequis import ServicePrerequis
from referentiel.tests.conftest import creer_element, donnees_element_referentiel


@pytest.fixture
def contexte_ecriture(redacteur, formation, matiere, type_officiers):
    """Un élément de référentiel, un objectif, un lien de prérequis — les
    ressources cibles des trois tests ci-dessous (journalisation, masquage,
    non-divulgation), créées par un profil habilité pour ne tester que le
    refus des tests qui suivent.
    """
    element = ElementReferentiel.objects.create(
        formation=formation, matiere=matiere, **donnees_element_referentiel()
    )
    autre_element = creer_element(formation, "Radiocommunications", "RAD01")
    objectif = ServiceObjectifPedagogique.ajouter(redacteur, matiere, "Analyser un schéma")
    prerequis = ServicePrerequis.ajouter(redacteur, formation, element, autre_element)
    return {
        "formation": formation,
        "matiere": matiere,
        "type_formation": type_officiers,
        "element": element,
        "autre_element": autre_element,
        "objectif": objectif,
        "prerequis": prerequis,
    }


def test_le_refus_est_journalise_une_fois_par_tentative(client, lecteur, contexte_ecriture):
    client.force_login(lecteur)
    formation = contexte_ecriture["formation"]

    client.post(reverse("referentiel:archiver_formation", args=[formation.pk]))

    assert EntreeJournal.objects.filter(type_action=TypeAction.ACCES_REFUSE).count() == 1


def test_l_affichage_d_un_ecran_masque_ne_journalise_rien(client, lecteur, contexte_ecriture):
    formation = contexte_ecriture["formation"]
    client.force_login(lecteur)

    for _ in range(3):
        client.get(reverse("referentiel:detail_formation", args=[formation.pk]))
        client.get(reverse("referentiel:referentiel_formation", args=[formation.pk]))
        client.get(reverse("referentiel:consultation_formation", args=[formation.pk]))

    assert not EntreeJournal.objects.filter(type_action=TypeAction.ACCES_REFUSE).exists()


def test_le_refus_ne_divulgue_pas_l_existence_de_l_element(client, lecteur, formation):
    """E4 de la fiche générique : l'identifiant inexistant (999999) reçoit le
    même refus 403 qu'un identifiant existant — jamais un 404 qui trahirait
    l'absence, ni un comportement distinct qui trahirait la présence."""
    client.force_login(lecteur)

    reponse_existant = client.post(reverse("referentiel:archiver_formation", args=[formation.pk]))
    reponse_inexistant = client.post(reverse("referentiel:archiver_formation", args=[999999]))

    assert reponse_existant.status_code == reponse_inexistant.status_code == 403
