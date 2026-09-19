# Recommandation — Prompt 32, risque R6

**2026-09-18.** Interprétation de `RESULTATS.md`, confrontée aux seuils
figés de `PROTOCOLE.md` § 7 (facteur de prudence ×3 déjà appliqué : 90 s /
900 s). Analyse coût/bénéfice incluant le poids de la dépendance (§ 1).

## Confrontation aux seuils

**GO — les quatre conditions sont réunies, à la taille RÉELLE, dans le pire
cas des instances testées, sur les 12 combinaisons de sensibilité (aucune
n'est infaisable) :**

1. Première solution admissible en moins de 90 s (prudence ×3) : **oui,
   très largement** — pire cas observé 5,09 s (régime ÉQUILIBRAGE, le plus
   lent des trois), l'immense majorité sous 2 s.
2. Taux de remplissage à 5 min ≥ heuristique : **oui** — le solveur atteint
   100 % sur les 60 instances, l'heuristique entre 97,1 % et 100 % selon la
   combinaison. Aucun cas où l'heuristique fait mieux.
3. Régime ÉQUILIBRAGE : écart de charge significativement meilleur que
   l'heuristique : **oui, nettement** — écart médian solveur 1 à 9 créneaux
   contre 16 à 19 pour l'heuristique, sur toutes les combinaisons. Le
   solveur ne perd JAMAIS ce comparatif, y compris au pire cas.
4. La roue `ortools` est installable hors ligne sur la plateforme cible :
   **oui** — § 1, vérifié réellement le 2026-09-17.

**Nuance à porter au dossier, pas au verdict : trois instances (sur 60) sur
le régime ÉQUILIBRAGE n'atteignent pas la preuve d'optimalité dans la borne
de 300 s** (statut FEASIBLE, écart résiduel de 1 sur l'objectif pondéré —
la solution reste à 100 % de remplissage, seul l'écart de charge n'est pas
prouvé strictement optimal). Cela ne déclenche aucun des trois critères
NO-GO (aucune infaisabilité, aucun remplissage sous l'heuristique, aucun
paquetage impossible) — un temps de preuve qui dépasse la borne sur un
sous-ensemble des combinaisons les plus favorables aux instructeurs
(densité 8 : plus d'options équivalentes à explorer) n'est pas un défaut de
faisabilité, mais **la piste concrète pour US-PLAN-08** : un intervalle de
tolérance (« bon à 2 créneaux près » plutôt que « strictement minimal »)
raccourcirait sans doute ces trois cas sans changer la qualité pratique de
la solution.

## Recommandation : GO

Le solveur CP-SAT est retenu comme option pour US-PLAN-08. Sur les
combinaisons mesurées, il domine l'heuristique sur le critère qui justifie
sa complexité — l'équilibrage de charge — sans jamais dégrader le taux de
remplissage, à un coût de temps qui reste très en deçà de BNF-04 même avec
le facteur de prudence appliqué.

## Analyse coût/bénéfice

**Bénéfice mesuré** : écart de charge divisé par 2 à 17 selon la
combinaison (médiane solveur 1–9 contre heuristique 16–19), sans coût en
remplissage. C'est le résultat que l'heuristique gloutonne — qui place et
n'ajuste jamais — ne peut structurellement pas obtenir : elle n'arbitre
jamais entre deux placements déjà faits.

**Coût mesuré, au-delà du § 1** :
- **Poids de la dépendance** : ~110 Mo installés (`ortools` 80 Mo +
  `numpy`/`pandas`/`protobuf` transitifs, D-160) — à intégrer au paquet hors
  ligne si retenu, sujet à un nouveau test d'installation isolée complet
  (celui du 7 septembre ne le couvre pas).
- **Maturité de la dépendance, constat NOUVEAU (PROTOCOLE.md § 5)** : un
  bogue mémoire natif reproductible a été trouvé et contourné pendant cette
  étude (relire `IntVar.Proto()` en cours de construction corrompt le
  modèle) — propre à `ortools-9.15.6755` sur `python:3.14.4-slim-bookworm`,
  la combinaison la plus récente possible (Python 3.14 a quelques mois).
  Le contournement est simple et documenté, mais sa DÉCOUVERTE a pris plus
  de temps que la totalité du reste du prototypage. Une montée de version
  future d'`ortools` ou de Python pourrait réintroduire un bogue
  équivalent, non couvert par les tests applicatifs existants.
- **Mémoire** : 1 à 5 Go pour le régime ÉQUILIBRAGE à la taille RÉELLE —
  sans commune mesure avec l'empreinte de l'heuristique (négligeable), à
  vérifier contre la mémoire réellement disponible sur le serveur cible
  (inconnue, § 8 de `PROTOCOLE.md`).
- **Complexité de maintenance** : un modèle CP-SAT et son vocabulaire
  (variables, contraintes de liaison, objectifs pondérés) sont un corps de
  connaissance distinct de la stratégie gloutonne actuelle — un
  changement de comportement futur (nouvelle contrainte métier) devra être
  porté aux DEUX implantations si `GENERATION_STRATEGIE` bascule au cas par
  cas (§ 7, GO CONDITIONNEL) plutôt qu'au remplacement complet.

**Limite de portée, à ne pas perdre de vue (PROTOCOLE.md, « Ajout du
2026-09-18 »)** : ce prototype ne modélise ni RG-36 (indisponibilités), ni
RG-38 (périodes bloquantes), et neutralise le sous-cas salle attitrée de
RG-37 par construction. Il mesure un problème AU MOINS AUSSI FACILE que le
problème réel. Le GO ci-dessus porte sur CE problème simplifié — la marge
observée (écart de charge divisé par plus de 2 dans le pire cas, remplissage
toujours à 100 %) est large, mais elle devra être reconfirmée si
`US-PLAN-08` couvre effectivement RG-36/RG-38.

## Proposition de réévaluation R6 (registre des risques)

| | Avant cette étude | Proposé, 2026-09-18 |
|---|---|---|
| **Probabilité** | Élevée (aucune mesure, hypothèse d'échec par défaut) | **Faible** — mesuré réel : GO sur toutes les combinaisons prioritaires, marge large |
| **Impact** | Élevé (US-PLAN-08 pourrait être irréalisable) | **Moyen** — US-PLAN-08 réalisable, mais coûte une dépendance lourde et jeune, et un second corps de code à maintenir |
| **Criticité** | Élevée | **Réduite** — le risque technique (« ça ne marchera pas ») est levé ; ce qui reste est un risque de PROJET (maintenance, empaquetage), pas de faisabilité |
| **État de la mesure d'atténuation** | Aucune mesure prise | **Mesure prise** : prototype fonctionnel, 60 instances mesurées à taille réelle, GO confirmé sur les quatre critères du § 7 |

**Recommandation pour le jalon C2 (26 septembre)** : lever R6 de la liste
des risques bloquants ; le reporter, si le registre le permet, vers un
risque de type « dette d'intégration » (poids/maintenance de la dépendance)
plutôt qu'un risque de faisabilité — la question posée par R6 (« un solveur
peut-il résoudre le problème dans les 5 minutes ? ») a une réponse mesurée :
oui, avec une marge confortable, sur le problème tel que ce prototype le
pose.

## Décision go/no-go J2 (10 octobre) — élément d'entrée, pas la décision

Ce document alimente la décision go/no-go d'US-PLAN-08, il ne la prend pas :
la décision porte aussi sur le calendrier du sprint 3, la disponibilité
pour porter RG-36/RG-38 dans le modèle si nécessaire, et l'arbitrage
`requirements.txt` (D-160, toujours en attente).
