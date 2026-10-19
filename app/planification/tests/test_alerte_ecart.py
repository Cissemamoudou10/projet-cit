"""US-SUI-02 — Être alerté des écarts significatifs (prompt 48, Temps 0).
D-282 ferme D-279 : la décoration du rapprochement (US-SUI-01), déplacée hors
de `selectors_ecart_volume.py` (US-PLAN-07), vit dans `selectors_alerte_ecart.py`.
Ces tests viennent de `test_ecart_volume.py` (prompt 47, Temps 2), déplacés ici
avec le code qu'ils vérifient. Données entièrement fictives.
"""

import datetime

from django.db import connection
from django.test import override_settings
from django.test.utils import CaptureQueriesContext
from django.urls import reverse
from django.utils import timezone

from organisation.services.brigade import ServiceBrigade
from organisation.tests.conftest import donnees_brigade
from planification.models import LigneProgramme, ProgrammeHebdomadaire
from planification.selectors_alerte_ecart import alertes, decorer_rapprochement
from planification.selectors_rapprochement import rapprochement
from planification.services.circuit import ServiceCircuitProgramme
from planification.services.suivi import ServiceSuivi
from planification.statut_volume import CONFORME, DEPASSEMENT, RETARD
from planification.tests.aide_circuit import seance_dans
from planification.tests.conftest import Cours, creer_element, instant, qualifier
from referentiel.models import Matiere

SIGNATAIRE_ESSAI = "Signataire essai alerte écart"
MOTIF_ESSAI = "Motif essai alerte écart."


def _programme_passe(decalage_semaines=4):
    """US-SUI-01 (`rapprochement`) ne compte une séance au réalisé que si
    elle est PASSÉE, pas seulement affichée (`seance__fin__lte=a_la_date`) —
    même précaution que `_programme_passe` de `test_rapprochement.py`."""
    lundi = datetime.date.today() - datetime.timedelta(weeks=decalage_semaines)
    lundi -= datetime.timedelta(days=lundi.weekday())
    return ProgrammeHebdomadaire.objects.create(lundi_de_semaine=lundi)


def _element(formation, volume, suffixe):
    matiere = Matiere.objects.create(intitule=f"Matière alerte {suffixe}", code=f"ALE{suffixe}")
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


def _ligne_de(groupes, element):
    """Cherche par identifiant d'élément, jamais par position : `session_formation`
    (conftest) sème elle-même un élément « semence », dont l'ordre vis-à-vis de
    celui du test n'est pas garanti."""
    for groupe in groupes:
        for ligne in groupe.lignes:
            if ligne.ligne.element_referentiel.pk == element.pk:
                return ligne
    return None


# --- A1/A2 — décoration du rapprochement (US-SUI-01) selon le réalisé ------


def test_decoration_conforme_quand_le_realise_suit_le_programme_echu(
    planificateur, redacteur, instructeur, brigade_formation
):
    """A2 : en cours de session, la référence est le PROGRAMMÉ ÉCHU — tant
    qu'aucune non-exécution n'est déclarée, le réalisé le suit exactement,
    quel que soit l'écart au prescrit (ici 10 h programmées sur 10 h
    prescrites, par construction du test)."""
    element = _element(brigade_formation.session.formation, volume=10, suffixe="P2")
    qualifier(instructeur, element.matiere)
    cours = Cours(element, instructeur)
    passe = _programme_passe()
    _programmer(passe, cours, brigade_formation, 5, passe.lundi_de_semaine)
    _amener_a_affiche(passe, planificateur, redacteur)

    groupes = rapprochement(brigade_id=brigade_formation.pk)
    decores = decorer_rapprochement(groupes)

    assert _ligne_de(decores, element).statut == CONFORME


