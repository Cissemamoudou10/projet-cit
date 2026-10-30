"""Évolution du prompt 53, Temps 2, S3 — un programme qui porte une séance
de contrôle (évaluation formative à venir) refuse la suppression de son
brouillon, en énumérant l'évaluation concernée (D-240). Données fictives.
"""

import pytest

from evaluations.services.evaluation import ServiceEvaluation
from planification.exceptions import SuppressionProgrammeRefusee
from planification.models import EtatProgramme, ProgrammeHebdomadaire
from planification.services.generation import ServiceGeneration


def _donnees_formative(controle):
    return {
        "element_referentiel": controle.element_referentiel,
        "type": "formative",
        "session": None,
        "brigade": controle.brigade,
        "date": controle.jour_creneau.jour,
        "creneau_type": controle.jour_creneau.creneau,
        "instructeur": controle.instructeur,
        "lieu": None,
        "motif_date_passee": "",
    }


def test_s3_refuse_la_suppression_d_un_programme_portant_une_seance_de_controle(
    controle, planificateur
):
    evaluation = ServiceEvaluation.creer(controle.examens, _donnees_formative(controle))
    programme = evaluation.seance.programme
    assert programme.etat == EtatProgramme.BROUILLON

    with pytest.raises(SuppressionProgrammeRefusee, match="séance de contrôle") as erreur:
        ServiceGeneration.supprimer_brouillon(planificateur, programme, True)

    assert str(evaluation) in str(erreur.value)
    assert ProgrammeHebdomadaire.objects.filter(pk=programme.pk).exists()
