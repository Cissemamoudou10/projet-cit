# Résultats bruts — Prompt 32 § 8 (matrice v2)

**Mesuré le 2026-09-19** sur le générateur corrigé (`PROTOCOLE.md`, ajouts du
2026-09-19). Remplace la première matrice du 2026-09-18, invalidée à la revue
et archivée dans `archives/matrice-v1-2026-09-18/` (demande en lieux appliquée
au catalogue, écart de charge sur tous les instructeurs, mémoire = maximum du
processus). Tableaux bruts ; l'interprétation est dans `RECOMMANDATION.md`.

**Périmètre.** Taille RÉELLE seule : 33 brigades × 20 créneaux = **660 cases**,
100 instructeurs, 85 modules, 7 lieux partagés = **140 créneaux-lieu**. Quatre
demandes en lieux (10 / 15 / 20 / 25 % → **66 / 99 / 132 / 165** séances à lieu
à pourvoir) × trois densités de qualification (2 / 4 / 8), modules rares à
5 %, 5 instances (graines 0 à 4) : 60 instances, 180 résolutions, 0 erreur,
borne 300 s. Données brutes : `resultats_bruts.jsonl` (une ligne par
instance) ; agrégation reproductible : `scripts/agreger_resultats.py`.

**Mesure.** Conteneur `python:3.14.4-slim-bookworm`, hôte Intel Core Ultra 7
165H (16 cœurs / 22 fils), mémoire plafonnée à 16 Go. **Chaque résolution
tourne dans un processus neuf** : le pic de mémoire est celui de la
résolution ; la ligne de base (interpréteur et bibliothèques) vaut 93 Mo.

**Nombre de variables booléennes** (`PROTOCOLE.md` § 5, graine 0) : de
**11 000** (10 %, densité 2) à **32 780** (25 %, densité 8), dans la
fourchette annoncée de 10 000 à 50 000.

Cellules « méd/pire » : médiane puis pire cas des 5 instances (pour un
remplissage, le pire cas est le minimum ; pour un nombre de séances à lieu
placées, la seconde valeur est le maximum). Temps en secondes, mémoire en Mo.

## Solveur — par régime

