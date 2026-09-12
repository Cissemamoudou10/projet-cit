"""US-INS-03 — contraintes en base (Prompt 27, § 9, Groupe B). Premier
usage réel de `btree_gist` par une contrainte d'exclusion déclarative
(`ExclusionConstraint`) — si B1 ne passe pas, l'extension n'a jamais
fonctionné pour ce mécanisme. Données entièrement fictives.
"""

import datetime

import pytest
from django.db import IntegrityError, transaction

from ressources.models import IndisponibiliteInstructeur, Instructeur, Statut


def _instant(jour, heure, minute=0):
    return datetime.datetime(2026, 10, jour, heure, minute, tzinfo=datetime.UTC)


@pytest.fixture
def autre_instructeur(db):
    return Instructeur.objects.create(
        nom="Bennani",
        prenom="Yasmine",
        grade="Cne",
        specialite="Transmissions",
        statut=Statut.VACATAIRE,
    )


def test_b1_deux_periodes_secantes_meme_instructeur_rejetees_en_base(db, instructeur):
    IndisponibiliteInstructeur.objects.create(
        instructeur=instructeur, debut=_instant(5, 8), fin=_instant(5, 12), motif="Mission"
    )

    with (
        pytest.raises(IntegrityError, match="ex_indispo_instructeur_chevauchement"),
        transaction.atomic(),
    ):
        IndisponibiliteInstructeur.objects.create(
            instructeur=instructeur, debut=_instant(5, 10), fin=_instant(5, 14), motif="Permission"
        )


def test_b2_deux_periodes_secantes_instructeurs_differents_acceptees(
    db, instructeur, autre_instructeur
):
    IndisponibiliteInstructeur.objects.create(
        instructeur=instructeur, debut=_instant(5, 8), fin=_instant(5, 12), motif="Mission"
    )

    seconde = IndisponibiliteInstructeur.objects.create(
        instructeur=autre_instructeur, debut=_instant(5, 10), fin=_instant(5, 14), motif="Stage"
    )

    assert seconde.pk is not None


def test_b3_bornes_contigues_fin_egale_au_debut_acceptees(db, instructeur):
    IndisponibiliteInstructeur.objects.create(
        instructeur=instructeur, debut=_instant(5, 8), fin=_instant(5, 12), motif="Mission matin"
    )

    apres_midi = IndisponibiliteInstructeur.objects.create(
        instructeur=instructeur,
        debut=_instant(5, 12),
        fin=_instant(5, 18),
        motif="Mission après-midi",
    )

    assert apres_midi.pk is not None


def test_b4_ck_indisponibilite_instructeur_bornes_par_insertion_directe(db, instructeur):
    with (
        pytest.raises(IntegrityError, match="ck_indisponibilite_instructeur_bornes"),
        transaction.atomic(),
    ):
        IndisponibiliteInstructeur.objects.create(
            instructeur=instructeur, debut=_instant(5, 12), fin=_instant(5, 8), motif="Mission"
        )


def test_ck_motif_non_vide_par_insertion_directe(db, instructeur):
    with (
        pytest.raises(IntegrityError, match="ck_indispo_instructeur_motif_non_vide"),
        transaction.atomic(),
    ):
        IndisponibiliteInstructeur.objects.create(
            instructeur=instructeur, debut=_instant(5, 8), fin=_instant(5, 12), motif=""
        )
