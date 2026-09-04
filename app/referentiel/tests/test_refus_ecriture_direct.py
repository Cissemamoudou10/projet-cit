"""US-REF-07, critère 3 — refus côté serveur de toute adresse d'écriture du
paquetage, pour les trois profils en lecture seule, appel direct compris.
Le masquage du balisage est testé dans test_masquage_ecriture.py ; ici on
vérifie uniquement la réponse serveur et la journalisation (§ 2.2 : un refus
journalise une fois, un affichage masqué ne journalise rien).
"""

import pytest
from django.urls import reverse

from administration.models import EntreeJournal, TypeAction
from referentiel.models import ElementReferentiel
from referentiel.services.objectif_pedagogique import ServiceObjectifPedagogique
from referentiel.services.prerequis import ServicePrerequis
from referentiel.tests.conftest import creer_element, donnees_element_referentiel

PROFILS_LECTURE_SEULE = [
    pytest.param("lecteur", id="examens"),
    pytest.param("planificateur", id="planification"),
    pytest.param("direction_formation", id="direction_formation"),
]


@pytest.fixture
def contexte_ecriture(redacteur, formation, matiere, type_officiers):
    """Deux éléments de référentiel, un objectif, un lien de prérequis —
    tout ce dont les 23 adresses d'écriture du paquetage ont besoin comme
    ressource cible, créé par un profil habilité pour ne tester que le refus.
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


def _adresses_ecriture(ctx):
    formation = ctx["formation"]
    matiere = ctx["matiere"]
    type_formation = ctx["type_formation"]
    element = ctx["element"]
    objectif = ctx["objectif"]
    prerequis = ctx["prerequis"]
    return [
        ("referentiel:creer_type_formation", []),
        ("referentiel:modifier_type_formation", [type_formation.pk]),
        ("referentiel:archiver_type_formation", [type_formation.pk]),
        ("referentiel:desarchiver_type_formation", [type_formation.pk]),
        ("referentiel:creer_formation", []),
        ("referentiel:modifier_formation", [formation.pk]),
        ("referentiel:archiver_formation", [formation.pk]),
        ("referentiel:desarchiver_formation", [formation.pk]),
        ("referentiel:creer_matiere", []),
        ("referentiel:modifier_matiere", [matiere.pk]),
        ("referentiel:archiver_matiere", [matiere.pk]),
        ("referentiel:desarchiver_matiere", [matiere.pk]),
        ("referentiel:rattacher_matiere", [formation.pk]),
        ("referentiel:creer_matiere_depuis_referentiel", [formation.pk]),
        ("referentiel:modifier_element_referentiel", [formation.pk, element.pk]),
        ("referentiel:retirer_element_referentiel", [formation.pk, element.pk]),
        ("referentiel:ajouter_objectif_pedagogique", [matiere.pk]),
        ("referentiel:modifier_objectif_pedagogique", [matiere.pk, objectif.pk]),
        ("referentiel:monter_objectif_pedagogique", [matiere.pk, objectif.pk]),
        ("referentiel:descendre_objectif_pedagogique", [matiere.pk, objectif.pk]),
        ("referentiel:supprimer_objectif_pedagogique", [matiere.pk, objectif.pk]),
        ("referentiel:ajouter_prerequis", [formation.pk, element.pk]),
        ("referentiel:supprimer_prerequis", [formation.pk, prerequis.pk]),
    ]


@pytest.mark.parametrize("profil", PROFILS_LECTURE_SEULE)
def test_appel_direct_en_ecriture_refuse_pour_chaque_adresse(
    client, request, profil, contexte_ecriture
):
    utilisateur = request.getfixturevalue(profil)
    client.force_login(utilisateur)

    for nom_url, args in _adresses_ecriture(contexte_ecriture):
        reponse = client.post(reverse(nom_url, args=args))
        assert reponse.status_code == 403, f"{nom_url} aurait dû être refusée à {profil}"


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
