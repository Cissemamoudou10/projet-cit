"""Gestion des objectifs pédagogiques d'une matière — CU-P2-06.

Hérite de `ServiceGestion` pour ce qu'il donne réellement (`creer`,
`obtenir`, `supprimer` — Prompt 09, étape 0) : `ObjectifPedagogique` n'est
pas un écran de liste de premier niveau (pas de `lister()` paginé/cherchable
ici, remplacé par `lister_pour_matiere`), ne porte pas d'archivage (pas
d'`archiver`/`desarchiver` appelés), et son réordonnancement n'a aucun
équivalent dans le patron.
"""

from django.db import transaction
from django.db.models import Max
from django.db.models.deletion import ProtectedError

from administration.habilitations import verifier_habilitation
from administration.models import TypeAction
from administration.services.journal import DonneesEntreeJournal, ServiceJournal
from noyau.exceptions import ErreurValidation
from noyau.services.base import ServiceBase
from noyau.services.gestion import ServiceGestion, decrire_opposants, valider_instance
from referentiel.models import ObjectifPedagogique


class ServiceObjectifPedagogique(ServiceGestion):
    DOMAINE = "referentiel"
    MODELE = ObjectifPedagogique
    CHAMP_UNICITE = "libelle"
    CHAMPS_JOURNALISES = ("matiere_id", "libelle", "ordre")
    OBJET_TYPE = "objectif_pedagogique"

    PERMISSION_LECTURE = "noyau.referentiel_lecture"
    PERMISSION_ECRITURE = "noyau.referentiel_ecriture"
    VERIFIER_HABILITATION = staticmethod(verifier_habilitation)
    ENREGISTRER_JOURNAL = staticmethod(ServiceJournal.enregistrer_detaillee)
    DONNEES_JOURNAL = DonneesEntreeJournal
    NATURE_CREATION = TypeAction.CREATION_ELEMENT_GESTION
    NATURE_MODIFICATION = TypeAction.MODIFICATION_ELEMENT_GESTION
    NATURE_SUPPRESSION = TypeAction.SUPPRESSION_ELEMENT_GESTION

    @classmethod
    def _erreur_unicite(cls, instance):
        """`CHAMP_UNICITE` ne porte ici aucune contrainte réelle — seule
        `uq_objectif_matiere_ordre` (matière, ordre) existe en base. Le
        message générique du patron, qui cherche un doublon sur `libelle`,
        n'a donc de sens que dans le seul cas où cette méthode est
        atteignable : deux ajouts concurrents sur la même matière se
        disputant le même `ordre` calculé (§ relecture US-REF-05).
        """
        return ErreurValidation(
            f"Un autre objectif a été ajouté à « {instance.matiere} » entre-temps : réessayez."
        )

    @classmethod
    def lister_pour_matiere(cls, agissant, matiere):
        cls._verifier(agissant, lecture=True)
        return cls.MODELE.objects.filter(matiere=matiere).order_by("ordre")

    @classmethod
    def ajouter(cls, agissant, matiere, libelle):
        """Ajoute en fin de liste : l'ordre se calcule, il ne se saisit
        jamais — le réordonnancement se fait ensuite par « monter »/
        « descendre » (§ 6.1). Réutilise `ServiceGestion.creer` tel quel.
        """
        dernier = cls.MODELE.objects.filter(matiere=matiere).aggregate(m=Max("ordre"))["m"] or 0
        return cls.creer(agissant, {"matiere": matiere, "libelle": libelle, "ordre": dernier + 1})

    @classmethod
    def modifier_libelle(cls, agissant, objectif, libelle):
        """Pas le `modifier()` du patron : son mécanisme de concurrence
        (`modifie_le_attendu`) n'a de sens que pour un formulaire à page
        entière, pas pour un tableau éditable en ligne — même choix qu'à
        US-REF-03 pour `ServiceReferentiel.modifier_volume`.
        """
        cls._verifier(agissant, lecture=False)
        avant = cls._capturer(objectif)
        objectif.libelle = libelle
        valider_instance(objectif)
        with transaction.atomic():
            ServiceBase.modifier(objectif, agissant)
            cls._journaliser(
                agissant,
                cls.NATURE_MODIFICATION,
                objectif,
                valeur_avant=avant,
                valeur_apres=cls._capturer(objectif),
            )
        return objectif

    @classmethod
    def monter(cls, agissant, objectif):
        precedent = (
            cls.MODELE.objects.filter(matiere=objectif.matiere, ordre__lt=objectif.ordre)
            .order_by("-ordre")
            .first()
        )
        if precedent is not None:
            cls.echanger_positions(agissant, objectif, precedent)
        return objectif

    @classmethod
    def descendre(cls, agissant, objectif):
        suivant = (
            cls.MODELE.objects.filter(matiere=objectif.matiere, ordre__gt=objectif.ordre)
            .order_by("ordre")
            .first()
        )
        if suivant is not None:
            cls.echanger_positions(agissant, objectif, suivant)
        return objectif

    @classmethod
    def echanger_positions(cls, agissant, objectif_a, objectif_b):
        """§ 2.2 — la contrainte `uq_objectif_matiere_ordre` est différée :
        les deux écritures doivent se dérouler dans la **même** transaction
        pour que l'état transitoire (deux objectifs de même ordre, entre les
        deux `save()`) soit toléré. Hors transaction explicite, chaque
        `save()` commite pour son propre compte et la contrainte, vérifiée à
        ce commit, refuse la première des deux écritures.
        """
        cls._verifier(agissant, lecture=False)
        avant_a, avant_b = cls._capturer(objectif_a), cls._capturer(objectif_b)
        objectif_a.ordre, objectif_b.ordre = objectif_b.ordre, objectif_a.ordre
        with transaction.atomic():
            ServiceBase.modifier(objectif_a, agissant)
            ServiceBase.modifier(objectif_b, agissant)
            cls._journaliser(
                agissant,
                cls.NATURE_MODIFICATION,
                objectif_a,
                valeur_avant=avant_a,
                valeur_apres=cls._capturer(objectif_a),
            )
            cls._journaliser(
                agissant,
                cls.NATURE_MODIFICATION,
                objectif_b,
                valeur_avant=avant_b,
                valeur_apres=cls._capturer(objectif_b),
            )

    @classmethod
    def supprimer(cls, agissant, pk):
        """Ne réutilise pas `ServiceGestion.supprimer` : le patron ne
        journalise jamais une suppression (voir sa docstring — aucune autre
        entité n'en avait besoin, elles archivent). Seule entité du projet à
        supprimer réellement (§ 2.3), donc la seule à devoir le faire ici.
        """
        cls._verifier(agissant, lecture=False)
        objectif = cls.obtenir(pk)
        avant = cls._capturer(objectif)
        try:
            with transaction.atomic():
                objectif.delete()
                cls._journaliser(
                    agissant,
                    TypeAction.SUPPRESSION_ELEMENT_GESTION,
                    objectif,
                    valeur_avant=avant,
                    valeur_apres=None,
                )
        except ProtectedError as erreur:
            raise ErreurValidation(
                decrire_opposants(objectif, erreur.protected_objects)
            ) from erreur
