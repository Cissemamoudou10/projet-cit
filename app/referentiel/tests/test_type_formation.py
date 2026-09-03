"""US-REF-00 — Gérer les types de formation, CU-P2-01."""

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.db import IntegrityError, transaction

from administration.models import EntreeJournal, TypeAction
from noyau.exceptions import ErreurHabilitation
from referentiel.models import TypeFormation
from referentiel.services.type_formation import ServiceTypeFormation


@pytest.fixture
def redacteur(db):
    call_command("initialiser_habilitations")
    modele = get_user_model()
    utilisateur = modele.objects.create_user(
        username="redacteur-ref", password="x", grade="Lt", profil=modele.Profil.CELLULE_PEDAGOGIQUE
    )
    utilisateur.groups.add(Group.objects.get(name="Cellule pédagogique"))
    return utilisateur


@pytest.fixture
def lecteur(db):
    call_command("initialiser_habilitations")
    modele = get_user_model()
    utilisateur = modele.objects.create_user(
        username="lecteur-ref", password="x", grade="Lt", profil=modele.Profil.CELLULE_EXAMENS
    )
    utilisateur.groups.add(Group.objects.get(name="Cellule examens"))
    return utilisateur


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


def test_planification_examens_direction_lisent_seulement(lecteur):
    ServiceTypeFormation.lister(lecteur, {}, None)  # ne lève pas

    with pytest.raises(ErreurHabilitation):
        ServiceTypeFormation.creer(lecteur, {"intitule": "Sous-officiers"})
