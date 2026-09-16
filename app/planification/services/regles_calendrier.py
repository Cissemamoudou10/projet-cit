"""RG-38 — créneau ouvert : aucune période bloquante du calendrier dont la
portée couvre la brigade. Les périodes INFORMATIVES n'entrent jamais dans
`contexte.periodes_bloquantes` (filtrées au chargement, § 7, Prompt 29) :
F5 est donc satisfait par construction, sans code dédié ici.
"""

from planification.services.regles_instructeur import _se_recouvrent
from planification.services.violations import violation


def _portee_couvre(entree, brigade):
    if entree["centre_entier"]:
        return True
    return brigade.pk in entree["brigades"] or brigade.session_id in entree["sessions"]


def verifier_rg38(candidate, contexte):
    violations = []
    for entree in contexte.periodes_bloquantes:
        periode = entree["periode"]
        if not _se_recouvrent(candidate.debut, candidate.fin, periode.debut, periode.fin):
            continue
        if not _portee_couvre(entree, candidate.brigade):
            continue
        violations.append(
            violation(
                "RG-38",
                f"La période « {periode.intitule} » ({periode.debut:%d/%m} au "
                f"{periode.fin:%d/%m}) bloque {candidate.brigade} sur ce créneau.",
            )
        )
    return violations
