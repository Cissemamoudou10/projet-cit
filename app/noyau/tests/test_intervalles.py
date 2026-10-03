"""Recouvrement d'intervalles (`noyau.intervalles`), sans base de données ni
modèle d'application : `noyau` ne dépend d'aucune application (test_couches).
L'équivalence contre la base, avec un modèle réel, vit dans
`ressources/tests/test_intervalles_noyau.py`.
"""

import pytest

from noyau.intervalles import filtre_recouvrement, se_recouvrent

CAS = [
    pytest.param((8, 9, 9, 10), False, id="contigus-fin-egale-debut"),
    pytest.param((9, 10, 8, 9), False, id="contigus-debut-egal-fin"),
    pytest.param((9, 10, 8, 12), True, id="englobant-la-ligne"),
    pytest.param((8, 12, 9, 10), True, id="inclus-dans-la-ligne"),
    pytest.param((9, 10, 9, 10), True, id="identique"),
    pytest.param((8, 9, 10, 11), False, id="disjoint"),
    pytest.param((8, 10, 9, 11), True, id="chevauchement-partiel"),
]


@pytest.mark.parametrize("cas, attendu", CAS)
def test_le_predicat_en_memoire_donne_le_verdict_attendu(cas, attendu):
    debut_a, fin_a, debut_b, fin_b = cas
    assert se_recouvrent(debut_a, fin_a, debut_b, fin_b) is attendu


@pytest.mark.parametrize("cas, attendu", CAS)
def test_la_forme_requete_est_le_meme_predicat(cas, attendu):
    """Vérifie la forme du Q (les deux comparaisons, bornes correctes) sans base :
    l'équivalence de verdict contre la base est prouvée côté ressources."""
    debut_a, fin_a, debut_b, fin_b = cas
    requete = filtre_recouvrement("debut", "fin", debut_a, fin_a)

    assert sorted(requete.children) == [("debut__lt", fin_a), ("fin__gt", debut_a)]
    assert se_recouvrent(debut_a, fin_a, debut_b, fin_b) is attendu
