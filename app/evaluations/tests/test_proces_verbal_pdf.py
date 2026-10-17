"""US-EVAL-07 — production réelle du PDF du procès-verbal (prompt 46,
point 3).

Marqué `pdf` : WeasyPrint exige des bibliothèques natives absentes du
poste de développement Windows (P-44, `docs/suivi/PROBLEMES.md`) — ignoré
là, à exécuter dans le conteneur de production. Voir
`.claude/rules/tests.md`. Données entièrement fictives.
"""

import io
import socket
import sys

import pytest
from django.core.management import call_command

from evaluations.models import TypeProcesVerbal
from evaluations.services.note import ServiceNote
from evaluations.services.proces_verbal import ServiceProcesVerbal
from evaluations.tests.conftest import affecter_stagiaires

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


@pytest.fixture(autouse=True)
def _gabarits_charges(db):
    call_command("initialiser_gabarits_documents")


def _noter(dossier, prefixe):
    stagiaire = affecter_stagiaires(dossier.redacteur, dossier.brigade, 1, prefixe=prefixe)[0]
    ServiceNote.confirmer(
        dossier.examens,
        dossier.certificative,
        {str(stagiaire.pk): {"valeur": "15", "absent": False}},
    )
    return stagiaire


def _proces_verbal_genere(dossier, prefixe):
    stagiaire = _noter(dossier, prefixe)
    pv = ServiceProcesVerbal.generer(
        dossier.examens, dossier.session, TypeProcesVerbal.FIN_DE_FORMATION
    )
    return pv, stagiaire


def _texte_du_pdf(pdf_bytes):
    from pypdf import PdfReader

    lecteur = PdfReader(io.BytesIO(pdf_bytes))
    return "".join(page.extract_text() for page in lecteur.pages)


def test_le_document_se_genere(dossier_pv):
    pv, _ = _proces_verbal_genere(dossier_pv, "PVPDF1")

    assert bytes(pv.fichier_pdf)[:4] == b"%PDF"
    assert len(pv.fichier_pdf) > 500


def test_il_contient_les_intitules_rangs_et_decisions(dossier_pv):
    pv, stagiaire = _proces_verbal_genere(dossier_pv, "PVPDF3")

    texte = _texte_du_pdf(bytes(pv.fichier_pdf))

    # Comparaison sans espaces : WeasyPrint/pypdf insèrent parfois un espace
    # parasite au sein d'un mot (crénage de police mal interprété par
    # l'extraction, constaté réellement sur « EVAL » en gras) — la présence
    # du contenu importe, pas la position exacte d'un espace de rendu.
    texte_sans_espaces = texte.replace(" ", "").replace("\n", "")
    assert str(stagiaire).replace(" ", "") in texte_sans_espaces
    assert dossier_pv.brigade.designation in texte_sans_espaces
    assert "Admis" in texte
    assert "1" in texte  # rang


def test_aucune_requete_reseau(dossier_pv, monkeypatch):
    _noter(dossier_pv, "PVPDF2")

    def _interdit(*args, **kwargs):
        raise AssertionError("tentative de connexion réseau pendant la production du PDF")

    monkeypatch.setattr(socket.socket, "connect", _interdit)

    pv = ServiceProcesVerbal.generer(
        dossier_pv.examens, dossier_pv.session, TypeProcesVerbal.FIN_DE_FORMATION
    )

    assert bytes(pv.fichier_pdf)[:4] == b"%PDF"
