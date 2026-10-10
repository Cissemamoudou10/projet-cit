"""Scénario de la démonstration J2 (prompt 43, § A1/A2) — le fil entier,
par le cycle HTTP réel, étape par étape, avec les cinq comptes de profil.

S'il échoue sur une règle métier, c'est un défaut à corriger avant la
démonstration (condition d'arrêt, § A2) — jamais à contourner ici.

Réutilise le chargement de `planification.jeu_demonstration_j2` : la même
fonction qui prépare la base réelle de la démonstration (`manage.py
preparer_demonstration`) prépare ici la base de test — un seul jeu de
données, jamais deux qui divergent.
"""

import datetime

import pytest
from django.urls import reverse
from django.utils import timezone

from evaluations.models import Evaluation, OrganisationEpreuve, Sujet
from planification.jeu_demonstration_j2.chargement import charger_tout
from planification.models import EtatProgramme, LigneProgramme, NatureAvenant, ProgrammeHebdomadaire
from planification.selectors import JOUR_SEMAINE_PAR_ISO, grille_active_avec_creneaux
from ressources.models import IndisponibiliteInstructeur

FORMAT_DATE_HEURE = "%Y-%m-%dT%H:%M"


@pytest.fixture
def donnees(db):
    return charger_tout(_StdoutMuet())


class _StdoutMuet:
    def write(self, *args, **kwargs):
        pass


def _lundi_prochain():
    aujourd_hui = timezone.localdate()
    jours = (7 - aujourd_hui.weekday()) % 7 or 7
    return aujourd_hui + datetime.timedelta(days=jours)


def _etape_1_generation(client, donnees, lundi):
    """Planification génère le programme de la semaine."""
    client.force_login(donnees["comptes"]["plan.j2"])
    reponse = client.post(
        reverse("planification:lancement_generation"),
        {"semaine": lundi.isoformat(), "brigades": [donnees["brigade"].pk]},
        follow=True,
    )
    assert reponse.status_code == 200
    programme = ProgrammeHebdomadaire.objects.get(lundi_de_semaine=lundi)
    assert LigneProgramme.objects.filter(seance__programme=programme).exists()
    return programme


def _premier_creneau_libre(programme, brigade, lundi):
    """Le premier créneau EXACT (jour, heure) que la brigade n'occupe pas —
    robuste quel que soit le nombre de séances que la génération a placées
    et quelle que soit leur répartition dans la semaine."""
    _, creneaux = grille_active_avec_creneaux()
    occupes = set()
    for ligne in LigneProgramme.objects.filter(
        seance__programme=programme, brigade=brigade
    ).select_related("seance"):
        debut_local = timezone.localtime(ligne.seance.debut)
        occupes.add((debut_local.isoweekday(), debut_local.time()))
    for creneau in creneaux:
        jour_iso = JOUR_SEMAINE_PAR_ISO[creneau.jour_semaine]
        if (jour_iso, creneau.heure_debut) not in occupes:
            jour = lundi + datetime.timedelta(days=jour_iso - 1)
            return jour, creneau
    raise AssertionError("Aucun créneau libre — réduire le volume de M1.")


def _etape_2_controle(client, donnees, programme, lundi):
    """Examens crée un contrôle formatif, pour la brigade témoin (jamais
    sélectionnée à la génération, § donnees.py) : séance verrouillée au
    programme de la même semaine, marquée « Contrôle »."""
    jour, creneau = _premier_creneau_libre(programme, donnees["brigade_temoin"], lundi)
    client.force_login(donnees["comptes"]["exa.j2"])
    reponse = client.post(
        reverse("evaluations:creer_evaluation"),
        {
            "element_referentiel": donnees["element_examens"].pk,
            "type": "formative",
            "session": "",
            "brigade": donnees["brigade_temoin"].pk,
            "date": jour.isoformat(),
            "creneau_type": creneau.pk,
            "instructeur": donnees["instructeurs"]["Beta (J2)"].pk,
            "lieu": donnees["lieu"].pk,
            "motif_date_passee": "",
        },
        follow=True,
    )
    assert reponse.status_code == 200
    evaluation = Evaluation.objects.get(type="formative")
    assert evaluation.seance.verrouillee is True
    assert evaluation.seance.programme_id == programme.pk
    return evaluation


