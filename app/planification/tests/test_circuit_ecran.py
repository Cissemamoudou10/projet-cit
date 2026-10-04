"""US-VAL-03, groupe G — cycle HTTP réel (V8, C4). Données fictives.

Pas de liste ni de fiche détaillée de programme à ce stade : la consultation de
la semaine en tient lieu (écart noté dans ECARTS-LIVRABLES-SPRINT-3.md).
"""

from django.urls import reverse

from planification.models import EtatProgramme, Seance
from planification.tests.aide_circuit import amener_a
from planification.tests.conftest import qualifier


def _pks_seances(programme):
    return set(Seance.objects.filter(programme=programme).values_list("pk", flat=True))


def test_g1_la_consultation_affiche_l_etat_du_programme(client, scenario, circuit):
    amener_a(EtatProgramme.SOUMIS, circuit)
    client.force_login(circuit.acteurs.planificateur)

    reponse = client.get(
        reverse("planification:consultation_programme"), {"semaine": scenario.lundi.isoformat()}
    )

    assert reponse.status_code == 200
    assert "SOUMIS" in reponse.content.decode("utf-8")


def test_g2_generation_sur_semaine_soumise_refusee_a_l_ecran_sans_seance_creee(
    client, scenario, circuit
):
    programme = circuit.programme
    qualifier(circuit.cours.instructeur, circuit.cours.element.matiere)
    amener_a(EtatProgramme.SOUMIS, circuit)
    client.force_login(circuit.acteurs.planificateur)
    avant = _pks_seances(programme)

    reponse = client.post(
        reverse("planification:lancement_generation"),
        {"semaine": scenario.lundi.isoformat(), "brigades": [circuit.brigade.pk]},
        follow=True,
    )

    assert "Retirez la soumission (T3)" in reponse.content.decode("utf-8")
    assert _pks_seances(programme) == avant


def test_g3_lancement_sur_semaine_validee_affiche_le_motif_et_desactive_le_bouton(
    client, scenario, circuit
):
    amener_a(EtatProgramme.VALIDE, circuit)
    client.force_login(circuit.acteurs.planificateur)

    reponse = client.get(
        reverse("planification:lancement_generation"), {"semaine": scenario.lundi.isoformat()}
    )

    contenu = reponse.content.decode("utf-8")
    assert reponse.status_code == 200
    assert "Annulez la validation (T9)" in contenu
    assert "disabled" in contenu
