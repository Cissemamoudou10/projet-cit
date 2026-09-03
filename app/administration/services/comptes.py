"""Gestion des comptes utilisateurs — RG-01, RG-04, RG-26, CU-P1-02.

Un service ne connaît pas la requête HTTP — voir .claude/rules/services.md.
Aucune suppression : un compte ayant produit des entrées de journal ne peut
être supprimé (RG-04) — voir Prompt 02, § 2.1. Seule la désactivation existe.
"""

from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as ErreurValidationDjango
from django.db import IntegrityError, models, transaction

from administration.constantes import PROFIL_VERS_GROUPE
from administration.exceptions import ErreurIdentifiantExistant
from administration.habilitations import verifier_habilitation
from administration.models import Profil, Utilisateur
from administration.services.garde_fous import (
    interdire_autodesactivation,
    interdire_perte_du_dernier_administrateur,
)
from administration.services.journal_comptes import (
    journaliser_creation,
    journaliser_desactivation,
    journaliser_modification,
    journaliser_reactivation,
)
from noyau.exceptions import ErreurIntrouvable, ErreurValidation
from noyau.pagination import paginer
from noyau.services.base import ServiceBase

# Domaine P1 de la matrice § 11.2 — noyau.Habilitation porte le catalogue,
# voir docs/suivi/DECISIONS.md pour la reprise depuis administration.change_utilisateur.
PERMISSION_GESTION_COMPTES = "noyau.administration_ecriture"


