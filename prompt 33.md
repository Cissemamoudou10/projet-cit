# Prompt 33 — Clôture du sprint 2 et prononcé du jalon C2

Douze stories, 61 points, périmètre entier livré. Plus l'étude de faisabilité du
solveur, hors périmètre chiffré.

CE PROMPT NE LIVRE PRESQUE PAS DE CODE. C'est un travail de pilotage, de
vérification et de cohérence documentaire.

CONTEXTE DE DATE, à traiter explicitement. Nous sommes le 30 septembre 2026.
Le jalon C2 était prévu le 26 septembre : il n'a pas été prononcé, faute de ses
éléments de pilotage. C'est la DEUXIÈME occurrence consécutive — le jalon C1 du
12 septembre avait déjà été franchi sans les heures réelles ni la révision de la
clé de conversion. Le sprint 3 a démarré le 28 septembre et n'a aucune story
engagée. Ce prompt produit donc une clôture et un prononcé EN RETARD, et il le
dit : ne rétrodate rien, ne fais pas comme si C2 avait été tenu le 26.

Vérifie d'abord l'état réel : `AVANCEMENT.md` porte encore la date du 8 septembre
et annonce « sprint 2, 0 livrée » ; les quatre cases de revue de `sprint-2.md`
sont vides ; `DECISIONS.md` s'arrête à D-163. Si tu constates autre chose,
dis-le avant de commencer.

Neuf blocs, dans l'ordre : A et B conditionnent la revue, les autres
l'alimentent.

## Bloc A — Heures réelles et clé de conversion

Condition de franchissement de C2, absente du sprint 1 comme du sprint 2.

Produis `docs/suivi/HEURES-SPRINT-2.md` :

| Story | Points | Heures relevées | Heures par point | Source du relevé |

Une ligne par story, plus une ligne pour l'étude du solveur (heures relevées,
AUCUN point — elle ne doit pas entrer dans le calcul de la clé).

La colonne « source du relevé » n'est pas décorative : indique pour chaque ligne
si l'heure vient d'un relevé contemporain, d'un horodatage de commit, ou d'une
reconstitution. **Si le relevé est partiel ou reconstitué, DIS-LE en tête du
fichier.** Une clé fondée sur des estimations rétrospectives est pire qu'une clé
absente : elle a l'apparence d'une mesure. À défaut de relevé fiable, propose la
méthode la moins fausse — par exemple l'écart entre premier et dernier commit
d'une story, en précisant qu'elle surestime ou sous-estime, et pourquoi.

Puis :

- la clé mesurée sur le sprint 2 : total des heures divisé par 61 points ;
- la même clé recalculée en excluant les stories largement pré-livrées par les
  précédentes — US-SES-04 et US-SES-07 — et en tenant compte du déplacement de
  charge d'US-PLAN-03 vers US-PLAN-04, qui a absorbé les trois modèles du
  paquetage P5. Dis ce que cette seconde clé change ;
- la comparaison à la clé provisoire de 1,3 h/point posée à D-33 ;
- la projection sur les 108 points restants des sprints 3 et 4, avec la clé
  retenue, convertie en jours ouvrés à la disponibilité réelle ;
- ta recommandation : faut-il réviser la clé, et à quelle valeur ?

## Bloc B — Tableau des reports, vérifié sur le code

Premier point de l'ordre du jour de la revue.

Reconstitue INTÉGRALEMENT le tableau des reports de `AVANCEMENT.md`, report par
report, EN VÉRIFIANT CHACUN SUR LE CODE RÉEL — jamais sur la déclaration de la
décision qui l'a posé, jamais sur l'affirmation d'une story qui prétend l'avoir
refermé.

Rappel de ce qui fonde l'exigence : D-50 a déclaré refermé un report qui ne
l'était pas ; il est resté ouvert quatre jours et il a fallu un lot de clôture
pour s'en apercevoir (P-25).

Pour chaque report : code de la décision, critère concerné, story d'origine,
story qui devait le refermer, ÉTAT VÉRIFIÉ, et LE TEST qui le prouve — fichier
et nom du test. **Un report déclaré refermé sans test nommé est réputé ouvert.**

Traite explicitement :

- les reports que le sprint 2 devait refermer : D-23, D-34, D-35 volet séance,
  D-39, D-45, D-51, D-54 volets brigade et séance ;
