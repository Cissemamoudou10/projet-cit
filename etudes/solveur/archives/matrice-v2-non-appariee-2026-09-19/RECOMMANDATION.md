# Recommandation — Prompt 32, risque R6 (version 2)

**2026-09-19.** Interprétation de `RESULTATS.md` (matrice v2), confrontée aux
seuils figés de `PROTOCOLE.md` § 7 (facteur de prudence ×3 appliqué aux deux
seuils de temps). Analyse coût/bénéfice incluant le poids de la dépendance
(§ 1).

> **Le prototype mesure un problème au moins aussi facile que le problème
> réel.** RG-36 (indisponibilités), RG-38 (périodes bloquantes) et le refus de
> salle attitrée (RG-37) ne sont pas modélisés (`PROTOCOLE.md` § 5). Un
> résultat favorable ne se généralise pas automatiquement au système réel ; un
> résultat défavorable tiendrait a fortiori.

## Ce qui change par rapport à la version du 2026-09-18

La première version concluait **GO** sur un écart de charge « divisé par 2 à
17 ». Cette conclusion est **retirée** : la revue a établi que ces écarts
étaient en grande partie des artefacts de mesure — demande en lieux appliquée
au catalogue (demande effective de 3 à 11 % pour 10 à 25 % annoncés), écart de
charge calculé sur des instructeurs inutilisables, contenu librement choisi par
le solveur mais imposé à l'heuristique par sa règle de priorité. Les trois
défauts sont corrigés et documentés (`PROTOCOLE.md`, ajouts du 2026-09-19) ; la
matrice a été refaite (60 instances, 180 résolutions). L'écart de charge est
désormais réduit de **24 % en médiane**, non de 50 à 95 %.

## Confrontation aux seuils du § 7

| Critère du GO | Seuil (avec ×3) | Mesuré, taille RÉELLE, 60 instances | Verdict |
|---|---|---|---|
| Première solution admissible | < 30 s (90 s) | médiane 0,47 s, pire cas 3,21 s (9,6 s avec ×3) | **atteint**, marge > 9× |
| Remplissage à 5 min ≥ heuristique | ≥ | jamais inférieur (0/60) ; égal 18 fois, meilleur 42 fois ; médiane +2 cases sur 660, maximum +22 (3,3 points) | **atteint** |
| Écart de charge « significativement meilleur » | non chiffré | meilleur 56 fois, égal 3 fois, **pire 1 fois** ; médiane −3 créneaux (−24 %), de −29 % à +80 % | **non tranchable** (voir ci-dessous) |
| Roue `ortools` installable hors ligne | oui | oui (§ 1, 2026-09-17) | **atteint** |

Aucun critère NO-GO n'est déclenché : solution en quelques secondes, jamais de
remplissage inférieur à l'heuristique, empaquetage possible.

**Le troisième critère ne peut pas être tranché honnêtement.** Le mot
« significativement » n'a jamais été chiffré dans le protocole figé, et le
prompt interdit de fixer un seuil après la première mesure. Les faits : la
direction est quasi constante (56 cas sur 60) mais l'amplitude est modeste
(−3 créneaux en médiane), avec un contre-exemple. Que −24 % soit « significatif »
pour US-PLAN-08 est un jugement qui vous appartient ; je n'en fixe pas le
seuil ici.

## Recommandation : GO CONDITIONNEL

Solveur retenu **comme option**, heuristique **par défaut**, bascule par le
paramètre `GENERATION_STRATEGIE` posé à US-PLAN-03 (`PROTOCOLE.md` § 7, cas
intermédiaire). Deux lectures, un même résultat : si −24 % est jugé
significatif, la lecture stricte du § 7 donne GO ; sinon c'est exactement le cas
intermédiaire. Dans les deux cas l'analyse coût/bénéfice ci-dessous ne justifie
pas de remplacer l'heuristique.

## Ce que le solveur apporte, et ce qu'il ne change pas

