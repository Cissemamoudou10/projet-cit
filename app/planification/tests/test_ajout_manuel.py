"""US-PLAN-05, fin (prompt 42, partie 1, C4) — écran d'ajout manuel d'une
séance. Service et cycle HTTP réel. Données fictives.
"""

import datetime

import pytest
from django.urls import reverse

from noyau.exceptions import ErreurValidation
from planification.exceptions import TransitionProgrammeRefusee
from planification.models import Avenant, EtatProgramme, NatureAvenant, Seance
from planification.selectors import JOUR_SEMAINE_PAR_ISO, grille_active_avec_creneaux
from planification.services.contraintes import Candidate
from planification.services.ecriture import ServiceEcritureSeance
from planification.services.modification import Avenantage
from planification.tests.aide_circuit import amener_a, seance_dans
from planification.tests.conftest import activer_grille, instant, qualifier

AVENANT_AJOUT = Avenantage(motif="Rattrapage programmé.", nature=NatureAvenant.AJOUT)


@pytest.fixture
def qualifie(circuit):
    """K8 (prompt 59) : le formulaire d'ajout impose un créneau de la grille
    active — vendredi et samedi (jours 4 et 5, utilisés par les tests HTTP
    ci-dessous) y portent un créneau 09:00-11:00."""
    from ressources.models import JourSemaine

    qualifier(circuit.cours.instructeur, circuit.cours.element.matiere)
    activer_grille(
        circuit.acteurs.planificateur,
        "Essai ajout manuel",
        [(datetime.time(9, 0), datetime.time(11, 0))],
        jours=[JourSemaine.VENDREDI, JourSemaine.SAMEDI],
    )
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


def test_ajout_d_un_element_hors_formation_est_refuse(qualifie):
    """RG-05 (D-309, prompt 58) : l'ajout manuel (C4) n'avait jusqu'ici
    AUCUNE protection, ni écran (la brigade se choisit dans le même
    formulaire que la matière, filtrage différé, E1 reporté) ni service —
    désormais refusé, RG-05 vivant dans `ServiceContraintes`."""
    from planification.tests.conftest import creer_element
    from referentiel.models import Formation, Matiere, TypeFormation

    autre_formation = Formation.objects.create(
        intitule="Autre formation (RG-05, ajout manuel)",
        specialite="Transmissions",
        duree_semaines=1,
        type_formation=TypeFormation.objects.create(intitule="Autre type RG-05 ajout"),
    )
    element_hors_formation = creer_element(
        autre_formation,
        Matiere.objects.create(intitule="Hors formation (ajout manuel, essai)", code="HFA01"),
    )
    qualifier(qualifie.cours.instructeur, element_hors_formation.matiere)
    debut = instant(qualifie.programme.lundi_de_semaine, 0, 8)
    candidature = Candidate(
        brigade=qualifie.brigade,
        element_referentiel=element_hors_formation,
        instructeur=qualifie.cours.instructeur,
        debut=debut,
        fin=debut + datetime.timedelta(minutes=120),
    )

    with pytest.raises(ErreurValidation, match="RG-05"):
        ServiceEcritureSeance.creer_seance(qualifie.acteurs.planificateur, qualifie.programme, [candidature])

    assert Seance.objects.filter(programme=qualifie.programme).count() == 0


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


def _creneau_du_jour(qualifie, jour):
    """K8 (prompt 59) : résout le créneau de la grille active dont le jour
    correspond à `jour` (décalage depuis le lundi du programme)."""
    jour_date = qualifie.programme.lundi_de_semaine + datetime.timedelta(days=jour)
    _, creneaux = grille_active_avec_creneaux()
    return next(c for c in creneaux if JOUR_SEMAINE_PAR_ISO[c.jour_semaine] == jour_date.isoweekday())


def _formulaire(qualifie, jour=4, **extra):
    donnees = {
        "brigade": qualifie.brigade.pk,
        "element_referentiel": qualifie.cours.element.pk,
        "instructeur": qualifie.cours.instructeur.pk,
        "lieu": "",
        "creneau": _creneau_du_jour(qualifie, jour).pk,
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
