"""Correctif P-42 — ordre de verrouillage déterministe du traitement en lot
(Prompt 44, Temps 1). Hors story : dette de production sur US-PLAN-09, pas un
critère d'acceptation. Voir `docs/suivi/PROBLEMES.md`.
"""

import datetime
import re

from django.db import connection
from django.test.utils import CaptureQueriesContext

from planification.models import ProgrammeHebdomadaire
from planification.services.indisponibilite import traiter_lot_remplacement
from planification.tests.aide_circuit import seance_dans
from planification.tests.conftest import instant, qualifier


def _trois_programmes_avec_une_seance(lundi, cours, brigade_formation):
    programmes = [
        ProgrammeHebdomadaire.objects.create(lundi_de_semaine=lundi + datetime.timedelta(weeks=n))
        for n in (1, 2, 3)
    ]
    seances = [
        seance_dans(programme, cours, brigade_formation, instant(programme.lundi_de_semaine, 0, 8))
        for programme in programmes
    ]
    return programmes, seances


def _requete_de_verrouillage_du_lot(requetes):
    """La requête UNIQUE posée par `_verrouiller_programmes_par_ordre_
    croissant` : un `SELECT ... WHERE id IN (...) ORDER BY id ASC FOR
    UPDATE`, à distinguer des verrous `WHERE id = <pk>` repris ensuite, un
    par séance, par `modifier_seance` (sans effet, déjà tenus)."""
    for sql in (requete["sql"] for requete in requetes.captured_queries):
        if "FOR UPDATE" in sql and "programme_hebdomadaire" in sql.lower() and " IN (" in sql:
            return sql
    return None


def test_p42_lot_verrouille_les_programmes_dans_l_ordre_croissant_de_leur_identifiant(
    circuit, cours, brigade_formation, autre_instructeur
):
    """Trois programmes, soumis dans un ordre mélangé (le second, le
    troisième, puis le premier) — le verrouillage préalable du lot doit
    malgré tout porter les trois programmes, triés par `ORDER BY id ASC`,
    en UNE seule requête (`.claude/rules/python.md`, aucune requête dans une
    boucle) avant toute écriture."""
    qualifier(autre_instructeur, cours.element.matiere)
    lundi = circuit.programme.lundi_de_semaine
    (programme_1, programme_2, programme_3), (seance_1, seance_2, seance_3) = (
        _trois_programmes_avec_une_seance(lundi, cours, brigade_formation)
    )
    assert programme_1.pk < programme_2.pk < programme_3.pk

    with CaptureQueriesContext(connection) as requetes:
        traiter_lot_remplacement(
            circuit.acteurs.planificateur,
            [seance_2, seance_3, seance_1],
            autre_instructeur,
        )

    sql = _requete_de_verrouillage_du_lot(requetes)
    assert sql is not None, "aucune requête de verrouillage préalable du lot trouvée"
    assert re.search(r'ORDER BY "[^"]+"\."id" ASC', sql), "pas de tri croissant explicite"
    pks_verrouilles = {int(n) for n in re.search(r"IN \(([\d, ]+)\)", sql).group(1).split(", ")}
    assert pks_verrouilles == {programme_1.pk, programme_2.pk, programme_3.pk}
