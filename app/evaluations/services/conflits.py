"""Conflits d'une organisation d'épreuve — RG-53 (P6 → P5), A5 et A9, Prompt 38.

Lit les sources, ne recalcule aucune règle : indisponibilités (`ressources`),
séances (`planification`), autres épreuves le même jour (`evaluations`). Nombre
de requêtes constant, quel que soit le nombre de lieux et de surveillants.
"""

from evaluations.models import OrganisationEpreuve, Surveillance
from noyau.intervalles import instant_de, se_recouvrent
from planification.selectors import seances_occupant_instructeurs, seances_occupant_lieux
from ressources.selectors import indisponibilites_des_instructeurs, indisponibilites_des_lieux


def creneau_de(evaluation):
    return (
        instant_de(evaluation.date, evaluation.heure_debut),
        instant_de(evaluation.date, evaluation.heure_fin),
    )


def _messages_indisponibilites(indisponibilites, attribut):
    return [
        f"{getattr(indispo, attribut)} est indisponible du {indispo.debut:%d/%m %H:%M} "
        f"au {indispo.fin:%d/%m %H:%M} ({indispo.motif})."
        for liste in indisponibilites.values()
        for indispo in liste
    ]


def _messages_seances(seances, attribut):
    return [
        f"{getattr(seance, attribut)} est occupé par la séance de "
        f"{seance.element_referentiel.matiere} le {seance.debut:%d/%m %H:%M}–{seance.fin:%H:%M}."
        for liste in seances.values()
        for seance in liste
    ]


def _conflits_sources(lieux, instructeurs, debut, fin):
    return (
        _messages_indisponibilites(indisponibilites_des_lieux(lieux, debut, fin), "lieu")
        + _messages_indisponibilites(
            indisponibilites_des_instructeurs(instructeurs, debut, fin), "instructeur"
        )
        + _messages_seances(seances_occupant_lieux(lieux, debut, fin), "lieu")
        + _messages_seances(seances_occupant_instructeurs(instructeurs, debut, fin), "instructeur")
    )


def _conflits_autres_epreuves(evaluation, lieux, instructeurs, debut, fin):
    """Autres épreuves le même jour : une requête pour leurs organisations, une
    pour leurs surveillances, recouvrement d'instants en mémoire."""
    autres_organisations = (
        OrganisationEpreuve.objects.filter(
            evaluation__date=evaluation.date, evaluation__heure_debut__isnull=False
        )
        .exclude(evaluation=evaluation)
        .select_related("evaluation__element_referentiel__matiere", "lieu")
    )
    autres_surveillances = (
        Surveillance.objects.filter(
            organisation__evaluation__date=evaluation.date,
            organisation__evaluation__heure_debut__isnull=False,
        )
        .exclude(organisation__evaluation=evaluation)
        .select_related("organisation__evaluation__element_referentiel__matiere", "instructeur")
    )
    constats = []
    for organisation in autres_organisations:
        autre = organisation.evaluation
        if organisation.lieu_id not in lieux:
            continue
        if not se_recouvrent(debut, fin, *creneau_de(autre)):
            continue
        constats.append(f"{organisation.lieu} est déjà pris par « {autre} ».")
    for surveillance in autres_surveillances:
        autre = surveillance.organisation.evaluation
        if surveillance.instructeur_id not in instructeurs:
            continue
        if not se_recouvrent(debut, fin, *creneau_de(autre)):
            continue
        constats.append(f"{surveillance.instructeur} surveille déjà « {autre} ».")
    return constats


def conflits(evaluation, lieux, instructeurs) -> list:
    """Messages de conflit pour des lieux et des instructeurs visés sur le créneau
    de `evaluation`. Vide : rien ne s'oppose. Ne lit pas les organisations de
    l'épreuve elle-même : c'est à l'appelant de passer ce qu'il veut vérifier."""
    if evaluation.heure_debut is None:
        return []
    lieux, instructeurs = set(lieux), set(instructeurs)
    debut, fin = creneau_de(evaluation)
    return _conflits_sources(lieux, instructeurs, debut, fin) + _conflits_autres_epreuves(
        evaluation, lieux, instructeurs, debut, fin
    )


def conflits_de_l_epreuve(evaluation) -> list:
    """A9 : conflits de toutes les organisations et surveillances de l'épreuve."""
    lieux = set(
        OrganisationEpreuve.objects.filter(
            evaluation=evaluation, lieu_id__isnull=False
        ).values_list("lieu_id", flat=True)
    )
    instructeurs = set(
        Surveillance.objects.filter(
            organisation__evaluation=evaluation, instructeur_id__isnull=False
        ).values_list("instructeur_id", flat=True)
    )
    return conflits(evaluation, lieux, instructeurs)
