"""US-SUI-05 — déclaration de non-exécution d'une séance (prompt 44, Temps 2).
Données entièrement fictives.

Le volume retranché du réalisé (C3) est vérifié par le calcul du
rapprochement lui-même, à l'US-SUI-01 (Temps 3, même prompt) : la définition
du réalisé y exclut par construction toute ligne portant une non-exécution,
rien à tester deux fois.
"""

import datetime

import pytest
from django.db import IntegrityError, transaction
from django.utils import timezone

from noyau.exceptions import ErreurHabilitation, ErreurValidation
from planification.models import EtatProgramme, NonExecution
from planification.services.suivi import ServiceSuivi
from planification.tests.aide_circuit import amener_a, seance_dans
from planification.tests.conftest import instant

MOTIF = "Instructeur absent sans déclaration préalable (essai)."
LUNDI_PASSE = datetime.date(2020, 1, 6)


def _ligne_passee(programme, circuit, brigade=None):
    seance = seance_dans(
        programme, circuit.cours, brigade or circuit.brigade, instant(LUNDI_PASSE, 0, 8)
    )
    return seance.lignes.get()


def _ligne_future(programme):
    """La séance posée par `amener_a` elle-même — toujours dans le futur
    (`lundi_semaine`, voir conftest.py)."""
    return programme.seances.get().lignes.get()


# --- base : contraintes en base de NonExecution -----------------------------


def test_base_doublon_sur_une_ligne_refuse_par_la_base(circuit):
    affiche = amener_a(EtatProgramme.AFFICHE, circuit)
    ligne = _ligne_passee(affiche, circuit)
    NonExecution.objects.create(ligne=ligne, motif=MOTIF)

    with pytest.raises(IntegrityError, match="non_execution_ligne_id_key"), transaction.atomic():
        NonExecution.objects.create(ligne=ligne, motif="Un autre motif (essai).")


def test_base_motif_blanc_refuse_par_la_base(circuit):
    affiche = amener_a(EtatProgramme.AFFICHE, circuit)
    ligne = _ligne_passee(affiche, circuit)

    with (
        pytest.raises(IntegrityError, match="ck_non_execution_motif_non_vide"),
        transaction.atomic(),
    ):
        NonExecution.objects.create(ligne=ligne, motif="   ")


# --- service : C1 à C5 -------------------------------------------------------


def test_c1_seance_future_refusee(circuit):
    affiche = amener_a(EtatProgramme.AFFICHE, circuit)
    ligne = _ligne_future(affiche)

    with pytest.raises(ErreurValidation, match="pas encore eu lieu"):
        ServiceSuivi.declarer_non_execution(circuit.acteurs.planificateur, ligne, MOTIF)


def test_c2_programme_non_affiche_refuse(circuit):
    ligne = _ligne_passee(circuit.programme, circuit)

    with pytest.raises(ErreurValidation, match="RG-60"):
        ServiceSuivi.declarer_non_execution(circuit.acteurs.planificateur, ligne, MOTIF)


def test_c2_motif_obligatoire(circuit):
    affiche = amener_a(EtatProgramme.AFFICHE, circuit)
    ligne = _ligne_passee(affiche, circuit)

    with pytest.raises(ErreurValidation, match="obligatoire"):
        ServiceSuivi.declarer_non_execution(circuit.acteurs.planificateur, ligne, "   ")


def test_c1_regroupee_une_seule_brigade_declaree(circuit, autre_brigade_formation):
    affiche = amener_a(EtatProgramme.AFFICHE, circuit)
    seance_regroupee = seance_dans(
        affiche, circuit.cours, circuit.brigade, instant(LUNDI_PASSE, 0, 8)
    )
    from planification.models import LigneProgramme

    LigneProgramme.objects.create(seance=seance_regroupee, brigade=autre_brigade_formation)
    ligne_brigade_1, ligne_brigade_2 = seance_regroupee.lignes.order_by("pk")

    ServiceSuivi.declarer_non_execution(circuit.acteurs.planificateur, ligne_brigade_1, MOTIF)

    ligne_brigade_1.refresh_from_db()
    ligne_brigade_2.refresh_from_db()
    assert hasattr(ligne_brigade_1, "non_execution")
    with pytest.raises(NonExecution.DoesNotExist):
        _ = ligne_brigade_2.non_execution


def test_c4_annulation_reversible(circuit):
    affiche = amener_a(EtatProgramme.AFFICHE, circuit)
    ligne = _ligne_passee(affiche, circuit)
    ServiceSuivi.declarer_non_execution(circuit.acteurs.planificateur, ligne, MOTIF)

    ServiceSuivi.annuler_non_execution(circuit.acteurs.planificateur, ligne)

    assert not NonExecution.objects.filter(ligne=ligne).exists()


def test_c4_annulation_sans_declaration_refusee(circuit):
    affiche = amener_a(EtatProgramme.AFFICHE, circuit)
    ligne = _ligne_passee(affiche, circuit)

    with pytest.raises(ErreurValidation, match="aucune non-exécution"):
        ServiceSuivi.annuler_non_execution(circuit.acteurs.planificateur, ligne)


def test_c5_journalisee_avec_auteur_et_horodatage(circuit):
    affiche = amener_a(EtatProgramme.AFFICHE, circuit)
    ligne = _ligne_passee(affiche, circuit)
    avant = timezone.now()

    ServiceSuivi.declarer_non_execution(circuit.acteurs.planificateur, ligne, MOTIF)

    non_execution = NonExecution.objects.get(ligne=ligne)
    assert non_execution.cree_par == circuit.acteurs.planificateur
    assert non_execution.cree_le >= avant


# --- habilitations : C6, seule la planification écrit -----------------------


@pytest.mark.parametrize("profil", ["pedagogique", "examens", "direction_formation"])
def test_c6_habilitation_refusee_en_service(circuit, profil, direction_formation):
    affiche = amener_a(EtatProgramme.AFFICHE, circuit)
    ligne = _ligne_passee(affiche, circuit)
    acteur = {
        "pedagogique": circuit.acteurs.pedagogique,
        "examens": circuit.acteurs.examens,
        "direction_formation": direction_formation,
    }[profil]

    with pytest.raises(ErreurHabilitation):
        ServiceSuivi.declarer_non_execution(acteur, ligne, MOTIF)
