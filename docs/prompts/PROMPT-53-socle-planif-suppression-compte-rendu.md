# Prompt 53 — État `socle-planif`, suppression d'un programme en brouillon, compte rendu de génération consultable

**Contexte.** RECETTE-00 a été jouée jusqu'à la section 7. Pour la section 8 (planification), le recetteur a généré la mauvaise semaine (W0 au lieu de W+1) et n'a pu ni annuler ni supprimer le brouillon obtenu. Le chef de projet a donc décidé :
1. de sortir les sections 8 et 9 de RECETTE-00 pour en faire un cahier à part, **RECETTE-00 bis**, sur un état de départ dédié, `socle-planif` (Temps 1) ;
2. deux évolutions demandées par le recetteur, que RECETTE-00 bis contrôlera :
   - **pouvoir supprimer un programme en brouillon** (Temps 2) ;
   - **un compte rendu de génération consultable après coup, et condensé** : NC sur R00-GEN-03 (Temps 3).

Ce sont les seules modifications applicatives de ce prompt. **Les autres constats de RECETTE-00 ne sont pas traités ici** : ils seront corrigés ensemble, à la fin de RECETTE-00 bis.

Dépose d'abord dans `docs/recette/` les fichiers fournis : `RECETTE-00-SOCLE.md` (mise à jour) et `RECETTE-00-BIS-PLANIFICATION.md`.

---

## Temps 0 — Relevé d'heure

Une ligne dans `docs/suivi/heures-phase-6.md`, notée avant d'ouvrir le premier fichier.

## Temps 1 — État `socle-planif` (outillage)

`charger_jeu_recette --etat socle-planif` = l'état `socle` inchangé, **plus ce que les sections 3 à 7 de RECETTE-00 construisent par l'interface**, et **aucun programme**. Mêmes règles que le prompt 51 : tout passe par les services, horloge simulée pour le passé, dates relatives à `D`, données fictives.

| Objet | Contenu |
|---|---|
| Session `S0` | F1, du lundi de W-1 au vendredi de W+10, effectif attendu 40 |
| Brigades | `EXP1` (20, salle attitrée L1), `EXP2` (15, salle attitrée L2) |
| Stagiaires | Les lignes de `01-valide-10.csv` et `03-valide-45-colonnes-permutees.csv`, importées par le **service d'import** (55 stagiaires), dont **1 radié** (motif et date). Répartition : 20 dans EXP1, 15 dans EXP2, 19 non affectés |
| Date des affectations | **Le lundi de W-1, par horloge simulée**, pour qu'un déplacement ou un retrait soit possible le jour de la recette. *Le recetteur a constaté qu'une affectation faite le jour même ne peut être déplacée qu'un jour plus tard (constat R00-SES-14/15, traité à la séance de corrections) : le jeu ne doit pas en hériter* |
| Calendrier | Conférence **centre entier**, mardi de W+1, 08:00–09:45, **bloquante** · Congé centre entier, vendredi de W+3 |
| Indisponibilités | `I1` du **jeudi de W+1 au lundi de W+2**, motif « mission » (la période fusionnée de R00-RES-08) · `L5` indisponible le lundi et le mardi de W+2 |
| Objectifs | Deux objectifs pédagogiques sur M3, ordres 1 et 2 |
| Programmes | **Aucun** |

Ajoute `socle-planif` au paramètre `-Etat` de `outils/recette/reinitialiser_base_recette.ps1`. Le script doit être enregistré **en UTF-8 avec BOM** et **exécuté réellement sous Windows PowerShell 5.1** (`powershell.exe`, pas `pwsh`) pour les quatre états. C'est le défaut constaté le 29/10, dont tu consignes la correction dans `PROBLEMES.md` si ce n'est pas déjà fait. Étends `--verifier` et le test du chargeur à cet état. Documente l'état dans `JEUX-DE-DONNEES-PHASE-6.md`.

## Temps 2 — Supprimer un programme en brouillon (évolution)

**Besoin.** La cellule planification peut se tromper de semaine ou de sélection à la génération. Aujourd'hui, rien ne permet de défaire un brouillon : seule la régénération le complète. Le chef de projet ajoute la suppression, **strictement limitée au brouillon qui n'est jamais entré dans le circuit**.

**Règles.**

