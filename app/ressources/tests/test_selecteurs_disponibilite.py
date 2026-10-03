"""Sélecteurs publics d'indisponibilités (prompt 38, D-210) : verdict identique
au prédicat en mémoire, et une seule requête quel que soit le nombre de
ressources. Données entièrement fictives.
"""

import datetime

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from noyau.intervalles import se_recouvrent
from ressources.models import (
    IndisponibiliteInstructeur,
    IndisponibiliteLieu,
    Instructeur,
    Lieu,
    Statut,
)
from ressources.selectors import indisponibilites_des_instructeurs, indisponibilites_des_lieux


def _h(heure):
    return timezone.make_aware(datetime.datetime(2026, 10, 5, heure, 0))


def _lieu(nom):
    return Lieu.objects.create(intitule=nom, capacite=10, categorie="salle_attitree")


def _instructeur(matricule):
    return Instructeur.objects.create(
        nom="Selecteur",
        prenom="Essai",
        matricule=matricule,
        grade="Lt",
        specialite="Transmissions",
        statut=Statut.MILITAIRE_DU_CENTRE,
    )


def test_lieux_ne_renvoie_que_les_recouvrements_et_respecte_le_predicat(db):
    occupe, contigu, libre = _lieu("Occupé"), _lieu("Contigu"), _lieu("Libre")
    IndisponibiliteLieu.objects.create(lieu=occupe, debut=_h(9), fin=_h(10), motif="Essai")
    IndisponibiliteLieu.objects.create(lieu=contigu, debut=_h(10), fin=_h(11), motif="Essai")

    resultat = indisponibilites_des_lieux([occupe.pk, contigu.pk, libre.pk], _h(9), _h(10))

    assert set(resultat) == {occupe.pk}
    assert se_recouvrent(_h(9), _h(10), _h(9), _h(10))
    assert not se_recouvrent(_h(9), _h(10), _h(10), _h(11))


def test_lieux_requete_unique_quel_que_soit_leur_nombre(db):
    petits = [_lieu(f"Petit {i}").pk for i in range(1)]
    grands = [_lieu(f"Grand {i}").pk for i in range(10)]

    with CaptureQueriesContext(connection) as un:
        indisponibilites_des_lieux(petits, _h(9), _h(10))
    with CaptureQueriesContext(connection) as dix:
        indisponibilites_des_lieux(grands, _h(9), _h(10))

    assert len(un) == len(dix) == 1


def test_instructeurs_ne_renvoie_que_les_recouvrements(db):
    occupe, contigu = _instructeur("SEL-1"), _instructeur("SEL-2")
    IndisponibiliteInstructeur.objects.create(
        instructeur=occupe, debut=_h(8), fin=_h(10), motif="Essai"
    )
    IndisponibiliteInstructeur.objects.create(
        instructeur=contigu, debut=_h(10), fin=_h(12), motif="Essai"
    )

    resultat = indisponibilites_des_instructeurs([occupe.pk, contigu.pk], _h(9), _h(10))

    assert set(resultat) == {occupe.pk}


def test_instructeurs_requete_unique_quel_que_soit_leur_nombre(db):
    un = [_instructeur("SEL-U").pk]
    dix = [_instructeur(f"SEL-D{i}").pk for i in range(10)]

    with CaptureQueriesContext(connection) as capture_un:
        indisponibilites_des_instructeurs(un, _h(9), _h(10))
    with CaptureQueriesContext(connection) as capture_dix:
        indisponibilites_des_instructeurs(dix, _h(9), _h(10))

    assert len(capture_un) == len(capture_dix) == 1
