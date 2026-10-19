"""Résolveur de charge d'enseignement — US-INS-04, C1 (prompt 48). Ce test
vit ici, jamais côté `ressources`, qui ne peut pas construire de `Seance`
(sens de dépendance interdit — même motif que `test_resolveur_qualification.py`,
D-128/D-133). Données entièrement fictives.
"""

import datetime

from django.db import connection
from django.test import override_settings
from django.test.utils import CaptureQueriesContext

from noyau.services.parametres import ResolveurHeuresEnseignementParInstructeur
from planification.models import LigneProgramme, ProgrammeHebdomadaire
from planification.selectors_charge_instructeur import heures_enseignement_par_instructeur
from planification.tests.aide_circuit import seance_dans
from planification.tests.conftest import Cours, creer_element, instant, qualifier
from referentiel.models import Matiere
from ressources.models import Instructeur, Statut
from ressources.selectors_charge import charge_d_un_instructeur, charge_instructeurs


def _element(formation, volume, suffixe):
    matiere = Matiere.objects.create(intitule=f"Matière charge {suffixe}", code=f"CHG{suffixe}")
    return creer_element(formation, matiere, volume=volume)


def _programme(decalage_semaines=10):
    lundi = datetime.date.today() + datetime.timedelta(weeks=decalage_semaines)
    lundi -= datetime.timedelta(days=lundi.weekday())
    return ProgrammeHebdomadaire.objects.create(lundi_de_semaine=lundi)


def test_le_fournisseur_de_planification_est_installe_au_demarrage():
    assert (
        ResolveurHeuresEnseignementParInstructeur._fournisseur
        is heures_enseignement_par_instructeur
    )


def test_regroupement_compte_une_fois(circuit, autre_brigade_formation):
    lundi = circuit.programme.lundi_de_semaine
    seance_regroupee = seance_dans(circuit.programme, circuit.cours, circuit.brigade, instant(lundi, 0, 8))
    LigneProgramme.objects.create(seance=seance_regroupee, brigade=autre_brigade_formation)
    debut, fin = instant(lundi, 0, 0), instant(lundi, 1, 0)

    resultat = heures_enseignement_par_instructeur(debut, fin)

    total = sum(detail["heures"] for detail in resultat[circuit.cours.instructeur.pk])
    assert total == 2.0


def test_periode_qui_coupe_une_semaine(instructeur, brigade_formation):
    """La période s'étend sur deux programmes (deux semaines) : les deux
    séances comptent, sans alignement artificiel sur une semaine entière."""
    formation = brigade_formation.session.formation
    element = _element(formation, volume=20, suffixe="P1")
    qualifier(instructeur, element.matiere)
    cours = Cours(element, instructeur)
    premiere = _programme(decalage_semaines=10)
    seconde = _programme(decalage_semaines=11)
    seance_dans(premiere, cours, brigade_formation, instant(premiere.lundi_de_semaine, 3, 8))
    seance_dans(seconde, cours, brigade_formation, instant(seconde.lundi_de_semaine, 1, 8))
    debut = instant(premiere.lundi_de_semaine, 3, 0)
    fin = instant(seconde.lundi_de_semaine, 2, 0)

    resultat = heures_enseignement_par_instructeur(debut, fin)

    total = sum(detail["heures"] for detail in resultat[instructeur.pk])
    assert total == 4.0


def test_seuil_franchi(instructeur, brigade_formation):
    formation = brigade_formation.session.formation
    element = _element(formation, volume=40, suffixe="S1")
    qualifier(instructeur, element.matiere)
    cours = Cours(element, instructeur)
    programme = _programme(decalage_semaines=12)
    for jour in range(5):
        seance_dans(
            programme, cours, brigade_formation, instant(programme.lundi_de_semaine, jour, 8), 360
        )  # 6 h × 5 jours = 30 h en une semaine
    debut = instant(programme.lundi_de_semaine, 0, 0)
    fin = instant(programme.lundi_de_semaine, 6, 23)

    with override_settings(SEUIL_CHARGE_HEBDOMADAIRE_INSTRUCTEUR="24"):
        ligne = charge_d_un_instructeur(instructeur, debut, fin)

    assert ligne.seuil_franchi is True


def test_requetes_constantes_avec_cinq_et_cinquante_instructeurs(db):
    def _instructeurs(prefixe, nombre):
        for i in range(nombre):
            Instructeur.objects.create(
                nom=f"Nom{prefixe}{i}",
                prenom="Prénom",
                matricule=f"MX{prefixe}{i}",
                grade="Lt",
                specialite="Transmissions",
                statut=Statut.MILITAIRE_DU_CENTRE,
            )

    _instructeurs("A", 5)
    debut = instant(datetime.date.today(), -14, 0)
    fin = instant(datetime.date.today(), 14, 0)

    charge_instructeurs(debut, fin)  # chauffe
    with CaptureQueriesContext(connection) as cinq:
        charge_instructeurs(debut, fin)

    _instructeurs("B", 45)
    with CaptureQueriesContext(connection) as cinquante:
        charge_instructeurs(debut, fin)

    assert len(cinq.captured_queries) == len(cinquante.captured_queries)