- D-51 en particulier — le `PROTECT` sur `Seance.instructeur` protège
  l'instructeur, pas la qualification. Refermé, et par quoi ?
- D-156 annonce la fermeture de six reports au Prompt 31 : recontrôle-les un par
  un plutôt que de reprendre le décompte ;
- les reports CRÉÉS pendant le sprint 2 : recense-les tous ;
- l'écart entre le compte annoncé à la revue du sprint 1 — « neuf reports, trois
  refermés, six des sept ouverts se referment au sprint 2 » — et le compte
  vérifié. `AVANCEMENT.md` relève déjà que ce chiffre est incohérent avec
  lui-même (9 − 3 = 6, pas 7). À SIGNALER en revue, jamais à corriger en silence.

Rends le compte final : combien d'ouverts, combien de refermés au sprint 2,
combien de créés, et vers quelles stories les ouverts pointent.

Traite aussi l'écart de numérotation signalé dans `AVANCEMENT.md` : plusieurs
décisions citent des codes de story qui ne correspondent plus à la numérotation
de `sprint-2.md`. Les correspondances fonctionnelles s'établissent par la
description du besoin, pas par le code cité. Dresse la table de correspondance
et propose une correction — NE TOUCHE PAS au backlog, c'est un arbitrage de chef
de projet.

## Bloc C — Registre des risques : propositions

Tu NE MODIFIES PAS `09_Registre_risques_v5`. Tu produis
`docs/suivi/RISQUES-PROPOSITIONS-C2.md`, que le chef de projet reportera.

- **R6** — reprends la réévaluation de `etudes/solveur/RECOMMANDATION.md` :
  probabilité, impact, criticité, état de la mesure d'atténuation. Ajoute la
  DÉCISION ARRÊTÉE : l'heuristique gloutonne est la stratégie de production ;
  US-PLAN-08 est déclassée en perspective d'évolution, réexaminée à la clôture du
  sprint 4 sous DEUX CONDITIONS CUMULATIVES — périmètre Must entièrement livré,
  et marge de quatorze jours ouvrés avant dépôt intacte. Motif : gain mesuré de
  deux à trois créneaux d'écart de charge à contenu imposé, contre 110 Mo de
  dépendance, 3,1 Go de mémoire, un bogue mémoire natif constaté et un second
  corps de code à maintenir.
- **R19, cohérence documentaire** — état après ce prompt, compte tenu du bloc D.
- **RISQUE NOUVEAU À PROPOSER, saturation des salles attitrées.** 32 à 38 salles
  ordinaires pour 30 à 35 brigades (`etudes/solveur/HYPOTHESES.md`) : dans la
  combinaison la plus défavorable, il en manque. RG-14 est presque saturée en
  permanence et ouvrir une session supplémentaire peut échouer faute de salle,
  indépendamment de tout logiciel. Formule-le pour ce qu'il est : un constat de
  terrain que le système va rendre visible, pas un risque projet.
- **RISQUE NOUVEAU À PROPOSER, divergence entre deux stratégies de génération**
  — conditionnel, sans objet tant qu'US-PLAN-08 n'est pas réalisée.
- **RISQUE NOUVEAU À PROPOSER, dispositif de pilotage non tenu.** Deux jalons
  consécutifs, C1 et C2, franchis sans leurs éléments de pilotage. Probabilité
  élevée — deux occurrences sur deux —, impact sur la crédibilité du suivi en
  soutenance. Mesure d'atténuation à proposer.
- **R9** — confirme qu'il reste éteint et que l'ajout d'`openpyxl` à US-SES-05 est
  bien entré au paquet hors ligne. Si le protocole n'a pas été rejoué depuis,
  dis-le : c'est une dette, pas un problème. Rappelle que `ortools` n'y entre
  pas (D-160).

## Bloc D — Cohérence documentaire

- **Doublon du titre D-157** dans `DECISIONS.md` : nettoie-le. Le décompte du
  bloc B s'appuie sur ce fichier.
- **Ordre des entrées** de `DECISIONS.md` : vérifie qu'il est décroissant sur
  toute la longueur, pas seulement sur les dernières insertions.
- **P-38** : vérifie qu'il est bien marqué résolu et que D-161 porte les mesures
  remesurées (41 requêtes, pente nulle). Il a été **livré puis découvert après
  clôture** d'US-PLAN-03 : assure-toi que `PROBLEMES.md` le dit explicitement —
  c'est un point de revue, et la troisième occurrence du motif « un critère de
  définition de fini jamais vraiment mesuré ».

