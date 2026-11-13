"""Moteur de calcul partagé par `ServiceMoyenne.calculer`, `.calculer_evaluation`
et `.detailler` (US-EVAL-06, US-EVAL-07, US-EVAL-12) — M1 : rien n'est stocké,
tout se recalcule à partir des notes déjà saisies (US-EVAL-05) et des poids du
référentiel. Module séparé de `evaluations/services/moyenne.py` pour rester
sous 400 lignes (`.claude/rules/python.md`) : celui-ci ne connaît ni
l'habilitation ni le journal, qui restent dans `moyenne.py`.
"""

import dataclasses
import decimal

from django.conf import settings
from django.db.models import Q

from evaluations.constantes import TRAITEMENT_ABSENCE_ZERO
from evaluations.models import Evaluation, Note, TypeEvaluation
from organisation.selectors import affectations_actives_des_brigades
from referentiel.models import ElementReferentiel

VINGT = decimal.Decimal(20)
DEUX_DECIMALES = decimal.Decimal("0.01")

_POIDS_PAR_TYPE = (
    (TypeEvaluation.FORMATIVE, "poids_formatif"),
    (TypeEvaluation.CERTIFICATIVE, "poids_certificatif"),
)


@dataclasses.dataclass(frozen=True)
class ContexteCalcul:
    """Regroupe ce qui voyage ensemble dans tout le calcul d'un stagiaire —
    `.claude/rules/python.md`, § 5 paramètres max."""

    session: object
    evaluations_par_module_type: dict
    notes: dict


@dataclasses.dataclass(frozen=True)
class NoteManquante:
    """M5, RG-59 bis : une entrée par (module, stagiaire) — jamais une par
    évaluation en cause, quel que soit leur nombre."""

    module: object
    brigade: object
    stagiaire: object


@dataclasses.dataclass(frozen=True)
class NoteDetail:
    """Une note individuelle du détail d'un module (US-EVAL-12) — valeur
    déjà ramenée sur 20 (M2), celle réellement utilisée par le calcul,
    jamais la valeur brute sur `note_maximale` qui ne se compare pas d'une
    évaluation à l'autre. `None` si l'absence est exclue du calcul (N6)."""

    evaluation: object
    valeur: decimal.Decimal | None
    absent: bool


@dataclasses.dataclass(frozen=True)
class DetailModule:
    """Détail d'un module pour UN stagiaire — notes par type, poids, note
    du module et coefficient (US-EVAL-12). Construit par `_note_module`,
    jamais recalculé séparément : même donnée que celle qui entre dans
    `ResultatStagiaire.moyenne`."""

    module: object
    notes_formatives: list
    notes_certificatives: list
    poids_formatif: object
    poids_certificatif: object
    note_module: decimal.Decimal | None
    coefficient: object


def _donnees_session(session):
    """Cinq requêtes au total, jamais une par brigade, par module ou par
    stagiaire (M8)."""
    modules = list(
        ElementReferentiel.objects.filter(formation_id=session.formation_id)
        .select_related("matiere")
        .order_by("matiere__intitule")
    )
    brigades = list(session.brigades.order_by("designation"))
    for brigade in brigades:
        # `Brigade.__str__` lit `self.session` : sans ce cache posé à la
        # main, chaque affichage (gabarit) déclencherait une requête PAR
        # brigade — le reverse manager ne peuple jamais le FK inverse.
        brigade.session = session
    brigade_ids = [brigade.pk for brigade in brigades]
    module_ids = [module.pk for module in modules]
    evaluations = list(
        Evaluation.objects.filter(element_referentiel_id__in=module_ids).filter(
            Q(session_id=session.pk) | Q(brigade_id__in=brigade_ids)
        )
    )
    notes = {
        (note.evaluation_id, note.stagiaire_id): note
        for note in Note.objects.filter(evaluation_id__in=[e.pk for e in evaluations])
    }
    affectations = list(affectations_actives_des_brigades(brigade_ids))
    brigades_par_id = {brigade.pk: brigade for brigade in brigades}
    for affectation in affectations:
        # Même brigade, même instance déjà mise en cache ci-dessus — jamais
        # une seconde copie non préchargée de `Brigade.session`.
        affectation.brigade = brigades_par_id[affectation.brigade_id]
    return modules, brigades, evaluations, notes, affectations


