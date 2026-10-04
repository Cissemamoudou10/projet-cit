import dataclasses
import datetime

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command

from organisation.models import Stagiaire
from organisation.services.affectation import ServiceAffectation
from organisation.services.brigade import ServiceBrigade
from organisation.services.session import ServiceSession
from referentiel.models import CategorieLieu, ElementReferentiel, Formation, Matiere, TypeFormation
from ressources.models import Instructeur, Lieu, ModePartage, Qualification, Statut


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
def planificateur(db):
    modele = get_user_model()
    return _utilisateur(
        "planificateur-plan", "Lt", modele.Profil.CELLULE_PLANIFICATION, "Cellule planification"
    )


@pytest.fixture
def redacteur(db):
    modele = get_user_model()
    return _utilisateur(
        "redacteur-plan", "Lt", modele.Profil.CELLULE_PEDAGOGIQUE, "Cellule pédagogique"
    )


@pytest.fixture
def direction_formation(db):
    modele = get_user_model()
    return _utilisateur(
        "direction-plan", "Col", modele.Profil.DIRECTION_FORMATION, "Direction de formation"
    )


@pytest.fixture
def examens(db):
    modele = get_user_model()
    return _utilisateur("examens-plan", "Cne", modele.Profil.CELLULE_EXAMENS, "Cellule examens")


@pytest.fixture
def type_officiers(db):
    return TypeFormation.objects.create(intitule="Officiers PLAN")


@pytest.fixture
def formation(db, type_officiers):
    return Formation.objects.create(
        intitule="Formation PLAN",
        specialite="Transmissions",
        duree_semaines=10,
        type_formation=type_officiers,
    )


def creer_element(
    formation, matiere, *, volume=40, categorie=CategorieLieu.AUCUN_LIEU, type_lieu_partage=None
):
    return ElementReferentiel.objects.create(
        formation=formation,
        matiere=matiere,
        volume_horaire_prescrit=volume,
        categorie_lieu=categorie,
        type_lieu_partage=type_lieu_partage,
    )


@pytest.fixture
def matiere(db):
    return Matiere.objects.create(intitule="Électronique numérique", code="ELN01")


@pytest.fixture
def element_referentiel(db, formation, matiere):
    return creer_element(formation, matiere)


@pytest.fixture
def session(db, redacteur, type_officiers):
    aujourd_hui = datetime.date.today()
    formation_session = Formation.objects.create(
        intitule="Formation session PLAN",
        specialite="Transmissions",
        duree_semaines=10,
        type_formation=type_officiers,
    )
    ElementReferentiel.objects.create(
        formation=formation_session,
        matiere=Matiere.objects.create(intitule="Antennes PLAN", code="ANTP1"),
        volume_horaire_prescrit=40,
        categorie_lieu=CategorieLieu.AUCUN_LIEU,
    )
    return ServiceSession.creer(
        redacteur,
        {
            "formation": formation_session,
            "intitule": "Session PLAN",
            "date_debut": aujourd_hui + datetime.timedelta(days=30),
            "date_fin": aujourd_hui + datetime.timedelta(days=111),
            "effectif_attendu": 24,
        },
    )


@pytest.fixture
def autre_session(db, redacteur, type_officiers):
    aujourd_hui = datetime.date.today()
    formation_session = Formation.objects.create(
        intitule="Formation session PLAN B",
        specialite="Transmissions",
        duree_semaines=10,
        type_formation=type_officiers,
    )
    ElementReferentiel.objects.create(
        formation=formation_session,
        matiere=Matiere.objects.create(intitule="Propagation PLAN", code="PROP1"),
        volume_horaire_prescrit=40,
        categorie_lieu=CategorieLieu.AUCUN_LIEU,
    )
    return ServiceSession.creer(
        redacteur,
        {
            "formation": formation_session,
            "intitule": "Session PLAN B",
            "date_debut": aujourd_hui + datetime.timedelta(days=200),
            "date_fin": aujourd_hui + datetime.timedelta(days=280),
            "effectif_attendu": 24,
        },
    )


