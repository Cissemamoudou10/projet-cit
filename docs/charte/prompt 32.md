# Prompt 32 (v2) — Prototype du solveur CP-SAT · étude de faisabilité du risque R6

Tâche transverse du sprint 2, à restituer au jalon C2 du 26 septembre.
CE N'EST PAS UNE STORY. Aucun code livré dans l'application.

## 0. Nature de ce travail

Le livrable est un TABLEAU DE MESURES et UNE RECOMMANDATION ARGUMENTÉE, pas un
générateur de programme. Le prototype répond à une seule question : un solveur à
contraintes peut-il résoudre le problème de programmation du Centre d'instruction
des transmissions, à la taille réelle, dans les cinq minutes de BNF-04 ?

De cette réponse dépendent la réévaluation de R6 au jalon C2 du 26 septembre et
la décision go/no-go sur US-PLAN-08 au jalon J2 du 10 octobre.

EMPLACEMENT : `etudes/solveur/`, à la racine du dépôt, HORS de `app/`.
Dépendances propres, environnement virtuel distinct. EXCLU du paquet de
déploiement hors ligne et de `tests/architecture/test_dependances.py`. Aucun
module de `app/` ne l'importe, et il n'importe aucun module de `app/`. Ajoute un
test d'architecture qui le constate.

Motif à consigner dans `DECISIONS.md` : `ortools` pèse de l'ordre de la centaine
de mégaoctets et devrait entrer dans le paquet hors ligne, alors que rien ne dit
encore qu'on le gardera. Le test d'installation isolée du 7 septembre a validé
une pile précise ; y ajouter une dépendance lourde avant la décision de J2
rouvrirait R9 pour une étude qui peut conclure au renoncement.

## 1. Étape 0 — la vérification qui peut tout arrêter

AVANT TOUT AUTRE TRAVAIL, une demi-heure.

`ortools` existe-t-il sous forme de roue précompilée pour la plateforme du
serveur cible — architecture, système, version de Python, version de la
bibliothèque C standard ? Télécharge-la réellement, note sa taille exacte,
installe-la dans un environnement neuf, exécute un modèle trivial.

Si la roue n'existe pas ou ne s'installe pas : LA QUESTION EST TRANCHÉE. Aucun
prototype nécessaire, décision de J2 rendue d'avance, R6 réévalué sur ce constat,
l'heuristique gloutonne devient la réponse définitive. Arrête-toi, rends-m'en
compte, écris-le dans `RECOMMANDATION.md`. C'est un résultat parfaitement
présentable au jury.

Si elle existe, sa taille entre dans l'analyse coût/bénéfice du § 8.

## 2. Les hypothèses de dimensionnement — relevées, non estimées

Elles proviennent d'un dépouillement des emplois du temps et des progressions
d'instruction du centre, conduit le 17 septembre 2026. Produis
`etudes/solveur/HYPOTHESES.md`, daté, reprenant le tableau ci-dessous et
distinguant pour chaque ligne CE QUI A ÉTÉ RELEVÉ de CE QUI EST DÉDUIT.

RELEVÉ SUR LES DOCUMENTS DU CENTRE :

