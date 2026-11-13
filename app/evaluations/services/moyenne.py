"""`ServiceMoyenne` — US-EVAL-06, RG-56, RG-57, RG-59 bis (D-276), prompt 46 ;
US-EVAL-12, prompt 64 (détail par module).

M1 : rien n'est stocké — moyennes et rangs se recalculent à chaque appel, à
partir des notes déjà saisies (US-EVAL-05) et des poids du référentiel
(coefficient, poids_formatif, poids_certificatif — US-REF-03, P-45). Le
procès-verbal (US-EVAL-07) fige un résultat, ce service ne le fait jamais.

M8 : même confidentialité que les notes (BNF-02, D-219 cas a) — visibilité
réservée à `evaluations_ecriture`, le backlog ne nomme que la cellule
examens, aucune lecture séparée.

Le moteur de calcul par module (`_note_module`, `_resultat_stagiaire`, etc.)
vit dans `evaluations.services.calcul_moyenne`, séparé pour rester sous 400
lignes (`.claude/rules/python.md`) — ce fichier ne porte que l'habilitation,
le journal et l'assemblage des rapports.

Aucune règle métier dans les vues ni les formulaires — voir
.claude/rules/services.md.
"""

import dataclasses
import decimal

from administration.habilitations import verifier_habilitation
from administration.models import TypeAction
from administration.services.journal import DonneesEntreeJournal, ServiceJournal
from evaluations.services.calcul_moyenne import (
    ContexteCalcul,
    _a_une_evaluation,
    _classer_session_et_brigades,
    _donnees_session,
    _grouper_evaluations,
    _perimetre_evaluation,
    _resultat_evaluation_brut,
    _resultat_stagiaire,
)
from noyau.exceptions import ErreurIntrouvable

PERMISSION_ECRITURE = "noyau.evaluations_ecriture"


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


@dataclasses.dataclass(frozen=True)
class DetailMoyenneStagiaire:
    stagiaire: object
    brigade: object
    modules: list
    moyenne: decimal.Decimal | None
    rang_session: int | None
    rang_brigade: int | None


@dataclasses.dataclass(frozen=True)
class ResultatEvaluation:
    """US-EVAL-07, V1 (D-277 révise le choix pris seul au prompt 46) : le
    « procès-verbal d'une évaluation » rapporte CETTE évaluation seule
    (CU-P6-07 A1), jamais la moyenne du module qui agrégerait d'autres
    évaluations hors du périmètre du document. `note` vaut `None` quand
    l'absence est exclue du calcul (`TRAITEMENT_ABSENCE_NOTE`, N6) : le
    stagiaire est alors affiché absent, sans note ni rang."""

    stagiaire: object
    brigade: object
    note: decimal.Decimal | None
    absent: bool
    rang_session: int | None
    rang_brigade: int | None


@dataclasses.dataclass(frozen=True)
class RapportEvaluation:
    resultats: list
    manquants: list


def evaluations_de_la_session(session) -> list:
    """US-EVAL-07, V3 : toutes les évaluations du périmètre de la session
    (verrouillage d'un procès-verbal de fin de formation) — même
    résolution que `calculer`, sans refaire la requête ici une seconde
    fois."""
    _, _, evaluations, _, _ = _donnees_session(session)
    return evaluations


def _journaliser_consultation_moyenne(agissant, stagiaire):
    """US-EVAL-12 : même patron que `ServiceNote._journaliser_consultation`
    — donnée sensible (M8), chaque consultation du détail journalisée."""
    ServiceJournal.enregistrer_detaillee(
        DonneesEntreeJournal(
            type_action=TypeAction.CONSULTATION_MOYENNES,
            identifiant_saisi=getattr(agissant, "username", ""),
            auteur=agissant,
            objet_type="stagiaire",
            objet_identifiant=str(stagiaire.pk),
        )
    )


