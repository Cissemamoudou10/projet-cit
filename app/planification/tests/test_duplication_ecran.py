"""US-PLAN-11, cycle HTTP réel — écran de duplication (prompt 48, Story 4).
Données entièrement fictives.
"""

import datetime

from django.urls import reverse

from planification.tests.aide_circuit import seance_dans
from planification.tests.conftest import instant, qualifier


def _lundi_cible(decalage_semaines=8):
    lundi = datetime.date.today() + datetime.timedelta(weeks=decalage_semaines)
    return lundi - datetime.timedelta(days=lundi.weekday())


def test_http_duplication_nominale(client, circuit):
    qualifier(circuit.cours.instructeur, circuit.cours.element.matiere)
    lundi_source = circuit.programme.lundi_de_semaine
    seance_dans(circuit.programme, circuit.cours, circuit.brigade, instant(lundi_source, 0, 8))
    lundi_cible = _lundi_cible()
    client.force_login(circuit.acteurs.planificateur)

    reponse = client.post(
        reverse("planification:lancement_duplication"),
        {
            "semaine_source": lundi_source.isoformat(),
            "semaine_cible": lundi_cible.isoformat(),
            "brigades": [circuit.brigade.pk],
        },
    )

    assert reponse.status_code == 200
    page = reponse.content.decode("utf-8")
    assert "1" in page
    assert "séance" in page


def test_http_refusee_a_la_cellule_examens(client, circuit):
    client.force_login(circuit.acteurs.examens)

    reponse = client.get(reverse("planification:lancement_duplication"))

    assert reponse.status_code == 403
