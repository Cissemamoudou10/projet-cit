"""D-51 (RG-22, US-INS-02) — fermeture RÉELLE, pas par déclaration (leçon de
D-50, § 9 Prompt 30) : `ServiceQualification.retirer` (`ressources`) doit
réellement refuser quand une séance future existe, via le résolveur de
`noyau` câblé par `planification.apps.PlanificationConfig.ready()`. Ce test
vit ici, jamais côté `ressources`, qui ne peut pas construire de `Seance`
(sens de dépendance interdit — voir D-128/D-133). Données entièrement
fictives.
"""

import datetime

import pytest

from noyau.exceptions import ErreurValidation
from noyau.services.parametres import ResolveurSeancesFuturesQualification
from planification.models import ProgrammeHebdomadaire, Seance
from planification.selectors import seances_futures_qualification
from ressources.models import Qualification
from ressources.services.qualification import ServiceQualification


def test_le_fournisseur_de_planification_est_installe_au_demarrage():
    assert ResolveurSeancesFuturesQualification._fournisseur is seances_futures_qualification


def test_retrait_refuse_si_une_seance_future_existe(redacteur, element_referentiel, instructeur):
    qualification = Qualification.objects.create(
        instructeur=instructeur, matiere=element_referentiel.matiere
    )
    demain = datetime.date.today() + datetime.timedelta(days=7)
    lundi = demain + datetime.timedelta(days=(7 - demain.weekday()) % 7)
    programme = ProgrammeHebdomadaire.objects.create(lundi_de_semaine=lundi)
    debut = datetime.datetime(lundi.year, lundi.month, lundi.day, 8, tzinfo=datetime.UTC)
    seance = Seance.objects.create(
        programme=programme,
        element_referentiel=element_referentiel,
        instructeur=instructeur,
        debut=debut,
        fin=debut + datetime.timedelta(minutes=105),
    )

    with pytest.raises(ErreurValidation) as info:
        ServiceQualification.retirer(redacteur, qualification)

    assert str(seance) in str(info.value)
    assert Qualification.objects.filter(pk=qualification.pk).exists()


def test_retrait_accepte_si_aucune_seance_future(redacteur, element_referentiel, instructeur):
    qualification = Qualification.objects.create(
        instructeur=instructeur, matiere=element_referentiel.matiere
    )

    ServiceQualification.retirer(redacteur, qualification)

    assert not Qualification.objects.filter(pk=qualification.pk).exists()


def test_seance_passee_ne_bloque_pas_le_retrait(redacteur, element_referentiel, instructeur):
    qualification = Qualification.objects.create(
        instructeur=instructeur, matiere=element_referentiel.matiere
    )
    hier = datetime.date.today() - datetime.timedelta(days=7)
    lundi = hier - datetime.timedelta(days=hier.weekday())
    programme = ProgrammeHebdomadaire.objects.create(lundi_de_semaine=lundi)
    debut = datetime.datetime(lundi.year, lundi.month, lundi.day, 8, tzinfo=datetime.UTC)
    Seance.objects.create(
        programme=programme,
        element_referentiel=element_referentiel,
        instructeur=instructeur,
        debut=debut,
        fin=debut + datetime.timedelta(minutes=105),
    )

    ServiceQualification.retirer(redacteur, qualification)

    assert not Qualification.objects.filter(pk=qualification.pk).exists()
