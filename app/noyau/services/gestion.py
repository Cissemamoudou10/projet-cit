"""Patron des services de gestion — consultation, création, modification,
archivage, suppression si jamais référencé. Prompt 05, § 2.1 : cinq stories
du référentiel (US-REF-00, 01, 02, 05, 07) en héritent et ne déclarent que ce
qui leur est propre.

Un service ne connaît pas la requête HTTP — voir .claude/rules/services.md.

`noyau` ne dépend d'aucune application, même le temps d'un import différé :
le test d'architecture qui l'impose lit le fichier entièrement, sans
distinguer un import en tête de module d'un import à l'intérieur d'une
fonction. La vérification d'habilitation et la journalisation exigent
pourtant `administration`. Résolu par injection : la sous-classe (posée
dans une application autorisée à dépendre d'`administration`) fournit les
fonctions et valeurs nécessaires en attributs de classe — voir
docs/suivi/DECISIONS.md, D-19.
"""

from django.core.exceptions import ValidationError as ErreurValidationDjango
from django.db import IntegrityError, models, transaction
from django.db.models.deletion import ProtectedError
from django.utils import timezone

from noyau.exceptions import ErreurIntrouvable, ErreurModificationConcurrente, ErreurValidation
from noyau.pagination import paginer
from noyau.services.base import ServiceBase


def decrire_opposants(instance, opposants):
    """Message d'E3 (fiche générique) — énumère jusqu'à dix éléments qui
    s'opposent à la suppression de `instance`. Fonction libre, pas seulement
    une méthode du patron : `ServiceReferentiel` (US-REF-03), qui n'hérite
    pas de `ServiceGestion`, en a le même besoin pour RG-07.
    """
    elements = ", ".join(str(objet) for objet in list(opposants)[:10])
    return f"{instance} est référencé par : {elements}. Impossible de le supprimer."


def valider_instance(instance):
    """Traduit un `ValidationError` Django (`full_clean`) en `ErreurValidation`
    métier — fonction libre pour la même raison que `decrire_opposants` :
    `ServiceReferentiel` valide `ElementReferentiel` sans hériter du patron.
    """
    try:
        instance.full_clean(validate_unique=False, validate_constraints=False)
    except ErreurValidationDjango as erreur:
        raise ErreurValidation(_decrire_erreurs(erreur)) from erreur


def _decrire_erreurs(erreur):
    if hasattr(erreur, "message_dict"):
        messages = [message for liste in erreur.message_dict.values() for message in liste]
    else:
        messages = erreur.messages
    return " ".join(messages)


