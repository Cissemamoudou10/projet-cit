"""US-SUI-06 — production réelle du PDF (prompt 45, Temps 2).

Marqué `pdf` : WeasyPrint exige des bibliothèques natives (GTK3/Pango/
Cairo) absentes du poste de développement Windows (P-44,
`docs/suivi/PROBLEMES.md`) — ignoré là, à exécuter dans le conteneur de
production (`python:3.14-slim-bookworm`). Voir `.claude/rules/tests.md`.
Données entièrement fictives.
"""

import datetime
import io
import socket
import sys

import pytest
from django.core.management import call_command
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from administration.models import GabaritDocument, TypeDocument
from organisation.services.brigade import ServiceBrigade
from organisation.tests.conftest import donnees_brigade
from planification.models import ProgrammeHebdomadaire
from planification.services.circuit import ServiceCircuitProgramme
from planification.services.suivi import ServiceSuivi
from planification.tests.aide_circuit import seance_dans
from planification.tests.conftest import instant

pytestmark = [
    pytest.mark.pdf,
    pytest.mark.skipif(
        sys.platform.startswith("win"),
        reason=(
            "WeasyPrint exige les bibliothèques natives (GTK3/Pango/Cairo) : "
            "exécuter dans le conteneur (P-44)."
        ),
    ),
]

SIGNATAIRE_ESSAI = "Signataire essai PDF"
LUNDI_FIXE = datetime.date(2024, 1, 1)


@pytest.fixture(autouse=True)
def _gabarits_charges(db):
    """Aucune migration de données (D-122) : le jeu de gabarits initial se
    charge par la commande, comme en production — jamais par une fixture qui
    pose les lignes à la main (`.claude/rules/tests.md`, P-21)."""
    call_command("initialiser_gabarits_documents")


def _amener_a_affiche(programme, acteurs):
    ServiceCircuitProgramme.soumettre(acteurs.planificateur, programme)
    ServiceCircuitProgramme.valider(acteurs.pedagogique, programme)
    ServiceCircuitProgramme.enregistrer_signature(
        acteurs.planificateur, programme, timezone.localdate(), SIGNATAIRE_ESSAI
    )
    ServiceCircuitProgramme.afficher(acteurs.planificateur, programme)
    programme.refresh_from_db()


def _programme_avec_edition(circuit, lundi=LUNDI_FIXE):
    programme = ProgrammeHebdomadaire.objects.create(lundi_de_semaine=lundi)
    seance_dans(programme, circuit.cours, circuit.brigade, instant(lundi, 0, 8))
    _amener_a_affiche(programme, circuit.acteurs)
    return ServiceSuivi.editer_progression(circuit.acteurs.planificateur, programme)


def _texte_du_pdf(pdf_bytes):
    from pypdf import PdfReader

    lecteur = PdfReader(io.BytesIO(pdf_bytes))
    return "".join(page.extract_text() for page in lecteur.pages)


def test_le_document_se_genere(circuit):
    edition = _programme_avec_edition(circuit)

    pdf = ServiceSuivi.produire_pdf_progression(circuit.acteurs.planificateur, edition)

    assert pdf[:4] == b"%PDF"
    assert len(pdf) > 500


def test_il_contient_les_intitules_attendus(circuit):
    edition = _programme_avec_edition(circuit)
    gabarit = GabaritDocument.objects.get(type_document=TypeDocument.PROGRESSION_REALISEE)

    pdf = ServiceSuivi.produire_pdf_progression(circuit.acteurs.planificateur, edition)
    texte = _texte_du_pdf(pdf)

    assert str(circuit.brigade) in texte
    assert str(circuit.cours.element.matiere) in texte
    assert gabarit.en_tete in texte


def test_gabarit_modifie_par_l_administrateur_apparait_sans_changement_de_code(circuit):
    edition = _programme_avec_edition(circuit)
    gabarit = GabaritDocument.objects.get(type_document=TypeDocument.PROGRESSION_REALISEE)
    gabarit.en_tete = "En-tête modifié par l'essai (sans changement de code)."
    gabarit.mentions = "Mentions modifiées par l'essai."
    gabarit.save()

    pdf = ServiceSuivi.produire_pdf_progression(circuit.acteurs.planificateur, edition)
    texte = _texte_du_pdf(pdf)

    assert "En-tête modifié par l'essai" in texte
    assert "Mentions modifiées par l'essai" in texte


def test_aucune_requete_reseau(circuit, monkeypatch):
    edition = _programme_avec_edition(circuit)

    def _interdit(*args, **kwargs):
        raise AssertionError("tentative de connexion réseau pendant la production du PDF")

    monkeypatch.setattr(socket.socket, "connect", _interdit)

    pdf = ServiceSuivi.produire_pdf_progression(circuit.acteurs.planificateur, edition)

    assert pdf[:4] == b"%PDF"


# --- HTTP : téléchargement, requêtes constantes ------------------------


def test_http_telechargement_par_la_direction(client, circuit, direction_formation):
    edition = _programme_avec_edition(circuit)
    client.force_login(direction_formation)

    reponse = client.get(reverse("planification:telecharger_progression", args=[edition.pk]))

    assert reponse.status_code == 200
    assert reponse["Content-Type"] == "application/pdf"
    assert reponse.content[:4] == b"%PDF"


def test_http_requetes_de_generation_constantes_avec_deux_et_dix_brigades(
    circuit, redacteur, session_formation, direction_formation
):
    edition = _programme_avec_edition(circuit)
    autre_brigade = ServiceBrigade.creer(
        redacteur, session_formation, donnees_brigade(designation="PDFB1")
    )
    seance_dans(
        edition.programme, circuit.cours, autre_brigade, instant(LUNDI_FIXE, 0, 10, minute=10)
    )

    # Appel de chauffe (P-39) : le premier appel peuple le cache de permissions
    # de `direction_formation` — sans lui, ce coût ponctuel se compterait dans
    # « deux » et fausserait la comparaison.
    ServiceSuivi.produire_pdf_progression(direction_formation, edition)

    with CaptureQueriesContext(connection) as deux:
        ServiceSuivi.produire_pdf_progression(direction_formation, edition)

    for i in range(8):
        brigade_i = ServiceBrigade.creer(
            redacteur, session_formation, donnees_brigade(designation=f"PDFB{i}2")
        )
        seance_dans(
            edition.programme,
            circuit.cours,
            brigade_i,
            instant(LUNDI_FIXE, 0, 10, minute=10),
        )

    with CaptureQueriesContext(connection) as dix:
        ServiceSuivi.produire_pdf_progression(direction_formation, edition)

    assert len(deux.captured_queries) == len(dix.captured_queries)
