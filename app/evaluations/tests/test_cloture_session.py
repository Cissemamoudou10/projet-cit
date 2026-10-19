"""US-SES-09, C2/C3 (prompt 47) — la part qui exige une évaluation, une
note ou un procès-verbal : `organisation` ne peut pas importer
`evaluations` (sens de dépendance interdit,
`tests/architecture/test_couches.py`), ces tests vivent donc ici, pas dans
`organisation/tests/`. Le reste de la story (C3 hors évaluations, C5, C6,
consultabilité, HTTP) est dans `organisation/tests/test_cloture_session.py`.
Données entièrement fictives.
"""

import datetime

import pytest
from django.urls import reverse
from django.utils import timezone

from evaluations.forms import FormulaireEvaluation
from evaluations.models import Evaluation, ProcesVerbal, TypeEvaluation, TypeProcesVerbal
from evaluations.services.evaluation import ServiceEvaluation
from evaluations.services.note import ServiceNote
from evaluations.tests.conftest import affecter_stagiaires
from noyau.exceptions import ErreurValidation
from organisation.models import EtatSession
from organisation.services.cloture import ServiceClotureSession


def _evaluation(session):
    return Evaluation.objects.create(
        element_referentiel=session.formation.elements_referentiel.get(),
        session=session,
        type=TypeEvaluation.CERTIFICATIVE,
        date=timezone.localdate() + datetime.timedelta(days=5),
        note_maximale=20,
    )


def _verrouiller(session, evaluation):
    pv = ProcesVerbal.objects.create(
        type=TypeProcesVerbal.EVALUATION,
        session=session,
        evaluation=evaluation,
        numero="",
        version=1,
        fichier_pdf=b"%PDF-essai",
    )
    pv.evaluations_couvertes.set([evaluation])
    return pv


# --- C2 — évaluations non finalisées ----------------------------------------


def test_refus_avec_evaluation_non_verrouillee_enumeree(redacteur, examens, session, brigade):
    evaluation = _evaluation(session)
    stagiaire = affecter_stagiaires(redacteur, brigade, 1, prefixe="CLOS")[0]
    ServiceNote.confirmer(
        examens, evaluation, {str(stagiaire.pk): {"valeur": "15", "absent": False}}
    )

    with pytest.raises(ErreurValidation) as info:
        ServiceClotureSession.cloturer(redacteur, session)

    assert str(evaluation) in str(info.value)
    session.refresh_from_db()
    assert session.etat == EtatSession.OUVERTE


def test_cloture_admise_apres_proces_verbal(redacteur, examens, session, brigade):
    evaluation = _evaluation(session)
    stagiaire = affecter_stagiaires(redacteur, brigade, 1, prefixe="CLOV")[0]
    ServiceNote.confirmer(
        examens, evaluation, {str(stagiaire.pk): {"valeur": "15", "absent": False}}
    )
    _verrouiller(session, evaluation)

    cloturee = ServiceClotureSession.cloturer(redacteur, session)

    assert cloturee.etat == EtatSession.CLOTUREE


# --- C3 — disparaît de la création d'évaluation -----------------------------


def test_session_et_brigade_absentes_du_formulaire_apres_cloture(redacteur, session, brigade):
    ServiceClotureSession.cloturer(redacteur, session)

    formulaire = FormulaireEvaluation()

    assert session.pk not in formulaire.fields["session"].queryset.values_list("pk", flat=True)
    assert brigade.pk not in formulaire.fields["brigade"].queryset.values_list("pk", flat=True)


def test_creation_refusee_sur_session_cloturee_meme_par_appel_direct(redacteur, examens, session):
    """Contourne le formulaire (identifiant de session connu) : le service
    doit refuser lui-même, pas seulement filtrer les querysets proposés à
    l'écran (`.claude/rules/vues.md`, trouvé en relecture)."""
    ServiceClotureSession.cloturer(redacteur, session)

    with pytest.raises(ErreurValidation, match="clôturée"):
        ServiceEvaluation.creer(
            examens,
            {
                "element_referentiel": session.formation.elements_referentiel.get(),
                "type": "certificative",
                "session": session,
                "brigade": None,
                "date": timezone.localdate() + datetime.timedelta(days=30),
                "creneau_type": None,
                "instructeur": None,
                "lieu": None,
                "motif_date_passee": "",
            },
        )


# --- HTTP --------------------------------------------------------------


def test_http_confirmation_bloquee_si_non_finalisee(client, redacteur, examens, session, brigade):
    evaluation = _evaluation(session)
    stagiaire = affecter_stagiaires(redacteur, brigade, 1, prefixe="CLOH")[0]
    ServiceNote.confirmer(
        examens, evaluation, {str(stagiaire.pk): {"valeur": "15", "absent": False}}
    )
    client.force_login(redacteur)

    reponse = client.get(reverse("organisation:cloturer_session", args=[session.pk]))

    assert reponse.status_code == 200
    assert str(evaluation) in reponse.content.decode("utf-8")
    assert "Clôturer</button>" not in reponse.content.decode("utf-8")
