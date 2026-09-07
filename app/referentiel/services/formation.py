"""Gestion des formations — CU-P2-02.

Tout vient du patron `ServiceGestion`, sauf l'unicité composite (écart 1,
Prompt 06 § 2.1) : `_erreur_unicite` est surchargée parce que le patron ne
connaît qu'une unicité à un seul champ (`CHAMP_UNICITE`). `_queryset` charge
le type en une requête (`select_related`) — la liste affiche son intitulé
sur chaque ligne — et annote, Prompt 17 § 2.3, le nombre de matières et le
volume prescrit total : une seule relation jointe (`elements_referentiel`),
`Count` et `Sum` peuvent donc partager la même agrégation sans double
comptage.
"""

from django.db.models import Count, Sum

from administration.habilitations import verifier_habilitation
from administration.models import TypeAction
from administration.services.journal import DonneesEntreeJournal, ServiceJournal
from noyau.exceptions import ErreurValidation
from noyau.services.gestion import ServiceGestion
from referentiel.models import Formation


class ServiceFormation(ServiceGestion):
    DOMAINE = "referentiel"
    MODELE = Formation
    CHAMP_UNICITE = "intitule"
    CHAMPS_RECHERCHE = ("intitule", "specialite")
    CHAMPS_FILTRABLES = ("type_formation",)
    CHAMPS_JOURNALISES = ("intitule", "specialite", "duree_semaines", "type_formation_id")
    OBJET_TYPE = "formation"

    PERMISSION_LECTURE = "noyau.referentiel_lecture"
    PERMISSION_ECRITURE = "noyau.referentiel_ecriture"
    VERIFIER_HABILITATION = staticmethod(verifier_habilitation)
    ENREGISTRER_JOURNAL = staticmethod(ServiceJournal.enregistrer_detaillee)
    DONNEES_JOURNAL = DonneesEntreeJournal
    NATURE_CREATION = TypeAction.CREATION_ELEMENT_GESTION
    NATURE_MODIFICATION = TypeAction.MODIFICATION_ELEMENT_GESTION
    NATURE_ARCHIVAGE = TypeAction.ARCHIVAGE_ELEMENT_GESTION
    NATURE_SUPPRESSION = TypeAction.SUPPRESSION_ELEMENT_GESTION

    @classmethod
    def _queryset(cls):
        return cls.MODELE.objects.select_related("type_formation").annotate(
            nombre_matieres=Count("elements_referentiel", distinct=True),
            volume_prescrit_total=Sum("elements_referentiel__volume_horaire_prescrit"),
        )

    @classmethod
    def _erreur_unicite(cls, instance):
        """Écart 1 : l'intitulé est unique au sein d'un type de formation,
        pas dans tout le centre — deux formations « Formation initiale »
        (officiers, sous-officiers) sont deux objets légitimes.
        """
        existant = (
            cls.MODELE.objects.filter(
                type_formation=instance.type_formation, intitule__iexact=instance.intitule
            )
            .exclude(pk=instance.pk)
            .first()
        )
        return ErreurValidation(
            f"« {instance.intitule} » est déjà attribué à {existant} "
            f"pour le type « {instance.type_formation} »."
        )
