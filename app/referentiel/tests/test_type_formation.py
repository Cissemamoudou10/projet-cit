"""US-REF-00 — Gérer les types de formation, CU-P2-01."""

import pytest
from django.contrib.messages import get_messages
from django.db import IntegrityError, transaction
from django.urls import reverse

from administration.models import EntreeJournal, TypeAction
from noyau.exceptions import ErreurHabilitation
from referentiel.models import TypeFormation
from referentiel.services.formation import ServiceFormation
from referentiel.services.type_formation import ServiceTypeFormation
from referentiel.tests.test_formation import _donnees


def test_intitule_unique_en_base_en_contournant_l_orm(db):
    """Sans passer par `full_clean` : un test qui passe par la validation
    Python ne prouve rien sur la contrainte — Prompt 05, § 7.
    """
    TypeFormation.objects.create(intitule="Officiers")

    with pytest.raises(IntegrityError), transaction.atomic():
        TypeFormation.objects.create(intitule="officiers")


def test_creation_modification_archivage_sont_journalises(redacteur):
    type_formation = ServiceTypeFormation.creer(redacteur, {"intitule": "Officiers"})
    ServiceTypeFormation.modifier(
        redacteur,
        type_formation.pk,
        {"intitule": "Officiers supérieurs"},
        type_formation.modifie_le,
    )
    ServiceTypeFormation.archiver(redacteur, type_formation.pk)

    natures = list(
        EntreeJournal.objects.filter(
            objet_type="type_formation", objet_identifiant__icontains="officiers"
        )
        .order_by("cree_le")
        .values_list("type_action", flat=True)
    )
    assert TypeAction.CREATION_ELEMENT_GESTION in natures
    assert TypeAction.MODIFICATION_ELEMENT_GESTION in natures
    assert TypeAction.ARCHIVAGE_ELEMENT_GESTION in natures


def test_un_type_archive_reste_consultable(redacteur):
    type_formation = ServiceTypeFormation.creer(redacteur, {"intitule": "Officiers"})
    ServiceTypeFormation.archiver(redacteur, type_formation.pk)

    page = ServiceTypeFormation.lister(redacteur, {}, None)

    assert type_formation.pk in [ligne.pk for ligne in page]


def test_cellule_pedagogique_ecrit(redacteur):
    ServiceTypeFormation.creer(redacteur, {"intitule": "Officiers"})  # ne lève pas


def test_modifier_par_le_vrai_formulaire_html_ne_declenche_pas_a_tort_e5(client, redacteur):
    """Bug réel trouvé en usage (2026-09-03) : le champ caché
    `modifie_le_attendu` arrive du POST comme une chaîne, jamais comparable
    telle quelle à `instance.modifie_le` (un `datetime`) — voir
    docs/suivi/PROBLEMES.md. Contrairement aux autres tests de ce fichier,
    celui-ci passe par le vrai cycle GET puis POST, seul chemin qui exerçait
    le bug — un appel direct au service avec un `datetime` Python ne
    l'aurait jamais révélé.
    """
    type_formation = ServiceTypeFormation.creer(redacteur, {"intitule": "Officiers"})
    client.force_login(redacteur)

    reponse_get = client.get(
        reverse("referentiel:modifier_type_formation", args=[type_formation.pk])
    )
    modifie_le_attendu = reponse_get.context["modifie_le_attendu"]

    reponse_post = client.post(
        reverse("referentiel:modifier_type_formation", args=[type_formation.pk]),
        {"intitule": "Officiers supérieurs", "modifie_le_attendu": modifie_le_attendu.isoformat()},
    )

    assert reponse_post.status_code == 302
    type_formation.refresh_from_db()
    assert type_formation.intitule == "Officiers supérieurs"


