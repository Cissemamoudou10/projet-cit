"""US-PLAN-05 — modification manuelle, suppression, déverrouillage et avenant
(prompt 41, groupes A, B, C, E). Appels directs à la porte unique. Données fictives.
"""

import datetime

import pytest
from django.db import IntegrityError, transaction
from django.utils import timezone

from administration.models import EntreeJournal, TypeAction
from noyau.exceptions import ErreurValidation
from planification.exceptions import TransitionProgrammeRefusee
from planification.models import Avenant, EtatProgramme, LigneProgramme, NatureAvenant, Seance
from planification.services.circuit import ServiceCircuitProgramme
from planification.services.ecriture import ServiceEcritureSeance
from planification.services.generation import ServiceGeneration
from planification.services.modification import Avenantage
from planification.tests.aide_circuit import SIGNATAIRE, amener_a, candidature, seance_dans
from planification.tests.conftest import Cours, creer_element, instant, qualifier
from referentiel.models import Matiere, Prerequis

AVENANT = Avenantage(motif="Changement de créneau demandé.", nature=NatureAvenant.DEPLACEMENT)


def _seance_seed(circuit):
    """La séance créée par `amener_a` : une seule, sans collision de créneau."""
    return Seance.objects.get(programme=circuit.programme)


def _seance_libre(circuit, jour=0, heure=8):
    return seance_dans(
        circuit.programme, circuit.cours, circuit.brigade,
        instant(circuit.programme.lundi_de_semaine, jour, heure),
    )


def _journal_seance(seance, type_action):
    return EntreeJournal.objects.filter(
        objet_type="seance", objet_identifiant=str(seance.pk), type_action=type_action
    )


def _deplacement(circuit, jour, heure=9, duree_min=120):
    debut = instant(circuit.programme.lundi_de_semaine, jour, heure)
    return {"debut": debut, "fin": debut + datetime.timedelta(minutes=duree_min)}


@pytest.fixture
def qualifie(circuit):
    qualifier(circuit.cours.instructeur, circuit.cours.element.matiere)
    return circuit


# --- A — modification, suppression, déverrouillage (service) -----------------


def test_a1_deplacement_sur_un_brouillon_est_admis_verrouille_et_journalise(qualifie):
    seance = _seance_libre(qualifie)
    ServiceEcritureSeance.modifier_seance(qualifie.acteurs.planificateur, seance, _deplacement(qualifie, 3))
    seance.refresh_from_db()
    assert seance.debut == instant(qualifie.programme.lundi_de_semaine, 3, 9)
    assert seance.verrouillee is True
    assert _journal_seance(seance, TypeAction.MODIFICATION_ELEMENT_GESTION).exists()


def test_a1_le_journal_detaille_l_ancienne_et_la_nouvelle_valeur(qualifie):
    seance = _seance_libre(qualifie)
    ServiceEcritureSeance.modifier_seance(qualifie.acteurs.planificateur, seance, _deplacement(qualifie, 3))
    entree = _journal_seance(seance, TypeAction.MODIFICATION_ELEMENT_GESTION).get()
    assert "debut :" in entree.detail and "→" in entree.detail


def test_a1_une_modification_sans_changement_est_journalisee_comme_telle(qualifie):
    seance = _seance_libre(qualifie)
    ServiceEcritureSeance.modifier_seance(qualifie.acteurs.planificateur, seance, {"lieu": None})
    entree = _journal_seance(seance, TypeAction.MODIFICATION_ELEMENT_GESTION).get()
    assert entree.detail == "modification : aucun champ modifié"


def test_a2_modification_violant_rg_34_est_refusee_en_la_nommant(qualifie):
    """Un autre cours du même instructeur occupe déjà le créneau visé."""
    seance = _seance_libre(qualifie)
    _seance_libre(qualifie, jour=3, heure=9)
    with pytest.raises(ErreurValidation, match="RG-34"):
        ServiceEcritureSeance.modifier_seance(qualifie.acteurs.planificateur, seance, _deplacement(qualifie, 3))
    seance.refresh_from_db()
    assert seance.debut == instant(qualifie.programme.lundi_de_semaine, 0, 8)


