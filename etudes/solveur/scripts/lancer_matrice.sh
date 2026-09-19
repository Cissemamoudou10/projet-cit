#!/bin/sh
# Lance la matrice prioritaire (§ 4) — taille RÉELLE, 12 combinaisons, 5
# instances chacune, une résolution par processus neuf. Écrit une ligne JSON
# par instance dans resultats_bruts.jsonl (suivi possible en direct).
set -e
cd /etude
python scripts/executer_mesures.py --taille REELLE --instances 5 --borne-temps 300 \
  > resultats_bruts.jsonl 2> journal_execution.log
