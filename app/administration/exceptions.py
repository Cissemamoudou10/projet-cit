"""Hiérarchie d'erreurs propre à `administration`, dérivée de la racine
partagée — voir .claude/rules/python.md.
"""

from noyau.exceptions import ErreurValidation


class ErreurIdentifiantExistant(ErreurValidation):
    """L'identifiant demandé est déjà attribué à un autre compte — RG-01,
    critère 4. Levée depuis la contrainte d'unicité en base, jamais depuis
    un contrôle préalable : entre la vérification et l'écriture, un autre
    administrateur peut avoir créé le même compte.
    """
