"""Compte rendu de préparation de la démonstration J2."""

import time


class Chronometre:
    def __init__(self):
        self._debut = time.monotonic()

    def ecoule(self):
        return time.monotonic() - self._debut


def imprimer_compte_rendu(stdout, compteurs, chronometre):
    stdout.write("")
    stdout.write("Compte rendu de préparation")
    for entite, total in compteurs.items():
        stdout.write(f"  {entite} : {total}")
    stdout.write(f"  Temps d'exécution : {chronometre.ecoule():.2f} s")
    stdout.write("")
    stdout.write("Prête pour l'étape 1 du scénario (docs/demonstration/DEMO-J2.md).")
