"""Garde-fous du jeu volumineux — Prompt 51, Temps 3, règle commune n° 6.
Même principe que `garde.py` (Prompt 34, § 4), jamais réutilisé tel quel :
les comptes connus diffèrent (`v_*`, `comptes_volume.py`), et la base cible
est distincte (`pfe_cit_volume`, jamais `pfe_cit_recette`) — aucune
coexistence entre les trois jeux (socle/complet, démonstration, volumineux)."""

import os

from django.contrib.auth import get_user_model
from django.core.management.base import CommandError

from evaluations.jeu_recette.comptes_volume import COMPTES_VOLUME, IDENTIFIANT_BOOTSTRAP_VOLUME

MARQUEUR_PRODUCTION = "production"


def verifier_environnement_volume_sur():
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
    identifiants_connus = {compte.identifiant for compte in COMPTES_VOLUME} | {IDENTIFIANT_BOOTSTRAP_VOLUME}
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
            "dédié (pfe_cit_volume), jamais partagé avec un autre jeu de données."
        )