def _grouper_evaluations(evaluations) -> dict:
    groupes: dict = {}
    for evaluation in evaluations:
        cle = (evaluation.element_referentiel_id, evaluation.type)
        groupes.setdefault(cle, []).append(evaluation)
    return groupes


def _a_une_evaluation(module, evaluations_par_module_type) -> bool:
    """M4 : un module sans AUCUNE évaluation (quel que soit le type) dans
    tout le périmètre de la session est ignoré de la moyenne générale."""
    return any(
        evaluations_par_module_type.get((module.pk, type_eval)) for type_eval, _ in _POIDS_PAR_TYPE
    )


def _evaluations_applicables(evaluations_du_type, session, brigade):
    """Celles qui concernent RÉELLEMENT ce stagiaire : rattachées à la
    session entière, ou à sa propre brigade — jamais celles d'une autre
    brigade de la même session."""
    return [
        evaluation
        for evaluation in evaluations_du_type
        if evaluation.session_id == session.pk or evaluation.brigade_id == brigade.pk
    ]


def _valeur_pour_le_calcul(note, evaluation):
    """M2/N6 : ramenée sur 20 ; une absence compte zéro ou exclut
    l'évaluation selon le paramètre BNF-13. `None` signifie exclue."""
    if not note.absent:
        return (note.valeur / evaluation.note_maximale) * VINGT
    if settings.TRAITEMENT_ABSENCE_NOTE == TRAITEMENT_ABSENCE_ZERO:
        return decimal.Decimal(0)
    return None


def _notes_du_type(module, type_eval, stagiaire, brigade, contexte):
    """Notes applicables à CE stagiaire pour un seul type d'évaluation d'un
    module — extrait de `_note_module` pour rester sous 40 lignes. Rend
    `(valeurs_sur_20, details, manquante)` ; `details` alimente l'écran
    US-EVAL-12, jamais un second parcours des notes."""
    applicables = _evaluations_applicables(
        contexte.evaluations_par_module_type.get((module.pk, type_eval), []),
        contexte.session,
        brigade,
    )
    valeurs, details, manquante = [], [], False
    for evaluation in applicables:
        note = contexte.notes.get((evaluation.pk, stagiaire.pk))
        if note is None:
            manquante = True
            continue
        valeur = _valeur_pour_le_calcul(note, evaluation)
        details.append(NoteDetail(evaluation=evaluation, valeur=valeur, absent=note.absent))
        if valeur is not None:
            valeurs.append(valeur)
    return valeurs, details, manquante


def _note_module(module, stagiaire, brigade, contexte):
    """M3 : moyenne simple par type, puis moyenne des deux pondérée par les
    poids du module — un type sans évaluation APPLICABLE est retiré du
    calcul et son poids avec lui. Rend `(DetailModule, manquante)` ;
    `manquante=True` bloque le stagiaire entier (M5, RG-59 bis), pas
    seulement ce module."""
    manquante = False
    moyennes_par_type = {}
    notes_par_type = {TypeEvaluation.FORMATIVE: [], TypeEvaluation.CERTIFICATIVE: []}
    for type_eval, nom_poids in _POIDS_PAR_TYPE:
        valeurs, details, manquante_type = _notes_du_type(
            module, type_eval, stagiaire, brigade, contexte
        )
        notes_par_type[type_eval] = details
        manquante = manquante or manquante_type
        if valeurs:
            moyennes_par_type[type_eval] = (sum(valeurs) / len(valeurs), getattr(module, nom_poids))
    note_module = None
    if not manquante and moyennes_par_type:
        total_poids = sum(poids for _, poids in moyennes_par_type.values())
        if total_poids != 0:
            note_module = (
                sum(moy * poids for moy, poids in moyennes_par_type.values()) / total_poids
            )
    detail = DetailModule(
        module=module,
        notes_formatives=notes_par_type[TypeEvaluation.FORMATIVE],
        notes_certificatives=notes_par_type[TypeEvaluation.CERTIFICATIVE],
        poids_formatif=module.poids_formatif,
        poids_certificatif=module.poids_certificatif,
        note_module=note_module,
        coefficient=module.coefficient,
    )
    return detail, manquante


