"""Hiérarchie unique des erreurs métier.

Les services lèvent ces erreurs ; ils ne retournent jamais d'objet HTTP et
n'en importent aucun — c'est la couche présentation qui traduit une erreur
métier en réponse.
"""


class ErreurMetier(Exception):
    """Racine de toute erreur métier du projet."""


class ErreurValidation(ErreurMetier):
    """Une donnée ou une combinaison de données viole une règle métier."""


class ErreurHabilitation(ErreurMetier):
    """L'utilisateur n'a pas le droit d'effectuer l'action demandée."""


class ErreurIntrouvable(ErreurMetier):
    """L'objet métier visé n'existe pas."""


class ErreurEtatInvalide(ErreurMetier):
    """L'action demandée ne s'applique pas à l'état courant de l'objet."""


class ErreurModificationConcurrente(ErreurMetier):
    """La donnée a changé depuis l'ouverture du formulaire — Prompt 05, § 2.2,
    E5 de la fiche générique de gestion. Le message porte l'auteur de la
    modification concurrente, pas seulement le constat du conflit.
    """


class ErreurAuthentification(ErreurMetier):
    """Identifiant inexistant ou mot de passe erroné — RG-01, CU-P1-01 E1.

    Un seul message pour les deux causes : ne jamais préciser laquelle des
    deux est en cause (critère 2).
    """


class ErreurCompteDesactive(ErreurMetier):
    """Le compte existe mais n'est pas actif — CU-P1-01 E2."""


class ErreurCompteVerrouille(ErreurMetier):
    """Le compte est temporairement verrouillé — RG-03, CU-P1-01 E3."""
