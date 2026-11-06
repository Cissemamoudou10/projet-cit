"""RG-05 — le référentiel appartient à la formation : aucune matière n'est
jamais rattachée à une brigade ni à une session, toutes les brigades d'une
session suivent le référentiel de la formation de cette session
(`docs/conception/11-cas-utilisation.md`).

Découverte en recette (RECETTE-01, A3, prompt 58) vérifiée seulement par le
filtrage des formulaires (confort d'écran, `forms_seance.py`/
`forms_indisponibilite.py`) — contournable par tout appel direct à
`ServiceEcritureSeance` (ajout manuel, regroupement en particulier,
jusqu'ici sans aucune protection, ni écran ni service). Déplacée ici
(D-309, supersède D-306) : septième — après RG-67 — règle hors de la série
RG-34 à RG-39, appliquée identiquement par les cinq chemins d'écriture."""

from planification.services.violations import violation


def verifier_rg05(candidate):
    """`session.formation_id` (jamais `session.formation`) : un accès direct
    à la clé étrangère, sans requête supplémentaire même si l'appelant n'a
    pas chargé `brigade__session__formation` — seul le message d'une
    violation, rare, paie le coût de l'objet complet."""
    session = candidate.brigade.session
    if candidate.element_referentiel.formation_id != session.formation_id:
        return [
            violation(
                "RG-05",
                f"{candidate.element_referentiel.matiere} appartient au référentiel de "
                f"{candidate.element_referentiel.formation}, pas à celui de la formation de "
                f"{candidate.brigade} ({session.formation}).",
            )
        ]
    return []
