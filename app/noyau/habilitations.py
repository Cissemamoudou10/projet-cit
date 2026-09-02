"""Mécanisme d'habilitation — RG-02 et RG-02 bis.

Mécanisme unique, appliqué en couche services et non dans chaque vue : une
habilitation vérifiée dans une vue laisse passer toute donnée entrant par un
autre chemin (import, API, commande d'administration).

Les droits reposent sur les groupes et permissions natifs de Django : le
profil reste une énumération de cinq valeurs, les droits attachés sont des
données modifiables par l'administrateur sans toucher au code (RG-02 bis).
"""

from functools import wraps

from django.contrib.auth.mixins import AccessMixin
from django.core.exceptions import PermissionDenied

from noyau.exceptions import ErreurHabilitation


def verifier_habilitation(utilisateur, permission: str) -> None:
    """Lève `ErreurHabilitation` si `utilisateur` n'a pas `permission`.

    `permission` suit la syntaxe native de Django : `"app_label.codename"`.
    """
    if not utilisateur.has_perm(permission):
        raise ErreurHabilitation(f"Habilitation manquante pour {permission!r} : {utilisateur}.")


def exige_habilitation(permission: str):
    """Décorateur de vue. Double le contrôle du service, ne le remplace jamais.

    Convertit `ErreurHabilitation` (exception métier, pas HTTP) en
    `PermissionDenied` (que Django rend en 403) — sans quoi une habilitation
    manquante produirait une erreur 500, jamais exercé avant US-ADM-02.
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
