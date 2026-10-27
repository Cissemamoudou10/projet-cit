"""Évaluations du jeu volumineux — Prompt 51, Temps 3, § 3.1 : une
formative par brigade active sur les semaines passées (notes complètes),
quelques certificatives à venir organisées en partie, procès-verbal de fin
de formation pour 2 des 3 sessions terminées.

Simplification délibérée par rapport à l'état `complet` (E1/E2/E5, § 2.5) :
§ 3.1 ne demande PAS de séance verrouillée pour les formatives du jeu
volumineux (« formatives par brigade sur les semaines passées, notes
complètes » — rien de plus) — la branche déclarative de `ServiceEvaluation.
creer` (date déjà passée + motif, sans séance) suffit, et découple
entièrement ce module de la génération des programmes. Consignée dans
`docs/recette/JEUX-DE-DONNEES-PHASE-6.md`."""

import dataclasses
import datetime

from evaluations.jeu_recette.alea import note_fictive
from evaluations.jeu_recette.donnees_volume import (
    NOMBRE_CERTIFICATIVES_A_VENIR,
    NOMBRE_SESSIONS_TERMINEES_AVEC_PV,
)
from evaluations.jeu_recette.semaines import jour_de_semaine
from organisation.selectors import stagiaires_actifs_des_brigades

MOTIF_DATE_PASSEE = "Contrôle déclaré après coup (jeu volumineux, § 3.1)."
JEUDI_ISO = 4


@dataclasses.dataclass(frozen=True)
class ContexteEvaluationsVolume:
    """`.claude/rules/python.md`, § 5 paramètres max : les quatre voyagent
    ensemble dans toutes les fonctions publiques de ce module."""

    agissant_examens: object
    generateur: object
    date_reference: object
    stdout: object


def _noter_completement(contexte: ContexteEvaluationsVolume, evaluation):
    """Toujours une évaluation de périmètre BRIGADE ici (jamais session) —
    les seules formatives que ce module crée."""
    from evaluations.services.note import ServiceNote

    stagiaires = list(stagiaires_actifs_des_brigades([evaluation.brigade_id]))
    if not stagiaires:
        return 0
    donnees_brutes = {
        str(s.pk): {"valeur": str(note_fictive(contexte.generateur))} for s in stagiaires
    }
    ServiceNote.confirmer(contexte.agissant_examens, evaluation, donnees_brutes)
    return len(stagiaires)


def _creer_une_formative_a_date(agissant_examens, brigade, element, date):
    from evaluations.models import TypeEvaluation
    from evaluations.services.evaluation import ServiceEvaluation

    return ServiceEvaluation.creer(
        agissant_examens,
        {
            "element_referentiel": element,
            "brigade": brigade,
            "type": TypeEvaluation.FORMATIVE,
            "date": date,
            "motif_date_passee": MOTIF_DATE_PASSEE,
        },
    )


def _creer_une_formative(contexte: ContexteEvaluationsVolume, brigade, element, decalage_semaines):
    jour = jour_de_semaine(contexte.date_reference, decalage_semaines, JEUDI_ISO)
    return _creer_une_formative_a_date(contexte.agissant_examens, brigade, element, jour)


def _regrouper_par_formation(elements):
    """`elements` vient de `charger_composition_volume` — clé `(code_formation,
    code_matiere)`, valeur l'`ElementReferentiel` créé : chaque élément porte
    déjà sa formation (RG-05), le regroupement n'a besoin d'aucune requête."""
    elements_par_formation = {}
    for element in elements.values():
        elements_par_formation.setdefault(element.formation_id, []).append(element)
    return elements_par_formation


