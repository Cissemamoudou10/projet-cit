import datetime

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command

from organisation.services.brigade import ServiceBrigade
from organisation.services.session import ServiceSession
from referentiel.models import CategorieLieu as CategorieLieuReferentiel
from referentiel.models import ElementReferentiel, Formation, Matiere, TypeFormation
from ressources.models import CategorieLieu, Instructeur, Lieu, NatureEvenement, Statut


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


@pytest.fixture
def autre_session(db, redacteur, type_officiers):
    """Une seconde session, aux dates disjointes de `session` — nécessaire
    pour tester les cibles multiples (C2/C3/D4) et la projection RG-30 bis
    sans dépendre d'une seule session partagée."""
    formation = Formation.objects.create(
        intitule="Formation session calendrier B",
        specialite="Transmissions",
        duree_semaines=10,
        type_formation=type_officiers,
    )
    ElementReferentiel.objects.create(
        formation=formation,
        matiere=Matiere.objects.create(intitule="Propagation", code="PRO01"),
        volume_horaire_prescrit=40,
        categorie_lieu=CategorieLieuReferentiel.SALLE_ATTITREE,
        type_lieu_partage=None,
    )
    aujourd_hui = datetime.date.today()
    return ServiceSession.creer(
        redacteur,
        {
            "formation": formation,
            "intitule": "Session calendrier B",
            "date_debut": aujourd_hui + datetime.timedelta(days=200),
            "date_fin": aujourd_hui + datetime.timedelta(days=280),
            "effectif_attendu": 24,
        },
    )


@pytest.fixture
def autre_brigade(db, redacteur, autre_session):
    return ServiceBrigade.creer(
        redacteur, autre_session, {"designation": "EXP2", "effectif_previsionnel": 18}
    )


@pytest.fixture
def troisieme_session(db, redacteur, type_officiers):
    """Nécessaire à D4 (Prompt 28) : intersection partielle entre une
    période ciblant A et B et une période ciblant B et C — trois sessions
    distinctes, dont une commune."""
    formation = Formation.objects.create(
        intitule="Formation session calendrier C",
        specialite="Transmissions",
        duree_semaines=10,
        type_formation=type_officiers,
    )
    ElementReferentiel.objects.create(
        formation=formation,
        matiere=Matiere.objects.create(intitule="Cryptographie", code="CRY01"),
        volume_horaire_prescrit=40,
        categorie_lieu=CategorieLieuReferentiel.SALLE_ATTITREE,
        type_lieu_partage=None,
    )
    aujourd_hui = datetime.date.today()
    return ServiceSession.creer(
        redacteur,
        {
            "formation": formation,
            "intitule": "Session calendrier C",
            "date_debut": aujourd_hui + datetime.timedelta(days=300),
            "date_fin": aujourd_hui + datetime.timedelta(days=380),
            "effectif_attendu": 24,
        },
    )


@pytest.fixture
def nature_evenement(db):
    return NatureEvenement.objects.create(libelle="Nature essai", effet_par_defaut="bloquant")
