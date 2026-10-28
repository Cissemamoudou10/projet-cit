# RECETTE-03 — Suivi et clôture

**Objet.** La traçabilité entre le prescrit et le réalisé, qui porte l'objectif OS4 : déclaration des non-exécutions, rapprochement prescrit, programmé et réalisé, alertes, tableau de bord, document de progression réalisée. S'y ajoute la clôture d'une session.

**Stories.** US-SUI-05, US-SUI-01, US-SUI-06 (Must) · US-SUI-02, US-SUI-03, US-SES-09 (Should).

**Cadre.** Plan `PLAN-DE-TESTS-PHASE-6.md`. Jeu `complet`, décrit dans `JEUX-DE-DONNEES-PHASE-6.md`.

| Date d'exécution | Recetteur | Relecteur | Navigateur | Date système | Lundi de W0 |
|---|---|---|---|---|---|
| | | | | | |

---

## 1. Préparation

1. `.\outils\recette\reinitialiser_base_recette.ps1 -Etat complet` : vérification à 73/73 et 47/47.
2. Windows pour tout le cahier, sauf les contrôles **[PDF]**, joués dans le conteneur (`outils/recette/lancer_recette_conteneur.ps1`, prompt 52), sur la même base.
3. **Ce cahier dépend du jour et de l'heure.** Le réalisé ne compte que les séances **passées** des programmes affichés. Notez la date et l'heure en tête : un contrôle de réalisé se recalcule à la main au moment où il est joué.

## 2. Données utilisées

| Objet | Contenu |
|---|---|
| S1 (F6, 05/10 → 25/12) | EXP1 (20), EXP2 (15). 39 stagiaires : 35 affectés, 4 non affectés dont 1 radié |
| S2 (F2, 05/10 → 11/12) | CDP1 (12). Une seule évaluation, E5, notes incomplètes |
| **S3** (F2, 03/08 → 25/09) | CDP9 (8). **Terminée mais non clôturée**, sans aucune évaluation ni programme. Son intitulé « S3 (close) » est un mnémonique : son état en base est « ouverte » |
| Non-exécution n° 1 | EXP2, séance M6 du lundi de W-2 (12/10) 08:00, motif « Instructeur en mission » |
| Non-exécution n° 2 | **Ligne de EXP2 seulement** sur la séance regroupée pk = 3 (M2, mardi de W-1, 20/10, 08:00), motif « Brigade de garde ». La ligne de EXP1 reste exécutée |
| Avenants en W0 | Séance pk = 95 (M6, EXP1) déplacée au vendredi 10:10–12:00, instructeur I6 → I8 |
| Progression réalisée | Une édition de W-2, par `u_plan`, non signée |
| Programmes | W-2, W-1, W0 affichés ; W+1 en brouillon (seule la séance du contrôle E2) |

---

## 3. Déclarer une non-exécution — US-SUI-05

Profil : `u_plan` sauf indication contraire.

| Code | Contrôle | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|
| R03-SUI05-01 | Sur W-1, choisir une séance passée de EXP1 (pas la séance regroupée) et déclarer sa non-exécution **sans motif** | Refus : motif obligatoire | US-SUI-05 c.2 | ☐ | |
| R03-SUI05-02 | Même séance, motif « Instructeur malade » | Déclarée ; journalisée avec auteur et horodatage | US-SUI-05 c.2, c.5 | ☐ | Noter la matière et la durée : recalcul en R03-SUI01-03 |
| R03-SUI05-03 | Séance regroupée pk = 3 : déclarer la non-exécution de la ligne de **EXP1** | Déclarée pour la seule ligne de EXP1 ; celle de EXP2 garde sa propre déclaration ; la séance elle-même n'est pas touchée | US-SUI-05 c.2 | ☐ | Annuler aussitôt cette déclaration pour la suite |
| R03-SUI05-04 | Déclarer la non-exécution d'une séance **future** de W0 (vendredi) | Refus : seule une séance passée se déclare | US-SUI-05 c.2 | ☐ | |
| R03-SUI05-05 | Déclarer la non-exécution de la séance de E2 dans W+1 (brouillon) | Refus : le programme n'est pas affiché | US-SUI-05 c.1, RG-60 | ☐ | |
| R03-SUI05-06 | Annuler la déclaration du contrôle 02 ; puis la redéclarer | Annulation admise (session non clôturée) ; redéclaration admise | US-SUI-05 c.4 | ☐ | |
| R03-SUI05-07 | Chercher la commande de déclaration avec `u_ped` | Absente ou refusée : la saisie relève de la planification | US-SUI-05 c.6 | ☐ | |