| Demande | Densité | Régime | Statuts | 1ère sol. s (méd/pire) | Temps final s (méd/pire) | Écart optim. (méd/pire) | Remplissage (méd/pire) |
|---|---|---|---|---|---|---|---|
| 10% | 2 | SATISFACTION | OPTIMAL | 0.13/0.15 | 0.14/0.17 | — | 0.0%/0.0% |
| 10% | 2 | REMPLISSAGE | OPTIMAL | 0.31/0.31 | 1.08/1.68 | 0/0 | 100.0%/100.0% |
| 10% | 2 | EQUILIBRAGE | OPTIMAL | 0.45/0.46 | 9.68/14.15 | 0/0 | 100.0%/100.0% |
| 10% | 4 | SATISFACTION | OPTIMAL | 0.23/0.28 | 0.25/0.29 | — | 0.0%/0.0% |
| 10% | 4 | REMPLISSAGE | OPTIMAL | 0.52/0.55 | 1.44/1.94 | 0/0 | 100.0%/99.7% |
| 10% | 4 | EQUILIBRAGE | OPTIMAL | 0.99/1.00 | 4.45/5.71 | 0/0 | 100.0%/99.7% |
| 10% | 8 | SATISFACTION | OPTIMAL | 0.35/0.46 | 0.37/0.48 | — | 0.0%/0.0% |
| 10% | 8 | REMPLISSAGE | OPTIMAL | 0.88/1.00 | 2.36/2.44 | 0/0 | 100.0%/99.8% |
| 10% | 8 | EQUILIBRAGE | OPTIMAL | 2.56/2.94 | 9.93/13.13 | 0/0 | 100.0%/99.8% |
| 15% | 2 | SATISFACTION | OPTIMAL | 0.16/0.21 | 0.18/0.23 | — | 0.0%/0.0% |
| 15% | 2 | REMPLISSAGE | OPTIMAL | 0.34/0.37 | 1.69/2.31 | 0/0 | 99.1%/98.8% |
| 15% | 2 | EQUILIBRAGE | OPTIMAL | 0.48/0.51 | 13.69/21.40 | 0/0 | 99.1%/98.8% |
| 15% | 4 | SATISFACTION | OPTIMAL | 0.23/0.28 | 0.25/0.30 | — | 0.0%/0.0% |
| 15% | 4 | REMPLISSAGE | OPTIMAL | 0.47/0.53 | 1.71/1.95 | 0/0 | 99.7%/98.0% |
| 15% | 4 | EQUILIBRAGE | OPTIMAL | 0.97/1.03 | 7.65/10.36 | 0/0 | 99.7%/98.0% |
| 15% | 8 | SATISFACTION | OPTIMAL | 0.40/0.41 | 0.42/0.43 | — | 0.0%/0.0% |
| 15% | 8 | REMPLISSAGE | OPTIMAL | 0.89/1.09 | 2.59/2.61 | 0/0 | 99.5%/98.6% |
| 15% | 8 | EQUILIBRAGE | OPTIMAL | 2.56/3.21 | 16.22/51.98 | 0/0 | 99.5%/98.6% |
| 20% | 2 | SATISFACTION | OPTIMAL | 0.19/0.22 | 0.21/0.23 | — | 0.0%/0.0% |
| 20% | 2 | REMPLISSAGE | OPTIMAL | 0.31/0.35 | 1.80/2.53 | 0/0 | 96.8%/96.2% |
| 20% | 2 | EQUILIBRAGE | OPTIMAL | 0.50/0.54 | 12.55/35.01 | 0/0 | 96.8%/96.2% |
| 20% | 4 | SATISFACTION | OPTIMAL | 0.26/0.33 | 0.27/0.36 | — | 0.0%/0.0% |
| 20% | 4 | REMPLISSAGE | OPTIMAL | 0.49/0.54 | 1.71/2.21 | 0/0 | 97.3%/96.4% |
| 20% | 4 | EQUILIBRAGE | OPTIMAL | 0.98/1.11 | 5.00/8.63 | 0/0 | 97.3%/96.4% |
| 20% | 8 | SATISFACTION | OPTIMAL | 0.41/0.45 | 0.43/0.48 | — | 0.0%/0.0% |
| 20% | 8 | REMPLISSAGE | OPTIMAL | 0.91/0.93 | 2.63/3.16 | 0/0 | 96.8%/96.2% |
| 20% | 8 | EQUILIBRAGE | OPTIMAL | 2.58/2.74 | 20.14/32.06 | 0/0 | 96.8%/96.2% |
| 25% | 2 | SATISFACTION | OPTIMAL | 0.21/0.25 | 0.22/0.27 | — | 0.0%/0.0% |
| 25% | 2 | REMPLISSAGE | OPTIMAL | 0.34/0.40 | 2.18/3.80 | 0/0 | 93.9%/93.5% |
| 25% | 2 | EQUILIBRAGE | OPTIMAL | 0.49/0.50 | 21.06/26.07 | 0/0 | 93.9%/93.5% |
| 25% | 4 | SATISFACTION | OPTIMAL | 0.30/0.32 | 0.32/0.35 | — | 0.0%/0.0% |
| 25% | 4 | REMPLISSAGE | OPTIMAL | 0.50/0.61 | 1.89/2.30 | 0/0 | 93.9%/93.0% |
| 25% | 4 | EQUILIBRAGE | OPTIMAL | 1.04/1.17 | 7.26/32.64 | 0/0 | 93.9%/93.0% |
| 25% | 8 | SATISFACTION | OPTIMAL | 0.46/0.48 | 0.48/0.51 | — | 0.0%/0.0% |
| 25% | 8 | REMPLISSAGE | OPTIMAL | 0.92/0.95 | 2.51/3.40 | 0/0 | 94.4%/92.1% |
| 25% | 8 | EQUILIBRAGE | OPTIMAL | 2.67/2.89 | 12.29/24.80 | 0/0 | 94.4%/92.1% |

