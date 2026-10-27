"""Jeu de données de recette — état `socle` (sprint 2, Prompt 34) et état
`complet` (Prompt 51, Temps 2).

DISTINCT du jeu de démonstration (`ressources.jeu_demonstration`, Prompt 15) :
celui-ci montre le système, celui-ci le recette. Le contenu du `socle` est
dicté par le § 4.2 du cahier de recette du sprint 2, pas par le réalisme —
voir `docs/suivi/JEU-RECETTE.md`.

Vit dans `evaluations`, pas dans `planification` ni `ressources` : à l'état
`socle` (Prompt 34), `planification` suffisait — `--verifier` (§ 5) lit
`planification.models.ProgrammeHebdomadaire`, et `planification` était la
seule application dont l'ordre de dépendance couvrait à la fois
`referentiel`, `organisation`, `ressources` et elle-même
(`tests/architecture/test_couches.py`). L'état `complet` (Prompt 51) crée
des évaluations, sujets, organisations d'épreuve et notes — `planification`
n'a pas le droit d'importer `evaluations`, seul `evaluations` couvre tout
le périmètre nécessaire aux deux états à la fois. Déplacé du premier au
second lors du prompt 51 plutôt que scindé en deux paquets : voir
docs/suivi/DECISIONS.md, D-297.
"""