@pytest.fixture
def brigade(db, redacteur, session):
    return ServiceBrigade.creer(
        redacteur, session, {"designation": "EXP1", "effectif_previsionnel": 20}
    )


@pytest.fixture
def session_formation(db, redacteur, formation):
    """Contrairement à `session` (qui crée sa PROPRE formation), celle-ci
    est ouverte sur `formation` — nécessaire dès qu'un test veut que
    `brigade.session.formation` corresponde à `element_referentiel`
    (génération, US-PLAN-03) : `ServiceContraintes` ne le vérifie jamais
    (`Candidate` porte les deux indépendamment), mais `ServiceGeneration`
    en a besoin pour déterminer les matières programmables d'une brigade.

    Sème un élément sur une matière DÉDIÉE, jamais sur la fixture `matiere`
    partagée : `ServiceSession.creer` refuse une formation sans référentiel
    composé (§ 4, Prompt 20), mais un test de génération construit souvent
    ses propres éléments sur `matiere`/`formation` — dépendre de la fixture
    `element_referentiel` ici créait un élément fantôme en doublon
    (`uq_element_referentiel_formation_matiere`), piège découvert en
    écrivant le groupe D de US-PLAN-03."""
    aujourd_hui = datetime.date.today()
    matiere_semence = Matiere.objects.create(intitule="Matière semence PLAN", code="SEM-PLAN")
    creer_element(formation, matiere_semence, volume=1)
    return ServiceSession.creer(
        redacteur,
        {
            "formation": formation,
            "intitule": "Session formation PLAN",
            "date_debut": aujourd_hui + datetime.timedelta(days=30),
            "date_fin": aujourd_hui + datetime.timedelta(days=200),
            "effectif_attendu": 24,
        },
    )


@pytest.fixture
def brigade_formation(db, redacteur, session_formation):
    return ServiceBrigade.creer(
        redacteur, session_formation, {"designation": "GEN1", "effectif_previsionnel": 20}
    )


@pytest.fixture
def autre_brigade_formation(db, redacteur, session_formation):
    return ServiceBrigade.creer(
        redacteur, session_formation, {"designation": "GEN2", "effectif_previsionnel": 20}
    )


@pytest.fixture
def autre_brigade(db, redacteur, session):
    return ServiceBrigade.creer(
        redacteur, session, {"designation": "EXP2", "effectif_previsionnel": 20}
    )


@pytest.fixture
def brigade_autre_session(db, redacteur, autre_session):
    return ServiceBrigade.creer(
        redacteur, autre_session, {"designation": "EXP1", "effectif_previsionnel": 20}
    )


def affecter_stagiaires(agissant, brigade, nombre, prefixe="M"):
    """Peuple `brigade.effectif_reel` — affectations OUVERTES de stagiaires
    NON RADIÉS (US-SES-06), jamais posées à la main (P-21) : passe par
    `ServiceAffectation`, comme le ferait un écran réel."""
    for i in range(nombre):
        stagiaire = Stagiaire.objects.create(
            session=brigade.session,
            matricule=f"{prefixe}{i:04d}",
            nom="Stagiaire",
            prenom=f"Essai{i}",
            grade="Sgt",
            unite="1er RTR",
        )
        ServiceAffectation.affecter(agissant, stagiaire, brigade)


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
def autre_instructeur(db):
    return Instructeur.objects.create(
        nom="Kibour",
        prenom="Youssef",
        matricule="M67890",
        grade="Cne",
        specialite="Transmissions",
        statut=Statut.MILITAIRE_DU_CENTRE,
    )


@pytest.fixture
def qualification(db, instructeur, matiere):
    return Qualification.objects.create(instructeur=instructeur, matiere=matiere)


def qualifier(instructeur, matiere):
    return Qualification.objects.create(instructeur=instructeur, matiere=matiere)


@pytest.fixture
def lieu_partage(db):
    return Lieu.objects.create(
        intitule="Amphi PLAN",
        capacite=30,
        categorie="lieu_partage",
        type_partage="amphitheatre",
        mode_partage=ModePartage.SIMULTANE,
    )