class ServiceCompte:
    DOMAINE = "administration"

    @staticmethod
    def creer(agissant, donnees):
        verifier_habilitation(agissant, PERMISSION_GESTION_COMPTES)

        compte = Utilisateur(
            username=donnees["identifiant"],
            grade=donnees["grade"],
            first_name=donnees.get("prenom", ""),
            last_name=donnees.get("nom", ""),
            profil=donnees["profil"],
        )
        try:
            with transaction.atomic():
                ServiceCompte.definir_mot_de_passe_initial(
                    agissant, compte, donnees["mot_de_passe"]
                )
                ServiceCompte._synchroniser_groupe(compte)
                journaliser_creation(agissant, compte)
        except IntegrityError as erreur:
            raise ErreurIdentifiantExistant(
                f"L'identifiant « {compte.username} » est déjà attribué."
            ) from erreur
        return compte

    @staticmethod
    def definir_mot_de_passe_initial(agissant, compte, mot_de_passe):
        """Valide selon AUTH_PASSWORD_VALIDATORS, condense, lève le drapeau
        de changement obligatoire. Réutilisable pour une réinitialisation
        sur un compte déjà existant, pas seulement à la création.
        """
        ServiceCompte._valider_mot_de_passe(mot_de_passe, compte)
        compte.set_password(mot_de_passe)
        compte.doit_changer_mot_de_passe = True
        if compte.pk is None:
            ServiceBase.creer(compte, agissant)
        else:
            ServiceBase.modifier(compte, agissant)

    @staticmethod
    def _synchroniser_groupe(compte):
        """RG-02 bis : les droits reposent sur les groupes Django, jamais
        sur `profil` — sans ce rattachement, un compte créé ou modifié ici
        porte un `profil` correct mais n'a en réalité aucune permission,
        `has_perm` ne consultant que les groupes. Remplace l'appartenance
        plutôt que d'ajouter : un compte n'est jamais rattaché qu'à un seul
        groupe métier à la fois, celui de son profil courant.
        """
        groupe = Group.objects.get(name=PROFIL_VERS_GROUPE[compte.profil])
        compte.groups.set([groupe])

    @staticmethod
    def modifier(agissant, compte, donnees):
        verifier_habilitation(agissant, PERMISSION_GESTION_COMPTES)

        ancien_profil = compte.profil
        nouveau_profil = donnees.get("profil", compte.profil)
        interdire_perte_du_dernier_administrateur(
            compte, reste_administrateur_actif=(nouveau_profil == Profil.ADMINISTRATEUR)
        )

        compte.username = donnees.get("identifiant", compte.username)
        compte.grade = donnees.get("grade", compte.grade)
        compte.first_name = donnees.get("prenom", compte.first_name)
        compte.last_name = donnees.get("nom", compte.last_name)
        compte.profil = nouveau_profil

        try:
            with transaction.atomic():
                ServiceBase.modifier(compte, agissant)
                ServiceCompte._synchroniser_groupe(compte)
                journaliser_modification(agissant, compte, ancien_profil)
        except IntegrityError as erreur:
            raise ErreurIdentifiantExistant(
                f"L'identifiant « {compte.username} » est déjà attribué."
            ) from erreur
        return compte

    @staticmethod
    @transaction.atomic
    def desactiver(agissant, compte):
        verifier_habilitation(agissant, PERMISSION_GESTION_COMPTES)
        interdire_autodesactivation(agissant, compte)
        interdire_perte_du_dernier_administrateur(compte, reste_administrateur_actif=False)

        compte.is_active = False
        ServiceBase.modifier(compte, agissant)
        journaliser_desactivation(agissant, compte)
        return compte

    @staticmethod
    @transaction.atomic
    def reactiver(agissant, compte):
        verifier_habilitation(agissant, PERMISSION_GESTION_COMPTES)

        compte.is_active = True
        ServiceBase.modifier(compte, agissant)
        journaliser_reactivation(agissant, compte)
        return compte

    @staticmethod
    @transaction.atomic
    def changer_mot_de_passe(compte, ancien_mot_de_passe, nouveau_mot_de_passe):
        if not compte.check_password(ancien_mot_de_passe):
            raise ErreurValidation("L'ancien mot de passe est incorrect.")

        ServiceCompte._valider_mot_de_passe(nouveau_mot_de_passe, compte)
        compte.set_password(nouveau_mot_de_passe)
        compte.doit_changer_mot_de_passe = False
        ServiceBase.modifier(compte, compte)
        return compte

    @staticmethod
    def doit_changer_mot_de_passe(compte):
        """La règle que l'intergiciel consulte — voir Prompt 02, § 2.2."""
        return compte.doit_changer_mot_de_passe

    @staticmethod
    def obtenir(pk):
        """La vue ne doit jamais importer `Utilisateur` — voir
        .claude/rules/vues.md. Elle passe par ici plutôt que par
        `get_object_or_404(Utilisateur, ...)`.
        """
        try:
            return Utilisateur.objects.get(pk=pk)
        except Utilisateur.DoesNotExist as erreur:
            raise ErreurIntrouvable(f"Compte introuvable (identifiant {pk}).") from erreur

    @staticmethod
    def profils_disponibles():
        return Profil.choices

    CHAMPS_TRIABLES = {"identifiant": "username", "derniere_connexion": "last_login"}

    @staticmethod
    def lister(agissant, filtres, page):
        verifier_habilitation(agissant, PERMISSION_GESTION_COMPTES)

        queryset = Utilisateur.objects.all()
        recherche = filtres.get("recherche")
        if recherche:
            queryset = queryset.filter(
                models.Q(username__icontains=recherche)
                | models.Q(last_name__icontains=recherche)
                | models.Q(grade__icontains=recherche)
            )
        if filtres.get("profil"):
            queryset = queryset.filter(profil=filtres["profil"])
        if filtres.get("etat") == "actif":
            queryset = queryset.filter(is_active=True)
        elif filtres.get("etat") == "desactive":
            queryset = queryset.filter(is_active=False)
        queryset = queryset.order_by(ServiceCompte._ordre(filtres.get("tri")))
        return paginer(queryset, page)

    @staticmethod
    def _ordre(tri):
        """§ 3.09 : `tri` est le nom de colonne côté présentation
        (« identifiant », « -derniere_connexion »...), traduit ici vers le
        nom du champ réel — la vue ne connaît que le premier.
        """
        tri = tri or "identifiant"
        colonne = tri.lstrip("-")
        champ = ServiceCompte.CHAMPS_TRIABLES.get(colonne, "username")
        return f"-{champ}" if tri.startswith("-") else champ

    @staticmethod
    def _valider_mot_de_passe(mot_de_passe, compte):
        try:
            validate_password(mot_de_passe, compte)
        except ErreurValidationDjango as erreur:
            raise ErreurValidation(" ".join(erreur.messages)) from erreur
