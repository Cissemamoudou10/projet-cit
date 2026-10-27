"""Commande d'administration : charge le jeu de données de recette —
état `socle` (sprint 2, Prompt 34) ou état `complet` (Prompt 51, Temps 2).

Vit dans `evaluations`, pas `planification` ni `ressources` : voir
`evaluations.jeu_recette.__init__` pour la raison (dépendance
d'architecture, décision D-297).

`--etat socle` (défaut, inchangé depuis le prompt 34) est idempotent sans
`--reinitialiser` (sentinelle : le compte `u_adm`). `--reinitialiser` vide
d'abord les données propres à ce jeu (comptes et journal conservés, RG-27 —
voir `reinitialisation.py`/`comptes.py`) puis recharge tout, dans une unique
transaction. `--etat complet` n'est PAS idempotent et ne supporte PAS
`--reinitialiser` : il ajoute au socle des objets uniques (sessions,
programmes, évaluations datés par rapport à `--date-reference`) — repartir
d'une base vidée par `outils/recette/reinitialiser_base_recette.ps1` est le
chemin prévu (Prompt 51, Temps 1), pas une réinitialisation partielle.

`--verifier` ne crée rien (rapport de lecture seule, § 5 / § 2.8).
`--pagination` ajoute vingt-cinq sessions sur une formation dédiée `F5`
(§ 6), seule ou combinée à un chargement `socle`.

NE charge PAS les grilles horaires (livrées par US-PLAN-12,
`initialiser_grilles_horaires`) : `--verifier` en confirme seulement la
présence.
"""

import datetime

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from administration.models import Utilisateur
from evaluations.jeu_recette.alea import DEFAUT_GRAINE
from evaluations.jeu_recette.comptes import charger_comptes, recuperer_comptes
from evaluations.jeu_recette.donnees import (
    FORMATIONS,
    IDENTIFIANT_ADMINISTRATEUR,
    INSTRUCTEURS,
    LIEUX,
    MATIERES,
    TYPES_FORMATION,
)
from evaluations.jeu_recette.fichiers_import.constructeur import DOSSIER
from evaluations.jeu_recette.fichiers_import.constructeur import generer as generer_fichiers
from evaluations.jeu_recette.garde import verifier_environnement_sur
from evaluations.jeu_recette.instructeurs import charger_instructeurs, charger_qualifications
from evaluations.jeu_recette.lieux import charger_lieux
from evaluations.jeu_recette.orchestration_complet import charger_etat_complet
from evaluations.jeu_recette.pagination import charger_pagination
from evaluations.jeu_recette.rapport import Chronometre, imprimer_compte_rendu
from evaluations.jeu_recette.referentiel import (
    charger_composition,
    charger_formations,
    charger_matieres,
    charger_prerequis,
    charger_types_formation,
)
from evaluations.jeu_recette.reinitialisation import vider_donnees_recette
from evaluations.jeu_recette.verification import verifier
from referentiel.models import ElementReferentiel, Formation, Matiere, TypeFormation
from ressources.models import Instructeur, Lieu


def _charger_referentiel(stdout, ped, plan):
    types = charger_types_formation(ped, stdout)
    matieres = charger_matieres(ped, stdout)
    formations = charger_formations(ped, types, stdout)
    elements = charger_composition(ped, formations, matieres, stdout)
    charger_prerequis(ped, formations, elements, stdout)
    instructeurs = charger_instructeurs(ped, stdout)
    charger_qualifications(ped, instructeurs, matieres, stdout)
    lieux = charger_lieux(plan, stdout)
    return types, matieres, formations, elements, instructeurs, lieux


def _charger(stdout, comptes_existent):
    """Comptes JAMAIS recréés dès qu'ils existent déjà (RG-27) — y compris
    après `--reinitialiser`, qui ne les vide pas (`reinitialisation.py`) :
    seule leur récupération est légitime. Le RESTE (types, matières,
    formations…) est, lui, toujours rechargé ici, que les comptes
    existent ou non — après `--reinitialiser`, les comptes survivent mais
    le reste a été vidé (`vider_donnees_recette`) : un appelant qui
    voudrait éviter ce rechargement (socle déjà complet, jamais vidé) doit
    passer par `_objets_socle()` directement, pas par cette fonction (voir
    `Command._charger_complet`). Rend `(compteurs, objets_socle)` — ce
    second élément sert directement `--etat complet`
    (`orchestration_complet.charger_etat_complet`)."""
    call_command("initialiser_habilitations")
    comptes = recuperer_comptes(stdout) if comptes_existent else charger_comptes(stdout)
    ped, plan = comptes["u_ped"], comptes["u_plan"]
    types, matieres, formations, elements, instructeurs, lieux = _charger_referentiel(
        stdout, ped, plan
    )
    objets = {
        "comptes": comptes,
        "types": types,
        "matieres": matieres,
        "formations": formations,
        "elements": elements,
        "instructeurs": instructeurs,
        "lieux": lieux,
    }
    compteurs = {
        "Comptes": len(comptes),
        "Types de formation": len(types),
        "Matières": len(matieres),
        "Formations": len(formations),
        "Éléments de référentiel": len(elements),
        "Instructeurs": len(instructeurs),
        "Lieux": len(lieux),
    }
    return compteurs, objets


