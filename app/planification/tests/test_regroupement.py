"""US-PLAN-06 — regroupement de plusieurs brigades sur une même séance en
lieu partagé (prompt 42, partie 2). Appels directs à la porte unique.
Données fictives.
"""

import datetime

import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from noyau.exceptions import ErreurValidation
from organisation.services.brigade import ServiceBrigade
from planification.exceptions import TransitionProgrammeRefusee
from planification.models import Avenant, EtatProgramme, LigneProgramme, NatureAvenant, Seance
from planification.services.ecriture import ServiceEcritureSeance
from planification.services.modification import Avenantage
from planification.tests.aide_circuit import amener_a
from planification.tests.conftest import (
    Cours,
    affecter_stagiaires,
    creer_element,
    instant,
    qualifier,
)
from referentiel.models import CategorieLieu, Matiere, Prerequis, TypeLieuPartage

AVENANT = Avenantage(motif="Rattrapage en commun.", nature=NatureAvenant.AJOUT)


@pytest.fixture
def partage(circuit, lieu_partage, autre_instructeur, autre_brigade_formation, redacteur):
    """Une séance en amphithéâtre (lieu partagé), sur la brigade du circuit,
    qualifiée, prête à accueillir une seconde brigade. Un instructeur distinct
    de `circuit.cours.instructeur` : la semence posée par `amener_a` (même
    programme, même créneau, cette autre matière) ne doit jamais interférer
    avec RG-34, qui n'exempte pas une séance déjà en base par son regroupement."""
    matiere = Matiere.objects.create(intitule="Guerre électronique (essai)", code="GE01")
    element = creer_element(
        circuit.cours.element.formation,
        matiere,
        volume=40,
        categorie=CategorieLieu.LIEU_PARTAGE,
        type_lieu_partage=TypeLieuPartage.AMPHITHEATRE,
    )
    qualifier(autre_instructeur, matiere)
    cours = Cours(element, autre_instructeur)
    debut = instant(circuit.programme.lundi_de_semaine, 0, 8)
    seance = Seance.objects.create(
        programme=circuit.programme,
        element_referentiel=element,
        instructeur=autre_instructeur,
        lieu=lieu_partage,
        debut=debut,
        fin=debut + datetime.timedelta(hours=2),
    )
    LigneProgramme.objects.create(seance=seance, brigade=circuit.brigade)
    affecter_stagiaires(circuit.acteurs.pedagogique, circuit.brigade, 10)
    return circuit, seance, cours


# --- association admise, charge comptée une fois (C1 à C4) -------------------


def test_association_admise_une_seule_seance_deux_lignes(partage, autre_brigade_formation):
    circuit, seance, _ = partage
    affecter_stagiaires(circuit.acteurs.pedagogique, autre_brigade_formation, 10, prefixe="N")

    ServiceEcritureSeance.associer_brigades(
        circuit.acteurs.planificateur, seance, [autre_brigade_formation]
    )

    assert Seance.objects.filter(pk=seance.pk).count() == 1
    assert LigneProgramme.objects.filter(seance=seance).count() == 2
    # C4 : une seule Seance porte les deux brigades, la charge de
    # l'instructeur (calculée sur les Seance, jamais sur les LigneProgramme)
    # ne peut donc pas être comptée deux fois — vrai par construction (D-139).


def test_capacite_depassee_est_refusee_avec_l_ecart(partage, autre_brigade_formation):
    circuit, seance, _ = partage
    affecter_stagiaires(circuit.acteurs.pedagogique, autre_brigade_formation, 25, prefixe="N")  # 10 + 25 = 35 > 30

    with pytest.raises(ErreurValidation, match="écart de 5"):
        ServiceEcritureSeance.associer_brigades(
            circuit.acteurs.planificateur, seance, [autre_brigade_formation]
        )
    assert LigneProgramme.objects.filter(seance=seance).count() == 1


def test_lieu_non_partageable_est_refuse(partage, autre_brigade_formation):
    circuit, seance, _ = partage
    seance.lieu.mode_partage = None
    seance.lieu.save()
    affecter_stagiaires(circuit.acteurs.pedagogique, autre_brigade_formation, 5, prefixe="N")

    with pytest.raises(ErreurValidation, match="RG-37"):
        ServiceEcritureSeance.associer_brigades(
            circuit.acteurs.planificateur, seance, [autre_brigade_formation]
        )


