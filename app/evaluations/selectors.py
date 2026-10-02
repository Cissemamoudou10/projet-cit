"""Lectures complexes séparées des services — .claude/rules/python.md.

`seances_de_controle_parmi` est installée comme fournisseur de
`noyau.services.parametres.ResolveurSeancesDeControle` au démarrage de
l'application (`evaluations.apps.EvaluationsConfig.ready`) — A9, Prompt 35.
`jours_d_examen` est installée de même pour `ResolveurJoursExamen` — A2,
Prompt 36.
"""

from organisation.models import Brigade

from evaluations.models import Evaluation, TypeEvaluation


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
