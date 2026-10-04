import dataclasses
import datetime

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.utils import timezone

from evaluations.services.evaluation import ServiceEvaluation
from evaluations.services.sujet import ServiceSujet
from organisation.models import Stagiaire
from organisation.services.affectation import ServiceAffectation
from organisation.services.brigade import ServiceBrigade
from organisation.services.session import ServiceSession
from planification.models import ProgrammeHebdomadaire, Seance
from referentiel.models import CategorieLieu, ElementReferentiel, Formation, Matiere, TypeFormation
from ressources.models import Instructeur, JourSemaine, Lieu, Qualification, Statut
from ressources.services.grille_horaire import ServiceCreneauType, ServiceGrilleHoraire


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
def examens(db):
    modele = get_user_model()
    return _utilisateur("examens-eval", "Cne", modele.Profil.CELLULE_EXAMENS, "Cellule examens")


@pytest.fixture
def planificateur(db):
    modele = get_user_model()
    return _utilisateur(
        "planificateur-eval", "Lt", modele.Profil.CELLULE_PLANIFICATION, "Cellule planification"
    )


@pytest.fixture
def redacteur(db):
    modele = get_user_model()
    return _utilisateur(
        "redacteur-eval", "Lt", modele.Profil.CELLULE_PEDAGOGIQUE, "Cellule pédagogique"
    )


@pytest.fixture
def direction_formation(db):
    modele = get_user_model()
    return _utilisateur(
        "direction-eval", "Col", modele.Profil.DIRECTION_FORMATION, "Direction de formation"
    )


@pytest.fixture
def administrateur(db):
    modele = get_user_model()
    return _utilisateur("admin-eval", "Cdt", modele.Profil.ADMINISTRATEUR, "Administrateur")


@pytest.fixture
def type_officiers(db):
    return TypeFormation.objects.create(intitule="Officiers EVAL")


@pytest.fixture
def formation(db, type_officiers):
    return Formation.objects.create(
        intitule="Formation EVAL",
        specialite="Transmissions",
        duree_semaines=10,
        type_formation=type_officiers,
    )


@pytest.fixture
def matiere(db):
    return Matiere.objects.create(intitule="Électronique numérique EVAL", code="ELNEV1")


@pytest.fixture
def element_referentiel(db, formation, matiere):
    return ElementReferentiel.objects.create(
        formation=formation,
        matiere=matiere,
        volume_horaire_prescrit=40,
        categorie_lieu=CategorieLieu.AUCUN_LIEU,
    )


@pytest.fixture
def autre_element_referentiel(db, type_officiers):
    """Module d'une AUTRE formation — B1/E1 : hors référentiel de la
    formation visée par le périmètre choisi."""
    autre_formation = Formation.objects.create(
        intitule="Autre formation EVAL",
        specialite="Transmissions",
        duree_semaines=10,
        type_formation=type_officiers,
    )
    autre_matiere = Matiere.objects.create(intitule="Propagation EVAL", code="PROPEV")
    return ElementReferentiel.objects.create(
        formation=autre_formation,
        matiere=autre_matiere,
        volume_horaire_prescrit=40,
        categorie_lieu=CategorieLieu.AUCUN_LIEU,
    )


@pytest.fixture
def session(redacteur, formation, element_referentiel):
    aujourd_hui = datetime.date.today()
    return ServiceSession.creer(
        redacteur,
        {
            "formation": formation,
            "intitule": "Session EVAL",
            "date_debut": aujourd_hui - datetime.timedelta(days=10),
            "date_fin": aujourd_hui + datetime.timedelta(days=180),
            "effectif_attendu": 24,
        },
    )


def creer_brigade(redacteur, session, designation, effectif=20):
    """Fonction libre, pas une fixture (`.claude/rules/python.md`, § 5
    paramètres max) : une brigade supplémentaire s'obtient par un appel
    direct dans le corps du test, pas par une fixture de plus à injecter."""
    return ServiceBrigade.creer(
        redacteur, session, {"designation": designation, "effectif_previsionnel": effectif}
    )


@pytest.fixture
def brigade(redacteur, session):
    return creer_brigade(redacteur, session, "EXP1")


@pytest.fixture
def instructeur(matiere):
    """Qualifié pour `matiere` dès sa création : la quasi-totalité des tests
    d'insertion de séance en ont besoin, jamais de l'instructeur seul."""
    instructeur = Instructeur.objects.create(
        nom="Zalbrok",
        prenom="Kelvar",
        matricule="M-EVAL1",
        grade="Lt",
        specialite="Transmissions",
        statut=Statut.MILITAIRE_DU_CENTRE,
    )
    Qualification.objects.create(instructeur=instructeur, matiere=matiere)
    return instructeur


@pytest.fixture
def lieu(db):
    return Lieu.objects.create(intitule="Salle EVAL 1", capacite=30, categorie="salle_attitree")


@pytest.fixture
def seance(lundi_semaine, element_referentiel, instructeur):
    """Séance directement instanciée (fabrique de test, exemptée de la porte
    d'écriture unique — `.claude/rules/tests.md`) : les tests du bloc A ne
    vérifient que les contraintes en base sur `Evaluation`, pas le circuit
    d'écriture d'une séance."""
    programme = ProgrammeHebdomadaire.objects.create(lundi_de_semaine=lundi_semaine)
    debut = timezone.make_aware(datetime.datetime.combine(lundi_semaine, datetime.time(8, 0)))
    fin = timezone.make_aware(datetime.datetime.combine(lundi_semaine, datetime.time(9, 45)))
    return Seance.objects.create(
        programme=programme,
        element_referentiel=element_referentiel,
        instructeur=instructeur,
        debut=debut,
        fin=fin,
        verrouillee=True,
    )


