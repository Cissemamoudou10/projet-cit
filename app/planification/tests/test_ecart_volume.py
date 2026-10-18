"""US-PLAN-07 — Signaler les écarts de volume horaire (prompt 47, Temps 2).
Données entièrement fictives.
"""

import datetime

import pytest
from django.db import connection
from django.test import override_settings
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from organisation.models import Brigade
from organisation.services.brigade import ServiceBrigade
from organisation.tests.conftest import donnees_brigade
from planification.models import ProgrammeHebdomadaire
from planification.selectors_ecart_volume import (
    CONFORME,
    DEPASSEMENT,
    EN_COURS,
    RETARD,
    decorer_rapprochement,
    ecarts_volume_horaire,
)
from planification.selectors_rapprochement import rapprochement
from planification.services.circuit import ServiceCircuitProgramme
from planification.tests.aide_circuit import seance_dans
from planification.tests.conftest import Cours, creer_element, instant, qualifier
from referentiel.models import Matiere

SIGNATAIRE_ESSAI = "Signataire essai écart volume"


def _programme_passe(decalage_semaines=4):
    """US-SUI-01 (`rapprochement`) ne compte une séance au réalisé que si
    elle est PASSÉE, pas seulement affichée (`seance__fin__lte=a_la_date`) —
    même précaution que `_programme_passe` de `test_rapprochement.py` :
    `lundi_semaine` (toujours futur, +14 à +20 jours) ne convient pas ici."""
    lundi = datetime.date.today() - datetime.timedelta(weeks=decalage_semaines)
    lundi -= datetime.timedelta(days=lundi.weekday())
    return ProgrammeHebdomadaire.objects.create(lundi_de_semaine=lundi)


def _element(formation, volume, suffixe):
    matiere = Matiere.objects.create(intitule=f"Matière écart {suffixe}", code=f"ECV{suffixe}")
    return creer_element(formation, matiere, volume=volume)


def _programmer(programme, cours, brigade, nombre_seances, lundi):
    for i in range(nombre_seances):
        seance_dans(programme, cours, brigade, instant(lundi, i % 5, 8))


def _amener_a_affiche(programme, planificateur, redacteur):
    ServiceCircuitProgramme.soumettre(planificateur, programme)
    ServiceCircuitProgramme.valider(redacteur, programme)
    ServiceCircuitProgramme.enregistrer_signature(
        planificateur, programme, timezone.localdate(), SIGNATAIRE_ESSAI
    )
    ServiceCircuitProgramme.afficher(planificateur, programme)


def _terminer_la_session(brigade):
    session = brigade.session
    session.date_debut = datetime.date.today() - datetime.timedelta(days=60)
    session.date_fin = datetime.date.today() - datetime.timedelta(days=1)
    session.save()


def _brigades_chargees(pks):
    return list(Brigade.objects.select_related("session__formation").filter(pk__in=pks))


def _ligne_de(groupes, element):
    """Cherche par identifiant d'élément, jamais par position : `session_formation`
    (conftest) sème elle-même un élément « semence », dont l'ordre vis-à-vis de
    celui du test n'est pas garanti."""
    for groupe in groupes:
        for ligne in groupe.lignes:
            cle = (
                ligne.element_referentiel
                if hasattr(ligne, "element_referentiel")
                else ligne.ligne.element_referentiel
            )
            if cle.pk == element.pk:
                return ligne
    return None


# --- E2/E3 — statut, seuil, en_cours vs retard ------------------------------


def test_depassement_signale_au_dela_du_seuil(
    instructeur, brigade_formation, programme, lundi_semaine
):
    element = _element(brigade_formation.session.formation, volume=10, suffixe="D1")
    qualifier(instructeur, element.matiere)
    cours = Cours(element, instructeur)
    _programmer(
        programme, cours, brigade_formation, 8, lundi_semaine
    )  # 16 h, prescrit 10 h : +60 %

    groupes = ecarts_volume_horaire(_brigades_chargees([brigade_formation.pk]))

    ligne = _ligne_de(groupes, element)
    assert ligne.statut == DEPASSEMENT
    assert ligne.ecart_pourcent == pytest.approx(60.0)


