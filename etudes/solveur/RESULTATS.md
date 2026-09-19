# Résultats bruts — Prompt 32 § 8 (matrice v3)

**Mesuré le 2026-09-19** sur le générateur corrigé (`PROTOCOLE.md`, ajouts du
2026-09-19). Remplace deux matrices antérieures, toutes deux archivées et non
citées : la v1 du 2026-09-18 (demande en lieux appliquée au catalogue, écart de
charge sur tous les instructeurs, mémoire = maximum du processus ;
`archives/matrice-v1-2026-09-18/`) et la v2 du 2026-09-19 (instances
différentes d'un processus à l'autre, donc comparaisons non appariées ;
`archives/matrice-v2-non-appariee-2026-09-19/`). Tableaux bruts ;
l'interprétation est dans `RECOMMANDATION.md`.

**Périmètre.** Taille RÉELLE seule : 33 brigades × 20 créneaux = **660 cases**,
100 instructeurs, 85 modules, 7 lieux partagés = **140 créneaux-lieu**. Quatre
demandes en lieux (10 / 15 / 20 / 25 % → **66 / 99 / 132 / 165** séances à lieu
à pourvoir) × trois densités de qualification (2 / 4 / 8), modules rares à
5 %, 5 instances (graines 0 à 4) : 60 instances, 180 résolutions, 0 erreur,
borne 300 s. Données brutes : `resultats_bruts.jsonl` (une ligne par
instance) ; agrégation reproductible : `scripts/agreger_resultats.py`.

