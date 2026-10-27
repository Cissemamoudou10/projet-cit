"""Commande d'administration : charge le jeu volumineux — Prompt 51,
Temps 3. Base dédiée (`pfe_cit_volume`), jamais `pfe_cit_recette` : aucune
coexistence avec le jeu de recette (socle/complet) ni le jeu de
démonstration (règle commune n° 6). Chargement non idempotent, non
rejouable sur une base déjà peuplée : repartir d'une base vidée par
`outils/recette/reinitialiser_base_recette.ps1 -Etat volume` (Temps 1).

`--verifier` ne crée rien (rapport de lecture seule, § 3.2, règle commune
n° 8). `--semaines N` réduit le nombre de semaines passées affichées si le
chargement complet dépasse 30 minutes (§ 3.2) — sans toucher au reste."""

import datetime

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from evaluations.jeu_recette.alea import DEFAUT_GRAINE, nouveau_generateur
from evaluations.jeu_recette.donnees_volume import SECONDES_MAX_CHARGEMENT_TOTAL, SEMAINES_PASSEES_AFFICHEES
from evaluations.jeu_recette.garde_volume import verifier_environnement_volume_sur
from evaluations.jeu_recette.orchestration_volume import charger_etat_volume
from evaluations.jeu_recette.rapport import Chronometre, imprimer_compte_rendu
from evaluations.jeu_recette.verification_volume import verifier_volume


class Command(BaseCommand):
    help = "Charge le jeu de données volumineux (Prompt 51, Temps 3)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--date-reference",
            default=None,
            help="AAAA-MM-JJ, défaut le jour du chargement (§ 3, règle commune n° 3).",
        )
        parser.add_argument(
            "--graine", type=int, default=DEFAUT_GRAINE, help="Graine de déterminisme (défaut 2026)."
        )
        parser.add_argument(
            "--verifier", action="store_true", help="Ne crée rien : rapport d'état (§ 3.2)."
        )
        parser.add_argument(
            "--semaines",
            type=int,
            default=SEMAINES_PASSEES_AFFICHEES,
            help=(
                "Nombre de semaines passées affichées (défaut 8, § 3.1) — à réduire si le "
                "chargement complet dépasse 30 minutes (§ 3.2)."
            ),
        )

    def handle(self, *args, **options):
        if options["verifier"]:
            verifier_volume(self.stdout)
            return
        verifier_environnement_volume_sur()
        date_reference = (
            datetime.date.fromisoformat(options["date_reference"])
            if options["date_reference"]
            else timezone.localdate()
        )
        generateur = nouveau_generateur(options["graine"])
        chronometre = Chronometre()
        with transaction.atomic():
            compteurs, _mesures = charger_etat_volume(
                generateur, date_reference, self.stdout, semaines_passees=options["semaines"]
            )
        duree = chronometre.ecoule()
        if duree > SECONDES_MAX_CHARGEMENT_TOTAL:
            self.stderr.write(
                f"AVERTISSEMENT : chargement de {duree:.0f} s, au-delà des {SECONDES_MAX_CHARGEMENT_TOTAL} s "
                "visés (§ 3.2) — relevé, sans correction. Essayez --semaines pour réduire la portée."
            )
        imprimer_compte_rendu(self.stdout, compteurs, chronometre, nombre_comptes=7)
