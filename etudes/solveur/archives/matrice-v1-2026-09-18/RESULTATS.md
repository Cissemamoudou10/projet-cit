# Résultats bruts — Prompt 32 § 8

**Mesuré le 2026-09-18.** Tableau brut, sans interprétation (l'interprétation
et la recommandation sont dans `RECOMMANDATION.md`). Protocole : voir
`PROTOCOLE.md`.

Matrice priorisée du § 4 : taille RÉELLE seule, 4 valeurs de demande en
lieux partagés (10 %, 15 %, 20 %, 25 %) × 3 densités de qualification
(2, 4, 8), fraction de modules rares fixée à 5 % — 12 combinaisons, 5
instances chacune, **60 instances mesurées, 0 erreur**. Graines 0 à 4,
consignées dans `resultats_bruts.jsonl` (une ligne JSON par instance, tous
les champs bruts).

**Nombre de variables booléennes du modèle** (`PROTOCOLE.md` § 5, engagement
tenu ici) : de **10 480** (demande 10 %, densité 2) à **32 840** (demande
25 %, densité 8) sur les 12 combinaisons de la matrice — dans la fourchette
annoncée de 10 000 à 50 000, aucun signal de formulation inefficace.

Chaque cellule « méd/pire » : médiane puis pire cas des 5 instances. Temps
en secondes, mémoire en mégaoctets. Machine de mesure et facteur de
prudence : voir `PROTOCOLE.md` § 7/§ 8.

