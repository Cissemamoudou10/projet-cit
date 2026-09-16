"""US-PLAN-04, Groupe I (I2) — `ServiceEcritureSeance`, la porte d'écriture
unique : toute tentative violant une règle est refusée par ce chemin, jamais
seulement par `ServiceContraintes` isolément. Prompt 30, § 5. Données
entièrement fictives.
"""

import datetime

import pytest

from noyau.exceptions import ErreurHabilitation, ErreurValidation
from planification.models import LigneProgramme, Seance
from planification.services.contraintes import Candidate
from planification.services.ecriture import ServiceEcritureSeance
from planification.tests.conftest import instant, qualifier


def _candidate(brigade, cours, debut, duree_min=105, **kw):
    fin = debut + datetime.timedelta(minutes=duree_min)
    return Candidate(
        brigade=brigade,
        element_referentiel=cours.element,
        instructeur=cours.instructeur,
        debut=debut,
        fin=fin,
        **kw,
    )


def test_creation_nominale_journalisee(planificateur, programme, cours, brigade):
    qualifier(cours.instructeur, cours.element.matiere)
    candidate = _candidate(brigade, cours, instant(programme.lundi_de_semaine, 0, 8))

    seance = ServiceEcritureSeance.creer_seance(planificateur, programme, [candidate])

    assert Seance.objects.filter(pk=seance.pk).exists()
    assert LigneProgramme.objects.filter(seance=seance, brigade=brigade).exists()


def test_creation_regroupee_plusieurs_lignes(
    planificateur, programme, cours, brigade, autre_brigade
):
    qualifier(cours.instructeur, cours.element.matiere)
    debut = instant(programme.lundi_de_semaine, 0, 8)
    candidates = [
        _candidate(b, cours, debut, cle_regroupement="groupe-ecriture")
        for b in (brigade, autre_brigade)
    ]

    seance = ServiceEcritureSeance.creer_seance(planificateur, programme, candidates)

    assert seance.lignes.count() == 2


def test_i2_tentative_violant_une_regle_refusee_par_le_chemin_de_service(
    planificateur, programme, cours, brigade
):
    """Aucune qualification posée : RG-35 refuse — et rien n'est écrit."""
    candidate = _candidate(brigade, cours, instant(programme.lundi_de_semaine, 0, 8))
    avant = Seance.objects.count()

    with pytest.raises(ErreurValidation, match="RG-35"):
        ServiceEcritureSeance.creer_seance(planificateur, programme, [candidate])

    assert Seance.objects.count() == avant


def test_habilitation_programme_ecriture_requise(redacteur, programme, cours, brigade):
    qualifier(cours.instructeur, cours.element.matiere)
    candidate = _candidate(brigade, cours, instant(programme.lundi_de_semaine, 0, 8))

    with pytest.raises(ErreurHabilitation):
        ServiceEcritureSeance.creer_seance(redacteur, programme, [candidate])
