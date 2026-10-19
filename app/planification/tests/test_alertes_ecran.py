"""US-SUI-02, cycle HTTP réel — écran et compteur de navigation des alertes
d'écart significatif (prompt 48, Story 1). Données entièrement fictives.
"""

import datetime

from django.urls import reverse
from django.utils import timezone

from organisation.services.brigade import ServiceBrigade
from organisation.tests.conftest import donnees_brigade
from planification.models import LigneProgramme, ProgrammeHebdomadaire
from planification.services.circuit import ServiceCircuitProgramme
from planification.services.suivi import ServiceSuivi
from planification.tests.aide_circuit import seance_dans
from planification.tests.conftest import Cours, creer_element, instant, qualifier
from referentiel.models import Matiere

SIGNATAIRE_ESSAI = "Signataire essai alertes HTTP"
MOTIF_ESSAI = "Motif essai alertes HTTP."


def _programme_passe(decalage_semaines=4):
    lundi = datetime.date.today() - datetime.timedelta(weeks=decalage_semaines)
    lundi -= datetime.timedelta(days=lundi.weekday())
    return ProgrammeHebdomadaire.objects.create(lundi_de_semaine=lundi)


def _element(formation, volume, suffixe):
    matiere = Matiere.objects.create(intitule=f"Matière alertes HTTP {suffixe}", code=f"ALH{suffixe}")
    return creer_element(formation, matiere, volume=volume)


def _mettre_une_brigade_en_alerte(planificateur, redacteur, instructeur, brigade, suffixe):
    """Un programme affiché, une séance déclarée non exécutée : retard
    certain en cours de session (A2)."""
    element = _element(brigade.session.formation, volume=10, suffixe=suffixe)
    qualifier(instructeur, element.matiere)
    cours = Cours(element, instructeur)
    passe = _programme_passe()
    seance_dans(passe, cours, brigade, instant(passe.lundi_de_semaine, 0, 8))
    ServiceCircuitProgramme.soumettre(planificateur, passe)
    ServiceCircuitProgramme.valider(redacteur, passe)
    ServiceCircuitProgramme.enregistrer_signature(
        planificateur, passe, timezone.localdate(), SIGNATAIRE_ESSAI
    )
    ServiceCircuitProgramme.afficher(planificateur, passe)
    ligne = LigneProgramme.objects.get(seance__programme=passe, brigade=brigade)
    ServiceSuivi.declarer_non_execution(planificateur, ligne, MOTIF_ESSAI)
    return element


def test_http_cellule_pedagogique_consulte_les_alertes(
    client, acteurs, instructeur, brigade_formation
):
    element = _mettre_une_brigade_en_alerte(
        acteurs.planificateur, acteurs.pedagogique, instructeur, brigade_formation, "H1"
    )
    client.force_login(acteurs.pedagogique)

    reponse = client.get(reverse("planification:alertes_ecart"))

    assert reponse.status_code == 200
    page = reponse.content.decode("utf-8")
    assert str(element.matiere) in page
    assert "retard" in page


def test_http_sans_alerte_affiche_le_message(client, acteurs):
    client.force_login(acteurs.pedagogique)

    reponse = client.get(reverse("planification:alertes_ecart"))

    assert "Aucune alerte" in reponse.content.decode("utf-8")


def test_http_filtre_par_brigade(client, acteurs, instructeur, brigade_formation, session_formation):
    _mettre_une_brigade_en_alerte(
        acteurs.planificateur, acteurs.pedagogique, instructeur, brigade_formation, "H2"
    )
    autre_brigade = ServiceBrigade.creer(
        acteurs.pedagogique, session_formation, donnees_brigade(designation="ALHB")
    )
    client.force_login(acteurs.pedagogique)

    reponse = client.get(reverse("planification:alertes_ecart"), {"brigade": autre_brigade.pk})

    page = reponse.content.decode("utf-8")
    # `autre_brigade` figure une seule fois : dans le menu déroulant du
    # filtre (toutes les brigades y sont proposées), jamais dans un groupe
    # de résultat, exclue — aucune alerte ne la concerne.
    assert page.count(str(autre_brigade)) == 1


def test_http_planification_autorisee(client, circuit):
    client.force_login(circuit.acteurs.planificateur)

    reponse = client.get(reverse("planification:alertes_ecart"))

    assert reponse.status_code == 200


def test_http_examens_autorisee(client, circuit):
    client.force_login(circuit.acteurs.examens)

    reponse = client.get(reverse("planification:alertes_ecart"))

    assert reponse.status_code == 200


def test_http_direction_autorisee(client, circuit, direction_formation):
    client.force_login(direction_formation)

    reponse = client.get(reverse("planification:alertes_ecart"))

    assert reponse.status_code == 200


# --- A3 — compteur de la navigation -----------------------------------------


def test_le_compteur_de_la_navigation_compte_les_alertes(
    client, acteurs, instructeur, brigade_formation
):
    _mettre_une_brigade_en_alerte(
        acteurs.planificateur, acteurs.pedagogique, instructeur, brigade_formation, "H3"
    )
    client.force_login(acteurs.pedagogique)

    reponse = client.get(reverse("planification:alertes_ecart"))

    assert reponse.context["alertes_en_attente"]["compte"] == 1


def test_le_compteur_de_la_navigation_n_apparait_pas_pour_la_planification(client, circuit):
    """A3 : « comme le compteur des programmes en attente » — réservé à la
    cellule pédagogique, pas à la planification qui lit pourtant l'écran."""
    client.force_login(circuit.acteurs.planificateur)

    reponse = client.get(reverse("planification:consultation_programme"))

    assert (
        "alertes_en_attente" not in reponse.context or not reponse.context["alertes_en_attente"]
    )
