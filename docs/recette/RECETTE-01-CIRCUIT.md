# RECETTE-01 — Circuit de validation et ajustements du programme

**Objet.** Le circuit de validation croisée du programme hebdomadaire (soumission, décision, signature, affichage) et tout ce qui modifie un programme après sa génération : modification manuelle, regroupement de brigades, traitement d'une indisponibilité.

**Stories.** US-VAL-03, US-VAL-01, US-VAL-02, US-VAL-04, US-PLAN-05, US-PLAN-06, US-PLAN-09 — toutes Must. La machine à états de référence est le diagramme **ETA-01** (cinq états, transitions T1 à T10) : en cas d'écart, ETA-01 l'emporte sur le backlog (backlog v11, § 8).

**Cadre.** Plan `PLAN-DE-TESTS-PHASE-6.md`. Jeu `complet`, décrit dans `JEUX-DE-DONNEES-PHASE-6.md`.

| Date d'exécution | Recetteur | Relecteur | Navigateur | Date système | Lundi de W0 |
|---|---|---|---|---|---|
| | | | | | |

---

## 1. Préparation

1. `.\outils\recette\reinitialiser_base_recette.ps1 -Etat complet`. Le rapport de vérification doit annoncer **73/73** (socle) et **47/47** (complet).
2. `python app\manage.py runserver --settings=config.settings.recette`. Mot de passe des comptes : `Transmissions#2026`.
3. Notez le lundi de W0. Les dates données entre parenthèses ci-dessous valent pour un chargement fait **dans la semaine du lundi 26 octobre 2026**. Un autre jour, elles glissent d'autant de semaines : seule la notation W compte.

## 2. Données utilisées

| Objet | État au chargement |
|---|---|
| Programme **W-2** (12/10) | Affiché, validé, signé. Une non-exécution de EXP2 |
| Programme **W-1** (19/10) | Affiché. Séance **regroupée** M2 EXP1 + EXP2, pk = 3, mardi 08:00–09:45, I1, L9. Contrôles E1 (EXP1) et E5 (CDP1) verrouillés le jeudi 08:00 |
| Programme **W0** (26/10) | Affiché. Séance pk = 95 (M6, EXP1) avec deux avenants : déplacement au vendredi 10:10–12:00, et remplacement I6 → I8 |
| Programme **W+1** (02/11) | **Brouillon ne contenant qu'une séance** : le contrôle E2 (M2, EXP2), verrouillé le mercredi 08:00–09:45 |
| W+2, W+3 | Aucun programme. Bivouac de EXP2 jeudi et vendredi de W+2 ; congé centre entier vendredi de W+3 |
| Brigades | S1 (F6) : EXP1 (20, L1), EXP2 (15, L2). S2 (F2) : CDP1 (12, L7) |
| Instructeurs | I1 (M1, M2, M3) · I2 (M1) · I3 (M1, M2) · I5 (M4, M5) · I6 (M6, M8) · I7 (M7) · I8 (M6, M9) · I9 (M3, M9) |
| Lieux partagés | L4 simultané 30 · L5 séquentiel 30 · L9 simultané 60 |

Le programme W+1 est d'abord **complété par une génération** (section 3) : ce sont ses séances qui serviront ensuite tout le circuit.

---

## 3. États et génération préalable — US-VAL-03, US-PLAN-03

Profil : `u_plan`.