def test_a3_ajout_sur_creneau_libre_est_admis_et_verrouille(qualifie):
    seance = ServiceEcritureSeance.creer_seance(
        qualifie.acteurs.planificateur, qualifie.programme,
        [candidature(qualifie.brigade, qualifie.cours, instant(qualifie.programme.lundi_de_semaine, 4, 9))],
    )
    assert seance.verrouillee is True


def test_a3_ajout_sur_creneau_occupe_est_refuse(qualifie):
    _seance_libre(qualifie)
    with pytest.raises(ErreurValidation):
        ServiceEcritureSeance.creer_seance(
            qualifie.acteurs.planificateur, qualifie.programme,
            [candidature(qualifie.brigade, qualifie.cours, instant(qualifie.programme.lundi_de_semaine, 0, 8))],
        )


def test_a4_suppression_sur_un_brouillon_est_admise_et_journalisee(qualifie):
    seance = _seance_libre(qualifie)
    pk = seance.pk
    ServiceEcritureSeance.supprimer_seance(qualifie.acteurs.planificateur, seance)
    assert not Seance.objects.filter(pk=pk).exists()
    assert not LigneProgramme.objects.filter(seance_id=pk).exists()
    assert _journal_seance(seance, TypeAction.SUPPRESSION_ELEMENT_GESTION).exists()


def test_a5_deverrouillage_puis_regeneration_remplace_la_seance(scenario, qualifie):
    seance = _seance_libre(qualifie)
    ServiceEcritureSeance.deverrouiller_seance(qualifie.acteurs.planificateur, seance)
    seance.refresh_from_db()
    assert seance.verrouillee is False
    ServiceGeneration.generer(scenario.planificateur, scenario.lundi, [qualifie.brigade])
    assert not Seance.objects.filter(pk=seance.pk).exists()


def test_a6_seance_regroupee_sans_confirmation_est_refusee_avec_ses_brigades(qualifie, autre_brigade):
    seance = _seance_libre(qualifie)
    LigneProgramme.objects.create(seance=seance, brigade=autre_brigade)
    with pytest.raises(ErreurValidation, match="Confirmez la modification"):
        ServiceEcritureSeance.modifier_seance(qualifie.acteurs.planificateur, seance, {"lieu": None})
    ServiceEcritureSeance.modifier_seance(
        qualifie.acteurs.planificateur, seance, {"lieu": None}, confirmee=True
    )
    seance.refresh_from_db()
    assert seance.lieu is None


def test_a7_deplacement_vers_une_autre_semaine_est_refuse(qualifie):
    seance = _seance_libre(qualifie)
    with pytest.raises(ErreurValidation, match="Déplacement hors de la semaine"):
        ServiceEcritureSeance.modifier_seance(
            qualifie.acteurs.planificateur, seance,
            {"debut": instant(qualifie.programme.lundi_de_semaine, 9, 9)},
        )


def test_a8_modification_d_une_seance_commencee_est_refusee(qualifie):
    passee = seance_dans(
        qualifie.programme, qualifie.cours, qualifie.brigade,
        timezone.now() - datetime.timedelta(hours=1),
    )
    with pytest.raises(ErreurValidation, match="commencée ne se modifie plus"):
        ServiceEcritureSeance.modifier_seance(qualifie.acteurs.planificateur, passee, {"lieu": None})


def test_a9_bascule_sans_lieu_admise_et_lieu_vide(qualifie):
    seance = _seance_libre(qualifie)
    ServiceEcritureSeance.modifier_seance(qualifie.acteurs.planificateur, seance, {"lieu": None})
    seance.refresh_from_db()
    assert seance.lieu is None


# --- B — états et avenant ----------------------------------------------------


