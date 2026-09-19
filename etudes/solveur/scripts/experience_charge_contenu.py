#!/usr/bin/env python3
"""Expérience du 2026-09-19 (revue, point 3) — remesure l'écart de charge de
l'heuristique CORRIGÉE (`_poids_module`, charge dans le choix de la matière)
sur les 60 instances de `resultats_bruts.jsonl`, régénérées à l'identique
(vérifié par empreinte) — même instance, même écart de charge du solveur déjà
enregistré, comparaison appariée sans relancer le solveur.

Usage : python scripts/experience_charge_contenu.py [resultats_bruts.jsonl]
"""

import json
import statistics
import sys

sys.path.insert(0, ".")

from solveur.generateur import ParametresInstance, generer
from solveur.instance import DUREE_CRENEAU_HEURES
from solveur.mesures import mesurer_heuristique

CHEMIN = sys.argv[1] if len(sys.argv) > 1 else "resultats_bruts.jsonl"
lignes = [json.loads(l) for l in open(CHEMIN, encoding="utf-8")]

ecarts_avant, ecarts_apres, ecarts_solveur = [], [], []
divergences_empreinte = 0

for ligne in lignes:
    c = ligne["combinaison"]
    instance = generer(ParametresInstance(**c, graine=ligne["graine"]))
    if instance.empreinte() != ligne["empreinte_instance"]:
        divergences_empreinte += 1
        continue
    nouvelle = mesurer_heuristique(instance, DUREE_CRENEAU_HEURES)
    ecarts_avant.append(ligne["heuristique"]["ecart_charge"])
    ecarts_apres.append(nouvelle.ecart_charge)
    ecarts_solveur.append(ligne["solveur_EQUILIBRAGE"]["ecart_charge"])

assert divergences_empreinte == 0, f"{divergences_empreinte} instances non reproduites à l'identique"

print(f"{len(lignes)} instances, toutes reproduites à l'identique (même empreinte)")
print(
    f"écart heuristique — AVANT (règle d'origine)  : médiane {statistics.median(ecarts_avant)}, "
    f"pire {max(ecarts_avant)}, meilleur {min(ecarts_avant)}"
)
print(
    f"écart heuristique — APRÈS (charge dans le contenu) : médiane "
    f"{statistics.median(ecarts_apres)}, pire {max(ecarts_apres)}, meilleur {min(ecarts_apres)}"
)
print(f"écart solveur (ÉQUILIBRAGE, inchangé) : médiane {statistics.median(ecarts_solveur)}")

gains = [a - b for a, b in zip(ecarts_avant, ecarts_apres, strict=True)]
print(
    f"gain (avant - après) : médiane {statistics.median(gains)}, min {min(gains)}, "
    f"max {max(gains)} ; heuristique dégradée sur {sum(1 for g in gains if g < 0)}/{len(gains)} instances"
)
ecart_reste = [b - s for b, s in zip(ecarts_apres, ecarts_solveur, strict=True)]
print(
    f"écart restant à combler face au solveur (après - solveur) : médiane "
    f"{statistics.median(ecart_reste)}, min {min(ecart_reste)}, max {max(ecart_reste)} ; "
    f"heuristique égale ou meilleure que le solveur sur {sum(1 for x in ecart_reste if x <= 0)}/{len(ecart_reste)}"
)