| Code | Contrôle | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|
| R01-VAL03-01 | Ouvrir les programmes W-2, W-1, W0 et W+1 | État visible sur chacun : affiché, affiché, affiché, brouillon. W-2 porte la mention de sa validation et de sa signature | US-VAL-03 c.4, US-VAL-04 c.4 | ☐ | |
| R01-VAL03-02 | Écran de lancement de la génération, semaine W0 | Génération indisponible, et l'écran dit pourquoi (programme affiché) | US-VAL-03 c.4, US-PLAN-03 c.8 | ☐ | |
| R01-VAL03-03 | Générer W+1 pour EXP1, EXP2 et CDP1 | Le programme existant est **complété** ; la séance du contrôle E2 (mercredi, EXP2) est **conservée** et toujours verrouillée | US-PLAN-03 c.1, c.7 | ☐ | |
| R01-VAL03-04 | Consulter W+1 jour par jour | Séances du lundi au vendredi seulement : la grille Ordinaire n'a aucun créneau le samedi | US-PLAN-12 c.2 | ☐ | **Point à vérifier** : `JEUX-DE-DONNEES` décrit W-2 comme « pleine sur les six jours ouvrables ». S'il y a des séances le samedi, consultez W-2 et notez-le (NC si la grille active n'a pas de samedi) |
| R01-VAL03-05 | Consulter la matière M8 dans le compte rendu de génération | M8 non placée, avec le motif « prérequis M6 non achevé » | US-PLAN-03 c.3, US-SUI-01 c.7 | ☐ | Le prérequis s'apprécie sur le volume **réalisé** |

## 4. Soumission — US-VAL-01

| Code | Contrôle | Profil | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|---|
| R01-VAL01-01 | Soumettre W+1 | `u_plan` | État **soumis** | US-VAL-01 c.1, c.2 | ☐ | |
| R01-VAL01-02 | Tenter de modifier une séance de W+1 | `u_plan` | Refus, avec l'indication de **retirer la soumission** | US-VAL-01 c.2, US-PLAN-05 c.7 | ☐ | |
| R01-VAL01-03 | Soumettre W+1 une seconde fois | `u_plan` | Commande absente ou refusée | US-VAL-01 c.4 | ☐ | |
| R01-VAL01-04 | Ouvrir la page des programmes en attente ; regarder la navigation | `u_ped` | W+1 y figure, avec la semaine, la date de soumission et son auteur (`u_plan`) ; un **compteur** est visible dans la navigation | US-VAL-01 c.3 | ☐ | |
| R01-VAL01-05 | Retirer la soumission | `u_plan` | W+1 redevient **brouillon** ; il disparaît de la page d'attente de `u_ped` | US-VAL-01 c.5 | ☐ | |
| R01-VAL01-06 | Soumettre à nouveau W+1 | `u_plan` | Soumis | — | ☐ | Préparation de la section 5 |

## 5. Décision de la cellule pédagogique — US-VAL-02

| Code | Contrôle | Profil | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|---|
| R01-VAL02-01 | Consulter W+1, puis W-2 et W0 | `u_ped` | Lecture possible pour toutes les semaines, quel que soit leur état ; l'écart entre volume prescrit et programmé est visible avant décision | US-VAL-02 c.1, SEQ-02 | ☐ | |
| R01-VAL02-02 | Chercher une décision par brigade | `u_ped` | Aucune : la décision porte sur le programme du centre entier | US-VAL-02 c.2 | ☐ | |
| R01-VAL02-03 | Rejeter W+1 **sans motif** | `u_ped` | Refus | US-VAL-02 c.4, RG-45 | ☐ | |
| R01-VAL02-04 | Rejeter W+1 avec le motif « Charge de I1 trop concentrée le lundi » | `u_ped` | État **rejeté** | US-VAL-02 c.4 | ☐ | |
| R01-VAL02-05 | Ouvrir W+1 | `u_plan` | État rejeté, motif visible | US-VAL-02 c.5 | ☐ | |
| R01-VAL02-06 | Modifier une séance de W+1 (déplacer une séance de EXP1 sur un créneau libre) | `u_plan` | La première modification **reprend le programme en correction** : il redevient brouillon, et le motif du rejet reste visible | US-VAL-02 c.4, c.5 | ☐ | |
| R01-VAL02-07 | Tenter de valider W+1 | `u_plan` | Commande absente ou refusée | US-VAL-02 c.6 | ☐ | |
| R01-VAL02-08 | `u_plan` soumet W+1 ; `u_ped` le valide | `u_plan` puis `u_ped` | État **validé**, avec le nom du validateur et la date ; le motif de rejet n'est plus affiché | US-VAL-02 c.3, c.5 | ☐ | |

## 6. Signature et affichage — US-VAL-04

Profil : `u_plan`.

| Code | Contrôle | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|
| R01-VAL04-01 | Chercher l'action d'affichage sur W+1, validé mais non signé | Absente, ou refusée côté serveur | US-VAL-04 c.1, c.3 | ☐ | |
| R01-VAL04-02 | Enregistrer une signature datée de la veille de la validation, puis une datée de demain | Les deux refusées | US-VAL-04 c.2 | ☐ | |
| R01-VAL04-03 | Enregistrer la signature datée d'aujourd'hui, signataire « Directeur de la formation (fictif) » ; puis corriger le nom du signataire | Enregistrée ; la correction est admise tant que le programme n'est pas affiché | US-VAL-04 c.2 | ☐ | |
| R01-VAL04-04 | Afficher W+1 | État **affiché** ; le programme porte la mention de sa validation et de sa signature | US-VAL-04 c.4 | ☐ | |
| R01-VAL04-05 | Chercher toute commande ramenant W+1 à brouillon | Aucune : un programme affiché ne revient jamais à brouillon | US-VAL-03 c.2 | ☐ | |
| R01-VAL04-06 | `u_adm` : journal, objet « programme » W+1 | Chaque transition des sections 4 à 6 : auteur, date, état de départ, état d'arrivée, motif s'il y en a un | US-VAL-03 c.6 | ☐ | |
| R01-VAL04-07 | Tenter une transition interdite : rejeter W0 (affiché) avec `u_ped` | Refus, avec un message qui nomme la règle | US-VAL-03 c.3 | ☐ | |

## 7. Modification manuelle — US-PLAN-05

Profil : `u_plan`. On travaille sur W+2, généré ici, puis sur W0 et W+1, affichés.

| Code | Contrôle | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|
| R01-PLAN05-01 | Générer W+2 pour EXP1, EXP2 et CDP1 | Brouillon ; **aucune séance de EXP2 jeudi et vendredi** (bivouac) ; EXP1 et CDP1 programmés normalement ces jours-là | US-PLAN-04 c.5 | ☐ | |
| R01-PLAN05-02 | Déplacer une séance de EXP1 sur un créneau libre de la même semaine | Acceptée ; la séance apparaît **verrouillée**, identifiable dans le programme | US-PLAN-05 c.1, c.5 | ☐ | |
| R01-PLAN05-03 | Confier une séance de M6 à I7 (non qualifié pour M6) | Refus qui nomme la contrainte (qualification) | US-PLAN-05 c.2, RG-35 | ☐ | |
| R01-PLAN05-04 | Déplacer une séance d'un instructeur sur un créneau où il enseigne déjà à une autre brigade | Refus qui nomme l'instructeur et la séance en conflit | US-PLAN-05 c.2, RG-34 | ☐ | |
| R01-PLAN05-05 | Ajouter une séance de M1 à EXP1 sur un créneau libre | Acceptée et verrouillée | US-PLAN-05 c.4, c.5 | ☐ | |
| R01-PLAN05-06 | Noter le volume programmé de M1 pour EXP1, supprimer la séance ajoutée au contrôle 05, puis relire | Volume programmé diminué de la durée de la séance | US-PLAN-05 c.4 | ☐ | |
| R01-PLAN05-07 | Déverrouiller la séance déplacée au contrôle 02, puis régénérer W+2 pour EXP1 | La séance déverrouillée peut être remplacée ; les séances encore verrouillées sont conservées | US-PLAN-05 c.5, US-PLAN-03 c.7 | ☐ | |
| R01-PLAN05-08 | Changer le lieu d'une séance de M2 (lieu partagé) de L4 vers L9, puis vers L1 | L9 accepté (catégorie conforme) ; L1 refusé (salle attitrée d'une autre brigade) | US-PLAN-05 c.3 | ☐ | |
| R01-PLAN05-09 | Basculer une séance de M2 vers une activité sans lieu (M3) | Acceptée. Le système ne l'a **jamais proposé de lui-même** | US-PLAN-05 c.3 | ☐ | |
| R01-PLAN05-10 | Tenter de modifier une séance de W0 **déjà passée** (lundi de W0) | Refus : une séance commencée n'est plus modifiable | US-PLAN-05 c.1 | ☐ | |
| R01-PLAN05-11 | Soumettre W+2 (`u_plan`) ; le valider (`u_ped`) ; puis modifier une séance de W+2 (`u_plan`) | La modification exige d'abord l'**annulation de la validation**, motivée et confirmée. Après confirmation, W+2 redevient brouillon et doit être soumis à nouveau. Rien n'est annulé implicitement | US-PLAN-05 c.8, RG-42 | ☐ | |
| R01-PLAN05-12 | Sur W0 (affiché), changer l'instructeur d'une séance **future** de EXP2 (jeudi ou vendredi) | Acceptée ; un **avenant** daté, motivé et typé est porté ; W0 reste affiché, validation et signature acquises | US-PLAN-05 c.9 | ☐ | |
| R01-PLAN05-13 | Sur W0, supprimer une séance future | Refus, avec un renvoi vers la déclaration de non-exécution | US-PLAN-05 c.9 | ☐ | |
| R01-PLAN05-14 | Ouvrir la séance pk = 95 (M6, EXP1, W0) | Deux avenants : déplacement vers **vendredi 10:10–12:00**, et remplacement I6 → I8, chacun avec son motif, son auteur et sa date | US-PLAN-05 c.9 | ☐ | Le jeu annonçait « jeudi » ; le report au vendredi est documenté (repli du chargeur) |
| R01-PLAN05-15 | Sur W+1 (affiché), tenter de déverrouiller puis de supprimer la séance du contrôle E2 | Les deux refusés | US-PLAN-05 c.5 | ☐ | |