**Remplissage : l'heuristique est déjà très proche de l'optimum.** Écart
médian à l'optimum prouvé : 2 cases sur 660 (0,3 point), au pire 22 cases
(3,3 points). Les trous de l'heuristique sont, pour l'essentiel, inévitables.
Ce que le solveur apporte est la **preuve** : 180 résolutions sur 180 au
statut OPTIMAL, écart d'optimalité nul sur les 120 qui portent un objectif —
l'heuristique ne saura jamais dire si un trou était évitable. À 25 % de demande, le remplissage optimal est de 93,9 %
en médiane, sous le plafond arithmétique de 96,2 % des lieux seuls (les types
de lieux spécialisés le resserrent).

**Équilibrage : un gain réel, modeste, d'origine mixte.** La démonstration à
contenu fixé (`RESULTATS.md`) sépare deux sources. À contenu imposé (celui de
l'heuristique), l'affectation optimale des instructeurs gagne 2 créneaux en
médiane (25 % / densité 4 : 13 → 11) à 3 (15 % / densité 8 : 10 → 7) — le
départage glouton est correctement implanté (placements provisoires inclus,
semaine en cours seulement) mais myope. Le reste (11 → 9 ; 7 → 6) tient au
contenu : le solveur pourvoit davantage de cases. La charge **maximale** est
souvent identique (médianes égales à densité 8 : 12 contre 12, 16 contre 16,
13 contre 13) : le gain vient du relèvement du minimum, le pic étant imposé par
des modules à instructeur rare ou unique.

## Temps : deux durées à ne pas confondre

- **Première solution admissible** — ce que BNF-04 exige de rendre : médiane
  0,47 s, pire cas 3,21 s ; 9,6 s avec ×3.
- **Preuve d'optimalité** : REMPLISSAGE pire cas 3,8 s ; ÉQUILIBRAGE médiane
  9,8 s, pire cas 52,0 s (densité 8) ; avec ×3, médiane ≈ 29 s et pire cas
  ≈ 156 s, sous la borne de 300 s (marge ×5,8). Sur une machine plus de 5,8
  fois plus lente que celle-ci, les pires cas dépasseraient la borne : le
  solveur rendrait la meilleure solution admissible trouvée (BNF-04
  l'autorise), sans preuve d'optimalité — et sans garantie que son remplissage
  soit optimal, seule la première matrice ayant montré des cas sans preuve, à
  100 % de remplissage.
  Le facteur ×3 reste une hypothèse, pas une mesure. (La première matrice
  comptait 3 instances FEASIBLE sur 60 ; la v2, mieux posée, aucune — les deux
  ne se comparent pas.)
- **Rapport à l'application.** L'heuristique du prototype (0,007 s) est une
  réimplantation Python pure, sans base de données ; elle ne représente pas le
  coût réel de l'application : la génération de 200 cases y prend 0,6 s (D-161),
  dont 97 % des requêtes SQL sont des écritures (P-38) ; l'extrapolation à 660
  cases, non mesurée, est de l'ordre de la seconde à quelques secondes. Une
  solution du solveur devrait s'écrire par la même porte, au même coût. Le surcoût du solveur est donc de quelques secondes à
  environ une minute, non d'un facteur 1 000.

## Mémoire

La valeur « 1 à 5 Go » de la première version est **retirée** : c'était le
maximum depuis le démarrage du processus (180 mesures monotones, 12 valeurs
distinctes), non une mesure par résolution. Mesuré désormais dans un processus
neuf par résolution (ligne de base 93 Mo) : REMPLISSAGE pic médian 776 Mo, pire
cas 1,18 Go ; ÉQUILIBRAGE pic médian 1,30 Go, **pire cas 2,88 Go** (densité 8),
soit un supplément de 1,2 à 2,8 Go. La mémoire croît avec la densité de
qualification. C'est l'un des rares coûts susceptibles de bloquer le
déploiement : il faut **au moins 3 Go libres** pour le solveur, en plus de
Django et de PostgreSQL, sur un serveur dont la mémoire est inconnue (question
de terrain, `PROTOCOLE.md` § 8). Réserve : mesuré sur les structures Python de
l'étude ; celles de l'application (objets Django, contexte) s'y ajouteraient.

## Analyse coût/bénéfice

**Bénéfice mesuré** : 0,3 point de remplissage en médiane (3,3 au maximum) ;
écart de charge réduit de 24 % en médiane ; preuve d'optimalité.

**Coût** :
- **Poids** : ~110 Mo installés (`ortools` 80 Mo + `numpy`/`pandas`/`protobuf`
  transitifs, D-160), nouveau test d'installation isolée à refaire.
- **Maturité** : un bogue mémoire natif reproductible a été trouvé et
  contourné (relire `IntVar.Proto()` en cours de construction corrompt le
  modèle), sous Windows et sur la plateforme cible ; une montée de version
  d'`ortools` ou de Python peut en réintroduire un équivalent, non couvert par
  les tests applicatifs.
- **Mémoire** : jusqu'à 2,9 Go (ci-dessus).
- **Double implantation** : un modèle CP-SAT redit RG-34 à RG-39 ; toute règle
  nouvelle devra être portée aux deux endroits, sous peine de divergence — le
  risque même que `CONTRAINTES-SOLVEUR.md` cherchait à prévenir.

**Bilan** : un bénéfice réel mais modeste pour un coût réel. C'est le cas
intermédiaire du § 7 : une option, pas un remplacement.

## Limites à ne pas perdre de vue

- **Problème plus facile que le réel** (en tête de ce document).
- **Contenu exogène.** Le programme cible retire au solveur la liberté de
  choisir quels modules placer. Le prototype ne dit rien d'un solveur qui
  choisirait aussi le contenu (ce qui exigerait un vrai modèle de progression
  hebdomadaire) : c'est une piste pour US-PLAN-08, pas un résultat.
- **Instances synthétiques**, une semaine, cinq graines par combinaison (les
  médianes et pires cas portent sur cinq valeurs) ; réimplantation de
  l'heuristique pouvant diverger de celle de l'application — la comparaison
  porte sur les approches (`PROTOCOLE.md` § 6).
- **Contrôle de réalité (§ 6)** : les quatre mesures d'US-PLAN-03 (D-161) — 100 %
  de remplissage sur 200 cases, jeu peu contraint — sont du même ordre que
  celles de la réimplantation à faible demande en lieux (98 à 100 %).

## Proposition de réévaluation R6 (registre des risques)

| | Avant l'étude | Proposé, 2026-09-19 |
|---|---|---|
| **Probabilité** | Élevée (aucune mesure) | **Faible** — faisabilité mesurée : solution en secondes, preuve d'optimalité, à taille réelle |
| **Impact** | Élevé (US-PLAN-08 irréalisable ?) | **Moyen** — réalisable, mais gain modeste, mémoire de 1 à 3 Go, dépendance lourde et jeune |
| **Criticité** | Élevée | **Réduite** |
| **Mesure d'atténuation** | Aucune | **Prise** : prototype, 60 instances, seuils du § 7 confrontés |

Le risque de faisabilité que porte R6 est levé. Ce qui subsiste est un risque
de **valeur et d'intégration** — « le solveur ne vaut pas son coût » — à
reformuler comme tel au registre plutôt que de conserver R6.

## Entrée pour la décision go/no-go de J2 (10 octobre)

Ce document alimente la décision d'US-PLAN-08, il ne la prend pas. Si l'option
est retenue : heuristique par défaut derrière `GENERATION_STRATEGIE` ; corriger
P-38 (écritures en boucle) au préalable, l'écriture étant commune aux deux
stratégies ; confirmer la mémoire disponible du serveur cible ; décider si
RG-36 et RG-38 entrent dans le modèle.

L'observation sur la saturation des salles attitrées (`HYPOTHESES.md`) n'est
pas un résultat de mesure et reste hors de ces tableaux.
