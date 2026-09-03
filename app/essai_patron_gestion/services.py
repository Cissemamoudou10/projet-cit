"""Service de test du patron — mêmes attributs injectés que
`referentiel.services.type_formation.ServiceTypeFormation` (D-19), pour un
usage réellement distinct de `TypeFormation`.
"""

from administration.habilitations import verifier_habilitation
from administration.models import TypeAction
from administration.services.journal import DonneesEntreeJournal, ServiceJournal
from essai_patron_gestion.models import ElementGestionTest
from noyau.services.gestion import ServiceGestion


class ServiceElementGestionTest(ServiceGestion):
    DOMAINE = "referentiel"
    MODELE = ElementGestionTest
    CHAMP_UNICITE = "intitule"
    CHAMPS_RECHERCHE = ("intitule",)
    CHAMPS_JOURNALISES = ("intitule",)
    OBJET_TYPE = "element_gestion_test"

    PERMISSION_LECTURE = "noyau.referentiel_lecture"
    PERMISSION_ECRITURE = "noyau.referentiel_ecriture"
    VERIFIER_HABILITATION = staticmethod(verifier_habilitation)
    ENREGISTRER_JOURNAL = staticmethod(ServiceJournal.enregistrer_detaillee)
    DONNEES_JOURNAL = DonneesEntreeJournal
    NATURE_CREATION = TypeAction.CREATION_ELEMENT_GESTION
    NATURE_MODIFICATION = TypeAction.MODIFICATION_ELEMENT_GESTION
    NATURE_ARCHIVAGE = TypeAction.ARCHIVAGE_ELEMENT_GESTION
