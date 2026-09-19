# Recommandation — Prompt 32, risque R6 (version 3)

**2026-09-19.** Interprétation de `RESULTATS.md` (matrice v3), confrontée aux
seuils figés de `PROTOCOLE.md` § 7 (facteur de prudence ×3 appliqué aux deux
seuils de temps). Analyse coût/bénéfice incluant le poids de la dépendance
(§ 1).

> **Le prototype mesure un problème au moins aussi facile que le problème
> réel.** RG-36 (indisponibilités), RG-38 (périodes bloquantes) et le refus de
> salle attitrée (RG-37) ne sont pas modélisés (`PROTOCOLE.md` § 5). Un
> résultat favorable ne se généralise pas automatiquement au système réel ; un
> résultat défavorable tiendrait a fortiori.

> **La conclusion opératoire de cette étude : l'écart de charge de
> l'heuristique vient surtout du CHOIX DU CONTENU, pas du départage entre
> instructeurs.** La démonstration à contenu fixé (`RESULTATS.md`) le mesure
> directement : à contenu imposé (celui de l'heuristique), l'affectation
> optimale des instructeurs ne gagne que 2 à 3 créneaux d'écart en médiane
> (13 → 11 ; 10 → 7) ; le reste de l'écart mesuré (11 → 9 ; 7 → 6) tient à
> QUELLE matière l'heuristique programme à quel créneau, choisi par sa règle
> « le plus difficile d'abord » avant même de choisir l'instructeur. Un
> solveur qui ne ferait qu'affecter des instructeurs à un contenu déjà fixé
> apporterait donc peu ; c'est ce que change réellement le solveur, et ce
> n'est pas d'abord une question d'algorithme de départage.

## Ce qui change par rapport aux versions précédentes

La première version (2026-09-18) concluait **GO** sur un écart de charge
« divisé par 2 à 17 ». Cette conclusion est **retirée** : la revue a établi que
ces écarts étaient en grande partie des artefacts de mesure — demande en lieux
appliquée au catalogue (demande effective de 3 à 11 % pour 10 à 25 % annoncés),
écart de charge calculé sur des instructeurs inutilisables, contenu librement
choisi par le solveur mais imposé à l'heuristique par sa règle de priorité. Une
seconde matrice, refaite avec ces corrections, a elle-même été écartée : une
vérification de dernière minute a montré que la génération d'instances n'était
pas déterministe d'un processus à l'autre, si bien que les régimes et
l'heuristique d'une même ligne n'étaient pas mesurés sur la même instance. Le
défaut est corrigé, testé, et gardé par une empreinte d'instance comparée entre
processus (`PROTOCOLE.md`, ajouts du 2026-09-19). **Cette version 3 repose sur
une matrice dont les 180 résolutions ont toutes l'empreinte de l'instance de
l'heuristique.** L'écart de charge est réduit de **24 % en médiane**.

## Confrontation aux seuils du § 7

| Critère du GO | Seuil (avec ×3) | Mesuré, taille RÉELLE, 60 instances appariées | Verdict |
|---|---|---|---|
| Première solution admissible | < 30 s (90 s) | médiane 0,47 s, pire cas 2,89 s (8,7 s avec ×3) | **atteint**, marge > 10× |
| Remplissage à 5 min ≥ heuristique | ≥ | jamais inférieur (0/60) ; égal 15 fois, meilleur 45 fois ; médiane +2 cases sur 660, maximum +22 (3,3 points) | **atteint** |
| Écart de charge « significativement meilleur » | non chiffré | jamais pire (0/60) ; égal 1 fois, meilleur 59 fois ; médiane −3 créneaux (écart médian 14 → 11, −24 %), de 0 % à −80 % | **non tranchable** (voir ci-dessous) |
| Roue `ortools` installable hors ligne | oui | oui (§ 1, 2026-09-17) | **atteint** |

Aucun critère NO-GO n'est déclenché : solution en quelques secondes, jamais de
remplissage inférieur à l'heuristique, empaquetage possible.

**Le troisième critère ne peut pas être tranché honnêtement.** Le mot
« significativement » n'a jamais été chiffré dans le protocole figé, et le
prompt interdit de fixer un seuil après la première mesure. Les faits : la
direction est désormais sans ambiguïté (59 cas sur 60, jamais pire) mais
l'amplitude reste modeste (−3 créneaux en médiane). Que −24 % soit
« significatif » pour US-PLAN-08 est un jugement qui vous appartient ; je n'en
fixe pas le seuil ici.

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
l'heuristique ne saura jamais dire si un trou était évitable. À 25 % de
demande, le remplissage optimal est de 94,2 % en médiane (heuristique 93,5 %),
sous le plafond arithmétique de 96,2 % des lieux seuls (les types de lieux
spécialisés le resserrent).

**Équilibrage : un gain réel, modeste, d'origine mixte.** La démonstration à
contenu fixé (`RESULTATS.md`) sépare deux sources. À contenu imposé (celui de
l'heuristique), l'affectation optimale des instructeurs gagne 2 créneaux en
médiane (25 % / densité 4 : 13 → 11) à 3 (15 % / densité 8 : 10 → 7) — le
départage glouton est correctement implanté (placements provisoires inclus,
semaine en cours seulement) mais myope. Le reste (11 → 9 ; 7 → 6) tient au
contenu : le solveur pourvoit davantage de cases. La charge **maximale** n'est
jamais plus haute pour le solveur (médiane −1, jusqu'à −7) et est souvent
identique (médianes égales à densité 8 : 12 contre 12, 16 contre 16, 13 contre
13) : le gain vient surtout du relèvement du minimum, le pic étant imposé par
des modules à instructeur rare ou unique.

**Expérience conduite pendant la revue (point 3)** : faire peser la charge des
instructeurs dans le CHOIX de la matière (pas seulement le départage à
matière déjà choisie) a été testé (`RESULTATS.md`, « Expérience — charge dans
le choix du contenu »). Gain médian nul (écart heuristique 14 → 13, dégradée
sur 11 instances sur 60) ; l'heuristique corrigée n'égale ou ne dépasse le
solveur que sur 1 instance sur 60. Le déséquilibre restant n'est donc pas la
conséquence d'une règle de tri trop simple, réparable par un critère
supplémentaire : il est structurel, lié à la matrice de qualification
(quelques modules à instructeur unique ou rare qui concentrent la charge) —
une conclusion de terrain, pas un résultat de mesure, à porter au mémoire.

## Temps : deux durées à ne pas confondre

- **Première solution admissible** — ce que BNF-04 exige de rendre : médiane
  0,47 s, pire cas 2,89 s ; 8,7 s avec ×3.
- **Preuve d'optimalité** : REMPLISSAGE pire cas 4,3 s ; ÉQUILIBRAGE médiane
  10,1 s, pire cas **119,4 s**. La distribution a une queue lourde : **une seule
  instance** dépasse 100 s (25 % / densité 8, graine 0) ; les 59 autres restent
  sous 31 s (92 s avec ×3). Avec ×3, cette instance atteindrait ≈ 358 s, **au-delà
  de la borne de 300 s** : le solveur rendrait alors la meilleure solution
  admissible trouvée (BNF-04 l'autorise), sans preuve d'optimalité — et sans
  garantie que son remplissage soit optimal. Sur 60 instances, c'est 1 cas
  (1,7 %) ; il faudrait une machine plus de 2,5 fois plus lente pour que cela
  se produise, ×3 restant une hypothèse et non une mesure.
- **Rapport à l'application.** L'heuristique du prototype (0,007 s) est une
  réimplantation Python pure, sans base de données ; elle ne représente pas le
  coût réel de l'application : la génération de 200 cases y prend 0,39 s,
  41 requêtes SQL constantes, indépendantes du nombre de séances (D-161,
  après correction de P-38 — un défaut d'écriture en boucle livré à la
  clôture d'US-PLAN-03, découvert et corrigé pendant cette revue) ;
  l'extrapolation à 660 cases, non mesurée, reste de l'ordre de la seconde. Une
  solution du solveur devrait s'écrire par la même porte, au même coût. Le
  surcoût du solveur est donc de quelques secondes à environ une minute (deux
  minutes au pire cas), non d'un facteur 1 000.
- **Toutes les mesures ci-dessus tournent à ~22 fils** (nombre de fils
  disponibles sur l'hôte de développement) — voir la section « Sensibilité au
  nombre de fils » ci-dessous : le serveur cible en aura vraisemblablement
  quatre ou huit, et le comportement n'y est pas le même.

## Sensibilité au nombre de fils — question du serveur cible (2026-09-19, revue point 4)

Toutes les mesures ci-dessus tournent avec `num_search_workers` par défaut
d'ortools, qui approche le nombre de fils disponibles — 22 sur l'hôte de
développement. Le serveur cible du CIT en aura vraisemblablement quatre ou
huit (question de terrain non tranchée, `PROTOCOLE.md` § 8) ; le facteur de
prudence ×3 du § 7 couvre un écart de FRÉQUENCE par cœur, pas une PERTE DE
PARALLÉLISME, qui est un axe distinct et jusqu'ici non mesuré.

Rejoué sur la combinaison la plus lourde de la matrice (25 % / densité 8,
graine 0), régime ÉQUILIBRAGE, à 22, 8 puis 4 fils (`RESULTATS.md`) :

**À 4 fils, le pire cas de la matrice dépasse la borne de 300 s sans preuve
d'optimalité — avant même d'appliquer le facteur ×3.** Sur un serveur à quatre
cœurs, ce n'est donc plus 1 instance sur 60 qui risque de manquer la preuve
(comme l'estimait la section « Temps » ci-dessus, sur la base des 22 fils de
l'hôte de développement), mais potentiellement plusieurs, dès la fréquence
d'un serveur ordinaire — l'estimation à « 1 cas sur 60 » ne tient donc QUE sur
du matériel proche de 22 fils, pas sur le matériel plausible du serveur cible.
La solution rendue resterait admissible (BNF-04 l'autorise) mais sans garantie
d'optimalité du remplissage ni de l'écart de charge.

La mémoire, en revanche, décroît nettement avec le nombre de fils (3,22 Go à
22 fils → 1,18 Go à 8 → 0,97 Go à 4) : un thread du solveur porte sa propre
copie de l'état de recherche, donc MOINS de fils consomme MOINS de mémoire —
sur un serveur à 4 cœurs, la réserve de 3,5 Go recommandée ci-dessus est
probablement excessive, 1 à 1,5 Go suffirait vraisemblablement (non mesuré
au-delà de cette seule instance).

**Limite supplémentaire, constatée en mesurant** : le temps n'est PAS monotone
avec le nombre de fils (8 fils, 15,5 s, OPTIMAL, plus rapide que 22 fils,
300,2 s, FEASIBLE sans preuve) et la même instance, au même nombre de fils
proche de 22, donne un résultat différent d'une exécution à l'autre (300,2 s
FEASIBLE ici, contre 119,4 s OPTIMAL dans la matrice v3) : un solveur
portefeuille multi-fils n'est pas parfaitement reproductible, l'ordonnancement
des fils variant d'une exécution à l'autre. Ce n'est pas une erreur de
mesure, c'est une propriété du solveur — qui limite la confiance à accorder à
n'importe quel pire cas isolé de cette étude, y compris ceux de la matrice
principale.

## Mémoire

La valeur « 1 à 5 Go » de la première version est **retirée** : c'était le
maximum depuis le démarrage du processus (180 mesures monotones, 12 valeurs
distinctes), non une mesure par résolution. Mesuré désormais dans un processus
neuf par résolution (ligne de base 93 Mo) : REMPLISSAGE pic médian 764 Mo, pire
cas 1,23 Go ; ÉQUILIBRAGE pic médian 1,34 Go, **pire cas 3,10 Go** (densité 8),
soit un supplément de 1,25 à 3,00 Go. La mémoire croît avec la densité de
qualification. C'est l'un des rares coûts susceptibles de bloquer le
déploiement : prévoir **de l'ordre de 3,5 Go libres** pour le solveur, en plus
de Django et de PostgreSQL, sur un serveur dont la mémoire est inconnue
(question de terrain, `PROTOCOLE.md` § 8). Réserve : mesuré sur les structures
Python de l'étude ; celles de l'application (objets Django, contexte)
s'y ajouteraient.

## Analyse coût/bénéfice

**Bénéfice mesuré** : 0,3 point de remplissage en médiane (3,3 au maximum) ;
écart de charge réduit de 24 % en médiane, jamais dégradé ; preuve
d'optimalité.

**Coût** :
- **Poids** : ~110 Mo installés (`ortools` 80 Mo + `numpy`/`pandas`/`protobuf`
  transitifs, D-160), nouveau test d'installation isolée à refaire.
- **Maturité** : un bogue mémoire natif reproductible a été trouvé et
  contourné (relire `IntVar.Proto()` en cours de construction corrompt le
  modèle), sous Windows et sur la plateforme cible ; une montée de version
  d'`ortools` ou de Python peut en réintroduire un équivalent, non couvert par
  les tests applicatifs.
- **Mémoire** : jusqu'à 3,1 Go (ci-dessus).
- **Temps** : queue lourde sur la preuve d'optimalité de l'équilibrage
  (119 s au pire sur 60 instances).
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
  médianes et pires cas d'une combinaison portent sur cinq valeurs) ;
  réimplantation de l'heuristique pouvant diverger de celle de l'application —
  la comparaison porte sur les approches (`PROTOCOLE.md` § 6).
- **Contrôle de réalité (§ 6)** : les quatre mesures d'US-PLAN-03 (D-161) —
  100 % de remplissage sur 200 cases, jeu peu contraint — sont du même ordre
  que celles de la réimplantation à faible demande en lieux (98 à 100 %).

## Proposition de réévaluation R6 (registre des risques)

| | Avant l'étude | Proposé, 2026-09-19 |
|---|---|---|
| **Probabilité** | Élevée (aucune mesure) | **Faible** — faisabilité mesurée : solution en secondes, preuve d'optimalité, à taille réelle |
| **Impact** | Élevé (US-PLAN-08 irréalisable ?) | **Moyen** — réalisable, mais gain modeste, mémoire de 1 à 3 Go, dépendance lourde et jeune |
| **Criticité** | Élevée | **Réduite** |
| **Mesure d'atténuation** | Aucune | **Prise** : prototype, 60 instances appariées, seuils du § 7 confrontés |

Le risque de faisabilité que porte R6 est levé. Ce qui subsiste est un risque
de **valeur et d'intégration** — « le solveur ne vaut pas son coût » — à
reformuler comme tel au registre plutôt que de conserver R6.

## Entrée pour la décision go/no-go de J2 (10 octobre)

Ce document alimente la décision d'US-PLAN-08, il ne la prend pas. Si l'option
est retenue : heuristique par défaut derrière `GENERATION_STRATEGIE` (P-38,
écritures en boucle, est déjà corrigé — commun aux deux stratégies) ;
confirmer la mémoire disponible du serveur cible ; décider si RG-36 et RG-38
entrent dans le modèle.

**Sur le critère « significativement meilleur » (§ 7)** : ce critère n'a
jamais été chiffré dans le protocole figé, alors que les trois autres critères
du GO le sont tous — c'est un défaut de rédaction du protocole, qui
m'appartient. Le prompt interdit de fixer un seuil après la première mesure ;
je ne le fais donc pas ici. L'appréciation qui suit est rendue
**explicitement** par le chef de projet, non par l'application d'un seuil que
le protocole aurait fixé d'avance : **−24 % d'écart de charge (médiane 14 → 11
créneaux) ne suffit pas**, et l'orientation est le **renoncement** au solveur
pour US-PLAN-08 — un gain de 3 créneaux d'écart est disproportionné face au
coût (~110 Mo de dépendance transitive, jusqu'à 3,1 Go de mémoire par
résolution, un bogue mémoire natif réellement constaté dans `ortools`, un
second corps de code à maintenir en miroir de `ServiceContraintes`). Cette
appréciation ne rouvre pas les mesures ci-dessus, qui restent GO CONDITIONNEL
au sens strict du § 7.

L'observation sur la saturation des salles attitrées (`HYPOTHESES.md`) n'est
pas un résultat de mesure et reste hors de ces tableaux.
