"""Garde-fous avant tout chargement — Prompt 34, § 4. Ce jeu crée des
comptes à mot de passe COMMUN ET CONNU (`donnees.MOT_DE_PASSE_COMMUN`) : les
deux gardes ci-dessous s'exécutent AVANT toute écriture.

Interprétation retenue, à confirmer — voir `docs/suivi/JEU-RECETTE.md` :
« des données autres que celles qu'elle a elle-même créées » est lu au sens
STRICT (aucune donnée étrangère, y compris le jeu de démonstration du
sprint 1) plutôt qu'au sens « autre que ses propres comptes ou ceux du jeu
de démonstration » — un jeu qui pose des mots de passe connus doit tourner
sur un environnement dédié, jamais partagé avec un autre jeu de données.
"""

import os

from django.contrib.auth import get_user_model
from django.core.management.base import CommandError

from planification.jeu_recette.donnees import COMPTES

MARQUEUR_PRODUCTION = "production"
IDENTIFIANT_BOOTSTRAP = "bootstrap.recette"


def verifier_environnement_sur():
    """CommandError, jamais une exception muette : une commande de gestion
    Django affiche le message d'une `CommandError` proprement, sans
    remonter de traceback qui noierait l'avertissement."""
    _verifier_reglages_production()
    _verifier_absence_donnees_etrangeres()


def _verifier_reglages_production():
    module_reglages = os.environ.get("DJANGO_SETTINGS_MODULE", "")
    if MARQUEUR_PRODUCTION in module_reglages:
        raise CommandError(
            f"Réglages de production détectés ({module_reglages}) : ce jeu crée des "
            "comptes à mot de passe COMMUN et CONNU — inexécutable hors développement."
        )


def _verifier_absence_donnees_etrangeres():
    identifiants_connus = {compte.identifiant for compte in COMPTES} | {IDENTIFIANT_BOOTSTRAP}
    etrangers = list(
        get_user_model()
        .objects.exclude(username__in=identifiants_connus)
        .values_list("username", flat=True)[:5]
    )
    if etrangers:
        raise CommandError(
            "La base contient des comptes que ce jeu n'a pas créés "
            f"({', '.join(etrangers)}{'…' if len(etrangers) == 5 else ''}) : ce jeu crée des "
            "comptes à mot de passe COMMUN et CONNU — exécutez-le sur un environnement "
            "dédié, jamais partagé avec le jeu de démonstration ou une base réelle."
        )
