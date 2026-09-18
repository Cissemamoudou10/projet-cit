#!/bin/sh
# Lance la matrice prioritaire (§ 4) — taille RÉELLE, 12 combinaisons, 5
# instances chacune, écrit une ligne JSON par mesure dans resultats_bruts.jsonl.
set -e
cd /etude
python scripts/executer_mesures.py --taille REELLE --instances 5 --borne-temps 300 \
  > resultats_bruts.jsonl 2> journal_execution.log
