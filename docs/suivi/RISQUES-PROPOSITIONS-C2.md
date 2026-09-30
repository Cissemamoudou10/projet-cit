# Propositions pour le registre des risques — jalon C2

Prompt 33, bloc C. **Ce document NE MODIFIE PAS `09_Registre_risques_v5`** —
il ne fait que proposer ; le report dans le registre reste au chef de projet.

## R6 — Faisabilité d'un solveur à contraintes (US-PLAN-08)

**Réévaluation, sur `etudes/solveur/RECOMMANDATION.md` (v3, 2026-09-19,
D-162).**

| | Avant l'étude | Après l'étude |
|---|---|---|
| Probabilité | Inconnue — aucune mesure | **Faisabilité technique levée** : le solveur résout la taille réelle en 0,47 s médiane, jamais un remplissage inférieur à l'heuristique |
| Impact | Élevé si le solveur s'avérait indispensable et infaisable | Résiduel — reclassé « valeur et intégration », plus « faisabilité » |
| Criticité | 9 (`AVANCEMENT.md`, § « Ce qu'il faut surveiller ») | **À la baisse** — le risque de blocage technique n'existe plus ; ce qui reste est un arbitrage coût/bénéfice, pas un risque de faisabilité |
| État de la mesure d'atténuation | Prototype à construire | **Terminée** — 60 instances appariées, empreinte vérifiée, mesures reproductibles (matrice v3) |

**DÉCISION ARRÊTÉE** (portée par ce prompt, entrée pour J2 du 10 octobre) :
l'heuristique gloutonne reste la stratégie de production. US-PLAN-08 est
**déclassée en perspective d'évolution**, réexaminée à la clôture du sprint 4
sous **deux conditions cumulatives** : périmètre *Must* entièrement livré,
et marge de quatorze jours ouvrés avant dépôt intacte. Motif : gain mesuré de
deux à trois créneaux d'écart de charge à contenu imposé, contre 110 Mo de
dépendance transitive, jusqu'à 3,1 Go de mémoire par résolution, un bogue
mémoire natif réellement constaté dans `ortools`, et un second corps de code
à maintenir en miroir de `ServiceContraintes`. Détail et chiffres complets :
`etudes/solveur/RECOMMANDATION.md`, section « Entrée pour la décision
go/no-go de J2 ».

**À noter pour le mémoire** (D-162) : le meilleur résultat de l'étude n'est
pas le chiffre du GO/NO-GO, mais le défaut de déterminisme trouvé et corrigé
dans le générateur d'instances — une matrice entière avait failli être
publiée sur des mesures non appariées d'un processus à l'autre. Voir bloc H.

## R9 — Installation hors ligne (BNF-06)

**Confirmé éteint**, avec une dette explicite à consigner. Le contenu
technique a été acquis le 7 septembre (VM Debian 12 isolée, protocole
complet rejoué, `docs/suivi/INSTALLATION-HORS-LIGNE.md`). Depuis :

- `openpyxl==3.1.5` (US-SES-05, import de stagiaires) a bien été ajouté au
  paquet hors ligne le 2026-09-12 (D-99) : présence de la roue vérifiée dans
  l'image Docker reconstruite (`pip show openpyxl`), roue pure Python sans
  dépendance native.
- **Le protocole complet (VM isolée, rejeu intégral) n'a PAS été rejoué
  depuis le 7 septembre.** C'est une dette, explicitement consignée comme
  telle par D-99 elle-même au moment de l'ajout — pas un problème découvert
  ici. À rejouer avant le dépôt réel, pas nécessairement avant chaque ajout
  mineur de dépendance pure Python.
- `ortools` (étude du solveur) **n'entre pas** dans `requirements.txt` ni
  dans le paquet hors ligne (D-160) : l'étude vit dans un environnement
  virtuel isolé, exclu de `tests/architecture/test_dependances.py` et du
  paquet de déploiement (`test_etude_solveur_isolee_de_l_application`). Sans
  objet pour R9 tant que la décision ci-dessus (renoncement) n'est pas
  révisée.

## R19 — Cohérence documentaire

**État après ce prompt** : le sprint 2 a produit un nombre inhabituel
d'écarts entre backlog, fiches de cas d'utilisation, diagramme de classes et
note d'implémentation — seize recensés (`docs/suivi/ECARTS-LIVRABLES-SPRINT-2.md`,
bloc E), dispersés dans `DECISIONS.md` avant ce prompt, maintenant consolidés
en un seul endroit pour que le chef de projet puisse les reporter. Deux
défauts mécaniques trouvés et corrigés en bloc D (une inversion d'ordre
D-16/D-17 vieille du 3 septembre, jamais remarquée jusqu'ici ; le doublon de
titre D-157 était déjà corrigé avant ce prompt). Deux reports de critères
retrouvés en scannant `DECISIONS.md` en entier (D-91, D-108) n'avaient jamais
été ajoutés au tableau de suivi malgré leur propre texte le demandant
explicitement (bloc B) — c'est la manifestation la plus concrète de R19 :
la trace existe, mais sa consolidation dans les fichiers de suivi n'est pas
automatique et se perd si personne ne la fait. **Risque non éteint** : la
cause (pas de vérification systématique qu'une décision marquée « à ajouter
au tableau de suivi » l'est réellement) reste entière — voir la proposition
de risque « dispositif de pilotage non tenu » ci-dessous, qui en est la
cause racine.

## RISQUE NOUVEAU À PROPOSER — Saturation des salles attitrées

**Constat de terrain, pas un risque projet au sens strict** — à formuler
ainsi dans le registre, pas comme un défaut du logiciel. `etudes/solveur/
HYPOTHESES.md` recense 32 à 38 salles ordinaires pour 30 à 35 brigades. Dans
la combinaison la plus défavorable, il en manque. RG-14 (salle attitrée
distincte par brigade sur une période sécante) est presque saturée en
permanence dans ces conditions : ouvrir une session supplémentaire peut
échouer faute de salle disponible, indépendamment de tout défaut logiciel —
le système va rendre ce constat visible en le faisant respecter
correctement, là où il restait implicite avant. Probabilité et impact à
apprécier par le chef de projet ; mesure d'atténuation possible : vérifier
le ratio réel salles/brigades au CIT avant le déploiement.

## RISQUE NOUVEAU À PROPOSER — Divergence entre deux stratégies de génération

**Conditionnel, sans objet tant qu'US-PLAN-08 n'est pas réalisée.** Si le
solveur CP-SAT était un jour activé en production à côté de l'heuristique
(bascule `GENERATION_STRATEGIE`), les deux stratégies pourraient produire des
programmes différents sur les mêmes données — écart perçu comme une
instabilité si mal expliqué aux utilisateurs. Sans objet aujourd'hui (R6
déclasse US-PLAN-08 en perspective d'évolution) ; à retenir comme risque
dérivé, à réactiver seulement si les deux conditions cumulatives de R6 sont
un jour remplies.

## RISQUE NOUVEAU À PROPOSER — Dispositif de pilotage non tenu

**Constat central de ce prompt.** Deux jalons consécutifs, C1 (12 septembre)
et C2 (26 septembre), franchis — ou ici, prononcé en retard — sans leurs
éléments de pilotage : heures réelles jamais relevées, clé de conversion
jamais révisée sur une mesure fiable (voir `docs/suivi/HEURES-SPRINT-2.md`),
`AVANCEMENT.md` resté à la date du 8 septembre pendant tout le sprint 2. C'est
la cause racine derrière R19 : une trace qui existe dans le code et les
décisions individuelles, mais que rien ne force à remonter dans les documents
de suivi consolidés.

- **Probabilité** : élevée — deux occurrences sur deux jalons possibles à ce
  jour.
- **Impact** : sur la crédibilité du dispositif de suivi en soutenance —
  un jury qui compare les dates de `AVANCEMENT.md` aux dates réelles du
  dépôt Git verra l'écart immédiatement.
- **Mesure d'atténuation à proposer** : voir bloc H (leçons) — un mécanisme
  concret pour J2 (10 octobre), pas une intention réitérée. Recommandation :
  faire de la mise à jour d'`AVANCEMENT.md` une étape explicite de CHAQUE
  clôture de story (comme `docs/suivi/sprint-N.md` l'est déjà), pas une tâche
  de fin de sprint reportée à un prompt de clôture séparé — c'est précisément
  parce que c'était une tâche séparée qu'elle a été manquée deux fois.
