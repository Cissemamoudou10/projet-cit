"""US-EVAL-01, bloc D — habilitations. D5 à D8 (arbitrage du point 3,
D-174) portent directement sur `ServiceEcritureSeance`, la porte unique :
un utilisateur de la cellule examens n'a et ne doit jamais avoir
`noyau.programme_ecriture`.
"""

import datetime
import inspect

import pytest
from django.utils import timezone

from evaluations.services.evaluation import ServiceEvaluation
from noyau.exceptions import ErreurHabilitation
from noyau.habilitations import a_permission
from planification.models import ProgrammeHebdomadaire
from planification.services.contraintes import Candidate
from planification.services.ecriture import ServiceEcritureSeance


def _donnees(**kwargs):
    base = {
        "element_referentiel": None,
        "type": "certificative",
        "session": None,
        "brigade": None,
        "date": None,
        "creneau_type": None,
        "instructeur": None,
        "lieu": None,
        "motif_date_passee": "",
    }
    base.update(kwargs)
    return base


def test_d1_examens_cree(examens, brigade, element_referentiel):
    donnees = _donnees(
        element_referentiel=element_referentiel,
        session=brigade.session,
        date=timezone.localdate() + datetime.timedelta(days=30),
    )
    evaluation = ServiceEvaluation.creer(examens, donnees)
    assert evaluation.pk is not None


def test_d2_direction_de_formation_lit_ne_cree_pas(direction_formation):
    assert a_permission(direction_formation, ServiceEvaluation.PERMISSION_LECTURE)
    assert not a_permission(direction_formation, ServiceEvaluation.PERMISSION_ECRITURE)


@pytest.mark.parametrize(
    "nom_fixture", ["planificateur", "redacteur", "direction_formation", "administrateur"]
)
def test_d3_autres_profils_refuses_en_ecriture(request, nom_fixture, brigade, element_referentiel):
    utilisateur = request.getfixturevalue(nom_fixture)
    donnees = _donnees(
        element_referentiel=element_referentiel,
        session=brigade.session,
        date=timezone.localdate() + datetime.timedelta(days=30),
    )
    with pytest.raises(ErreurHabilitation):
        ServiceEvaluation.creer(utilisateur, donnees)


def _programme_et_candidate(controle):
    jour_creneau = controle.jour_creneau
    debut = timezone.make_aware(
        datetime.datetime.combine(jour_creneau.jour, jour_creneau.creneau.heure_debut)
    )
    fin = timezone.make_aware(
        datetime.datetime.combine(jour_creneau.jour, jour_creneau.creneau.heure_fin)
    )
    lundi = jour_creneau.jour - datetime.timedelta(days=jour_creneau.jour.weekday())
    programme = ProgrammeHebdomadaire.objects.create(lundi_de_semaine=lundi)
    candidate = Candidate(
        brigade=controle.brigade,
        element_referentiel=controle.element_referentiel,
        instructeur=controle.instructeur,
        debut=debut,
        fin=fin,
    )
    return programme, [candidate]


def test_d5_examens_via_inserer_seance_de_controle_admis(controle):
    programme, candidates = _programme_et_candidate(controle)
    seance = ServiceEcritureSeance.inserer_seance_de_controle(
        controle.examens, programme, candidates
    )
    assert seance.pk is not None


def test_d6_examens_via_creer_seance_toujours_refuse(controle):
    programme, candidates = _programme_et_candidate(controle)
    with pytest.raises(ErreurHabilitation):
        ServiceEcritureSeance.creer_seance(controle.examens, programme, candidates)


def test_d7_planification_via_inserer_seance_de_controle_refuse(controle, planificateur):
    programme, candidates = _programme_et_candidate(controle)
    with pytest.raises(ErreurHabilitation):
        ServiceEcritureSeance.inserer_seance_de_controle(planificateur, programme, candidates)


def test_d8_seance_creee_verrouillee_sans_qu_aucun_parametre_ne_l_ait_demande(controle):
    """A3 : aucun paramètre de `inserer_seance_de_controle` ne permet de
    l'écrire non verrouillée — vérifié par sa signature elle-même, pas
    seulement par le résultat."""
    signature = inspect.signature(ServiceEcritureSeance.inserer_seance_de_controle)
    assert "verrouillee" not in signature.parameters

    programme, candidates = _programme_et_candidate(controle)
    seance = ServiceEcritureSeance.inserer_seance_de_controle(
        controle.examens, programme, candidates
    )
    assert seance.verrouillee is True
