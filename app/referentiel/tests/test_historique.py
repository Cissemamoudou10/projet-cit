"""US-REF-09 — Historiser les modifications du référentiel (prompt 48,
Story 5 ; prompt 49, Temps 1 — révise D-285, identité technique stable
dans le journal). Données entièrement fictives.
"""

from django.urls import reverse

from administration.models import EntreeJournal
from administration.services.journal import ServiceJournal
from referentiel.models import Matiere
from referentiel.services.formation import ServiceFormation
from referentiel.services.matiere import ServiceMatiere
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


def test_renommage_formation_garde_l_historique_sous_les_deux_intitules(redacteur, type_officiers):
    """Prompt 49, Temps 1, point 3 : l'historique filtre désormais sur
    l'identité technique (`objet_cle`), pas sur l'intitulé — la création,
    journalisée sous l'ANCIEN intitulé, reste retrouvée après renommage."""
    formation = ServiceFormation.creer(
        redacteur,
        {
            "intitule": "Formation avant renommage REF09",
            "specialite": "Transmissions",
            "duree_semaines": 10,
            "type_formation": type_officiers,
        },
    )
    ServiceFormation.modifier(
        redacteur, formation.pk, {"intitule": "Formation après renommage REF09"}, formation.modifie_le
    )
    formation.refresh_from_db()

    entrees = ServiceJournal.historique_de("formation", formation)

    assert len(entrees) == 2
    assert any(e.type_action == "creation_element_gestion" for e in entrees)
    modification = next(e for e in entrees if e.type_action == "modification_element_gestion")
    assert modification.valeur_avant["intitule"] == "Formation avant renommage REF09"
    assert modification.valeur_apres["intitule"] == "Formation après renommage REF09"


def test_renommage_matiere_garde_l_historique_sous_les_deux_intitules(redacteur):
    matiere = ServiceMatiere.creer(
        redacteur, {"intitule": "Matière avant renommage REF09", "code": "MAV09"}
    )
    ServiceMatiere.modifier(
        redacteur, matiere.pk, {"intitule": "Matière après renommage REF09"}, matiere.modifie_le
    )
    matiere.refresh_from_db()

    entrees = ServiceJournal.historique_de("matiere", matiere)

    assert len(entrees) == 2
    modification = next(e for e in entrees if e.type_action == "modification_element_gestion")
    assert modification.valeur_avant["intitule"] == "Matière avant renommage REF09"
    assert modification.valeur_apres["intitule"] == "Matière après renommage REF09"


def test_suppression_journalise_la_bonne_cle_technique(redacteur, type_officiers):
    """Relecture du prompt 49, Temps 1 : `ServiceGestion.supprimer`
    journalisait après `instance.delete()`, qui vide `instance.pk` —
    `objet_cle` valait la chaîne littérale « None », jamais la clé
    primaire réelle, dans un journal pourtant immuable (RG-27)."""
    formation = ServiceFormation.creer(
        redacteur,
        {
            "intitule": "Formation à supprimer REF09",
            "specialite": "Transmissions",
            "duree_semaines": 10,
            "type_formation": type_officiers,
        },
    )
    pk_attendu = str(formation.pk)

    ServiceFormation.supprimer(redacteur, formation.pk)

    entree = EntreeJournal.objects.filter(
        objet_type="formation", type_action="suppression_element_gestion"
    ).latest("cree_le")
    assert entree.objet_cle == pk_attendu


def test_entree_anterieure_sans_cle_technique_reste_affichee(formation):
    """Point 2 : les entrées déjà enregistrées avant cette révision (sans
    `objet_cle`) restent affichées — repli sur `objet_identifiant`, tant
    que l'objet n'a pas été renommé depuis (D-286, aucune reprise
    rétroactive)."""
    EntreeJournal.objects.create(
        type_action="creation_element_gestion",
        identifiant_saisi=str(formation),
        objet_type="formation",
        objet_identifiant=str(formation),
        objet_cle="",
    )

    entrees = ServiceJournal.historique_de("formation", formation)

    assert len(entrees) == 1


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
