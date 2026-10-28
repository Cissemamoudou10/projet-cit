# RECETTE-04 — Pilotage de la planification

**Objet.** Les outils qui aident la planification et la pédagogie à piloter : écarts de volume avant soumission, duplication d'un programme, liste et historique des programmes, charge des instructeurs, historique du référentiel.

**Stories.** US-PLAN-07, US-PLAN-11, US-VAL-05, US-INS-04, US-REF-09 — **toutes Should**. Si le temps manque, ce cahier est le premier qu'on réduit (plan, § 8).

**Cadre.** Plan `PLAN-DE-TESTS-PHASE-6.md`. Jeu `complet`, décrit dans `JEUX-DE-DONNEES-PHASE-6.md`.

| Date d'exécution | Recetteur | Relecteur | Navigateur | Date système | Lundi de W0 |
|---|---|---|---|---|---|
| | | | | | |

---

## 1. Préparation

1. `.\outils\recette\reinitialiser_base_recette.ps1 -Etat complet` : vérification à 73/73 et 47/47.
2. `python app\manage.py runserver --settings=config.settings.recette`.
3. `u_plan` génère W+1 pour EXP1, EXP2 et CDP1.

## 2. Données utilisées

| Objet | Contenu |
|---|---|
| Programmes | W-2 et W-1 affichés (chronologie simulée : générés le jeudi, validés le vendredi, signés et affichés le samedi de la semaine précédente). W0 affiché avec deux avenants. W+1 en brouillon |
| W-1 | Séance regroupée pk = 3 (M2, EXP1 + EXP2, I1, L9) ; contrôles E1 (EXP1) et E5 (CDP1) le jeudi ; non-exécution de la ligne de EXP2 sur pk = 3 |
| Calendrier | Bivouac de **EXP2** jeudi et vendredi de **W+2** ; **congé centre entier** le vendredi de **W+3** |
| S3 | Terminée le 25/09, aucun programme |
| E3 | Épreuve du mardi de W+5 ; **I8** y est surveillant de EXP1 |

---

## 3. Écarts de volume horaire — US-PLAN-07

Profil : `u_plan`.

| Code | Contrôle | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|
| R04-PLAN07-01 | Consulter W+1 (brouillon) avant soumission | Pour chaque matière : prescrit et programmé cumulé | US-PLAN-07 c.1, c.4 | ☐ | |
| R04-PLAN07-02 | Lire l'indicateur des matières de S1, en cours de session | « En cours », jamais « sous-programmé » tant que la session n'est pas finie | US-PLAN-07 c.5 | ☐ | |
| R04-PLAN07-03 | `u_ped` réduit M7 dans F6 en dessous du volume déjà **programmé** pour EXP1 ; `u_plan` recharge | Écart signalé visuellement comme **sur-programmation**, avec le seuil de 10 %. Remettre 30 h | US-PLAN-07 c.2, c.3 | ☐ | |
| R04-PLAN07-04 | Consulter les écarts de CDP9 (S3, terminée sans aucun programme) | Sous-programmation signalée : la session est finie | US-PLAN-07 c.3, c.5 | ☐ | Si S3 n'apparaît dans aucun écran d'écart, noter SO avec l'écran consulté |
| R04-PLAN07-05 | Ouvrir l'indicateur avec `u_exa` | Refus | matrice | ☐ | |

## 4. Duplication d'un programme — US-PLAN-11

Profil : `u_plan`.

| Code | Contrôle | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|
| R04-PLAN11-01 | Dupliquer **W0 → W+2**, pour EXP1, EXP2 et CDP1 | Programme W+2 créé en **brouillon**, modifiable ; séances reportées sur les créneaux équivalents | US-PLAN-11 c.1, c.2 | ☐ | |
| R04-PLAN11-02 | Lire la liste des séances écartées | Les séances de **EXP2 du jeudi et du vendredi** sont écartées, motif « bivouac » (période bloquante) | US-PLAN-11 c.3, c.4 | ☐ | |
| R04-PLAN11-03 | Comparer le volume cumulé après duplication au prescrit | Dépassement éventuel **signalé** | US-PLAN-11 c.5 | ☐ | |
| R04-PLAN11-04 | Dupliquer **W-1 → W+3**, pour EXP1 seulement | Le **contrôle E1** et toute séance non exécutée de EXP1 ne sont **pas** dupliqués et figurent dans la liste des séances écartées ; les séances du vendredi sont écartées pour le congé centre entier | US-PLAN-11 c.3, c.6, c.7 | ☐ | |
| R04-PLAN11-05 | Dupliquer vers W0 (affiché), puis vers W+1 après l'avoir soumis | Les deux refusées ; retirer ensuite la soumission de W+1 | US-PLAN-11 c.2 | ☐ | |
| R04-PLAN11-06 | Vérifier le verrouillage des séances dupliquées ; régénérer W+2 pour EXP1 | Les séances dupliquées ne sont **pas** verrouillées : la régénération peut les remplacer | US-PLAN-11 c.7 | ☐ | |
| R04-PLAN11-07 | Sur W+2, chercher un instructeur sur deux séances simultanées | Aucun : toutes les contraintes dures ont été vérifiées sur la semaine cible | US-PLAN-11 c.3 | ☐ | |

## 5. Liste et historique des programmes — US-VAL-05

