"""US-SUI-01 — rapprochement prescrit/programmé/réalisé (prompt 44, Temps 3).
Données entièrement fictives.
"""

import datetime

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.utils import timezone

from noyau.exceptions import ErreurHabilitation
from organisation.services.brigade import ServiceBrigade
from organisation.tests.conftest import donnees_brigade
from planification.models import NonExecution, ProgrammeHebdomadaire
from planification.services.circuit import ServiceCircuitProgramme
from planification.services.suivi import ServiceSuivi
from planification.tests.aide_circuit import seance_dans
from planification.tests.conftest import instant

SIGNATAIRE_ESSAI = "Signataire essai rapprochement"


def _amener_a_affiche(programme, acteurs):
    ServiceCircuitProgramme.soumettre(acteurs.planificateur, programme)
    ServiceCircuitProgramme.valider(acteurs.pedagogique, programme)
    ServiceCircuitProgramme.enregistrer_signature(
        acteurs.planificateur, programme, timezone.localdate(), SIGNATAIRE_ESSAI
    )
    ServiceCircuitProgramme.afficher(acteurs.planificateur, programme)


def _programme_passe(decalage_semaines=4):
    lundi = datetime.date.today() - datetime.timedelta(weeks=decalage_semaines)
    lundi -= datetime.timedelta(days=lundi.weekday())
    return ProgrammeHebdomadaire.objects.create(lundi_de_semaine=lundi)


def _groupe(groupes, brigade):
    return next(g for g in groupes if g.brigade.pk == brigade.pk)


def _ligne(groupe, element):
    return next(ligne for ligne in groupe.lignes if ligne.element_referentiel.pk == element.pk)


# --- C1/C2/C3 — trois volumes, écart --------------------------------------


def test_c1_c3_prescrit_programme_realise_et_ecart(circuit, direction_formation):
    passe = _programme_passe()
    seance_dans(passe, circuit.cours, circuit.brigade, instant(passe.lundi_de_semaine, 0, 8))
    _amener_a_affiche(passe, circuit.acteurs)
    # Séance future (programme non affiché) : compte au programmé, pas au réalisé (R4/R1).
    seance_dans(
        circuit.programme,
        circuit.cours,
        circuit.brigade,
        instant(circuit.programme.lundi_de_semaine, 0, 8),
    )

    groupes = ServiceSuivi.rapprochement(direction_formation)

    ligne = _ligne(_groupe(groupes, circuit.brigade), circuit.cours.element)
    assert ligne.prescrit == circuit.cours.element.volume_horaire_prescrit
    assert ligne.programme == 4.0  # deux séances de deux heures
    assert ligne.realise == 2.0  # une seule affichée et passée
    assert ligne.ecart_heures == ligne.prescrit - 2.0
    assert ligne.ecart_pourcent == pytest.approx((ligne.ecart_heures / ligne.prescrit) * 100)


def test_c2_non_execution_retranchee_du_realise(circuit, direction_formation):
    passe = _programme_passe()
    seance = seance_dans(
        passe, circuit.cours, circuit.brigade, instant(passe.lundi_de_semaine, 0, 8)
    )
    _amener_a_affiche(passe, circuit.acteurs)
    NonExecution.objects.create(ligne=seance.lignes.get(), motif="Essai rapprochement.")

    groupes = ServiceSuivi.rapprochement(direction_formation)

    ligne = _ligne(_groupe(groupes, circuit.brigade), circuit.cours.element)
    assert ligne.realise == 0.0
    assert ligne.programme == 2.0


# --- R4 — programmé, tous états confondus, rejeté compris -------------------


def test_r4_programme_compte_un_programme_rejete(circuit, direction_formation):
    """Le programmé compte le rejeté (R4) — brigade par ailleurs affichée
    sur une AUTRE matière, pour isoler ce point de l'E1/R5 (ci-dessous),
    sans quoi la brigade entière serait masquée avant d'en mesurer les
    volumes."""
    from planification.tests.conftest import Cours, creer_element, qualifier
    from referentiel.models import Matiere

    autre_matiere = Matiere.objects.create(intitule="Autre matière (essai R4)", code="RAP-R4")
    autre_element = creer_element(circuit.cours.element.formation, autre_matiere)
    qualifier(circuit.cours.instructeur, autre_matiere)
    affiche = _programme_passe(decalage_semaines=6)
    seance_dans(
        affiche,
        Cours(autre_element, circuit.cours.instructeur),
        circuit.brigade,
        instant(affiche.lundi_de_semaine, 0, 8),
    )
    _amener_a_affiche(affiche, circuit.acteurs)

    rejete = _programme_passe(decalage_semaines=4)
    seance_dans(rejete, circuit.cours, circuit.brigade, instant(rejete.lundi_de_semaine, 0, 8))
    ServiceCircuitProgramme.soumettre(circuit.acteurs.planificateur, rejete)
    ServiceCircuitProgramme.rejeter(circuit.acteurs.pedagogique, rejete, "Motif essai.")

    groupes = ServiceSuivi.rapprochement(direction_formation)

    groupe = _groupe(groupes, circuit.brigade)
    assert groupe.sans_programme_affiche is False
    ligne = _ligne(groupe, circuit.cours.element)
    assert ligne.programme == 2.0
    assert ligne.realise == 0.0
    assert ligne.realise == 0.0


