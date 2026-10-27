"""Évaluations ajoutées par l'état `complet` — Prompt 51, § 2.5. E1/E2/E5
(les trois contrôles dont la séance verrouillée doit réserver son volume
AVANT que la génération des semaines n'épuise le prescrit, RG-39) sont
créées par `programme_complet.charger_programmes_complet` ; ce module
charge leurs notes (E1/E5 seulement — E2 n'en a aucune), et E3/E4 en
entier — aucun de ces appels n'exige l'horloge gelée (dates toutes
réellement futures, ou sans garde temporelle pour les notes — voir la
recherche de service qui a précédé l'écriture de ce fichier)."""

import datetime

from evaluations.jeu_recette.alea import note_fictive, nouveau_generateur
from evaluations.jeu_recette.semaines import jour_de_semaine

MOTIF_SURVEILLANT_EXTERIEUR = "FICT Surveillant-A"
REFERENCE_SUJET_A = "SUJ-E3-A"
REFERENCE_SUJET_B = "SUJ-E3-B"
MARDI_ISO = 2
MERCREDI_ISO = 3


def charger_notes_e1(contexte, evaluation_e1):
    """19 notes, 1 absence (effectif EXP1 actif = 20) — au moins deux
    stagiaires ex aequo (§ 2.5). Même sélecteur que `ServiceNote` lui-même
    (`organisation.selectors.stagiaires_actifs_des_brigades`), pour que
    l'ordre et le périmètre résolus ici coïncident exactement avec ce que
    le service validera."""
    from evaluations.services.note import ServiceNote
    from organisation.selectors import stagiaires_actifs_des_brigades

    stagiaires = list(stagiaires_actifs_des_brigades([evaluation_e1.brigade_id]))
    if len(stagiaires) != 20:
        contexte.stdout.write(
            f"  AVERTISSEMENT : EXP1 compte {len(stagiaires)} stagiaire(s) actif(s), "
            "20 attendus pour E1 — notes posées sur l'effectif réel."
        )
    generateur = nouveau_generateur(contexte.graine)
    donnees_brutes = {}
    absent, *notes_a_saisir = stagiaires if stagiaires else [None]
    if absent is not None:
        donnees_brutes[str(absent.pk)] = {"absent": True}
    valeur_commune = None
    for position, stagiaire in enumerate(notes_a_saisir):
        if position < 2:
            if valeur_commune is None:
                valeur_commune = note_fictive(generateur)
            valeur = valeur_commune
        else:
            valeur = note_fictive(generateur)
        donnees_brutes[str(stagiaire.pk)] = {"valeur": str(valeur)}
    ServiceNote.confirmer(contexte.agissant_examens, evaluation_e1, donnees_brutes)
    contexte.stdout.write(
        f"  Notes de E1 enregistrées ({len(notes_a_saisir)} notes dont deux ex aequo, 1 absence)."
    )


def charger_notes_e5(contexte, evaluation_e5):
    """10 notes sur 12, deux manquantes (§ 2.5) — jamais d'absence ici,
    « manquantes » au sens strict (clé omise de `donnees_brutes`)."""
    from evaluations.services.note import ServiceNote
    from organisation.selectors import stagiaires_actifs_des_brigades

    stagiaires = list(stagiaires_actifs_des_brigades([evaluation_e5.brigade_id]))
    if len(stagiaires) != 12:
        contexte.stdout.write(
            f"  AVERTISSEMENT : CDP1 compte {len(stagiaires)} stagiaire(s) actif(s), "
            "12 attendus pour E5 — notes posées sur l'effectif réel."
        )
    generateur = nouveau_generateur(contexte.graine + 1)
    notes_a_saisir = stagiaires[: max(len(stagiaires) - 2, 0)]
    donnees_brutes = {
        str(stagiaire.pk): {"valeur": str(note_fictive(generateur))} for stagiaire in notes_a_saisir
    }
    ServiceNote.confirmer(contexte.agissant_examens, evaluation_e5, donnees_brutes)
    contexte.stdout.write(
        f"  Notes de E5 enregistrées ({len(notes_a_saisir)}/12, deux manquantes)."
    )


def _creer_evaluation_e3(contexte, session_s1):
    from evaluations.models import TypeEvaluation
    from evaluations.services.evaluation import ServiceEvaluation
    from evaluations.services.sujet import ServiceSujet

    mardi_w5 = jour_de_semaine(contexte.date_reference, 5, MARDI_ISO)
    evaluation = ServiceEvaluation.creer(
        contexte.agissant_examens,
        {
            "element_referentiel": contexte.elements_f6["M6"],
            "session": session_s1,
            "type": TypeEvaluation.CERTIFICATIVE,
            "date": mardi_w5,
        },
    )
    sujet_a = ServiceSujet.enregistrer(
        contexte.agissant_examens,
        evaluation,
        {"reference": REFERENCE_SUJET_A, "date_depot": contexte.date_reference},
    )
    ServiceSujet.enregistrer(
        contexte.agissant_examens,
        evaluation,
        {"reference": REFERENCE_SUJET_B, "date_depot": contexte.date_reference},
    )
    ServiceSujet.retenir(contexte.agissant_examens, sujet_a)
    return evaluation


def _organiser_evaluation_e3(contexte, evaluation):
    from evaluations.services.organisation import ServiceOrganisationEpreuve

    ServiceOrganisationEpreuve.fixer_creneau(
        contexte.agissant_examens, evaluation, datetime.time(8, 0), datetime.time(10, 0)
    )
    organisation_exp1 = ServiceOrganisationEpreuve.ajouter_organisation(
        contexte.agissant_examens,
        evaluation,
        contexte.exp1,
        contexte.lieux["L9"],
        contexte.exp1.effectif_previsionnel,
    )
    ServiceOrganisationEpreuve.ajouter_surveillant(
        contexte.agissant_examens, organisation_exp1, instructeur=contexte.instructeurs["I8"]
    )
    ServiceOrganisationEpreuve.ajouter_surveillant(
        contexte.agissant_examens, organisation_exp1, nom_libre=MOTIF_SURVEILLANT_EXTERIEUR
    )


def charger_evaluation_e3(contexte, session_s1):
    """§ 2.5 : M6, session S1, mardi W+5. Deux sujets (A retenu).
    Organisation PARTIELLE : EXP1 dans L9 (surveillant I8 + un surveillant
    extérieur). EXP2 (périmètre session, donc automatiquement concernée par
    l'évaluation) n'est délibérément jamais organisée : incomplète, non
    prête, exprès (§ 2.5)."""
    evaluation = _creer_evaluation_e3(contexte, session_s1)
    _organiser_evaluation_e3(contexte, evaluation)
    contexte.stdout.write(
        "  E3 créée (deux sujets, A retenu, organisation partielle : EXP1 seule, EXP2 "
        "non organisée)."
    )
    return evaluation


def charger_evaluation_e4(contexte, session_s1):
    """§ 2.5 : M3, session S1, mercredi W+6. Aucun sujet, aucune
    organisation — exprès (§ 2.7)."""
    from evaluations.models import TypeEvaluation
    from evaluations.services.evaluation import ServiceEvaluation

    mercredi_w6 = jour_de_semaine(contexte.date_reference, 6, MERCREDI_ISO)
    evaluation = ServiceEvaluation.creer(
        contexte.agissant_examens,
        {
            "element_referentiel": contexte.elements_f6["M3"],
            "session": session_s1,
            "type": TypeEvaluation.CERTIFICATIVE,
            "date": mercredi_w6,
        },
    )
    contexte.stdout.write("  E4 créée (aucun sujet, aucune organisation).")
    return evaluation
