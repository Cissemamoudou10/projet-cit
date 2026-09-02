import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command


@pytest.fixture
def mot_de_passe():
    return "un-mot-de-passe-suffisamment-long"


@pytest.fixture
def utilisateur(db, mot_de_passe):
    """Déjà onboardé (`doit_changer_mot_de_passe=False`, posé depuis
    US-ADM-02) : sans quoi l'intergiciel de première connexion redirigerait
    toute requête faite avec ce compte, y compris dans les tests d'US-ADM-01
    qui ne s'attendent pas à ce comportement.
    """
    modele = get_user_model()
    compte = modele.objects.create_user(
        username="essai",
        password=mot_de_passe,
        grade="Lt",
        profil=modele.Profil.ADMINISTRATEUR,
    )
    compte.doit_changer_mot_de_passe = False
    compte.save()
    return compte


@pytest.fixture
def groupes_habilitation(db):
    """Les groupes et leurs permissions n'existent qu'après cette commande —
    voir app/administration/management/commands/initialiser_habilitations.py.
    """
    call_command("initialiser_habilitations")


@pytest.fixture
def administrateur(groupes_habilitation, mot_de_passe):
    """Membre du groupe Administrateur, donc réellement habilité au sens de
    `verifier_habilitation` — pas seulement `profil=administrateur` (RG-02
    bis : les droits reposent sur les groupes Django, pas sur `profil`).
    Déjà onboardé (`doit_changer_mot_de_passe=False`) : les tests qui
    exercent précisément l'intergiciel de première connexion lèvent le
    drapeau eux-mêmes, explicitement.
    """
    modele = get_user_model()
    compte = modele.objects.create_user(
        username="admin-essai",
        password=mot_de_passe,
        grade="Cne",
        profil=modele.Profil.ADMINISTRATEUR,
    )
    compte.groups.add(Group.objects.get(name="Administrateur"))
    compte.doit_changer_mot_de_passe = False
    compte.save()
    return compte


@pytest.fixture
def non_administrateur(db, mot_de_passe):
    modele = get_user_model()
    compte = modele.objects.create_user(
        username="non-admin-essai",
        password=mot_de_passe,
        grade="Sgt",
        profil=modele.Profil.CELLULE_PEDAGOGIQUE,
    )
    compte.doit_changer_mot_de_passe = False
    compte.save()
    return compte
