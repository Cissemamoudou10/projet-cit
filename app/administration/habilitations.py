"""Contrôle d'accès qui refuse et journalise — RG-02, RG-26.

Vit ici, pas dans `noyau` : journaliser un refus exige `ServiceJournal`, et
`noyau` ne dépend d'aucune application — voir docs/suivi/DECISIONS.md, D-09.
Toute application future (autorisée à dépendre d'`administration`) importe
d'ici pour ses contrôles d'accès qui doivent refuser une opération ; pour un
masquage silencieux de navigation, c'est `noyau.habilitations.a_permission`.
"""

from functools import wraps

from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied

from administration.models import TypeAction
from administration.services.journal import ServiceJournal
from noyau.exceptions import ErreurHabilitation
from noyau.habilitations import a_permission


def verifier_habilitation(utilisateur, permission: str) -> None:
    """Lève `ErreurHabilitation` **et** journalise le refus — une fois par
    tentative refusée, jamais par un affichage qui se contente de masquer
    (`a_permission`, silencieuse, sert cet autre cas). Voir Prompt 03, § 2.2.
    """
    if a_permission(utilisateur, permission):
        return
    ServiceJournal.enregistrer(
        type_action=TypeAction.ACCES_REFUSE,
        identifiant_saisi=getattr(utilisateur, "username", ""),
        detail=f"Permission demandée : {permission}.",
        auteur=utilisateur if utilisateur.is_authenticated else None,
        cible=permission,
    )
    raise ErreurHabilitation(f"Habilitation manquante pour {permission!r} : {utilisateur}.")


def exige_habilitation(permission: str):
    """Décorateur de vue. Double le contrôle du service, ne le remplace jamais.

    Convertit `ErreurHabilitation` (exception métier, pas HTTP) en
    `PermissionDenied` (que Django rend en 403) — voir docs/suivi/PROBLEMES.md, P-09.
    """

    def decorateur(vue):
        @wraps(vue)
        def enveloppe(request, *args, **kwargs):
            try:
                verifier_habilitation(request.user, permission)
            except ErreurHabilitation as erreur:
                raise PermissionDenied(str(erreur)) from erreur
            return vue(request, *args, **kwargs)

        return enveloppe

    return decorateur


class HabilitationMixin(AccessMixin):
    """Mixin de vue basée classe. Double le contrôle du service, ne le
    remplace jamais.
    """

    permission_requise: str = ""

    def dispatch(self, request, *args, **kwargs):
        try:
            verifier_habilitation(request.user, self.permission_requise)
        except ErreurHabilitation:
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)
