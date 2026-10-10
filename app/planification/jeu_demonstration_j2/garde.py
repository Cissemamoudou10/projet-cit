"""Garde-fous avant tout chargement — Prompt 43, § A3 : « refuse de
s'exécuter sur une autre base ». Trois conditions, toutes vérifiées AVANT
la moindre écriture — ce jeu pose des comptes à mot de passe COMMUN ET
CONNU (`donnees.MOT_DE_PASSE_COMMUN`), comme les deux jeux existants.
"""

import os

from django.contrib.auth import get_user_model
from django.core.management.base import CommandError
from django.db import connection

from planification.jeu_demonstration_j2.comptes import IDENTIFIANT_BOOTSTRAP
from planification.jeu_demonstration_j2.donnees import COMPTES

MARQUEUR_PRODUCTION = "production"
NOM_BASE_ATTENDU = "pfe_cit_demo_j2"


def verifier_environnement_sur():
    _verifier_reglages_production()
    _verifier_nom_de_base()
    _verifier_absence_donnees_etrangeres()


def _verifier_reglages_production():
    module_reglages = os.environ.get("DJANGO_SETTINGS_MODULE", "")
    if MARQUEUR_PRODUCTION in module_reglages:
        raise CommandError(
            f"Réglages de production détectés ({module_reglages}) : ce jeu crée des "
            "comptes à mot de passe COMMUN et CONNU — inexécutable hors démonstration."
        )


def _verifier_nom_de_base():
    """§ A3 : « refuse de s'exécuter sur une autre base » — y compris la
    base de développement habituelle et celle de la recette du sprint 2
    (`pfe_cit_recette`, § A3 : « ne pas la toucher »)."""
    nom_base = connection.settings_dict.get("NAME", "")
    if nom_base != NOM_BASE_ATTENDU:
        raise CommandError(
            f"Base connectée : « {nom_base} », attendue : « {NOM_BASE_ATTENDU} ». Relancez "
            "avec --settings=config.settings.demonstration (jamais sur la base de "
            "développement, jamais sur celle de la recette)."
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
            "comptes à mot de passe COMMUN et CONNU — exécutez-le sur une base dédiée, "
            "jamais partagée avec un autre jeu de données."
        )
