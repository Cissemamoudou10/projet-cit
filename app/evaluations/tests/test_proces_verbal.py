"""US-EVAL-07 — Générer les procès-verbaux de résultats, RG-58, RG-59,
CU-P6-07. Le modèle et ses contraintes en base, puis le service — le
PDF réel et le déroulement HTTP sont dans test_proces_verbal_pdf.py et
test_proces_verbal_ecran.py.
"""

import pytest
from django.db import IntegrityError, transaction
from django.test import override_settings

from administration.models import EntreeJournal, TypeAction
from evaluations.models import ProcesVerbal, TypeProcesVerbal
from evaluations.services.note import ServiceNote
from evaluations.services.proces_verbal import ServiceProcesVerbal
from evaluations.tests.conftest import affecter_stagiaires
from noyau.exceptions import ErreurValidation


@pytest.fixture(autouse=True)
def _pdf_simule(monkeypatch):
    """Ces tests exercent le verrouillage et la journalisation, pas le
    rendu PDF réel (couvert par test_proces_verbal_pdf.py, marqué `pdf`) —
    un test qui règle lui-même son propre monkeypatch (échec forcé,
    versions distinctes) l'écrase simplement ensuite, sans conflit."""
    monkeypatch.setattr(
        "evaluations.services.proces_verbal.ServiceDocument.produire", lambda *a, **k: b"%PDF-essai"
    )


def _noter(dossier, prefixe, valeur="15"):
    stagiaire = affecter_stagiaires(dossier.redacteur, dossier.brigade, 1, prefixe=prefixe)[0]
    ServiceNote.confirmer(
        dossier.examens,
        dossier.certificative,
        {str(stagiaire.pk): {"valeur": valeur, "absent": False}},
    )
    return stagiaire


# --- Base : contraintes en base ---


def test_fin_de_formation_sans_evaluation_est_acceptee_en_base(session):
    ProcesVerbal.objects.create(
        type=TypeProcesVerbal.FIN_DE_FORMATION, session=session, fichier_pdf=b""
    )  # ne lève pas


def test_evaluation_absente_pour_le_type_evaluation_est_refusee_en_base(session, certificative):
    with pytest.raises(IntegrityError), transaction.atomic():
        ProcesVerbal.objects.create(
            type=TypeProcesVerbal.EVALUATION,
            session=session,
            evaluation=None,
            fichier_pdf=b"",
        )


def test_evaluation_renseignee_avec_fin_de_formation_est_refusee_en_base(session, certificative):
    with pytest.raises(IntegrityError), transaction.atomic():
        ProcesVerbal.objects.create(
            type=TypeProcesVerbal.FIN_DE_FORMATION,
            session=session,
            evaluation=certificative,
            fichier_pdf=b"",
        )


# --- Service : ServiceProcesVerbal ---


def test_generation_refusee_sur_note_manquante_avec_la_liste(dossier_pv):
    affecter_stagiaires(dossier_pv.redacteur, dossier_pv.brigade, 1, prefixe="PVM1")

    with pytest.raises(ErreurValidation) as info:
        ServiceProcesVerbal.generer(
            dossier_pv.examens, dossier_pv.session, TypeProcesVerbal.FIN_DE_FORMATION
        )

    assert "manquante" in str(info.value).lower()
    assert not ProcesVerbal.objects.exists()


def test_notes_verrouillees_apres_generation_puis_ecriture_refusee(dossier_pv):
    stagiaire = _noter(dossier_pv, "PVL1")

    ServiceProcesVerbal.generer(
        dossier_pv.examens, dossier_pv.session, TypeProcesVerbal.FIN_DE_FORMATION
    )

    with pytest.raises(ErreurValidation) as info:
        ServiceNote.confirmer(
            dossier_pv.examens,
            dossier_pv.certificative,
            {str(stagiaire.pk): {"valeur": "16", "absent": False}},
        )
    assert "verrouillé" in str(info.value).lower()


