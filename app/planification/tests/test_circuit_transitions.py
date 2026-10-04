"""US-VAL-03 — transitions admises, refus et journal (V1 à V6), groupe D
(habilitations). Appels directs au service, sans HTTP (groupe G pour le HTTP).
"""

import datetime

import pytest
from django.utils import timezone

from administration.models import EntreeJournal, TypeAction
from noyau.exceptions import ErreurHabilitation
from planification.exceptions import TransitionProgrammeRefusee
from planification.models import EtatProgramme, ProgrammeHebdomadaire
from planification.services.circuit import ServiceCircuitProgramme
from planification.tests.aide_circuit import (
    MOTIF_ANNULATION,
    MOTIF_REJET,
    SIGNATAIRE,
    amener_a,
    seance_dans,
)
from planification.tests.conftest import instant


def _journal_du_programme(programme):
    return EntreeJournal.objects.filter(
        objet_type="programme", objet_identifiant=str(programme.pk)
    ).order_by("pk")


def test_soumettre_passe_a_soumis_et_journalise_la_transition(circuit):
    programme, acteurs = circuit.programme, circuit.acteurs
    seance_dans(
        programme, circuit.cours, circuit.brigade, instant(programme.lundi_de_semaine, 0, 8)
    )

    ServiceCircuitProgramme.soumettre(acteurs.planificateur, programme)

    programme.refresh_from_db()
    assert programme.etat == EtatProgramme.SOUMIS
    assert programme.date_soumission is not None
    entree = _journal_du_programme(programme).get(type_action=TypeAction.TRANSITION_PROGRAMME)
    assert entree.valeur_avant == {"etat": "brouillon"}
    assert entree.valeur_apres == {"etat": "soumis"}
    assert entree.auteur == acteurs.planificateur
    assert entree.detail == "T2"


def test_soumettre_un_programme_sans_seance_est_refuse_avec_la_regle(circuit):
    programme, acteurs = circuit.programme, circuit.acteurs

    with pytest.raises(TransitionProgrammeRefusee, match="générez-le avant de le soumettre"):
        ServiceCircuitProgramme.soumettre(acteurs.planificateur, programme)

    programme.refresh_from_db()
    assert programme.etat == EtatProgramme.BROUILLON


def test_retirer_la_soumission_repasse_a_brouillon_et_efface_la_date(circuit):
    programme, acteurs = circuit.programme, circuit.acteurs
    amener_a(EtatProgramme.SOUMIS, circuit)

    ServiceCircuitProgramme.retirer_soumission(acteurs.planificateur, programme)

    programme.refresh_from_db()
    assert programme.etat == EtatProgramme.BROUILLON
    assert programme.date_soumission is None


def test_valider_un_soumis_journalise_la_nature_de_rg_26(circuit):
    programme, acteurs = circuit.programme, circuit.acteurs
    amener_a(EtatProgramme.SOUMIS, circuit)

    ServiceCircuitProgramme.valider(acteurs.pedagogique, programme)

    programme.refresh_from_db()
    assert programme.etat == EtatProgramme.VALIDE
    assert programme.valide_par == acteurs.pedagogique
    assert programme.date_validation is not None
    assert (
        _journal_du_programme(programme)
        .filter(type_action=TypeAction.VALIDATION_PROGRAMME)
        .exists()
    )


def test_rejeter_sans_motif_est_refuse_sans_changer_l_etat(circuit):
    programme, acteurs = circuit.programme, circuit.acteurs
    amener_a(EtatProgramme.SOUMIS, circuit)

    for motif_vide in ("", "   "):
        with pytest.raises(TransitionProgrammeRefusee, match="exige un motif"):
            ServiceCircuitProgramme.rejeter(acteurs.pedagogique, programme, motif_vide)

    programme.refresh_from_db()
    assert programme.etat == EtatProgramme.SOUMIS


def test_rejeter_avec_motif_passe_a_rejete_et_garde_le_motif(circuit):
    programme, acteurs = circuit.programme, circuit.acteurs
    amener_a(EtatProgramme.SOUMIS, circuit)

    ServiceCircuitProgramme.rejeter(acteurs.pedagogique, programme, f"  {MOTIF_REJET}  ")

    programme.refresh_from_db()
    assert programme.etat == EtatProgramme.REJETE
    assert programme.motif_rejet == MOTIF_REJET
    assert _journal_du_programme(programme).filter(type_action=TypeAction.REJET_PROGRAMME).exists()


