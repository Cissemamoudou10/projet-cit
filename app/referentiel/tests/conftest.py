import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command


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
