"""Fixtures propres aux tests d'architecture qui ont besoin de la base et du
cycle HTTP réel (test_ecrans_ecriture.py) — les trois autres fichiers du
dossier sont de l'analyse statique pure, sans fixture.

Ce dossier n'est lié par aucune règle de dépendance entre applications
(tests/architecture/test_couches.py importe déjà toutes les applications
pour vérifier justement cette règle) : les fixtures ci-dessous importent
librement administration, referentiel et ressources, ce qu'aucun fichier
sous app/ n'aurait le droit de faire dans le même sens.
"""

import datetime

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command

from administration.constantes import GROUPES
from evaluations.models import Evaluation, OrganisationEpreuve, Sujet, Surveillance, TypeEvaluation
from organisation.models import Brigade, Session, Stagiaire
from planification.models import LigneProgramme, ProgrammeHebdomadaire, Seance
from referentiel.models import CategorieLieu, ElementReferentiel, Formation, Matiere, TypeFormation
from referentiel.services.objectif_pedagogique import ServiceObjectifPedagogique
from referentiel.services.prerequis import ServicePrerequis
from ressources.models import CategorieLieu as CategorieLieuRessource
from ressources.models import (
    CreneauType,
    GrilleHoraire,
    IndisponibiliteInstructeur,
    IndisponibiliteLieu,
    Instructeur,
    JourSemaine,
    Lieu,
    NatureEvenement,
    PeriodeCalendrier,
    Qualification,
    Statut,
)


@pytest.fixture
def groupes_habilitation(db):
    call_command("initialiser_habilitations")


@pytest.fixture
def utilisateurs(groupes_habilitation):
    """Un compte réel par groupe (§ 11.2), jamais un compte sans groupe :
    RG-02 bis, les droits reposent sur les groupes Django, jamais sur
    `profil` seul — voir administration/habilitations.py.
    """
    modele = get_user_model()
    profils = {
        "Administrateur": modele.Profil.ADMINISTRATEUR,
        "Cellule pédagogique": modele.Profil.CELLULE_PEDAGOGIQUE,
        "Cellule planification": modele.Profil.CELLULE_PLANIFICATION,
        "Cellule examens": modele.Profil.CELLULE_EXAMENS,
        "Direction de formation": modele.Profil.DIRECTION_FORMATION,
    }
    comptes = {}
    for groupe in GROUPES:
        compte = modele.objects.create_user(
            username=f"essai-{groupe}",
            password="x",
            grade="Lt",
            profil=profils[groupe],
        )
        compte.groups.add(Group.objects.get(name=groupe))
        compte.doit_changer_mot_de_passe = False
        compte.save()
        comptes[groupe] = compte
    return comptes