def _etape_3_soumission(client, donnees, programme):
    client.force_login(donnees["comptes"]["plan.j2"])
    reponse = client.post(reverse("planification:soumettre", args=[programme.pk]), follow=True)
    programme.refresh_from_db()
    assert reponse.status_code == 200
    assert programme.etat == EtatProgramme.SOUMIS


def _etape_4_rejet(client, donnees, programme):
    client.force_login(donnees["comptes"]["ped.j2"])
    reponse = client.post(
        reverse("planification:rejeter", args=[programme.pk]),
        {"motif": "Créneaux à revoir (démonstration)."},
        follow=True,
    )
    programme.refresh_from_db()
    assert reponse.status_code == 200
    assert programme.etat == EtatProgramme.REJETE
    assert programme.motif_rejet


def _etape_5_modification_et_resoumission(client, donnees, programme):
    """Planification lit le motif, modifie une séance — reprise implicite
    (REJETÉ -> BROUILLON, T6) — puis resoumet."""
    client.force_login(donnees["comptes"]["plan.j2"])
    ligne = (
        LigneProgramme.objects.filter(seance__programme=programme, brigade=donnees["brigade"])
        .select_related("seance")
        .first()
    )
    seance = ligne.seance
    debut_local = timezone.localtime(seance.debut)
    reponse = client.post(
        reverse("planification:modifier_seance", args=[seance.pk]),
        {
            "element_referentiel": seance.element_referentiel_id,
            "instructeur": seance.instructeur_id,
            "lieu": "",
            "date_seance": debut_local.date().isoformat(),
            "heure_debut": debut_local.time().strftime("%H:%M"),
            "heure_fin": timezone.localtime(seance.fin).time().strftime("%H:%M"),
            "confirmee": "",
            "nature_avenant": "",
            "motif_avenant": "",
        },
        follow=True,
    )
    programme.refresh_from_db()
    assert reponse.status_code == 200
    assert programme.etat == EtatProgramme.BROUILLON
    _etape_3_soumission(client, donnees, programme)


def _etape_6_validation(client, donnees, programme):
    client.force_login(donnees["comptes"]["ped.j2"])
    reponse = client.post(reverse("planification:valider", args=[programme.pk]), follow=True)
    programme.refresh_from_db()
    assert reponse.status_code == 200
    assert programme.etat == EtatProgramme.VALIDE


def _etape_7_signature_et_affichage(client, donnees, programme):
    client.force_login(donnees["comptes"]["plan.j2"])
    client.post(
        reverse("planification:signer", args=[programme.pk]),
        {"date_signature": timezone.localdate().isoformat(), "signataire": "Directeur (démo)"},
        follow=True,
    )
    reponse = client.post(reverse("planification:afficher", args=[programme.pk]), follow=True)
    programme.refresh_from_db()
    assert reponse.status_code == 200
    assert programme.etat == EtatProgramme.AFFICHE


def _etape_8_indisponibilite(client, donnees, programme):
    """Planification enregistre une indisponibilité sur le titulaire :
    séances impactées listées, remplacement par avenant, le programme
    reste AFFICHÉ."""
    titulaire = donnees["instructeurs"]["Alpha (J2)"]
    ligne = (
        LigneProgramme.objects.filter(seance__programme=programme, seance__instructeur=titulaire)
        .select_related("seance")
        .first()
    )
    seance = ligne.seance
    client.force_login(donnees["comptes"]["plan.j2"])
    reponse = client.post(
        reverse("ressources:declarer_indisponibilite_instructeur"),
        {
            "instructeur": titulaire.pk,
            "debut": (seance.debut - datetime.timedelta(hours=1)).strftime(FORMAT_DATE_HEURE),
            "fin": (seance.fin + datetime.timedelta(hours=1)).strftime(FORMAT_DATE_HEURE),
            "motif": "Mission (démonstration).",
        },
        follow=True,
    )
    assert reponse.status_code == 200
    indisponibilite = IndisponibiliteInstructeur.objects.get(instructeur=titulaire)
    assert str(donnees["element_programme"].matiere) in reponse.content.decode()

    remplacant = donnees["instructeurs"]["Gamma (J2)"]
    reponse = client.post(
        reverse("planification:remplacer_seance", args=[indisponibilite.pk, seance.pk]),
        {
            "instructeur": remplacant.pk,
            "confirmee": "",
            "nature_avenant": NatureAvenant.REMPLACEMENT_INSTRUCTEUR,
            "motif_avenant": "Indisponibilité déclarée (démonstration).",
        },
        follow=True,
    )
    seance.refresh_from_db()
    programme.refresh_from_db()
    assert reponse.status_code == 200
    assert seance.instructeur_id == remplacant.pk
    assert programme.etat == EtatProgramme.AFFICHE
    assert seance.avenants.exists()


