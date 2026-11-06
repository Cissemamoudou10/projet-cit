"""RG-67 — une brigade ne peut pas avoir deux séances qui se chevauchent.

Découverte en recette (RECETTE-01, A10/A1/A6 b, prompt 58) : aucune règle
ne portait ce cas avant — RG-34 porte sur l'INSTRUCTEUR, RG-37 sur le LIEU,
aucune des deux sur la BRIGADE elle-même. Même patron que
`regles_instructeur.verifier_rg34` (fonctions pures, candidate + contexte +
lot en entrée, liste de violations en sortie, jamais d'écriture — voir
`planification.services.contraintes`).

Une séance regroupée occupe le créneau pour CHACUNE de ses brigades (une
ligne par brigade) : vérifié contre toutes les lignes de la séance, pas
seulement une brigade unique portée par la séance elle-même.
"""

from noyau.intervalles import se_recouvrent
from planification.services.violations import violation


def _rg67_conflits_existants(candidate, seances_existantes):
    violations = []
    for seance in seances_existantes:
        brigades_seance = {ligne.brigade_id for ligne in seance.lignes.all()}
        if candidate.brigade.pk not in brigades_seance:
            continue
        if not se_recouvrent(candidate.debut, candidate.fin, seance.debut, seance.fin):
            continue
        violations.append(
            violation(
                "RG-67",
                f"{candidate.brigade} a déjà une séance de "
                f"{seance.element_referentiel.matiere} le "
                f"{seance.debut:%d/%m %H:%M}–{seance.fin:%H:%M}.",
                origine="base",
            )
        )
    return violations


def _rg67_conflits_lot(candidate, lot_acceptees):
    violations = []
    for autre in lot_acceptees:
        if autre.brigade.pk != candidate.brigade.pk:
            continue
        if (
            candidate.cle_regroupement is not None
            and candidate.cle_regroupement == autre.cle_regroupement
        ):
            continue
        if not se_recouvrent(candidate.debut, candidate.fin, autre.debut, autre.fin):
            continue
        violations.append(
            violation(
                "RG-67",
                f"{candidate.brigade} est déjà retenue, dans ce même lot, pour "
                f"{autre.element_referentiel.matiere} le "
                f"{autre.debut:%d/%m %H:%M}–{autre.fin:%H:%M}.",
                origine="lot",
            )
        )
    return violations


def verifier_rg67(candidate, contexte, lot_acceptees):
    return _rg67_conflits_existants(
        candidate, contexte.seances_existantes
    ) + _rg67_conflits_lot(candidate, lot_acceptees)