## Demande réelle en lieux partagés

| Demande | Densité | Séances à lieu demandées | Capacité (espaces × créneaux) | Plafond arithmétique de remplissage (lieux seuls) | Séances à lieu placées : solveur REMPL. (méd/pire) | heuristique (méd/pire) | Remplissage heuristique (méd/pire) |
|---|---|---|---|---|---|---|---|
| 10% | 2 | 66 | 140 | 100.0% | 66/66 | 66/66 | 98.0%/97.4% |
| 10% | 4 | 66 | 140 | 100.0% | 66/66 | 66/66 | 100.0%/99.7% |
| 10% | 8 | 66 | 140 | 100.0% | 66/66 | 66/66 | 100.0%/99.7% |
| 15% | 2 | 99 | 140 | 100.0% | 93/99 | 92/99 | 97.9%/97.1% |
| 15% | 4 | 99 | 140 | 100.0% | 97/99 | 93/99 | 99.1%/97.9% |
| 15% | 8 | 99 | 140 | 100.0% | 96/99 | 94/99 | 99.2%/98.6% |
| 20% | 2 | 132 | 140 | 100.0% | 111/124 | 110/124 | 96.2%/95.3% |
| 20% | 4 | 132 | 140 | 100.0% | 114/126 | 112/125 | 97.0%/96.4% |
| 20% | 8 | 132 | 140 | 100.0% | 111/127 | 109/121 | 96.5%/95.9% |
| 25% | 2 | 165 | 140 | 96.2% | 125/132 | 125/132 | 93.2%/91.7% |
| 25% | 4 | 165 | 140 | 96.2% | 125/136 | 125/135 | 93.9%/92.4% |
| 25% | 8 | 165 | 140 | 96.2% | 128/137 | 123/135 | 93.6%/91.8% |

## Équilibrage de charge — solveur contre heuristique

| Demande | Densité | Écart de charge : solveur (méd/pire) | heuristique (méd/pire) | Charge max : solveur (méd/pire) | heuristique (méd/pire) | Temps heuristique s (méd/pire) |
|---|---|---|---|---|---|---|
| 10% | 2 | 13/18 | 17/19 | 14/18 | 17/19 | 0.006/0.006 |
| 10% | 4 | 10/17 | 14/19 | 11/20 | 15/20 | 0.007/0.007 |
| 10% | 8 | 8/14 | 10/17 | 12/20 | 12/20 | 0.007/0.008 |
| 15% | 2 | 14/16 | 17/18 | 15/17 | 17/19 | 0.006/0.007 |
| 15% | 4 | 10/13 | 12/17 | 13/15 | 13/18 | 0.007/0.008 |
| 15% | 8 | 6/12 | 10/13 | 12/14 | 12/14 | 0.008/0.008 |
| 20% | 2 | 13/15 | 17/20 | 14/16 | 17/20 | 0.007/0.008 |
| 20% | 4 | 9/16 | 12/17 | 11/17 | 13/17 | 0.008/0.008 |
| 20% | 8 | 10/12 | 12/14 | 16/17 | 16/17 | 0.007/0.008 |
| 25% | 2 | 15/19 | 18/20 | 16/20 | 18/20 | 0.007/0.008 |
| 25% | 4 | 8/11 | 14/15 | 11/13 | 14/15 | 0.008/0.009 |
| 25% | 8 | 10/15 | 12/17 | 13/20 | 13/20 | 0.008/0.010 |

## Mémoire — une résolution par processus neuf

