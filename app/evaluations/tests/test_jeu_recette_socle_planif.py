"""État `socle-planif` du jeu de recette — Prompt 53, Temps 1. Données
entièrement fictives."""

import io

import pytest
from django.core.management import call_command
from django.core.management.base import CommandError

from organisation.models import Session
from planification.models import ProgrammeHebdomadaire


def test_chargement_socle_planif_passe_la_verification(db):
    call_command("charger_jeu_recette", etat="socle-planif")
    # Grilles horaires chargées à part (exige un compte administrateur),
    # comme le fait `reinitialiser_base_recette.ps1` (§ 5, après le chargeur).
    call_command("initialiser_grilles_horaires")
    sortie = io.StringIO()
    call_command("charger_jeu_recette", etat="socle-planif", verifier=True, stdout=sortie)
    rapport = sortie.getvalue()
    assert "MANQUANT" not in rapport
    assert "73/73 contrôles conformes." in rapport
    assert "14/14 contrôles conformes." in rapport


def test_reinitialiser_refuse_sur_etat_socle_planif(db):
    with pytest.raises(CommandError, match="reinitialiser"):
        call_command("charger_jeu_recette", etat="socle-planif", reinitialiser=True)


def test_socle_planif_reutilise_le_socle_deja_charge(db):
    """Un second appel ne doit ni recréer le socle (contraintes d'unicité de
    `donnees.py`) ni dupliquer la session S0."""
    call_command("charger_jeu_recette", etat="socle")
    call_command("charger_jeu_recette", etat="socle-planif")

    assert Session.objects.count() == 1


def test_socle_planif_ne_cree_aucun_programme(db):
    call_command("charger_jeu_recette", etat="socle-planif")

    assert not ProgrammeHebdomadaire.objects.exists()
