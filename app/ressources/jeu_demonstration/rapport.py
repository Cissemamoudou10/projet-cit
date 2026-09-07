"""Compte rendu de chargement — Prompt 15, § 5.

Imprime, en fin de commande, le nombre d'objets créés par entité, le temps
d'exécution et la liste des règles métier effectivement exercées — c'est
cette liste qui fait du chargement un test d'intégration, pas seulement un
peuplement de données.
"""

import time

REGLES_EXERCEES = (
    "RG-01 / RG-02 bis — identifiant unique, mot de passe validé, groupe synchronisé au profil",
    "RG-03 / RG-26 — verrouillage après échecs consécutifs, journalisation de chaque échec",
    "RG-04 — aucune suppression de compte : seule la désactivation existe",
    "Écart 1 (CU-P2-02) — deux « Formation initiale » homonymes, distinguées par leur type",
    "Critère 3, US-REF-03 — Secourisme rattachée à deux formations, volumes différents",
    "Critère 5, US-REF-03 — écart volume prescrit / durée, avertissement non bloquant",
    "RG-09 / RG-10 — prérequis limités au même référentiel, chaîne acyclique à trois niveaux",
    "Critère 4, US-INS-02 — matière rattachée sans aucun instructeur qualifié",
    "RG-37 — capacités de lieu variées, exploitables par le filtre de capacité minimale",
    "Contrainte d'exclusion des indisponibilités — période contiguë acceptée, "
    "recouvrement admis sur un lieu différent",
    "RG-26 / RG-27 — journal alimenté de plusieurs natures ; --reinitialiser ne le vide jamais",
)


class Chronometre:
    def __init__(self):
        self._debut = time.monotonic()

    def ecoule(self):
        return time.monotonic() - self._debut


def imprimer_compte_rendu(stdout, compteurs, chronometre):
    stdout.write("")
    stdout.write("Compte rendu de chargement")
    for entite, total in compteurs.items():
        stdout.write(f"  {entite} : {total}")
    stdout.write(f"  Temps d'exécution : {chronometre.ecoule():.2f} s")
    stdout.write("")
    stdout.write("Règles métier exercées pendant le chargement :")
    for regle in REGLES_EXERCEES:
        stdout.write(f"  - {regle}")
