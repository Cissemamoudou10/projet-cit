#!/usr/bin/env python3
"""Script d'exécution de la matrice de mesures — Prompt 32 § 4/§ 8.

Usage :
    python scripts/executer_mesures.py --taille REELLE --instances 5

Écrit un JSON brut (une ligne par mesure) sur la sortie standard — la mise
en forme MÉDIANE/PIRE CAS pour `RESULTATS.md` (§ 8) est un traitement
séparé, volontairement : ce script ne fait QUE mesurer.
"""

import argparse
import itertools
import json
import sys

sys.path.insert(0, ".")

from solveur.generateur import ParametresInstance, generer
from solveur.mesures import mesurer_heuristique, mesurer_solveur
from solveur.modele import (
    DUREE_CRENEAU_HEURES,
    REGIME_EQUILIBRAGE,
    REGIME_REMPLISSAGE,
    REGIME_SATISFACTION,
)

REGIMES = [REGIME_SATISFACTION, REGIME_REMPLISSAGE, REGIME_EQUILIBRAGE]

# § 4 : priorité à la taille RÉELLE sur les quatre demandes de lieux et les
# trois densités de qualification (fraction de modules rares fixée à 5 % —
# le confort des 15 % croisées vient ensuite si le temps le permet).
DEMANDES_LIEUX_PARTAGES = [0.10, 0.15, 0.20, 0.25]
DENSITES_QUALIFICATION = [2, 4, 8]
FRACTION_MODULES_RARES_PRIORITAIRE = 0.05


def _combinaisons_prioritaires(taille):
    for demande, densite in itertools.product(DEMANDES_LIEUX_PARTAGES, DENSITES_QUALIFICATION):
        yield dict(
            taille=taille,
            demande_lieux_partages=demande,
            densite_qualification=densite,
            fraction_modules_rares=FRACTION_MODULES_RARES_PRIORITAIRE,
        )


def _mesurer_une_instance(combinaison, graine, borne_temps_secondes):
    parametres = ParametresInstance(**combinaison, graine=graine)
    instance = generer(parametres)

    resultat = {"combinaison": combinaison, "graine": graine}
    for regime in REGIMES:
        mesure = mesurer_solveur(instance, regime, borne_temps_secondes)
        resultat[f"solveur_{regime}"] = _dataclass_en_dict(mesure)
    resultat["heuristique"] = _dataclass_en_dict(
        mesurer_heuristique(instance, DUREE_CRENEAU_HEURES)
    )
    return resultat


def _dataclass_en_dict(objet):
    import dataclasses

    return dataclasses.asdict(objet)


def executer(taille, nb_instances, borne_temps_secondes):
    for combinaison in _combinaisons_prioritaires(taille):
        for graine in range(nb_instances):
            resultat = _mesurer_une_instance(combinaison, graine, borne_temps_secondes)
            print(json.dumps(resultat, ensure_ascii=False))
            sys.stdout.flush()


def _arguments():
    parseur = argparse.ArgumentParser(description=__doc__)
    parseur.add_argument("--taille", default="REELLE", choices=["CONTROLE", "REELLE", "HAUTE"])
    parseur.add_argument("--instances", type=int, default=5)
    parseur.add_argument("--borne-temps", type=int, default=300, help="secondes, BNF-04 = 300")
    return parseur.parse_args()


if __name__ == "__main__":
    args = _arguments()
    executer(args.taille, args.instances, args.borne_temps)