@pytest.fixture
def lundi_semaine():
    """Un vrai lundi, dans le futur — sans dépendre de la date du jour."""
    aujourd_hui = datetime.date.today()
    jours_jusqu_au_lundi = (7 - aujourd_hui.weekday()) % 7 or 7
    return aujourd_hui + datetime.timedelta(days=jours_jusqu_au_lundi + 14)


@pytest.fixture
def programme(db, lundi_semaine):
    from planification.models import ProgrammeHebdomadaire

    return ProgrammeHebdomadaire.objects.create(lundi_de_semaine=lundi_semaine)


@dataclasses.dataclass(frozen=True)
class Cours:
    """Regroupe élément de référentiel et instructeur — .claude/rules/
    python.md, § 5 paramètres max : ces deux-là voyagent ensemble dans
    presque tous les appels d'aide de ce dossier de tests."""

    element: object
    instructeur: object


@pytest.fixture
def cours(element_referentiel, instructeur):
    return Cours(element_referentiel, instructeur)


def instant(lundi_semaine, jour_offset, heure, minute=0):
    jour = lundi_semaine + datetime.timedelta(days=jour_offset)
    return datetime.datetime(jour.year, jour.month, jour.day, heure, minute, tzinfo=datetime.UTC)


def activer_grille(planificateur, intitule, creneaux, jours=None):
    """`creneaux` : liste de `(heure_debut, heure_fin)` en `datetime.time`,
    un rang par ordre d'apparition, répétés sur `jours` (tous les jours
    ouvrés par défaut) — US-PLAN-03, groupes A à I."""
    from ressources.models import GrilleHoraire, JourSemaine
    from ressources.services.grille_horaire import ServiceCreneauType, ServiceGrilleHoraire

    jours = jours or [
        JourSemaine.LUNDI,
        JourSemaine.MARDI,
        JourSemaine.MERCREDI,
        JourSemaine.JEUDI,
        JourSemaine.VENDREDI,
    ]
    grille = GrilleHoraire.objects.create(intitule=intitule)
    for jour in jours:
        for ordre, (debut, fin) in enumerate(creneaux, start=1):
            ServiceCreneauType.ajouter(
                planificateur,
                grille,
                {"jour_semaine": jour, "ordre": ordre, "heure_debut": debut, "heure_fin": fin},
            )
    return ServiceGrilleHoraire.activer(planificateur, grille.pk)


@pytest.fixture
def grille_active(planificateur):
    return activer_grille(
        planificateur,
        "Ordinaire PLAN",
        [(datetime.time(8, 0), datetime.time(9, 45)), (datetime.time(10, 10), datetime.time(12, 0))],
    )


@dataclasses.dataclass(frozen=True)
class ScenarioGeneration:
    """Regroupe les trois fixtures quasi systématiques d'un test de
    génération (US-PLAN-03) — `.claude/rules/python.md`, § 5 paramètres
    max, la même figure que `Cours` pour US-PLAN-04."""

    planificateur: object
    lundi: object
    grille: object


@pytest.fixture
def scenario(planificateur, grille_active, lundi_semaine):
    return ScenarioGeneration(planificateur=planificateur, lundi=lundi_semaine, grille=grille_active)


@dataclasses.dataclass(frozen=True)
class Acteurs:
    """Les trois acteurs qui conduisent le circuit du programme (US-VAL-03)."""

    planificateur: object
    pedagogique: object
    examens: object


@dataclasses.dataclass(frozen=True)
class CircuitDeTest:
    """Le programme d'un test du circuit, son élément, sa brigade et ses
    acteurs — regroupés pour respecter la limite de cinq paramètres."""

    programme: object
    cours: object
    brigade: object
    acteurs: Acteurs


@pytest.fixture
def acteurs(planificateur, redacteur, examens):
    return Acteurs(planificateur=planificateur, pedagogique=redacteur, examens=examens)


@pytest.fixture
def circuit(programme, cours, brigade_formation, acteurs):
    return CircuitDeTest(
        programme=programme, cours=cours, brigade=brigade_formation, acteurs=acteurs
    )