| Code | Contrôle | Profil | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|---|
| R04-VAL05-01 | Ouvrir la liste des programmes ; filtrer par état (affiché), puis par période | `u_ped` | Toutes les semaines avec leur état ; filtres opérants ; chaque programme accessible | US-VAL-05 c.1 | ☐ | |
| R04-VAL05-02 | Historique de W-2 | `u_ped` | Génération, soumission, validation, signature, affichage : chacun avec auteur, date et motif s'il y en a un ; dates dans l'ordre chronologique simulé (jeudi, vendredi, samedi de W-3) | US-VAL-05 c.2, c.3 | ☐ | |
| R04-VAL05-03 | Faire un cycle sur W+1 : `u_plan` soumet ; `u_ped` rejette (motif) ; `u_plan` modifie et resoumet ; `u_ped` valide | `u_plan`, `u_ped` | L'historique de W+1 présente soumission, rejet avec motif, reprise, resoumission et validation, **dans l'ordre chronologique** | US-VAL-05 c.4 | ☐ | |
| R04-VAL05-04 | Ouvrir la liste avec `u_plan`, `u_df` puis `u_exa` | — | Conforme à la matrice : lecture pour `u_plan` et `u_df` ; noter le comportement pour `u_exa` | US-VAL-05, D-280 | ☐ | |

## 6. Charge d'un instructeur — US-INS-04

Profil : `u_plan`.

| Code | Contrôle | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|
| R04-INS04-01 | Charge de **I1** sur W-1 | Heures sur la période, avec le détail par matière | US-INS-04 c.1, c.2 | ☐ | |
| R04-INS04-02 | Recompter la charge de I1 sur W-1 à la main | La séance regroupée pk = 3 n'est comptée **qu'une fois** | US-INS-04 c.5 | ☐ | |
| R04-INS04-03 | Comparer I1, I6 et I8 sur la période W-2 → W0 | Comparables entre eux sur la même période | US-INS-04 c.3 | ☐ | |
| R04-INS04-04 | Repérer un instructeur dont la moyenne hebdomadaire dépasse 24 h, s'il y en a un | Signalé ; sinon, aucun signalement | US-INS-04 c.4 | ☐ | Seuil par défaut : 24 h/semaine, hypothèse à confirmer avec le terrain |
| R04-INS04-05 | Charge de **I8** sur une période qui inclut W+5 | La surveillance de E3 est présentée **à part**, sans s'ajouter à la charge d'enseignement | US-INS-04 c.6 | ☐ | Si I8 n'est pas surveillant de E3 (voir R02-EVAL04-01), prendre le surveillant référencé réellement affecté |
| R04-INS04-06 | Ouvrir la charge avec `u_ped` et `u_df` | Accès conforme à la matrice | CU-P4-04 | ☐ | |

## 7. Historique du référentiel — US-REF-09

Profil : `u_ped`.

| Code | Contrôle | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|
| R04-REF09-01 | Porter M6 dans F6 de 40 à 42 h ; ouvrir l'historique du référentiel de F6 | Modification enregistrée avec auteur, date, **valeur avant (40) et après (42)** | US-REF-09 c.1, c.3 | ☐ | Remettre 40 h |
| R04-REF09-02 | Renommer M9 ; ouvrir l'historique de M9 | L'historique **suit la matière après le renommage** : les entrées d'avant le renommage sont toujours là | US-REF-09 c.2 | ☐ | |
| R04-REF09-03 | Ajouter puis supprimer un prérequis dans F6 ; ouvrir l'historique du prérequis | Création et suppression visibles | US-REF-09 c.2 | ☐ | |
| R04-REF09-04 | Chercher une commande de modification ou de suppression d'une entrée d'historique | Aucune | US-REF-09 c.4 | ☐ | |
| R04-REF09-05 | Historique d'une matière du socle (M1) | Il ne commence qu'à la mise en service de la fonction : aucune modification antérieure n'est reconstituée | US-REF-09 c.5 | ☐ | Limite assumée (D-286) |

---

## 8. Dépouillement

| Section | Contrôles | C | NC majeur | NC mineur | B | SO |
|---|---|---|---|---|---|---|
| 3. Écarts de volume | 5 | | | | | |
| 4. Duplication | 7 | | | | | |
| 5. Liste et historique | 4 | | | | | |
| 6. Charge | 6 | | | | | |
| 7. Historique du référentiel | 5 | | | | | |
| **Total** | **27** | | | | | |

Toutes les stories étant Should, un NC majeur ici **ne bloque pas C3** s'il est consigné avec sa mesure (plan, § 9). Il bloque le prononcé du cahier.

☐ Prononcée ☐ Prononcée sous réserve (rejeu le ______) ☐ Refusée

**Observations :**

## 9. Matrice critère → contrôles

| Story | Critères | Contrôles |
|---|---|---|
| US-PLAN-07 | c.1 à c.5 | PLAN07-01 à 05 |
| US-PLAN-11 | c.1 à c.7 | PLAN11-01 à 07 |
| US-VAL-05 | c.1 à c.4 | VAL05-01 à 04 |
| US-INS-04 | c.1 à c.6 | INS04-01 à 06 |
| US-REF-09 | c.1 à c.5 | REF09-01 à 05 |

## 10. Fiche d'anomalie

Modèle commun : `RECETTE-00-SOCLE.md`, § 12 (code `R04-…`).

---

*RECETTE-04 — version 1 du 28 octobre 2026. Lot WBS 6.3.*
