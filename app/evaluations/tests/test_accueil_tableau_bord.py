"""US-IHM-01 (prompt 64) — tableau de bord de la page d'accueil
(`noyau:accueil`). Vit dans `evaluations/tests/`, pas `noyau/tests/` :
`noyau` ne peut importer aucune application métier
(`tests/architecture/test_couches.py`), mais rien n'empêche un test d'une
application EN TÊTE de la chaîne (`evaluations`) d'exercer une URL d'une
application plus basse — même précédent que
`planification/tests/test_generation_ecran.py`. Données entièrement
fictives.
"""

import datetime

from django.db import connection
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from evaluations.tests.conftest import creer_brigade
from organisation.models import Stagiaire
from organisation.services.affectation import ServiceAffectation
from organisation.services.brigade import ServiceBrigade
from organisation.services.session import ServiceSession
from planification.models import EtatProgramme, LigneProgramme, ProgrammeHebdomadaire
from referentiel.models import Matiere
from ressources.models import IndisponibiliteInstructeur, Instructeur, Lieu, Qualification, Statut
from ressources.services.salle_attitree import ServiceSalleAttitree


def _lundi_de_la_semaine(date):
    return date - datetime.timedelta(days=date.weekday())


def test_cellule_pedagogique_voit_les_chiffres_mais_pas_les_evaluations(client, redacteur, brigade):
    client.force_login(redacteur)

    reponse = client.get(reverse("noyau:accueil"))

    assert reponse.status_code == 200
    tableau = reponse.context["tableau"]
    assert tableau.nombre_formations is not None
    assert tableau.nombre_instructeurs is not None
    assert tableau.nombre_sessions_en_cours is not None
    assert tableau.nombre_alertes_ecart is not None
    assert tableau.nombre_programmes_en_attente is not None
    assert tableau.semaine_courante is not None
    # La cellule pédagogique n'a pas evaluations_lecture (§ 11.2) : aucun
    # chiffre d'évaluation, même si l'évaluation existe réellement.
    assert tableau.nombre_evaluations_non_pretes is None


def test_cellule_examens_voit_les_evaluations_mais_pas_le_programme_ni_les_instructeurs(
    client, examens, certificative
):
    # `certificative` (fixture) n'a aucun sujet retenu : elle compte parmi
    # les évaluations à venir non prêtes.
    client.force_login(examens)

    reponse = client.get(reverse("noyau:accueil"))

    assert reponse.status_code == 200
    tableau = reponse.context["tableau"]
    assert tableau.nombre_evaluations_non_pretes >= 1
    assert tableau.nombre_formations is not None
    assert tableau.nombre_sessions_en_cours is not None
    # ni instructeurs_qualifications_lecture, ni programme_lecture (§ 11.2).
    assert tableau.nombre_instructeurs is None
    assert tableau.nombre_matieres_sans_instructeur is None
    assert tableau.nombre_programmes_en_attente is None
    assert tableau.semaine_courante is None


def test_administrateur_ne_voit_aucun_chiffre_metier(client, administrateur):
    client.force_login(administrateur)

    reponse = client.get(reverse("noyau:accueil"))

    assert reponse.status_code == 200
    tableau = reponse.context["tableau"]
    assert tableau.nombre_formations is None
    assert tableau.nombre_instructeurs is None
    assert tableau.nombre_evaluations_non_pretes is None


def test_matieres_sans_instructeur_qualifie_est_compte(client, redacteur, matiere):
    Matiere.objects.create(intitule="Sans instructeur EVAL", code="SANSI1")
    instructeur = Instructeur.objects.create(
        nom="Barnak",
        prenom="Oswin",
        matricule="M-ACC1",
        grade="Lt",
        specialite="Transmissions",
        statut=Statut.MILITAIRE_DU_CENTRE,
    )
    Qualification.objects.create(instructeur=instructeur, matiere=matiere)
    client.force_login(redacteur)

    reponse = client.get(reverse("noyau:accueil"))

    tableau = reponse.context["tableau"]
    # `matiere` (fixture) est qualifiée, `autre_matiere` ne l'est pas.
    assert tableau.nombre_matieres_sans_instructeur >= 1


