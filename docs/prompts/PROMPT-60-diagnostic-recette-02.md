# Prompt 60 — Diagnostic des anomalies de RECETTE-02 et des restes de RECETTE-01 (lecture seule)

**Contexte.** RECETTE-02 (évaluations) a été jouée du 04 au 05/11 sur `recette-phase-6-c4`, état `complet` chargé le 04/11, avec W+1 généré. **Refusée** : 5 NC majeurs, dont 2 à qualifier, et 1 NC mineur. Les dates d'examen, les notes et les procès-verbaux sont conformes.

Dépose dans `docs/recette/` le fichier fourni `RECETTE-02-EVALUATIONS.md` (résultats remplis).

**Diagnostic seulement : ne modifie aucun fichier de code, de test ou de données.** Lecture du code, et requêtes `SELECT` en lecture seule si besoin. Le recetteur peut jouer une recette en même temps : aucun `pytest`, aucune migration, aucune remise à zéro.

---

Pour chaque anomalie : cause exacte (fichier, fonction), critère concerné, **qualification proposée**, correction et estimation.

| N° | Contrôle | Constat |
|---|---|---|
| B-A1 | R02-EVAL01-02 | À la création, en choisissant « formative » puis « certificative », **aucun périmètre n'est proposé par défaut** (attendu : brigade pour la formative, session pour la certificative) ; deux champs libres, session et brigade ; aucun avertissement quand on choisit le périmètre session. US-EVAL-01 c.3 |
| B-A2 | R02-EVAL01-09 | **Aucune commande pour supprimer une évaluation.** Attendu : suppression d'une évaluation non organisée, avec sa séance ; refus pour E3 (organisée, sujet retenu). La suppression existe-t-elle côté service ? US-EVAL-01 c.8, D-240 |
| B-A3 | R02-EVAL01-10 | `u_plan` soumet W+1, puis `u_exa` crée une formative en W+1 : le refus est juste, mais il s'affiche par **une page d'exception Django** (`TransitionProgrammeRefusee` non gérée dans `evaluations.views.vue_creer_evaluation`, levée par `circuit.py::_transition_admise`). En production, ce serait une erreur 500. **Cherche toutes les vues qui appellent un service susceptible de lever `TransitionProgrammeRefusee` ou une autre exception métier sans la convertir en message** |
| B-A4 | R02-EVAL03-03 | Les sujets A (retenu) et B de E3 sont visibles, mais **aucune commande pour retenir B** avec un motif. La fonction existe-t-elle côté service ? US-EVAL-03 c.4, c.5 |
| B-A5 | R02-EVAL04-10 | Changer la date de E3 vers un jour où des séances sont déjà programmées donne d'abord une **erreur 500** : `TypeError: string indices must be integers, not 'str'` sur `POST /evaluations/4/modifier-date/`. Au retour, le changement est enregistré et l'avertissement des conflits s'affiche. Le changement est-il enregistré **avant** l'erreur, donc hors transaction avec l'avertissement ? US-EVAL-04 c.7 |
| B-A6 | R02-EVAL06-02 à 05 | Moyennes de **S1** : « Aucune moyenne calculable pour l'instant ». Moyennes de **S2** : affichées. **E1 apparaît « non prête » (ou « non conforme ») dans la liste des évaluations**, alors que ses 20 stagiaires ont une note ou une absence. Explique : (1) la condition exacte qui rend une moyenne calculable pour un stagiaire (toutes les évaluations de la session notées ? seulement celles déjà passées ? certificatives seulement ?) ; (2) ce que signifie l'état « non prête » de E1 et pourquoi ; (3) si le cahier se trompe en attendant une moyenne pour EXP1 avec E1 seule notée. Cite US-EVAL-06 c.1, c.7 et la décision correspondante |

## Données

- **E3** est chargée à **08:00–10:00**, hors de la grille Ordinaire. Corrige-le dans la proposition pour le chargeur (créneau de la grille).
- R02-EVAL01-05 : le refus « RG-34 : I9 déjà affecté à une séance de M3 (EXP1) le 12/11 10:10–12:00 » vient-il d'une séance masquée par A10 (chevauchement relevé au prompt 58) ? Confirme-le en base.

## Demandes d'ergonomie à estimer (pas à décider)

1. **E1, listes filtrées**, demandée pour la deuxième fois (RECETTE-01 et 02) : instructeurs qualifiés et lieux compatibles selon la matière, dans la création d'évaluation et dans les formulaires de séance. Propose **la solution la moins coûteuse** qui évite au recetteur d'ouvrir un autre compte pour savoir qui enseigne quoi : par exemple un formulaire en deux étapes (matière d'abord), ou un rappel affiché des instructeurs qualifiés et du type de lieu de la matière. Compare avec l'AJAX déjà estimé à 4 à 6 h.
2. Recherche, filtres et pagination sur la saisie des notes.
3. Créneau affiché sur la fiche d'une épreuve.
4. Brigades des sessions terminées masquées à la génération ; brigades hors session masquées dans l'organisation d'une épreuve.
5. Effectif attendu modifiable directement dans l'organisation.
6. Bouton « fixer le créneau » qui déborde.

## Anomalies restantes de RECETTE-01 (rejeu des 06 et 07/11 sur `recette-phase-6-c5` puis `c6`)

Le rejeu de RECETTE-01 a levé A1, A2, A3, A5 à A11. Trois points restent ouverts ; diagnostique-les **avec** RECETTE-02, pour un seul lot de corrections.

| N° | Contrôle | Constat |
|---|---|---|
| A4 (non levée) | R01-PLAN05-08 | **Malgré K2 (prompt 58)**, en modification manuelle d'une séance de W+2, **tous les lieux sont acceptés** : une séance de **M7** (catégorie lieu partagé) a été placée en **L1**, salle attitrée. Deux règles manquent : la **catégorie** du lieu doit correspondre à celle de la matière ; la **salle attitrée d'une autre brigade** est refusée. Explique pourquoi le correctif K2 et ses tests ne couvrent pas ce chemin (écran « Modifier » d'une séance), et vérifie tous les chemins (ajout, modification, substitution, regroupement, duplication) |
| A13 | R01-PLAN06-08 | Sur un programme **affiché** (W+1), l'association d'une brigade est refusée : « La modification d'une séance n'est pas possible sur un programme affiché. Portez un avenant (T10) depuis la modification de la séance. » Or l'écran « Modifier » ne permet pas d'ajouter une brigade : **aucun chemin** ne tient US-PLAN-06 c.8. Correction voulue par le chef de projet : l'association depuis la page « Brigades » de la séance, permise sur un programme affiché, **portant un avenant** (nature, motif, auteur, date), sans annuler validation ni signature ; le retrait d'une brigade y reste refusé avec renvoi vers la non-exécution |
| A12 | R01-PLAN06-04 | Regroupement demandé sur une séance en **L5** (lieu partagé **séquentiel**) : le refus est juste, mais le message dit « RG-37 : L5 est déjà occupé … par EXP1 ». Attendu : un message qui dit qu'un lieu séquentiel n'accueille pas de regroupement (RG-40), et, si possible, ne pas proposer le regroupement du tout pour une séance en lieu séquentiel |

## Rendu

Tableau B-A1 à B-A6, puis A4, A13 et A12 ; les points de données ; les estimations d'ergonomie ; les causes communes avec les anomalies de RECETTE-01 ; un ordre de correction et le total. **Ne corrige rien.**