def test_reprendre_un_rejete_repasse_a_brouillon_et_efface_le_circuit(circuit):
    programme, acteurs = circuit.programme, circuit.acteurs
    amener_a(EtatProgramme.REJETE, circuit)

    ServiceCircuitProgramme.reprendre(acteurs.planificateur, programme)

    programme.refresh_from_db()
    assert programme.etat == EtatProgramme.BROUILLON
    assert programme.motif_rejet is None
    assert programme.date_soumission is None
    entree = _journal_du_programme(programme).get(detail__startswith="T6")
    assert "reprise explicite" in entree.detail


def test_enregistrer_la_signature_garde_l_etat_valide(circuit):
    programme, acteurs = circuit.programme, circuit.acteurs
    amener_a(EtatProgramme.VALIDE, circuit)
    aujourd_hui = timezone.localdate()

    ServiceCircuitProgramme.enregistrer_signature(
        acteurs.planificateur, programme, aujourd_hui, SIGNATAIRE
    )

    programme.refresh_from_db()
    assert programme.etat == EtatProgramme.VALIDE
    assert programme.date_signature == aujourd_hui
    assert programme.signataire == SIGNATAIRE


def test_signature_anterieure_a_la_validation_est_refusee(circuit):
    programme, acteurs = circuit.programme, circuit.acteurs
    amener_a(EtatProgramme.VALIDE, circuit)
    avant = timezone.localdate(programme.date_validation) - datetime.timedelta(days=1)

    with pytest.raises(TransitionProgrammeRefusee, match="précéder la validation"):
        ServiceCircuitProgramme.enregistrer_signature(
            acteurs.planificateur, programme, avant, SIGNATAIRE
        )


def test_signature_sans_date_est_refusee_sans_erreur_technique(circuit):
    programme, acteurs = circuit.programme, circuit.acteurs
    amener_a(EtatProgramme.VALIDE, circuit)

    with pytest.raises(TransitionProgrammeRefusee, match="exige une date"):
        ServiceCircuitProgramme.enregistrer_signature(
            acteurs.planificateur, programme, None, SIGNATAIRE
        )


def test_signature_future_ou_sans_signataire_est_refusee(circuit):
    programme, acteurs = circuit.programme, circuit.acteurs
    amener_a(EtatProgramme.VALIDE, circuit)
    demain = timezone.localdate() + datetime.timedelta(days=1)

    with pytest.raises(TransitionProgrammeRefusee, match="postérieure à aujourd'hui"):
        ServiceCircuitProgramme.enregistrer_signature(
            acteurs.planificateur, programme, demain, SIGNATAIRE
        )
    with pytest.raises(TransitionProgrammeRefusee, match="nom du signataire"):
        ServiceCircuitProgramme.enregistrer_signature(
            acteurs.planificateur, programme, timezone.localdate(), "  "
        )


def test_afficher_sans_signature_est_refuse_rg_46(circuit):
    programme, acteurs = circuit.programme, circuit.acteurs
    amener_a(EtatProgramme.VALIDE, circuit)

    with pytest.raises(TransitionProgrammeRefusee, match="RG-46"):
        ServiceCircuitProgramme.afficher(acteurs.planificateur, programme)

    programme.refresh_from_db()
    assert programme.etat == EtatProgramme.VALIDE


def test_afficher_un_programme_signe_passe_a_affiche(circuit):
    programme = circuit.programme
    amener_a(EtatProgramme.AFFICHE, circuit)

    programme.refresh_from_db()
    assert programme.etat == EtatProgramme.AFFICHE
    assert programme.date_affichage is not None


def test_annuler_la_validation_exige_confirmation_et_motif(circuit):
    programme, acteurs = circuit.programme, circuit.acteurs
    amener_a(EtatProgramme.VALIDE, circuit)

    with pytest.raises(TransitionProgrammeRefusee, match="confirmation et un motif"):
        ServiceCircuitProgramme.annuler_validation(
            acteurs.planificateur, programme, MOTIF_ANNULATION, False
        )
    with pytest.raises(TransitionProgrammeRefusee, match="confirmation et un motif"):
        ServiceCircuitProgramme.annuler_validation(acteurs.planificateur, programme, " ", True)


