#!/usr/bin/env python3
"""Expérience du 2026-09-19 (revue, point 4) — sensibilité au nombre de fils
(`num_search_workers`). Toutes les mesures de `resultats_bruts.jsonl` ont été
prises sur 22 fils (hôte de développement) ; le serveur cible en aura quatre
ou huit — le facteur de prudence ×3 (`PROTOCOLE.md` § 7) couvre la fréquence
par cœur, pas la perte de parallélisme, qui est un axe différent.

Rejoue la combinaison la plus lourde de la matrice (25 % / densité 8, graine 0
— 119,4 s à 22 fils, le pire cas de `RESULTATS.md`), régime ÉQUILIBRAGE, avec
`num_search_workers` à 4 puis 8, une résolution par processus neuf (mémoire
isolée, comme `executer_mesures.py`).

Usage : python scripts/mesure_parallelisme.py
"""

import multiprocessing
import sys

sys.path.insert(0, ".")

from ortools.sat.python import cp_model

from solveur.generateur import ParametresInstance, generer
from solveur.mesures import memoire_max_ko
from solveur.modele import REGIME_EQUILIBRAGE, configurer_objectif, construire

COMBINAISON = dict(taille="REELLE", demande_lieux_partages=0.25, densite_qualification=8,
                    fraction_modules_rares=0.05, graine=0)
BORNE_TEMPS_SECONDES = 300


def _resoudre_avec_n_fils(nb_fils):
    baseline_ko = memoire_max_ko()
    instance = generer(ParametresInstance(**COMBINAISON))
    modele, variables = construire(instance)
    configurer_objectif(modele, variables, REGIME_EQUILIBRAGE)
    solveur = cp_model.CpSolver()
    solveur.parameters.max_time_in_seconds = BORNE_TEMPS_SECONDES
    solveur.parameters.num_search_workers = nb_fils
    statut = solveur.Solve(modele)
    return {
        "nb_fils": nb_fils,
        "statut": solveur.StatusName(statut),
        "temps_final": solveur.WallTime(),
        "ecart_charge": (
            max(solveur.Value(v) for v in variables.charge.values())
            - min(solveur.Value(v) for v in variables.charge.values())
        ),
        "memoire_pic_ko": memoire_max_ko(),
        "memoire_supplement_ko": memoire_max_ko() - baseline_ko,
    }


def _dans_un_processus_neuf(nb_fils):
    contexte = multiprocessing.get_context("spawn")
    with contexte.Pool(processes=1) as pool:
        return pool.apply(_resoudre_avec_n_fils, (nb_fils,))


if __name__ == "__main__":
    print(f"Combinaison la plus lourde : {COMBINAISON} — régime ÉQUILIBRAGE")
    for nb_fils in (22, 8, 4):
        r = _dans_un_processus_neuf(nb_fils)
        print(
            f"fils={r['nb_fils']:2d} statut={r['statut']:9s} temps={r['temps_final']:7.1f}s "
            f"ecart_charge={r['ecart_charge']:2d} memoire_pic={r['memoire_pic_ko']/1024:7.0f}Mo "
            f"supplement={r['memoire_supplement_ko']/1024:7.0f}Mo"
        )