# --- R5/E1 — brigade sans aucun programme affiché ---------------------------


def test_r5_e1_brigade_sans_programme_affiche_signalee_separement(circuit, direction_formation):
    groupes = ServiceSuivi.rapprochement(direction_formation)

    groupe = _groupe(groupes, circuit.brigade)
    assert groupe.sans_programme_affiche is True
    assert groupe.lignes == []


# --- Filtres ------------------------------------------------------------


def test_filtre_brigade_restreint_le_resultat(
    circuit, direction_formation, redacteur, session_formation
):
    autre_brigade = ServiceBrigade.creer(
        redacteur, session_formation, donnees_brigade(designation="RAP2")
    )

    groupes = ServiceSuivi.rapprochement(direction_formation, brigade_id=circuit.brigade.pk)

    assert {g.brigade.pk for g in groupes} == {circuit.brigade.pk}
    assert autre_brigade.pk not in {g.brigade.pk for g in groupes}


def test_filtre_periode_change_la_date_de_reference_du_realise(circuit, direction_formation):
    passe = _programme_passe(decalage_semaines=8)
    seance_dans(passe, circuit.cours, circuit.brigade, instant(passe.lundi_de_semaine, 0, 8))
    _amener_a_affiche(passe, circuit.acteurs)
    avant_la_seance = timezone.make_aware(
        datetime.datetime.combine(
            passe.lundi_de_semaine - datetime.timedelta(days=1), datetime.time.max
        )
    )

    groupes = ServiceSuivi.rapprochement(direction_formation, periode_fin=avant_la_seance)

    groupe = _groupe(groupes, circuit.brigade)
    assert groupe.sans_programme_affiche is True


# --- R7 — requêtes constantes ------------------------------------------------


def test_r7_requetes_constantes_avec_deux_et_dix_brigades(
    circuit, redacteur, session_formation, direction_formation
):
    """R7, littéralement : deux brigades et une matière à la première
    mesure, dix brigades et deux matières à la seconde — les deux axes que
    la propriété annonce, pas seulement les brigades."""
    from planification.tests.conftest import creer_element
    from referentiel.models import Matiere

    ServiceBrigade.creer(redacteur, session_formation, donnees_brigade(designation="RAP-DEUX"))
    # Chauffe : la première vérification d'habilitation d'un utilisateur
    # charge et met en cache ses permissions (deux requêtes, une fois pour
    # tout l'objet) — sans elle, la première mesure porterait à tort deux
    # requêtes de plus, sans rapport avec le nombre de brigades (même
    # leçon que P-39, `docs/suivi/PROBLEMES.md`).
    ServiceSuivi.rapprochement(direction_formation)

    with CaptureQueriesContext(connection) as deux:
        ServiceSuivi.rapprochement(direction_formation)
    for i in range(8):
        ServiceBrigade.creer(redacteur, session_formation, donnees_brigade(designation=f"RAP{i}"))
    autre_matiere = Matiere.objects.create(intitule="Seconde matière (essai R7)", code="RAP-R7")
    creer_element(circuit.cours.element.formation, autre_matiere)

    with CaptureQueriesContext(connection) as dix:
        ServiceSuivi.rapprochement(direction_formation)

    assert len(deux.captured_queries) == len(dix.captured_queries)


# --- C5 — habilitations -------------------------------------------------


@pytest.mark.parametrize("profil", ["planificateur", "examens"])
def test_c5_habilitation_refusee_en_service(circuit, profil):
    """C5 : refusés — planification et examens. La pédagogique et la
    Direction sont autorisées (voir les deux tests suivants)."""
    acteur = {
        "planificateur": circuit.acteurs.planificateur,
        "examens": circuit.acteurs.examens,
    }[profil]

    with pytest.raises(ErreurHabilitation):
        ServiceSuivi.rapprochement(acteur)


def test_c5_direction_de_formation_autorisee(circuit, direction_formation):
    ServiceSuivi.rapprochement(direction_formation)


def test_c5_cellule_pedagogique_autorisee(circuit):
    ServiceSuivi.rapprochement(circuit.acteurs.pedagogique)
