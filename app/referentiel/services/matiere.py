"""Gestion du catalogue des matières — CU-P2-03.

Seconde surcharge, Prompt 17 § 2.1 : `_queryset` annote trois compteurs pour
la liste — formations, instructeurs qualifiés non archivés, objectifs — en
une seule requête agrégée, jamais une par ligne (`.claude/rules/python.md`).
`Count(..., distinct=True)` sur les trois relations simultanément : chacune
compte sa propre clé primaire, donc le produit cartésien introduit par les
jointures multiples ne fausse aucun des trois totaux.
"""

from django.db.models import Count, Q

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
    NATURE_SUPPRESSION = TypeAction.SUPPRESSION_ELEMENT_GESTION

    @classmethod
    def _queryset(cls):
        return cls.MODELE.objects.annotate(
            nombre_formations=Count("elements_referentiel", distinct=True),
            nombre_instructeurs_qualifies=Count(
                "qualifications",
                filter=Q(qualifications__instructeur__archive=False),
                distinct=True,
            ),
            nombre_objectifs=Count("objectifs_pedagogiques", distinct=True),
        )

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