**Intégrité.** Chaque ligne porte l'empreinte de son instance
(`Instance.empreinte()`). Les 60 empreintes sont distinctes ; **les 180
résolutions ont exactement l'empreinte de l'instance mesurée par l'heuristique**
(le script s'arrête sinon). Comparaison de cohérence : sur les 60 instances,
ÉQUILIBRAGE et REMPLISSAGE pourvoient exactement le même nombre de cases.

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
| 10% | 2 | SATISFACTION | OPTIMAL | 0.12/0.18 | 0.13/0.20 | — | 0.0%/0.0% |
| 10% | 2 | REMPLISSAGE | OPTIMAL | 0.29/0.33 | 1.70/2.04 | 0/0 | 100.0%/100.0% |
| 10% | 2 | EQUILIBRAGE | OPTIMAL | 0.44/0.50 | 11.67/14.58 | 0/0 | 100.0%/100.0% |
| 10% | 4 | SATISFACTION | OPTIMAL | 0.24/0.28 | 0.25/0.29 | — | 0.0%/0.0% |
| 10% | 4 | REMPLISSAGE | OPTIMAL | 0.47/0.49 | 1.40/1.55 | 0/0 | 100.0%/99.7% |
| 10% | 4 | EQUILIBRAGE | OPTIMAL | 0.96/1.02 | 6.21/19.29 | 0/0 | 100.0%/99.7% |
| 10% | 8 | SATISFACTION | OPTIMAL | 0.39/0.43 | 0.41/0.44 | — | 0.0%/0.0% |
| 10% | 8 | REMPLISSAGE | OPTIMAL | 0.88/0.93 | 2.04/2.76 | 0/0 | 100.0%/99.8% |
| 10% | 8 | EQUILIBRAGE | OPTIMAL | 2.54/2.60 | 12.66/18.97 | 0/0 | 100.0%/99.8% |
| 15% | 2 | SATISFACTION | OPTIMAL | 0.16/0.21 | 0.17/0.23 | — | 0.0%/0.0% |
| 15% | 2 | REMPLISSAGE | OPTIMAL | 0.32/0.33 | 1.73/2.54 | 0/0 | 99.1%/98.8% |
| 15% | 2 | EQUILIBRAGE | OPTIMAL | 0.49/0.51 | 10.46/15.98 | 0/0 | 99.1%/98.8% |
| 15% | 4 | SATISFACTION | OPTIMAL | 0.23/0.29 | 0.25/0.30 | — | 0.0%/0.0% |
| 15% | 4 | REMPLISSAGE | OPTIMAL | 0.48/0.51 | 1.62/1.94 | 0/0 | 99.7%/98.0% |
| 15% | 4 | EQUILIBRAGE | OPTIMAL | 0.97/1.05 | 4.94/23.22 | 0/0 | 99.7%/98.0% |
| 15% | 8 | SATISFACTION | OPTIMAL | 0.38/0.41 | 0.39/0.44 | — | 0.0%/0.0% |
| 15% | 8 | REMPLISSAGE | OPTIMAL | 0.81/0.88 | 2.43/2.63 | 0/0 | 99.5%/98.6% |
| 15% | 8 | EQUILIBRAGE | OPTIMAL | 2.57/2.62 | 18.88/25.08 | 0/0 | 99.5%/98.6% |
| 20% | 2 | SATISFACTION | OPTIMAL | 0.17/0.21 | 0.19/0.22 | — | 0.0%/0.0% |
| 20% | 2 | REMPLISSAGE | OPTIMAL | 0.32/0.36 | 1.52/1.70 | 0/0 | 96.8%/96.2% |
| 20% | 2 | EQUILIBRAGE | OPTIMAL | 0.44/0.48 | 6.20/19.28 | 0/0 | 96.8%/96.2% |
| 20% | 4 | SATISFACTION | OPTIMAL | 0.26/0.31 | 0.28/0.33 | — | 0.0%/0.0% |
| 20% | 4 | REMPLISSAGE | OPTIMAL | 0.51/0.54 | 1.84/2.34 | 0/0 | 97.3%/96.4% |
| 20% | 4 | EQUILIBRAGE | OPTIMAL | 0.99/1.03 | 6.29/7.04 | 0/0 | 97.3%/96.4% |
| 20% | 8 | SATISFACTION | OPTIMAL | 0.44/0.49 | 0.46/0.52 | — | 0.0%/0.0% |
| 20% | 8 | REMPLISSAGE | OPTIMAL | 0.89/1.00 | 2.54/3.24 | 0/0 | 96.8%/96.2% |
| 20% | 8 | EQUILIBRAGE | OPTIMAL | 2.61/2.78 | 18.63/22.51 | 0/0 | 96.8%/96.2% |
| 25% | 2 | SATISFACTION | OPTIMAL | 0.21/0.22 | 0.22/0.23 | — | 0.0%/0.0% |
| 25% | 2 | REMPLISSAGE | OPTIMAL | 0.32/0.34 | 1.81/4.26 | 0/0 | 93.9%/93.5% |
| 25% | 2 | EQUILIBRAGE | OPTIMAL | 0.49/0.50 | 10.58/22.67 | 0/0 | 93.9%/93.5% |
| 25% | 4 | SATISFACTION | OPTIMAL | 0.30/0.34 | 0.32/0.38 | — | 0.0%/0.0% |
| 25% | 4 | REMPLISSAGE | OPTIMAL | 0.49/0.58 | 1.71/2.06 | 0/0 | 93.9%/93.0% |
| 25% | 4 | EQUILIBRAGE | OPTIMAL | 1.06/1.17 | 6.34/30.49 | 0/0 | 93.9%/93.0% |
| 25% | 8 | SATISFACTION | OPTIMAL | 0.46/0.50 | 0.49/0.52 | — | 0.0%/0.0% |
| 25% | 8 | REMPLISSAGE | OPTIMAL | 0.95/1.12 | 2.61/2.77 | 0/0 | 94.4%/92.1% |
| 25% | 8 | EQUILIBRAGE | OPTIMAL | 2.73/2.89 | 17.61/119.40 | 0/0 | 94.4%/92.1% |

## Demande réelle en lieux partagés

| Demande | Densité | Séances à lieu demandées | Capacité (espaces × créneaux) | Plafond arithmétique de remplissage (lieux seuls) | Séances à lieu placées : solveur REMPL. (méd/pire) | heuristique (méd/pire) | Remplissage heuristique (méd/pire) |
|---|---|---|---|---|---|---|---|
| 10% | 2 | 66 | 140 | 100.0% | 66/66 | 66/66 | 97.9%/97.3% |
| 10% | 4 | 66 | 140 | 100.0% | 66/66 | 66/66 | 100.0%/99.7% |
| 10% | 8 | 66 | 140 | 100.0% | 66/66 | 66/66 | 100.0%/99.7% |
| 15% | 2 | 99 | 140 | 100.0% | 93/99 | 93/99 | 97.9%/97.1% |
| 15% | 4 | 99 | 140 | 100.0% | 97/99 | 93/99 | 98.9%/97.9% |
| 15% | 8 | 99 | 140 | 100.0% | 96/99 | 93/99 | 99.1%/98.6% |
| 20% | 2 | 132 | 140 | 100.0% | 111/124 | 109/124 | 96.2%/95.6% |
| 20% | 4 | 132 | 140 | 100.0% | 114/126 | 112/125 | 97.0%/96.4% |
| 20% | 8 | 132 | 140 | 100.0% | 111/127 | 108/119 | 96.4%/95.9% |
| 25% | 2 | 165 | 140 | 96.2% | 125/132 | 125/132 | 93.0%/91.7% |
| 25% | 4 | 165 | 140 | 96.2% | 125/136 | 123/135 | 93.6%/92.4% |
| 25% | 8 | 165 | 140 | 96.2% | 128/137 | 123/135 | 93.6%/91.8% |

## Équilibrage de charge — solveur contre heuristique

| Demande | Densité | Écart de charge : solveur (méd/pire) | heuristique (méd/pire) | Charge max : solveur (méd/pire) | heuristique (méd/pire) | Temps heuristique s (méd/pire) |
|---|---|---|---|---|---|---|
| 10% | 2 | 13/18 | 17/19 | 14/18 | 17/19 | 0.006/0.006 |
| 10% | 4 | 10/17 | 14/19 | 11/20 | 15/20 | 0.006/0.007 |
| 10% | 8 | 8/14 | 10/17 | 12/20 | 12/20 | 0.008/0.008 |
| 15% | 2 | 14/16 | 16/18 | 15/17 | 17/19 | 0.007/0.008 |
| 15% | 4 | 10/13 | 12/17 | 13/15 | 13/18 | 0.007/0.009 |
| 15% | 8 | 6/12 | 10/13 | 12/14 | 12/14 | 0.007/0.008 |
| 20% | 2 | 13/15 | 17/20 | 14/16 | 18/20 | 0.007/0.007 |
| 20% | 4 | 8/16 | 11/17 | 11/17 | 12/17 | 0.007/0.008 |
| 20% | 8 | 10/12 | 13/14 | 16/17 | 16/17 | 0.008/0.008 |
| 25% | 2 | 15/19 | 17/20 | 16/20 | 17/20 | 0.007/0.007 |
| 25% | 4 | 9/11 | 13/15 | 11/13 | 13/15 | 0.008/0.009 |
| 25% | 8 | 10/15 | 12/17 | 13/20 | 13/20 | 0.008/0.008 |

## Mémoire — une résolution par processus neuf

| Demande | Densité | Régime | Pic Mo (méd/pire) | Supplément vs base Mo (méd/pire) |
|---|---|---|---|---|
| 10% | 2 | SATISFACTION | 157/165 | 63/72 |
| 10% | 2 | REMPLISSAGE | 616/624 | 523/530 |
| 10% | 2 | EQUILIBRAGE | 1092/1166 | 999/1072 |
| 10% | 4 | SATISFACTION | 195/210 | 102/117 |
| 10% | 4 | REMPLISSAGE | 734/772 | 641/679 |
| 10% | 4 | EQUILIBRAGE | 1355/1611 | 1261/1518 |
| 10% | 8 | SATISFACTION | 243/258 | 150/165 |
| 10% | 8 | REMPLISSAGE | 1047/1123 | 953/1030 |
| 10% | 8 | EQUILIBRAGE | 2427/2500 | 2334/2407 |
| 15% | 2 | SATISFACTION | 180/198 | 86/105 |
| 15% | 2 | REMPLISSAGE | 611/657 | 518/564 |
| 15% | 2 | EQUILIBRAGE | 1020/1122 | 927/1028 |
| 15% | 4 | SATISFACTION | 207/231 | 113/138 |
| 15% | 4 | REMPLISSAGE | 772/845 | 679/752 |
| 15% | 4 | EQUILIBRAGE | 1291/1708 | 1197/1614 |
| 15% | 8 | SATISFACTION | 254/280 | 160/187 |
| 15% | 8 | REMPLISSAGE | 1055/1087 | 961/993 |
| 15% | 8 | EQUILIBRAGE | 2475/2758 | 2382/2665 |
| 20% | 2 | SATISFACTION | 192/215 | 99/122 |
| 20% | 2 | REMPLISSAGE | 606/617 | 513/523 |
| 20% | 2 | EQUILIBRAGE | 902/1218 | 809/1125 |
| 20% | 4 | SATISFACTION | 217/245 | 124/152 |
| 20% | 4 | REMPLISSAGE | 757/844 | 663/751 |
| 20% | 4 | EQUILIBRAGE | 1321/1358 | 1228/1265 |
| 20% | 8 | SATISFACTION | 275/298 | 182/205 |
| 20% | 8 | REMPLISSAGE | 1089/1213 | 996/1119 |
| 20% | 8 | EQUILIBRAGE | 2515/2579 | 2422/2486 |
| 25% | 2 | SATISFACTION | 216/220 | 122/126 |
| 25% | 2 | REMPLISSAGE | 626/764 | 532/671 |
| 25% | 2 | EQUILIBRAGE | 1077/1298 | 983/1205 |
| 25% | 4 | SATISFACTION | 251/262 | 158/168 |
| 25% | 4 | REMPLISSAGE | 799/812 | 706/719 |
| 25% | 4 | EQUILIBRAGE | 1414/1699 | 1321/1606 |
| 25% | 8 | SATISFACTION | 310/317 | 216/223 |
| 25% | 8 | REMPLISSAGE | 1122/1228 | 1029/1135 |
| 25% | 8 | EQUILIBRAGE | 2584/3096 | 2491/3003 |


## Remplissage par demande en lieux (60 instances)

| Demande | Solveur, médiane / minimum | Heuristique, médiane / minimum |
|---|---|---|
| 10 % | 100,0 % / 99,7 % | 99,8 % / 97,3 % |
| 15 % | 99,5 % / 98,0 % | 98,9 % / 97,1 % |
| 20 % | 96,8 % / 96,2 % | 96,4 % / 95,6 % |
| 25 % | 94,2 % / 92,1 % | 93,5 % / 91,7 % |

## Statistiques appariées — 60 instances, même instance pour les deux méthodes

| Grandeur | Constat |
|---|---|
| Statuts des 180 résolutions | 180 OPTIMAL, 0 FEASIBLE, 0 INFAISABLE |
| Remplissage : solveur (REMPLISSAGE) moins heuristique | **jamais négatif** : égal 15 fois, solveur meilleur 45 fois ; médiane +2 cases sur 660, maximum +22 cases (3,3 points) |
| Écart de charge : heuristique moins solveur (ÉQUILIBRAGE) | **jamais négatif** : égal 1 fois, solveur meilleur 59 fois ; médiane −3 créneaux (0 à 8) ; médianes des écarts : solveur 11, heuristique 14 |
| Réduction relative de l'écart de charge | médiane 24 % ; de 0 % à 80 % |
| Charge maximale : heuristique moins solveur | médiane +1 ; de 0 à +7 (jamais plus haute pour le solveur) |
| Première solution admissible, toutes résolutions | médiane 0,47 s ; pire cas 2,89 s |
| Temps jusqu'à la preuve d'optimalité, REMPLISSAGE | médiane 1,8 s ; pire cas 4,3 s |
| Temps jusqu'à la preuve d'optimalité, ÉQUILIBRAGE | médiane 10,1 s ; pire cas **119,4 s** (densité 2 : 10,5 / 22,7 ; densité 4 : 6,3 / 30,5 ; densité 8 : 15,8 / 119,4). Queue lourde : une seule instance dépasse 100 s (25 % / densité 8, graine 0) ; les 59 autres restent sous 31 s |
| Mémoire, REMPLISSAGE (pic) | médiane 764 Mo ; pire cas 1 228 Mo |
| Mémoire, ÉQUILIBRAGE (pic) | médiane 1 344 Mo ; pire cas 3 096 Mo (supplément à la base : 1 251 / 3 003 Mo) |

## Démonstration à contenu fixé — d'où vient l'écart de charge de l'heuristique

`scripts/diagnostic_contenu_fixe.py`, instances de la matrice v3 (reproductibles :
mêmes empreintes), écart de charge sur les instructeurs mobilisables, une seule
instance par ligne pour les trois colonnes (appariement garanti, tout dans un
même processus). Le solveur « contenu fixé » reçoit le contenu (quel module
dans quelle case) choisi par l'heuristique et n'optimise plus que le choix des
instructeurs et des lieux.

| Combinaison | Graine | Heuristique | Solveur libre | Solveur, contenu fixé à celui de l'heuristique |
|---|---|---|---|---|
| 25 % / densité 4 | 0 | 15 | 11 | 13 |
| 25 % / densité 4 | 1 | 14 | 7 | 11 |
| 25 % / densité 4 | 2 | 13 | 8 | 11 |
| 25 % / densité 4 | 3 | 12 | 9 | 11 |
| 25 % / densité 4 | 4 | 10 | 9 | 9 |
| **médiane** | | **13** | **9** | **11** |
| 15 % / densité 8 | 0 | 12 | 8 | 9 |
| 15 % / densité 8 | 1 | 9 | 6 | 6 |
| 15 % / densité 8 | 2 | 13 | 12 | 12 |
| 15 % / densité 8 | 3 | 10 | 6 | 7 |
| 15 % / densité 8 | 4 | 5 | 1 | 4 |
| **médiane** | | **10** | **6** | **7** |

Lecture : à contenu imposé, l'affectation optimale des instructeurs gagne 2
créneaux en médiane (13 → 11) et 3 (10 → 7) ; le reste (11 → 9 ; 7 → 6) vient
du contenu effectivement placé.

Vérification du départage de l'heuristique (`solveur/heuristique.py`) :
`min(disponibles, key=lambda i: (etat.charge_instructeur[i], i))` (l. 136) ; la
charge est incrémentée à chaque placement (`_occuper`, l. 105 : placements
provisoires inclus) et initialisée à zéro (l. 52 : aucun historique, semaine en
cours seulement) — les deux corrections exigées à la relecture du prompt 31 sont
présentes.


## Expérience — charge dans le choix du contenu (2026-09-19, revue, point 3)

`scripts/experience_charge_contenu.py` : `solveur/heuristique.py::_poids_module`
modifié pour faire peser la charge minimale des instructeurs disponibles dans
le CHOIX DE LA MATIÈRE (et non plus seulement dans le départage à matière déjà
choisie). Rejoué sur les 60 instances de la matrice, régénérées à l'identique
(60/60 empreintes concordantes), comparé à l'écart de charge du solveur déjà
enregistré ci-dessus (non relancé) :

| | Écart de charge heuristique |
|---|---|
| Avant (règle d'origine, tableau ci-dessus) | médiane 14, de 5 à 20 |
| Après (charge dans le choix de la matière) | médiane 13, de 6 à 20 |
| Gain (avant − après) | médiane 0 ; dégradée sur 11/60 instances (min −3), améliorée sur le reste (max +3) |
| Écart restant face au solveur (après − solveur, solveur médiane 11) | médiane 3 ; l'heuristique corrigée égale ou dépasse le solveur sur **1 instance sur 60** |

Le gain médian est nul et la nouvelle règle dégrade l'heuristique sur 11
instances sur 60 : faire peser la charge dans le choix de la matière ne
referme pas l'écart avec le solveur. Interprétation dans `RECOMMANDATION.md`.

## Expérience — sensibilité au nombre de fils (2026-09-19, revue, point 4)

`scripts/mesure_parallelisme.py`, combinaison la plus lourde de la matrice
(25 % / densité 8, graine 0), régime ÉQUILIBRAGE, une résolution par processus
neuf :

| Fils | Statut | Temps | Écart de charge | Mémoire pic | Supplément vs base |
|---|---|---|---|---|---|
| 22 (mesure de référence, hôte de développement) | FEASIBLE | 300,2 s | 10 | 3 217 Mo | 3 125 Mo |
| 8 | OPTIMAL | 15,5 s | 9 | 1 178 Mo | 1 086 Mo |
| 4 | FEASIBLE | 300,0 s | 10 | 971 Mo | 879 Mo |

**À 4 fils, le pire cas de la matrice dépasse la borne de 300 s sans preuve
d'optimalité — avant même d'appliquer le facteur de prudence ×3 du § 7.** La
mémoire décroît nettement avec le nombre de fils (3 217 → 1 178 → 971 Mo, un
thread du solveur portefeuille porte sa propre copie de l'état de recherche).
Le temps, en revanche, n'est PAS monotone avec le nombre de fils : le résultat
à 22 fils (300,2 s, FEASIBLE) est PLUS LENT que celui à 8 fils (15,5 s,
OPTIMAL) — et diffère du résultat obtenu sur la même instance dans la matrice
v3 (119,4 s, OPTIMAL, également à un nombre de fils proche de 22). Un solveur
portefeuille multi-fils n'est pas parfaitement reproductible d'une exécution à
l'autre (l'ordonnancement des fils varie) : ce n'est pas une erreur de mesure,
c'est une propriété du solveur, qui limite la précision de toute médiane ou
pire cas basé sur une poignée d'exécutions — y compris celles de la matrice
principale.

## Constats bruts

**Aucune instance n'est ressortie INFAISABLE, et le modèle ne peut pas
l'être.** Toutes les contraintes dures sont des plafonds (au plus une séance
par instructeur et par créneau, au plus le programme cible, au plus le volume
prescrit, au plus la capacité du lieu) : ne rien placer les satisfait toutes.
Ce constat ne dit rien de la capacité du centre. L'effet d'une demande en
lieux supérieure à la capacité se lit dans le remplissage (tableau ci-dessus) ;
plafond arithmétique à 25 % pour les seuls lieux : 96,2 % (635/660).

**Le régime SATISFACTION rend la solution vide** (remplissage 0,0 %) : c'est
le résultat attendu d'un problème dont toutes les contraintes sont des
plafonds, non un défaut. Il est conservé pour le temps de première solution ;
il n'entre dans aucun seuil.

**Mémoire.** Les valeurs de la première matrice (143 à 4 890 Mo, monotones, 12
valeurs distinctes sur 180) étaient un maximum depuis le démarrage du
processus, pas une mesure par résolution ; elles ne sont plus citées. Les
valeurs ci-dessus sont des pics de processus neuf.
