"""US-PLAN-09 — traitement d'une indisponibilité déclarée (prompt 42,
partie 3). Données fictives.
"""

import datetime

import pytest
from django.utils import timezone

from noyau.exceptions import ErreurValidation
from organisation.services.brigade import ServiceBrigade
from organisation.services.session import ServiceSession
from planification.exceptions import TransitionProgrammeRefusee
from planification.models import EtatProgramme, NatureAvenant, ProgrammeHebdomadaire
from planification.selectors_indisponibilite import (
    instructeurs_remplacants,
    seances_impactees_par_indisponibilite,
)
from planification.services.circuit import ServiceCircuitProgramme
from planification.services.ecriture import ServiceEcritureSeance
from planification.services.indisponibilite import traiter_lot_remplacement
from planification.services.modification import Avenantage
from planification.tests.aide_circuit import seance_dans
from planification.tests.conftest import Cours, creer_element, instant, qualifier
from referentiel.models import Formation, Matiere, Prerequis, TypeFormation
from ressources.services.indisponibilite_instructeur import ServiceIndisponibiliteInstructeur

SIGNATAIRE = "Signataire essai"


def _programme(lundi):
    return ProgrammeHebdomadaire.objects.create(lundi_de_semaine=lundi)


def _indisponibilite(planificateur, instructeur, debut, fin):
    return ServiceIndisponibiliteInstructeur.confirmer(
        planificateur, instructeur, debut, fin, "Mission (essai)"
    )


def _amener_a_valide(programme, acteurs):
    ServiceCircuitProgramme.soumettre(acteurs.planificateur, programme)
    ServiceCircuitProgramme.valider(acteurs.pedagogique, programme)


def _amener_a_affiche(programme, acteurs):
    _amener_a_valide(programme, acteurs)
    ServiceCircuitProgramme.enregistrer_signature(
        acteurs.planificateur, programme, timezone.localdate(), SIGNATAIRE
    )
    ServiceCircuitProgramme.afficher(acteurs.planificateur, programme)


# --- I2 : séances impactées --------------------------------------------------


def test_i2_liste_les_seances_impactees_sur_deux_brigades_et_trois_etats_de_programme(
    circuit, cours, brigade_formation, autre_brigade_formation
):
    lundi = circuit.programme.lundi_de_semaine
    programme_valide = _programme(lundi + datetime.timedelta(weeks=1))
    programme_affiche = _programme(lundi + datetime.timedelta(weeks=2))
    seance_brouillon = seance_dans(
        circuit.programme, cours, brigade_formation, instant(lundi, 0, 8)
    )
    seance_valide = seance_dans(
        programme_valide,
        cours,
        autre_brigade_formation,
        instant(lundi + datetime.timedelta(weeks=1), 0, 8),
    )
    seance_affiche = seance_dans(
        programme_affiche,
        cours,
        brigade_formation,
        instant(lundi + datetime.timedelta(weeks=2), 0, 8),
    )
    _amener_a_valide(programme_valide, circuit.acteurs)
    _amener_a_affiche(programme_affiche, circuit.acteurs)

    indisponibilite = _indisponibilite(
        circuit.acteurs.planificateur,
        cours.instructeur,
        instant(lundi, 0, 0),
        instant(lundi + datetime.timedelta(weeks=3), 0, 0),
    )

    impactees = seances_impactees_par_indisponibilite(indisponibilite)

    assert {s.pk for s in impactees} == {seance_brouillon.pk, seance_valide.pk, seance_affiche.pk}
    assert {s.lignes.first().brigade for s in impactees} == {
        brigade_formation,
        autre_brigade_formation,
    }


def test_i2_exclut_une_seance_deja_commencee(cours, redacteur, planificateur):
    type_formation = TypeFormation.objects.create(intitule="Type passé (essai)")
    formation = Formation.objects.create(
        intitule="Formation passée (essai)",
        specialite="Transmissions",
        duree_semaines=10,
        type_formation=type_formation,
    )
    creer_element(
        formation,
        Matiere.objects.create(intitule="Semence passée (essai)", code="SEM-P1"),
        volume=1,
    )
    session = ServiceSession.creer(
        redacteur,
        {
            "formation": formation,
            "intitule": "Session passée (essai)",
            "date_debut": datetime.date(2019, 1, 1),
            "date_fin": datetime.date(2020, 12, 31),
            "effectif_attendu": 10,
        },
    )
    brigade = ServiceBrigade.creer(
        redacteur, session, {"designation": "PAS1", "effectif_previsionnel": 10}
    )
    programme_passe = _programme(datetime.date(2020, 1, 6))
    debut_passe = datetime.datetime(2020, 1, 6, 8, 0, tzinfo=datetime.UTC)
    seance_dans(programme_passe, cours, brigade, debut_passe)

    indisponibilite = _indisponibilite(
        planificateur, cours.instructeur, debut_passe, debut_passe + datetime.timedelta(hours=4)
    )

    assert seances_impactees_par_indisponibilite(indisponibilite) == []


