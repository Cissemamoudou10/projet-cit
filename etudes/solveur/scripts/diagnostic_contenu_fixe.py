#!/usr/bin/env python3
"""Décompose l'écart de charge de l'heuristique — revue du 2026-09-18, point 2.

Trois mesures sur la MÊME instance, sur les instructeurs mobilisables :
  1. l'heuristique ;
  2. le solveur en régime ÉQUILIBRAGE, libre (contenu ET instructeurs) ;
  3. le solveur ÉQUILIBRAGE avec le CONTENU FIXÉ à celui de l'heuristique
     (quel module dans quelle case) : il n'optimise plus que le choix des
     instructeurs et des lieux.

Si (3) ≈ (1), le départage par charge de l'heuristique est optimal à contenu
donné : l'écart est dû au CONTENU (règle « le plus difficile d'abord »), pas à
un départage défaillant. Si (3) << (1), le départage perd réellement.

Usage : python scripts/diagnostic_contenu_fixe.py [--demande 0.25] [--densite 4] [--graines 0 1 2]
"""

import argparse
import statistics
import sys

sys.path.insert(0, ".")

from ortools.sat.python import cp_model
from solveur.generateur import ParametresInstance, generer
from solveur.heuristique import generer as generer_heuristique
from solveur.instance import DUREE_CRENEAU_HEURES
from solveur.modele import REGIME_EQUILIBRAGE, configurer_objectif, construire, resoudre
from solveur.preparation import modules_programmables

BORNE_TEMPS_SECONDES = 120


def _ecart_et_max(charges):
    return max(charges) - min(charges), max(charges)


def _charges_heuristique(instance, placements, mobilisables):
    charge = dict.fromkeys(mobilisables, 0)
    for _b, _c, _m, instructeur_id, _l in placements:
        charge[instructeur_id] += 1
    return list(charge.values())


def _solveur_contenu_fixe(instance, placements):
    modele, variables = construire(instance)
    fixes = {(b, c, m) for b, c, m, _i, _l in placements}
    for cle, var in variables.x.items():
        modele.Add(var == (1 if cle in fixes else 0))
    configurer_objectif(modele, variables, REGIME_EQUILIBRAGE)
    solveur = cp_model.CpSolver()
    solveur.parameters.max_time_in_seconds = BORNE_TEMPS_SECONDES
    statut = solveur.Solve(modele)
    return solveur.StatusName(statut), [solveur.Value(v) for v in variables.charge.values()]


def _une_graine(demande, densite, graine):
    instance = generer(ParametresInstance("REELLE", demande, densite, 0.05, graine))
    mobilisables = modules_programmables(instance).mobilisables
    placements = generer_heuristique(instance, DUREE_CRENEAU_HEURES).placements

    heur = _ecart_et_max(_charges_heuristique(instance, placements, mobilisables))

    modele, variables = construire(instance)
    solveur, statut = resoudre(modele, variables, REGIME_EQUILIBRAGE, BORNE_TEMPS_SECONDES)
    libre = _ecart_et_max([solveur.Value(v) for v in variables.charge.values()])

    statut_fixe, charges_fixe = _solveur_contenu_fixe(instance, placements)
    fixe = _ecart_et_max(charges_fixe)
    return heur, libre, fixe, solveur.StatusName(statut), statut_fixe, len(mobilisables)


if __name__ == "__main__":
    parseur = argparse.ArgumentParser(description=__doc__)
    parseur.add_argument("--demande", type=float, default=0.25)
    parseur.add_argument("--densite", type=int, default=4)
    parseur.add_argument("--graines", type=int, nargs="+", default=[0, 1, 2, 3, 4])
    args = parseur.parse_args()

    lignes = [_une_graine(args.demande, args.densite, g) for g in args.graines]
    print(
        f"demande={args.demande:.0%} densite={args.densite} — (écart, charge max) sur mobilisables"
    )
    print("graine | heuristique | solveur libre | solveur contenu FIXÉ (heuristique) | statuts")
    for graine, (heur, libre, fixe, st_libre, st_fixe, n) in zip(
        args.graines, lignes, strict=False
    ):
        print(f"{graine:6d} | {heur} | {libre} | {fixe} | {st_libre}/{st_fixe} ({n} mobilisables)")
    for nom, i in (("heuristique", 0), ("solveur libre", 1), ("contenu fixé", 2)):
        print(f"médiane écart {nom}: {statistics.median(ligne[i][0] for ligne in lignes)}")