## 8. Regroupement de brigades — US-PLAN-06

Profil : `u_plan`. Sur W+2, brouillon (après le contrôle R01-PLAN05-11).

| Code | Contrôle | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|
| R01-PLAN06-01 | Choisir une séance de M2 de EXP1 et demander à y associer d'autres brigades | Seules les brigades pour lesquelles M2 est programmable sur ce créneau sont proposées : EXP2 oui, **CDP1 non** (M2 hors de son référentiel) | US-PLAN-06 c.1 | ☐ | |
| R01-PLAN06-02 | Associer EXP2 alors que la séance est en L4 (capacité 30, effectifs 20 + 15) | Refus, avec l'écart chiffré (35 > 30) | US-PLAN-06 c.4 | ☐ | |
| R01-PLAN06-03 | Placer la séance en L9 (60), puis associer EXP2 | Acceptée ; une ligne par brigade, rattachées à la même séance | US-PLAN-06 c.2 | ☐ | |
| R01-PLAN06-04 | Choisir une séance de M7 (laboratoire séquentiel L5) et demander un regroupement | Refusé ou non proposé : un lieu séquentiel n'accueille pas de regroupement | US-PLAN-06 c.7, RG-40 | ☐ | |
| R01-PLAN06-05 | Modifier le créneau de la séance regroupée | Confirmation demandée, après **énumération des brigades** concernées | US-PLAN-05 c.6 | ☐ | |
| R01-PLAN06-06 | Retirer EXP2 du regroupement | La ligne de EXP2 disparaît et son créneau est libéré ; **aucune séance autonome** n'est créée pour EXP2 | US-PLAN-06 c.6 | ☐ | |
| R01-PLAN06-07 | Charge de I1 sur W-1 (écran de charge d'un instructeur) | La séance regroupée pk = 3 (EXP1 + EXP2) n'est comptée **qu'une fois** | US-PLAN-06 c.3, US-INS-04 c.5 | ☐ | |
| R01-PLAN06-08 | Sur W0 (affiché), associer CDP1 ou une autre brigade à une séance future en lieu partagé, puis tenter d'en retirer une | L'association porte un avenant. Le retrait est refusé, avec un renvoi vers la non-exécution | US-PLAN-06 c.8 | ☐ | S'il n'y a aucun candidat programmable, noter SO et la raison |

## 9. Traitement d'une indisponibilité — US-PLAN-09

Profil : `u_plan`. À ce stade : W0 et W+1 sont affichés, W+2 est en brouillon.

| Code | Contrôle | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|
| R01-PLAN09-01 | Déclarer I1 indisponible du **lundi au vendredi de W+1**, motif « mission » | **Immédiatement**, la liste des séances non commencées de I1 sur cette période, **toutes brigades confondues**, avec l'état du programme de chacune (affiché) | US-PLAN-09 c.1 | ☐ | |
| R01-PLAN09-02 | Quitter l'écran, puis revenir à cette indisponibilité | La liste reste consultable | US-PLAN-09 c.1 | ☐ | |
| R01-PLAN09-03 | Étendre la période jusqu'au mercredi de W+2 | La liste est recalculée et inclut les séances de W+2 (brouillon) | US-PLAN-09 c.1, CU-P4-03 A3 | ☐ | |
| R01-PLAN09-04 | Choisir une séance de M2 de W+1 ; voir les trois voies proposées | Remplacer, substituer, déprogrammer | US-PLAN-09 c.2 | ☐ | |
| R01-PLAN09-05 | Demander les remplaçants | Uniquement des instructeurs qualifiés pour M2 et libres sur le créneau (I3 s'il est libre) ; jamais I1, jamais un instructeur déjà en séance | US-PLAN-09 c.3 | ☐ | |
| R01-PLAN09-06 | Remplacer par I3 sur cette séance de W+1 (affiché) | Accepté ; un **avenant** est porté ; W+1 reste affiché | US-PLAN-09 c.6 | ☐ | |
| R01-PLAN09-07 | Sur une autre séance de W+1, choisir « déprogrammer » | Refus, avec un renvoi vers la non-exécution | US-PLAN-09 c.6 | ☐ | |
| R01-PLAN09-08 | Sur une séance de I1 en W+2 (brouillon), substituer une autre matière ; noter les matières proposées | Seules des matières du référentiel respectant prérequis et volume ; **M8 n'est pas proposée** (M6 non achevée) | US-PLAN-09 c.4 | ☐ | |
| R01-PLAN09-09 | Traiter en lot toutes les séances de M1 de I1 en W+2 avec un remplaçant, en choisissant un remplaçant **occupé sur l'une d'elles** | Refus de l'ensemble : **aucune séance n'est modifiée**, et le refus nomme la séance et la contrainte | US-PLAN-09 c.5 | ☐ | |
| R01-PLAN09-10 | Recommencer le lot avec un remplaçant libre sur toutes les séances | Confirmation globale, puis toutes remplacées | US-PLAN-09 c.5 | ☐ | |
| R01-PLAN09-11 | Soumettre W+2 ; traiter une séance de W+2 ; retirer la soumission | Tant que W+2 est soumis, le traitement renvoie au retrait de la soumission | US-PLAN-09 c.6 | ☐ | |
| R01-PLAN09-12 | Déclarer I6 indisponible sur une période qui inclut **aujourd'hui avant l'heure actuelle** | Les séances de I6 déjà commencées ne figurent **pas** dans la liste à traiter | US-PLAN-09 c.7 | ☐ | S'il n'y a aucune séance de I6 aujourd'hui, choisir un instructeur qui en a une le matin |
| R01-PLAN09-13 | Programme de W+1 après le contrôle 06 | Aucune séance de W+1 n'est confiée à I1 pendant sa période ; toute résolution a respecté les contraintes | US-PLAN-09 c.8 | ☐ | Les séances non traitées restent visibles dans la liste |

## 10. Habilitations du circuit

| Code | Contrôle | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|
| R01-HAB-01 | `u_df` ouvre les programmes W-2 à W+2 | Lecture seule ; aucune commande de soumission, de décision, de signature, de modification | US-ADM-03 c.2 | ☐ | |
| R01-HAB-02 | `u_ped` cherche les commandes de génération, de modification et de signature | Absentes ; un appel direct est refusé | matrice § 11.2 | ☐ | |
| R01-HAB-03 | `u_exa` ouvre la consultation d'un programme | Conforme à la matrice : refus, la cellule examens ne lit pas le programme (test PLAN-07) | matrice, D-280 | ☐ | Noter le comportement observé |

---

## 11. Dépouillement

| Section | Contrôles | C | NC majeur | NC mineur | B | SO |
|---|---|---|---|---|---|---|
| 3. États et génération | 5 | | | | | |
| 4. Soumission | 6 | | | | | |
| 5. Décision | 8 | | | | | |
| 6. Signature et affichage | 7 | | | | | |
| 7. Modification manuelle | 15 | | | | | |
| 8. Regroupement | 8 | | | | | |
| 9. Indisponibilité | 13 | | | | | |
| 10. Habilitations | 3 | | | | | |
| **Total** | **65** | | | | | |

☐ Prononcée ☐ Prononcée sous réserve (rejeu le ______) ☐ Refusée

**Observations :**

## 12. Matrice critère → contrôles

| Story | Critère | Contrôles |
|---|---|---|
| US-VAL-03 | c.2 transitions ETA-01 | VAL04-05, VAL04-07 |
| | c.3 refus motivé | VAL04-07 |
| | c.4 état visible, génération | VAL03-01, VAL03-02 |
| | c.6 journal des transitions | VAL04-06 |
| US-VAL-01 | c.1 à c.5 | VAL01-01 à 06 |
| US-VAL-02 | c.1 à c.6 | VAL02-01 à 08 |
| US-VAL-04 | c.1 à c.4 | VAL04-01 à 04, VAL03-01 |
| US-PLAN-05 | c.1 | PLAN05-02, PLAN05-10 |
| | c.2 | PLAN05-03, PLAN05-04 |
| | c.3 | PLAN05-08, PLAN05-09 |
| | c.4 | PLAN05-05, PLAN05-06 |
| | c.5 | PLAN05-02, PLAN05-07, PLAN05-15 |
| | c.6 | PLAN06-05 |
| | c.7 | VAL01-02 |
| | c.8 | PLAN05-11 |
| | c.9 | PLAN05-12 à 14 |
| US-PLAN-06 | c.1 à c.8 | PLAN06-01 à 08 |
| US-PLAN-09 | c.1 à c.8 | PLAN09-01 à 13 |

Hors champ ici : US-VAL-03 c.1 (cinq états) se lit dans l'ensemble du cahier ; c.5 (droits par état et profil) dans la section 10 et RECETTE-05.

## 13. Fiche d'anomalie

Modèle commun : `RECETTE-00-SOCLE.md`, § 12 (code `R01-…`).

---

*RECETTE-01 — version 1 du 28 octobre 2026. Lot WBS 6.3.*