def test_sous_programmation_non_signalee_avant_la_fin_de_session(
    instructeur, brigade_formation, programme, lundi_semaine
):
    """E3 : la session de `brigade_formation` se termine dans le futur — la
    matière très en-deçà du prescrit est « en cours », pas un écart
    remonté sur la consultation."""
    element = _element(brigade_formation.session.formation, volume=10, suffixe="E1")
    qualifier(instructeur, element.matiere)
    cours = Cours(element, instructeur)
    _programmer(programme, cours, brigade_formation, 1, lundi_semaine)  # 2 h sur 10 h prescrites

    groupes = ecarts_volume_horaire(_brigades_chargees([brigade_formation.pk]))

    assert _ligne_de(groupes, element) is None


def test_sous_programmation_signalee_apres_la_fin_de_session(
    instructeur, brigade_formation, programme, lundi_semaine
):
    element = _element(brigade_formation.session.formation, volume=10, suffixe="R1")
    qualifier(instructeur, element.matiere)
    cours = Cours(element, instructeur)
    _programmer(programme, cours, brigade_formation, 1, lundi_semaine)
    _terminer_la_session(brigade_formation)

    groupes = ecarts_volume_horaire(_brigades_chargees([brigade_formation.pk]))

    ligne = _ligne_de(groupes, element)
    assert ligne.statut == RETARD
    assert ligne.ecart_pourcent == pytest.approx(80.0)


def test_conforme_sous_le_seuil_n_est_jamais_signale(
    instructeur, brigade_formation, programme, lundi_semaine
):
    element = _element(brigade_formation.session.formation, volume=10, suffixe="C1")
    qualifier(instructeur, element.matiere)
    cours = Cours(element, instructeur)
    _programmer(
        programme, cours, brigade_formation, 5, lundi_semaine
    )  # 10 h, exactement le prescrit
    _terminer_la_session(brigade_formation)

    groupes = ecarts_volume_horaire(_brigades_chargees([brigade_formation.pk]))

    assert _ligne_de(groupes, element) is None


def test_seuil_modifie_par_parametre(instructeur, brigade_formation, programme, lundi_semaine):
    """E3 : un seuil relevé à 70 % absorbe le dépassement de 60 % mesuré
    par `test_depassement_signale_au_dela_du_seuil`."""
    element = _element(brigade_formation.session.formation, volume=10, suffixe="S1")
    qualifier(instructeur, element.matiere)
    cours = Cours(element, instructeur)
    _programmer(programme, cours, brigade_formation, 8, lundi_semaine)  # +60 %

    with override_settings(SEUIL_ECART_VOLUME_HORAIRE="70"):
        groupes = ecarts_volume_horaire(_brigades_chargees([brigade_formation.pk]))

    assert _ligne_de(groupes, element) is None


# --- E2, second volet — même mise en évidence sur le rapprochement (US-SUI-01) ---


def test_decoration_du_rapprochement_porte_le_meme_statut(
    planificateur, redacteur, instructeur, brigade_formation
):
    element = _element(brigade_formation.session.formation, volume=10, suffixe="P1")
    qualifier(instructeur, element.matiere)
    cours = Cours(element, instructeur)
    passe = _programme_passe()
    _programmer(passe, cours, brigade_formation, 8, passe.lundi_de_semaine)
    _amener_a_affiche(passe, planificateur, redacteur)

    groupes = rapprochement(brigade_id=brigade_formation.pk)
    decores = decorer_rapprochement(groupes)

    assert _ligne_de(decores, element).statut == DEPASSEMENT


def test_decoration_signale_en_cours_avant_la_fin_de_session(
    planificateur, redacteur, instructeur, brigade_formation
):
    """Le rapprochement complet (US-SUI-01) montre `en_cours`, à la
    différence de la liste d'alerte de la consultation — qui le tait
    (`test_sous_programmation_non_signalee_avant_la_fin_de_session`)."""
    element = _element(brigade_formation.session.formation, volume=10, suffixe="P3")
    qualifier(instructeur, element.matiere)
    cours = Cours(element, instructeur)
    passe = _programme_passe()
    _programmer(passe, cours, brigade_formation, 1, passe.lundi_de_semaine)
    _amener_a_affiche(passe, planificateur, redacteur)

    groupes = rapprochement(brigade_id=brigade_formation.pk)
    decores = decorer_rapprochement(groupes)

    assert _ligne_de(decores, element).statut == EN_COURS