def test_annuler_la_validation_repasse_a_brouillon_et_efface_la_signature(circuit):
    programme, acteurs = circuit.programme, circuit.acteurs
    amener_a(EtatProgramme.VALIDE, circuit)
    ServiceCircuitProgramme.enregistrer_signature(
        acteurs.planificateur, programme, timezone.localdate(), SIGNATAIRE
    )

    ServiceCircuitProgramme.annuler_validation(
        acteurs.planificateur, programme, MOTIF_ANNULATION, True
    )

    programme.refresh_from_db()
    assert programme.etat == EtatProgramme.BROUILLON
    assert programme.date_validation is None
    assert programme.date_signature is None
    assert programme.signataire is None


def test_porter_un_avenant_sur_un_affiche_reste_affiche_et_journalise(circuit):
    programme, acteurs = circuit.programme, circuit.acteurs
    amener_a(EtatProgramme.AFFICHE, circuit)

    ServiceCircuitProgramme.porter_avenant(
        acteurs.planificateur, programme, "Changement de créneau.", "Modification mineure"
    )

    programme.refresh_from_db()
    assert programme.etat == EtatProgramme.AFFICHE
    assert _journal_du_programme(programme).filter(detail__startswith="T10").exists()


def test_porter_un_avenant_sans_motif_ou_sans_nature_est_refuse(circuit):
    programme, acteurs = circuit.programme, circuit.acteurs
    amener_a(EtatProgramme.AFFICHE, circuit)

    with pytest.raises(TransitionProgrammeRefusee, match="motif et sa nature"):
        ServiceCircuitProgramme.porter_avenant(acteurs.planificateur, programme, "motif", "")


# --- D — habilitations : chaque transition refusée aux profils non autorisés ---

PROFILS_HORS_PLANIFICATION = ["redacteur", "direction_formation", "examens"]
PROFILS_HORS_PEDAGOGIQUE = ["planificateur", "direction_formation", "examens"]


@pytest.mark.parametrize("profil", PROFILS_HORS_PLANIFICATION)
@pytest.mark.parametrize("methode", ["soumettre", "retirer_soumission", "reprendre"])
def test_d_transitions_de_planification_refusees_hors_planification(
    profil, methode, programme, request
):
    agissant = request.getfixturevalue(profil)

    with pytest.raises(ErreurHabilitation):
        getattr(ServiceCircuitProgramme, methode)(agissant, programme)


@pytest.mark.parametrize("profil", PROFILS_HORS_PLANIFICATION)
def test_d_signature_et_affichage_refusees_hors_planification(profil, programme, request):
    agissant = request.getfixturevalue(profil)

    with pytest.raises(ErreurHabilitation):
        ServiceCircuitProgramme.enregistrer_signature(
            agissant, programme, timezone.localdate(), SIGNATAIRE
        )
    with pytest.raises(ErreurHabilitation):
        ServiceCircuitProgramme.afficher(agissant, programme)


@pytest.mark.parametrize("profil", PROFILS_HORS_PEDAGOGIQUE)
def test_d_valider_et_rejeter_refusees_hors_cellule_pedagogique(profil, programme, request):
    agissant = request.getfixturevalue(profil)

    with pytest.raises(ErreurHabilitation):
        ServiceCircuitProgramme.valider(agissant, programme)
    with pytest.raises(ErreurHabilitation):
        ServiceCircuitProgramme.rejeter(agissant, programme, MOTIF_REJET)


def test_d_la_transition_refusee_pour_habilitation_ne_touche_pas_l_etat(circuit):
    programme, acteurs = circuit.programme, circuit.acteurs
    amener_a(EtatProgramme.SOUMIS, circuit)

    with pytest.raises(ErreurHabilitation):
        ServiceCircuitProgramme.valider(acteurs.planificateur, programme)

    assert ProgrammeHebdomadaire.objects.get(pk=programme.pk).etat == EtatProgramme.SOUMIS
