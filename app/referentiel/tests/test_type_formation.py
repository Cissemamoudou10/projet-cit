"""US-REF-00 — Gérer les types de formation, CU-P2-01."""

import pytest
from django.db import IntegrityError, transaction
from django.urls import reverse

from administration.models import EntreeJournal, TypeAction
from noyau.exceptions import ErreurHabilitation
from referentiel.models import TypeFormation
from referentiel.services.type_formation import ServiceTypeFormation


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


def test_planification_examens_direction_lisent_seulement(lecteur):
    ServiceTypeFormation.lister(lecteur, {}, None)  # ne lève pas

    with pytest.raises(ErreurHabilitation):
        ServiceTypeFormation.creer(lecteur, {"intitule": "Sous-officiers"})