def test_programme_de_la_semaine_courante_et_suivante(client, redacteur):
    lundi_courant = _lundi_de_la_semaine(timezone.localdate())
    maintenant = timezone.now()
    ProgrammeHebdomadaire.objects.create(
        lundi_de_semaine=lundi_courant,
        etat=EtatProgramme.VALIDE,
        date_soumission=maintenant,
        date_validation=maintenant,
        valide_par=redacteur,
    )
    client.force_login(redacteur)

    reponse = client.get(reverse("noyau:accueil"))

    tableau = reponse.context["tableau"]
    assert tableau.semaine_courante.etat == "valide"
    assert tableau.semaine_courante.etat_libelle == "Validé"
    assert tableau.semaine_suivante.etat is None
    assert tableau.semaine_suivante.etat_libelle is None


def test_detail_de_la_semaine_compte_les_seances_et_les_brigades(
    client, redacteur, seance, brigade
):
    programme = seance.programme
    programme.lundi_de_semaine = _lundi_de_la_semaine(timezone.localdate())
    programme.save()
    LigneProgramme.objects.create(seance=seance, brigade=brigade)
    client.force_login(redacteur)

    reponse = client.get(reverse("noyau:accueil"))

    tableau = reponse.context["tableau"]
    assert tableau.semaine_courante.nombre_seances == 1
    assert tableau.semaine_courante.nombre_brigades == 1
    assert tableau.semaine_suivante.nombre_seances == 0


def test_brigades_sans_salle_attitree_est_compte(client, planificateur, redacteur, session):
    creer_brigade(redacteur, session, "SANSSALLE")
    brigade_avec_salle = creer_brigade(redacteur, session, "AVECSALLE")
    lieu = Lieu.objects.create(intitule="Salle ACC1", capacite=20, categorie="salle_attitree")
    ServiceSalleAttitree.attribuer(planificateur, brigade_avec_salle, lieu)
    client.force_login(redacteur)

    reponse = client.get(reverse("noyau:accueil"))

    tableau = reponse.context["tableau"]
    assert tableau.nombre_brigades_sans_salle >= 1


def test_instructeurs_indisponibles_cette_semaine_est_compte(client, redacteur, instructeur):
    lundi_courant = _lundi_de_la_semaine(timezone.localdate())
    IndisponibiliteInstructeur.objects.create(
        instructeur=instructeur,
        debut=timezone.make_aware(datetime.datetime.combine(lundi_courant, datetime.time(8, 0))),
        fin=timezone.make_aware(datetime.datetime.combine(lundi_courant, datetime.time(12, 0))),
        motif="Mission extérieure",
    )
    client.force_login(redacteur)

    reponse = client.get(reverse("noyau:accueil"))

    tableau = reponse.context["tableau"]
    assert tableau.nombre_instructeurs_indisponibles_semaine >= 1


def _creer_session_avec_brigade_notee(redacteur, formation, suffixe):
    session = ServiceSession.creer(
        redacteur,
        {
            "formation": formation,
            "intitule": f"Session ACC{suffixe}",
            "date_debut": datetime.date.today() - datetime.timedelta(days=5),
            "date_fin": datetime.date.today() + datetime.timedelta(days=90),
            "effectif_attendu": 10,
        },
    )
    brigade = ServiceBrigade.creer(
        redacteur, session, {"designation": "EXPB", "effectif_previsionnel": 10}
    )
    stagiaire = Stagiaire.objects.create(
        session=session,
        matricule=f"ACC{suffixe:04d}",
        nom="Stagiaire",
        prenom="Essai",
        grade="Sgt",
        unite="1er RTR",
    )
    ServiceAffectation.affecter(redacteur, stagiaire, brigade)


def test_nombre_de_requetes_constant_avec_deux_volumes_de_donnees(
    client, redacteur, formation, element_referentiel
):
    """Témoin à deux brigades réelles, PAS zéro : avec zéro brigade, le
    moteur d'alertes (`rapprochement`) court-circuite sa requête `__in`
    vide — une base vide masquerait une vraie croissance en la comparant à
    elle-même (0 requête des deux côtés serait toujours égal)."""
    url = reverse("noyau:accueil")
    for i in range(2):
        _creer_session_avec_brigade_notee(redacteur, formation, i)
    client.force_login(redacteur)
    client.get(url)  # appel de chauffe (P-39) : cache de permissions

    with CaptureQueriesContext(connection) as deux_brigades:
        client.get(url)

    for i in range(2, 10):
        _creer_session_avec_brigade_notee(redacteur, formation, i)

    with CaptureQueriesContext(connection) as dix_brigades:
        client.get(url)

    assert len(deux_brigades.captured_queries) == len(dix_brigades.captured_queries)
