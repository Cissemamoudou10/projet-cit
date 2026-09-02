---
name: regles-metier
description: Les vingt-cinq règles métier structurantes du domaine, celles dont la remise en cause invaliderait le modèle. À consulter avant d'implanter une validation, une contrainte, ou toute logique dans la couche services.
---

# Règles métier structurantes

Le livrable complet en compte soixante-cinq. Voici les vingt-cinq marquées
**structurantes** : elles viennent du terrain et **ne doivent jamais être
réinterprétées**. Les autres figurent dans
`docs/conception/11-cas-utilisation.md`, section 11.3.

## Référentiel

`RG-05` Le référentiel appartient à la formation, **jamais à la brigade**. Aucune
matière n'est rattachée directement à une brigade ni à une session.

`RG-08` Volume prescrit, coefficient et catégorie de lieu sont propres au **couple
formation-matière**. La même matière porte des valeurs différentes dans deux
formations. Le volume est strictement positif.

`RG-10` Le graphe des prérequis d'un référentiel est **acyclique**. Vérifié à
chaque ajout, en couche services, avec affichage de la chaîne du cycle en cas de
refus.

## Organisation

`RG-12` Le nombre et la composition des brigades relèvent d'une **décision
humaine**. Le système enregistre, il ne calcule pas.

`RG-16` Les brigades d'une session suivent des matières et volumes identiques ;
**seul l'ordre diffère**. Le décalage est délibéré : ne cherche jamais à
l'aligner.

`RG-20` Un stagiaire appartient à **une seule brigade à la fois**. Un changement
est daté et historisé, il ne crée pas une seconde affectation.

## Ressources et calendrier

`RG-23` L'indisponibilité est en **saisie déléguée** : horodatée et rattachée à
l'agent de la cellule qui l'enregistre, jamais à l'instructeur concerné.

`RG-28` Les périodes du calendrier ont une **granularité horaire**. La journée
n'est pas l'unité.

`RG-29` L'**effet** d'une période — bloquante ou informative — est **dissocié de sa
nature**. Chaque nature porte un défaut paramétrable, surchargeable au cas par
cas. Seul le doublon exact est refusé ; toute autre intersection donne un
avertissement.

`RG-30` Une période porte **plusieurs cibles**, sessions et brigades
indépendamment. Aucune cible : le centre entier. La portée est **dérivée**.

`RG-30 bis` Les dates des sessions sont **projetées** depuis `Session`, jamais
saisies au calendrier.

`RG-62` Plusieurs grilles horaires coexistent, **une seule est active**.

`RG-63` L'activation d'une grille est une **décision datée et nominative**, jamais
déduite du calendrier.

`RG-64` La grille contraint ce que la génération **propose**, jamais ce que la
saisie manuelle décide. La séance porte ses heures réelles, le créneau type
n'étant qu'une référence facultative.

## Planification

`RG-32` Le programme porte **une ligne par brigade**, y compris quand plusieurs
partagent la même séance.

`RG-33` La génération **n'aligne jamais** les progressions.

`RG-33 bis` Le programme couvre **le centre entier** pour une semaine.

`RG-40` Les lignes d'une **séance regroupée** partagent créneau, lieu — ou absence
de lieu — matière et instructeur. La charge de l'instructeur est comptée **une
fois**, le volume **pour chaque brigade**. Le regroupement suppose un lieu de
mode de partage simultané.

`RG-42` **Programme validé non affiché** : retour à brouillon. **Programme
affiché** : la séance porte un **avenant** daté, la validation et la signature
demeurent acquises.

`RG-42 ter` Une séance **reportée** puis tenue n'entame pas le réalisé ; une
**non-exécution** le retranche.

`RG-43` Le classement des remplaçants repose sur des **règles explicites**, jamais
sur un apprentissage : qualification et disponibilité éliminatoires, puis charge
croissante, antériorité sur la brigade, statut. Le critère est **affiché**.

`RG-46` **Aucun affichage sans validation pédagogique et signature du directeur.**

## Évaluations

`RG-48` **Deux types** — formative et certificative — déterminant le décideur de
la date.

`RG-49` La date d'une évaluation certificative est **fixée par le 3ᵉ bureau**. Le
système l'enregistre comme une contrainte subie.

`RG-50` **Deux sujets si certificative, un seul si formative.**

`RG-50 bis` Le sujet retenu est choisi par la **commission d'examen**. La cellule
examens enregistre une décision prise ailleurs.

`RG-52` Une évaluation porte sur **un seul module** et son **périmètre est
explicite** : une session ou une brigade, jamais les deux, jamais aucun.

`RG-52 bis` Une évaluation formative donne lieu à une **séance verrouillée** au
programme.

`RG-53 bis` Une épreuve certificative se déroule **simultanément pour toutes les
brigades**, chacune dans une salle dédiée avec ses propres surveillants. Le
multi-salles est le cas nominal.

`RG-57` Le classement est établi au niveau de la **session**, tous stagiaires
confondus.

`RG-59 bis` **Un seul procès-verbal par fin de formation**, rattaché à la session.

## Suivi et transverse

`RG-60` Le volume réalisé est celui des séances des programmes **affichés**,
**diminué des non-exécutions déclarées**.

`RG-65` Tout attribut déclaratif dont une valeur calculée existe donne lieu à un
**avertissement en cas d'écart, jamais à un refus**. La cible est une intention,
pas une limite.

## Les six contraintes dures

Implantées **une seule fois**, dans `ServiceContraintes`, appelé par la génération,
la modification manuelle, le regroupement et la duplication.

`RG-34` unicité d'affectation de l'instructeur, toutes sessions confondues, sauf
séance regroupée · `RG-35` qualification requise · `RG-36` disponibilité de
l'instructeur · `RG-37` disponibilité et capacité du lieu, la capacité étant
contrôlée dès qu'elle est déclarée, toutes typologies comprises · `RG-38` créneau
ouvert au calendrier compte tenu de la portée · `RG-39` volume prescrit non
dépassé et prérequis achevés.