# --- I1 : remplacer, substituer, déprogrammer (BROUILLON) -------------------


def test_remplacement_admis_modifie_l_instructeur_et_verrouille(
    circuit, cours, brigade_formation, autre_instructeur
):
    qualifier(autre_instructeur, cours.element.matiere)
    seance = seance_dans(
        circuit.programme,
        cours,
        brigade_formation,
        instant(circuit.programme.lundi_de_semaine, 0, 8),
    )

    ServiceEcritureSeance.modifier_seance(
        circuit.acteurs.planificateur, seance, {"instructeur": autre_instructeur}
    )

    seance.refresh_from_db()
    assert seance.instructeur == autre_instructeur
    assert seance.verrouillee is True


def test_remplacant_non_qualifie_est_refuse_par_les_contraintes(
    circuit, cours, brigade_formation, autre_instructeur
):
    seance = seance_dans(
        circuit.programme,
        cours,
        brigade_formation,
        instant(circuit.programme.lundi_de_semaine, 0, 8),
    )

    with pytest.raises(ErreurValidation, match="RG-35"):
        ServiceEcritureSeance.modifier_seance(
            circuit.acteurs.planificateur, seance, {"instructeur": autre_instructeur}
        )


def test_substitution_admise_change_la_matiere(circuit, cours, brigade_formation):
    autre_matiere = Matiere.objects.create(intitule="Substitution (essai)", code="SUB01")
    autre_element = creer_element(cours.element.formation, autre_matiere, volume=20)
    qualifier(cours.instructeur, autre_matiere)
    seance = seance_dans(
        circuit.programme,
        cours,
        brigade_formation,
        instant(circuit.programme.lundi_de_semaine, 0, 8),
    )

    ServiceEcritureSeance.modifier_seance(
        circuit.acteurs.planificateur, seance, {"element_referentiel": autre_element}
    )

    seance.refresh_from_db()
    assert seance.element_referentiel == autre_element


def test_substitution_violant_un_prerequis_est_refusee(circuit, cours, brigade_formation):
    autre_matiere = Matiere.objects.create(intitule="Substitution refusée (essai)", code="SUB02")
    autre_element = creer_element(cours.element.formation, autre_matiere, volume=20)
    qualifier(cours.instructeur, autre_matiere)
    prerequis = creer_element(
        cours.element.formation,
        Matiere.objects.create(intitule="Bases (essai)", code="BAS2"),
        volume=4,
    )
    Prerequis.objects.create(element=autre_element, element_prerequis=prerequis)
    seance = seance_dans(
        circuit.programme,
        cours,
        brigade_formation,
        instant(circuit.programme.lundi_de_semaine, 0, 8),
    )

    with pytest.raises(ErreurValidation, match="RG-39"):
        ServiceEcritureSeance.modifier_seance(
            circuit.acteurs.planificateur, seance, {"element_referentiel": autre_element}
        )


def test_deprogrammation_admise_sur_un_brouillon(circuit, cours, brigade_formation):
    seance = seance_dans(
        circuit.programme,
        cours,
        brigade_formation,
        instant(circuit.programme.lundi_de_semaine, 0, 8),
    )

    ServiceEcritureSeance.supprimer_seance(circuit.acteurs.planificateur, seance)

    assert not circuit.programme.seances.filter(pk=seance.pk).exists()


# --- I3 : états bloquants ----------------------------------------------------


def test_seance_d_un_programme_valide_renvoie_a_l_annulation_t9(
    circuit, cours, brigade_formation, autre_instructeur
):
    qualifier(autre_instructeur, cours.element.matiere)
    seance = seance_dans(
        circuit.programme,
        cours,
        brigade_formation,
        instant(circuit.programme.lundi_de_semaine, 0, 8),
    )
    _amener_a_valide(circuit.programme, circuit.acteurs)

    with pytest.raises(TransitionProgrammeRefusee, match="T9"):
        ServiceEcritureSeance.modifier_seance(
            circuit.acteurs.planificateur, seance, {"instructeur": autre_instructeur}
        )


