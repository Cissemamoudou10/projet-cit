# Prompt 44 — Ouverture du sprint 4 : correctif P-42, US-SUI-05, US-SUI-01

Phase 5, sprint 4, du 12 au 24 octobre 2026 — dernier sprint de développement,
jalon J3 le 24. Trois temps, trois commits, **un seul rendu à la fin**.

Références qui font foi, dans la base de connaissances : **backlog produit v10**
et **registre des risques v7**, tous deux du 10 octobre. Le backlog v10 a
réécrit les critères des stories du sprint 3 ; ceux des stories ci-dessous sont
cités tels qu'il les porte.

Règles inchangées : arrêt sur les seules conditions écrites ici ; pour tout
autre écart, tu tranches selon les trois principes d'arbitrage, tu consignes,
tu continues ; aucun numéro de décision cité de mémoire ; heure de début de
session écrite avant toute autre action.

---

## Temps 0 — Ouvrir le sprint

1. **`docs/suivi/sprint-4.md`**, sur le gabarit des sprints précédents :

   | Ordre | Élément | Points | Priorité | Porteur |
   |---|---|---|---|---|
   | 0 | Correctif P-42 et mesure de stabilité de la suite | — | — | |
   | 1 | US-SUI-05 — Déclarer la non-exécution d'une séance | 2 | Must | |
   | 2 | US-SUI-01 — Consulter le rapprochement prescrit et réalisé | 5 | Must | |
   | 3 | US-SUI-06 — Éditer la progression réalisée hebdomadaire | 3 | Must | |
   | 4 | US-EVAL-05 — Saisir et vérifier les notes | 5 | Must | |
   | 5 | US-EVAL-06 — Calculer moyennes et classement | 5 | Must | |
   | 6 | US-EVAL-07 — Générer les procès-verbaux de résultats | 5 | Must | |
   | 7 | US-PLAN-07 — Signaler les écarts de volume horaire | 3 | Should | |
   | 8 | US-VAL-05 — Consulter les programmes et l'historique des validations | 5 | Should | |
   | 9 | US-SES-09 — Clôturer une session | 3 | Should | |
   | 10 | US-SUI-02 — Être alerté des écarts significatifs | 3 | Should | |
   | 11 | US-SUI-03 — Consulter le tableau de bord des formations | 5 | Should | |
   | 12 | US-INS-04 — Consulter la charge d'un instructeur | 3 | Should | |
   | 13 | US-REF-09 — Historiser les modifications du référentiel | 3 | Should | |
   | 14 | US-PLAN-11 — Dupliquer un programme hebdomadaire | 5 | Should | |

   Totaux : 14 stories, **55 points** — 25 Must, 30 Should. US-PLAN-08 reste
   déclassée et rejoint la réserve. US-EVAL-11, nouvelle en v10, va aussi en
   **réserve**.
   La colonne **Porteur** reste vide : elle est à remplir par l'étudiant
   (mesure de R16). Écris-le en tête du fichier.
   Sous le tableau, le **point de décision du mercredi 21 octobre au soir** :
   toute story Should non commencée à cette date passe en réserve, pour
   préserver la phase de tests qui commence le 26.

2. **`docs/suivi/heures-sprint-4.md`** : mêmes colonnes que celui du sprint 3.
   En tête, la règle nouvelle du registre v7 (R23) : *la colonne « heures
   humaines » est remplie par l'étudiant au moment où il transmet le prompt,
   avec l'heure de transmission ; l'outil ne la remplit jamais.*

3. **`AVANCEMENT.md`** : ligne du sprint 4 (14 stories, 55 points, J3) ;
   réserve à 9 stories, 39 points, dont US-PLAN-08 déclassée et US-EVAL-11 ; périmètre total 61 stories, 263 points ;
   échéance du **16 octobre** pour le retour des cellules sur ETA-01 (R1), à
   « Ce qu'il faut surveiller ».

4. **Champ « Auteur » des décisions** : à partir de ce prompt, il nomme le
   porteur inscrit dans `sprint-4.md` pour la story concernée. Si la colonne
   est vide, écris « porteur non renseigné » plutôt qu'un nom par défaut.

Pas de commit séparé : ces fichiers vont avec le temps 1.

---