def charger_formatives_actives_volume(contexte: ContexteEvaluationsVolume, brigades_actives, elements):
    """Une formative par brigade active (§ 3.1), répartie sur les huit
    semaines passées, notes complètes — jamais de séance (voir docstring
    du module)."""
    elements_par_formation = _regrouper_par_formation(elements)
    total_notes = 0
    total_evaluations = 0
    brigades = list(brigades_actives.values())
    for indice, brigade in enumerate(brigades):
        elements_formation = elements_par_formation.get(brigade.session.formation_id)
        if not elements_formation:
            continue
        element = elements_formation[indice % len(elements_formation)]
        decalage = -1 - (indice % 8)
        evaluation = _creer_une_formative(contexte, brigade, element, decalage)
        total_notes += _noter_completement(contexte, evaluation)
        total_evaluations += 1
    contexte.stdout.write(
        f"  {total_evaluations} évaluations formatives créées (une par brigade active), "
        f"{total_notes} notes enregistrées."
    )


def charger_formatives_terminees_volume(contexte: ContexteEvaluationsVolume, brigades_terminees, elements):
    """Une formative par brigade des sessions terminées (notes complètes) —
    condition nécessaire à `ServiceMoyenne.calculer` : le procès-verbal de
    fin de formation porte sur TOUTES les évaluations de la session
    (`evaluations_de_la_session`), donc chacune doit déjà être notée
    intégralement avant `charger_proces_verbaux_volume`."""
    elements_par_formation = _regrouper_par_formation(elements)
    total_notes = 0
    total_evaluations = 0
    for brigade in brigades_terminees.values():
        elements_formation = elements_par_formation.get(brigade.session.formation_id)
        if not elements_formation:
            continue
        element = elements_formation[0]
        date_passee = brigade.session.date_fin - datetime.timedelta(weeks=1)
        evaluation = _creer_une_formative_a_date(contexte.agissant_examens, brigade, element, date_passee)
        total_notes += _noter_completement(contexte, evaluation)
        total_evaluations += 1
    contexte.stdout.write(
        f"  {total_evaluations} évaluations formatives créées sur les sessions terminées, "
        f"{total_notes} notes enregistrées."
    )


def charger_certificatives_a_venir_volume(contexte: ContexteEvaluationsVolume, sessions_actives):
    """Quelques certificatives « à venir », périmètre session (RG-52,
    RG-53 bis), datées deux semaines avant la fin de leur session (RG-49 :
    une date réelle, subie, jamais calculée en production — seule la
    génération de ce jeu la déduit) — organisées EN PARTIE : seule
    l'évaluation existe, sans sujet ni surveillant."""
    from evaluations.models import TypeEvaluation
    from evaluations.services.evaluation import ServiceEvaluation

    codes = list(sessions_actives.keys())[:NOMBRE_CERTIFICATIVES_A_VENIR]
    for code in codes:
        session = sessions_actives[code]
        element = session.formation.elements_referentiel.first()
        if element is None:
            continue
        date_examen = session.date_fin - datetime.timedelta(weeks=2)
        ServiceEvaluation.creer(
            contexte.agissant_examens,
            {
                "element_referentiel": element,
                "session": session,
                "type": TypeEvaluation.CERTIFICATIVE,
                "date": date_examen,
            },
        )
    contexte.stdout.write(f"  {len(codes)} évaluations certificatives à venir créées (organisées en partie).")


def charger_proces_verbaux_volume(contexte: ContexteEvaluationsVolume, sessions_terminees):
    """Procès-verbal de fin de formation pour `NOMBRE_SESSIONS_TERMINEES_AVEC_PV`
    des sessions terminées (§ 3.1) — WeasyPrint exige ses bibliothèques
    natives (P-44) : n'aboutit pas sous Windows, seulement dans le
    conteneur `python:3.14-slim-bookworm`."""
    from evaluations.models import TypeProcesVerbal
    from evaluations.services.proces_verbal import ServiceProcesVerbal

    codes = list(sessions_terminees.keys())[:NOMBRE_SESSIONS_TERMINEES_AVEC_PV]
    for code in codes:
        ServiceProcesVerbal.generer(contexte.agissant_examens, sessions_terminees[code], TypeProcesVerbal.FIN_DE_FORMATION)
    contexte.stdout.write(f"  {len(codes)} procès-verbaux de fin de formation générés ({', '.join(codes)}).")