def _resultats_et_detail_stagiaire(stagiaire_vise, affectations, modules_avec_evaluation, contexte):
    """US-EVAL-12 : un seul passage sur toutes les affectations — sert à la
    fois le classement (RG-57) et le détail du stagiaire visé, jamais un
    second parcours des notes."""
    resultats_bruts = []
    modules_du_stagiaire = []
    moyenne_stagiaire = None
    for affectation in affectations:
        moyenne, _, details = _resultat_stagiaire(
            affectation.stagiaire, affectation.brigade, modules_avec_evaluation, contexte
        )
        if moyenne is not None:
            resultats_bruts.append((affectation.stagiaire, affectation.brigade, moyenne))
        if affectation.stagiaire_id == stagiaire_vise.pk:
            modules_du_stagiaire = details
            moyenne_stagiaire = moyenne
    return resultats_bruts, modules_du_stagiaire, moyenne_stagiaire


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
            moyenne, manquants_stagiaire, _ = _resultat_stagiaire(
                affectation.stagiaire, affectation.brigade, modules_avec_evaluation, contexte
            )
            manquants.extend(manquants_stagiaire)
            if moyenne is not None:
                resultats_bruts.append((affectation.stagiaire, affectation.brigade, moyenne))

        rangs = _classer_session_et_brigades(resultats_bruts, brigades)
        resultats = [
            ResultatStagiaire(
                stagiaire=stagiaire,
                brigade=brigade,
                moyenne=moyenne,
                rang_session=rangs[stagiaire.pk][0],
                rang_brigade=rangs[stagiaire.pk][1],
            )
            for stagiaire, brigade, moyenne in resultats_bruts
        ]
        return RapportMoyennes(
            resultats=resultats, manquants=manquants, modules_ignores=modules_ignores
        )

    @staticmethod
    def calculer_evaluation(agissant, session, evaluation) -> RapportEvaluation:
        """US-EVAL-07, V1 (D-277) : résultat d'une seule évaluation —
        CU-P6-07 A1 impose que le « procès-verbal d'une évaluation » ne
        rapporte que celle-ci, jamais la moyenne du module qui agrégerait
        d'autres évaluations hors de son périmètre (RG-52)."""
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        _, brigades, _, notes, affectations = _donnees_session(session)
        brigades_perimetre, affectations_perimetre = _perimetre_evaluation(
            evaluation, brigades, affectations
        )

        resultats_bruts = []
        manquants = []
        for affectation in affectations_perimetre:
            resultat, manquant = _resultat_evaluation_brut(evaluation, affectation, notes)
            if manquant is not None:
                manquants.append(manquant)
            else:
                resultats_bruts.append(resultat)

        classables = [(s, b, v) for s, b, v, _ in resultats_bruts if v is not None]
        rangs = _classer_session_et_brigades(classables, brigades_perimetre)
        resultats = [
            ResultatEvaluation(
                stagiaire=stagiaire,
                brigade=brigade,
                note=valeur,
                absent=absent,
                rang_session=rangs.get(stagiaire.pk, (None, None))[0],
                rang_brigade=rangs.get(stagiaire.pk, (None, None))[1],
            )
            for stagiaire, brigade, valeur, absent in resultats_bruts
        ]
        return RapportEvaluation(resultats=resultats, manquants=manquants)

    @staticmethod
    def detailler(agissant, session, stagiaire) -> DetailMoyenneStagiaire:
        """US-EVAL-12 : détail par module d'UN stagiaire — réutilise
        `_note_module`/`_resultat_stagiaire` (`calcul_moyenne.py`), jamais
        une seconde implantation du calcul (même moteur que `calculer`,
        test d'architecture dédié)."""
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        modules, brigades, evaluations, notes, affectations = _donnees_session(session)
        evaluations_par_module_type = _grouper_evaluations(evaluations)
        modules_avec_evaluation = [
            module for module in modules if _a_une_evaluation(module, evaluations_par_module_type)
        ]
        contexte = ContexteCalcul(
            session=session, evaluations_par_module_type=evaluations_par_module_type, notes=notes
        )
        try:
            affectation_visee = next(a for a in affectations if a.stagiaire_id == stagiaire.pk)
        except StopIteration as erreur:
            raise ErreurIntrouvable(
                "Ce stagiaire n'est affecté à aucune brigade de cette session."
            ) from erreur

        resultats_bruts, modules_du_stagiaire, moyenne_stagiaire = _resultats_et_detail_stagiaire(
            stagiaire, affectations, modules_avec_evaluation, contexte
        )
        rangs = _classer_session_et_brigades(resultats_bruts, brigades)
        rang_session, rang_brigade = rangs.get(stagiaire.pk, (None, None))
        _journaliser_consultation_moyenne(agissant, stagiaire)
        return DetailMoyenneStagiaire(
            stagiaire=stagiaire,
            brigade=affectation_visee.brigade,
            modules=modules_du_stagiaire,
            moyenne=moyenne_stagiaire,
            rang_session=rang_session,
            rang_brigade=rang_brigade,
        )