## Temps 1 — Correctif P-42 : ordre de verrouillage du traitement en lot

Défaut de production, non de test (registre v7, R26).

1. Dans le traitement en lot d'US-PLAN-09, verrouille les programmes concernés
   **dans l'ordre croissant de leur identifiant**, une seule fois chacun, avant
   toute écriture.
2. **Inventaire** : tout autre chemin qui verrouille plus d'un programme ou plus
   d'une ligne de même table dans une transaction. Ouvre les fichiers. S'il en
   existe, même règle ; liste-les.
3. **Test** : un lot couvrant trois programmes, transmis dans un ordre mélangé ;
   les requêtes capturées montrent les verrous posés en ordre croissant.
   Prouve qu'il échoue sans le tri, puis rétablis.
4. **Mesure de stabilité** : cinq exécutions complètes et consécutives de la
   suite, après le correctif. Rends les cinq résultats, échecs nommés. Ne
   corrige pas d'échec intermittent ici : consigne-le.

Commit : `fix(planification): ordre de verrouillage déterministe du lot (P-42)`.

---

## Temps 2 — US-SUI-05 : Déclarer la non-exécution d'une séance

2 points · Must · BF-SUI-05 · CLS-05 § 6.7 · RG-60.

**Critères (backlog v10)**

| # | Critère |
|---|---|
| C1 | Une séance d'un programme affiché est réputée exécutée : seule la non-exécution se déclare |
| C2 | La déclaration porte sur une séance passée, avec un motif obligatoire ; pour une séance regroupée, elle porte sur la ligne d'une brigade |
| C3 | Le volume de la séance est retranché du réalisé de la matière pour la brigade concernée |
| C4 | La déclaration est réversible tant que la session n'est pas clôturée |
| C5 | Journalisée avec son auteur et son horodatage |
| C6 | Saisie par la cellule planification |

**Arbitrages**

- **S1 — Rattachée à la ligne, pas à la séance** (CLS-05 § 6.7) : une séance
  regroupée peut n'avoir été manquée que par une brigade. Au plus une
  non-exécution par ligne, garanti en base ; motif non vide en base.
- **S2 — Séance passée = terminée.** Fin de la séance antérieure à l'instant de
  la déclaration. Programme affiché seulement ; tout autre état est refusé, avec
  la règle nommée.
- **S3 — Ce n'est pas une écriture de séance.** La déclaration n'écrit ni
  `Seance` ni `LigneProgramme` : elle ne passe pas par la porte unique, mais par
  un service dédié de `planification`, qui vérifie l'état du programme.
- **S4 — Réversibilité.** La clôture de session n'existe pas encore (US-SES-09,
  même sprint). D'ici là, la déclaration est réversible sans condition ; prévois
  la garde comme une fonction qu'US-SES-09 complétera, et ouvre le report.
- **S5 — L'écran.** Depuis la consultation de la semaine affichée, sur chaque
  ligne d'une séance passée : « Déclarer non exécutée » et, une fois déclarée,
  la mention, le motif et « Annuler la déclaration ». Le refus de suppression
  d'une séance affichée (US-PLAN-05) renvoie désormais à cette action.
- **S6 — Nature de journal.** Réutilise une nature existante si l'une convient
  ; sinon une nouvelle, comptée hors RG-26 et ajoutée au registre des écarts.

**Tests attendus** : base (doublon sur une ligne, motif blanc) ; service
(séance future refusée ; programme non affiché refusé ; regroupée, une seule
brigade déclarée ; annulation ; volume retranché par le calcul du temps 3) ;
habilitations (pédagogique, examens, Direction : refusés en service et en HTTP)
; HTTP (déclaration puis affichage de la mention ; POST sans motif ; POST sur
une séance future forgé).

Commit : `feat(planification): US-SUI-05 déclaration de non-exécution`.

---

## Temps 3 — US-SUI-01 : Consulter le rapprochement prescrit et réalisé

5 points · Must · BF-SUI-01 · CU-P6-11 · RG-60, RG-61 · **objectif OS4**.

**Critères (backlog v10)**

