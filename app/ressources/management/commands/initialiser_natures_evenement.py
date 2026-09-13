"""Commande d'administration : crée les sept natures d'événement du
critère 1 du backlog (US-PLAN-01, § 3, Prompt 28) — catalogue de RÉFÉRENCE,
nécessaire dans tout environnement, y compris en production sur le réseau
isolé du CIT (BNF-06). Même précédent que `initialiser_habilitations`
(`administration`), jamais une migration de données : une migration
appliquée une fois pour toutes ne survit pas à `transactional_db` dans les
tests qui en ont besoin (`referentiel.tests.test_objectif_pedagogique_ordre`,
contrainte différée) — la base y est vidée puis restaurée SANS les données
post-migration, `serialized_rollback` n'étant pas activé sur ce projet.

Idempotente sans écraser une nature déjà réglée : seul un libellé absent du
catalogue est créé, jamais son effet par défaut réécrit si l'agent l'a déjà
modifié depuis l'écran de gestion.
"""

from django.core.management.base import BaseCommand

from ressources.models import NatureEvenement

NATURES_INITIALES = [
    ("Cours", "informatif"),
    ("Conférence", "bloquant"),
    ("Visite", "bloquant"),
    ("Congé", "bloquant"),
    ("Examen", "bloquant"),
    ("Bivouac", "bloquant"),
    ("Formation technique", "bloquant"),
]


class Command(BaseCommand):
    help = "Crée les sept natures d'événement du calendrier académique (critère 1, US-PLAN-01)."

    def handle(self, *args, **options):
        for libelle, effet_par_defaut in NATURES_INITIALES:
            _, cree = NatureEvenement.objects.get_or_create(
                libelle=libelle, defaults={"effet_par_defaut": effet_par_defaut}
            )
            if cree:
                self.stdout.write(
                    self.style.SUCCESS(f"Nature créée : {libelle} ({effet_par_defaut})")
                )
            else:
                self.stdout.write(f"{libelle} : déjà présente, non modifiée.")