## 4. Rapprochement prescrit, programmé et réalisé — US-SUI-01

Profil : `u_ped` sauf indication contraire.

| Code | Contrôle | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|
| R03-SUI01-01 | Ouvrir le rapprochement de S1 | Pour EXP1 et EXP2, chaque matière de F6 avec trois volumes : prescrit, programmé, réalisé | US-SUI-01 c.1 | ☐ | |
| R03-SUI01-02 | Lire l'écart d'une matière | En heures **et** en pourcentage | US-SUI-01 c.3 | ☐ | |
| R03-SUI01-03 | **Recalcul à la main**, EXP2, M6 : somme des séances de M6 de EXP2 passées dans W-2, W-1 et W0 avant maintenant, moins la séance non exécutée de W-2 | Le réalisé affiché est égal au recalcul | US-SUI-01 c.2, RG-60 | ☐ | Écrire le détail du calcul en Obs. |
| R03-SUI01-04 | M2 : comparer le réalisé de EXP1 et celui de EXP2 sur la séance regroupée pk = 3 | Compté pour EXP1, **retranché pour EXP2** | US-SUI-01 c.2, RG-60 | ☐ | |
| R03-SUI01-05 | Séance pk = 95 (avenants) : si l'heure actuelle a dépassé vendredi 12:00 de W0, vérifier qu'elle compte au réalisé de M6 pour EXP1 ; sinon, vérifier qu'elle n'y compte pas encore | Une séance sous avenant compte au réalisé dès qu'elle est passée | US-SUI-01 c.2 | ☐ | |
| R03-SUI01-06 | Filtrer par formation, par session, par brigade, puis par période (W-2 seule) | Les quatre filtres opèrent ; sur W-2 seule, le réalisé de M6 de EXP2 exclut la séance non exécutée | US-SUI-01 c.4 | ☐ | |
| R03-SUI01-07 | Ouvrir le rapprochement de **S3** | CDP9 présentée **à part, « sans programme affiché »**, jamais comme un réalisé nul assimilé à un retard | US-SUI-01, D-108 (R5/E1) | ☐ | |
| R03-SUI01-08 | Ouvrir le rapprochement avec `u_plan`, `u_exa`, `u_df` puis `u_adm` | Les trois premiers en lecture ; `u_adm` refusé | US-SUI-01 c.5 (v11) | ☐ | |
| R03-SUI01-09 | `u_ped` affecte à EXP2 l'un des non-affectés de S1 | L'affectation **signale le volume déjà dispensé** à EXP2 | US-SUI-01 c.6 | ☐ | |
| R03-SUI01-10 | `u_plan` génère W+1 pour EXP1 ; lire le compte rendu | M8 écartée : prérequis M6 **non achevé au sens du réalisé** (M6 réalisé < 40 h) | US-SUI-01 c.7 | ☐ | |

## 5. Alertes sur les écarts — US-SUI-02

Profil : `u_ped`.