def test_b1_modification_sur_un_soumis_refusee_avec_retirer_la_soumission(qualifie):
    amener_a(EtatProgramme.SOUMIS, qualifie)
    with pytest.raises(TransitionProgrammeRefusee, match="(?i)retirez la soumission"):
        ServiceEcritureSeance.modifier_seance(qualifie.acteurs.planificateur, _seance_seed(qualifie), {"lieu": None})


def test_b2_modification_sur_un_valide_refusee_puis_admise_apres_annulation(qualifie):
    amener_a(EtatProgramme.VALIDE, qualifie)
    seance = _seance_seed(qualifie)
    with pytest.raises(TransitionProgrammeRefusee, match="(?i)annulez la validation"):
        ServiceEcritureSeance.modifier_seance(qualifie.acteurs.planificateur, seance, {"lieu": None})
    ServiceCircuitProgramme.annuler_validation(
        qualifie.acteurs.planificateur, qualifie.programme, "Erreur de créneau.", True
    )
    ServiceEcritureSeance.modifier_seance(qualifie.acteurs.planificateur, seance, {"lieu": None})
    seance.refresh_from_db()
    assert seance.lieu is None


def test_b3_modification_sur_un_affiche_sans_avenant_est_refusee(qualifie):
    amener_a(EtatProgramme.AFFICHE, qualifie)
    with pytest.raises(TransitionProgrammeRefusee, match="(?i)portez un avenant"):
        ServiceEcritureSeance.modifier_seance(qualifie.acteurs.planificateur, _seance_seed(qualifie), {"lieu": None})


def test_b3_avec_avenant_le_programme_reste_affiche_et_l_avenant_est_enregistre(qualifie):
    amener_a(EtatProgramme.AFFICHE, qualifie)
    seance = _seance_seed(qualifie)
    programme = qualifie.programme
    validation = programme.date_validation
    ServiceEcritureSeance.modifier_seance(
        qualifie.acteurs.planificateur, seance, _deplacement(qualifie, 3), avenant=AVENANT
    )
    programme.refresh_from_db()
    assert programme.etat == EtatProgramme.AFFICHE
    assert programme.date_validation == validation
    assert programme.signataire == SIGNATAIRE
    avenant = Avenant.objects.get(seance=seance)
    assert avenant.nature == NatureAvenant.DEPLACEMENT
    assert "debut :" in avenant.detail


def test_b4_avenant_sur_un_brouillon_est_refuse(qualifie):
    seance = _seance_libre(qualifie)
    with pytest.raises(TransitionProgrammeRefusee, match="affiché reçoit un avenant"):
        ServiceEcritureSeance.modifier_seance(
            qualifie.acteurs.planificateur, seance, {"lieu": None}, avenant=AVENANT
        )


def test_b5_suppression_sur_un_affiche_est_refusee_renvoyant_a_la_non_execution(qualifie):
    amener_a(EtatProgramme.AFFICHE, qualifie)
    seance = _seance_seed(qualifie)
    with pytest.raises(ErreurValidation, match="non-exécution"):
        ServiceEcritureSeance.supprimer_seance(qualifie.acteurs.planificateur, seance)
    assert Seance.objects.filter(pk=seance.pk).exists()


def test_b6_rejete_reprise_implicite_puis_modification_journal_dans_cet_ordre(qualifie):
    amener_a(EtatProgramme.REJETE, qualifie)
    seance = _seance_seed(qualifie)
    ServiceEcritureSeance.modifier_seance(qualifie.acteurs.planificateur, seance, {"lieu": None})
    journal = list(
        EntreeJournal.objects.filter(
            objet_identifiant__in=[str(qualifie.programme.pk), str(seance.pk)]
        ).order_by("pk")
    )
    indice_reprise = next(i for i, e in enumerate(journal) if "implicite" in e.detail)
    indice_modification = next(
        i for i, e in enumerate(journal) if e.type_action == TypeAction.MODIFICATION_ELEMENT_GESTION
    )
    assert indice_reprise < indice_modification


# --- C — contraintes en base de l'avenant -----------------------------------