@pytest.fixture
def lundi_semaine():
    """Un vrai lundi, dans le futur — sans dépendre de la date du jour."""
    aujourd_hui = datetime.date.today()
    jours_jusqu_au_lundi = (7 - aujourd_hui.weekday()) % 7 or 7
    return aujourd_hui + datetime.timedelta(days=jours_jusqu_au_lundi + 14)


@pytest.fixture
def grille_active(planificateur):
    grille = ServiceGrilleHoraire.creer(planificateur, "Ordinaire EVAL")
    jours = [
        JourSemaine.LUNDI,
        JourSemaine.MARDI,
        JourSemaine.MERCREDI,
        JourSemaine.JEUDI,
        JourSemaine.VENDREDI,
    ]
    for jour in jours:
        ServiceCreneauType.ajouter(
            planificateur,
            grille,
            {
                "jour_semaine": jour,
                "ordre": 1,
                "heure_debut": datetime.time(8, 0),
                "heure_fin": datetime.time(9, 45),
            },
        )
    return ServiceGrilleHoraire.activer(planificateur, grille.pk)


def jour_lundi(lundi_semaine, decalage=0):
    """Un jour ouvré de la semaine du programme — RG-38 (calendrier),
    correspondant au créneau unique posé par `grille_active` (lundi à
    vendredi)."""
    return lundi_semaine + datetime.timedelta(days=decalage)


def creneau_du_jour(grille, jour):
    jours_iso = {
        1: JourSemaine.LUNDI,
        2: JourSemaine.MARDI,
        3: JourSemaine.MERCREDI,
        4: JourSemaine.JEUDI,
        5: JourSemaine.VENDREDI,
    }
    return grille.creneaux.get(jour_semaine=jours_iso[jour.isoweekday()], ordre=1)


def affecter_stagiaires(agissant, brigade, nombre, prefixe="M"):
    """Peuple `brigade.effectif_reel` — RG-37 (capacité d'un lieu) ne
    compare jamais à `effectif_previsionnel`, toujours à l'effectif réel."""
    for i in range(nombre):
        stagiaire = Stagiaire.objects.create(
            session=brigade.session,
            matricule=f"{prefixe}{i:04d}",
            nom="Stagiaire",
            prenom=f"Essai{i}",
            grade="Sgt",
            unite="1er RTR EVAL",
        )
        ServiceAffectation.affecter(agissant, stagiaire, brigade)


@dataclasses.dataclass(frozen=True)
class JourCreneau:
    """Regroupe le jour retenu et son créneau de la grille active —
    `.claude/rules/python.md`, § 5 paramètres max : les deux voyagent
    ensemble dans presque tous les appels de ce dossier de tests, même
    figure que `Cours`/`ScenarioGeneration` (`planification.tests.conftest`).
    """

    jour: object
    creneau: object


@pytest.fixture
def jour_creneau(grille_active, lundi_semaine):
    jour = jour_lundi(lundi_semaine)
    return JourCreneau(jour=jour, creneau=creneau_du_jour(grille_active, jour))


@dataclasses.dataclass(frozen=True)
class Controle:
    """Le scénario quasi systématique d'un test d'insertion de séance de
    contrôle : une brigade, un module, un instructeur qualifié, un jour et
    son créneau de la grille active."""

    examens: object
    brigade: object
    element_referentiel: object
    instructeur: object
    jour_creneau: JourCreneau


@pytest.fixture
def controle(examens, brigade, element_referentiel, instructeur, jour_creneau):
    return Controle(
        examens=examens,
        brigade=brigade,
        element_referentiel=element_referentiel,
        instructeur=instructeur,
        jour_creneau=jour_creneau,
    )


# --- US-EVAL-03 : sujets — fixtures partagées entre test_sujets.py et
# test_sujets_ecran.py (`.claude/rules/python.md`, fichier sous 400 lignes).


@pytest.fixture
def certificative(examens, session, element_referentiel):
    return ServiceEvaluation.creer(
        examens,
        {
            "element_referentiel": element_referentiel,
            "type": "certificative",
            "session": session,
            "brigade": None,
            "date": timezone.localdate() + datetime.timedelta(days=30),
            "creneau_type": None,
            "instructeur": None,
            "lieu": None,
            "motif_date_passee": "",
        },
    )


@pytest.fixture
def certificative_echue(examens, session, element_referentiel):
    """A9/B5 : jour de l'épreuve ATTEINT — contrôle à venir puis écoulé,
    jamais créée directement avec une date passée (RG-49 le refuserait à
    la création elle-même, ce n'est pas ce qu'on veut tester ici)."""
    return ServiceEvaluation.creer(
        examens,
        {
            "element_referentiel": element_referentiel,
            "type": "certificative",
            "session": session,
            "brigade": None,
            "date": timezone.localdate(),
            "creneau_type": None,
            "instructeur": None,
            "lieu": None,
            "motif_date_passee": "",
        },
    )


def _formative(controle, jour=None):
    return ServiceEvaluation.creer(
        controle.examens,
        {
            "element_referentiel": controle.element_referentiel,
            "type": "formative",
            "session": None,
            "brigade": controle.brigade,
            "date": jour or controle.jour_creneau.jour,
            "creneau_type": controle.jour_creneau.creneau,
            "instructeur": controle.instructeur,
            "lieu": None,
            "motif_date_passee": "",
        },
    )


@pytest.fixture
def formative(controle):
    return _formative(controle)


def _enregistrer(agissant, evaluation, reference, date_depot=None):
    return ServiceSujet.enregistrer(
        agissant,
        evaluation,
        {"reference": reference, "date_depot": date_depot or timezone.localdate()},
    )