class ServiceGestion:
    """Sous-classe : déclare `MODELE`, `DOMAINE`, `CHAMP_UNICITE` (aussi
    l'identifiant lisible du journal), `CHAMPS_RECHERCHE`, `CHAMPS_TRIABLES`,
    `CHAMPS_FILTRABLES`, `OBJET_TYPE`, `CHAMPS_JOURNALISES`, plus les six
    attributs injectés ci-dessous (D-19) : `PERMISSION_LECTURE`,
    `PERMISSION_ECRITURE`, `VERIFIER_HABILITATION`, `ENREGISTRER_JOURNAL`,
    `DONNEES_JOURNAL`, `NATURE_CREATION`/`NATURE_MODIFICATION`/`NATURE_ARCHIVAGE`/
    `NATURE_SUPPRESSION`.
    """

    MODELE = None
    CHAMP_UNICITE = None
    CHAMPS_RECHERCHE = ()
    CHAMPS_TRIABLES = {}
    CHAMPS_FILTRABLES = ()  # égalité, dans lister() ; filtre ignoré si vide
    OBJET_TYPE = ""
    CHAMPS_JOURNALISES = ()

    PERMISSION_LECTURE = None
    PERMISSION_ECRITURE = None
    VERIFIER_HABILITATION = None
    ENREGISTRER_JOURNAL = None
    DONNEES_JOURNAL = None
    NATURE_CREATION = None
    NATURE_MODIFICATION = None
    NATURE_ARCHIVAGE = None
    NATURE_SUPPRESSION = None

    @classmethod
    def _queryset(cls):
        """Base de `lister()` : à surcharger pour `select_related`/annotation."""
        return cls.MODELE.objects.all()

    @classmethod
    def lister(cls, agissant, filtres, page):
        cls._verifier(agissant, lecture=True)
        queryset = cls._queryset()
        if filtres.get("etat") == "actif":
            queryset = queryset.filter(archive=False)
        elif filtres.get("etat") == "archive":
            queryset = queryset.filter(archive=True)
        for champ in cls.CHAMPS_FILTRABLES:
            valeur = filtres.get(champ)
            if valeur:
                queryset = queryset.filter(**{champ: valeur})
        recherche = filtres.get("recherche")
        if recherche and cls.CHAMPS_RECHERCHE:
            condition = models.Q()
            for champ in cls.CHAMPS_RECHERCHE:
                condition |= models.Q(**{f"{champ}__icontains": recherche})
            queryset = queryset.filter(condition)
        queryset = queryset.order_by(cls._ordre(filtres.get("tri")))
        return paginer(queryset, page)

    @classmethod
    def disponibles_pour_selection(cls):
        """§ 2.4 : une sélection ne montre jamais un archivé, `lister` si."""
        return cls.MODELE.objects.filter(archive=False)

    @classmethod
    def obtenir(cls, pk):
        try:
            return cls.MODELE.objects.get(pk=pk)
        except cls.MODELE.DoesNotExist as erreur:
            raise ErreurIntrouvable(f"Élément introuvable (identifiant {pk}).") from erreur

    @classmethod
    def creer(cls, agissant, donnees):
        cls._verifier(agissant, lecture=False)
        instance = cls.MODELE(**donnees)
        cls._valider(instance)
        try:
            with transaction.atomic():
                ServiceBase.creer(instance, agissant)
                cls._journaliser(
                    agissant, cls.NATURE_CREATION, instance, valeur_apres=cls._capturer(instance)
                )
        except IntegrityError as erreur:
            raise cls._erreur_unicite(instance) from erreur
        return instance

    @classmethod
    def modifier(cls, agissant, pk, donnees, modifie_le_attendu):
        cls._verifier(agissant, lecture=False)
        instance = cls.obtenir(pk)
        if instance.modifie_le != modifie_le_attendu:
            raise ErreurModificationConcurrente(
                f"Cet élément a été modifié par {instance.modifie_par} entre-temps : "
                "reprenez votre saisie."
            )
        avant = cls._capturer(instance)
        for champ, valeur in donnees.items():
            setattr(instance, champ, valeur)
        cls._valider(instance)
        try:
            with transaction.atomic():
                ServiceBase.modifier(instance, agissant)
                cls._journaliser(
                    agissant,
                    cls.NATURE_MODIFICATION,
                    instance,
                    valeur_avant=avant,
                    valeur_apres=cls._capturer(instance),
                )
        except IntegrityError as erreur:
            raise cls._erreur_unicite(instance) from erreur
        return instance

    @classmethod
    def archiver(cls, agissant, pk):
        cls._verifier(agissant, lecture=False)
        instance = cls.obtenir(pk)
        with transaction.atomic():
            instance.archive = True
            instance.archive_le = timezone.now()
            ServiceBase.modifier(instance, agissant)
            cls._journaliser(agissant, cls.NATURE_ARCHIVAGE, instance)
        return instance

    @classmethod
    def desarchiver(cls, agissant, pk):
        cls._verifier(agissant, lecture=False)
        instance = cls.obtenir(pk)
        with transaction.atomic():
            instance.archive = False
            instance.archive_le = None
            ServiceBase.modifier(instance, agissant)
        return instance

    @classmethod
    def supprimer(cls, agissant, pk):
        cls._verifier(agissant, lecture=False)
        instance = cls.obtenir(pk)
        try:
            with transaction.atomic():
                instance.delete()
                cls._journaliser(agissant, cls.NATURE_SUPPRESSION, instance)
        except ProtectedError as erreur:
            raise ErreurValidation(
                decrire_opposants(instance, erreur.protected_objects)
            ) from erreur

    @classmethod
    def _verifier(cls, agissant, *, lecture):
        permission = cls.PERMISSION_LECTURE if lecture else cls.PERMISSION_ECRITURE
        cls.VERIFIER_HABILITATION(agissant, permission)

    @classmethod
    def _ordre(cls, tri):
        tri = tri or cls.CHAMP_UNICITE
        colonne = tri.lstrip("-")
        champ = cls.CHAMPS_TRIABLES.get(colonne, cls.CHAMP_UNICITE)
        return f"-{champ}" if tri.startswith("-") else champ

    @staticmethod
    def _valider(instance):
        valider_instance(instance)

    @classmethod
    def _erreur_unicite(cls, instance):
        valeur = getattr(instance, cls.CHAMP_UNICITE)
        existant = (
            cls.MODELE.objects.filter(**{f"{cls.CHAMP_UNICITE}__iexact": valeur})
            .exclude(pk=instance.pk)
            .first()
        )
        return ErreurValidation(f"« {valeur} » est déjà attribué à {existant}.")

    @classmethod
    def _capturer(cls, instance):
        return {champ: getattr(instance, champ) for champ in cls.CHAMPS_JOURNALISES}

    @classmethod
    def _journaliser(cls, agissant, nature, instance, *, valeur_avant=None, valeur_apres=None):
        identifiant = str(getattr(instance, cls.CHAMP_UNICITE))
        cls.ENREGISTRER_JOURNAL(
            cls.DONNEES_JOURNAL(
                type_action=nature,
                identifiant_saisi=identifiant,
                auteur=agissant,
                objet_type=cls.OBJET_TYPE,
                objet_identifiant=identifiant,
                valeur_avant=valeur_avant,
                valeur_apres=valeur_apres,
            )
        )