@pytest.fixture
def objets(db, utilisateurs):
    """Un jeu minimal d'objets cibles, un par écran d'écriture — construit
    par un compte Administrateur (habilité partout) pour ne tester ici que
    le refus, jamais la création elle-même (déjà testée ailleurs, par
    écran). Jamais mutés par les tests de refus : une tentative refusée
    n'atteint jamais le service.
    """
    redacteur = utilisateurs["Cellule pédagogique"]
    type_formation = TypeFormation.objects.create(intitule="Officiers")
    formation = Formation.objects.create(
        intitule="Formation initiale",
        specialite="Transmissions",
        duree_semaines=10,
        type_formation=type_formation,
    )
    matiere = Matiere.objects.create(intitule="Électronique numérique", code="ELN01")
    element = ElementReferentiel.objects.create(
        formation=formation,
        matiere=matiere,
        volume_horaire_prescrit=40,
        categorie_lieu=CategorieLieu.SALLE_ATTITREE,
        type_lieu_partage=None,
    )
    autre_matiere = Matiere.objects.create(intitule="Radiocommunications", code="RAD01")
    autre_element = ElementReferentiel.objects.create(
        formation=formation,
        matiere=autre_matiere,
        volume_horaire_prescrit=20,
        categorie_lieu=CategorieLieu.SALLE_ATTITREE,
        type_lieu_partage=None,
    )
    objectif = ServiceObjectifPedagogique.ajouter(redacteur, matiere, "Analyser un schéma")
    prerequis = ServicePrerequis.ajouter(redacteur, formation, element, autre_element)
    lieu = Lieu.objects.create(
        intitule="Salle 101", capacite=30, categorie=CategorieLieuRessource.SALLE_ATTITREE
    )
    indisponibilite = IndisponibiliteLieu.objects.create(
        lieu=lieu,
        debut="2026-09-08T08:00:00Z",
        fin="2026-09-08T09:45:00Z",
        motif="Essai",
    )
    instructeur = Instructeur.objects.create(
        nom="Zalbrok",
        prenom="Kelvar",
        matricule="M12345",
        grade="Lt",
        specialite="Transmissions",
        statut=Statut.MILITAIRE_DU_CENTRE,
    )
    qualification = Qualification.objects.create(instructeur=instructeur, matiere=matiere)
    indisponibilite_instructeur = IndisponibiliteInstructeur.objects.create(
        instructeur=instructeur,
        debut="2026-09-08T08:00:00Z",
        fin="2026-09-08T09:45:00Z",
        motif="Essai",
    )
    compte_cible = get_user_model().objects.create_user(
        username="compte-cible-essai",
        password="x",
        grade="Sgt",
        profil=get_user_model().Profil.CELLULE_PEDAGOGIQUE,
    )
    session = Session.objects.create(
        formation=formation,
        intitule="Session essai",
        date_debut="2026-01-05",
        date_fin="2026-03-27",
        effectif_attendu=24,
    )
    brigade = Brigade.objects.create(session=session, designation="EXP1", effectif_previsionnel=20)
    stagiaire = Stagiaire.objects.create(
        session=session,
        matricule="M001",
        nom="Zalbrok",
        prenom="Kelvar",
        grade="Lt",
        unite="1er RTR",
    )
    nature_evenement = NatureEvenement.objects.create(
        libelle="Nature essai", effet_par_defaut="bloquant"
    )
    periode_calendrier = PeriodeCalendrier.objects.create(
        nature=nature_evenement,
        intitule="Période essai",
        debut="2026-09-08T08:00:00Z",
        fin="2026-09-08T09:45:00Z",
        effet="bloquant",
    )
    grille_horaire = GrilleHoraire.objects.create(intitule="Grille essai")
    creneau_type = CreneauType.objects.create(
        grille=grille_horaire,
        jour_semaine=JourSemaine.LUNDI,
        ordre=1,
        heure_debut="08:00",
        heure_fin="09:45",
    )
    evaluation = Evaluation.objects.create(
        element_referentiel=element,
        session=session,
        type=TypeEvaluation.CERTIFICATIVE,
        date="2026-02-01",
    )
    sujet = Sujet.objects.create(
        evaluation=evaluation, rang=1, reference="Sujet essai", date_depot="2026-01-15"
    )
    organisation = OrganisationEpreuve.objects.create(
        evaluation=evaluation, brigade=brigade, lieu=lieu, effectif_attendu=1
    )
    surveillance = Surveillance.objects.create(organisation=organisation, nom_libre="Surveillant essai")
    programme_seance = ProgrammeHebdomadaire.objects.create(lundi_de_semaine=datetime.date(2030, 1, 14))
    seance = Seance.objects.create(
        programme=programme_seance,
        element_referentiel=element,
        instructeur=instructeur,
        debut=datetime.datetime(2030, 1, 14, 8, 0, tzinfo=datetime.UTC),
        fin=datetime.datetime(2030, 1, 14, 10, 0, tzinfo=datetime.UTC),
    )
    ligne_programme = LigneProgramme.objects.create(seance=seance, brigade=brigade)
    return {
        "seance": seance,
        "ligne_programme": ligne_programme,
        "type_formation": type_formation,
        "formation": formation,
        "matiere": matiere,
        "element": element,
        "autre_element": autre_element,
        "objectif": objectif,
        "prerequis": prerequis,
        "lieu": lieu,
        "indisponibilite": indisponibilite,
        "instructeur": instructeur,
        "qualification": qualification,
        "indisponibilite_instructeur": indisponibilite_instructeur,
        "compte_cible": compte_cible,
        "session": session,
        "brigade": brigade,
        "evaluation": evaluation,
        "programme": ProgrammeHebdomadaire.objects.create(
            lundi_de_semaine=datetime.date(2030, 1, 7)
        ),
        "sujet": sujet,
        "organisation": organisation,
        "surveillance": surveillance,
        "stagiaire": stagiaire,
        "nature_evenement": nature_evenement,
        "periode_calendrier": periode_calendrier,
        "grille_horaire": grille_horaire,
        "creneau_type": creneau_type,
    }
