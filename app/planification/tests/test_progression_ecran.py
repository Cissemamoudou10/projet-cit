"""US-SUI-06, cycle HTTP réel (prompt 45, Temps 2) — hors production de PDF
réelle (voir `test_progression_pdf.py`, marqué `pdf`). Données fictives.
"""

import datetime

from django.urls import reverse
from django.utils import timezone

from planification.models import EditionProgression, ProgrammeHebdomadaire
from planification.services.circuit import ServiceCircuitProgramme
from planification.tests.aide_circuit import seance_dans
from planification.tests.conftest import instant

SIGNATAIRE_ESSAI = "Signataire essai écran"
LUNDI_FIXE = datetime.date(2024, 1, 1)


def _amener_a_affiche(programme, acteurs):
    ServiceCircuitProgramme.soumettre(acteurs.planificateur, programme)
    ServiceCircuitProgramme.valider(acteurs.pedagogique, programme)
    ServiceCircuitProgramme.enregistrer_signature(
        acteurs.planificateur, programme, timezone.localdate(), SIGNATAIRE_ESSAI
    )
    ServiceCircuitProgramme.afficher(acteurs.planificateur, programme)
    programme.refresh_from_db()


def _programme_affiche(circuit):
    programme = ProgrammeHebdomadaire.objects.create(lundi_de_semaine=LUNDI_FIXE)
    seance_dans(programme, circuit.cours, circuit.brigade, instant(LUNDI_FIXE, 0, 8))
    _amener_a_affiche(programme, circuit.acteurs)
    return programme


def _url_progression(programme):
    return reverse("planification:progression_realisee", args=[programme.pk])


def test_http_edition_par_la_planification(client, circuit):
    programme = _programme_affiche(circuit)
    client.force_login(circuit.acteurs.planificateur)

    reponse = client.post(
        reverse("planification:editer_progression", args=[programme.pk]), follow=True
    )

    assert reponse.status_code == 200
    assert EditionProgression.objects.filter(programme=programme).exists()
    assert "Progression réalisée éditée" in reponse.content.decode("utf-8")


def test_http_edition_refusee_a_la_pedagogique(client, circuit):
    programme = _programme_affiche(circuit)
    client.force_login(circuit.acteurs.pedagogique)

    reponse = client.post(reverse("planification:editer_progression", args=[programme.pk]))

    assert reponse.status_code == 403
    assert not EditionProgression.objects.filter(programme=programme).exists()


def test_http_signature_par_la_planification(client, circuit):
    programme = _programme_affiche(circuit)
    client.force_login(circuit.acteurs.planificateur)
    client.post(reverse("planification:editer_progression", args=[programme.pk]))
    edition = EditionProgression.objects.get(programme=programme)

    reponse = client.post(
        reverse("planification:signer_progression", args=[edition.pk]),
        {
            "date_signature": timezone.localdate().isoformat(),
            "signataire": SIGNATAIRE_ESSAI,
        },
        follow=True,
    )

    assert reponse.status_code == 200
    edition.refresh_from_db()
    assert edition.signataire == SIGNATAIRE_ESSAI
    assert edition.date_signature == timezone.localdate()


def test_http_consultation_de_l_ecran_par_les_quatre_profils(client, circuit, direction_formation):
    programme = _programme_affiche(circuit)
    for acteur in (
        circuit.acteurs.planificateur,
        circuit.acteurs.pedagogique,
        circuit.acteurs.examens,
        direction_formation,
    ):
        client.force_login(acteur)
        reponse = client.get(_url_progression(programme))
        assert reponse.status_code == 200
