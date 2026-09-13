"""Gestion des natures d'événement du calendrier — CLS-03, § 3 du Prompt 28.

`ServiceNatureEvenement` n'ajoute qu'un domaine : tout le reste vient du
patron `ServiceGestion`, même précédent que `ServiceTypeFormation`
(US-REF-00). Pas de mixin d'archivage (.claude/rules/modeles.md, diagramme
CLS-03) : `archiver`/`desarchiver` restent hérités mais inutilisés, aucune
vue ne les expose.
"""

from administration.habilitations import verifier_habilitation
from administration.models import TypeAction
from administration.services.journal import DonneesEntreeJournal, ServiceJournal
from noyau.services.gestion import ServiceGestion
from ressources.models import EffetPeriode, NatureEvenement


class ServiceNatureEvenement(ServiceGestion):
    DOMAINE = "lieux_calendrier"
    MODELE = NatureEvenement
    CHAMP_UNICITE = "libelle"
    CHAMPS_RECHERCHE = ("libelle",)
    CHAMPS_JOURNALISES = ("libelle", "effet_par_defaut")
    OBJET_TYPE = "nature_evenement"

    PERMISSION_LECTURE = "noyau.lieux_calendrier_lecture"
    PERMISSION_ECRITURE = "noyau.lieux_calendrier_ecriture"
    VERIFIER_HABILITATION = staticmethod(verifier_habilitation)
    ENREGISTRER_JOURNAL = staticmethod(ServiceJournal.enregistrer_detaillee)
    DONNEES_JOURNAL = DonneesEntreeJournal
    NATURE_CREATION = TypeAction.CREATION_ELEMENT_GESTION
    NATURE_MODIFICATION = TypeAction.MODIFICATION_ELEMENT_GESTION
    NATURE_SUPPRESSION = TypeAction.SUPPRESSION_ELEMENT_GESTION

    @staticmethod
    def choix_effet():
        """La vue ne doit jamais importer `ressources.models` directement —
        voir .claude/rules/vues.md (même patron que `ServiceLieu.
        choix_categorie`)."""
        return EffetPeriode.choices

    @staticmethod
    def libelle_effet(valeur):
        return EffetPeriode(valeur).label

    @staticmethod
    def choix_natures():
        """Pour le filtre et le champ de sélection des écrans du calendrier
        — la vue ne doit jamais importer `ressources.models` directement
        (.claude/rules/vues.md), même patron que `ServiceIndisponibiliteInstructeur.
        choix_instructeurs`."""
        return [
            (nature.pk, nature.libelle) for nature in NatureEvenement.objects.order_by("libelle")
        ]