## Bloc E — Écarts avec les livrables, consolidés

Le sprint 2 a produit un nombre inhabituel d'écarts entre backlog, fiches de cas
d'utilisation, diagramme de classes et note d'implémentation. Ils sont dispersés
dans `DECISIONS.md` ; le chef de projet ne peut pas les reporter s'ils restent
éparpillés.

Produis `docs/suivi/ECARTS-LIVRABLES-SPRINT-2.md`, une ligne par écart :
livrable concerné, ce qu'il dit, ce qui a été implanté, la décision qui
l'arbitre, l'action attendue du chef de projet.

Recense au moins, en vérifiant qu'il n'en manque pas :

- titre d'US-PLAN-03 au backlog — « d'une brigade » alors que RG-33 bis fait
  porter le programme sur le centre entier ;
- omission de la Direction de la formation au critère 3 d'US-SES-04, RÉCIDIVE de
  D-44 : appelle une relecture systématique du backlog sur ce point ;
- taux d'occupation présent au tableau des écarts des cas d'utilisation, absent
  des critères d'US-SES-04 ;
- unicité de désignation de brigade : note d'implémentation au niveau du type de
  formation, implantée au niveau de la session ;
- critère 1 d'US-SES-06 contre la fiche CU-P3-06 : remplissage séquentiel contre
  répartition équilibrée ;
- critère 3 d'US-SES-06 : refus contre avertissement sur les deux plafonds ;
- radiation absente des critères d'US-SES-05, présente à la fiche ;
- critère 4 d'US-PLAN-01 contre le § 5.4 du diagramme de classes v4 ;
- critère 5 d'US-PLAN-12, clôture d'une grille, traitée par l'archivage absent de
  CLS-03 ;
- RG-14 absente du tableau des treize contraintes de la phase 4 ;
- D-153, nature `GENERATION_PROGRAMME` : extension à RG-26, à porter au cahier
  des charges avec les trois natures hors RG-26 déjà signalées en D-16 ;
- D-154, `programme_lecture` accordé à deux profils seulement : la cellule
  pédagogique ne peut pas lire le programme de ses propres brigades. À arbitrer
  par le chef de projet, pas à corriger ;
- D-155, impression « par journée » de RG-33 bis non implantée ;
- décompte des contraintes en couche services : il a bougé plusieurs fois pendant
  le sprint — donne le compte final et sa composition, c'est un argument de
  soutenance sur la justification de la couche services ;
- inversion de l'ordre d'US-PLAN-03 et US-PLAN-04 (D-134) ;
- tout autre écart consigné que cette liste ne couvre pas.

## Bloc F — Gardes mécaniques et couverture, inventaire

La règle de couverture HTTP a été inscrite en définition de fini à la clôture du
sprint 1, après un inventaire qui avait révélé 24 chemins nominaux et 36 refus
d'habilitation manquants.

Refais l'inventaire sur le périmètre du sprint 2 :

- toute adresse d'écriture ajoutée figure-t-elle à la table des refus ?
- tout écran livré a-t-il son test de chemin nominal ET son test de refus par le
  cycle HTTP réel ?
- le garde mécanique d'US-PLAN-04 — aucun module hors `ServiceEcritureSeance`
  n'écrit `Seance` ou `LigneProgramme` — est-il effectif, et couvre-t-il le
  chemin de la génération ?
- US-PLAN-04 ne livrait aucun écran : confirme que la règle de couverture HTTP y
  est SANS OBJET, plutôt que contournée.

Comble ce qui manque. Rends le compte de ce qui a été ajouté.

## Bloc G — Mesures de référence consolidées

`docs/suivi/MESURES-REFERENCE.md` :

- les quatre mesures du § 10 d'US-PLAN-03, dans leur version post-P-38 ;
- le nombre de requêtes d'un `verifier_lot` (test H6 d'US-PLAN-04) ;
- le total des tests de la suite, et sa progression depuis les 738 de la clôture
  du sprint 1 ;
- les mesures d'impression accumulées pendant le sprint. Consolide-les dans
  `IMPRESSION-ANALYSE.md`, dis ce que le lot des gabarits imprimables du sprint 4
  devra traiter — en ajoutant ces écrans aux deux déjà connus, Instructeurs
  33 px et Lieux 74 px — et indique lesquels appellent le format paysage.

