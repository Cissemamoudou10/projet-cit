"""Hiérarchie des erreurs métier de `planification` — .claude/rules/python.md.

Les deux exceptions ci-dessous ne signalent pas un refus d'une candidate
(ça, c'est `ErreurValidation`, levée par `ServiceEcritureSeance`) mais une
IMPOSSIBILITÉ DE LANCER LA GÉNÉRATION ELLE-MÊME — § 6, Prompt 31, E1 et E6.
Aucun `ProgrammeHebdomadaire` n'est créé dans les deux cas.
"""

from noyau.exceptions import ErreurMetier


class ErreurPlanification(ErreurMetier):
    """Racine des erreurs propres à `planification`."""


class AucuneGrilleActive(ErreurPlanification):
    """E6 — aucune grille horaire active ; renvoi vers sa gestion."""


class SemaineEntierementBloquee(ErreurPlanification):
    """E1 — aucun créneau ouvert pour les brigades sélectionnées sur cette
    semaine, toutes périodes bloquantes confondues."""