| Demande | Densité | Régime | Pic Mo (méd/pire) | Supplément vs base Mo (méd/pire) |
|---|---|---|---|---|
| 10% | 2 | SATISFACTION | 163/171 | 69/78 |
| 10% | 2 | REMPLISSAGE | 538/623 | 445/530 |
| 10% | 2 | EQUILIBRAGE | 1070/1149 | 977/1056 |
| 10% | 4 | SATISFACTION | 191/205 | 98/112 |
| 10% | 4 | REMPLISSAGE | 740/788 | 646/695 |
| 10% | 4 | EQUILIBRAGE | 1251/1315 | 1158/1222 |
| 10% | 8 | SATISFACTION | 238/270 | 144/177 |
| 10% | 8 | REMPLISSAGE | 1058/1083 | 965/990 |
| 10% | 8 | EQUILIBRAGE | 2358/2477 | 2265/2384 |
| 15% | 2 | SATISFACTION | 180/194 | 87/101 |
| 15% | 2 | REMPLISSAGE | 617/632 | 524/539 |
| 15% | 2 | EQUILIBRAGE | 1093/1189 | 999/1095 |
| 15% | 4 | SATISFACTION | 204/229 | 110/136 |
| 15% | 4 | REMPLISSAGE | 772/841 | 678/748 |
| 15% | 4 | EQUILIBRAGE | 1397/1450 | 1303/1356 |
| 15% | 8 | SATISFACTION | 253/268 | 160/174 |
| 15% | 8 | REMPLISSAGE | 1054/1102 | 961/1009 |
| 15% | 8 | EQUILIBRAGE | 2488/2883 | 2394/2790 |
| 20% | 2 | SATISFACTION | 187/214 | 94/120 |
| 20% | 2 | REMPLISSAGE | 604/671 | 510/577 |
| 20% | 2 | EQUILIBRAGE | 1072/1286 | 978/1193 |
| 20% | 4 | SATISFACTION | 224/243 | 131/150 |
| 20% | 4 | REMPLISSAGE | 775/811 | 681/717 |
| 20% | 4 | EQUILIBRAGE | 1306/1390 | 1213/1297 |
| 20% | 8 | SATISFACTION | 276/288 | 182/194 |
| 20% | 8 | REMPLISSAGE | 1121/1144 | 1028/1051 |
| 20% | 8 | EQUILIBRAGE | 2584/2765 | 2491/2672 |
| 25% | 2 | SATISFACTION | 212/220 | 118/127 |
| 25% | 2 | REMPLISSAGE | 631/716 | 538/622 |
| 25% | 2 | EQUILIBRAGE | 1191/1239 | 1098/1145 |
| 25% | 4 | SATISFACTION | 245/257 | 152/164 |
| 25% | 4 | REMPLISSAGE | 791/821 | 698/728 |
| 25% | 4 | EQUILIBRAGE | 1429/1688 | 1335/1595 |
| 25% | 8 | SATISFACTION | 313/314 | 219/221 |
| 25% | 8 | REMPLISSAGE | 1148/1179 | 1054/1085 |
| 25% | 8 | EQUILIBRAGE | 2451/2795 | 2357/2701 |


## Statistiques appariées — 60 instances, même instance pour les deux méthodes