@pytest.mark.django_db
def test_c_avenant_motif_vide_refuse_par_la_base(qualifie):
    seance = _seance_libre(qualifie)
    with pytest.raises(IntegrityError, match="ck_avenant_motif_non_vide"), transaction.atomic():
        Avenant.objects.create(seance=seance, motif="   ", nature=NatureAvenant.DEPLACEMENT)


@pytest.mark.django_db
def test_c_avenant_nature_inconnue_refusee_par_la_base(qualifie):
    seance = _seance_libre(qualifie)
    with pytest.raises(IntegrityError, match="ck_avenant_nature_connue"), transaction.atomic():
        Avenant.objects.create(seance=seance, motif="Motif.", nature="inconnue")


# --- E — prérequis exploités en saisie manuelle (M11) -----------------------


def test_e_prerequis_non_acheve_refuse_une_modification_manuelle(qualifie):
    """La séance passe à un élément dont la matière prérequise n'est pas achevée
    pour cette brigade : RG-39 b) le refuse, comme à la génération."""
    formation = qualifie.cours.element.formation
    matiere_prerequise = Matiere.objects.create(intitule="Bases électroniques", code="BASE1")
    matiere_cible = Matiere.objects.create(intitule="Radiocommunications", code="RAD1")
    element_prerequis = creer_element(formation, matiere_prerequise, volume=4)
    element_cible = creer_element(formation, matiere_cible, volume=10)
    Prerequis.objects.create(element=element_cible, element_prerequis=element_prerequis)
    qualifier(qualifie.cours.instructeur, matiere_cible)
    seance = _seance_libre(qualifie)

    with pytest.raises(ErreurValidation, match="prérequise"):
        ServiceEcritureSeance.modifier_seance(
            qualifie.acteurs.planificateur, seance, {"element_referentiel": element_cible}
        )
    seance.refresh_from_db()
    assert seance.element_referentiel == qualifie.cours.element


def test_a2_volume_programme_compte_les_autres_seances_du_meme_programme(qualifie):
    """RG-39 a) : une modification ne dépasse pas le prescrit à cause d'une autre
    séance du MÊME programme (relecture US-PLAN-05, point 1)."""
    element = qualifie.cours.element
    element.volume_horaire_prescrit = 2
    element.save()
    cours = Cours(element, qualifie.cours.instructeur)
    deux_heures = datetime.timedelta(hours=2)
    premiere = seance_dans(qualifie.programme, cours, qualifie.brigade, instant(qualifie.programme.lundi_de_semaine, 0, 8), 120)
    seconde = seance_dans(qualifie.programme, cours, qualifie.brigade, instant(qualifie.programme.lundi_de_semaine, 2, 8), 120)
    assert premiere.fin - premiere.debut == deux_heures
    with pytest.raises(ErreurValidation, match="RG-39"):
        ServiceEcritureSeance.modifier_seance(
            qualifie.acteurs.planificateur, seconde,
            {"debut": instant(qualifie.programme.lundi_de_semaine, 4, 8), "fin": instant(qualifie.programme.lundi_de_semaine, 4, 10)},
        )
    seconde.refresh_from_db()
    assert seconde.debut == instant(qualifie.programme.lundi_de_semaine, 2, 8)


def test_a9_bascule_sans_lieu_refusee_si_la_matiere_exige_un_lieu(qualifie):
    """Une matière qui exige un lieu ne bascule pas sans lieu : les contraintes
    décident, la bascule n'est jamais admise d'office (M9, D-241)."""
    from referentiel.models import CategorieLieu

    element = qualifie.cours.element
    element.categorie_lieu = CategorieLieu.SALLE_ATTITREE
    element.save()
    seance = _seance_libre(qualifie)
    with pytest.raises(ErreurValidation, match="exige un lieu"):
        ServiceEcritureSeance.modifier_seance(qualifie.acteurs.planificateur, seance, {"lieu": None})
    seance.refresh_from_db()
    assert seance.lieu is None
