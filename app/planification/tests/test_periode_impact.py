"""US-PLAN-05, fin (prompt 42, partie 1) — D-121 E2 et A3 : une période
bloquante énumère les séances déjà programmées qu'elle recouvre, sans les
modifier ; sa suppression ne restaure rien. Données fictives.
"""

import datetime

from django.urls import reverse

from planification.models import Seance
from planification.selectors import brigades_de_la_periode, seances_recouvertes
from planification.tests.aide_circuit import seance_dans
from planification.tests.conftest import instant
from ressources.models import NatureEvenement
from ressources.services.periode_calendrier import DonneesPeriode, ServicePeriodeCalendrier

FORMAT = "%Y-%m-%dT%H:%M"


def _donnees_bloquantes(nature, debut, fin, brigades=()):
    return DonneesPeriode(
        nature=nature,
        intitule="Mission fictive",
        debut=debut,
        fin=fin,
        effet="",
        sessions=[],
        brigades=list(brigades),
    )


def _nature_bloquante():
    return NatureEvenement.objects.create(libelle="Mission (essai)", effet_par_defaut="bloquant")


def test_e2_la_periode_bloquante_enumere_la_seance_recouverte(circuit):
    seance = seance_dans(
        circuit.programme,
        circuit.cours,
        circuit.brigade,
        instant(circuit.programme.lundi_de_semaine, 0, 8),
    )
    debut, fin = (
        seance.debut - datetime.timedelta(hours=1),
        seance.fin + datetime.timedelta(hours=1),
    )
    periode = ServicePeriodeCalendrier.creer(
        circuit.acteurs.planificateur,
        _donnees_bloquantes(_nature_bloquante(), debut, fin, [circuit.brigade]),
    )

    brigades = brigades_de_la_periode(periode)
    seances = seances_recouvertes(brigades, periode.debut, periode.fin)

    assert seance in seances


def test_e2_une_periode_sans_recouvrement_n_enumere_rien(circuit):
    seance_dans(
        circuit.programme,
        circuit.cours,
        circuit.brigade,
        instant(circuit.programme.lundi_de_semaine, 0, 8),
    )
    debut = instant(circuit.programme.lundi_de_semaine, 4, 8)
    periode = ServicePeriodeCalendrier.creer(
        circuit.acteurs.planificateur,
        _donnees_bloquantes(
            _nature_bloquante(), debut, debut + datetime.timedelta(hours=1), [circuit.brigade]
        ),
    )

    seances = seances_recouvertes(brigades_de_la_periode(periode), periode.debut, periode.fin)

    assert seances == []


def test_e2_http_la_fiche_de_la_periode_lie_vers_les_seances_impactees(client, circuit):
    seance = seance_dans(
        circuit.programme,
        circuit.cours,
        circuit.brigade,
        instant(circuit.programme.lundi_de_semaine, 0, 8),
    )
    debut, fin = (
        seance.debut - datetime.timedelta(hours=1),
        seance.fin + datetime.timedelta(hours=1),
    )
    nature = _nature_bloquante()
    client.force_login(circuit.acteurs.planificateur)

    creation = client.post(
        reverse("ressources:declarer_periode_calendrier"),
        {
            "nature": nature.pk,
            "intitule": "Mission fictive",
            "debut": debut.strftime(FORMAT),
            "fin": fin.strftime(FORMAT),
            "effet": "",
            "sessions": [],
            "brigades": [circuit.brigade.pk],
        },
        follow=True,
    )
    contenu_fiche = creation.content.decode("utf-8")
    assert "Voir les séances déjà programmées concernées" in contenu_fiche

    url_impact = reverse(
        "planification:seances_de_la_periode", args=[creation.context["periode"].pk]
    )
    page_impact = client.get(url_impact)

    contenu_impact = page_impact.content.decode("utf-8")
    assert str(circuit.cours.element.matiere) in contenu_impact
    assert reverse("planification:modifier_seance", args=[seance.pk]) in contenu_impact


def test_a3_suppression_d_une_periode_bloquante_ne_restaure_aucune_seance(circuit):
    """D-121 A3 : la suppression ne fait réapparaître aucune séance supprimée
    par la régénération pendant que la période bloquait le créneau."""
    debut = instant(circuit.programme.lundi_de_semaine, 4, 8)
    fin = debut + datetime.timedelta(hours=2)
    periode = ServicePeriodeCalendrier.creer(
        circuit.acteurs.planificateur,
        _donnees_bloquantes(_nature_bloquante(), debut, fin, [circuit.brigade]),
    )
    avant = Seance.objects.filter(programme=circuit.programme).count()

    ServicePeriodeCalendrier.supprimer(circuit.acteurs.planificateur, periode.pk)

    assert Seance.objects.filter(programme=circuit.programme).count() == avant
