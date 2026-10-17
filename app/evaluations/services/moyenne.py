"""`ServiceMoyenne` — US-EVAL-06, RG-56, RG-57, prompt 46.

M1 : rien n'est stocké — moyennes et rangs se recalculent à chaque appel, à
partir des notes déjà saisies (US-EVAL-05) et des poids du référentiel
(coefficient, poids_formatif, poids_certificatif — US-REF-03, P-45). Le
procès-verbal (US-EVAL-07) fige un résultat, ce service ne le fait jamais.

M8 : même confidentialité que les notes (BNF-02, D-219 cas a) — visibilité
réservée à `evaluations_ecriture`, le backlog ne nomme que la cellule
examens, aucune lecture séparée.

Aucune règle métier dans les vues ni les formulaires — voir
.claude/rules/services.md.
"""

import dataclasses
import decimal

from django.conf import settings
from django.db.models import Q

from administration.habilitations import verifier_habilitation
from evaluations.constantes import TRAITEMENT_ABSENCE_ZERO
from evaluations.models import Evaluation, Note, TypeEvaluation
from organisation.selectors import affectations_actives_des_brigades
from referentiel.models import ElementReferentiel

PERMISSION_ECRITURE = "noyau.evaluations_ecriture"

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
    """M5 : une entrée par (module, stagiaire) — jamais une par
    évaluation en cause, quel que soit leur nombre."""

    module: object
    brigade: object
    stagiaire: object


@dataclasses.dataclass(frozen=True)
class ResultatStagiaire:
    stagiaire: object
    brigade: object
    moyenne: decimal.Decimal
    rang_session: int
    rang_brigade: int


@dataclasses.dataclass(frozen=True)
class RapportMoyennes:
    resultats: list
    manquants: list
    modules_ignores: list


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


def _note_module(module, stagiaire, brigade, contexte):
    """M3 : moyenne simple par type, puis moyenne des deux pondérée par les
    poids du module — un type sans évaluation APPLICABLE est retiré du
    calcul et son poids avec lui. Rend `(note_ou_None, manquante)` ;
    `manquante=True` bloque le stagiaire entier (M5), pas seulement ce
    module."""
    manquante = False
    moyennes_par_type = {}
    for type_eval, nom_poids in _POIDS_PAR_TYPE:
        applicables = _evaluations_applicables(
            contexte.evaluations_par_module_type.get((module.pk, type_eval), []),
            contexte.session,
            brigade,
        )
        if not applicables:
            continue
        valeurs = []
        for evaluation in applicables:
            note = contexte.notes.get((evaluation.pk, stagiaire.pk))
            if note is None:
                manquante = True
                continue
            valeur = _valeur_pour_le_calcul(note, evaluation)
            if valeur is not None:
                valeurs.append(valeur)
        if valeurs:
            moyennes_par_type[type_eval] = (sum(valeurs) / len(valeurs), getattr(module, nom_poids))
    if manquante:
        return None, True
    if not moyennes_par_type:
        return None, False
    total_poids = sum(poids for _, poids in moyennes_par_type.values())
    if total_poids == 0:
        return None, False
    note_ponderee = sum(moy * poids for moy, poids in moyennes_par_type.values()) / total_poids
    return note_ponderee, False


def _resultat_stagiaire(stagiaire, brigade, modules_avec_evaluation, contexte):
    """M4/M5 : moyenne générale pondérée par les coefficients des modules —
    une seule note manquante, sur un seul module, bloque la moyenne entière
    du stagiaire ; les modules sans évaluation applicable à CE stagiaire
    (brigade différente) sont silencieusement écartés, pas signalés : ce
    n'est pas un manquant, le module ne le concerne simplement pas."""
    termes = []
    manquants = []
    for module in modules_avec_evaluation:
        note_module, manquante = _note_module(module, stagiaire, brigade, contexte)
        if manquante:
            manquants.append(NoteManquante(module=module, brigade=brigade, stagiaire=stagiaire))
            continue
        if note_module is not None:
            termes.append((note_module, module.coefficient))
    if manquants:
        return None, manquants
    if not termes:
        return None, []
    total_coefficient = sum(coefficient for _, coefficient in termes)
    moyenne = sum(note * coefficient for note, coefficient in termes) / total_coefficient
    return moyenne.quantize(DEUX_DECIMALES), []


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


class ServiceMoyenne:
    DOMAINE = "evaluations"
    PERMISSION_ECRITURE = PERMISSION_ECRITURE

    @staticmethod
    def calculer(agissant, session) -> RapportMoyennes:
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        modules, brigades, evaluations, notes, affectations = _donnees_session(session)
        evaluations_par_module_type = _grouper_evaluations(evaluations)
        modules_avec_evaluation = [
            module for module in modules if _a_une_evaluation(module, evaluations_par_module_type)
        ]
        modules_ignores = [module for module in modules if module not in modules_avec_evaluation]
        contexte = ContexteCalcul(
            session=session, evaluations_par_module_type=evaluations_par_module_type, notes=notes
        )

        resultats_bruts = []
        manquants = []
        for affectation in affectations:
            moyenne, manquants_stagiaire = _resultat_stagiaire(
                affectation.stagiaire, affectation.brigade, modules_avec_evaluation, contexte
            )
            manquants.extend(manquants_stagiaire)
            if moyenne is not None:
                resultats_bruts.append((affectation.stagiaire, affectation.brigade, moyenne))

        rangs_session = _classer([(s, m) for s, _, m in resultats_bruts])
        resultats = []
        for brigade in brigades:
            de_la_brigade = [(s, m) for s, b, m in resultats_bruts if b.pk == brigade.pk]
            rangs_brigade = _classer(de_la_brigade)
            for stagiaire, moyenne in de_la_brigade:
                resultats.append(
                    ResultatStagiaire(
                        stagiaire=stagiaire,
                        brigade=brigade,
                        moyenne=moyenne,
                        rang_session=rangs_session[stagiaire.pk],
                        rang_brigade=rangs_brigade[stagiaire.pk],
                    )
                )
        return RapportMoyennes(
            resultats=resultats, manquants=manquants, modules_ignores=modules_ignores
        )