| Demande lieux | Densité qualif. | Régime | Statuts | 1ère sol. (méd/pire) | Temps final (méd/pire) | Écart optim. (méd/pire) | Remplissage (méd/pire) | Écart charge (méd/pire) | Mémoire Mo (méd/pire) |
|---|---|---|---|---|---|---|---|---|---|
| 10% | 2 | SATISFACTION | OPTIMAL | 0.15/0.21 | 0.16/0.23 | — | 0.3%/0.3% | — | 1060/1060 |
| 10% | 2 | REMPLISSAGE | OPTIMAL | 0.47/0.58 | 0.61/0.81 | 0/0 | 100.0%/100.0% | — | 1060/1060 |
| 10% | 2 | EQUILIBRAGE | OPTIMAL | 0.56/0.60 | 12.61/24.38 | 0/0 | 100.0%/100.0% | 9/9 | 1060/1065 |
| 10% | 2 | HEURISTIQUE | — | — | 0.008/0.009 | — | 100.0%/100.0% | 17/18 | — |
| 10% | 4 | SATISFACTION | OPTIMAL | 0.20/0.31 | 0.21/0.33 | — | 0.3%/0.2% | — | 1112/1142 |
| 10% | 4 | REMPLISSAGE | OPTIMAL | 0.77/0.85 | 1.01/1.07 | 0/0 | 100.0%/100.0% | — | 1112/1142 |
| 10% | 4 | EQUILIBRAGE | OPTIMAL | 1.04/1.22 | 3.26/3.61 | 0/0 | 100.0%/100.0% | 7/8 | 1112/1142 |
| 10% | 4 | HEURISTIQUE | — | — | 0.010/0.013 | — | 100.0%/100.0% | 19/19 | — |
| 10% | 8 | SATISFACTION | OPTIMAL | 0.33/0.49 | 0.35/0.51 | — | 0.2%/0.2% | — | 3812/3812 |
| 10% | 8 | REMPLISSAGE | OPTIMAL | 1.34/1.40 | 1.69/1.88 | 0/0 | 100.0%/100.0% | — | 3812/3812 |
| 10% | 8 | EQUILIBRAGE | OPTIMAL | 4.31/4.53 | 22.33/251.37 | 0/0 | 100.0%/100.0% | 1/7 | 3812/3812 |
| 10% | 8 | HEURISTIQUE | — | — | 0.016/0.017 | — | 100.0%/99.2% | 17/18 | — |
| 15% | 2 | SATISFACTION | OPTIMAL | 0.23/0.34 | 0.24/0.36 | — | 0.5%/0.2% | — | 3812/3812 |
| 15% | 2 | REMPLISSAGE | OPTIMAL | 0.50/0.54 | 0.65/0.67 | 0/0 | 100.0%/100.0% | — | 3812/3812 |
| 15% | 2 | EQUILIBRAGE | OPTIMAL | 0.62/0.86 | 12.40/22.67 | 0/0 | 100.0%/100.0% | 9/9 | 3812/3812 |
| 15% | 2 | HEURISTIQUE | — | — | 0.009/0.010 | — | 100.0%/98.6% | 18/19 | — |
| 15% | 4 | SATISFACTION | OPTIMAL | 0.29/0.36 | 0.31/0.38 | — | 0.2%/0.0% | — | 3812/3812 |
| 15% | 4 | REMPLISSAGE | OPTIMAL | 0.77/0.98 | 0.92/1.22 | 0/0 | 100.0%/100.0% | — | 3812/3812 |
| 15% | 4 | EQUILIBRAGE | OPTIMAL | 1.13/1.13 | 3.25/4.07 | 0/0 | 100.0%/100.0% | 7/8 | 3812/3812 |
| 15% | 4 | HEURISTIQUE | — | — | 0.011/0.014 | — | 100.0%/98.8% | 17/17 | — |
| 15% | 8 | SATISFACTION | OPTIMAL | 0.48/0.51 | 0.50/0.54 | — | 0.2%/0.0% | — | 3812/3812 |
| 15% | 8 | REMPLISSAGE | OPTIMAL | 1.30/1.36 | 1.69/2.97 | 0/0 | 100.0%/100.0% | — | 3812/3812 |
| 15% | 8 | EQUILIBRAGE | OPTIMAL | 4.61/5.04 | 16.71/32.35 | 0/0 | 100.0%/100.0% | 1/7 | 3812/3812 |
| 15% | 8 | HEURISTIQUE | — | — | 0.015/0.016 | — | 100.0%/99.4% | 16/18 | — |
| 20% | 2 | SATISFACTION | OPTIMAL | 0.25/0.28 | 0.26/0.29 | — | 0.3%/0.0% | — | 3812/3812 |
| 20% | 2 | REMPLISSAGE | OPTIMAL | 0.53/0.64 | 0.72/0.95 | 0/0 | 100.0%/100.0% | — | 3812/3812 |
| 20% | 2 | EQUILIBRAGE | OPTIMAL | 0.69/0.82 | 18.20/35.59 | 0/0 | 100.0%/100.0% | 9/9 | 3812/3812 |
| 20% | 2 | HEURISTIQUE | — | — | 0.010/0.011 | — | 100.0%/97.6% | 16/18 | — |
| 20% | 4 | SATISFACTION | OPTIMAL | 0.32/0.42 | 0.33/0.44 | — | 0.2%/0.0% | — | 3812/3812 |
| 20% | 4 | REMPLISSAGE | OPTIMAL | 0.76/0.78 | 0.95/1.04 | 0/0 | 100.0%/100.0% | — | 3812/3812 |
| 20% | 4 | EQUILIBRAGE | OPTIMAL | 0.97/1.07 | 4.49/19.53 | 0/0 | 100.0%/100.0% | 7/8 | 3812/3812 |
| 20% | 4 | HEURISTIQUE | — | — | 0.011/0.012 | — | 100.0%/97.1% | 17/18 | — |
| 20% | 8 | SATISFACTION | OPTIMAL | 0.48/0.71 | 0.51/0.74 | — | 0.2%/0.0% | — | 4071/4071 |
| 20% | 8 | REMPLISSAGE | OPTIMAL | 1.42/1.50 | 1.83/2.00 | 0/0 | 100.0%/100.0% | — | 4071/4071 |
| 20% | 8 | EQUILIBRAGE | FEASIBLE,OPTIMAL | 4.78/5.09 | 207.71/300.22 | 0/1 | 100.0%/100.0% | 1/7 | 4071/4071 |
| 20% | 8 | HEURISTIQUE | — | — | 0.016/0.019 | — | 100.0%/98.0% | 17/19 | — |
| 25% | 2 | SATISFACTION | OPTIMAL | 0.25/0.28 | 0.26/0.30 | — | 0.2%/0.0% | — | 4071/4071 |
| 25% | 2 | REMPLISSAGE | OPTIMAL | 0.61/0.67 | 0.77/2.05 | 0/0 | 100.0%/100.0% | — | 4071/4071 |
| 25% | 2 | EQUILIBRAGE | OPTIMAL | 0.68/0.75 | 19.73/42.96 | 0/0 | 100.0%/100.0% | 9/9 | 4071/4071 |
| 25% | 2 | HEURISTIQUE | — | — | 0.010/0.012 | — | 99.2%/97.7% | 18/18 | — |
| 25% | 4 | SATISFACTION | OPTIMAL | 0.43/0.48 | 0.44/0.51 | — | 0.0%/0.0% | — | 4071/4071 |
| 25% | 4 | REMPLISSAGE | OPTIMAL | 0.82/0.99 | 1.19/2.16 | 0/0 | 100.0%/100.0% | — | 4071/4071 |
| 25% | 4 | EQUILIBRAGE | OPTIMAL | 1.09/1.28 | 3.59/120.45 | 0/0 | 100.0%/100.0% | 7/8 | 4071/4071 |
| 25% | 4 | HEURISTIQUE | — | — | 0.011/0.019 | — | 98.9%/98.3% | 17/19 | — |
| 25% | 8 | SATISFACTION | OPTIMAL | 0.51/0.70 | 0.54/0.72 | — | 0.2%/0.0% | — | 4890/4890 |
| 25% | 8 | REMPLISSAGE | OPTIMAL | 1.43/1.48 | 2.06/2.91 | 0/0 | 100.0%/100.0% | — | 4890/4890 |
| 25% | 8 | EQUILIBRAGE | FEASIBLE,OPTIMAL | 4.43/5.01 | 23.98/300.26 | 0/1 | 100.0%/100.0% | 1/7 | 4890/4890 |
| 25% | 8 | HEURISTIQUE | — | — | 0.017/0.022 | — | 100.0%/97.4% | 16/18 | — |

## Constat brut à signaler avant toute interprétation

**Aucune instance n'est ressortie INFAISABLE**, y compris à 25 % de demande
en lieux partagés — alors que `PROTOCOLE.md` § 4 (reprenant le prompt)
anticipait que ce seuil « dépasse probablement la capacité ». Constaté, pas
corrigé rétroactivement dans `HYPOTHESES.md` (règle absolue de ce fichier) :
si une hypothèse se révèle fausse, ça se traite par recommandation, pas par
réécriture de l'hypothèse.

Trois instances (deux à 20 %/densité 8, une à 25 %/densité 8) ont atteint
la borne de 300 s sur le régime ÉQUILIBRAGE sans preuve d'optimalité
(statut FEASIBLE, écart d'optimalité résiduel de 1) — la solution restait
néanmoins à 100 % de remplissage.
