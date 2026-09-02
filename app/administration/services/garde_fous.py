"""Garde-fous de gestion des comptes — règles nouvelles, non prévues par les
livrables, extraites de `ServiceCompte` pour rester sous 200 lignes. Voir
docs/suivi/DECISIONS.md, D-07.
"""

from administration.models import Profil, Utilisateur
from noyau.exceptions import ErreurValidation


def interdire_autodesactivation(agissant, compte):
    if agissant.pk == compte.pk:
        raise ErreurValidation(
            "Vous ne pouvez pas désactiver votre propre compte. "
            "Un autre administrateur doit s'en charger."
        )


def interdire_perte_du_dernier_administrateur(compte, *, reste_administrateur_actif):
    if compte.profil != Profil.ADMINISTRATEUR or not compte.is_active:
        return
    if reste_administrateur_actif:
        return
    autres = Utilisateur.objects.filter(profil=Profil.ADMINISTRATEUR, is_active=True).exclude(
        pk=compte.pk
    )
    if not autres.exists():
        raise ErreurValidation(
            "Impossible : c'est le dernier compte administrateur actif du système."
        )
