"""Hiérarchie d'erreurs propre à `administration`, dérivée de la racine
partagée — voir .claude/rules/python.md.
"""

from noyau.exceptions import ErreurIntrouvable, ErreurValidation


class ErreurIdentifiantExistant(ErreurValidation):
    """L'identifiant demandé est déjà attribué à un autre compte — RG-01,
    critère 4. Levée depuis la contrainte d'unicité en base, jamais depuis
    un contrôle préalable : entre la vérification et l'écriture, un autre
    administrateur peut avoir créé le même compte.
    """


class ErreurGabaritIntrouvable(ErreurIntrouvable):
    """Aucun `GabaritDocument` chargé pour le type demandé, ou la ressource
    statique qui porte les polices/la mise en page PDF est absente — US-SUI-06
    (prompt 45), `ServiceDocument.produire`.
    """
