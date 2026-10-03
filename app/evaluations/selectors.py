"""Lectures complexes séparées des services — .claude/rules/python.md.

`seances_de_controle_parmi` est installée comme fournisseur de
`noyau.services.parametres.ResolveurSeancesDeControle` au démarrage de
l'application (`evaluations.apps.EvaluationsConfig.ready`) — A9, Prompt 35.
`jours_d_examen` est installée de même pour `ResolveurJoursExamen` — A2,
Prompt 36.
"""

from django.db.models import Exists, OuterRef

from evaluations.models import Evaluation, Sujet, TypeEvaluation
from organisation.models import Brigade


def seances_de_controle_parmi(ids_seances) -> frozenset:
    """Une seule requête pour tout l'ensemble reçu (E2, Prompt 35) : jamais
    une par séance affichée."""
    if not ids_seances:
        return frozenset()
    return frozenset(
        Evaluation.objects.filter(seance_id__in=ids_seances).values_list("seance_id", flat=True)
    )


def jours_d_examen(debut, fin) -> list[dict]:
    """A2/A4, Prompt 36 : deux requêtes, bornées, jamais une par évaluation
    ni une par brigade — le périmètre session se résout en une seule
    requête groupée, au moment de l'appel (A4 : une brigade constituée
    après la saisie de la date est fermée elle aussi, puisqu'elle entre
    dans cette requête comme les autres)."""
    lignes = list(
        Evaluation.objects.filter(
            type=TypeEvaluation.CERTIFICATIVE, date__gte=debut, date__lt=fin
        ).values_list("date", "brigade_id", "session_id", "element_referentiel__matiere__intitule")
    )
    sessions_visees = {session_id for _, _, session_id, _ in lignes if session_id}
    brigades_par_session: dict = {}
    if sessions_visees:
        for brigade_id, session_id in Brigade.objects.filter(
            session_id__in=sessions_visees
        ).values_list("pk", "session_id"):
            brigades_par_session.setdefault(session_id, set()).add(brigade_id)
    resultat = []
    for jour, brigade_id, session_id, matiere in lignes:
        brigades = brigades_par_session.get(session_id, set()) if session_id else {brigade_id}
        resultat.append(
            {"jour": jour, "brigades": brigades, "libelle": f"Examen final — {matiere}"}
        )
    return resultat


def resume_sujets(evaluation) -> dict:
    """A5 : résumé NON sensible pour le détail de l'évaluation — ni
    référence, ni rang du retenu. Une requête, aucun passage par
    `ServiceSujet.consulter` (réservé à l'écran dédié, qui journalise RG-51 :
    ce résumé n'est pas cet écran, A6)."""
    sujets = list(evaluation.sujets.values_list("retenu", flat=True))
    return {"nombre": len(sujets), "a_un_retenu": any(sujets)}


def evaluations_non_pretes(ids_evaluations) -> frozenset:
    """A11, Prompt 37 : badge « non prête » — requête UNIQUE pour tout
    l'ensemble reçu (deux sous-requêtes corrélées, `Exists`, jamais un aller-
    retour par évaluation affichée). Certificative sans sujet retenu, ou
    formative sans aucun sujet."""
    if not ids_evaluations:
        return frozenset()
    sujets = Sujet.objects.filter(evaluation=OuterRef("pk"))
    lignes = (
        Evaluation.objects.filter(pk__in=ids_evaluations)
        .annotate(a_sujet=Exists(sujets), a_retenu=Exists(sujets.filter(retenu=True)))
        .values_list("pk", "type", "a_sujet", "a_retenu")
    )
    return frozenset(
        pk
        for pk, type_, a_sujet, a_retenu in lignes
        if (type_ == TypeEvaluation.CERTIFICATIVE and not a_retenu)
        or (type_ == TypeEvaluation.FORMATIVE and not a_sujet)
    )
