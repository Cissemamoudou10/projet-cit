"""US-SUI-01, cycle HTTP réel (prompt 44, Temps 3). Données fictives."""

import datetime

from django.urls import reverse
from django.utils import timezone

from planification.models import ProgrammeHebdomadaire
from planification.services.circuit import ServiceCircuitProgramme
from planification.tests.aide_circuit import seance_dans
from planification.tests.conftest import instant

SIGNATAIRE_ESSAI = "Signataire essai rapprochement HTTP"


def _programme_passe(decalage_semaines=4):
    lundi = datetime.date.today() - datetime.timedelta(weeks=decalage_semaines)
    lundi -= datetime.timedelta(days=lundi.weekday())
    return ProgrammeHebdomadaire.objects.create(lundi_de_semaine=lundi)


def _amener_a_affiche(programme, acteurs):
    ServiceCircuitProgramme.soumettre(acteurs.planificateur, programme)
    ServiceCircuitProgramme.valider(acteurs.pedagogique, programme)
    ServiceCircuitProgramme.enregistrer_signature(
        acteurs.planificateur, programme, timezone.localdate(), SIGNATAIRE_ESSAI
    )
    ServiceCircuitProgramme.afficher(acteurs.planificateur, programme)


def _url():
    return reverse("planification:rapprochement")


def test_http_direction_consulte_le_rapprochement(client, circuit, direction_formation):
    passe = _programme_passe()
    seance_dans(passe, circuit.cours, circuit.brigade, instant(passe.lundi_de_semaine, 0, 8))
    _amener_a_affiche(passe, circuit.acteurs)
    client.force_login(direction_formation)

    reponse = client.get(_url())

    assert reponse.status_code == 200
    page = reponse.content.decode("utf-8")
    assert str(circuit.brigade) in page
    assert str(circuit.cours.element.matiere) in page


def test_http_sans_programme_affiche_affiche_le_message_e1(client, circuit, direction_formation):
    client.force_login(direction_formation)

    reponse = client.get(_url())

    assert "Aucun programme affiché" in reponse.content.decode("utf-8")


def test_http_filtre_par_brigade(
    client, circuit, direction_formation, redacteur, session_formation
):
    from organisation.services.brigade import ServiceBrigade
    from organisation.tests.conftest import donnees_brigade

    autre_brigade = ServiceBrigade.creer(
        redacteur, session_formation, donnees_brigade(designation="RAPH1")
    )
    client.force_login(direction_formation)

    reponse = client.get(_url(), {"brigade": circuit.brigade.pk})

    page = reponse.content.decode("utf-8")
    assert str(circuit.brigade) in page
    # `autre_brigade` figure une seule fois : dans le menu déroulant du
    # filtre (toutes les brigades y sont proposées), jamais dans un groupe
    # de résultat, exclu par le filtre.
    assert page.count(str(autre_brigade)) == 1


def test_http_planification_autorisee(client, circuit):
    """D-265 révise D-264 : § 11.2 fait foi, la planification lit le suivi."""
    client.force_login(circuit.acteurs.planificateur)

    reponse = client.get(_url())

    assert reponse.status_code == 200


def test_http_examens_autorisee(client, circuit):
    client.force_login(circuit.acteurs.examens)

    reponse = client.get(_url())

    assert reponse.status_code == 200


def test_http_cellule_pedagogique_autorisee(client, circuit):
    client.force_login(circuit.acteurs.pedagogique)

    reponse = client.get(_url())

    assert reponse.status_code == 200