def test_brigade_deja_occupee_sur_le_creneau_est_refusee(partage, autre_brigade_formation):
    circuit, seance, cours = partage
    Seance.objects.create(
        programme=circuit.programme,
        element_referentiel=cours.element,
        instructeur=cours.instructeur,
        lieu=None,
        debut=seance.debut,
        fin=seance.fin,
    ).lignes.create(brigade=autre_brigade_formation)

    with pytest.raises(ErreurValidation, match="n'est pas libre sur ce créneau"):
        ServiceEcritureSeance.associer_brigades(
            circuit.acteurs.planificateur, seance, [autre_brigade_formation]
        )


def test_prerequis_non_atteint_pour_une_brigade_ajoutee_est_refuse(partage, autre_brigade_formation):
    circuit, seance, cours = partage
    prerequis = creer_element(
        cours.element.formation, Matiere.objects.create(intitule="Bases (essai)", code="BAS1"), volume=4
    )
    Prerequis.objects.create(element=cours.element, element_prerequis=prerequis)
    affecter_stagiaires(circuit.acteurs.pedagogique, autre_brigade_formation, 5, prefixe="N")

    with pytest.raises(ErreurValidation, match="RG-39"):
        ServiceEcritureSeance.associer_brigades(
            circuit.acteurs.planificateur, seance, [autre_brigade_formation]
        )


# --- retrait et dissolution (R2) ---------------------------------------------


def test_retrait_supprime_la_ligne_et_libere_le_creneau(partage, autre_brigade_formation):
    circuit, seance, _ = partage
    affecter_stagiaires(circuit.acteurs.pedagogique, autre_brigade_formation, 5, prefixe="N")
    ServiceEcritureSeance.associer_brigades(
        circuit.acteurs.planificateur, seance, [autre_brigade_formation]
    )

    ServiceEcritureSeance.retirer_brigade(circuit.acteurs.planificateur, seance, autre_brigade_formation)

    assert not LigneProgramme.objects.filter(seance=seance, brigade=autre_brigade_formation).exists()
    assert Seance.objects.filter(pk=seance.pk).exists()


def test_retirer_la_derniere_brigade_est_refuse(partage):
    circuit, seance, _ = partage

    with pytest.raises(ErreurValidation, match="supprimer la séance"):
        ServiceEcritureSeance.retirer_brigade(circuit.acteurs.planificateur, seance, circuit.brigade)


def test_dissolution_retire_toutes_les_brigades_sauf_une(partage, autre_brigade_formation):
    circuit, seance, cours = partage
    troisieme = circuit.brigade  # la brigade choisie pour rester
    affecter_stagiaires(circuit.acteurs.pedagogique, autre_brigade_formation, 5, prefixe="N")
    ServiceEcritureSeance.associer_brigades(
        circuit.acteurs.planificateur, seance, [autre_brigade_formation]
    )

    ServiceEcritureSeance.retirer_brigade(circuit.acteurs.planificateur, seance, autre_brigade_formation)

    assert list(LigneProgramme.objects.filter(seance=seance).values_list("brigade_id", flat=True)) == [
        troisieme.pk
    ]


# --- programme affiché et soumis (R4, C9) ------------------------------------


def test_retrait_sur_un_affiche_est_refuse(partage, autre_brigade_formation):
    circuit, seance, _ = partage
    affecter_stagiaires(circuit.acteurs.pedagogique, autre_brigade_formation, 5, prefixe="N")
    ServiceEcritureSeance.associer_brigades(
        circuit.acteurs.planificateur, seance, [autre_brigade_formation]
    )
    amener_a(EtatProgramme.AFFICHE, circuit)

    with pytest.raises(ErreurValidation, match="non-exécution"):
        ServiceEcritureSeance.retirer_brigade(circuit.acteurs.planificateur, seance, autre_brigade_formation)


