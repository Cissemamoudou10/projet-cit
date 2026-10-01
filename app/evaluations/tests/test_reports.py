"""US-EVAL-01, bloc G — reports refermés par le vrai chemin de service
(leçon D-83) : `evaluations` porte les FK protégées (`element_referentiel`,
`session`, `brigade` en `PROTECT`), ces tests vivent donc ici, pas dans les
applications protégées — même logique que D-83
(`planification.tests.test_modeles`)."""

import datetime

import pytest
from django.utils import timezone

from evaluations.models import TypeEvaluation
from evaluations.services.evaluation import ServiceEvaluation
from evaluations.tests.conftest import creer_brigade
from noyau.exceptions import ErreurValidation
from organisation.services.brigade import ServiceBrigade
from organisation.services.session import ServiceSession
from referentiel.services.referentiel import ServiceReferentiel


def test_g1_retirer_un_element_porteur_d_une_evaluation_refuse_evaluation_enumeree(
    examens, redacteur, session, element_referentiel
):
    evaluation = ServiceEvaluation.creer(
        examens,
        {
            "element_referentiel": element_referentiel,
            "type": TypeEvaluation.CERTIFICATIVE,
            "session": session,
            "brigade": None,
            "date": timezone.localdate() + datetime.timedelta(days=30),
            "creneau_type": None,
            "instructeur": None,
            "lieu": None,
            "motif_date_passee": "",
        },
    )
    with pytest.raises(ErreurValidation, match=str(evaluation)):
        ServiceReferentiel.retirer(redacteur, element_referentiel)


def test_g2_supprimer_une_brigade_porteuse_d_une_evaluation_refuse(
    examens, redacteur, brigade, element_referentiel
):
    creer_brigade(redacteur, brigade.session, "EXP2")
    ServiceEvaluation.creer(
        examens,
        {
            "element_referentiel": element_referentiel,
            "type": TypeEvaluation.CERTIFICATIVE,
            "session": None,
            "brigade": brigade,
            "date": timezone.localdate() + datetime.timedelta(days=30),
            "creneau_type": None,
            "instructeur": None,
            "lieu": None,
            "motif_date_passee": "",
        },
    )
    with pytest.raises(ErreurValidation):
        ServiceBrigade.supprimer(redacteur, brigade)


def test_g3_supprimer_une_session_porteuse_d_une_evaluation_refuse(
    examens, redacteur, formation, element_referentiel
):
    aujourd_hui = timezone.localdate()
    session_sans_brigade = ServiceSession.creer(
        redacteur,
        {
            "formation": formation,
            "intitule": "Session G3 EVAL",
            "date_debut": aujourd_hui - datetime.timedelta(days=5),
            "date_fin": aujourd_hui + datetime.timedelta(days=150),
            "effectif_attendu": 24,
        },
    )
    ServiceEvaluation.creer(
        examens,
        {
            "element_referentiel": element_referentiel,
            "type": TypeEvaluation.CERTIFICATIVE,
            "session": session_sans_brigade,
            "brigade": None,
            "date": timezone.localdate() + datetime.timedelta(days=30),
            "creneau_type": None,
            "instructeur": None,
            "lieu": None,
            "motif_date_passee": "",
        },
    )
    with pytest.raises(ErreurValidation):
        ServiceSession.supprimer(redacteur, session_sans_brigade.pk)
