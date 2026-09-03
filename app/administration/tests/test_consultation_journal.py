"""Écran de consultation — CU-P1-03, Prompt 04 § 6, § 2.4."""

from datetime import timedelta

import pytest
from django.urls import reverse
from django.utils import timezone

from administration.models import EntreeJournal, TypeAction
from administration.services.journal import ServiceJournal
from noyau.exceptions import ErreurHabilitation


def test_un_non_administrateur_est_refuse(client, non_administrateur):
    client.force_login(non_administrateur)

    reponse = client.get(reverse("administration:journal"))

    assert reponse.status_code == 403


def test_une_consultation_produit_une_seule_entree(administrateur):
    ServiceJournal.consulter(administrateur, {}, None)

    assert EntreeJournal.objects.filter(type_action=TypeAction.CONSULTATION_JOURNAL).count() == 1


def test_vingt_entrees_affichees_ne_produisent_pas_vingt_et_une_entrees(administrateur):
    for i in range(20):
        EntreeJournal.objects.create(
            type_action=TypeAction.ECHEC_AUTHENTIFICATION, identifiant_saisi=f"essai-{i}"
        )

    ServiceJournal.consulter(administrateur, {}, None)

    assert EntreeJournal.objects.filter(type_action=TypeAction.CONSULTATION_JOURNAL).count() == 1


def test_le_filtre_nature_restreint_le_resultat(administrateur):
    EntreeJournal.objects.create(
        type_action=TypeAction.ECHEC_AUTHENTIFICATION, identifiant_saisi="a"
    )
    EntreeJournal.objects.create(
        type_action=TypeAction.MODIFICATION_HABILITATIONS, identifiant_saisi="b"
    )

    page = ServiceJournal.consulter(
        administrateur, {"nature": TypeAction.ECHEC_AUTHENTIFICATION}, None
    )

    assert all(entree.type_action == TypeAction.ECHEC_AUTHENTIFICATION for entree in page)


def test_le_filtre_auteur_restreint_le_resultat(administrateur, non_administrateur):
    EntreeJournal.objects.create(
        type_action=TypeAction.MODIFICATION_HABILITATIONS,
        identifiant_saisi="a",
        auteur=administrateur,
    )
    EntreeJournal.objects.create(
        type_action=TypeAction.MODIFICATION_HABILITATIONS,
        identifiant_saisi="b",
        auteur=non_administrateur,
    )

    page = ServiceJournal.consulter(administrateur, {"auteur": non_administrateur.username}, None)

    assert all(entree.auteur == non_administrateur for entree in page)


def test_le_filtre_periode_restreint_le_resultat(administrateur):
    ancienne = EntreeJournal.objects.create(
        type_action=TypeAction.ECHEC_AUTHENTIFICATION, identifiant_saisi="ancienne"
    )
    EntreeJournal.objects.filter(pk=ancienne.pk).update(cree_le=timezone.now() - timedelta(days=30))

    page = ServiceJournal.consulter(
        administrateur, {"debut": timezone.now().date().isoformat()}, None
    )

    assert all(entree.pk != ancienne.pk for entree in page)


def test_le_filtre_objet_restreint_le_resultat(administrateur):
    EntreeJournal.objects.create(
        type_action=TypeAction.CREATION_COMPTE,
        identifiant_saisi="a",
        objet_type="utilisateur",
        objet_identifiant="essai-cible",
    )
    EntreeJournal.objects.create(
        type_action=TypeAction.CREATION_COMPTE,
        identifiant_saisi="b",
        objet_type="utilisateur",
        objet_identifiant="autre-cible",
    )

    page = ServiceJournal.consulter(
        administrateur,
        {"objet_type": "utilisateur", "objet_identifiant": "essai-cible"},
        None,
    )

    assert {entree.objet_identifiant for entree in page} == {"essai-cible"}


def test_filtre_sans_resultat_rappelle_les_filtres(client, administrateur):
    client.force_login(administrateur)

    reponse = client.get(
        reverse("administration:journal"), {"objet_type": "introuvable", "objet_identifiant": "x"}
    )

    contenu = reponse.content.decode()
    assert "Aucune entrée ne correspond aux filtres" in contenu
    assert "introuvable" in contenu


def test_le_contrat_d_adresse_preselectionne_le_filtre_objet(client, administrateur):
    client.force_login(administrateur)

    reponse = client.get(
        reverse("administration:journal"),
        {"objet_type": "utilisateur", "objet_identifiant": "essai-cible"},
    )

    contenu = reponse.content.decode()
    assert 'value="utilisateur"' in contenu
    assert 'value="essai-cible"' in contenu


def test_au_dela_de_vingt_entrees_le_resultat_est_pagine(administrateur):
    for i in range(25):
        EntreeJournal.objects.create(
            type_action=TypeAction.ECHEC_AUTHENTIFICATION, identifiant_saisi=f"page-{i}"
        )

    page = ServiceJournal.consulter(administrateur, {}, None)

    assert page.has_next()
    assert page.paginator.count >= 25


def test_verifier_habilitation_refuse_un_non_administrateur(non_administrateur):
    """Le service refuse indépendamment de l'écran — § 2.3."""
    with pytest.raises(ErreurHabilitation):
        ServiceJournal.consulter(non_administrateur, {}, None)
