"""R00B-GEN-06 (recette RECETTE-00 bis, observation retenue, prompt 54) :
un créneau bloqué par une période du calendrier (US-PLAN-04) doit porter le
libellé de l'événement sur la consultation du programme, pas une case vide
indiscernable d'un trou de grille — même exigence à l'impression, assurée
par le même gabarit (`impression.css` s'applique tel quel, pas de gabarit
PDF dédié pour cet écran). Données entièrement fictives.
"""

import datetime

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from organisation.services.brigade import ServiceBrigade
from organisation.tests.conftest import donnees_brigade
from ressources.models import NatureEvenement, PeriodeCalendrier


def _url_consultation(programme):
    return (
        reverse("planification:consultation_programme")
        + f"?semaine={programme.lundi_de_semaine.isoformat()}"
    )


def _bloquer_le_premier_creneau(lundi, *, libelle="Conférence", brigades=()):
    """Couvre exactement le créneau 08:00-09:45 de `grille_active` (voir
    conftest), avec les mêmes conversions que `planification.selectors.
    grille_consultation` (`timezone.make_aware`) — jamais un offset UTC à la
    main, qui décale avec le fuseau du Maroc hors de la fenêtre pré-2018."""
    nature = NatureEvenement.objects.create(libelle=libelle, effet_par_defaut="bloquant")
    periode = PeriodeCalendrier.objects.create(
        nature=nature,
        intitule=libelle,
        debut=timezone.make_aware(datetime.datetime.combine(lundi, datetime.time(8, 0))),
        fin=timezone.make_aware(datetime.datetime.combine(lundi, datetime.time(9, 45))),
        effet="bloquant",
    )
    if brigades:
        periode.brigades.set(brigades)
    return periode


def test_le_creneau_bloque_porte_le_libelle_de_l_evenement(client, circuit, grille_active):
    lundi = circuit.programme.lundi_de_semaine
    _bloquer_le_premier_creneau(lundi, libelle="Conférence")
    client.force_login(circuit.acteurs.planificateur)

    contenu = client.get(_url_consultation(circuit.programme)).content.decode("utf-8")

    assert "Conférence" in contenu
    # le second créneau (10:10), non bloqué, reste un trou de grille ordinaire :
    # une seule occurrence de la case vide, pas deux (grille à deux créneaux).
    assert contenu.count("AD/GROUPEMENT") == 1


def test_le_creneau_bloque_pour_une_autre_brigade_ne_change_rien_ici(
    client, circuit, grille_active, autre_brigade_formation
):
    """La portée (brigades ciblées) doit être respectée — une période qui ne
    cible pas `circuit.brigade` ne doit pas lui masquer son créneau."""
    lundi = circuit.programme.lundi_de_semaine
    _bloquer_le_premier_creneau(lundi, libelle="Conférence", brigades=[autre_brigade_formation])
    client.force_login(circuit.acteurs.planificateur)

    contenu = client.get(_url_consultation(circuit.programme)).content.decode("utf-8")

    assert "AD/GROUPEMENT" in contenu  # créneau de circuit.brigade resté un trou ordinaire


def test_le_nombre_de_requetes_est_inchange_avec_le_nombre_de_brigades(
    client, circuit, grille_active, redacteur
):
    """Temps 3 du prompt 54 : le calcul du blocage se charge UNE FOIS pour
    tout le jour (`charger_periodes_bloquantes`), jamais une requête par
    brigade — même exigence que US-PLAN-03, § 2.6."""
    lundi = circuit.programme.lundi_de_semaine
    _bloquer_le_premier_creneau(lundi, libelle="Conférence")
    client.force_login(circuit.acteurs.planificateur)
    url = _url_consultation(circuit.programme)

    with CaptureQueriesContext(connection) as capture_une:
        client.get(url)

    for i in range(5):
        ServiceBrigade.creer(
            redacteur, circuit.brigade.session, donnees_brigade(designation=f"EXP{i:02d}")
        )
    with CaptureQueriesContext(connection) as capture_six:
        client.get(url)

    assert len(capture_six) == len(capture_une)
