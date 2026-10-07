"""US-PLAN-05, fin (prompt 42, partie 1, C4) — écran d'ajout manuel d'une
séance. Service et cycle HTTP réel. Données fictives.
"""

import datetime

import pytest
from django.urls import reverse

from noyau.exceptions import ErreurValidation
from planification.exceptions import TransitionProgrammeRefusee
from planification.models import Avenant, EtatProgramme, NatureAvenant, Seance
from planification.services.contraintes import Candidate
from planification.services.ecriture import ServiceEcritureSeance
from planification.services.modification import Avenantage
from planification.tests.aide_circuit import amener_a, seance_dans
from planification.tests.conftest import instant, qualifier

AVENANT_AJOUT = Avenantage(motif="Rattrapage programmé.", nature=NatureAvenant.AJOUT)


@pytest.fixture
def qualifie(circuit):
    qualifier(circuit.cours.instructeur, circuit.cours.element.matiere)
    return circuit


def _candidature(circuit, jour=0, heure=8, duree_min=120):
    debut = instant(circuit.programme.lundi_de_semaine, jour, heure)
    return Candidate(
        brigade=circuit.brigade,
        element_referentiel=circuit.cours.element,
        instructeur=circuit.cours.instructeur,
        debut=debut,
        fin=debut + datetime.timedelta(minutes=duree_min),
    )


# --- service -----------------------------------------------------------------


def test_ajout_sur_creneau_libre_admis_et_verrouille(qualifie):
    seance = ServiceEcritureSeance.creer_seance(
        qualifie.acteurs.planificateur, qualifie.programme, [_candidature(qualifie)]
    )
    assert seance.verrouillee is True


def test_ajout_violant_une_contrainte_est_refuse_en_la_nommant(qualifie):
    seance_dans(
        qualifie.programme,
        qualifie.cours,
        qualifie.brigade,
        instant(qualifie.programme.lundi_de_semaine, 0, 8),
    )
    with pytest.raises(ErreurValidation, match="RG-34"):
        ServiceEcritureSeance.creer_seance(
            qualifie.acteurs.planificateur, qualifie.programme, [_candidature(qualifie)]
        )
    assert Seance.objects.filter(programme=qualifie.programme).count() == 1


def test_ajout_sur_un_affiche_sans_avenant_refuse_avec_refuse(qualifie):
    amener_a(EtatProgramme.AFFICHE, qualifie)
    avant = Seance.objects.filter(programme=qualifie.programme).count()
    with pytest.raises(TransitionProgrammeRefusee, match="(?i)portez un avenant"):
        ServiceEcritureSeance.creer_seance(
            qualifie.acteurs.planificateur, qualifie.programme, [_candidature(qualifie, jour=4)]
        )
    assert Seance.objects.filter(programme=qualifie.programme).count() == avant


def test_ajout_sur_un_affiche_avec_avenant_admis_nature_ajout(qualifie):
    amener_a(EtatProgramme.AFFICHE, qualifie)
    seance = ServiceEcritureSeance.creer_seance(
        qualifie.acteurs.planificateur,
        qualifie.programme,
        [_candidature(qualifie, jour=4)],
        avenant=AVENANT_AJOUT,
    )
    qualifie.programme.refresh_from_db()
    assert qualifie.programme.etat == EtatProgramme.AFFICHE
    assert seance.verrouillee is True
    avenant = Avenant.objects.get(seance=seance)
    assert avenant.nature == NatureAvenant.AJOUT


# --- HTTP ----------------------------------------------------------------


def _url_ajout(programme):
    return reverse("planification:ajouter_seance", args=[programme.pk])


def _formulaire(qualifie, jour=4, debut="09:00", fin="11:00", **extra):
    donnees = {
        "brigade": qualifie.brigade.pk,
        "element_referentiel": qualifie.cours.element.pk,
        "instructeur": qualifie.cours.instructeur.pk,
        "lieu": "",
        "date_seance": (
            qualifie.programme.lundi_de_semaine + datetime.timedelta(days=jour)
        ).isoformat(),
        "heure_debut": debut,
        "heure_fin": fin,
    }
    donnees.update(extra)
    return donnees


def test_http_ajout_admis_verrouille_et_marque_sur_la_consultation(client, qualifie):
    client.force_login(qualifie.acteurs.planificateur)

    reponse = client.post(_url_ajout(qualifie.programme), _formulaire(qualifie), follow=True)

    assert "Séance ajoutée et verrouillée." in reponse.content.decode("utf-8")
    assert Seance.objects.filter(programme=qualifie.programme).exists()


def test_http_ajout_sur_un_affiche_sans_avenant_refuse_avec_avenant_admis(client, qualifie):
    amener_a(EtatProgramme.AFFICHE, qualifie)
    client.force_login(qualifie.acteurs.planificateur)

    refus = client.post(_url_ajout(qualifie.programme), _formulaire(qualifie, jour=5), follow=True)
    assert "portez un avenant" in refus.content.decode("utf-8").lower()

    admis = client.post(
        _url_ajout(qualifie.programme),
        _formulaire(
            qualifie,
            jour=5,
            motif_avenant="Rattrapage programmé.",
            nature_avenant=NatureAvenant.AJOUT,
        ),
        follow=True,
    )
    assert "Séance ajoutée et verrouillée." in admis.content.decode("utf-8")
    qualifie.programme.refresh_from_db()
    assert qualifie.programme.etat == EtatProgramme.AFFICHE
