#!/usr/bin/env python3
"""Script d'exécution de la matrice de mesures — Prompt 32 § 4/§ 8.

Usage :
    python scripts/executer_mesures.py --taille REELLE --instances 5
    python scripts/executer_mesures.py --taille REELLE --instances 1 \
        --demandes 0.25 --densites 8          # sous-ensemble

Écrit un JSON brut (une ligne par instance) sur la sortie standard — la mise
en forme MÉDIANE/PIRE CAS pour `RESULTATS.md` (§ 8) est un traitement séparé
(`scripts/agreger_resultats.py`) : ce script ne fait QUE mesurer.

CHAQUE RÉSOLUTION TOURNE DANS UN PROCESSUS NEUF (`spawn`). Le pic de mémoire
d'un processus (`ru_maxrss`) est un maximum depuis son démarrage : mesuré
dans un processus qui enchaîne toutes les résolutions, il est monotone et ne
dit rien d'une résolution en particulier — défaut de la première matrice,
constaté à la revue du 2026-09-18. Ici le pic d'un processus neuf EST celui
de la résolution (instance, modèle et solveur compris), et la ligne de base
(après import, avant instance) permet d'en retrancher l'interpréteur.
"""

import argparse
import dataclasses
import itertools
import json
import multiprocessing
import sys

sys.path.insert(0, ".")

from solveur.generateur import ParametresInstance, generer
from solveur.instance import DUREE_CRENEAU_HEURES
from solveur.mesures import memoire_max_ko, mesurer_heuristique, mesurer_solveur
from solveur.modele import REGIME_EQUILIBRAGE, REGIME_REMPLISSAGE, REGIME_SATISFACTION

REGIMES = [REGIME_SATISFACTION, REGIME_REMPLISSAGE, REGIME_EQUILIBRAGE]

# § 4 : priorité à la taille RÉELLE sur les quatre demandes de lieux et les
# trois densités de qualification (fraction de modules rares fixée à 5 % —
# le confort des 15 % croisées vient ensuite si le temps le permet).
DEMANDES_LIEUX_PARTAGES = [0.10, 0.15, 0.20, 0.25]
DENSITES_QUALIFICATION = [2, 4, 8]
FRACTION_MODULES_RARES_PRIORITAIRE = 0.05


def _combinaisons_prioritaires(taille, demandes, densites):
    for demande, densite in itertools.product(demandes, densites):
        yield dict(
            taille=taille,
            demande_lieux_partages=demande,
            densite_qualification=densite,
            fraction_modules_rares=FRACTION_MODULES_RARES_PRIORITAIRE,
        )


def _mesurer_regime_isole(combinaison, graine, regime, borne_temps_secondes):
    """Exécutée dans un processus NEUF — voir la docstring du module."""
    baseline_ko = memoire_max_ko()
    instance = generer(ParametresInstance(**combinaison, graine=graine))
    mesure = mesurer_solveur(instance, regime, borne_temps_secondes)
    return dataclasses.replace(mesure, memoire_baseline_ko=baseline_ko)


def _mesurer_dans_un_processus_neuf(combinaison, graine, regime, borne_temps_secondes):
    contexte = multiprocessing.get_context("spawn")
    with contexte.Pool(processes=1) as pool:
        return pool.apply(
            _mesurer_regime_isole, (combinaison, graine, regime, borne_temps_secondes)
        )


def _mesurer_une_instance(combinaison, graine, borne_temps_secondes):
    instance = generer(ParametresInstance(**combinaison, graine=graine))
    resultat = {
        "combinaison": combinaison,
        "graine": graine,
        "meta_instance": instance.meta,
        "capacite_lieux_partages": len(instance.lieux_partages) * len(instance.creneaux),
    }
    resultat["empreinte_instance"] = instance.empreinte()
    for regime in REGIMES:
        mesure = _mesurer_dans_un_processus_neuf(combinaison, graine, regime, borne_temps_secondes)
        if mesure.empreinte_instance != resultat["empreinte_instance"]:
            raise RuntimeError(
                f"Instance différente entre le processus parent et le processus du régime "
                f"{regime} ({combinaison}, graine {graine}) : les mesures ne portent pas sur "
                "le même problème."
            )
        resultat[f"solveur_{regime}"] = dataclasses.asdict(mesure)
    resultat["heuristique"] = dataclasses.asdict(
        mesurer_heuristique(instance, DUREE_CRENEAU_HEURES)
    )
    return resultat


def executer(taille, nb_instances, borne_temps_secondes, demandes, densites):
    for combinaison in _combinaisons_prioritaires(taille, demandes, densites):
        for graine in range(nb_instances):
            resultat = _mesurer_une_instance(combinaison, graine, borne_temps_secondes)
            print(json.dumps(resultat, ensure_ascii=False))
            sys.stdout.flush()


def _arguments():
    parseur = argparse.ArgumentParser(description=__doc__)
    parseur.add_argument("--taille", default="REELLE", choices=["CONTROLE", "REELLE", "HAUTE"])
    parseur.add_argument("--instances", type=int, default=5)
    parseur.add_argument("--borne-temps", type=int, default=300, help="secondes, BNF-04 = 300")
    parseur.add_argument("--demandes", type=float, nargs="+", default=DEMANDES_LIEUX_PARTAGES)
    parseur.add_argument("--densites", type=int, nargs="+", default=DENSITES_QUALIFICATION)
    return parseur.parse_args()


if __name__ == "__main__":
    args = _arguments()
    executer(args.taille, args.instances, args.borne_temps, args.demandes, args.densites)