- sessions de formation actives simultanément : 15
- brigades actives, toutes sessions confondues : 30 à 35
  (une à trois brigades par session ; moyenne de l'ordre de 2,2)
- instructeurs : 80 à 120
- modules au catalogue : 70 à 100
- lieux : 40 à 45 salles au total, dont 4 à 5 spécialisées ou communes,
  plus 2 à 3 espaces extérieurs (garage, terrain)
- créneaux hebdomadaires : grille ordinaire, 4 créneaux du lundi au jeudi,
  vendredi plus court — 19 à 20 créneaux

DÉDUIT DE CES RELEVÉS, à écrire comme tel :

- salles ordinaires disponibles pour les salles attitrées : 32 à 38
  (total moins spécialisées moins espaces extérieurs)
- cases à pourvoir par semaine : 570 à 700 (brigades × créneaux)
- capacité brute en créneaux-instructeur : 1 520 à 2 400 par semaine
- capacité des lieux partagés : 114 à 160 créneaux-lieu par semaine
  (6 à 8 espaces × 19 à 20 créneaux)

NON ENCORE RELEVÉ — traité en axe de sensibilité (§ 4) :

- proportion des séances exigeant un lieu spécialisé ou extérieur
- densité de la matrice de qualification : nombre moyen d'instructeurs
  qualifiés par module, et proportion de modules n'en comptant qu'un ou deux
- nombre de modules programmables par brigade sur une semaine donnée
- densité des indisponibilités d'instructeurs et des périodes bloquantes

RÈGLE ABSOLUE : ce fichier est écrit et daté AVANT la première mesure et n'est
plus modifié ensuite. Si une hypothèse se révèle fausse, ajoute une ligne datée,
ne réécris jamais l'ancienne. Des hypothèses ajustées après coup transformeraient
l'étude en justification.

OBSERVATION À CONSIGNER, qui dépasse le prototype : 32 à 38 salles ordinaires
pour 30 à 35 brigades. Dans la combinaison la plus défavorable, il en manque. Le
centre fonctionne donc à la limite de sa capacité en salles attitrées, ce qui
signifie que RG-14 est presque saturée en permanence et qu'ouvrir une session
supplémentaire peut échouer faute de salle. À porter au mémoire et à signaler au
chef de projet : c'est une conclusion de terrain, pas un résultat de mesure.

## 3. Les trois tailles

- CONTRÔLE — 1 session, 3 brigades, ressources proportionnelles. Sert à vérifier
  que le modèle est correct, jamais qu'il passe à l'échelle.
- RÉELLE — 15 sessions, 33 brigades, 100 instructeurs, 85 modules, 35 salles
  ordinaires, 7 lieux partagés, 20 créneaux. Valeurs médianes des fourchettes
  du § 2. C'est la SEULE taille qui décide du go/no-go.
- HAUTE — bornes hautes de toutes les fourchettes : 35 brigades, 120
  instructeurs, 100 modules, 8 lieux partagés.

NE FAIS PAS DE « TAILLE DOUBLE ». Soixante-dix brigades ne sont pas le centre, et
mesurer un problème qui n'existera jamais ne renseigne sur rien. La marge de
sécurité se prend sur le RÉGIME DE CONTRAINTE (§ 4), pas sur le volume.

## 4. L'axe de sensibilité — ce qui sature, pas ce qui est confortable

Les instructeurs sont confortables en agrégé : 570 à 700 cases pour 1 520 à 2 400
créneaux-instructeur disponibles, soit 25 à 45 % d'occupation. Ce n'est donc pas
là que le problème devient difficile. Deux dimensions décident, et les deux sont
mal connues : fais-les varier.

DEMANDE EN LIEUX PARTAGÉS — proportion des séances exigeant un lieu spécialisé ou
extérieur. Mesure à 10 %, 15 %, 20 % et 25 %.
Repère de calcul : à 15 %, la demande atteint une centaine de créneaux pour 114 à
160 disponibles, soit 70 à 85 % d'occupation. À 25 %, la demande dépasse
probablement la capacité et le problème devient INFAISABLE. C'est un résultat,
pas un échec : il faut alors mesurer en combien de temps le solveur SAIT le dire,
et constater que l'heuristique, elle, ne le saura jamais — elle laissera des
trous sans pouvoir expliquer s'ils étaient évitables.

DENSITÉ DE QUALIFICATION — nombre moyen d'instructeurs qualifiés par module.
Mesure à 2, 4 et 8. Dans chaque cas, garde une fraction de modules « rares » à un
seul instructeur qualifié : 5 %, puis 15 %. Ce sont ces modules-là qui font
échouer la génération, et c'est sur eux qu'est bâti l'ordre de priorité de
l'heuristique.

Soit une matrice de mesures. Priorité si le temps manque : la taille RÉELLE, sur
les quatre valeurs de demande en lieux et les trois densités de qualification —
douze combinaisons, cinq instances chacune. Le reste est du confort.

## 5. Le modèle

Pars de `docs/suivi/CONTRAINTES-SOLVEUR.md`, produit à US-PLAN-04. S'il te paraît
incomplet ou inexact, corrige-le et signale la correction : une divergence entre
ce document et l'implantation réelle des contraintes invaliderait toute l'étude.

Formulation recommandée, à discuter si tu vois mieux : décomposition booléenne
avec contraintes de liaison — une variable par couple brigade-créneau-matière,
une par brigade-créneau-instructeur restreinte aux instructeurs qualifiés, une
par brigade-créneau-lieu restreinte aux séances exigeant un lieu partagé. À la
taille réelle, l'ordre de grandeur attendu est de dix mille à cinquante mille
variables booléennes. Si tu dépasses largement, c'est que la formulation n'exploite
pas les restrictions de domaine — dis-le avant de mesurer.

SIMPLIFICATIONS AUTORISÉES, à DÉCLARER dans `PROTOCOLE.md` avec leur effet
probable sur les mesures :
- pas de regroupement de brigades (US-PLAN-06, sprint 3) ;
- prérequis traités par pré-filtrage des matières programmables, comme le fait
  l'heuristique, plutôt que par contraintes de précédence ;
- une séance par créneau, jamais de fusion, comme à US-PLAN-03.
Toute autre simplification doit être déclarée. Une simplification non déclarée
rend les mesures inexploitables : c'est le défaut le plus courant de ce genre
d'étude.

TROIS RÉGIMES mesurés séparément :
- SATISFACTION — trouver une solution admissible, sans objectif ;
- REMPLISSAGE — maximiser le nombre de cases pourvues ;
- ÉQUILIBRAGE — remplissage, puis minimisation de l'écart de charge entre
  instructeurs. C'est le seul régime qui justifierait réellement le solveur face
  à l'heuristique : à 25-45 % d'occupation, trouver UNE solution n'est pas
  l'enjeu, bien répartir l'est.

## 6. La comparaison avec l'heuristique

Un GÉNÉRATEUR D'INSTANCES dans `etudes/solveur/` produit une description neutre —
JSON — d'un problème complet, paramétrée par les valeurs du § 3 et du § 4, avec
graine aléatoire fixée et consignée. Le modèle CP-SAT la lit ; une
RÉIMPLANTATION COURTE de l'heuristique, appliquant la même règle de priorité que
`app/planification`, la lit également.

Déclare la limite : cette réimplantation peut diverger de celle de l'application.
La comparaison porte sur les APPROCHES, pas sur les implantations. Le contrôle de
réalité est fourni par les quatre mesures relevées à US-PLAN-03 § 10 sur le jeu
de démonstration ; si elles sont du même ordre que celles de la réimplantation
sur une instance comparable, la comparaison tient. Si elles divergent nettement,
dis-le — cela vaudrait d'être expliqué avant toute conclusion.

Cinq instances par combinaison.

## 7. Les seuils de décision — figés avant la première mesure

Écris-les dans `PROTOCOLE.md`. Ils ne bougent plus ensuite.

GO — le solveur est retenu si, à la TAILLE RÉELLE, dans le PIRE CAS des instances
testées, et pour les combinaisons de sensibilité où le problème est faisable :
- une première solution admissible est obtenue en moins de trente secondes ;
- le taux de remplissage à cinq minutes est au moins égal à celui de
  l'heuristique ;
- sur le régime ÉQUILIBRAGE, l'écart de charge entre instructeurs est
  significativement meilleur que celui de l'heuristique ;
- la roue `ortools` est installable hors ligne sur la plateforme cible.

NO-GO — l'heuristique reste la réponse définitive si, à la taille réelle :
- aucune solution admissible en trois cents secondes sur une combinaison
  faisable ;
- taux de remplissage inférieur à celui de l'heuristique ;
- empaquetage hors ligne impossible.

GO CONDITIONNEL — cas intermédiaire : solveur retenu comme option, heuristique par
défaut, basculement par le paramètre `GENERATION_STRATEGIE` posé à US-PLAN-03.

Si ces seuils te paraissent mal calibrés, DIS-LE MAINTENANT. Après la première
mesure, ce ne serait plus recevable.

## 8. Les mesures

Pour chaque combinaison, chaque régime et chaque instance :
- temps jusqu'à la première solution admissible ;
- temps jusqu'à la preuve d'optimalité, ou dépassement de la borne ;
- statut retourné : optimal, admissible, INFAISABLE, indéterminé. Le statut
  infaisable est une information précieuse et propre au solveur — l'heuristique
  ne sait jamais dire si une solution existait ;
- taux de remplissage, cases pourvues sur cases ouvertes ;
- écart d'optimalité restant à cinq minutes ;
- écart de charge entre instructeurs, sur le régime ÉQUILIBRAGE ;
- mémoire maximale ;
- pour l'heuristique, sur les mêmes instances : temps total, taux de remplissage,
  écart de charge.

Rapporte la MÉDIANE et le PIRE CAS des cinq instances. La médiane décrit le
comportement courant, le pire cas décide — c'est lui que rencontrera l'agent un
lundi matin.

Machine de mesure identifiée dans `PROTOCOLE.md` : processeur, mémoire, et si
elle est représentative du serveur cible. Si elle ne l'est pas — et elle ne l'est
probablement pas, les caractéristiques du serveur étant elles-mêmes une question
de terrain ouverte — propose un facteur de prudence et applique-le aux seuils du
§ 7.

## 9. Les livrables

Dans `etudes/solveur/` :
- `HYPOTHESES.md` (§ 2), daté, figé ;
- `PROTOCOLE.md` (§ 3 à § 8), figé avant mesure ;
- le code : générateur d'instances, modèle CP-SAT, heuristique de comparaison,
  script d'exécution ;
- `RESULTATS.md` — le tableau brut, sans interprétation ;
- `RECOMMANDATION.md` — l'interprétation, la recommandation confrontée aux seuils
  du § 7, et l'analyse coût/bénéfice incluant le poids de la dépendance relevé
  au § 1.

Plus, pour le registre des risques : une proposition de réévaluation de R6 —
probabilité, impact, criticité, état de la mesure d'atténuation. C'est ce que
porte le jalon C2.

Plus, séparément : l'observation sur la saturation des salles attitrées (§ 2),
qui n'est pas un résultat de mesure et ne doit pas être noyée dans les tableaux.

## 10. Ce que tu ne fais pas

Aucune modification de `app/`. Aucun import d'`ortools` dans l'application.
Aucun programme réel généré : le prototype travaille sur des instances
synthétiques. Aucune modification d'`HYPOTHESES.md` ni de `PROTOCOLE.md` après la
première mesure, sinon par ajout daté.

## 11. Ce que tu me rends

- Le résultat du § 1, aujourd'hui, avant tout le reste.
- `HYPOTHESES.md` et `PROTOCOLE.md` pour validation AVANT la première mesure. Je
  veux pouvoir contester les hypothèses et les seuils pendant qu'ils sont encore
  contestables.
- Le nombre de variables du modèle à la taille réelle, avant de lancer la
  matrice de mesures.
- Puis les résultats, la recommandation, la réévaluation de R6.
- Le temps réellement passé, à la demi-heure près. Cette étude ne porte aucun
  point et son coût doit être visible dans le bilan du sprint.