| N° | Règle |
|---|---|
| S1 | Seule la permission d'écriture du programme (cellule planification) peut supprimer |
| S2 | Le programme doit être à l'état **brouillon** et n'avoir **jamais été soumis** : aucune transition du circuit au journal. Un brouillon issu d'un rejet ou d'un retrait de soumission a une histoire de validation : sa suppression effacerait la trace du circuit, elle est **refusée**, avec la marche à suivre (le modifier, ou le régénérer) |
| S3 | Refus si le programme porte une **séance de contrôle** (évaluation formative) : le refus énumère les évaluations concernées. La séance d'un contrôle ne se supprime que par la suppression de l'évaluation (D-240) |
| S4 | **Confirmation explicite** (BNF-09) qui nomme la semaine, les brigades et le nombre de séances supprimées |
| S5 | Suppression **atomique** du programme, de ses séances et de ses lignes, dans une seule transaction, par un service. Respecte la règle « une seule main écrit » des tests d'architecture : choisis le service qui porte déjà l'écriture du programme et justifie ce choix |
| S6 | **Journalisée** : nouvelle nature de journal (suppression d'un programme), avec la semaine, les brigades, le nombre de séances et l'auteur. Le journal n'est pas touché par la suppression (RG-27) |
| S7 | Après suppression, la semaine se génère de nouveau comme si rien n'avait existé |

**Écran.** Un bouton « Supprimer ce brouillon » sur la consultation du programme, visible seulement quand S1 et S2 sont réunies. Sinon, il est absent : jamais grisé sans explication.

**Tests.** Nominal par le vrai cycle HTTP ; refus pour chacun des états soumis, validé, rejeté et affiché ; refus pour un brouillon ayant une histoire de circuit ; refus S3 ; refus pour `u_ped` ; entrée de journal ; régénération possible après suppression ; test d'architecture à jour.

**Traçabilité.** Consigne une décision dans `DECISIONS.md` (numéro relu, pas supposé) : « suppression d'un programme en brouillon jamais soumis, évolution demandée en recette par le chef de projet ». Ajoute un écart dans `docs/suivi/ECARTS-LIVRABLES-PHASE-6.md` (fichier à créer, même gabarit que celui du sprint 4) : le backlog v11 (US-PLAN-03) devra recevoir un critère nouveau.

## Temps 3 — Compte rendu de génération consultable et condensé (NC R00-GEN-03)

**Constat du recetteur.** Le compte rendu s'affiche juste après la génération (adresse `/planification/generer/?semaine=…`). Dès qu'on clique sur « consulter le programme », on ne sait plus où le retrouver. Et il est **trop long** pour être lu.

**Ce qui est attendu.**

| N° | Exigence |
|---|---|
| C1 | Après une génération, l'utilisateur arrive sur la **consultation du programme**, avec un **résumé** en tête : séances placées, séances non placées, brigades traitées |
| C2 | Le compte rendu détaillé de la **dernière génération** de la semaine reste **consultable depuis la page du programme**, à tout moment, tant que le programme existe |
| C3 | Il est **condensé** : les séances non placées sont **regroupées par motif**, puis par brigade et matière, avec un décompte. Le détail ligne par ligne est replié par défaut et dépliable. On voit d'un coup d'œil *pourquoi* des cases sont vides |
| C4 | Les motifs restent ceux d'aujourd'hui : la règle violée et l'élément en cause (US-PLAN-03 c.9, CU-P5-02 E1) |

Pour C2, il faut conserver le compte rendu : les motifs d'une génération passée ne se recalculent pas après coup. Conserve **la dernière génération seulement** par programme, écrasée à chaque nouvelle génération, sous la forme la plus simple qui respecte les conventions du projet. Justifie le choix, et consigne une décision. Réutilise les composants de la charte (pas de style en ligne). La suppression du programme (Temps 2) supprime son compte rendu.

**Tests.** C1 par le cycle HTTP ; C2 : consultable après navigation ailleurs, et remplacé par une nouvelle génération ; C3 : regroupement et décompte justes sur un jeu de test qui produit plusieurs motifs ; mesure du nombre de requêtes de la page du programme, constant avec le nombre de brigades.

## Temps 4 — Contrôle, étiquette, commit

1. Relecture par `relecteur-conception` des Temps 2 et 3.
2. Suite complète, **seule sur la machine** (P-51), plus `pytest -m pdf` en conteneur.
3. Commits séparés : état `socle-planif` ; suppression ; compte rendu ; documentation.
4. Pose **une nouvelle étiquette `recette-phase-6-c1`** sur le dernier commit. `recette-phase-6` ne bouge pas : c'est la base de RECETTE-00 sections 3 à 7, déjà jouées.
5. Mets à jour le nombre de tests dans `AVANCEMENT.md`.
6. Clôture la ligne de `heures-phase-6.md`.

## Rendu attendu

- La commande `-Etat socle-planif` et le rapport de `--verifier`.
- La preuve que le script tourne sous PowerShell 5.1.
- Les règles S1 à S7 et C1 à C4 telles qu'implantées, et tout écart.
- Les numéros de décision ouverts.
- Ce que tu as tranché seul, et ce que tu n'as pas pu vérifier.
