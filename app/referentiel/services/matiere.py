"""Gestion du catalogue des matières — CU-P2-03.

Tout vient du patron `ServiceGestion`, sans rien y ajouter (Prompt 07,
étape 0) : `Matiere` n'a ni relation ni filtre ni colonne calculée. Seule
surcharge : `_erreur_unicite`, parce que `Matiere` porte deux champs
indépendamment uniques (`intitule`, `code`) — le patron ne sait désigner un
doublon que sur un seul champ (`CHAMP_UNICITE`).
"""

from administration.habilitations import verifier_habilitation
from administration.models import TypeAction
from administration.services.journal import DonneesEntreeJournal, ServiceJournal
from noyau.exceptions import ErreurValidation
from noyau.services.gestion import ServiceGestion
from referentiel.models import Matiere


class ServiceMatiere(ServiceGestion):
    DOMAINE = "referentiel"
    MODELE = Matiere
    CHAMP_UNICITE = "intitule"
    CHAMPS_RECHERCHE = ("intitule",)
    CHAMPS_JOURNALISES = ("intitule", "code")
    OBJET_TYPE = "matiere"

    PERMISSION_LECTURE = "noyau.referentiel_lecture"
    PERMISSION_ECRITURE = "noyau.referentiel_ecriture"
    VERIFIER_HABILITATION = staticmethod(verifier_habilitation)
    ENREGISTRER_JOURNAL = staticmethod(ServiceJournal.enregistrer_detaillee)
    DONNEES_JOURNAL = DonneesEntreeJournal
    NATURE_CREATION = TypeAction.CREATION_ELEMENT_GESTION
    NATURE_MODIFICATION = TypeAction.MODIFICATION_ELEMENT_GESTION
    NATURE_ARCHIVAGE = TypeAction.ARCHIVAGE_ELEMENT_GESTION

    @classmethod
    def _erreur_unicite(cls, instance):
        if instance.code:
            conflit = (
                cls.MODELE.objects.filter(code__iexact=instance.code)
                .exclude(pk=instance.pk)
                .first()
            )
            if conflit:
                return ErreurValidation(
                    f"Le code « {instance.code} » est déjà attribué à {conflit}."
                )
        return super()._erreur_unicite(instance)
