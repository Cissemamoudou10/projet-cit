"""Traitement d'une indisponibilité déclarée — US-PLAN-09 (prompt 42,
partie 3, I1 à I5).

I1 : remplacer, substituer et déprogrammer sont des opérations d'US-PLAN-05
(`ServiceEcritureSeance.modifier_seance`/`supprimer_seance`) — aucune
nouvelle voie d'écriture, ce module n'instancie jamais `Seance` ni
`LigneProgramme`. La seule règle propre à cette story est le lot (I5, C5) :
chaque séance du lot passe individuellement la garde et les contraintes,
dans une seule transaction, tout ou rien.
"""

from django.db import transaction

from noyau.exceptions import ErreurMetier, ErreurValidation
from planification.services.ecriture import ServiceEcritureSeance

MESSAGE_LOT_VIDE = "Choisissez au moins une séance à traiter en lot."
MESSAGE_LOT_MATIERES_MELANGEES = (
    "Le traitement en lot ne réunit que des séances de la même matière (C5) : "
    "traitez les autres séparément."
)


def _verifier_lot(seances):
    if not seances:
        raise ErreurValidation(MESSAGE_LOT_VIDE)
    matieres = {seance.element_referentiel.matiere_id for seance in seances}
    if len(matieres) > 1:
        raise ErreurValidation(MESSAGE_LOT_MATIERES_MELANGEES)


def traiter_lot_remplacement(agissant, seances, instructeur, avenant=None, confirmee=False):
    """C5 : même remplaçant pour toutes les séances du lot, qui ne réunit
    que des séances de la même matière. I5 : si une seule échoue — garde
    ou contraintes —, rien n'est écrit ; le refus nomme la séance (le
    message de la contrainte nomme déjà la règle en cause)."""
    _verifier_lot(seances)
    with transaction.atomic():
        for seance in seances:
            try:
                ServiceEcritureSeance.modifier_seance(
                    agissant,
                    seance,
                    {"instructeur": instructeur},
                    avenant=avenant,
                    confirmee=confirmee,
                )
            except ErreurMetier as erreur:
                raise ErreurValidation(f"{seance} : {erreur}") from erreur
    return seances