def test_association_sur_un_affiche_sans_puis_avec_avenant(partage, autre_brigade_formation):
    circuit, seance, _ = partage
    affecter_stagiaires(circuit.acteurs.pedagogique, autre_brigade_formation, 5, prefixe="N")
    amener_a(EtatProgramme.AFFICHE, circuit)

    with pytest.raises(TransitionProgrammeRefusee, match="(?i)portez un avenant"):
        ServiceEcritureSeance.associer_brigades(
            circuit.acteurs.planificateur, seance, [autre_brigade_formation]
        )

    ServiceEcritureSeance.associer_brigades(
        circuit.acteurs.planificateur, seance, [autre_brigade_formation], avenant=AVENANT
    )
    circuit.programme.refresh_from_db()
    assert circuit.programme.etat == EtatProgramme.AFFICHE
    assert Avenant.objects.filter(seance=seance, nature=NatureAvenant.AJOUT).exists()


def test_association_sur_un_soumis_est_refusee(partage, autre_brigade_formation):
    circuit, seance, _ = partage
    affecter_stagiaires(circuit.acteurs.pedagogique, autre_brigade_formation, 5, prefixe="N")
    amener_a(EtatProgramme.SOUMIS, circuit)

    with pytest.raises(TransitionProgrammeRefusee, match="(?i)retirez la soumission"):
        ServiceEcritureSeance.associer_brigades(
            circuit.acteurs.planificateur, seance, [autre_brigade_formation]
        )


# --- HTTP ---------------------------------------------------------------


def _url_brigades(seance):
    return reverse("planification:gerer_brigades", args=[seance.pk])


def test_http_association_par_la_planification(client, partage, autre_brigade_formation):
    circuit, seance, _ = partage
    affecter_stagiaires(circuit.acteurs.pedagogique, autre_brigade_formation, 5, prefixe="N")
    client.force_login(circuit.acteurs.planificateur)

    reponse = client.post(
        _url_brigades(seance), {"brigades": [autre_brigade_formation.pk]}, follow=True
    )

    assert "Brigades associées à la séance." in reponse.content.decode("utf-8")
    assert LigneProgramme.objects.filter(seance=seance, brigade=autre_brigade_formation).exists()


def test_http_association_par_la_pedagogique_est_refusee_403(client, partage, autre_brigade_formation):
    circuit, seance, _ = partage
    affecter_stagiaires(circuit.acteurs.pedagogique, autre_brigade_formation, 5, prefixe="N")
    client.force_login(circuit.acteurs.pedagogique)

    reponse = client.post(_url_brigades(seance), {"brigades": [autre_brigade_formation.pk]})

    assert reponse.status_code == 403
    assert not LigneProgramme.objects.filter(seance=seance, brigade=autre_brigade_formation).exists()


def test_http_liste_des_brigades_candidates_en_nombre_de_requetes_constant(client, partage, autre_brigade_formation):
    circuit, seance, _ = partage
    session = circuit.brigade.session
    client.force_login(circuit.acteurs.planificateur)

    with CaptureQueriesContext(connection) as deux_candidates:
        reponse = client.get(_url_brigades(seance))
    assert autre_brigade_formation.designation.encode() in reponse.content

    for i in range(8):
        ServiceBrigade.creer(
            circuit.acteurs.pedagogique, session, {"designation": f"SUP{i}", "effectif_previsionnel": 5}
        )

    with CaptureQueriesContext(connection) as dix_candidates:
        client.get(_url_brigades(seance))

    assert len(deux_candidates.captured_queries) == len(dix_candidates.captured_queries)


# --- relecture : deux refus métier, pas d'exception technique -------------


def test_associer_une_brigade_deja_presente_est_refusee_proprement(partage):
    circuit, seance, _ = partage

    with pytest.raises(ErreurValidation, match="est déjà sur cette séance"):
        ServiceEcritureSeance.associer_brigades(
            circuit.acteurs.planificateur, seance, [circuit.brigade]
        )
    assert LigneProgramme.objects.filter(seance=seance).count() == 1


def test_retirer_une_brigade_absente_de_la_seance_est_refusee_proprement(partage, autre_brigade_formation):
    circuit, seance, _ = partage

    with pytest.raises(ErreurValidation, match="n'est pas sur cette séance"):
        ServiceEcritureSeance.retirer_brigade(circuit.acteurs.planificateur, seance, autre_brigade_formation)
