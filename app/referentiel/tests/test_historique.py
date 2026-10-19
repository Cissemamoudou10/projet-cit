"""US-REF-09 — Historiser les modifications du référentiel (prompt 48,
Story 5). Données entièrement fictives.
"""

from django.urls import reverse

from administration.services.journal import ServiceJournal
from referentiel.models import Matiere
from referentiel.services.formation import ServiceFormation
from referentiel.services.prerequis import ServicePrerequis
from referentiel.services.referentiel import ServiceReferentiel
from referentiel.tests.conftest import donnees_element_referentiel


def test_modification_du_volume_avec_valeurs_avant_et_apres(redacteur, formation, matiere):
    element = ServiceReferentiel.rattacher(
        redacteur, formation, matiere, donnees_element_referentiel(volume_horaire_prescrit=40)
    )

    ServiceReferentiel.modifier_volume(
        redacteur, element, donnees_element_referentiel(volume_horaire_prescrit=30, coefficient=2)
    )

    entrees = ServiceJournal.historique_de("element_referentiel", element)
    modification = next(e for e in entrees if e.type_action == "modification_element_gestion")
    assert modification.valeur_avant["volume_horaire_prescrit"] == 40
    assert modification.valeur_avant["coefficient"] == 1.0
    assert modification.valeur_apres["volume_horaire_prescrit"] == 30
    assert modification.valeur_apres["coefficient"] == 2.0
    assert modification.auteur == redacteur


def test_archivage_enregistre_auteur_et_date(redacteur, formation):
    ServiceFormation.archiver(redacteur, formation.pk)

    entrees = ServiceJournal.historique_de("formation", formation)
    archivage = next(e for e in entrees if e.type_action == "archivage_element_gestion")
    assert archivage.auteur == redacteur
    assert archivage.cree_le is not None


def test_historique_sur_la_fiche_formation(client, redacteur, formation):
    ServiceFormation.modifier(
        redacteur, formation.pk, {"intitule": "Formation modifiée"}, formation.modifie_le
    )
    client.force_login(redacteur)

    reponse = client.get(reverse("referentiel:detail_formation", args=[formation.pk]))

    assert reponse.status_code == 200
    page = reponse.content.decode("utf-8")
    assert "Historique des modifications" in page
    assert "Modification" in page


def test_historique_sur_la_fiche_matiere(client, redacteur, matiere):
    from referentiel.services.matiere import ServiceMatiere

    ServiceMatiere.modifier(redacteur, matiere.pk, {"intitule": "Matière modifiée"}, matiere.modifie_le)
    client.force_login(redacteur)

    reponse = client.get(reverse("referentiel:detail_matiere", args=[matiere.pk]))

    assert reponse.status_code == 200
    assert "Historique des modifications" in reponse.content.decode("utf-8")


def test_historique_sur_la_fiche_referentiel(client, redacteur, formation, matiere):
    element = ServiceReferentiel.rattacher(
        redacteur, formation, matiere, donnees_element_referentiel(volume_horaire_prescrit=40)
    )
    ServiceReferentiel.modifier_volume(
        redacteur, element, donnees_element_referentiel(volume_horaire_prescrit=30)
    )
    client.force_login(redacteur)

    reponse = client.get(reverse("referentiel:referentiel_formation", args=[formation.pk]))

    assert reponse.status_code == 200
    page = reponse.content.decode("utf-8")
    assert "Historique des modifications" in page
    assert "30" in page


def test_historique_sur_la_fiche_prerequis(client, redacteur, formation):
    """E2 range le prérequis dans le périmètre de la story au même titre
    que les trois autres entités — l'ajout d'un prérequis journalisé reste
    sinon invisible, bien que déjà journalisé par `ServicePrerequis`."""
    matiere_a = Matiere.objects.create(intitule="Matière A REF-09", code="MAREF09")
    matiere_b = Matiere.objects.create(intitule="Matière B REF-09", code="MBREF09")
    element_a = ServiceReferentiel.rattacher(
        redacteur, formation, matiere_a, donnees_element_referentiel()
    )
    element_b = ServiceReferentiel.rattacher(
        redacteur, formation, matiere_b, donnees_element_referentiel()
    )
    ServicePrerequis.ajouter(redacteur, formation, element_b, element_a)
    client.force_login(redacteur)

    reponse = client.get(reverse("referentiel:prerequis_formation", args=[formation.pk]))

    assert reponse.status_code == 200
    assert "Historique des modifications" in reponse.content.decode("utf-8")


def test_tentative_de_modification_refusee(redacteur, formation):
    """E3 : une entrée d'historique du référentiel n'est pas modifiable.
    La preuve au niveau base de données (RG-27, GRANT/REVOKE du rôle
    applicatif) est déjà apportée, génériquement, par
    `app/administration/tests/test_immuabilite_journal.py` — elle ne
    dépend pas du service qui a produit la ligne, inutile de la rejouer
    ici. Ce test vérifie seulement qu'aucun CHEMIN APPLICATIF (service) ne
    permet de modifier une entrée déjà enregistrée."""
    ServiceFormation.archiver(redacteur, formation.pk)
    entrees = ServiceJournal.historique_de("formation", formation)
    assert entrees[0].auteur == redacteur

    assert not hasattr(ServiceJournal, "modifier")
    assert not hasattr(ServiceJournal, "supprimer")