def test_creer_par_l_ecran_cree_reellement_le_type(client, redacteur):
    """Bloc D.2 du Prompt 19 : preuve d'un effet réel, pas d'un code de
    retour (P-21)."""
    client.force_login(redacteur)

    client.post(reverse("referentiel:creer_type_formation"), {"intitule": "Sous-officiers"})

    assert TypeFormation.objects.filter(intitule="Sous-officiers").exists()


def test_archiver_par_l_ecran_le_retire_reellement_de_la_selection(client, redacteur):
    type_formation = ServiceTypeFormation.creer(redacteur, {"intitule": "Officiers"})
    client.force_login(redacteur)

    client.post(reverse("referentiel:archiver_type_formation", args=[type_formation.pk]))

    assert type_formation.pk not in [
        t.pk for t in ServiceTypeFormation.disponibles_pour_selection()
    ]


def test_desarchiver_par_l_ecran_le_rend_reellement_a_la_selection(client, redacteur):
    type_formation = ServiceTypeFormation.creer(redacteur, {"intitule": "Officiers"})
    ServiceTypeFormation.archiver(redacteur, type_formation.pk)
    client.force_login(redacteur)

    client.post(reverse("referentiel:desarchiver_type_formation", args=[type_formation.pk]))

    assert type_formation.pk in [t.pk for t in ServiceTypeFormation.disponibles_pour_selection()]


def test_planification_examens_direction_lisent_seulement(lecteur):
    ServiceTypeFormation.lister(lecteur, {}, None)  # ne lève pas

    with pytest.raises(ErreurHabilitation):
        ServiceTypeFormation.creer(lecteur, {"intitule": "Sous-officiers"})


def test_suppression_est_journalisee(redacteur):
    """Prompt 16, cause racine n° 3, § 5 : « chaque suppression est
    journalisée » — relevé en relecture, `ServiceGestion.supprimer` ne
    journalisait rien, contrairement à `creer`/`modifier`/`archiver`."""
    type_formation = ServiceTypeFormation.creer(redacteur, {"intitule": "Officiers"})

    ServiceTypeFormation.supprimer(redacteur, type_formation.pk)

    assert EntreeJournal.objects.filter(
        objet_type="type_formation",
        objet_identifiant="Officiers",
        type_action=TypeAction.SUPPRESSION_ELEMENT_GESTION,
    ).exists()


def test_suppression_d_un_type_jamais_utilise_reussit_depuis_l_ecran(client, redacteur):
    """Prompt 16, cause racine n° 3 : aucune route de suppression n'existait
    pour les types de formation — seul `ServiceGestion.supprimer` (déjà prêt)
    était atteignable, jamais l'écran. Confirmation par dialogue (BNF-09),
    comme l'archivage, mais avec un texte distinct — une suppression est
    définitive."""
    type_formation = ServiceTypeFormation.creer(redacteur, {"intitule": "Officiers"})
    client.force_login(redacteur)

    reponse_get = client.get(
        reverse("referentiel:supprimer_type_formation", args=[type_formation.pk])
    )
    assert reponse_get.status_code == 200

    reponse_post = client.post(
        reverse("referentiel:supprimer_type_formation", args=[type_formation.pk])
    )

    assert reponse_post.status_code == 302
    assert not TypeFormation.objects.filter(pk=type_formation.pk).exists()


def test_suppression_d_un_type_utilise_est_refusee_en_enumerant_les_formations(
    client, redacteur, type_officiers
):
    """E3 : le refus énumère l'élément qui s'oppose, pas un refus sec."""
    formation = ServiceFormation.creer(redacteur, _donnees(type_officiers))
    client.force_login(redacteur)

    reponse = client.post(reverse("referentiel:supprimer_type_formation", args=[type_officiers.pk]))

    assert reponse.status_code == 302
    assert TypeFormation.objects.filter(pk=type_officiers.pk).exists()
    messages_affiches = [str(m) for m in get_messages(reponse.wsgi_request)]
    assert any(formation.intitule in message for message in messages_affiches)
