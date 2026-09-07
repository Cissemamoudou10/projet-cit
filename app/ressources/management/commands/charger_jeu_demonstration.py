"""Commande d'administration : charge le jeu de données de démonstration du
sprint 1 — Prompt 15.

Vit dans `ressources`, pas `administration` : c'est la seule application
dont l'ordre de dépendance (`tests/architecture/test_couches.py`) autorise
l'import d'`administration`, de `referentiel` et de `ressources` elle-même,
les trois applications que ce chargement traverse.

Idempotente sans `--reinitialiser` (§ 1.3 du prompt) : une base déjà peuplée
n'est pas rechargée, jamais dupliquée. `--reinitialiser` vide d'abord les
données de référentiel et de ressources (comptes et journal exceptés, RG-27
— voir `reinitialisation.py` et `comptes.py`) puis recharge tout, dans une
unique transaction : un échec en cours de chargement ne doit laisser aucune
donnée partielle.
"""

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction

from administration.models import Utilisateur
from ressources.jeu_demonstration.comptes import charger_comptes, recuperer_comptes
from ressources.jeu_demonstration.instructeurs import charger_instructeurs, charger_qualifications
from ressources.jeu_demonstration.lieux import charger_indisponibilites, charger_lieux
from ressources.jeu_demonstration.rapport import Chronometre, imprimer_compte_rendu
from ressources.jeu_demonstration.referentiel import (
    charger_composition,
    charger_formations,
    charger_matieres,
    charger_objectifs,
    charger_prerequis,
    charger_types_formation,
)
from ressources.jeu_demonstration.reinitialisation import vider_donnees_demonstration

IDENTIFIANT_SENTINELLE = "adm.demo"


class Command(BaseCommand):
    help = "Charge le jeu de données de démonstration du sprint 1 (Prompt 15)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reinitialiser",
            action="store_true",
            help="Vide d'abord les données de démonstration (journal conservé, RG-27).",
        )

    def handle(self, *args, **options):
        comptes_existants = Utilisateur.objects.filter(username=IDENTIFIANT_SENTINELLE).exists()
        if not options["reinitialiser"] and comptes_existants:
            self.stdout.write("Jeu de démonstration déjà chargé — rien à faire.")
            return

        chronometre = Chronometre()
        with transaction.atomic():
            if options["reinitialiser"]:
                vider_donnees_demonstration(self.stdout)
            compteurs = self._charger(comptes_existants)
        imprimer_compte_rendu(self.stdout, compteurs, chronometre)

    def _charger(self, comptes_existants):
        call_command("initialiser_habilitations")
        comptes = (
            recuperer_comptes(self.stdout) if comptes_existants else charger_comptes(self.stdout)
        )
        ped, pla = comptes["ped.demo"], comptes["pla.demo"]

        types = charger_types_formation(ped, self.stdout)
        matieres = charger_matieres(ped, self.stdout)
        formations = charger_formations(ped, types, self.stdout)
        elements = charger_composition(ped, formations, matieres, self.stdout)
        charger_objectifs(ped, matieres, self.stdout)
        charger_prerequis(ped, formations, elements, self.stdout)

        instructeurs = charger_instructeurs(ped, self.stdout)
        charger_qualifications(ped, instructeurs, matieres, self.stdout)

        lieux = charger_lieux(pla, self.stdout)
        charger_indisponibilites(pla, lieux, self.stdout)

        return {
            "Comptes": len(comptes),
            "Types de formation": len(types),
            "Matières": len(matieres),
            "Formations": len(formations),
            "Éléments de référentiel": len(elements),
            "Instructeurs": len(instructeurs),
            "Lieux": len(lieux),
        }
