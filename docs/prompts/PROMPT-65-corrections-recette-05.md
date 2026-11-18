# Prompt 65 — Corrections de RECETTE-05 (dernier lot avant le gel)

**Contexte.** RECETTE-05 est jouée. Deux retours du recetteur, tous deux sur l'écran du programme hebdomadaire. Ce sont des corrections de présentation : **aucune règle métier, aucun modèle, aucune migration ne change**. Après ce lot, le code est gelé (C3). Travaille dans un worktree. Aucune remise à zéro de base, aucun arrêt de processus, aucune modification de tes permissions.

Temps 0 : une ligne dans `heures-phase-6.md`. **Temps limité : 3 heures.**

## E-A1 — Impression du programme hebdomadaire (R05-IMP-01, NC mineur)

**Constat.** Le bouton « Imprimer » du programme imprime aussi l'interface : boutons, historique, rubriques d'écarts, navigation.

**Attendu.** Le bouton « Imprimer » ouvre une **vue d'impression dédiée**, qui ne contient que le programme :
- **toute la semaine, toutes les brigades** du programme, avec le même filtre de brigades que l'écran s'il y en a un ;
- en-tête : semaine (du lundi au samedi), état du programme, date et signataire s'il est signé ; rien d'autre ;
- **A4 paysage**, mise en page condensée et lisible : une section par jour (brigades en lignes, créneaux en colonnes, chaque case donnant matière, instructeur et lieu en abrégé), saut de page entre deux jours **seulement si nécessaire**, police d'au moins 8 pt, bordures fines, sans couleur de fond pleine (économie d'encre) ;
- aucune case ne doit être coupée entre deux pages (`break-inside: avoid` sur les lignes) ;
- aucun bouton, menu, historique ni rubrique d'écart, ni à l'écran de cette vue ni à l'impression.

L'impression par journée (D-157) reste possible si elle existe déjà ; la vue de la semaine devient le bouton principal. Consigne la décision dans `DECISIONS.md`.

**Preuve** (tests `navigateur`, Playwright, comme D-301) : sur le jeu `complet`, trois brigades, **aucun débordement horizontal** en A4 paysage et nombre de pages relevé ; sur une fixture de 32 brigades, relève le nombre de pages et dis-le-moi, sans seuil bloquant. Vérifie aussi qu'aucun élément d'interface n'apparaît dans le rendu imprimé.

## E-A2 — Rubriques repliables sur l'écran du programme (ergonomie)

**Constat.** Les rubriques « Écarts de volume horaire — prescrit / programmé » et « Historique » occupent tout le haut de la page ; il faut défiler jusqu'en bas pour voir le programme.

**Attendu.** Ces deux rubriques sont **repliables**, avec une flèche qui indique leur état, et **repliées par défaut**. Leur titre reste visible et affiche un résumé (par exemple le nombre d'écarts signalés et le nombre d'entrées d'historique), pour qu'une alerte ne soit jamais cachée sans trace. Même technique que le menu du compte (`<details>`, sans dépendance), et même composant pour les deux rubriques.

**Preuve** : test `navigateur` — rubriques repliées au chargement, dépliées au clic, programme visible sans défilement sur un écran de 1366 × 768 avec trois brigades.

## Fin

Relecture `relecteur-conception`. Suite complète seule (P-51), `-m pdf` en conteneur, `-m navigateur`. Un commit par anomalie, puis un commit de documentation (`PROBLEMES.md`, `DECISIONS.md`, `ECARTS-LIVRABLES-PHASE-6.md`), qui inclut aussi `docs/recette/RECETTE-05-TRANSVERSE.md` tel qu'il est dans le répertoire principal. Fusion, étiquette **`recette-phase-6-c11`**. Donne-moi : nombre de tests, `git describe --tags`, nombre de pages imprimées (3 brigades et 32 brigades), et une capture de la vue d'impression.
