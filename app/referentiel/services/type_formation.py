"""Gestion des types de formation — CU-P2-01.

`ServiceTypeFormation` n'ajoute qu'un comportement : tout le reste vient du
patron `ServiceGestion`. Les attributs injectés (D-19, docs/suivi/DECISIONS.md)
sont ce qui permet à `noyau` d'appeler l'habilitation et le journal sans
jamais importer `administration`.

`_queryset` annote le nombre de formations rattachées (Prompt 06, § 7) — une
seule requête pour toute la page, jamais une par ligne (python.md).
"""

from django.db.models import Count

from administration.habilitations import verifier_habilitation
from administration.models import TypeAction
from administration.services.journal import DonneesEntreeJournal, ServiceJournal
from noyau.services.gestion import ServiceGestion
from referentiel.models import TypeFormation


class ServiceTypeFormation(ServiceGestion):
    DOMAINE = "referentiel"
    MODELE = TypeFormation
    CHAMP_UNICITE = "intitule"
    CHAMPS_RECHERCHE = ("intitule",)
    CHAMPS_JOURNALISES = ("intitule",)
    OBJET_TYPE = "type_formation"

    PERMISSION_LECTURE = "noyau.referentiel_lecture"
    PERMISSION_ECRITURE = "noyau.referentiel_ecriture"
    VERIFIER_HABILITATION = staticmethod(verifier_habilitation)
    ENREGISTRER_JOURNAL = staticmethod(ServiceJournal.enregistrer_detaillee)
    DONNEES_JOURNAL = DonneesEntreeJournal
    NATURE_CREATION = TypeAction.CREATION_ELEMENT_GESTION
    NATURE_MODIFICATION = TypeAction.MODIFICATION_ELEMENT_GESTION
    NATURE_ARCHIVAGE = TypeAction.ARCHIVAGE_ELEMENT_GESTION

    @classmethod
    def _queryset(cls):
        return cls.MODELE.objects.annotate(nombre_formations=Count("formations"))
