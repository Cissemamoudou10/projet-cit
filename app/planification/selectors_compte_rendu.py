"""Lecture du compte rendu de génération condensé — correction de
NC R00-GEN-03 (évolution du prompt 53, Temps 3). Une seule requête,
indépendante du nombre de brigades traitées par la génération (le condensé
est un unique `JSONField`, jamais une ligne par brigade ou par motif)."""

from planification.models import CompteRenduGeneration


def derniere_generation(programme):
    return CompteRenduGeneration.objects.filter(programme=programme).first()
