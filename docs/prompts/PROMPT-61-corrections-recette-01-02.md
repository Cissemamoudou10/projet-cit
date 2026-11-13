# Prompt 61 — Corrections de RECETTE-02 et des restes de RECETTE-01

**Contexte.** Diagnostic du prompt 60 reçu et arbitré par le chef de projet. Ce lot corrige 8 anomalies et ajoute 3 améliorations d'ergonomie peu coûteuses. **B-A6 n'est pas une anomalie** : RG-59 bis est respectée, c'est le cahier qui se trompait. Aucune correction de code pour B-A6 ; le cahier est corrigé de mon côté.

**Organisation, impérative.** Le recetteur **joue RECETTE-03** pendant que tu travailles.
- Travaille dans un **worktree séparé**. Ne touche jamais au répertoire principal, ni à `pfe_cit_recette`.
- Pendant le développement : tests ciblés seulement.
- **Pas de suite complète, pas de fusion, pas d'étiquette avant mon feu vert explicite.** Je te le donnerai quand RECETTE-03 sera terminée.
- Tu ne modifies jamais toi-même les permissions de `.claude/`.

Temps 0 : une ligne dans `heures-phase-6.md`. **Temps limité : 16 heures**, estimation faite avant de commencer ; au-delà, arrête-toi et propose ce qu'on retire de la partie B.

---

## A. Corrections, dans cet ordre

| N° | Anomalie | Correction validée | Exigences |
|---|---|---|---|
| L1 | **B-A3** | `except ErreurMetier` généralisé dans **toutes** les vues d'`evaluations` | Cherche aussi dans les autres applications toute vue qui appelle un service métier sans rattraper `ErreurMetier` : liste-les et corrige-les. Plus aucune exception métier ne doit produire une page 500 |
| L2 | **B-A5** | `conflits()` et `conflits_de_l_epreuve()` retournent des dicts via `avertissement()` | Le calcul des avertissements se fait **dans la même transaction** que l'écriture de la date, ou alors le changement ne peut plus échouer après écriture : explique ton choix |
| L3 | **A4** | `_verifier_lieu_partage` vérifie la **catégorie réelle** du lieu et refuse la **salle attitrée d'une autre brigade** | Une seule implantation, appliquée aux 5 chemins manuels. Explique pourquoi les tests de K2 (prompt 58) n'ont pas vu ce cas, et ajoute les tests qui l'auraient vu : M7 en L1 refusée, M2 en L1 refusée pour EXP2, M2 en L9 acceptée |
| L4 | **A12** | Message RG-40 dédié au lieu séquentiel ; regroupement non proposé quand `mode_partage == SEQUENTIEL` | Même fichier que L3, même relecture |
| L5 | **B-A2** | Vue POST, URL et bouton de suppression d'une évaluation | Confirmation explicite (BNF-09) qui nomme l'évaluation et sa séance ; refus D-240 affichés en message |
| L6 | **B-A4** | Formulaire « retenir ce sujet » sur la ligne du sujet **non** retenu | Motif obligatoire ; test par le vrai cycle HTTP |
| L7 | **A13** | Champs nature et motif d'avenant dans le formulaire d'association, lus par `_appliquer_association` | Sur un programme affiché, l'association porte un avenant visible (K9) sans annuler validation ni signature ; sur un brouillon, pas de champ d'avenant ; le retrait reste refusé sur un programme affiché |
| L8 | **B-A1** | Périmètre par défaut selon le type (brigade pour la formative, session pour la certificative), modifiable ; avertissement serveur pour le périmètre session | La valeur par défaut doit aussi exister **sans JavaScript** (valeur initiale du formulaire) ; le JS ne fait que la suivre au changement de type |
| L9 | Données : **E3 hors grille** | Le chargeur `complet` place E3 sur un créneau réel de la grille Ordinaire | `--verifier` contrôle qu'aucune séance ni épreuve du jeu n'est hors grille |

## B. Ergonomie retenue

| N° | Demande | Solution validée |
|---|---|---|
| L10 | **Listes filtrées** (demande répétée en RECETTE-01 et 02) | Ta proposition : données de qualification et de catégorie de lieu chargées dans la page, **filtrage côté client** sans aller-retour, dans la création d'évaluation et dans les formulaires de séance (ajout, modification, substitution). Le serveur reste seul juge. Sans JavaScript, la liste complète reste utilisable |
| L11 | Créneau affiché sur la fiche d'une épreuve | Un champ dans le gabarit |
| L12 | Bouton « fixer le créneau » qui déborde | Correctif CSS dans la charte, sans style en ligne |

**Reportés en perspective** (une ligne chacun dans `ECARTS-LIVRABLES-PHASE-6.md`) : recherche et pagination de la saisie des notes ; brigades de sessions terminées ou hors session masquées ; effectif attendu modifiable en ligne.

## Tests

Un test par correction, par le vrai cycle HTTP quand c'est un écran. **Tests navigateur** (`-m navigateur`) pour L8 et L10 : le filtrage et la valeur par défaut fonctionnent dans Chromium. La preuve sur la session entière (prompt 56) doit toujours passer.

## Fin, après mon feu vert seulement

1. Relecture `relecteur-conception` de L2, L3 et L7.
2. Suite complète seule sur la machine (P-51), `-m pdf` en conteneur, `-m navigateur`.
3. Commits séparés : L1-L2 ; L3-L4 ; L5-L6 ; L7 ; L8 ; L9 ; partie B ; documentation (`PROBLEMES.md`, décisions, écarts pour le backlog v12).
4. Fusion, étiquette **`recette-phase-6-c7`**, suppression du worktree.
5. Donne : la vérification de `complet`, le nombre de tests, `git describe --tags`, et la liste des contrôles à rejouer dans RECETTE-01 et RECETTE-02.
