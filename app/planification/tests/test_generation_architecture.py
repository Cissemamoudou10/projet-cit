"""US-PLAN-03 — Groupe I : architecture et performance. Prompt 31, § 12.
I1/I2/I4 sont couverts par `tests/architecture` (relancé après chaque série
d'éditions, .claude/rules/tests.md) — ce module ne porte que I3, qui exige
un jeu de données dédié. Données entièrement fictives.
"""

import datetime

from django.db import connection
from django.test.utils import CaptureQueriesContext

from planification.services.generation import ServiceGeneration
from planification.tests.conftest import activer_grille, qualifier


def test_i3_nombre_de_requetes_sql_borne_independant_du_nombre_de_cases(
    scenario, cours, brigade_formation
):
    """Prescrit à 1 h, sous le plus petit créneau (1,75 h) : une seule
    séance s'écrit, UNE FOIS pour toute la mesure (RG-39 a) modifiée,
    prompt 56, dès la chauffe) — isole les requêtes de LECTURE de celles
    d'ÉCRITURE, qui scalent avec les séances produites, pas les cases."""
    qualifier(cours.instructeur, cours.element.matiere)
    cours.element.volume_horaire_prescrit = 1
    cours.element.save()

    # Semaine de chauffe, hors mesure : absorbe les requêtes ponctuelles
    # (caches Django sur les permissions/types de contenu) qui fausseraient
    # sinon la comparaison entre la première et la seconde mesure.
    lundi_chauffe = scenario.lundi - datetime.timedelta(weeks=1)
    ServiceGeneration.generer(scenario.planificateur, lundi_chauffe, [brigade_formation])

    with CaptureQueriesContext(connection) as petite_grille:
        ServiceGeneration.generer(scenario.planificateur, scenario.lundi, [brigade_formation])

    lundi_suivant = scenario.lundi + datetime.timedelta(weeks=1)
    activer_grille(
        scenario.planificateur,
        "Grande grille I3",
        [
            (datetime.time(8, 0), datetime.time(9, 45)),
            (datetime.time(10, 10), datetime.time(12, 0)),
            (datetime.time(13, 0), datetime.time(14, 45)),
            (datetime.time(15, 0), datetime.time(16, 45)),
        ],
    )
    with CaptureQueriesContext(connection) as grande_grille:
        ServiceGeneration.generer(scenario.planificateur, lundi_suivant, [brigade_formation])

    ecart = abs(len(grande_grille.captured_queries) - len(petite_grille.captured_queries))
    assert ecart <= 5, (
        f"{len(petite_grille.captured_queries)} requêtes (10 cases) contre "
        f"{len(grande_grille.captured_queries)} (20 cases) — écart de {ecart}, attendu <= 5."
    )
