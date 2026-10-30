"""Objectifs pédagogiques ajoutés par l'état `socle-planif` — Prompt 53,
Temps 1. Réutilise la matière M3 du socle (aucune nouvelle matière)."""

from evaluations.jeu_recette.donnees_socle_planif import (
    CODE_MATIERE_OBJECTIFS,
    OBJECTIFS_PEDAGOGIQUES_M3,
)
from referentiel.services.objectif_pedagogique import ServiceObjectifPedagogique


def charger_objectifs_socle_planif(agissant_ped, matieres, stdout):
    matiere_m3 = matieres[CODE_MATIERE_OBJECTIFS]
    for libelle in OBJECTIFS_PEDAGOGIQUES_M3:
        ServiceObjectifPedagogique.ajouter(agissant_ped, matiere_m3, libelle)
    stdout.write(f"  {len(OBJECTIFS_PEDAGOGIQUES_M3)} objectifs pédagogiques ajoutés sur M3.")
