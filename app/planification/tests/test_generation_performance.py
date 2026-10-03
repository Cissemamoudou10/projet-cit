"""US-PLAN-03 — mesures de référence, Prompt 31 § 10.

Ferme le report laissé ouvert à la clôture d'US-PLAN-03 (`prompt 31.md`
§ 13 : « Mesures du § 10 reportées ») et fournit le contrôle de réalité
attendu par `etudes/solveur/PROTOCOLE.md` § 6 (Prompt 32) pour la
comparaison avec le prototype CP-SAT au jalon C2.

Jeu REPRÉSENTATIF (§ 10 : « plusieurs sessions actives, une dizaine de
brigades, une semaine complète ») — PAS l'échelle réelle du centre, qui vit
dans `etudes/solveur/HYPOTHESES.md` (15 sessions, 33 brigades) : les deux
mesures répondent à des questions différentes, l'une valide le système tel
qu'il tourne aujourd'hui, l'autre dimensionne l'étude du solveur.
"""

import dataclasses
import datetime
import logging
import time
from unittest import mock

import pytest
from django.conf import settings
from django.db import connection
from django.test.utils import CaptureQueriesContext

from organisation.services.brigade import ServiceBrigade
from organisation.services.session import ServiceSession
from planification.services.contraintes import ServiceContraintes
from planification.services.generation import ServiceGeneration
from planification.tests.conftest import activer_grille, creer_element, qualifier
from referentiel.models import CategorieLieu, Formation, Matiere, TypeFormation
from ressources.models import Instructeur, Statut

BRIGADES_PAR_SESSION = [4, 3, 3]  # dix brigades, trois sessions — § 10, Prompt 31
CRENEAUX_PAR_JOUR = 4
JOURS_OUVRES = 5
INSTRUCTEURS_PAR_MATIERE = 2  # assez pour ne pas buter systématiquement sur une
# indisponibilité, sans viser un remplissage à 100 % — § 10 MESURE ce taux, il
# ne le force pas.

# Requêtes constantes du jeu représentatif — 2026-10-03, D-211 (A6, prompt 38) : 43 → 45,
# une requête par chargement de `ServiceContraintes.contexte` (fournisseur des épreuves
# occupées), deux chargements par génération. D-161 (41, pente nulle de 40 à
# 200 séances, correction P-38) puis D-192/A8 (41 → 43 : seconde source de
# RG-38, `ResolveurJoursExamen`, un appel de plus dans `ServiceContraintes.
# contexte()`, même sans examen en base). Marge pour amortir un futur ajout
# borné analogue sans faire échouer ce test à chaque requête supplémentaire
# légitime — toute dérive AU-DELÀ de la marge doit rester visible ici, pas
# seulement dans MESURES-REFERENCE.md (Prompt 37, Temps 1).
REQUETES_REFERENCE_US_PLAN_03 = 45
MARGE_REQUETES = 2

journal = logging.getLogger(__name__)


def _creer_session_mesuree(redacteur, indice, lundi):
    type_formation = TypeFormation.objects.create(intitule=f"Type mesure {indice}")
    formation = Formation.objects.create(
        intitule=f"Formation mesure {indice}",
        specialite="Transmissions",
        duree_semaines=10,
        type_formation=type_formation,
    )
    matieres = [
        Matiere.objects.create(intitule=f"Matière mesure {indice}-{n}", code=f"MES{indice}{n}")
        for n in range(1, 4)
    ]
    for matiere in matieres:
        creer_element(formation, matiere, volume=200, categorie=CategorieLieu.AUCUN_LIEU)
    session = ServiceSession.creer(
        redacteur,
        {
            "formation": formation,
            "intitule": f"Session mesure {indice}",
            "date_debut": lundi - datetime.timedelta(days=10),
            "date_fin": lundi + datetime.timedelta(days=200),
            "effectif_attendu": 20,
        },
    )
    return session, matieres


def _creer_brigades(redacteur, session, nombre):
    return [
        ServiceBrigade.creer(
            redacteur, session, {"designation": f"BR{n}", "effectif_previsionnel": 20}
        )
        for n in range(1, nombre + 1)
    ]


def _creer_instructeurs_qualifies(matieres_par_session):
    compteur = 0
    for matieres in matieres_par_session:
        for matiere in matieres:
            for _ in range(INSTRUCTEURS_PAR_MATIERE):
                compteur += 1
                instructeur = Instructeur.objects.create(
                    nom=f"Instructeur{compteur}",
                    prenom="Mesure",
                    matricule=f"MES{compteur:04d}",
                    grade="Lt",
                    specialite="Transmissions",
                    statut=Statut.MILITAIRE_DU_CENTRE,
                )
                qualifier(instructeur, matiere)


