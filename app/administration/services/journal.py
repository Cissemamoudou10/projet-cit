"""Journal des actions sensibles — RG-26.

Un service ne connaît pas la requête HTTP — voir .claude/rules/services.md.
"""

from django.db import transaction

from administration.models import EntreeJournal
from noyau.services.base import ServiceBase


class ServiceJournal:
    """Aucune permission vérifiée ici : le journal est écrit par les autres
    services, jamais consulté directement par un utilisateur dans cette
    story. `DOMAINE` reste déclaré (§ 2.4) — l'app propriétaire est
    `administration`.
    """

    DOMAINE = "administration"

    @staticmethod
    @transaction.atomic
    def enregistrer(type_action, identifiant_saisi, detail="", auteur=None, cible=""):
        """Aucun utilisateur authentifié ne « crée » techniquement une
        entrée de journal : `cree_par` reste vide, `auteur` porte le compte
        concerné — voir la docstring de `EntreeJournal`.
        """
        entree = EntreeJournal(
            type_action=type_action,
            cible=cible,
            auteur=auteur,
            identifiant_saisi=identifiant_saisi,
            detail=detail,
        )
        return ServiceBase.creer(entree, utilisateur=None)