def _resultat_stagiaire(stagiaire, brigade, modules_avec_evaluation, contexte):
    """M4/M5, RG-59 bis : moyenne générale pondérée par les coefficients des modules —
    une seule note manquante, sur un seul module, bloque la moyenne entière
    du stagiaire ; les modules sans évaluation applicable à CE stagiaire
    (brigade différente) sont silencieusement écartés, pas signalés : ce
    n'est pas un manquant, le module ne le concerne simplement pas. Rend
    aussi le détail par module (US-EVAL-12) — ignoré par `calculer`, utilisé
    par `detailler`, jamais recalculé séparément."""
    termes = []
    manquants = []
    details = []
    for module in modules_avec_evaluation:
        detail, manquante = _note_module(module, stagiaire, brigade, contexte)
        if manquante:
            manquants.append(NoteManquante(module=module, brigade=brigade, stagiaire=stagiaire))
            continue
        if detail.note_module is not None:
            termes.append((detail.note_module, module.coefficient))
            details.append(detail)
    if manquants:
        return None, manquants, []
    if not termes:
        return None, [], []
    total_coefficient = sum(coefficient for _, coefficient in termes)
    moyenne = sum(note * coefficient for note, coefficient in termes) / total_coefficient
    return moyenne.quantize(DEUX_DECIMALES), [], details


def _classer(paires) -> dict:
    """M6/M7 : classement de compétition sur la moyenne déjà arrondie à
    deux décimales — deux ex aequo partagent le même rang, le suivant
    prend le rang augmenté du nombre d'ex aequo (1, 2, 2, 4). Ordre
    alphabétique au sein d'un groupe d'ex aequo (tri stable)."""
    tries = sorted(paires, key=lambda paire: (-paire[1], str(paire[0])))
    rangs: dict = {}
    rang_courant = 1
    indice = 0
    while indice < len(tries):
        meme_moyenne = [paire for paire in tries[indice:] if paire[1] == tries[indice][1]]
        for stagiaire, _ in meme_moyenne:
            rangs[stagiaire.pk] = rang_courant
        rang_courant += len(meme_moyenne)
        indice += len(meme_moyenne)
    return rangs


def _classer_session_et_brigades(resultats_bruts, brigades) -> dict:
    """M6/M7 : un classement sur l'ensemble, un second par brigade —
    factorisé, `calculer` et `calculer_evaluation` partagent cette forme."""
    rangs_session = _classer([(s, v) for s, _, v in resultats_bruts])
    rangs: dict = {}
    for brigade in brigades:
        de_la_brigade = [(s, v) for s, b, v in resultats_bruts if b.pk == brigade.pk]
        rangs_brigade = _classer(de_la_brigade)
        for stagiaire, _ in de_la_brigade:
            rangs[stagiaire.pk] = (rangs_session[stagiaire.pk], rangs_brigade[stagiaire.pk])
    return rangs


def _perimetre_evaluation(evaluation, brigades, affectations):
    """RG-52 : le périmètre d'une évaluation est une session ou une
    brigade, jamais les deux — restreint le classement et les affectations
    considérées à ce seul périmètre, pas à toute la session."""
    if evaluation.brigade_id is None:
        return brigades, affectations
    brigades_perimetre = [brigade for brigade in brigades if brigade.pk == evaluation.brigade_id]
    affectations_perimetre = [
        affectation
        for affectation in affectations
        if affectation.brigade_id == evaluation.brigade_id
    ]
    return brigades_perimetre, affectations_perimetre


def _resultat_evaluation_brut(evaluation, affectation, notes):
    """Une affectation -> `(stagiaire, brigade, valeur_ou_None, absent)` si
    une note existe pour CETTE évaluation, ou un `NoteManquante` si elle
    n'a même pas été saisie — jamais les deux (M5, RG-59 bis). `valeur` est
    `None` quand l'absence est exclue du calcul (N6) : le stagiaire reste
    affiché, sans valeur ni rang."""
    note = notes.get((evaluation.pk, affectation.stagiaire_id))
    if note is None:
        return None, NoteManquante(
            module=evaluation.element_referentiel,
            brigade=affectation.brigade,
            stagiaire=affectation.stagiaire,
        )
    valeur = _valeur_pour_le_calcul(note, evaluation)
    if valeur is not None:
        valeur = valeur.quantize(DEUX_DECIMALES)
    resultat = (affectation.stagiaire, affectation.brigade, valeur, note.absent)
    return resultat, None
