"""Les deux formes du recouvrement (`noyau.intervalles`) donnent le même
verdict sur les cas limites. Vérifié contre la base : une indisponibilité
de lieu est la ligne `[debut_b, fin_b)`, la requête porte `[debut_a, fin_a)`.
Données entièrement fictives.
"""

import datetime

import pytest
from django.utils import timezone

from noyau.intervalles import filtre_recouvrement, se_recouvrent
from ressources.models import IndisponibiliteLieu, Lieu


def _instant(heure):
    return timezone.make_aware(datetime.datetime(2026, 10, 5, heure, 0))


CAS = [
    pytest.param((8, 9, 9, 10, False), id="contigus-fin-egale-debut"),
    pytest.param((9, 10, 8, 9, False), id="contigus-debut-egal-fin"),
    pytest.param((9, 10, 8, 12, True), id="englobant-la-ligne"),
    pytest.param((8, 12, 9, 10, True), id="inclus-dans-la-ligne"),
    pytest.param((9, 10, 9, 10, True), id="identique"),
    pytest.param((8, 9, 10, 11, False), id="disjoint"),
    pytest.param((8, 10, 9, 11, True), id="chevauchement-partiel"),
]


@pytest.mark.parametrize("cas", CAS)
def test_les_deux_formes_donnent_le_meme_verdict(db, cas):
    debut_a, fin_a, debut_b, fin_b, attendu = cas
    lieu = Lieu.objects.create(intitule="Salle intervalles", capacite=10, categorie="salle_attitree")
    IndisponibiliteLieu.objects.create(
        lieu=lieu, debut=_instant(debut_b), fin=_instant(fin_b), motif="Essai"
    )

    en_memoire = se_recouvrent(_instant(debut_a), _instant(fin_a), _instant(debut_b), _instant(fin_b))
    en_base = IndisponibiliteLieu.objects.filter(
        filtre_recouvrement("debut", "fin", _instant(debut_a), _instant(fin_a))
    ).exists()

    assert en_memoire is attendu
    assert en_base is attendu
