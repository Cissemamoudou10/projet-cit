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
        username="redacteur-ref", password="x", grade="Lt", profil=modele.Profil.CELLULE_PEDAGOGIQUE
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
        username="lecteur-ref", password="x", grade="Lt", profil=modele.Profil.CELLULE_EXAMENS
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
        username="planificateur-ref",
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
        username="direction-ref",
        password="x",
        grade="Cne",
        profil=modele.Profil.DIRECTION_FORMATION,
    )
    utilisateur.groups.add(Group.objects.get(name="Direction de formation"))
    utilisateur.doit_changer_mot_de_passe = False
    utilisateur.save()
    return utilisateur


@pytest.fixture
def type_officiers(db):
    return TypeFormation.objects.create(intitule="Officiers")


@pytest.fixture
def formation(db, type_officiers):
    return Formation.objects.create(
        intitule="Formation initiale",
        specialite="Transmissions",
        duree_semaines=10,
        type_formation=type_officiers,
    )


@pytest.fixture
def matiere(db):
    return Matiere.objects.create(intitule="Électronique numérique", code="ELN01")


def donnees_element_referentiel(**supplement):
    """Pas une fixture — un helper : US-REF-03/04, `ElementReferentiel` a
    besoin d'un couple (formation, matière) différent selon le test.
    """
    donnees = {
        "volume_horaire_prescrit": 40,
        "categorie_lieu": CategorieLieu.SALLE_ATTITREE,
        "type_lieu_partage": None,
    }
    donnees.update(supplement)
    return donnees


def creer_element(formation, intitule, code=""):
    """Pas une fixture — un helper : US-REF-06 a besoin d'un nombre variable
    d'éléments de référentiel par test, pour composer un graphe de
    prérequis.
    """
    matiere = Matiere.objects.create(intitule=intitule, code=code)
    return ElementReferentiel.objects.create(
        formation=formation, matiere=matiere, **donnees_element_referentiel()
    )