def test_deux_proces_verbaux_sur_la_meme_evaluation(dossier_pv):
    """V3 : une évaluation peut être couverte par son propre procès-verbal
    PUIS par celui de fin de formation — jamais un seul à la fois."""
    _noter(dossier_pv, "PVD1")

    pv_evaluation = ServiceProcesVerbal.generer(
        dossier_pv.examens,
        dossier_pv.session,
        TypeProcesVerbal.EVALUATION,
        dossier_pv.certificative,
    )
    pv_session = ServiceProcesVerbal.generer(
        dossier_pv.examens, dossier_pv.session, TypeProcesVerbal.FIN_DE_FORMATION
    )

    assert dossier_pv.certificative in pv_evaluation.evaluations_couvertes.all()
    assert dossier_pv.certificative in pv_session.evaluations_couvertes.all()
    assert dossier_pv.certificative.proces_verbaux_verrouillants.count() == 2


def test_echec_du_pdf_ne_verrouille_aucune_note(dossier_pv, monkeypatch):
    stagiaire = _noter(dossier_pv, "PVE1")

    def _echoue(*args, **kwargs):
        raise RuntimeError("échec forcé du rendu PDF")

    monkeypatch.setattr("evaluations.services.proces_verbal.ServiceDocument.produire", _echoue)

    with pytest.raises(RuntimeError):
        ServiceProcesVerbal.generer(
            dossier_pv.examens, dossier_pv.session, TypeProcesVerbal.FIN_DE_FORMATION
        )

    assert not ProcesVerbal.objects.exists()
    assert not dossier_pv.certificative.proces_verbaux_verrouillants.exists()
    # La note reste écrivable : rien n'a verrouillé l'évaluation.
    ServiceNote.confirmer(
        dossier_pv.examens,
        dossier_pv.certificative,
        {str(stagiaire.pk): {"valeur": "17", "absent": False}},
    )


def test_regeneration_rend_le_meme_fichier(dossier_pv):
    _noter(dossier_pv, "PVR1")

    pv = ServiceProcesVerbal.generer(
        dossier_pv.examens, dossier_pv.session, TypeProcesVerbal.FIN_DE_FORMATION
    )
    telecharge_une_fois = ServiceProcesVerbal.telecharger(dossier_pv.examens, pv)
    telecharge_deux_fois = ServiceProcesVerbal.telecharger(dossier_pv.examens, pv)

    assert telecharge_une_fois == telecharge_deux_fois == b"%PDF-essai"


def test_nouvelle_version_apres_une_seconde_generation_l_ancienne_reste(dossier_pv, monkeypatch):
    _noter(dossier_pv, "PVV1")
    contenus = iter([b"%PDF-v1", b"%PDF-v2"])
    monkeypatch.setattr(
        "evaluations.services.proces_verbal.ServiceDocument.produire",
        lambda *a, **k: next(contenus),
    )

    v1 = ServiceProcesVerbal.generer(
        dossier_pv.examens, dossier_pv.session, TypeProcesVerbal.FIN_DE_FORMATION
    )
    v2 = ServiceProcesVerbal.generer(
        dossier_pv.examens, dossier_pv.session, TypeProcesVerbal.FIN_DE_FORMATION
    )

    assert v1.version == 1
    assert v2.version == 2
    assert ServiceProcesVerbal.telecharger(dossier_pv.examens, v1) == b"%PDF-v1"
    assert ServiceProcesVerbal.telecharger(dossier_pv.examens, v2) == b"%PDF-v2"
    assert ProcesVerbal.objects.filter(session=dossier_pv.session).count() == 2


def test_seuil_modifie_par_parametre_change_la_decision(dossier_pv):
    _noter(dossier_pv, "PVS1", valeur="12")

    apercu_defaut = ServiceProcesVerbal.apercu(dossier_pv.examens, dossier_pv.session)
    assert apercu_defaut.lignes[0].decision == "Admis"

    with override_settings(SEUIL_ADMISSION_PROCES_VERBAL="15"):
        apercu_seuil_releve = ServiceProcesVerbal.apercu(dossier_pv.examens, dossier_pv.session)
    assert apercu_seuil_releve.lignes[0].decision == "Ajourné"


def test_generation_est_journalisee(dossier_pv):
    _noter(dossier_pv, "PVJ1")

    ServiceProcesVerbal.generer(
        dossier_pv.examens, dossier_pv.session, TypeProcesVerbal.FIN_DE_FORMATION
    )

    assert EntreeJournal.objects.filter(type_action=TypeAction.GENERATION_PROCES_VERBAL).exists()