def _construire_jeu_representatif(redacteur, lundi_semaine):
    matieres_par_session, brigades = [], []
    for indice, nombre_brigades in enumerate(BRIGADES_PAR_SESSION, start=1):
        session, matieres = _creer_session_mesuree(redacteur, indice, lundi_semaine)
        matieres_par_session.append(matieres)
        brigades += _creer_brigades(redacteur, session, nombre_brigades)
    _creer_instructeurs_qualifies(matieres_par_session)
    return brigades


@dataclasses.dataclass(frozen=True)
class GenerationBrute:
    """Ce que `_generer_en_mesurant` observe directement, avant calcul du
    taux de remplissage — `.claude/rules/python.md`, § 5 paramètres max :
    ces quatre valeurs voyagent ensemble jusqu'à `_mesures`."""

    compte_rendu: object
    duree: float
    nb_requetes: int
    nb_appels_contraintes: int


def _generer_en_mesurant(planificateur, lundi_semaine, brigades):
    appels_contraintes = {"n": 0}
    verifier_original = ServiceContraintes.verifier

    def _verifier_compte(*args, **kwargs):
        appels_contraintes["n"] += 1
        return verifier_original(*args, **kwargs)

    with (
        mock.patch.object(ServiceContraintes, "verifier", side_effect=_verifier_compte),
        CaptureQueriesContext(connection) as requetes,
    ):
        debut = time.perf_counter()
        compte_rendu = ServiceGeneration.generer(planificateur, lundi_semaine, brigades)
        duree = time.perf_counter() - debut

    return GenerationBrute(
        compte_rendu, duree, len(requetes.captured_queries), appels_contraintes["n"]
    )


@dataclasses.dataclass(frozen=True)
class MesuresGeneration:
    """Regroupe les quatre mesures du § 10 — même motif que `GenerationBrute`,
    elles voyagent ensemble du calcul à la journalisation."""

    nb_brigades: int
    cases_ouvertes: int
    duree: float
    nb_requetes: int
    nb_appels_contraintes: int
    cases_pourvues: int
    taux_remplissage: float


def _mesures(brigades, cases_ouvertes, brute):
    """Suppose que toute case est soit placée, soit comptée en
    `cases_non_pourvues` — faux si la génération a été interrompue par la
    borne de temps (`interrompu_par_la_borne`) : l'appelant doit l'avoir
    déjà écarté."""
    cases_non_pourvues = len(brute.compte_rendu.cases_non_pourvues)
    cases_pourvues = cases_ouvertes - cases_non_pourvues
    return MesuresGeneration(
        nb_brigades=len(brigades),
        cases_ouvertes=cases_ouvertes,
        duree=brute.duree,
        nb_requetes=brute.nb_requetes,
        nb_appels_contraintes=brute.nb_appels_contraintes,
        cases_pourvues=cases_pourvues,
        taux_remplissage=cases_pourvues / cases_ouvertes,
    )


def _journaliser(mesures):
    journal.info(
        "[Prompt 31 § 10] Mesures de référence — jeu représentatif "
        "(%d brigades, %d cases) : temps=%.3fs requêtes=%d appels_contraintes=%d "
        "remplissage=%.1f%% (%d/%d)",
        mesures.nb_brigades,
        mesures.cases_ouvertes,
        mesures.duree,
        mesures.nb_requetes,
        mesures.nb_appels_contraintes,
        mesures.taux_remplissage * 100,
        mesures.cases_pourvues,
        mesures.cases_ouvertes,
    )


@pytest.mark.django_db
def test_mesures_de_reference_us_plan_03_paragraphe_10(planificateur, redacteur, lundi_semaine):
    activer_grille(
        planificateur,
        "Grille mesure § 10",
        [
            (datetime.time(8, 0), datetime.time(9, 45)),
            (datetime.time(10, 10), datetime.time(12, 0)),
            (datetime.time(13, 0), datetime.time(14, 45)),
            (datetime.time(15, 0), datetime.time(16, 45)),
        ],
    )
    brigades = _construire_jeu_representatif(redacteur, lundi_semaine)
    cases_ouvertes = len(brigades) * CRENEAUX_PAR_JOUR * JOURS_OUVRES

    brute = _generer_en_mesurant(planificateur, lundi_semaine, brigades)

    assert not brute.compte_rendu.interrompu_par_la_borne, (
        "génération interrompue par la borne de temps : cases ni placées ni "
        "comptées en cases_non_pourvues, le taux de remplissage serait faux"
    )
    mesures = _mesures(brigades, cases_ouvertes, brute)
    _journaliser(mesures)

    assert mesures.duree < settings.GENERATION_BORNE_TEMPS_SECONDES  # BNF-04
    assert mesures.taux_remplissage > 0
    assert mesures.nb_requetes <= REQUETES_REFERENCE_US_PLAN_03 + MARGE_REQUETES
