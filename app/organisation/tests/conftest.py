import datetime

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command

from referentiel.models import CategorieLieu, ElementReferentiel, Formation, Matiere, TypeFormation


@pytest.fixture
def redacteur(db):
    """Déjà onboardé (`doit_changer_mot_de_passe=False`) : sans quoi
    l'intergiciel de première connexion redirigerait toute requête faite par
    ce compte dans un test de vue — voir administration/tests/conftest.py.
    """
    call_command("initialiser_habilitations")
    modele = get_user_model()
    utilisateur = modele.objects.create_user(
        username="redacteur-org", password="x", grade="Lt", profil=modele.Profil.CELLULE_PEDAGOGIQUE
    )
    utilisateur.groups.add(Group.objects.get(name="Cellule pédagogique"))
    utilisateur.doit_changer_mot_de_passe = False
    utilisateur.save()
    return utilisateur


@pytest.fixture
def lecteur(db):
    call_command("initialiser_habilitations")
    modele = get_user_model()
    utilisateur = modele.objects.create_user(
        username="lecteur-org", password="x", grade="Lt", profil=modele.Profil.CELLULE_EXAMENS
    )
    utilisateur.groups.add(Group.objects.get(name="Cellule examens"))
    utilisateur.doit_changer_mot_de_passe = False
    utilisateur.save()
    return utilisateur


@pytest.fixture
def planificateur(db):
    call_command("initialiser_habilitations")
    modele = get_user_model()
    utilisateur = modele.objects.create_user(
        username="planificateur-org",
        password="x",
        grade="Lt",
        profil=modele.Profil.CELLULE_PLANIFICATION,
    )
    utilisateur.groups.add(Group.objects.get(name="Cellule planification"))
    utilisateur.doit_changer_mot_de_passe = False
    utilisateur.save()
    return utilisateur


@pytest.fixture
def direction_formation(db):
    call_command("initialiser_habilitations")
    modele = get_user_model()
    utilisateur = modele.objects.create_user(
        username="direction-org",
        password="x",
        grade="Cne",
        profil=modele.Profil.DIRECTION_FORMATION,
    )
    utilisateur.groups.add(Group.objects.get(name="Direction de formation"))
    utilisateur.doit_changer_mot_de_passe = False
    utilisateur.save()
    return utilisateur


@pytest.fixture
def administrateur(db):
    call_command("initialiser_habilitations")
    modele = get_user_model()
    utilisateur = modele.objects.create_user(
        username="administrateur-org",
        password="x",
        grade="Cdt",
        profil=modele.Profil.ADMINISTRATEUR,
    )
    utilisateur.groups.add(Group.objects.get(name="Administrateur"))
    utilisateur.doit_changer_mot_de_passe = False
    utilisateur.save()
    return utilisateur


@pytest.fixture
def type_officiers(db):
    return TypeFormation.objects.create(intitule="Officiers")


@pytest.fixture
def formation(db, type_officiers):
    """Référentiel composé (une matière rattachée) : c'est le cas courant,
    seul autorisé à l'ouverture d'une session — E4 le refuse sinon."""
    formation = Formation.objects.create(
        intitule="Formation initiale",
        specialite="Transmissions",
        duree_semaines=10,
        type_formation=type_officiers,
    )
    matiere = Matiere.objects.create(intitule="Électronique numérique", code="ELN01")
    ElementReferentiel.objects.create(
        formation=formation,
        matiere=matiere,
        volume_horaire_prescrit=40,
        categorie_lieu=CategorieLieu.SALLE_ATTITREE,
        type_lieu_partage=None,
    )
    return formation


@pytest.fixture
def formation_archivee(db, type_officiers):
    formation = Formation.objects.create(
        intitule="Formation archivée",
        specialite="Transmissions",
        duree_semaines=8,
        type_formation=type_officiers,
    )
    formation.archive = True
    formation.save()
    return formation


@pytest.fixture
def formation_vide(db, type_officiers):
    """Aucun élément de référentiel — E4."""
    return Formation.objects.create(
        intitule="Formation sans référentiel",
        specialite="Transmissions",
        duree_semaines=6,
        type_formation=type_officiers,
    )


def donnees_session(formation, **supplement):
    """Pas une fixture — un helper : plusieurs tests ont besoin d'une
    formation différente ou d'une période différente."""
    donnees = {
        "formation": formation,
        "intitule": "Session 1",
        "date_debut": datetime.date(2026, 1, 5),
        "date_fin": datetime.date(2026, 3, 27),
        "effectif_attendu": 24,
    }
    donnees.update(supplement)
    return donnees