def _etape_9_examen_final(client, donnees):
    """Examens crée l'examen final, enregistre deux sujets, en retient un,
    organise l'épreuve, imprime la convocation sans sujet."""
    client.force_login(donnees["comptes"]["exa.j2"])
    date_examen = timezone.localdate() + datetime.timedelta(days=45)
    reponse = client.post(
        reverse("evaluations:creer_evaluation"),
        {
            "element_referentiel": donnees["element_examens"].pk,
            "type": "certificative",
            "session": donnees["session"].pk,
            "brigade": "",
            "date": date_examen.isoformat(),
            "creneau_type": "",
            "instructeur": "",
            "lieu": "",
            "motif_date_passee": "",
        },
        follow=True,
    )
    assert reponse.status_code == 200
    evaluation = Evaluation.objects.get(type="certificative")

    client.post(
        reverse("evaluations:fixer_creneau", args=[evaluation.pk]),
        {"heure_debut": "08:00", "heure_fin": "10:00"},
    )
    for reference in ("Pli A (démo)", "Pli B (démo)"):
        client.post(
            reverse("evaluations:sujets", args=[evaluation.pk]),
            {"reference": reference, "date_depot": timezone.localdate().isoformat()},
        )
    premier_sujet = Sujet.objects.filter(evaluation=evaluation).order_by("rang").first()
    client.post(
        reverse("evaluations:retenir_sujet", args=[premier_sujet.pk]), {"confirmation": "on"}
    )

    client.post(
        reverse("evaluations:ajouter_organisation", args=[evaluation.pk]),
        {
            "brigade": donnees["brigade"].pk,
            "lieu": donnees["lieu"].pk,
            "effectif_attendu": donnees["brigade"].effectif_previsionnel,
        },
    )
    organisation = OrganisationEpreuve.objects.get(evaluation=evaluation)
    client.post(
        reverse("evaluations:ajouter_surveillant", args=[organisation.pk]),
        {"nom_libre": "Surveillant (démonstration)", "instructeur": ""},
    )

    reponse = client.get(reverse("evaluations:convocation", args=[evaluation.pk]))
    assert reponse.status_code == 200
    assert "Pli A (démo)" not in reponse.content.decode()
    return evaluation


def _etape_10_direction_formation(client, donnees, programme, evaluation, lundi):
    client.force_login(donnees["comptes"]["df.j2"])
    reponse = client.get(
        reverse("planification:consultation_programme") + f"?semaine={lundi.isoformat()}"
    )
    assert reponse.status_code == 200
    assert programme.get_etat_display() in reponse.content.decode()

    reponse = client.get(reverse("evaluations:convocation", args=[evaluation.pk]))
    assert reponse.status_code == 200

    reponse = client.get(reverse("evaluations:sujets", args=[evaluation.pk]))
    assert reponse.status_code == 403


def test_scenario_j2_du_debut_a_la_fin(client, donnees):
    lundi = _lundi_prochain()
    programme = _etape_1_generation(client, donnees, lundi)
    _etape_2_controle(client, donnees, programme, lundi)
    _etape_3_soumission(client, donnees, programme)
    _etape_4_rejet(client, donnees, programme)
    _etape_5_modification_et_resoumission(client, donnees, programme)
    _etape_6_validation(client, donnees, programme)
    _etape_7_signature_et_affichage(client, donnees, programme)
    _etape_8_indisponibilite(client, donnees, programme)
    evaluation = _etape_9_examen_final(client, donnees)
    _etape_10_direction_formation(client, donnees, programme, evaluation, lundi)
