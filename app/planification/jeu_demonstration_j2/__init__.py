"""Jeu de données de la démonstration J2 — Prompt 43, partie A.

Vit dans `planification`, pas `ressources` : contrairement au jeu de
démonstration du sprint 1 (`ressources.jeu_demonstration`) et au jeu de
recette du sprint 2 (`evaluations.jeu_recette`), ce jeu pose une SESSION
et une BRIGADE (organisation) pour que l'étape 1 du scénario (générer le
programme d'une semaine) ait quelque chose à programmer — `ressources` ne
peut pas dépendre d'`organisation`, `planification` le peut déjà (DEPENDANCES_
AUTORISEES, tests/architecture/test_couches.py).

Distinct des deux jeux existants (D-163 pour le premier, Prompt 34 pour le
second) : celui-ci sert UN SEUL scénario fixe (le fil A1 du prompt 43),
jamais rechargé partiellement, toujours remis à zéro (§ A3 : « rejouable »).
Toutes les données sont fictives.
"""
