"""US-SUI-03 — Consulter le tableau de bord des formations (prompt 48,
Story 2). Données entièrement fictives.
"""

import datetime

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from organisation.services.brigade import ServiceBrigade
from organisation.services.cloture import ServiceClotureSession
from organisation.tests.conftest import donnees_brigade
from planification.models import LigneProgramme, ProgrammeHebdomadaire
from planification.selectors_tableau_bord import tableau_de_bord
from planification.services.circuit import ServiceCircuitProgramme
from planification.services.suivi import ServiceSuivi
from planification.tests.aide_circuit import seance_dans
from planification.tests.conftest import Cours, creer_element, instant, qualifier
from referentiel.models import Matiere

SIGNATAIRE_ESSAI = "Signataire essai tableau de bord"
MOTIF_ESSAI = "Motif essai tableau de bord."


def _mettre_en_cours(brigade):
    """B1 : session non clôturée dont la période couvre la date du jour."""
    session = brigade.session
    session.date_debut = datetime.date.today() - datetime.timedelta(days=30)
    session.date_fin = datetime.date.today() + datetime.timedelta(days=30)
    session.save()


def _programme_passe(decalage_semaines=4):
    lundi = datetime.date.today() - datetime.timedelta(weeks=decalage_semaines)
    lundi -= datetime.timedelta(days=lundi.weekday())
    return ProgrammeHebdomadaire.objects.create(lundi_de_semaine=lundi)


def _element(formation, volume, suffixe):
    matiere = Matiere.objects.create(intitule=f"Matière tableau {suffixe}", code=f"TAB{suffixe}")
    return creer_element(formation, matiere, volume=volume)


def _programmer(programme, cours, brigade, nombre_seances):
    for i in range(nombre_seances):
        seance_dans(programme, cours, brigade, instant(programme.lundi_de_semaine, i % 5, 8))


def _amener_a_affiche(programme, planificateur, redacteur):
    ServiceCircuitProgramme.soumettre(planificateur, programme)
    ServiceCircuitProgramme.valider(redacteur, programme)
    ServiceCircuitProgramme.enregistrer_signature(
        planificateur, programme, timezone.localdate(), SIGNATAIRE_ESSAI
    )
    ServiceCircuitProgramme.afficher(planificateur, programme)


def _ligne_de(groupes, brigade):
    for groupe in groupes:
        for ligne in groupe["lignes"]:
            if ligne.brigade.pk == brigade.pk:
                return ligne
    return None


def test_taux_avancement_calcule(planificateur, redacteur, instructeur, brigade_formation):
    """B2 : réalisé cumulé ÷ prescrit cumulé de la brigade — 12 h réalisées
    sur 21 h prescrites (deux matières de 10 h, plus la matière semence à
    1 h de `session_formation`, jamais programmée)."""
    _mettre_en_cours(brigade_formation)
    formation = brigade_formation.session.formation
    element_1 = _element(formation, volume=10, suffixe="T1")
    element_2 = _element(formation, volume=10, suffixe="T2")
    qualifier(instructeur, element_1.matiere)
    qualifier(instructeur, element_2.matiere)
    passe = _programme_passe()
    _programmer(passe, Cours(element_1, instructeur), brigade_formation, 5)  # 10 h
    _programmer(passe, Cours(element_2, instructeur), brigade_formation, 1)  # 2 h
    _amener_a_affiche(passe, planificateur, redacteur)

    ligne = _ligne_de(tableau_de_bord(), brigade_formation)

    assert ligne.taux_avancement == pytest.approx(12 / 21 * 100)


def test_comptes_matieres_achevee_en_cours_non_commencee(
    planificateur, redacteur, instructeur, brigade_formation
):
    """B3 : achevée (réalisé ≥ prescrit), en cours (0 < réalisé < prescrit),
    non commencée (réalisé nul) — même règle que le prérequis achevé. La
    matière semence de `session_formation` (conftest), jamais programmée,
    ajoute une seconde non commencée en plus de celle créée par ce test."""
    _mettre_en_cours(brigade_formation)
    formation = brigade_formation.session.formation
    achevee = _element(formation, volume=10, suffixe="C1")
    en_cours = _element(formation, volume=10, suffixe="C2")
    non_commencee = _element(formation, volume=10, suffixe="C3")
    for element in (achevee, en_cours, non_commencee):
        qualifier(instructeur, element.matiere)
    passe = _programme_passe()
    _programmer(passe, Cours(achevee, instructeur), brigade_formation, 5)
    _programmer(passe, Cours(en_cours, instructeur), brigade_formation, 1)
    _amener_a_affiche(passe, planificateur, redacteur)

    ligne = _ligne_de(tableau_de_bord(), brigade_formation)

    assert ligne.nombre_achevees == 1
    assert ligne.nombre_en_cours == 1
    assert ligne.nombre_non_commencees == 2


