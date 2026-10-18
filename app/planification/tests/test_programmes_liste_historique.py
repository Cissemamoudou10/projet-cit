"""US-VAL-05 — Consulter les programmes et l'historique des validations
(prompt 47, Temps 3). Données entièrement fictives.
"""

import datetime

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from administration.models import TypeAction
from planification.models import ProgrammeHebdomadaire
from planification.selectors_circuit import historique_du_programme, programmes_filtres
from planification.services.circuit import ServiceCircuitProgramme
from planification.tests.aide_circuit import seance_dans

MOTIF_REJET = "Créneaux à reprendre (essai)."
SIGNATAIRE = "Signataire essai historique"


def _debut(circuit):
    return timezone.make_aware(
        datetime.datetime.combine(circuit.programme.lundi_de_semaine, datetime.time(8, 0))
    )


# --- H1 — historique, ordre chronologique, auteurs et motifs ---------------


def test_cycle_complet_dans_l_ordre_chronologique_avec_auteurs_et_motifs(circuit):
    seance_dans(circuit.programme, circuit.cours, circuit.brigade, _debut(circuit))
    acteurs = circuit.acteurs

    ServiceCircuitProgramme.soumettre(acteurs.planificateur, circuit.programme)
    ServiceCircuitProgramme.rejeter(acteurs.pedagogique, circuit.programme, MOTIF_REJET)
    ServiceCircuitProgramme.reprendre(acteurs.planificateur, circuit.programme)
    ServiceCircuitProgramme.soumettre(acteurs.planificateur, circuit.programme)
    ServiceCircuitProgramme.valider(acteurs.pedagogique, circuit.programme)
    ServiceCircuitProgramme.enregistrer_signature(
        acteurs.planificateur, circuit.programme, timezone.localdate(), SIGNATAIRE
    )
    ServiceCircuitProgramme.afficher(acteurs.planificateur, circuit.programme)

    entrees = list(historique_du_programme(circuit.programme))

    natures = [entree.type_action for entree in entrees]
    assert natures == [
        TypeAction.TRANSITION_PROGRAMME,  # T2 — soumission
        TypeAction.REJET_PROGRAMME,  # T5
        TypeAction.TRANSITION_PROGRAMME,  # T6 — reprise
        TypeAction.TRANSITION_PROGRAMME,  # T2 — resoumission
        TypeAction.VALIDATION_PROGRAMME,  # T4
        TypeAction.TRANSITION_PROGRAMME,  # T7 — signature
        TypeAction.TRANSITION_PROGRAMME,  # T8 — affichage
    ]
    assert MOTIF_REJET in entrees[1].detail
    assert entrees[1].auteur == acteurs.pedagogique
    assert entrees[0].auteur == acteurs.planificateur
    assert entrees[4].auteur == acteurs.pedagogique


# --- H2 — liste, filtres ----------------------------------------------------


def test_filtre_par_etat(circuit):
    seance_dans(circuit.programme, circuit.cours, circuit.brigade, _debut(circuit))
    ServiceCircuitProgramme.soumettre(circuit.acteurs.planificateur, circuit.programme)
    autre = ProgrammeHebdomadaire.objects.create(
        lundi_de_semaine=circuit.programme.lundi_de_semaine + datetime.timedelta(weeks=1)
    )

    resultat = programmes_filtres(etat="soumis")

    pks = {p.pk for p in resultat}
    assert circuit.programme.pk in pks
    assert autre.pk not in pks


def test_filtre_par_periode(circuit):
    hors_periode = ProgrammeHebdomadaire.objects.create(
        lundi_de_semaine=circuit.programme.lundi_de_semaine + datetime.timedelta(weeks=10)
    )

    resultat = programmes_filtres(
        periode_debut=circuit.programme.lundi_de_semaine,
        periode_fin=circuit.programme.lundi_de_semaine + datetime.timedelta(weeks=1),
    )

    pks = {p.pk for p in resultat}
    assert circuit.programme.pk in pks
    assert hors_periode.pk not in pks


# --- H3 — requêtes constantes -----------------------------------------------


def _programme_valide(lundi, valide_par):
    """VALIDÉ directement par l'ORM (lecture seule testée ici, pas le
    moteur) : exerce `programmes_filtres`/`valide_par`, affiché par
    `liste_programmes.html` — seul chemin qui déclenchait une requête par
    ligne avant `select_related("valide_par")` (trouvé en relecture)."""
    maintenant = timezone.now()
    return ProgrammeHebdomadaire.objects.create(
        lundi_de_semaine=lundi,
        etat="valide",
        date_soumission=maintenant,
        date_validation=maintenant,
        valide_par=valide_par,
    )


def test_http_requetes_constantes_avec_trois_et_trente_programmes(client, direction_formation):
    """Le lot de 30 porte PLUSIEURS programmes validés (quinze, tous dans la
    première page) contre un seul dans le lot de 3 : si `valide_par` n'était
    pas préchargé, le lot de 30 coûterait quatorze requêtes de plus — un
    nombre égal de requêtes malgré des comptes de VALIDÉS différents est
    donc une preuve réelle du préchargement, pas une coïncidence (trouvé en
    relecture : la première version de ce test ne portait qu'un seul
    programme validé de chaque côté, incapable de détecter un N+1)."""
    base = datetime.date.today() + datetime.timedelta(days=365)
    base -= datetime.timedelta(days=base.weekday())
    _programme_valide(base, direction_formation)
    for i in range(1, 3):
        ProgrammeHebdomadaire.objects.create(lundi_de_semaine=base + datetime.timedelta(weeks=i))
    client.force_login(direction_formation)

    with CaptureQueriesContext(connection) as trois:
        client.get(reverse("planification:liste_programmes"))

    for i in range(3, 15):
        ProgrammeHebdomadaire.objects.create(lundi_de_semaine=base + datetime.timedelta(weeks=i))
    for i in range(15, 30):
        _programme_valide(base + datetime.timedelta(weeks=i), direction_formation)

    with CaptureQueriesContext(connection) as trente:
        client.get(reverse("planification:liste_programmes"))

    assert len(trois.captured_queries) == len(trente.captured_queries)


# --- HTTP ---------------------------------------------------------------


def test_http_liste_programmes_affiche_les_semaines(client, direction_formation, circuit):
    client.force_login(direction_formation)

    reponse = client.get(reverse("planification:liste_programmes"))

    assert reponse.status_code == 200
    assert f"Semaine du {circuit.programme.lundi_de_semaine:%d/%m/%Y}" in reponse.content.decode(
        "utf-8"
    )


def test_http_consultation_affiche_l_historique(client, circuit):
    seance_dans(circuit.programme, circuit.cours, circuit.brigade, _debut(circuit))
    ServiceCircuitProgramme.soumettre(circuit.acteurs.planificateur, circuit.programme)
    client.force_login(circuit.acteurs.pedagogique)

    reponse = client.get(
        reverse("planification:consultation_programme"),
        {"semaine": circuit.programme.lundi_de_semaine.isoformat()},
    )

    assert reponse.status_code == 200
    assert "Historique" in reponse.content.decode("utf-8")


def test_http_liste_programmes_refusee_a_la_cellule_examens(client, examens):
    client.force_login(examens)

    reponse = client.get(reverse("planification:liste_programmes"))

    assert reponse.status_code == 403
