"""Preuve par le vrai générateur — prompt 56, RG-66 : rejoue la session S1
du jeu `complet` (M1-M9, M6 prérequis de M8, ~11,6 semaines) semaine par
semaine, du début à la fin, pour deux brigades. Lent (une douzaine de
générations réelles, deux brigades) : marqueur `plafond_session_entiere`,
mais PAS exclu par défaut (à la différence de `navigateur`) — il fait
partie de la suite complète, prompt 56 ne demande pas de l'en isoler.
Données entièrement fictives.
"""

import datetime
import logging

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.utils import timezone

from organisation.services.brigade import ServiceBrigade
from organisation.services.session import ServiceSession
from planification.models import Seance
from planification.services.circuit import ServiceCircuitProgramme
from planification.services.contraintes import volumes_programme_echu_par_element_brigade
from planification.services.generation import ServiceGeneration
from referentiel.models import (
    CategorieLieu,
    ElementReferentiel,
    Formation,
    Matiere,
    Prerequis,
    TypeFormation,
)
from ressources.models import CategorieLieu as CategorieLieuR
from ressources.models import (
    GrilleHoraire,
    Instructeur,
    JourSemaine,
    Lieu,
    ModePartage,
    Qualification,
    SalleAttitree,
    Statut,
)
from ressources.models import TypeLieuPartage as TypeLieuPartageR
from ressources.services.grille_horaire import ServiceCreneauType, ServiceGrilleHoraire

pytestmark = pytest.mark.plafond_session_entiere

journal = logging.getLogger(__name__)

# (code, prescrit, catégorie de lieu, type de lieu partagé) — exactement la
# composition de F6 (donnees_complet.py, prompt 51), 200 h au total.
COMPOSITION_S1 = [
    ("M1", 40, CategorieLieu.SALLE_ATTITREE, None),
    ("M2", 30, CategorieLieu.LIEU_PARTAGE, TypeLieuPartageR.AMPHITHEATRE),
    ("M3", 20, CategorieLieu.AUCUN_LIEU, None),
    ("M6", 40, CategorieLieu.SALLE_ATTITREE, None),
    ("M7", 30, CategorieLieu.LIEU_PARTAGE, TypeLieuPartageR.LABORATOIRE),
    ("M8", 20, CategorieLieu.SALLE_ATTITREE, None),
    ("M9", 20, CategorieLieu.SALLE_ATTITREE, None),
]
DUREE_SESSION_JOURS = 81  # ~11,6 semaines, même durée que S1 (prompt 55)


def _utilisateur(username, profil, groupe):
    modele = get_user_model()
    utilisateur = modele.objects.create_user(username=username, password="x", profil=profil)
    utilisateur.groups.add(Group.objects.get(name=groupe))
    utilisateur.doit_changer_mot_de_passe = False
    utilisateur.save()
    return utilisateur


def _creer_referentiel(formation):
    elements = {}
    for code, volume, categorie, type_partage in COMPOSITION_S1:
        matiere = Matiere.objects.create(intitule=f"{code} session entière", code=f"SE-{code}")
        elements[code] = ElementReferentiel.objects.create(
            formation=formation,
            matiere=matiere,
            volume_horaire_prescrit=volume,
            categorie_lieu=categorie,
            type_lieu_partage=type_partage,
        )
    Prerequis.objects.create(element=elements["M8"], element_prerequis=elements["M6"])
    return elements


def _qualifier_deux_instructeurs(elements):
    for code, element in elements.items():
        for i in range(2):
            instructeur = Instructeur.objects.create(
                nom=f"SE-{code}-{i}",
                prenom="Test",
                matricule=f"SE-{code}{i}",
                grade="Lt",
                specialite="Transmissions",
                statut=Statut.MILITAIRE_DU_CENTRE,
            )
            Qualification.objects.create(instructeur=instructeur, matiere=element.matiere)


def _creer_lieux_partages():
    amphi = Lieu.objects.create(
        intitule="Amphi SE",
        capacite=200,
        categorie=CategorieLieuR.LIEU_PARTAGE,
        type_partage=TypeLieuPartageR.AMPHITHEATRE,
        mode_partage=ModePartage.SIMULTANE,
    )
    labo = Lieu.objects.create(
        intitule="Labo SE",
        capacite=200,
        categorie=CategorieLieuR.LIEU_PARTAGE,
        type_partage=TypeLieuPartageR.LABORATOIRE,
        mode_partage=ModePartage.SIMULTANE,
    )
    return amphi, labo


def _creer_session_et_brigades(redacteur, planificateur, formation):
    aujourd_hui = timezone.localdate()
    debut = aujourd_hui + datetime.timedelta(days=(7 - aujourd_hui.weekday()) % 7 or 7)
    session = ServiceSession.creer(
        redacteur,
        {
            "formation": formation,
            "intitule": "S1 session entière",
            "date_debut": debut,
            "date_fin": debut + datetime.timedelta(days=DUREE_SESSION_JOURS),
            "effectif_attendu": 35,
        },
    )
    exp1 = ServiceBrigade.creer(
        redacteur, session, {"designation": "EXP1-SE", "effectif_previsionnel": 20}
    )
    exp2 = ServiceBrigade.creer(
        redacteur, session, {"designation": "EXP2-SE", "effectif_previsionnel": 15}
    )
    for brigade in (exp1, exp2):
        salle = Lieu.objects.create(
            intitule=f"Salle {brigade.designation}",
            capacite=25,
            categorie=CategorieLieuR.SALLE_ATTITREE,
        )
        SalleAttitree.objects.create(brigade=brigade, lieu=salle)
    return session, exp1, exp2


