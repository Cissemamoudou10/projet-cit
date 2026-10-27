"""État `complet` du jeu de recette — Prompt 51, Temps 2, § 2.8. Données
entièrement fictives."""

import io

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import transaction

from evaluations.jeu_recette.donnees import IDENTIFIANT_ADMINISTRATEUR
from evaluations.models import Note


def test_chargement_complet_passe_la_verification(db):
    call_command("charger_jeu_recette", etat="complet")
    sortie = io.StringIO()
    call_command("charger_jeu_recette", etat="complet", verifier=True, stdout=sortie)
    rapport = sortie.getvalue()
    assert "MANQUANT" not in rapport
    assert "47/47 contrôles conformes." in rapport


def test_refuse_hors_developpement(monkeypatch, db):
    monkeypatch.setenv("DJANGO_SETTINGS_MODULE", "cit.reglages.production")

    with pytest.raises(CommandError, match="production"):
        call_command("charger_jeu_recette", etat="complet")

    assert not get_user_model().objects.filter(username=IDENTIFIANT_ADMINISTRATEUR).exists()


def test_reinitialiser_refuse_sur_etat_complet(db):
    with pytest.raises(CommandError, match="reinitialiser"):
        call_command("charger_jeu_recette", etat="complet", reinitialiser=True)


def _empreinte_notes_e1():
    """Les valeurs de notes d'E1 sont la seule donnée réellement tirée de
    la graine (§ 2.5, 2.8) — identifiants métier (matricules, codes) fixes
    par ailleurs, voir `donnees_complet.py`."""
    return sorted(
        (note.stagiaire.matricule, str(note.valeur))
        for note in Note.objects.filter(
            evaluation__element_referentiel__matiere__code="M1", absent=False
        ).select_related("stagiaire")
    )


@pytest.mark.django_db(transaction=True)
def test_determinisme_meme_graine_memes_valeurs():
    empreintes = []
    for _ in range(2):
        with transaction.atomic():
            call_command("charger_jeu_recette", etat="complet", graine=2026)
            empreintes.append(_empreinte_notes_e1())
            transaction.set_rollback(True)
    assert len(empreintes[0]) == 19
    assert empreintes[0] == empreintes[1]
