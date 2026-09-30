"""Compte rendu de chargement — Prompt 34, § 5 (miroir de
`ressources.jeu_demonstration.rapport`, mêmes formes)."""

import time

from planification.jeu_recette.donnees import MOT_DE_PASSE_COMMUN


class Chronometre:
    def __init__(self):
        self._debut = time.monotonic()

    def ecoule(self):
        return time.monotonic() - self._debut


def imprimer_compte_rendu(stdout, compteurs, chronometre):
    stdout.write("")
    stdout.write("Compte rendu de chargement du jeu de recette")
    for entite, total in compteurs.items():
        stdout.write(f"  {entite} : {total}")
    stdout.write(f"  Temps d'exécution : {chronometre.ecoule():.2f} s")
    stdout.write("")
    stdout.write(f"Mot de passe commun des cinq comptes : {MOT_DE_PASSE_COMMUN}")
    stdout.write("Relancez avec --verifier pour un rapport d'état complet.")