| Code | Contrôle | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|
| R03-SUI02-01 | Ouvrir la liste des alertes ; noter le seuil en vigueur | Seuil exprimé en pourcentage du prescrit (10 % par défaut) ; les matières au-delà du seuil sont listées | US-SUI-02 c.1, c.2 | ☐ | |
| R03-SUI02-02 | Lire la nature de chaque alerte | Retard et dépassement sont distingués | US-SUI-02 c.3 | ☐ | |
| R03-SUI02-03 | Recalculer une alerte de retard en cours de session | Elle se mesure par rapport au volume programmé **déjà échu** (séances terminées des programmes affichés), pas au prescrit total | US-SUI-02 c.5 | ☐ | |
| R03-SUI02-04 | `u_plan` déclare des non-exécutions supplémentaires sur des séances passées de M6 de EXP2, jusqu'à ce que l'écart dépasse le seuil ; `u_ped` recharge | Une alerte de **retard** apparaît pour M6, EXP2 ; le compteur de la navigation pédagogique augmente | US-SUI-02 c.2, c.6 | ☐ | |
| R03-SUI02-05 | `u_plan` annule ces non-exécutions ; `u_ped` recharge | L'alerte **disparaît**, le compteur revient | US-SUI-02 c.4 | ☐ | |
| R03-SUI02-06 | `u_ped` réduit le volume prescrit de M7 dans F6 en dessous du volume déjà réalisé par une brigade ; recharge | Alerte de **dépassement**, signalée même si les contraintes l'empêchent normalement (D-283). Remettre 30 h | US-SUI-02 c.5 | ☐ | Si aucune brigade n'a encore de réalisé en M7, choisir une matière qui en a |

## 6. Tableau de bord — US-SUI-03

| Code | Contrôle | Profil | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|---|
| R03-SUI03-01 | Ouvrir le tableau de bord | `u_df` | EXP1, EXP2, CDP1 présentes ; **CDP9 absente** (sa session est terminée depuis le 25/09) | US-SUI-03 c.1 | ☐ | |
| R03-SUI03-02 | Recalculer le taux d'avancement de CDP1 : réalisé total ÷ prescrit de F2 (20 h) | Égal à l'affichage | US-SUI-03 c.1 | ☐ | |
| R03-SUI03-03 | Nombre de matières achevées, en cours et non commencées pour EXP1 | Cohérent avec le rapprochement : une matière est achevée quand son réalisé atteint le prescrit | US-SUI-03 c.2 | ☐ | |
| R03-SUI03-04 | Pendant que l'alerte de R03-SUI02-04 est active, ouvrir le tableau de bord | EXP2 mise en évidence | US-SUI-03 c.3 | ☐ | À jouer entre SUI02-04 et SUI02-05, ou rejouer SUI02-04 |
| R03-SUI03-05 | Ouvrir le tableau de bord avec `u_ped`, `u_plan`, `u_exa`, puis `u_adm` | Les trois premiers en lecture ; `u_adm` refusé | US-SUI-03 c.4 | ☐ | |

## 7. Progression réalisée hebdomadaire — US-SUI-06

Profil : `u_plan`.

| Code | Contrôle | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|
| R03-SUI06-01 | Ouvrir l'édition existante de W-2 | Consultable, avec sa date d'édition et son auteur (`u_plan`), non signée | US-SUI-06 c.6 | ☐ | |
| R03-SUI06-02 | Éditer W-1 | Pour chaque brigade et chaque matière : programmé de la semaine et réalisé. Écarts détaillés : la non-exécution de EXP2 sur la séance regroupée, avec le motif « Brigade de garde » | US-SUI-06 c.1, c.2 | ☐ | |
| R03-SUI06-03 | Éditer W0 | Les deux avenants de la séance pk = 95 figurent avec leur nature et leur motif ; le **déplacement dans la semaine n'est pas un écart** (réalisé inchangé) | US-SUI-06 c.2, c.3 | ☐ | |
| R03-SUI06-04 | Éditer W+1 | Refus : le programme n'est pas affiché | US-SUI-06 c.4 | ☐ | |
| R03-SUI06-05 | Éditer W-1 une seconde fois | Deux éditions conservées ; la plus récente fait foi | US-SUI-06 c.4 | ☐ | |
| R03-SUI06-06 | Enregistrer la signature de l'édition W-1 (date, signataire) | Date et signataire enregistrés | US-SUI-06 c.6 | ☐ | |
| R03-SUI06-07 | Vérifier qu'aucune donnée du document n'a été saisie | Tout est calculé à partir des programmes, des non-exécutions et des avenants | US-SUI-06 c.5 | ☐ | |
| R03-SUI06-08 | [PDF] Produire le PDF de l'édition W-1 ; le relire | Produit à partir du gabarit ; lisible ; aucun débordement ni code interne | US-SUI-06 c.7, RG-58 | ☐ | |