def _activer_grille(planificateur):
    """Trois créneaux par jour, cinq jours — marge confortable (≈ 26 h de
    capacité brute par semaine et par brigade) au-dessus des 200 h à placer
    sur 11,6 semaines, pour que seul le plafond (et le prérequis) pacent la
    génération, jamais la grille elle-même."""
    creneaux = [
        (datetime.time(8, 0), datetime.time(9, 45)),
        (datetime.time(10, 10), datetime.time(12, 0)),
        (datetime.time(13, 0), datetime.time(14, 45)),
    ]
    grille = GrilleHoraire.objects.create(intitule="Grille session entière")
    jours = [
        JourSemaine.LUNDI,
        JourSemaine.MARDI,
        JourSemaine.MERCREDI,
        JourSemaine.JEUDI,
        JourSemaine.VENDREDI,
    ]
    for jour in jours:
        for ordre, (debut, fin) in enumerate(creneaux, start=1):
            ServiceCreneauType.ajouter(
                planificateur,
                grille,
                {"jour_semaine": jour, "ordre": ordre, "heure_debut": debut, "heure_fin": fin},
            )
    ServiceGrilleHoraire.activer(planificateur, grille.pk)


def _approuver_semaine(planificateur, pedagogique, programme):
    """Amène le programme à AFFICHÉ — sans quoi son volume ne compte jamais
    comme RÉALISÉ (RG-60) et M8 ne franchirait jamais le prérequis de M6
    (`regles_volume._verifier_prerequis`). Une semaine SANS séance (A9,
    `ServiceCircuitProgramme.soumettre`) n'est jamais soumise — attendu en
    fin de session, une fois chaque matière épuisée ou son plafond à zéro
    de reste : rien à approuver, rien à signaler."""
    if not Seance.objects.filter(programme=programme).exists():
        return
    ServiceCircuitProgramme.soumettre(planificateur, programme)
    programme.refresh_from_db()
    ServiceCircuitProgramme.valider(pedagogique, programme)
    programme.refresh_from_db()
    ServiceCircuitProgramme.enregistrer_signature(
        planificateur, programme, timezone.localdate(), "Signataire session entière"
    )
    programme.refresh_from_db()
    ServiceCircuitProgramme.afficher(planificateur, programme)


def _lundi_de(date_reference):
    return date_reference - datetime.timedelta(days=date_reference.weekday())


@pytest.fixture
def _scenario(db):
    call_command("initialiser_habilitations")
    planificateur = _utilisateur("plan-se", "cellule_planification", "Cellule planification")
    redacteur = _utilisateur("ped-se", "cellule_pedagogique", "Cellule pédagogique")
    type_formation = TypeFormation.objects.create(intitule="Type session entière")
    formation = Formation.objects.create(
        intitule="Formation session entière",
        specialite="Transmissions",
        duree_semaines=12,
        type_formation=type_formation,
    )
    elements = _creer_referentiel(formation)
    _qualifier_deux_instructeurs(elements)
    _creer_lieux_partages()
    _activer_grille(planificateur)
    session, exp1, exp2 = _creer_session_et_brigades(redacteur, planificateur, formation)
    return planificateur, redacteur, session, exp1, exp2, elements


def test_plafond_pace_la_session_entiere_sans_depassement(_scenario):
    planificateur, redacteur, session, exp1, exp2, elements = _scenario
    brigades = [exp1, exp2]
    lundi = _lundi_de(session.date_debut)
    tableau = []

    while lundi <= session.date_fin:
        compte_rendu = ServiceGeneration.generer(planificateur, lundi, brigades)
        for ligne in compte_rendu.volumes:
            tableau.append(
                (
                    lundi,
                    ligne.brigade.designation,
                    ligne.element.matiere.code,
                    ligne.heures_cette_semaine,
                )
            )
        _approuver_semaine(planificateur, redacteur, compte_rendu.programme)
        lundi += datetime.timedelta(weeks=1)

    a_la_date = timezone.make_aware(datetime.datetime.combine(lundi, datetime.time.min))
    echu = volumes_programme_echu_par_element_brigade(
        a_la_date, brigade_ids=[b.pk for b in brigades]
    )
    journal.info("=== Bilan final, par brigade et par matière ===")
    for brigade in brigades:
        for code, element in elements.items():
            atteint = echu.get((element.pk, brigade.pk), 0)
            journal.info(
                "  %-10s %-4s prescrit=%6.2f atteint=%7.3f reste=%7.3f",
                brigade.designation,
                code,
                element.volume_horaire_prescrit,
                atteint,
                element.volume_horaire_prescrit - atteint,
            )
    _verifier_prescrit_presque_atteint(brigades, elements, echu, tableau)
    _verifier_m8_entierement_placee(brigades, elements, echu)


def _duree_creneau():
    return 1.75  # heures — le plus court créneau de la grille de ce test


def _verifier_prescrit_presque_atteint(brigades, elements, echu, tableau):
    for brigade in brigades:
        for code, element in elements.items():
            atteint = echu.get((element.pk, brigade.pk), 0)
            ecart = element.volume_horaire_prescrit - atteint
            assert ecart <= _duree_creneau() + 1e-9, (
                f"{brigade.designation}/{code} : {atteint:.2f} h sur {element.volume_horaire_prescrit} h "
                f"prescrites — écart {ecart:.2f} h, au-delà d'une séance ({tableau[-5:]})"
            )


def _verifier_m8_entierement_placee(brigades, elements, echu):
    m8 = elements["M8"]
    for brigade in brigades:
        atteint = echu.get((m8.pk, brigade.pk), 0)
        assert m8.volume_horaire_prescrit - atteint <= _duree_creneau() + 1e-9, (
            f"{brigade.designation}/M8 non entièrement placée : {atteint:.2f} h sur "
            f"{m8.volume_horaire_prescrit} h — M6 n'a pas laissé assez de session pour M8"
        )