| Grandeur | Constat |
|---|---|
| Statuts des 180 résolutions | 180 OPTIMAL, 0 FEASIBLE, 0 INFAISABLE |
| Remplissage : solveur (REMPLISSAGE) moins heuristique | jamais négatif : égal 18 fois, solveur meilleur 42 fois ; médiane +2 cases sur 660, maximum +22 cases (3,3 points) |
| Écart de charge : heuristique moins solveur (ÉQUILIBRAGE) | solveur meilleur 56 fois, égal 3 fois, **pire 1 fois** ; médiane −3 créneaux ; minimum −2, maximum +8 |
| Réduction relative de l'écart de charge | médiane 24 % ; de −29 % (1 cas défavorable) à +80 % |
| Charge maximale : heuristique moins solveur | médiane +1,5 ; minimum −7 (le solveur, qui pourvoit plus de cases, peut porter une charge maximale plus haute) ; maximum +7 |
| Première solution admissible, toutes résolutions | médiane 0,47 s ; pire cas 3,21 s |
| Temps jusqu'à la preuve d'optimalité, REMPLISSAGE | médiane 1,9 s ; pire cas 3,8 s |
| Temps jusqu'à la preuve d'optimalité, ÉQUILIBRAGE | médiane 9,8 s ; pire cas 52,0 s (densité 2 : 13,1 / 35,0 ; densité 4 : 4,8 / 32,6 ; densité 8 : 12,2 / 52,0) |
| Mémoire, REMPLISSAGE (pic) | médiane 776 Mo ; pire cas 1 179 Mo |
| Mémoire, ÉQUILIBRAGE (pic) | médiane 1 299 Mo ; pire cas 2 883 Mo (supplément à la base : 1 206 / 2 790 Mo) |

## Démonstration à contenu fixé — d'où vient l'écart de charge de l'heuristique

`scripts/diagnostic_contenu_fixe.py`, instances de la matrice, écart de charge
sur les instructeurs mobilisables. Le solveur « contenu fixé » reçoit le
contenu (quel module dans quelle case) choisi par l'heuristique et n'optimise
plus que le choix des instructeurs et des lieux.

| Combinaison | Graine | Heuristique | Solveur libre | Solveur, contenu fixé à celui de l'heuristique |
|---|---|---|---|---|
| 25 % / densité 4 | 0 | 13 | 11 | 12 |
| 25 % / densité 4 | 1 | 14 | 7 | 11 |
| 25 % / densité 4 | 2 | 13 | 8 | 11 |
| 25 % / densité 4 | 3 | 13 | 9 | 11 |
| 25 % / densité 4 | 4 | 9 | 9 | 9 |
| **médiane** | | **13** | **9** | **11** |
| 15 % / densité 8 | 0 | 12 | 8 | 9 |
| 15 % / densité 8 | 1 | 9 | 6 | 6 |
| 15 % / densité 8 | 2 | 13 | 12 | 12 |
| 15 % / densité 8 | 3 | 10 | 6 | 7 |
| 15 % / densité 8 | 4 | 5 | 1 | 4 |
| **médiane** | | **10** | **6** | **7** |

Vérification du départage de l'heuristique (`solveur/heuristique.py`,
l. 125) : `min(disponibles, key=(charge, id))` ; la charge est incrémentée à
chaque placement (`_occuper`, placements provisoires inclus) et initialisée à
zéro (aucun historique) — les deux corrections exigées à la relecture du
prompt 31 sont présentes.

## Constats bruts

**Aucune instance n'est ressortie INFAISABLE, et le modèle ne peut pas
l'être.** Toutes les contraintes dures sont des plafonds (au plus une séance
par instructeur et par créneau, au plus le programme cible, au plus le volume
prescrit, au plus la capacité du lieu) : ne rien placer les satisfait toutes.
Ce constat ne dit rien de la capacité du centre. L'effet d'une demande en
lieux supérieure à la capacité se lit dans le remplissage : médiane 100 % à
10 % de demande, 99,1-99,7 % à 15 %, 96,8-97,3 % à 20 %, 93,9-94,4 % à 25 %
(plafond arithmétique 96,2 % à 25 % pour les seuls lieux, 635/660).

**Le régime SATISFACTION rend la solution vide** (remplissage 0,0 %) : c'est
le résultat attendu d'un problème dont toutes les contraintes sont des
plafonds, non un défaut. Il est conservé pour le temps de première solution ;
il n'entre dans aucun seuil.

**Mémoire.** Les valeurs de la première matrice (143 à 4 890 Mo, monotones, 12
valeurs distinctes sur 180) étaient un maximum depuis le démarrage du
processus, pas une mesure par résolution ; elles ne sont plus citées. Les
valeurs ci-dessus sont des pics de processus neuf.
