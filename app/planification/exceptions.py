"""Hiérarchie des erreurs métier de `planification` — .claude/rules/python.md.

Les deux exceptions ci-dessous ne signalent pas un refus d'une candidate
(ça, c'est `ErreurValidation`, levée par `ServiceEcritureSeance`) mais une
IMPOSSIBILITÉ DE LANCER LA GÉNÉRATION ELLE-MÊME — § 6, Prompt 31, E1 et E6.
Aucun `ProgrammeHebdomadaire` n'est créé dans les deux cas.
"""

from noyau.exceptions import ErreurMetier


class ErreurPlanification(ErreurMetier):
    """Racine des erreurs propres à `planification`."""


class TransitionProgrammeRefusee(ErreurPlanification):
    """Transition du circuit du programme refusée (ETA-01) : le message nomme
    la règle et, quand elle existe, la marche à suivre."""


class AucuneGrilleActive(ErreurPlanification):
    """E6 — aucune grille horaire active ; renvoi vers sa gestion."""


class SemaineEntierementBloquee(ErreurPlanification):
    """E1 — aucun créneau ouvert pour les brigades sélectionnées sur cette
    semaine, toutes périodes bloquantes confondues."""


class SuppressionProgrammeRefusee(ErreurPlanification):
    """Évolution du prompt 53, Temps 2 (S1 à S3) : suppression d'un
    programme en brouillon refusée — permission manquante, histoire de
    circuit (soumission, validation, rejet) ou séance de contrôle portée.
    Le message nomme la cause et, quand il existe, le geste de rattrapage."""
