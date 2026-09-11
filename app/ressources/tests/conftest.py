import datetime

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command

from organisation.services.brigade import ServiceBrigade
from organisation.services.session import ServiceSession
from referentiel.models import CategorieLieu as CategorieLieuReferentiel
from referentiel.models import ElementReferentiel, Formation, Matiere, TypeFormation
from ressources.models import CategorieLieu, Instructeur, Lieu, Statut


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


@pytest.fixture
def instructeur(db):
    return Instructeur.objects.create(
        nom="Ziani",
        prenom="Karim",
        matricule="M12345",
        grade="Lt",
        specialite="Transmissions",
        statut=Statut.MILITAIRE_DU_CENTRE,
    )


@pytest.fixture
def lieu(db):
    return Lieu.objects.create(
        intitule="Salle 101", capacite=30, categorie=CategorieLieu.SALLE_ATTITREE
    )


@pytest.fixture
def administrateur(db):
    modele = get_user_model()
    return _utilisateur("administrateur-ins", "Cdt", modele.Profil.ADMINISTRATEUR, "Administrateur")


@pytest.fixture
def session(db, redacteur, type_officiers):
    """US-SES-03 : `organisation` est désormais importable depuis
    `ressources` (D-85) — construite par le service, jamais à la main
    (P-21, .claude/rules/tests.md)."""
    formation = Formation.objects.create(
        intitule="Formation session salle",
        specialite="Transmissions",
        duree_semaines=10,
        type_formation=type_officiers,
    )
    ElementReferentiel.objects.create(
        formation=formation,
        matiere=Matiere.objects.create(intitule="Antennes", code="ANT01"),
        volume_horaire_prescrit=40,
        categorie_lieu=CategorieLieuReferentiel.SALLE_ATTITREE,
        type_lieu_partage=None,
    )
    aujourd_hui = datetime.date.today()
    return ServiceSession.creer(
        redacteur,
        {
            "formation": formation,
            "intitule": "Session salle attitrée",
            "date_debut": aujourd_hui + datetime.timedelta(days=30),
            "date_fin": aujourd_hui + datetime.timedelta(days=111),
            "effectif_attendu": 24,
        },
    )


@pytest.fixture
def brigade(db, redacteur, session):
    return ServiceBrigade.creer(
        redacteur, session, {"designation": "EXP1", "effectif_previsionnel": 20}
    )
