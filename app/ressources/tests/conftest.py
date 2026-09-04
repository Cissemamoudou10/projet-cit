import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command


def _utilisateur(username, grade, profil, groupe):
    call_command("initialiser_habilitations")
    modele = get_user_model()
    utilisateur = modele.objects.create_user(
        username=username, password="x", grade=grade, profil=profil
    )
    utilisateur.groups.add(Group.objects.get(name=groupe))
    utilisateur.doit_changer_mot_de_passe = False
    utilisateur.save()
    return utilisateur


@pytest.fixture
def redacteur(db):
    modele = get_user_model()
    return _utilisateur(
        "redacteur-ins", "Lt", modele.Profil.CELLULE_PEDAGOGIQUE, "Cellule pédagogique"
    )


@pytest.fixture
def planificateur(db):
    modele = get_user_model()
    return _utilisateur(
        "planificateur-ins", "Lt", modele.Profil.CELLULE_PLANIFICATION, "Cellule planification"
    )


@pytest.fixture
def direction_formation(db):
    modele = get_user_model()
    return _utilisateur(
        "direction-ins", "Cne", modele.Profil.DIRECTION_FORMATION, "Direction de formation"
    )


@pytest.fixture
def cellule_examens(db):
    """§ 4.1 du Prompt 12 : aucun accès au domaine, ni lecture ni écriture —
    la matrice § 11.2 ne lui donne rien sur `instructeurs_qualifications`,
    contrairement au référentiel où elle lit."""
    modele = get_user_model()
    return _utilisateur("examens-ins", "Lt", modele.Profil.CELLULE_EXAMENS, "Cellule examens")