| # | Critère |
|---|---|
| C1 | Par brigade et par matière : prescrit, programmé, réalisé |
| C2 | Réalisé = séances des programmes affichés, moins les non-exécutions ; une séance portant un avenant compte au réalisé |
| C3 | Écart en heures et en pourcentage du prescrit |
| C4 | Filtres : formation, session, brigade, période |
| C5 | Consultable par la cellule pédagogique et la Direction de Formation |
| C6 | L'affectation d'un stagiaire à une brigade signale le volume déjà dispensé à cette brigade |
| C7 | Le prérequis d'une matière est réputé achevé sur le volume **réalisé** ; la définition provisoire sur le volume programmé est remplacée |

**Arbitrages**

- **R1 — Une seule définition du réalisé, paramétrée par une date de
  référence.** Réalisé à la date T = durée des lignes de séances de programmes
  affichés **terminées avant T**, moins celles qui portent une non-exécution.
  Une séance future d'un programme affiché n'est pas encore dispensée : RG-60 ne
  le précisait pas, c'est une précision à consigner comme écart. Écran : T =
  maintenant, ou la fin de la période filtrée. Une fonction, un seul endroit,
  dans le module où vit déjà le calcul de volume ; aucune colonne stockée.
- **R2 — Prérequis (C7) : même fonction, T = lundi de la semaine générée.** Un
  prérequis est achevé quand son réalisé **avant le début de la semaine
  programmée** atteint le prescrit. Les séances de la semaine en cours, si son
  programme est affiché, comptent donc pour générer la suivante : une séance
  affichée est réputée exécutée. Remplace la définition provisoire dans le
  contrôle des prérequis, **sans changer la signature de `ServiceContraintes`**.
  Conséquence assumée : une semaine dont le programme n'est pas encore affiché ne
  fournit aucun prérequis à la suivante. Le compte rendu de génération nomme le
  prérequis non achevé. Question ajoutée au terrain : la semaine suivante se
  prépare-t-elle avant l'affichage de la courante ?
- **R3 — Les tests de la définition provisoire changent, c'est attendu.** Liste
  chacun dans le rendu, avec ce qu'il vérifiait avant et ce qu'il vérifie
  maintenant. **Condition d'arrêt** : si le changement fait échouer des tests de
  génération hors prérequis (lieux, volumes, contraintes d'instructeur), ou fait
  passer la mesure de référence des requêtes au-delà de sa marge, arrête-toi et
  montre-moi.
- **R4 — Programmé** = toutes les séances de la brigade pour la matière, tous
  états de programme confondus (définition déjà en place pour le volume, rejetés
  compris) ; à réutiliser, pas à réécrire.
- **R5 — E1 de la fiche** : sans programme affiché sur la période, l'écran le
  dit explicitement au lieu d'afficher des réalisés nuls comme un retard.
- **R6 — C6** : à l'affectation d'un stagiaire, un avertissement non bloquant
  indique le volume déjà réalisé par la brigade, toutes matières confondues, et
  renvoie au rapprochement. Ferme le report D-108.
- **R7 — Requêtes** : le rapprochement d'une session de dix brigades se calcule
  en un nombre de requêtes indépendant du nombre de brigades et de matières.

**Tests attendus** : calcul (séance passée affichée comptée ; future non ;
non-exécution retranchée ; avenant compté ; regroupée comptée pour chaque
brigade, une fois) ; prérequis (achevé par la semaine précédente affichée ; non
achevé si elle est validée mais pas affichée ; non achevé si une non-exécution
le fait retomber) ; écran (filtres ; E1 ; requêtes constantes avec 2 et 10
brigades) ; habilitations (planification et examens refusés en lecture,
Direction autorisée) ; C6 par le cycle HTTP de l'affectation.

Commit : `feat(suivi): US-SUI-01 rapprochement prescrit et réalisé`.

---

## Suivi et rendu

Pour chaque story : décisions, reports (D-108 fermé ; définition provisoire du
prérequis fermée ; réversibilité de la non-exécution ouverte vers US-SES-09),
écarts (RG-60 précisé par R1), définition de fini complète, relecture
`relecteur-conception` avant chaque commit.

Rendu final, en français, en une fois : les cinq exécutions de la suite ;
l'inventaire des verrous ; les tests modifiés par R3 ; requêtes avant et après ;
reports ouverts et fermés ; ce que tu as tranché seul ; ce que tu n'as pas pu
vérifier.