## 8. Clôture d'une session — US-SES-09

Profil : `u_ped` sauf indication contraire.

| Code | Contrôle | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|
| R03-SES09-01 | Clôturer **S1** | Refus : les évaluations non finalisées sont **énumérées** (E1 à E4 : aucune n'a de procès-verbal) | US-SES-09 c.4 | ☐ | |
| R03-SES09-02 | Clôturer **S3** | Clôturée ; auteur et date enregistrés et journalisés | US-SES-09 c.3 | ☐ | |
| R03-SES09-03 | Chercher S3 ou CDP9 dans les listes de sélection : génération (`u_plan`), création d'évaluation (`u_exa`), affectation d'un stagiaire (`u_ped`) | Absentes des trois | US-SES-09 c.1 | ☐ | |
| R03-SES09-04 | Consulter S3, CDP9 et ses stagiaires | Consultables | US-SES-09 c.2 | ☐ | |
| R03-SES09-05 | Chercher une commande de réouverture de S3 | Aucune : limite assumée (D-281) | US-SES-09 c.6 | ☐ | |
| R03-SES09-06 | [PDF] Rendre S2 clôturable : `u_exa` complète les notes de E5 et génère son procès-verbal ; `u_ped` clôture S2 ; `u_plan` tente de déclarer puis d'annuler une non-exécution sur une séance passée de CDP1 | S2 clôturée ; déclaration **et** annulation refusées | US-SES-09 c.4, c.5 | ☐ | Seule évaluation de S2 : E5 |

---

## 9. Dépouillement

| Section | Contrôles | C | NC majeur | NC mineur | B | SO |
|---|---|---|---|---|---|---|
| 3. Non-exécution | 7 | | | | | |
| 4. Rapprochement | 10 | | | | | |
| 5. Alertes | 6 | | | | | |
| 6. Tableau de bord | 5 | | | | | |
| 7. Progression réalisée | 8 | | | | | |
| 8. Clôture | 6 | | | | | |
| **Total** | **42** | | | | | |

☐ Prononcée ☐ Prononcée sous réserve (rejeu le ______) ☐ Refusée

**Observations :**

## 10. Matrice critère → contrôles

| Story | Critères | Contrôles |
|---|---|---|
| US-SUI-05 | c.1 à c.6 | SUI05-01 à 07 ; c.3 (retranché) : SUI01-03, SUI01-04 ; c.4 après clôture : SES09-06 |
| US-SUI-01 | c.1 à c.7 | SUI01-01 à 10 |
| US-SUI-02 | c.1 à c.6 | SUI02-01 à 06 |
| US-SUI-03 | c.1 à c.4 | SUI03-01 à 05 |
| US-SUI-06 | c.1 à c.7 | SUI06-01 à 08 |
| US-SES-09 | c.1 à c.6 | SES09-01 à 06 |

## 11. Fiche d'anomalie

Modèle commun : `RECETTE-00-SOCLE.md`, § 12 (code `R03-…`).

---

*RECETTE-03 — version 1 du 28 octobre 2026. Lot WBS 6.3.*