def test_decoration_respecte_conforme_quand_rien_ne_depasse(
    planificateur, redacteur, instructeur, brigade_formation
):
    element = _element(brigade_formation.session.formation, volume=10, suffixe="P2")
    qualifier(instructeur, element.matiere)
    cours = Cours(element, instructeur)
    passe = _programme_passe()
    _programmer(passe, cours, brigade_formation, 5, passe.lundi_de_semaine)
    _amener_a_affiche(passe, planificateur, redacteur)

    groupes = rapprochement(brigade_id=brigade_formation.pk)
    decores = decorer_rapprochement(groupes)

    assert _ligne_de(decores, element).statut == CONFORME


# --- Requêtes constantes -----------------------------------------------------


def test_requetes_constantes_avec_deux_et_dix_brigades(
    redacteur, instructeur, brigade_formation, programme, lundi_semaine
):
    element = _element(brigade_formation.session.formation, volume=10, suffixe="Q1")
    qualifier(instructeur, element.matiere)
    cours = Cours(element, instructeur)
    _programmer(programme, cours, brigade_formation, 8, lundi_semaine)
    autre = ServiceBrigade.creer(
        redacteur, brigade_formation.session, donnees_brigade(designation="ECVQ2")
    )
    _programmer(programme, cours, autre, 1, lundi_semaine)

    # Chauffe : la première résolution d'une relation peut peupler un
    # cache indépendant du nombre de brigades (même précaution que P-39).
    ecarts_volume_horaire(_brigades_chargees([brigade_formation.pk, autre.pk]))

    with CaptureQueriesContext(connection) as deux:
        ecarts_volume_horaire(_brigades_chargees([brigade_formation.pk, autre.pk]))

    pks = [brigade_formation.pk, autre.pk]
    for i in range(8):
        supplement = ServiceBrigade.creer(
            redacteur, brigade_formation.session, donnees_brigade(designation=f"ECVQ{i + 3}")
        )
        pks.append(supplement.pk)

    with CaptureQueriesContext(connection) as dix:
        ecarts_volume_horaire(_brigades_chargees(pks))

    assert len(deux.captured_queries) == len(dix.captured_queries)


# --- HTTP ---------------------------------------------------------------


def test_http_consultation_du_programme_affiche_le_depassement(
    client, planificateur, instructeur, brigade_formation
):
    element = _element(brigade_formation.session.formation, volume=10, suffixe="H1")
    qualifier(instructeur, element.matiere)
    cours = Cours(element, instructeur)
    passe = _programme_passe()
    _programmer(passe, cours, brigade_formation, 8, passe.lundi_de_semaine)
    client.force_login(planificateur)

    reponse = client.get(
        reverse("planification:consultation_programme"),
        {"semaine": passe.lundi_de_semaine.isoformat()},
    )

    assert reponse.status_code == 200
    assert "dépassement" in reponse.content.decode("utf-8")


def test_http_rapprochement_affiche_le_statut(
    client, acteurs, direction_formation, instructeur, brigade_formation
):
    element = _element(brigade_formation.session.formation, volume=10, suffixe="H2")
    qualifier(instructeur, element.matiere)
    cours = Cours(element, instructeur)
    passe = _programme_passe()
    _programmer(passe, cours, brigade_formation, 8, passe.lundi_de_semaine)
    _amener_a_affiche(passe, acteurs.planificateur, acteurs.pedagogique)
    client.force_login(direction_formation)

    reponse = client.get(reverse("planification:rapprochement"))

    assert reponse.status_code == 200
    assert "dépassement" in reponse.content.decode("utf-8")


# --- E4 — habilitations (profils qui lisent le programme) -------------------


def test_http_consultation_refusee_a_la_cellule_examens(client, examens):
    """La Cellule examens ne lit pas le programme (§ 11.2) — la décoration
    E2 ajoutée à cet écran ne change rien à son habilitation existante."""
    client.force_login(examens)

    reponse = client.get(reverse("planification:consultation_programme"))

    assert reponse.status_code == 403