def _objets_socle(stdout):
    """Relit depuis la base les objets du jeu `socle` déjà chargés — seul
    chemin légitime une fois les comptes présents (jamais une recréation,
    RG-27). Même liste de codes que `donnees.py`."""
    comptes = recuperer_comptes(stdout)
    types = {
        code: TypeFormation.objects.get(intitule=intitule)
        for code, intitule in TYPES_FORMATION.items()
    }
    matieres = {code: Matiere.objects.get(code=code) for code in MATIERES}
    formations = {
        donnees.code: Formation.objects.get(intitule=donnees.libelle) for donnees in FORMATIONS
    }
    elements = {
        (donnees.code, code_matiere): ElementReferentiel.objects.get(
            formation=formations[donnees.code], matiere__code=code_matiere
        )
        for donnees in FORMATIONS
        for code_matiere, _volume in donnees.composition
    }
    instructeurs = {
        donnees.code: Instructeur.objects.get(nom=donnees.code) for donnees in INSTRUCTEURS
    }
    lieux = {donnees.code: Lieu.objects.get(intitule=donnees.libelle) for donnees in LIEUX}
    return {
        "comptes": comptes,
        "types": types,
        "matieres": matieres,
        "formations": formations,
        "elements": elements,
        "instructeurs": instructeurs,
        "lieux": lieux,
    }


class Command(BaseCommand):
    help = "Charge le jeu de données de recette (état socle ou complet)."

    def add_arguments(self, parser):
        self._arguments_communes(parser)
        self._arguments_etat_complet(parser)

    @staticmethod
    def _arguments_communes(parser):
        parser.add_argument(
            "--etat",
            choices=("socle", "complet"),
            default="socle",
            help="socle (défaut, Prompt 34) ou complet (Prompt 51, Temps 2).",
        )
        parser.add_argument(
            "--reinitialiser",
            action="store_true",
            help="État socle seulement : vide d'abord les données de recette (RG-27).",
        )
        parser.add_argument(
            "--verifier",
            action="store_true",
            help="Ne crée rien : rapport d'état du jeu de recette (§ 5 / § 2.8).",
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

    @staticmethod
    def _arguments_etat_complet(parser):
        parser.add_argument(
            "--date-reference",
            default=None,
            help="État complet seulement : AAAA-MM-JJ, défaut le jour du chargement (§ 3).",
        )
        parser.add_argument(
            "--graine",
            type=int,
            default=DEFAUT_GRAINE,
            help="État complet seulement : graine de déterminisme (défaut 2026, § 5).",
        )

    def handle(self, *args, **options):
        if options["verifier"]:
            verifier(self.stdout, etat=options["etat"])
            return
        if options["etat"] == "complet":
            self._charger_complet(options)
            return
        self._charger_socle(options)

    def _charger_socle(self, options):
        verifier_environnement_sur()
        comptes_existent = Utilisateur.objects.filter(username=IDENTIFIANT_ADMINISTRATEUR).exists()
        deja_charge = comptes_existent and not options["reinitialiser"]

        chronometre = Chronometre()
        with transaction.atomic():
            if options["reinitialiser"] and comptes_existent:
                vider_donnees_recette(self.stdout)
            if deja_charge:
                self.stdout.write("Jeu de recette déjà chargé — rien à recharger.")
                compteurs, objets = {}, _objets_socle(self.stdout)
            else:
                compteurs, objets = _charger(self.stdout, comptes_existent)
            if options["pagination"]:
                charger_pagination(
                    objets["comptes"]["u_ped"], objets["types"], objets["matieres"], self.stdout
                )

        if options["regenerer_fichiers_import"]:
            self.stderr.write(
                f"AVERTISSEMENT : les fichiers de recette de {DOSSIER}/ vont être réécrits. "
                "Relisez leur diff avant de les committer."
            )
            generer_fichiers(DOSSIER, self.stdout)
        imprimer_compte_rendu(self.stdout, compteurs, chronometre)

    def _charger_complet(self, options):
        if options["reinitialiser"]:
            raise CommandError(
                "--reinitialiser ne s'applique pas à --etat complet (voir le docstring de "
                "cette commande) : repartez d'une base vidée par "
                "outils/recette/reinitialiser_base_recette.ps1."
            )
        verifier_environnement_sur()
        call_command("initialiser_natures_evenement")
        comptes_existent = Utilisateur.objects.filter(username=IDENTIFIANT_ADMINISTRATEUR).exists()
        date_reference = (
            datetime.date.fromisoformat(options["date_reference"])
            if options["date_reference"]
            else timezone.localdate()
        )
        chronometre = Chronometre()
        with transaction.atomic():
            if comptes_existent:
                # Socle déjà chargé par un appel antérieur : le relire,
                # jamais le recréer (violerait les contraintes d'unicité
                # de `donnees.py` — même raison que `_charger_socle`).
                self.stdout.write("Jeu socle déjà chargé — récupéré depuis la base.")
                compteurs_socle, objets_socle = {}, _objets_socle(self.stdout)
            else:
                compteurs_socle, objets_socle = _charger(self.stdout, comptes_existent=False)
            call_command("initialiser_grilles_horaires")
            compteurs_complet = charger_etat_complet(
                objets_socle, date_reference, options["graine"], self.stdout
            )
        imprimer_compte_rendu(self.stdout, {**compteurs_socle, **compteurs_complet}, chronometre)
