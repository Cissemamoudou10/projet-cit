# RECETTE-00 bis — Planification du socle et contrôles transverses

**Objet.** La suite de RECETTE-00 : la génération du programme (sprint 2) et les contrôles transverses du socle. Ces sections ont été sorties de RECETTE-00 le 30/10 pour être jouées sur un état de départ propre. On y contrôle aussi les deux évolutions du prompt 53 : la suppression d'un brouillon et le compte rendu consultable.

**Stories.** US-PLAN-03, US-PLAN-04 (Must) ; US-ADM-03, US-ADM-04 sous l'angle transverse ; évolution « suppression d'un brouillon » (prompt 53, Temps 2) ; correction de R00-GEN-03 (prompt 53, Temps 3).

**Cadre.** Plan `PLAN-DE-TESTS-PHASE-6.md`. Étiquette **`recette-phase-6-c1`**.

| Date d'exécution | Recetteur | Relecteur | Navigateur | Date système | **Lundi de W0** | **Lundi de W+1** |
|---|---|---|---|---|---|---|
| | | | | | | |

> **Avant de commencer, écrivez dans le tableau ci-dessus la date du lundi de W+1.** C'est la semaine que vous sélectionnerez à l'écran de génération dans presque tous les contrôles. Si vous jouez ce cahier dans la semaine du 26/10, W+1 est la semaine du **lundi 2 novembre**. Si vous le jouez à partir du 2 novembre, W+1 est la semaine du **lundi 9 novembre**.

---

## 1. Préparation

1. `.\outils\recette\reinitialiser_base_recette.ps1 -Etat socle-planif`, puis confirmer avec `pfe_cit_recette`.
2. Le rapport de vérification doit être entièrement conforme.
3. `python app\manage.py runserver --settings=config.settings.recette`. Mot de passe : `Transmissions#2026`.

**Si vous vous trompez en cours de route** (mauvaise semaine, mauvaises brigades) : supprimez le brouillon (section 3). Si la situation n'est plus récupérable, recommencez à l'étape 1 : la remise à zéro prend moins de deux minutes.

## 2. Données de départ (`socle-planif`)

C'est exactement ce que vous aviez construit dans RECETTE-00, sections 3 à 7 :

| Objet | Contenu |
|---|---|
| Session `S0` | F1 (M1 20 h, M2 10 h, M3 10 h : **40 h en tout**), du lundi de W-1 au vendredi de W+10 |
| Brigades | `EXP1` (20 stagiaires, salle L1) · `EXP2` (15 stagiaires, salle L2) |
| Calendrier | **Conférence bloquante le mardi de W+1, 08:00–09:45**, centre entier · Congé le vendredi de W+3 |
| Indisponibilités | **I1 du jeudi de W+1 au lundi de W+2** · L5 lundi et mardi de W+2 |
| Instructeurs | I1 (M1, M2, M3, **indisponible** jeudi et vendredi de W+1) · I2 (M1) · I3 (M2) · I4 archivé |
| Lieux | L1, L2 attitrées · L4 partagé simultané · L5 partagé séquentiel |
| Programmes | **Aucun** |

---

## 3. Supprimer un brouillon (évolution du prompt 53)

Profil : `u_plan`. Cette section vient **en premier** : une fois qu'elle est connue, une erreur de génération ne bloque plus le cahier.

| Code | Contrôle | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|
| R00B-SUP-01 | Écran de génération : sélectionner **volontairement la semaine W0**, brigades EXP1 et EXP2 ; générer | Un brouillon est créé pour W0 : c'est l'erreur que vous aviez faite. On va la réparer | US-PLAN-03 c.1 | ☐ | |
| R00B-SUP-02 | Sur la consultation du programme W0, chercher le bouton « Supprimer ce brouillon » ; cliquer | Une confirmation qui nomme **la semaine, les brigades et le nombre de séances** | évolution S4, BNF-09 | ☐ | |
| R00B-SUP-03 | Confirmer | Le programme W0 n'existe plus ; la liste des programmes ne le montre plus | S5 | ☐ | |
| R00B-SUP-04 | `u_adm` : journal | Une entrée « suppression d'un programme » : semaine, brigades, nombre de séances, auteur `u_plan` | S6, RG-26 | ☐ | |
| R00B-SUP-05 | Générer de nouveau W0 pour EXP1, puis le supprimer | Génération normale, comme si rien n'avait existé ; suppression acceptée | S7 | ☐ | Il ne doit rester **aucun programme** à la fin de cette section |
| R00B-SUP-06 | Avec `u_ped`, ouvrir un programme en brouillon (en générer un avec `u_plan` au besoin) | Aucun bouton de suppression ; une adresse directe est refusée | S1 | ☐ | Supprimer ce brouillon ensuite avec `u_plan` |

