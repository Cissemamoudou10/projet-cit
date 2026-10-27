"""Commande d'administration : charge le jeu de données de recette du
sprint 2 — Prompt 34.

Vit dans `planification`, pas `ressources` : voir `planification.jeu_recette.
__init__` pour la raison (dépendance d'architecture).

Idempotente sans `--reinitialiser` (sentinelle : le compte `u_adm`).
`--reinitialiser` vide d'abord les données propres à ce jeu (comptes et
journal conservés, RG-27 — voir `reinitialisation.py`/`comptes.py`) puis
recharge tout, dans une unique transaction. `--verifier` ne crée rien
(rapport de lecture seule, § 5). `--pagination` ajoute vingt-cinq sessions
sur une formation dédiée `F5` (§ 6), seule ou combinée à un chargement.

NE charge PAS les grilles horaires (livrées par US-PLAN-12,
`initialiser_grilles_horaires`) : `--verifier` en confirme seulement la
présence.
"""

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import transaction

from administration.models import Utilisateur
from planification.jeu_recette.comptes import charger_comptes, recuperer_comptes
from planification.jeu_recette.donnees import IDENTIFIANT_ADMINISTRATEUR, MATIERES, TYPES_FORMATION
from planification.jeu_recette.fichiers_import.constructeur import DOSSIER
from planification.jeu_recette.fichiers_import.constructeur import generer as generer_fichiers
from planification.jeu_recette.garde import verifier_environnement_sur
from planification.jeu_recette.instructeurs import charger_instructeurs, charger_qualifications
from planification.jeu_recette.lieux import charger_lieux
from planification.jeu_recette.pagination import charger_pagination
from planification.jeu_recette.rapport import Chronometre, imprimer_compte_rendu
from planification.jeu_recette.referentiel import (
    charger_composition,
    charger_formations,
    charger_matieres,
    charger_prerequis,
    charger_types_formation,
)
from planification.jeu_recette.reinitialisation import vider_donnees_recette
from planification.jeu_recette.verification import verifier
from referentiel.models import Matiere, TypeFormation


class Command(BaseCommand):
    help = "Charge le jeu de données de recette du sprint 2 (Prompt 34)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--reinitialiser",
            action="store_true",
            help="Vide d'abord les données de recette (comptes et journal conservés, RG-27).",
        )
        parser.add_argument(
            "--verifier",
            action="store_true",
            help="Ne crée rien : rapport d'état du jeu de recette (§ 5).",
        )
        parser.add_argument(
            "--pagination",
            action="store_true",
            help="Ajoute 25 sessions sur une formation dédiée F5, pour R2-SES01-17 (§ 6).",
        )
        parser.add_argument(
            "--regenerer-fichiers-import",
            action="store_true",
            help=(
                "Réécrit docs/recette/fichiers-import/ (fichiers suivis). Ces fichiers vont "
                "changer : relire le diff avant de les committer."
            ),
        )

    def handle(self, *args, **options):
        if options["verifier"]:
            verifier(self.stdout)
            return

        verifier_environnement_sur()
        comptes_existent = Utilisateur.objects.filter(username=IDENTIFIANT_ADMINISTRATEUR).exists()
        deja_charge = comptes_existent and not options["reinitialiser"]

        chronometre = Chronometre()
        with transaction.atomic():
            if options["reinitialiser"] and comptes_existent:
                vider_donnees_recette(self.stdout)
            if deja_charge:
                self.stdout.write("Jeu de recette déjà chargé — rien à recharger.")
                compteurs = {}
                comptes = recuperer_comptes(self.stdout)
                types, matieres = self._recuperer_types_et_matieres()
            else:
                compteurs, comptes, types, matieres = self._charger(comptes_existent)
            if options["pagination"]:
                charger_pagination(comptes["u_ped"], types, matieres, self.stdout)

        if options["regenerer_fichiers_import"]:
            self.stderr.write(
                f"AVERTISSEMENT : les fichiers de recette de {DOSSIER}/ vont être réécrits. "
                "Relisez leur diff avant de les committer."
            )
            generer_fichiers(DOSSIER, self.stdout)
        imprimer_compte_rendu(self.stdout, compteurs, chronometre)

    def _charger(self, comptes_existent):
        """Comptes JAMAIS recréés dès qu'ils existent déjà (RG-27) — y
        compris après `--reinitialiser`, qui ne les vide pas
        (`reinitialisation.py`) : seule leur récupération est légitime."""
        call_command("initialiser_habilitations")
        comptes = (
            recuperer_comptes(self.stdout) if comptes_existent else charger_comptes(self.stdout)
        )
        ped, plan = comptes["u_ped"], comptes["u_plan"]

        types = charger_types_formation(ped, self.stdout)
        matieres = charger_matieres(ped, self.stdout)
        formations = charger_formations(ped, types, self.stdout)
        elements = charger_composition(ped, formations, matieres, self.stdout)
        charger_prerequis(ped, formations, elements, self.stdout)

        instructeurs = charger_instructeurs(ped, self.stdout)
        charger_qualifications(ped, instructeurs, matieres, self.stdout)

        lieux = charger_lieux(plan, self.stdout)

        compteurs = {
            "Comptes": len(comptes),
            "Types de formation": len(types),
            "Matières": len(matieres),
            "Formations": len(formations),
            "Éléments de référentiel": len(elements),
            "Instructeurs": len(instructeurs),
            "Lieux": len(lieux),
        }
        return compteurs, comptes, types, matieres

    @staticmethod
    def _recuperer_types_et_matieres():
        types = {
            code: TypeFormation.objects.get(intitule=intitule)
            for code, intitule in TYPES_FORMATION.items()
        }
        matieres = {code: Matiere.objects.get(code=code) for code in MATIERES}
        return types, matieres
