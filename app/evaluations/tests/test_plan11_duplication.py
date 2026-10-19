"""US-PLAN-11 — scénarios de duplication nécessitant `evaluations` (contrôle
non dupliqué, jour d'examen sur la cible). Prompt 48, Story 4. Ni
`planification` ni `ressources` ne peuvent importer `evaluations` — même
motif que `test_rg38_examen.py`. Données entièrement fictives.
"""

import datetime

from evaluations.services.evaluation import ServiceEvaluation
from planification.models import ProgrammeHebdomadaire
from planification.services.duplication import MOTIF_CONTROLE, ServiceDuplication
from planification.tests.aide_circuit import seance_dans
from planification.tests.conftest import Cours, instant


def _lundi_cible(decalage_semaines=10):
    lundi = datetime.date.today() + datetime.timedelta(weeks=decalage_semaines)
    return lundi - datetime.timedelta(days=lundi.weekday())


def _programme_de(jour):
    lundi = jour - datetime.timedelta(days=jour.weekday())
    return ProgrammeHebdomadaire.objects.get(lundi_de_semaine=lundi)


def _certificative(examens, element_referentiel, jour, brigade):
    return ServiceEvaluation.creer(
        examens,
        {
            "element_referentiel": element_referentiel,
            "type": "certificative",
            "session": None,
            "brigade": brigade,
            "date": jour,
            "creneau_type": None,
            "instructeur": None,
            "lieu": None,
            "motif_date_passee": "",
        },
    )


def test_controle_non_duplique(formative, controle, planificateur):
    """D3 : la séance d'un contrôle, liée à une évaluation datée, n'est
    jamais dupliquée — listée avec son motif."""
    programme_source = _programme_de(controle.jour_creneau.jour)
    lundi_cible = _lundi_cible()

    compte_rendu = ServiceDuplication.dupliquer(
        planificateur, programme_source, lundi_cible, [controle.brigade]
    )

    assert compte_rendu.nombre_creees == 0
    assert len(compte_rendu.exclues) == 1
    assert compte_rendu.exclues[0].motif == MOTIF_CONTROLE


def test_refus_jour_d_examen_sur_la_cible(controle, planificateur, redacteur):
    """Contraintes dures vérifiées sur la CIBLE (critère du backlog) : un
    jour d'examen certificatif sur la semaine cible refuse la candidate,
    même si la semaine source n'en portait aucun."""
    lundi_source = controle.jour_creneau.jour - datetime.timedelta(weeks=4)
    lundi_source -= datetime.timedelta(days=lundi_source.weekday())
    programme_source = ProgrammeHebdomadaire.objects.create(lundi_de_semaine=lundi_source)
    cours = Cours(controle.element_referentiel, controle.instructeur)
    seance_dans(programme_source, cours, controle.brigade, instant(lundi_source, 0, 8))
    lundi_cible = _lundi_cible()
    _certificative(controle.examens, controle.element_referentiel, lundi_cible, controle.brigade)

    compte_rendu = ServiceDuplication.dupliquer(
        planificateur, programme_source, lundi_cible, [controle.brigade]
    )

    assert compte_rendu.nombre_creees == 0
    assert len(compte_rendu.refusees) == 1
    assert any(v["code"] == "RG-38" for v in compte_rendu.refusees[0].violations)
