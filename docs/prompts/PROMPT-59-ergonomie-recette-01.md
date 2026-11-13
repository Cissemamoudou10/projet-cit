# Prompt 59 — Lot 2 de RECETTE-01 : créneau, avenants, non-exécution

**Contexte.** Le prompt 58 a traité le lot 1 et K11. Ce prompt traite le reste du lot 2, reporté pour tenir le budget. **Prérequis : le prompt 58 est fusionné et étiqueté `recette-phase-6-c5`.** Même organisation que le 58 : worktree séparé si le recetteur joue une recette ; suite complète seulement après mon feu vert.

Temps 0 : une ligne dans `heures-phase-6.md`. **Temps limité : 6 heures.** Estime avant de commencer ; au-delà, arrête-toi et propose.

---

| N° | Constat (RECETTE-01) | Correction attendue |
|---|---|---|
| **K8 = A2** | Une séance déplacée à 14:45–16:00 (le créneau est 14:40–16:00) est acceptée sans message, puis **n'apparaît plus** sur le programme | (1) Dans l'ajout et la modification manuelle d'une séance, **le recetteur choisit un créneau de la grille active** (liste des créneaux du jour), au lieu de saisir des heures. Nouvelle décision qui fait évoluer RG-64 (D-133) en le disant. (2) **Plus jamais de séance invisible** : une séance déjà hors grille (données anciennes, duplication depuis une autre grille, grille changée en cours de semaine) s'affiche dans une ligne « hors grille » de son jour, à l'écran et à l'impression |
| **K9 = A5** | Sur un programme affiché, l'avenant (remplacement I6 → I8) n'est consultable nulle part depuis la séance | (1) Les avenants d'une séance sont **visibles sur son écran** (« Modifier ») : nature, motif, auteur, date, valeur avant et après. (2) Dans la liste des avenants du programme, chaque avenant **nomme sa séance** : jour, créneau, brigade, matière. (3) Une séance qui porte un avenant est repérable dans la grille (marque discrète, de la charte) |
| **K10 = A7** | Sur une séance d'un programme affiché, rien n'explique comment déclarer qu'elle n'aura pas lieu | Sur une séance **future** d'un programme affiché : un message court dit que la déclaration de non-exécution sera possible une fois la séance passée, et que d'ici là, un changement passe par un avenant (remplacement ou déplacement). Sur une séance **passée** : le lien de déclaration, inchangé |

**Tests.** K8 : le formulaire ne propose que les créneaux de la grille active ; une séance hors grille créée directement en base s'affiche dans la ligne « hors grille », à l'écran et à l'impression. K9 : avenant visible sur la séance et nommé dans la liste. K10 : message sur une séance future, lien sur une séance passée. Un test navigateur (`-m navigateur`) pour la ligne « hors grille » à l'impression.

**Fin.** Relecture `relecteur-conception` de K8. Après mon feu vert : suite complète seule sur la machine, `-m pdf`, `-m navigateur`. Commits séparés (K8 ; K9 ; K10 ; documentation : `PROBLEMES.md`, décision RG-64, écarts backlog v12). Étiquette **`recette-phase-6-c6`**. Donne la liste des contrôles à rejouer.