Les refus sur un programme soumis, validé, rejeté ou affiché se contrôlent en fin de cahier (section 6), quand ces états existent.

## 4. Générer le programme — US-PLAN-03, US-PLAN-04

Profil : `u_plan`. **Toujours la semaine W+1**, celle que vous avez notée en tête du cahier.

| Code | Contrôle | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|
| R00B-GEN-01 | Écran de génération : semaine **W+1**, brigades **EXP1 et EXP2** ; lancer | La grille active (Ordinaire) est indiquée ; un programme **brouillon** est créé pour W+1 | US-PLAN-03 c.1, RG-31 | ☐ | |
| R00B-GEN-02 | Juste après la génération : où arrivez-vous ? | Sur la **consultation du programme W+1**, avec un **résumé** en tête : séances placées, non placées, brigades traitées | correction R00-GEN-03 (C1) | ☐ | |
| R00B-GEN-03 | Ouvrir le compte rendu détaillé depuis la page du programme | Les séances non placées sont **regroupées par motif**, avec un décompte ; le détail est replié et se déplie. La page se lit en une minute | US-PLAN-03 c.9, C3, C4 | ☐ | |
| R00B-GEN-04 | Aller sur une autre page (liste des sessions), puis revenir au programme W+1 et rouvrir le compte rendu | Toujours là, inchangé | C2 | ☐ | |
| R00B-GEN-05 | Consulter le programme W+1 | Une ligne par brigade ; M1 dans la salle attitrée de la brigade (L1 ou L2) ; M3 sans lieu ; M2 dans un lieu partagé (L4 ou L5) | US-PLAN-03 c.4 à c.6, RG-32 | ☐ | |
| R00B-GEN-06 | Regarder le **mardi de W+1 de 08:00 à 09:45** | **Aucune séance** pour EXP1 ni EXP2 : la conférence bloque ce créneau | US-PLAN-04 c.5, RG-38 | ☐ | |
| R00B-GEN-07 | Regarder le **jeudi et le vendredi de W+1** | **Aucune séance confiée à I1** (indisponible). D'autres instructeurs peuvent y avoir des séances | US-PLAN-04 c.5, RG-36 | ☐ | |
| R00B-GEN-08 | Pour chaque créneau de W+1, comparer les instructeurs de EXP1 et de EXP2 | Jamais le même instructeur sur deux séances au même moment | US-PLAN-04 c.1, RG-34 | ☐ | |
| R00B-GEN-09 | Relancer la génération de W+1 pour **EXP1 seule** | Le programme de la semaine est **complété** : les lignes de EXP2 sont intactes ; le compte rendu affiché est celui de cette dernière génération | US-PLAN-03 c.1, C2 | ☐ | |
| R00B-GEN-10 | Générer **W+2** pour EXP1 et EXP2 ; comparer, matière par matière, le volume programmé cumulé de W+1 et W+2 au prescrit (M1 20 h, M2 10 h, M3 10 h) | Aucune matière ne dépasse son prescrit. Une matière épuisée est **écartée**, avec le motif « volume épuisé » dans le compte rendu | US-PLAN-03 c.3, US-PLAN-04 c.6 | ☐ | F1 ne compte que 40 h : l'épuisement est attendu dès W+2 |
| R00B-GEN-11 | Chronométrer une génération (W+1, deux brigades) | Bien en deçà de 5 minutes | BNF-04 | ☐ | Temps : ______ |

## 5. Contrôles transverses du socle