## Bloc H — Leçons apprises

`docs/suivi/LECONS-SPRINT-2.md`, trois à six leçons, chacune en trois parties :
ce qui s'est passé, ce qu'on en retient, ce qu'on change.

Candidates, à compléter ou écarter selon ton jugement :

- **Le dispositif de pilotage n'a pas tourné.** Deux jalons consécutifs, C1 et
  C2, franchis sans heures réelles ni révision de la clé de conversion. Ce qu'on
  change concrètement pour J2 le 10 octobre — propose un mécanisme, pas une
  intention.
- L'inversion d'US-PLAN-03 et US-PLAN-04 : un cas d'utilisation inclus se
  développe avant celui qui l'inclut.
- P-38 : troisième occurrence du motif « un critère de définition de fini jamais
  vraiment mesuré » — le critère existait, le test existait, la dimension mesurée
  n'était pas la bonne.
- Le défaut de déterminisme du générateur d'instances du prototype, trouvé en
  vérifiant qu'un formatage ne changeait rien, qui avait invalidé une matrice
  entière de mesures sans que rien ne l'indique. C'est la meilleure leçon du
  sprint — l'étude qui avait failli valider ses propres résultats — et elle
  mérite d'être rédigée pour le mémoire.
- Les arbitrages backlog contre livrables : trois principes différents ont été
  appliqués — la fiche plus précise l'emporte, la règle structurante l'emporte
  sur la formulation, une règle doit être exprimable sur le modèle qu'on
  implante. Énonce-les ENSEMBLE : appliqués séparément, ils passent pour de
  l'arbitraire.
- P-36, troisième occurrence : une recherche par motif qui ne trouve rien prise
  pour une preuve d'absence.

## Bloc I — Mise à jour des documents de suivi

- `docs/suivi/sprint-2.md` : toutes les cases cochées, revue et rétrospective
  comprises. La tâche « Prototype du solveur CP-SAT » est ACHEVÉE — l'étude est
  rendue ; coche-la en renvoyant à `etudes/solveur/`. La tâche « Diagramme
  d'états du programme (ETA-01) » : si elle n'a pas été produite, reporte-la
  explicitement au sprint 3, où US-VAL-03 la rend nécessaire, plutôt que de la
  laisser décochée sans mention.
- `docs/suivi/AVANCEMENT.md` : phase 5 à jour, sprint 2 CLOS avec 12 stories et
  61 points livrés, indicateurs renseignés — stories, points, vélocité MESURÉE,
  clé de conversion RÉVISÉE, marge avant dépôt. Tableau des reports remplacé par
  celui du bloc B. Section « Ce qu'il faut surveiller » réécrite : R9 et R6 n'y
  ont plus leur place sous leur forme actuelle. État des questions de terrain :
  le volume horaire hebdomadaire de référence est refermé par le code à
  US-PLAN-12 ; dis lesquelles restent ouvertes et lesquelles ont été ajoutées
  pendant le sprint — dont celle sur l'existence d'un troisième horaire au CIT.
  Ajoute la date réelle de mise à jour, et mentionne que C2 est prononcé le
  30 septembre, en retard de quatre jours.
- `docs/suivi/DECISIONS.md` : entrées de ce prompt, ordre vérifié, doublon
  nettoyé.

## Ce que tu ne touches pas

Le backlog produit, le cahier des charges, le registre des risques, le dossier
d'architecture, la note d'implémentation, les diagrammes. `.claude/rules` les
réserve au chef de projet. Tous les écarts et propositions passent par les
fichiers de suivi que ce prompt demande.

Aucune story du sprint 3.

## Ce que tu me rends

- Le tableau des heures, la clé retenue, ta recommandation, et une phrase franche
  sur la fiabilité du relevé (bloc A).
- Le compte final des reports, chacun adossé à un test nommé (bloc B).
- Les propositions de risques, R6 en tête (bloc C).
- La liste consolidée des écarts avec les livrables (bloc E).
- Ce que l'inventaire du bloc F a révélé et comblé.
- Les leçons (bloc H), dont celle sur le dispositif de pilotage.
- Et, en une phrase : le sprint 2 est-il clos, et reste-t-il quelque chose qui
  empêche de prononcer C2 aujourd'hui ?