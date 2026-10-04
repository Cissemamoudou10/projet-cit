"""US-VAL-01, cycle HTTP réel (prompt 40 § 1) — soumission, retrait, page d'attente.

Données entièrement fictives. Les états se conduisent par le circuit, pas par
écriture directe (aide_circuit).
"""

import dataclasses
import datetime

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from administration.models import EntreeJournal, TypeAction
from planification.models import EtatProgramme, ProgrammeHebdomadaire
from planification.tests.aide_circuit import amener_a, seance_dans
from planification.tests.conftest import instant


def _url(nom, programme):
    return reverse(nom, args=[programme.pk])


def _entrees_de_soumission(programme):
    return EntreeJournal.objects.filter(
        objet_type="programme",
        objet_identifiant=str(programme.pk),
        type_action=TypeAction.TRANSITION_PROGRAMME,
        detail="T2",
    )


def _soumettre_une_autre_semaine(circuit, decalage_semaines):
    lundi = circuit.programme.lundi_de_semaine + datetime.timedelta(weeks=decalage_semaines)
    programme = ProgrammeHebdomadaire.objects.create(lundi_de_semaine=lundi)
    autre = dataclasses.replace(circuit, programme=programme)
    amener_a(EtatProgramme.SOUMIS, autre)
    return programme


def _requetes_de_la_page_d_attente(client, utilisateur):
    client.force_login(utilisateur)
    with CaptureQueriesContext(connection) as contexte:
        reponse = client.get(reverse("planification:attente_validation"))
    assert reponse.status_code == 200
    return len(contexte.captured_queries)


def test_soumission_par_la_planification_passe_a_soumis_et_journalise(client, circuit):
    programme = circuit.programme
    seance_dans(
        programme, circuit.cours, circuit.brigade, instant(programme.lundi_de_semaine, 0, 8)
    )
    client.force_login(circuit.acteurs.planificateur)

    reponse = client.post(_url("planification:soumettre", programme), follow=True)

    programme.refresh_from_db()
    assert programme.etat == EtatProgramme.SOUMIS
    assert _entrees_de_soumission(programme).exists()
    assert "Programme soumis à validation." in reponse.content.decode("utf-8")


def test_second_soumission_est_refusee_avec_la_regle_et_l_etat_reste(client, circuit):
    programme = circuit.programme
    amener_a(EtatProgramme.SOUMIS, circuit)
    client.force_login(circuit.acteurs.planificateur)

    reponse = client.post(_url("planification:soumettre", programme), follow=True)

    programme.refresh_from_db()
    assert programme.etat == EtatProgramme.SOUMIS
    assert "sur un programme soumis" in reponse.content.decode("utf-8")
    assert _entrees_de_soumission(programme).count() == 1


def test_soumission_d_un_programme_vide_n_est_pas_proposee_et_refusee_si_forcee(client, circuit):
    programme = circuit.programme
    client.force_login(circuit.acteurs.planificateur)

    reponse = client.post(_url("planification:soumettre", programme), follow=True)

    programme.refresh_from_db()
    assert programme.etat == EtatProgramme.BROUILLON
    assert "générez-le avant de le soumettre" in reponse.content.decode("utf-8")


def test_retrait_de_la_soumission_repasse_a_brouillon_et_sort_de_l_attente(client, circuit):
    programme = circuit.programme
    amener_a(EtatProgramme.SOUMIS, circuit)
    client.force_login(circuit.acteurs.planificateur)

    client.post(_url("planification:retirer_soumission", programme))

    programme.refresh_from_db()
    assert programme.etat == EtatProgramme.BROUILLON
    client.force_login(circuit.acteurs.pedagogique)
    reponse = client.get(reverse("planification:attente_validation"))
    assert reponse.context["validation_en_attente"]["compte"] == 0
    assert reponse.context["lignes"] == []


def test_soumission_par_la_pedagogique_est_refusee_403(client, circuit):
    programme = circuit.programme
    amener_a(EtatProgramme.BROUILLON, circuit)
    client.force_login(circuit.acteurs.pedagogique)

    reponse = client.post(_url("planification:soumettre", programme))

    assert reponse.status_code == 403
    programme.refresh_from_db()
    assert programme.etat == EtatProgramme.BROUILLON


def test_programme_soumis_apparait_en_attente_et_le_compteur_vaut_un(client, circuit):
    amener_a(EtatProgramme.SOUMIS, circuit)
    client.force_login(circuit.acteurs.pedagogique)

    reponse = client.get(reverse("planification:attente_validation"))

    assert reponse.status_code == 200
    assert reponse.context["validation_en_attente"]["compte"] == 1
    assert len(reponse.context["lignes"]) == 1
    date_semaine = circuit.programme.lundi_de_semaine.strftime("%d/%m/%Y")
    assert f"Semaine du {date_semaine}" in reponse.content.decode("utf-8")


def test_le_compteur_de_la_navigation_n_apparait_pas_pour_la_planification(client, circuit):
    amener_a(EtatProgramme.SOUMIS, circuit)
    client.force_login(circuit.acteurs.planificateur)

    reponse = client.get(reverse("planification:consultation_programme"))

    assert (
        "validation_en_attente" not in reponse.context
        or not reponse.context["validation_en_attente"]
    )


def test_requetes_de_la_page_d_attente_identiques_avec_un_et_dix_programmes(client, circuit):
    amener_a(EtatProgramme.SOUMIS, circuit)
    _requetes_de_la_page_d_attente(client, circuit.acteurs.pedagogique)
    avec_un = _requetes_de_la_page_d_attente(client, circuit.acteurs.pedagogique)

    for decalage in range(1, 10):
        _soumettre_une_autre_semaine(circuit, decalage)
    avec_dix = _requetes_de_la_page_d_attente(client, circuit.acteurs.pedagogique)

    assert avec_un == avec_dix
