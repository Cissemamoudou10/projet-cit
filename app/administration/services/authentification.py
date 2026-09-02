"""Authentification — RG-01, RG-03, RG-26, CU-P1-01.

Un service ne connaît pas la requête HTTP — voir .claude/rules/services.md.
La comparaison du condensat passe par `django.contrib.auth.authenticate` :
aucune primitive cryptographique n'est réécrite ici.
"""

from datetime import timedelta

from django.conf import settings
from django.contrib.auth import authenticate
from django.db import transaction
from django.utils import timezone

from administration.models import TypeAction, Utilisateur
from administration.services.journal import ServiceJournal
from noyau.exceptions import ErreurAuthentification, ErreurCompteDesactive, ErreurCompteVerrouille
from noyau.services.base import ServiceBase

MESSAGE_IDENTIFIANTS_INVALIDES = "Identifiant ou mot de passe invalide."
MESSAGE_COMPTE_DESACTIVE = "Ce compte est désactivé. Adressez-vous à l'administrateur."
MESSAGE_COMPTE_VERROUILLE = "Ce compte est temporairement verrouillé. Réessayez plus tard."


class ServiceAuthentification:
    @staticmethod
    def authentifier(identifiant, mot_de_passe):
        """Ordre des contrôles : compte inexistant, désactivé puis verrouillé
        se vérifient avant toute comparaison de mot de passe — un compte
        verrouillé reste refusé même avec le bon mot de passe.
        """
        utilisateur = Utilisateur.objects.filter(username=identifiant).first()

        if utilisateur is None:
            ServiceAuthentification.enregistrer_echec(identifiant)
            raise ErreurAuthentification(MESSAGE_IDENTIFIANTS_INVALIDES)

        if not utilisateur.is_active:
            ServiceAuthentification._journaliser_refus(
                identifiant, utilisateur, "Compte désactivé."
            )
            raise ErreurCompteDesactive(MESSAGE_COMPTE_DESACTIVE)

        if ServiceAuthentification.est_verrouille(utilisateur):
            ServiceAuthentification._journaliser_refus(
                identifiant, utilisateur, "Compte verrouillé."
            )
            raise ErreurCompteVerrouille(MESSAGE_COMPTE_VERROUILLE)

        utilisateur_authentifie = authenticate(username=identifiant, password=mot_de_passe)
        if utilisateur_authentifie is None:
            ServiceAuthentification.enregistrer_echec(identifiant)
            raise ErreurAuthentification(MESSAGE_IDENTIFIANTS_INVALIDES)

        ServiceAuthentification.reinitialiser_echecs(utilisateur_authentifie)
        return utilisateur_authentifie

    @staticmethod
    def _journaliser_refus(identifiant, utilisateur, detail):
        ServiceJournal.enregistrer(
            type_action=TypeAction.ECHEC_AUTHENTIFICATION,
            identifiant_saisi=identifiant,
            detail=detail,
            auteur=utilisateur,
            cible="authentification",
        )

    @staticmethod
    @transaction.atomic
    def enregistrer_echec(identifiant):
        """Identifiant inexistant ou mot de passe erroné : les deux passent
        par ici, avec le même message d'erreur côté appelant (critère 2).
        """
        utilisateur = Utilisateur.objects.filter(username=identifiant).first()
        if utilisateur is not None:
            utilisateur.echecs_consecutifs += 1
            if utilisateur.echecs_consecutifs >= settings.AUTH_SEUIL_ECHECS:
                utilisateur.verrouille_jusqu_a = timezone.now() + timedelta(
                    minutes=settings.AUTH_DUREE_VERROUILLAGE_MINUTES
                )
            ServiceBase.modifier(utilisateur, utilisateur=None)

        ServiceJournal.enregistrer(
            type_action=TypeAction.ECHEC_AUTHENTIFICATION,
            identifiant_saisi=identifiant,
            detail="Identifiant ou mot de passe invalide.",
            auteur=utilisateur,
            cible="authentification",
        )

    @staticmethod
    @transaction.atomic
    def reinitialiser_echecs(utilisateur):
        if utilisateur.echecs_consecutifs or utilisateur.verrouille_jusqu_a:
            utilisateur.echecs_consecutifs = 0
            utilisateur.verrouille_jusqu_a = None
            ServiceBase.modifier(utilisateur, utilisateur=None)

    @staticmethod
    def est_verrouille(utilisateur):
        return (
            utilisateur.verrouille_jusqu_a is not None
            and utilisateur.verrouille_jusqu_a > timezone.now()
        )