def test_decoration_signale_retard_en_cours_de_session_sur_une_non_execution(
    planificateur, redacteur, instructeur, brigade_formation
):
    """A2 : seule une séance déclarée non exécutée fait apparaître un
    retard en cours de session — jamais une matière simplement pas encore
    enseignée (`test_decoration_conforme_quand_le_realise_suit_le_programme_echu`),
    ce qui était le défaut corrigé par D-282."""
    element = _element(brigade_formation.session.formation, volume=10, suffixe="P1")
    qualifier(instructeur, element.matiere)
    cours = Cours(element, instructeur)
    passe = _programme_passe()
    _programmer(passe, cours, brigade_formation, 5, passe.lundi_de_semaine)  # 10 h programmées
    _amener_a_affiche(passe, planificateur, redacteur)
    lignes = LigneProgramme.objects.filter(
        seance__programme=passe, seance__element_referentiel=element, brigade=brigade_formation
    ).order_by("pk")
    for ligne in lignes[:3]:
        ServiceSuivi.declarer_non_execution(planificateur, ligne, MOTIF_ESSAI)  # -6 h réalisées

    groupes = rapprochement(brigade_id=brigade_formation.pk)
    decores = decorer_rapprochement(groupes)

    assert _ligne_de(decores, element).statut == RETARD


def test_decoration_signale_depassement_apres_la_fin_de_session(
    planificateur, redacteur, instructeur, brigade_formation
):
    """Une fois la session terminée, la référence devient le prescrit
    (même borne que D-278) : le réalisé peut alors la dépasser, ce que le
    programmé échu interdisait par construction en cours de session."""
    element = _element(brigade_formation.session.formation, volume=10, suffixe="P4")
    qualifier(instructeur, element.matiere)
    cours = Cours(element, instructeur)
    passe = _programme_passe()
    _programmer(passe, cours, brigade_formation, 8, passe.lundi_de_semaine)  # 16 h, prescrit 10 h
    _amener_a_affiche(passe, planificateur, redacteur)
    _terminer_la_session(brigade_formation)

    groupes = rapprochement(brigade_id=brigade_formation.pk)
    decores = decorer_rapprochement(groupes)

    assert _ligne_de(decores, element).statut == DEPASSEMENT


# --- A1/A3 — la liste d'alertes elle-même -----------------------------------


def test_aucune_alerte_quand_le_realise_suit_le_programme_echu(
    planificateur, redacteur, instructeur, brigade_formation
):
    element = _element(brigade_formation.session.formation, volume=10, suffixe="A1")
    qualifier(instructeur, element.matiere)
    cours = Cours(element, instructeur)
    passe = _programme_passe()
    _programmer(passe, cours, brigade_formation, 5, passe.lundi_de_semaine)
    _amener_a_affiche(passe, planificateur, redacteur)

    groupes = alertes(brigade_id=brigade_formation.pk)

    assert _ligne_de(groupes, element) is None


def test_retard_signale_sur_le_prescrit_en_fin_de_session(
    planificateur, redacteur, instructeur, brigade_formation
):
    """Après la fin de session, la référence devient le prescrit : un
    réalisé encore en-deçà y reste en retard, à la différence du
    dépassement (`test_decoration_signale_depassement_apres_la_fin_de_session`)."""
    element = _element(brigade_formation.session.formation, volume=10, suffixe="A2")
    qualifier(instructeur, element.matiere)
    cours = Cours(element, instructeur)
    passe = _programme_passe()
    _programmer(passe, cours, brigade_formation, 1, passe.lundi_de_semaine)  # 2 h sur 10 h prescrites
    _amener_a_affiche(passe, planificateur, redacteur)
    _terminer_la_session(brigade_formation)

    groupes = alertes(brigade_id=brigade_formation.pk)

    assert _ligne_de(groupes, element).statut == RETARD


def test_alerte_disparait_apres_annulation_de_la_non_execution(
    planificateur, redacteur, instructeur, brigade_formation
):
    """Réversibilité d'US-SUI-05 : annuler la non-exécution restitue le
    réalisé au programmé échu, et l'alerte disparaît (A1 : jamais stockée)."""
    element = _element(brigade_formation.session.formation, volume=10, suffixe="A3")
    qualifier(instructeur, element.matiere)
    cours = Cours(element, instructeur)
    passe = _programme_passe()
    _programmer(passe, cours, brigade_formation, 5, passe.lundi_de_semaine)
    _amener_a_affiche(passe, planificateur, redacteur)
    ligne = LigneProgramme.objects.filter(
        seance__programme=passe, seance__element_referentiel=element, brigade=brigade_formation
    ).first()
    ServiceSuivi.declarer_non_execution(planificateur, ligne, MOTIF_ESSAI)
    assert _ligne_de(alertes(brigade_id=brigade_formation.pk), element).statut == RETARD

    ServiceSuivi.annuler_non_execution(planificateur, ligne)

    assert _ligne_de(alertes(brigade_id=brigade_formation.pk), element) is None


