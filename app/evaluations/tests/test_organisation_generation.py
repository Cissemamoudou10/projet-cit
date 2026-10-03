"""US-EVAL-04, D3 — génération sur une semaine où une épreuve occupe un lieu (A6, P5 → P6).

Passe par `ServiceGeneration.generer` : présélection puis vérification. Scénario
valide : la brigade générée n'est PAS dans la session de l'épreuve (sinon RG-38,
jour d'examen, bloque toute la session et masque A6). Le lieu est un lieu partagé
occupé par l'épreuve ; le témoin sans organisation prouve que le créneau est sinon
pris. Données entièrement fictives.
"""

import dataclasses
import datetime

import pytest

from evaluations.services.evaluation import ServiceEvaluation
from evaluations.services.organisation import ServiceOrganisationEpreuve as Service
from evaluations.tests.conftest import creer_brigade
from noyau.intervalles import instant_de
from organisation.services.session import ServiceSession
from planification.models import Seance
from planification.services.generation import ServiceGeneration
from referentiel.models import CategorieLieu, ElementReferentiel, Formation, TypeLieuPartage
from ressources.models import Lieu, ModePartage

H8, H10 = datetime.time(8, 0), datetime.time(10, 0)


@dataclasses.dataclass(frozen=True)
class CadreD3:
    planificateur: object
    examens: object
    redacteur: object
    session: object
    type_officiers: object
    matiere: object
    element: object
    brigade: object
    lundi: datetime.date


@pytest.fixture
def acteurs(planificateur, examens, redacteur, grille_active, instructeur):
    return {"planificateur": planificateur, "examens": examens, "redacteur": redacteur}


@pytest.fixture
def epreuve_cadre(session, type_officiers, matiere, element_referentiel, brigade):
    return {
        "session": session,
        "type_officiers": type_officiers,
        "matiere": matiere,
        "element": element_referentiel,
        "brigade": brigade,
    }


@pytest.fixture
def cadre(acteurs, epreuve_cadre, lundi_semaine):
    return CadreD3(**acteurs, **epreuve_cadre, lundi=lundi_semaine)


def _epreuve_sur_le_lieu(cadre, lieu, mardi, avec_organisation):
    epreuve = ServiceEvaluation.creer(
        cadre.examens,
        {
            "element_referentiel": cadre.element,
            "type": "certificative",
            "session": cadre.session,
            "brigade": None,
            "date": mardi,
            "creneau_type": None,
            "instructeur": None,
            "lieu": None,
            "motif_date_passee": "",
        },
    )
    Service.fixer_creneau(cadre.examens, epreuve, H8, H10)
    if avec_organisation:
        organisation = Service.ajouter_organisation(cadre.examens, epreuve, cadre.brigade, lieu, 1)
        Service.ajouter_surveillant(cadre.examens, organisation, nom_libre="Surveillant D3")


def _brigade_hors_session(cadre):
    """Brigade d'une autre session, formation qui programme des cours en lieu partagé."""
    formation = Formation.objects.create(
        intitule="Formation D3 B2",
        specialite="Transmissions",
        duree_semaines=10,
        type_formation=cadre.type_officiers,
    )
    ElementReferentiel.objects.create(
        formation=formation,
        matiere=cadre.matiere,
        volume_horaire_prescrit=200,
        categorie_lieu=CategorieLieu.LIEU_PARTAGE,
        type_lieu_partage=TypeLieuPartage.AMPHITHEATRE,
    )
    session = ServiceSession.creer(
        cadre.redacteur,
        {
            "formation": formation,
            "intitule": "Session D3 B2",
            "date_debut": cadre.lundi - datetime.timedelta(days=10),
            "date_fin": cadre.lundi + datetime.timedelta(days=200),
            "effectif_attendu": 20,
        },
    )
    return creer_brigade(cadre.redacteur, session, "D3-B2")


@pytest.mark.parametrize(
    "avec_organisation", [True, False], ids=["epreuve-organisee", "temoin-sans-epreuve"]
)
def test_d3_generation_n_occupe_pas_le_lieu_de_l_epreuve_sur_son_creneau(avec_organisation, cadre):
    lieu = Lieu.objects.create(
        intitule="Amphi D3",
        capacite=60,
        categorie="lieu_partage",
        type_partage="amphitheatre",
        mode_partage=ModePartage.SIMULTANE,
    )
    mardi = cadre.lundi + datetime.timedelta(days=1)
    _epreuve_sur_le_lieu(cadre, lieu, mardi, avec_organisation)
    brigade_b2 = _brigade_hors_session(cadre)

    ServiceGeneration.generer(cadre.planificateur, cadre.lundi, [brigade_b2])

    fenetre = Seance.objects.filter(debut__lt=instant_de(mardi, H10), fin__gt=instant_de(mardi, H8))
    if avec_organisation:
        assert not fenetre.filter(lieu=lieu).exists()
    else:
        assert fenetre.filter(lieu=lieu).exists()
    assert Seance.objects.filter(lignes__brigade=brigade_b2).exists()
