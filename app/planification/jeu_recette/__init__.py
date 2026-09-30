"""Jeu de données de recette du sprint 2 — Prompt 34.

DISTINCT du jeu de démonstration (`ressources.jeu_demonstration`, Prompt 15) :
celui-ci montre le système, celui-ci le recette. Son contenu est dicté par le
§ 4.2 du cahier de recette du sprint 2, pas par le réalisme — voir
`docs/suivi/JEU-RECETTE.md`.

Vit dans `planification`, pas dans `ressources` (à la différence du jeu de
démonstration) : `--verifier` (§ 5) lit `planification.models.
ProgrammeHebdomadaire` pour signaler les programmes du sprint 2 déjà en base
— `ressources` n'a pas le droit d'importer `planification`
(`tests/architecture/test_couches.py`), `planification` est la seule
application dont l'ordre de dépendance couvre à la fois `referentiel`,
`organisation`, `ressources` ET elle-même.
"""
