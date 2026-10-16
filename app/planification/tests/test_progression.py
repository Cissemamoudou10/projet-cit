"""US-SUI-06 — progression réalisée hebdomadaire (prompt 45, Temps 2).
Calcul, modèle et service — rien ici ne produit de PDF (voir
`test_progression_pdf.py`). Données entièrement fictives.
"""

import datetime

import pytest
from django.db import IntegrityError, transaction
from django.utils import timezone

from noyau.exceptions import ErreurHabilitation, ErreurValidation
from planification.models import (
    Avenant,
    EditionProgression,
    NatureAvenant,
    NonExecution,
    ProgrammeHebdomadaire,
)
from planification.selectors_progression import progression_realisee
from planification.services.circuit import ServiceCircuitProgramme
from planification.services.suivi import ServiceSuivi
from planification.tests.aide_circuit import seance_dans
from planification.tests.conftest import instant

SIGNATAIRE_ESSAI = "Signataire essai progression"
LUNDI_FIXE = datetime.date(2024, 1, 1)  # un lundi, fixe — indépendant de la date du jour (P-43)


def _amener_a_affiche(programme, acteurs):
    """Chaque transition verrouille et relit SA PROPRE copie fraîche du
    programme (`circuit.py::_verrouiller`) ; sans ce `refresh_from_db` final,
    l'objet Python tenu par l'appelant resterait figé à « brouillon » — même
    piège que celui qu'`aide_circuit.amener_a` évite déjà pour les tests du
    circuit lui-même."""
    ServiceCircuitProgramme.soumettre(acteurs.planificateur, programme)
    ServiceCircuitProgramme.valider(acteurs.pedagogique, programme)
    ServiceCircuitProgramme.enregistrer_signature(
        acteurs.planificateur, programme, timezone.localdate(), SIGNATAIRE_ESSAI
    )
    ServiceCircuitProgramme.afficher(acteurs.planificateur, programme)
    programme.refresh_from_db()


def _programme_fixe():
    return ProgrammeHebdomadaire.objects.create(lundi_de_semaine=LUNDI_FIXE)


def _instant_mercredi():
    """T explicite, au milieu de la semaine fixe — jamais `timezone.now()`."""
    return instant(LUNDI_FIXE, 2, 12)  # mercredi midi


def _groupe_unique(groupes):
    (lignes_brigades,) = groupes.values()
    (groupe,) = lignes_brigades
    return groupe


# --- C1 — programmé de la semaine et dispensé -------------------------------


def test_c1_programme_semaine_et_dispense_par_brigade_et_matiere(circuit):
    programme = _programme_fixe()
    seance_dans(programme, circuit.cours, circuit.brigade, instant(LUNDI_FIXE, 0, 8))  # lundi
    _amener_a_affiche(programme, circuit.acteurs)

    groupes = progression_realisee(programme, instant_edition=_instant_mercredi())

    groupe = _groupe_unique(groupes)
    (ligne,) = groupe.lignes
    assert ligne.element_referentiel.pk == circuit.cours.element.pk
    assert ligne.programme_semaine == 2.0
    assert ligne.dispense == 2.0


def test_c1_seance_a_venir_non_comptee_au_dispense(circuit):
    """La séance du jeudi n'a pas encore eu lieu à l'instant de l'édition
    (mercredi midi) : comptée au programmé, pas au dispensé."""
    programme = _programme_fixe()
    seance_dans(programme, circuit.cours, circuit.brigade, instant(LUNDI_FIXE, 3, 8))  # jeudi
    _amener_a_affiche(programme, circuit.acteurs)

    groupes = progression_realisee(programme, instant_edition=_instant_mercredi())

    groupe = _groupe_unique(groupes)
    (ligne,) = groupe.lignes
    assert ligne.programme_semaine == 2.0
    assert ligne.dispense == 0.0


def test_c1_regroupee_comptee_pour_chaque_brigade(circuit, autre_brigade_formation):
    programme = _programme_fixe()
    seance = seance_dans(programme, circuit.cours, circuit.brigade, instant(LUNDI_FIXE, 0, 8))
    from planification.models import LigneProgramme

    LigneProgramme.objects.create(seance=seance, brigade=autre_brigade_formation)
    _amener_a_affiche(programme, circuit.acteurs)

    groupes = progression_realisee(programme, instant_edition=_instant_mercredi())

    toutes_lignes = [groupe for lignes in groupes.values() for groupe in lignes]
    assert len(toutes_lignes) == 2
    for groupe in toutes_lignes:
        (ligne,) = groupe.lignes
        assert ligne.dispense == 2.0


# --- C2/C3 — écarts : non-exécution, avenant, déplacement compté -----------


