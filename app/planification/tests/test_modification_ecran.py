"""US-PLAN-05, cycle HTTP réel (prompt 41 § 4, groupe F). Données fictives."""

import datetime

import pytest
from django.urls import reverse

from administration.models import EntreeJournal, TypeAction
from planification.models import Avenant, EtatProgramme, NatureAvenant, Seance
from planification.selectors import JOUR_SEMAINE_PAR_ISO, grille_active_avec_creneaux
from planification.tests.aide_circuit import amener_a, seance_dans
from planification.tests.conftest import activer_grille, instant, qualifier


def _seance_de_test(circuit):
    return seance_dans(
        circuit.programme, circuit.cours, circuit.brigade, instant(circuit.programme.lundi_de_semaine, 0, 8)
    )


@pytest.fixture
def grille(circuit):
    """K8 (prompt 59) : le formulaire de modification impose un créneau de
    la grille active — deux créneaux (celui par défaut de `_formulaire` et
    celui, décalé, utilisé par F1) sur tous les jours ouvrés."""
    from ressources.models import JourSemaine

    return activer_grille(
        circuit.acteurs.planificateur,
        "Essai modification écran",
        [(datetime.time(9, 0), datetime.time(10, 0)), (datetime.time(10, 10), datetime.time(12, 0))],
        jours=[
            JourSemaine.LUNDI,
            JourSemaine.MARDI,
            JourSemaine.MERCREDI,
            JourSemaine.JEUDI,
            JourSemaine.VENDREDI,
            JourSemaine.SAMEDI,
        ],
    )


def _creneau(circuit, jour, debut, fin):
    jour_date = circuit.programme.lundi_de_semaine + datetime.timedelta(days=jour)
    _, creneaux = grille_active_avec_creneaux()
    debut_t = datetime.time.fromisoformat(debut)
    fin_t = datetime.time.fromisoformat(fin)
    return next(
        c
        for c in creneaux
        if JOUR_SEMAINE_PAR_ISO[c.jour_semaine] == jour_date.isoweekday()
        and c.heure_debut == debut_t
        and c.heure_fin == fin_t
    )


def _formulaire(circuit, jour, debut="09:00", fin="10:00", **extra):
    donnees = {
        "element_referentiel": circuit.cours.element.pk,
        "instructeur": circuit.cours.instructeur.pk,
        "lieu": "",
        "creneau": _creneau(circuit, jour, debut, fin).pk,
    }
    donnees.update(extra)
    return donnees


def _url_modifier(seance):
    return reverse("planification:modifier_seance", args=[seance.pk])


def _consultation(circuit, jour=None):
    """La consultation n'affiche qu'un jour à la fois : `jour` choisit l'onglet."""
    url = reverse("planification:consultation_programme") + (
        f"?semaine={circuit.programme.lundi_de_semaine.isoformat()}"
    )
    return url + (f"&jour={jour}" if jour else "")


def test_f1_modification_par_la_planification_verrouille_et_s_affiche(client, grille, circuit):
    qualifier(circuit.cours.instructeur, circuit.cours.element.matiere)
    seance = _seance_de_test(circuit)
    client.force_login(circuit.acteurs.planificateur)

    reponse = client.post(
        _url_modifier(seance), _formulaire(circuit, 3, debut="10:10", fin="12:00"), follow=True
    )

    seance.refresh_from_db()
    assert seance.debut == instant(circuit.programme.lundi_de_semaine, 3, 10, 10)
    assert seance.verrouillee is True
    assert "Séance modifiée et verrouillée." in reponse.content.decode("utf-8")
    assert "#verrou" in client.get(_consultation(circuit, "jeudi")).content.decode("utf-8")


def test_f2_modification_violant_une_contrainte_affiche_la_regle_et_n_ecrit_rien(client, grille, circuit):
    qualifier(circuit.cours.instructeur, circuit.cours.element.matiere)
    seance = _seance_de_test(circuit)
    seance_dans(circuit.programme, circuit.cours, circuit.brigade, instant(circuit.programme.lundi_de_semaine, 3, 9))
    client.force_login(circuit.acteurs.planificateur)
    avant = seance.debut

    reponse = client.post(_url_modifier(seance), _formulaire(circuit, 3), follow=True)

    seance.refresh_from_db()
    assert seance.debut == avant
    assert seance.verrouillee is False
    assert "RG-34" in reponse.content.decode("utf-8")


