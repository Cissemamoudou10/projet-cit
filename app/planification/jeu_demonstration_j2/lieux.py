"""Chargement du lieu de la démonstration J2 — une salle, utilisée par
l'organisation de l'épreuve (étape 9), aucune matière du référentiel ne
l'exige (AUCUN_LIEU, voir `referentiel.py`) : elle n'est là que pour
qu'une organisation d'épreuve ait un lieu réel à proposer."""

from planification.jeu_demonstration_j2.donnees import LIEU, LIEU_CAPACITE
from ressources.models import CategorieLieu
from ressources.services.lieu import ServiceLieu


def charger_lieu(agissant, stdout):
    lieu = ServiceLieu.creer(
        agissant,
        {"intitule": LIEU, "capacite": LIEU_CAPACITE, "categorie": CategorieLieu.SALLE_ATTITREE},
    )
    stdout.write(f"  Lieu « {lieu} » créé.")
    return lieu