def test_seance_d_un_programme_affiche_exige_un_avenant_et_reste_affiche(
    circuit, cours, brigade_formation, autre_instructeur
):
    qualifier(autre_instructeur, cours.element.matiere)
    seance = seance_dans(
        circuit.programme,
        cours,
        brigade_formation,
        instant(circuit.programme.lundi_de_semaine, 0, 8),
    )
    _amener_a_affiche(circuit.programme, circuit.acteurs)

    with pytest.raises(TransitionProgrammeRefusee, match="T10"):
        ServiceEcritureSeance.modifier_seance(
            circuit.acteurs.planificateur, seance, {"instructeur": autre_instructeur}
        )

    ServiceEcritureSeance.modifier_seance(
        circuit.acteurs.planificateur,
        seance,
        {"instructeur": autre_instructeur},
        avenant=Avenantage(
            motif="Remplacement (essai).", nature=NatureAvenant.REMPLACEMENT_INSTRUCTEUR
        ),
    )

    seance.refresh_from_db()
    circuit.programme.refresh_from_db()
    assert seance.instructeur == autre_instructeur
    assert circuit.programme.etat == EtatProgramme.AFFICHE


def test_deprogrammation_refusee_sur_un_affiche(circuit, cours, brigade_formation):
    seance = seance_dans(
        circuit.programme,
        cours,
        brigade_formation,
        instant(circuit.programme.lundi_de_semaine, 0, 8),
    )
    _amener_a_affiche(circuit.programme, circuit.acteurs)

    with pytest.raises(ErreurValidation, match="non-exécution"):
        ServiceEcritureSeance.supprimer_seance(circuit.acteurs.planificateur, seance)


# --- I5 : lot -----------------------------------------------------------------


def test_lot_admis_remplace_toutes_les_seances_du_lot(
    circuit, cours, brigade_formation, autre_brigade_formation, autre_instructeur
):
    qualifier(autre_instructeur, cours.element.matiere)
    lundi = circuit.programme.lundi_de_semaine
    programme_2 = _programme(lundi + datetime.timedelta(weeks=1))
    seance_1 = seance_dans(circuit.programme, cours, brigade_formation, instant(lundi, 0, 8))
    seance_2 = seance_dans(
        programme_2,
        cours,
        autre_brigade_formation,
        instant(lundi + datetime.timedelta(weeks=1), 0, 8),
    )

    traiter_lot_remplacement(circuit.acteurs.planificateur, [seance_1, seance_2], autre_instructeur)

    seance_1.refresh_from_db()
    seance_2.refresh_from_db()
    assert seance_1.instructeur == autre_instructeur
    assert seance_2.instructeur == autre_instructeur


def test_lot_avec_une_seance_en_conflit_rien_n_est_ecrit(
    circuit, cours, brigade_formation, autre_brigade_formation, autre_instructeur
):
    qualifier(autre_instructeur, cours.element.matiere)
    lundi = circuit.programme.lundi_de_semaine
    programme_2 = _programme(lundi + datetime.timedelta(weeks=1))
    seance_1 = seance_dans(circuit.programme, cours, brigade_formation, instant(lundi, 0, 8))
    debut_2 = instant(lundi + datetime.timedelta(weeks=1), 0, 8)
    seance_2 = seance_dans(programme_2, cours, autre_brigade_formation, debut_2)
    autre_matiere = Matiere.objects.create(intitule="Conflit (essai)", code="CFL01")
    autre_element = creer_element(cours.element.formation, autre_matiere)
    qualifier(autre_instructeur, autre_matiere)
    seance_dans(
        programme_2, Cours(autre_element, autre_instructeur), autre_brigade_formation, debut_2
    )

    with pytest.raises(ErreurValidation, match="RG-34"):
        traiter_lot_remplacement(
            circuit.acteurs.planificateur, [seance_1, seance_2], autre_instructeur
        )

    seance_1.refresh_from_db()
    assert seance_1.instructeur == cours.instructeur


# --- I4 : liste des remplaçants -----------------------------------------------


def test_instructeurs_remplacants_exclut_un_non_qualifie(cours, autre_instructeur):
    debut = instant(datetime.date(2030, 3, 4), 0, 8)
    fin = debut + datetime.timedelta(hours=2)

    remplacants = instructeurs_remplacants(cours.element.matiere, debut, fin)

    assert cours.instructeur not in remplacants
    assert autre_instructeur not in remplacants


def test_instructeurs_remplacants_propose_un_qualifie_libre(cours, autre_instructeur):
    qualifier(autre_instructeur, cours.element.matiere)
    debut = instant(datetime.date(2030, 3, 4), 0, 8)
    fin = debut + datetime.timedelta(hours=2)

    remplacants = instructeurs_remplacants(cours.element.matiere, debut, fin)

    assert autre_instructeur in remplacants


def test_instructeurs_remplacants_exclut_un_indisponible(cours, autre_instructeur, planificateur):
    qualifier(autre_instructeur, cours.element.matiere)
    debut = instant(datetime.date(2030, 3, 4), 0, 8)
    fin = debut + datetime.timedelta(hours=2)
    _indisponibilite(planificateur, autre_instructeur, debut, fin)

    remplacants = instructeurs_remplacants(cours.element.matiere, debut, fin)

    assert autre_instructeur not in remplacants
