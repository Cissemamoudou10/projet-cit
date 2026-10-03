"""Sélecteurs d'occupation par les séances (prompt 38, D-210) : contiguës
non occupantes, une requête pour N lieux ou N instructeurs. Données fictives.
"""

from django.db import connection
from django.test.utils import CaptureQueriesContext

from planification.models import Seance
from planification.selectors import seances_occupant_instructeurs, seances_occupant_lieux
from planification.tests.conftest import instant
from ressources.models import Lieu


def _lieu(nom):
    return Lieu.objects.create(intitule=nom, capacite=10, categorie="salle_attitree")


def _seance(programme, cours, lieu, heure_debut, heure_fin):
    return Seance.objects.create(
        programme=programme,
        element_referentiel=cours.element,
        instructeur=cours.instructeur,
        lieu=lieu,
        debut=instant(programme.lundi_de_semaine, 0, heure_debut),
        fin=instant(programme.lundi_de_semaine, 0, heure_fin),
    )


def test_lieux_occupes_recouvrement_sans_contigu(programme, cours):
    occupe, contigu = _lieu("Occupé"), _lieu("Contigu")
    _seance(programme, cours, occupe, 8, 10)
    _seance(programme, cours, contigu, 10, 11)
    debut = instant(programme.lundi_de_semaine, 0, 9)
    fin = instant(programme.lundi_de_semaine, 0, 10)

    resultat = seances_occupant_lieux([occupe.pk, contigu.pk], debut, fin)

    assert set(resultat) == {occupe.pk}


def test_lieux_requete_unique_quel_que_soit_leur_nombre(programme, cours):
    un = [_lieu("Petit").pk]
    dix = [_lieu(f"Grand {i}").pk for i in range(10)]
    debut = instant(programme.lundi_de_semaine, 0, 9)
    fin = instant(programme.lundi_de_semaine, 0, 10)

    with CaptureQueriesContext(connection) as capture_un:
        seances_occupant_lieux(un, debut, fin)
    with CaptureQueriesContext(connection) as capture_dix:
        seances_occupant_lieux(dix, debut, fin)

    assert len(capture_un) == len(capture_dix) == 1


def test_instructeurs_occupes_recouvrement_sans_contigu(programme, cours):
    _seance(programme, cours, None, 8, 9)
    debut = instant(programme.lundi_de_semaine, 0, 9)
    fin = instant(programme.lundi_de_semaine, 0, 10)

    assert seances_occupant_instructeurs([cours.instructeur.pk], debut, fin) == {}
    debut_chevauche = instant(programme.lundi_de_semaine, 0, 8, 30)
    resultat = seances_occupant_instructeurs([cours.instructeur.pk], debut_chevauche, fin)
    assert set(resultat) == {cours.instructeur.pk}