def test_f3_affiche_sans_avenant_est_refuse_puis_avec_avenant_le_motif_s_affiche(client, grille, circuit):
    qualifier(circuit.cours.instructeur, circuit.cours.element.matiere)
    amener_a(EtatProgramme.AFFICHE, circuit)
    seance = Seance.objects.get(programme=circuit.programme)
    client.force_login(circuit.acteurs.planificateur)

    refus = client.post(_url_modifier(seance), _formulaire(circuit, 3), follow=True)
    assert "portez un avenant" in refus.content.decode("utf-8").lower()
    assert not Avenant.objects.filter(seance=seance).exists()

    client.post(
        _url_modifier(seance),
        _formulaire(circuit, 3, motif_avenant="Changement de créneau demandé par le lieu.",
                    nature_avenant=NatureAvenant.DEPLACEMENT),
        follow=True,
    )

    circuit.programme.refresh_from_db()
    assert circuit.programme.etat == EtatProgramme.AFFICHE
    assert Avenant.objects.filter(seance=seance, nature=NatureAvenant.DEPLACEMENT).exists()
    assert "Changement de créneau demandé par le lieu." in client.get(_consultation(circuit)).content.decode("utf-8")


def test_f4_annulation_de_validation_sans_motif_refusee_puis_admise_avec_motif(client, circuit):
    amener_a(EtatProgramme.VALIDE, circuit)
    client.force_login(circuit.acteurs.planificateur)
    url = reverse("planification:annuler_validation", args=[circuit.programme.pk])

    refus = client.post(url, {"motif": "   ", "confirmee": "on"}, follow=True)
    assert "exige une confirmation et un motif" in refus.content.decode("utf-8")
    circuit.programme.refresh_from_db()
    assert circuit.programme.etat == EtatProgramme.VALIDE

    client.post(url, {"motif": "Créneau à corriger.", "confirmee": "on"})
    circuit.programme.refresh_from_db()
    assert circuit.programme.etat == EtatProgramme.BROUILLON
    assert EntreeJournal.objects.filter(
        objet_identifiant=str(circuit.programme.pk), type_action=TypeAction.TRANSITION_PROGRAMME,
        detail__startswith="T9",
    ).exists()


def test_f5_modification_par_la_pedagogique_est_refusee_403(client, grille, circuit):
    seance = _seance_de_test(circuit)
    client.force_login(circuit.acteurs.pedagogique)

    reponse = client.post(_url_modifier(seance), _formulaire(circuit, 3))

    assert reponse.status_code == 403
    seance.refresh_from_db()
    assert seance.verrouillee is False


def test_f6_la_bascule_sans_lieu_n_est_pas_preselectionnee(client, circuit):
    seance = _seance_de_test(circuit)
    client.force_login(circuit.acteurs.planificateur)

    contenu = client.get(_url_modifier(seance)).content.decode("utf-8")

    assert f'value="{NatureAvenant.BASCULE_SANS_LIEU}" selected' not in contenu
    assert "bascule_sans_lieu" in contenu  # l'option existe, elle n'est pas présélectionnée


def test_f7_la_matiere_proposee_est_filtree_sur_la_formation_de_la_brigade(client, circuit):
    """K3, prompt 58 (RECETTE-01 A3) : l'écran de modification ne propose
    que les éléments de référentiel de la formation de la brigade de la
    séance — jamais une matière homonyme d'une AUTRE formation, qui
    porterait un volume prescrit différent sans que rien ne les distingue
    à l'écran."""
    from referentiel.models import ElementReferentiel, Formation, TypeFormation

    seance = _seance_de_test(circuit)
    autre_formation = Formation.objects.create(
        intitule="Autre formation (homonyme)",
        specialite="Transmissions",
        duree_semaines=1,
        type_formation=TypeFormation.objects.create(intitule="Autre type F7"),
    )
    element_homonyme = ElementReferentiel.objects.create(
        formation=autre_formation,
        matiere=circuit.cours.element.matiere,
        volume_horaire_prescrit=999,
        categorie_lieu=circuit.cours.element.categorie_lieu,
    )
    client.force_login(circuit.acteurs.planificateur)

    contenu = client.get(_url_modifier(seance)).content.decode("utf-8")

    assert f'value="{circuit.cours.element.pk}"' in contenu
    assert f'value="{element_homonyme.pk}"' not in contenu