def test_seuil_alerte_modifie_par_parametre(
    planificateur, redacteur, instructeur, brigade_formation
):
    """Le dépassement de 60 % mesuré par
    `test_decoration_signale_depassement_apres_la_fin_de_session` disparaît
    sous un seuil relevé à 70 % — seuil propre à SUI-02
    (`SEUIL_ALERTE_ECART_REALISE`), indépendant de celui de PLAN-07 (D-282)."""
    element = _element(brigade_formation.session.formation, volume=10, suffixe="A4")
    qualifier(instructeur, element.matiere)
    cours = Cours(element, instructeur)
    passe = _programme_passe()
    _programmer(passe, cours, brigade_formation, 8, passe.lundi_de_semaine)  # +60 %
    _amener_a_affiche(passe, planificateur, redacteur)
    _terminer_la_session(brigade_formation)

    with override_settings(SEUIL_ALERTE_ECART_REALISE="70"):
        groupes = alertes(brigade_id=brigade_formation.pk)

    assert _ligne_de(groupes, element) is None


# --- Requêtes constantes -----------------------------------------------------


def _brigades_programmees(session, passe, planificateur, redacteur, instructeur):
    """Dix brigades de la même session, chacune avec sa propre matière
    programmée dans l'unique programme de la semaine (RG-33 bis)."""
    brigades = []
    for i in range(10):
        brigade = ServiceBrigade.creer(redacteur, session, donnees_brigade(designation=f"ALEQ{i}"))
        element = _element(session.formation, volume=10, suffixe=f"Q{i}")
        qualifier(instructeur, element.matiere)
        _programmer(passe, Cours(element, instructeur), brigade, 5, passe.lundi_de_semaine)
        brigades.append((brigade, element))
    _amener_a_affiche(passe, planificateur, redacteur)
    return brigades


def _mettre_en_alerte(passe, planificateur, brigade, element):
    ligne = LigneProgramme.objects.filter(
        seance__programme=passe, seance__element_referentiel=element, brigade=brigade
    ).first()
    ServiceSuivi.declarer_non_execution(planificateur, ligne, MOTIF_ESSAI)


def test_requetes_constantes_avec_deux_et_dix_brigades(
    planificateur, redacteur, instructeur, brigade_formation
):
    """Même précaution que la relecture d'US-VAL-05 : fait varier le NOMBRE
    de brigades EN ALERTE entre les deux mesures (2 puis 10), pas seulement
    le nombre total de brigades — sans quoi un N+1 sur la seule requête
    ajoutée par Temps 0 (`volumes_programme_echu_par_element_brigade`)
    resterait invisible."""
    session = brigade_formation.session
    passe = _programme_passe()
    brigades = _brigades_programmees(session, passe, planificateur, redacteur, instructeur)

    _mettre_en_alerte(passe, planificateur, *brigades[0])
    _mettre_en_alerte(passe, planificateur, *brigades[1])
    alertes(session_id=session.pk)  # chauffe

    with CaptureQueriesContext(connection) as deux:
        alertes(session_id=session.pk)

    for brigade, element in brigades[2:]:
        _mettre_en_alerte(passe, planificateur, brigade, element)

    with CaptureQueriesContext(connection) as dix:
        alertes(session_id=session.pk)

    assert len(deux.captured_queries) == len(dix.captured_queries)


# --- HTTP --------------------------------------------------------------


def test_http_rapprochement_affiche_le_statut(
    client, acteurs, direction_formation, instructeur, brigade_formation
):
    element = _element(brigade_formation.session.formation, volume=10, suffixe="H2")
    qualifier(instructeur, element.matiere)
    cours = Cours(element, instructeur)
    passe = _programme_passe()
    _programmer(passe, cours, brigade_formation, 8, passe.lundi_de_semaine)
    _amener_a_affiche(passe, acteurs.planificateur, acteurs.pedagogique)
    _terminer_la_session(brigade_formation)
    client.force_login(direction_formation)

    reponse = client.get(reverse("planification:rapprochement"))

    assert reponse.status_code == 200
    assert "dépassement" in reponse.content.decode("utf-8")