| Code | Contrôle | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|
| R00B-TRV-01 | Avec `u_df`, parcourir les écrans du socle (référentiel, instructeurs, lieux, sessions, stagiaires, calendrier, programme W+1) | Lecture là où la matrice l'accorde ; **aucune commande d'écriture**, pas même grisée | US-ADM-03 c.2 | ☐ | |
| R00B-TRV-02 | Avec `u_plan`, saisir l'adresse de la liste des évaluations | Refus : la planification n'accède à aucune note | US-ADM-03 c.4 | ☐ | |
| R00B-TRV-03 | Se déconnecter, puis saisir directement l'adresse de création d'une session | Redirection vers l'authentification ; rien n'est créé | US-ADM-03 c.6 | ☐ | |
| R00B-TRV-04 | `u_adm` : journal | La génération apparaît avec la semaine, les brigades, les comptes et l'auteur, sans le détail des séances. Les suppressions de la section 3 sont là | RG-26, BNF-14 | ☐ | |
| R00B-TRV-05 | Liste des stagiaires de S0 (55) | Paginée au-delà de vingt, avec recherche | BNF-15 | ☐ | |
| R00B-TRV-06 | Relire trois messages de refus rencontrés dans ce cahier | Chacun dit la cause **et** l'action corrective | BNF-10 | ☐ | |
| R00B-TRV-07 | Aperçu avant impression de la fiche de composition de S0 et de la liste des instructeurs | Colonne Actions masquée ; noter le débordement en pixels | D-63, K3 | ☐ | Connu : Instructeurs 168 px. À consigner, pas à corriger ici |

## 6. Refus de suppression hors brouillon (évolution du prompt 53)

Profils : `u_plan` et `u_ped`. On fait passer W+1 par le circuit pour obtenir chaque état.

| Code | Contrôle | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|
| R00B-SUP-07 | `u_plan` soumet W+1 ; chercher la suppression | Absente ou refusée : programme soumis | S2 | ☐ | |
| R00B-SUP-08 | `u_plan` retire la soumission : W+1 redevient brouillon ; chercher la suppression | **Refusée** : ce brouillon a une histoire de circuit. Le message propose de le modifier ou de le régénérer | S2 | ☐ | |
| R00B-SUP-09 | `u_plan` resoumet ; `u_ped` rejette (motif) ; `u_plan` cherche la suppression | Refusée : programme rejeté | S2 | ☐ | |
| R00B-SUP-10 | `u_plan` modifie et resoumet ; `u_ped` valide ; `u_plan` cherche la suppression | Refusée : programme validé | S2 | ☐ | |
| R00B-SUP-11 | `u_plan` enregistre la signature et affiche ; cherche la suppression | Refusée : programme affiché | S2 | ☐ | |
| R00B-SUP-12 | W+2 (généré en R00B-GEN-10, jamais soumis) : le supprimer | Acceptée : brouillon sans histoire de circuit | S2, S5 | ☐ | |

---

## 7. Dépouillement

| Section | Contrôles | C | NC majeur | NC mineur | B | SO |
|---|---|---|---|---|---|---|
| 3. Supprimer un brouillon | 6 | | | | | |
| 4. Génération | 11 | | | | | |
| 5. Transverses | 7 | | | | | |
| 6. Refus de suppression | 6 | | | | | |
| **Total** | **30** | | | | | |

☐ Prononcée ☐ Prononcée sous réserve (rejeu le ______) ☐ Refusée

Avec les sections 3 à 7 de RECETTE-00, ce cahier forme la recette du socle. Les deux se prononcent ensemble, après la séance de corrections.

**Observations :**

## 8. Correspondance avec l'ancienne numérotation

| Ancien code (RECETTE-00) | Nouveau code |
|---|---|
| R00-GEN-01 | R00B-GEN-01 |
| R00-GEN-02 | R00B-GEN-05 |
| R00-GEN-03 (NC le 30/10) | R00B-GEN-02 à 04 |
| R00-GEN-04 à 06 | R00B-GEN-06 à 08 |
| R00-GEN-07 | R00B-GEN-10 |
| R00-GEN-08 | R00B-GEN-09 |
| R00-GEN-09 | R00B-GEN-11 |
| R00-TRV-01 à 07 | R00B-TRV-01 à 07 |
| — | R00B-SUP-01 à 12 (évolution nouvelle) |

## 9. Fiche d'anomalie

Modèle commun : `RECETTE-00-SOCLE.md`, § 12 (code `R00B-…`).

---

*RECETTE-00 bis — version 1 du 30 octobre 2026. Lot WBS 6.3.*
