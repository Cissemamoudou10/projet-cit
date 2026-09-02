# Charte graphique et composants

## État

`BRIEF-CLAUDE-DESIGN.md` est le brief à remettre à Claude Design, accompagné des
cinq wireframes rendus en PNG depuis `docs/diagrammes/`.

Les livrables attendus en retour se déposent ici :

| Fichier | Contenu |
|---|---|
| `tailwind.config.js` | Palette, typographies, espacements, rayons |
| `composants.html` | Les 46 composants avec leurs états et leur balisage |
| `CHARTE.md` | Règles d'emploi, en une page |
| `ecrans/` | Les 5 écrans de démonstration |
| `impression.css` | Feuille de style d'impression, paysage |
| `icones/` | Les SVG, nommés en français |

## Quand

Pendant le **sprint 1**, en parallèle du socle. Pas avant : une charte se décide
mieux sur un premier écran réel que dans le vide.

## Après réception

Le HTML produit est autonome. Il faut le transposer en gabarits Django — blocs,
inclusions, boucles. Comptez une demi-journée de travail mécanique.

Une fois en place, la règle `.claude/rules/gabarits.md` renvoie Claude Code ici :
il reprendra les classes existantes au lieu d'en inventer.