def test_brigade_absente_si_session_cloturee(planificateur, redacteur, brigade_formation):
    _mettre_en_cours(brigade_formation)
    ServiceClotureSession.cloturer(redacteur, brigade_formation.session)

    assert _ligne_de(tableau_de_bord(), brigade_formation) is None


def test_brigade_absente_si_session_future(brigade_formation):
    """`session_formation` (conftest) ouvre dans 30 jours — pas encore en
    cours, aucune mise en cours forcée ici."""
    assert _ligne_de(tableau_de_bord(), brigade_formation) is None


def test_mise_en_evidence_des_alertes(planificateur, redacteur, instructeur, brigade_formation):
    _mettre_en_cours(brigade_formation)
    element = _element(brigade_formation.session.formation, volume=10, suffixe="M1")
    qualifier(instructeur, element.matiere)
    passe = _programme_passe()
    _programmer(passe, Cours(element, instructeur), brigade_formation, 5)
    _amener_a_affiche(passe, planificateur, redacteur)
    ligne_programme = LigneProgramme.objects.filter(
        seance__programme=passe, brigade=brigade_formation
    ).first()
    ServiceSuivi.declarer_non_execution(planificateur, ligne_programme, MOTIF_ESSAI)

    ligne = _ligne_de(tableau_de_bord(), brigade_formation)

    assert ligne.nombre_alertes == 1


def test_requetes_constantes_avec_deux_et_dix_brigades(
    planificateur, redacteur, instructeur, brigade_formation
):
    """Mesure d'abord à deux brigades, étend ensuite à dix et mesure à
    nouveau — jamais les deux mesures sur le même état final, sans quoi
    une requête ajoutée dans une boucle resterait invisible."""
    session = brigade_formation.session
    _mettre_en_cours(brigade_formation)
    element = _element(session.formation, volume=10, suffixe="Q1")
    qualifier(instructeur, element.matiere)
    cours = Cours(element, instructeur)
    passe = _programme_passe()
    autre = ServiceBrigade.creer(redacteur, session, donnees_brigade(designation="TABQ0"))
    for brigade in (brigade_formation, autre):
        _programmer(passe, cours, brigade, 1)
    _amener_a_affiche(passe, planificateur, redacteur)

    tableau_de_bord()  # chauffe
    with CaptureQueriesContext(connection) as deux:
        tableau_de_bord()

    for i in range(8):
        supplement = ServiceBrigade.creer(
            redacteur, session, donnees_brigade(designation=f"TABQ{i + 1}")
        )
        _programmer(passe, cours, supplement, 1)

    with CaptureQueriesContext(connection) as dix:
        tableau_de_bord()

    assert len(deux.captured_queries) == len(dix.captured_queries)


# --- HTTP ---------------------------------------------------------------


def test_http_pedagogique_consulte_le_tableau_de_bord(
    client, acteurs, instructeur, brigade_formation
):
    _mettre_en_cours(brigade_formation)
    element = _element(brigade_formation.session.formation, volume=10, suffixe="H1")
    qualifier(instructeur, element.matiere)
    passe = _programme_passe()
    _programmer(passe, Cours(element, instructeur), brigade_formation, 5)
    _amener_a_affiche(passe, acteurs.planificateur, acteurs.pedagogique)
    client.force_login(acteurs.pedagogique)

    reponse = client.get(reverse("planification:tableau_bord"))

    assert reponse.status_code == 200
    page = reponse.content.decode("utf-8")
    assert str(brigade_formation) in page
    # 10 h réalisées sur 11 h prescrites (10 h de `element`, 1 h de la
    # matière semence de `session_formation`, jamais programmée) : 91 %.
    assert "91 %" in page


def test_http_direction_autorisee(client, circuit, direction_formation):
    client.force_login(direction_formation)

    reponse = client.get(reverse("planification:tableau_bord"))

    assert reponse.status_code == 200


def test_http_examens_autorisee(client, circuit):
    """D-284 : la matrice fait foi, quatre profils — pas seulement les
    deux cités par le critère."""
    client.force_login(circuit.acteurs.examens)

    reponse = client.get(reverse("planification:tableau_bord"))

    assert reponse.status_code == 200


def test_http_sans_brigade_en_cours_affiche_le_message(client, acteurs):
    client.force_login(acteurs.pedagogique)

    reponse = client.get(reverse("planification:tableau_bord"))

    assert "Aucune brigade en cours" in reponse.content.decode("utf-8")