def test_c2_non_execution_listee_avec_motif_et_retranchee(circuit):
    programme = _programme_fixe()
    seance = seance_dans(programme, circuit.cours, circuit.brigade, instant(LUNDI_FIXE, 0, 8))
    _amener_a_affiche(programme, circuit.acteurs)
    NonExecution.objects.create(ligne=seance.lignes.get(), motif="Instructeur absent (essai).")

    groupes = progression_realisee(programme, instant_edition=_instant_mercredi())

    groupe = _groupe_unique(groupes)
    (ligne,) = groupe.lignes
    assert ligne.dispense == 0.0
    (ecart,) = groupe.ecarts
    assert ecart.libelle == "Non-exécution"
    assert ecart.motif == "Instructeur absent (essai)."


def test_c2_avenant_liste_avec_nature_et_motif(circuit):
    programme = _programme_fixe()
    seance = seance_dans(programme, circuit.cours, circuit.brigade, instant(LUNDI_FIXE, 0, 8))
    _amener_a_affiche(programme, circuit.acteurs)
    Avenant.objects.create(
        seance=seance, motif="Salle indisponible (essai).", nature=NatureAvenant.CHANGEMENT_LIEU
    )

    groupes = progression_realisee(programme, instant_edition=_instant_mercredi())

    groupe = _groupe_unique(groupes)
    (ecart,) = groupe.ecarts
    assert ecart.libelle == "Changement de lieu"
    assert ecart.motif == "Salle indisponible (essai)."


def test_c3_deplacement_dans_la_semaine_compte_au_dispense(circuit):
    """P3 : une séance « reportée » dans la semaine porte un avenant de
    nature déplacement — son volume compte au dispensé si elle a eu lieu."""
    programme = _programme_fixe()
    seance = seance_dans(programme, circuit.cours, circuit.brigade, instant(LUNDI_FIXE, 0, 8))
    _amener_a_affiche(programme, circuit.acteurs)
    Avenant.objects.create(
        seance=seance, motif="Créneau échangé (essai).", nature=NatureAvenant.DEPLACEMENT
    )

    groupes = progression_realisee(programme, instant_edition=_instant_mercredi())

    groupe = _groupe_unique(groupes)
    (ligne,) = groupe.lignes
    assert ligne.dispense == 2.0  # inchangé : la séance a bien eu lieu
    (ecart,) = groupe.ecarts
    assert ecart.libelle == "Déplacement"


# --- base : signature ----------------------------------------------------


def test_base_signature_incomplete_refusee_par_la_base(db):
    programme = _programme_fixe()
    with (
        pytest.raises(IntegrityError, match="ck_edition_progression_signature_complete"),
        transaction.atomic(),
    ):
        EditionProgression.objects.create(programme=programme, signataire="Quelqu'un")


def test_base_date_signature_seule_refusee_par_la_base(db):
    programme = _programme_fixe()
    with (
        pytest.raises(IntegrityError, match="ck_edition_progression_signature_complete"),
        transaction.atomic(),
    ):
        EditionProgression.objects.create(programme=programme, date_signature=timezone.localdate())


# --- service : P1, P4, C5 ----------------------------------------------------


def test_p4_edition_refusee_hors_programme_affiche(circuit):
    with pytest.raises(ErreurValidation, match="RG-60"):
        ServiceSuivi.editer_progression(circuit.acteurs.planificateur, circuit.programme)


def test_p1_deux_editions_conservees_la_plus_recente_fait_foi(circuit):
    programme = _programme_fixe()
    seance_dans(programme, circuit.cours, circuit.brigade, instant(LUNDI_FIXE, 0, 8))
    _amener_a_affiche(programme, circuit.acteurs)

    premiere = ServiceSuivi.editer_progression(circuit.acteurs.planificateur, programme)
    seconde = ServiceSuivi.editer_progression(circuit.acteurs.planificateur, programme)

    assert EditionProgression.objects.filter(programme=programme).count() == 2
    assert premiere.pk != seconde.pk
    assert ServiceSuivi.derniere_edition(programme).pk == seconde.pk


def test_signature_date_future_refusee(circuit):
    programme = _programme_fixe()
    seance_dans(programme, circuit.cours, circuit.brigade, instant(LUNDI_FIXE, 0, 8))
    _amener_a_affiche(programme, circuit.acteurs)
    edition = ServiceSuivi.editer_progression(circuit.acteurs.planificateur, programme)
    demain = timezone.localdate() + datetime.timedelta(days=1)

    with pytest.raises(ErreurValidation, match="postérieure"):
        ServiceSuivi.enregistrer_signature_progression(
            circuit.acteurs.planificateur, edition, demain, SIGNATAIRE_ESSAI
        )


@pytest.mark.parametrize("profil", ["pedagogique", "examens"])
def test_c5_edition_refusee_hors_planification(circuit, profil):
    acteur = {
        "pedagogique": circuit.acteurs.pedagogique,
        "examens": circuit.acteurs.examens,
    }[profil]
    programme = _programme_fixe()
    seance_dans(programme, circuit.cours, circuit.brigade, instant(LUNDI_FIXE, 0, 8))
    _amener_a_affiche(programme, circuit.acteurs)

    with pytest.raises(ErreurHabilitation):
        ServiceSuivi.editer_progression(acteur, programme)
