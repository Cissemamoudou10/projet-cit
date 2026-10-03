"""Gestion des lieux — CU-P4-06, RG-37 (la comparaison à l'effectif viendra
avec les brigades, sprint 3 : cette story pose la donnée, pas le contrôle).

`lister` est surchargé : `ServiceGestion.CHAMPS_FILTRABLES` ne sait exprimer
que l'égalité, alors que la capacité minimale exige `__gte` et la
disponibilité une exclusion sur `IndisponibiliteLieu` — voir § 4 du Prompt 14.
"""

import datetime

from django.db.models import Count, Exists, OuterRef, Q
from django.utils import timezone

from administration.habilitations import verifier_habilitation
from administration.models import TypeAction
from administration.services.journal import DonneesEntreeJournal, ServiceJournal
from noyau.exceptions import ErreurValidation
from noyau.intervalles import filtre_recouvrement
from noyau.pagination import paginer
from noyau.services.gestion import ServiceGestion
from ressources.models import CategorieLieu, IndisponibiliteLieu, Lieu, TypeLieuPartage


class ServiceLieu(ServiceGestion):
    DOMAINE = "lieux_calendrier"
    MODELE = Lieu
    CHAMP_UNICITE = "intitule"
    CHAMPS_RECHERCHE = ("intitule",)
    CHAMPS_JOURNALISES = ("intitule", "capacite", "categorie", "type_partage")
    OBJET_TYPE = "lieu"

    PERMISSION_LECTURE = "noyau.lieux_calendrier_lecture"
    PERMISSION_ECRITURE = "noyau.lieux_calendrier_ecriture"
    VERIFIER_HABILITATION = staticmethod(verifier_habilitation)
    ENREGISTRER_JOURNAL = staticmethod(ServiceJournal.enregistrer_detaillee)
    DONNEES_JOURNAL = DonneesEntreeJournal
    NATURE_CREATION = TypeAction.CREATION_ELEMENT_GESTION
    NATURE_MODIFICATION = TypeAction.MODIFICATION_ELEMENT_GESTION
    NATURE_ARCHIVAGE = TypeAction.ARCHIVAGE_ELEMENT_GESTION
    NATURE_SUPPRESSION = TypeAction.SUPPRESSION_ELEMENT_GESTION

    @classmethod
    def _erreur_unicite(cls, instance):
        """`intitule` n'est pas la seule contrainte en base : `Lieu` porte
        aussi `ck_lieu_capacite_positive` et `ck_lieu_type_partage_coherent`
        (§ 2 du Prompt 14), chacune capable de provoquer l'`IntegrityError`
        que ce patron intercepte. Sans cette distinction, le message
        générique cherche un doublon d'intitulé qui n'existe pas et produit
        « ... est déjà attribué à None. » — même défaut que celui corrigé
        pour `ServiceObjectifPedagogique` (US-REF-05), sur une contrainte
        différente à chaque fois.
        """
        if instance.capacite is not None and instance.capacite <= 0:
            return ErreurValidation("La capacité doit être un nombre strictement positif.")
        if instance.categorie == CategorieLieu.LIEU_PARTAGE and not instance.type_partage:
            return ErreurValidation(
                f"« {instance.intitule} » est un lieu partagé : précisez son type "
                "(amphithéâtre, laboratoire ou salle spécialisée)."
            )
        if instance.categorie != CategorieLieu.LIEU_PARTAGE and instance.type_partage:
            return ErreurValidation(
                f"« {instance.intitule} » n'est pas un lieu partagé : retirez le "
                "type de partage renseigné."
            )
        return super()._erreur_unicite(instance)

    @staticmethod
    def choix_categorie():
        """La vue ne doit jamais importer `ressources.models` directement —
        voir .claude/rules/vues.md, même patron que `ServiceInstructeur.
        choix_statut`."""
        return CategorieLieu.choices

    @staticmethod
    def libelle_categorie(valeur):
        return CategorieLieu(valeur).label

    @staticmethod
    def choix_type_partage():
        return TypeLieuPartage.choices

    @classmethod
    def _queryset(cls):
        """Annote `est_indisponible_maintenant` (§ 8) et, Prompt 17 § 2.5,
        `nombre_indisponibilites_a_venir` — une seule requête pour toute la
        page, jamais une par ligne (.claude/rules/python.md). Les deux
        portent sur la même relation (`indisponibilites`) : `Exists` est une
        sous-requête corrélée, `Count` la seule jointure du queryset, aucun
        produit cartésien entre les deux à craindre.
        """
        maintenant = timezone.now()
        return cls.MODELE.objects.annotate(
            est_indisponible_maintenant=Exists(
                IndisponibiliteLieu.objects.filter(
                    lieu=OuterRef("pk"), debut__lte=maintenant, fin__gt=maintenant
                )
            ),
            nombre_indisponibilites_a_venir=Count(
                "indisponibilites", filter=Q(indisponibilites__fin__gt=maintenant)
            ),
        )

    @classmethod
    def lister(cls, agissant, filtres, page):
        cls._verifier(agissant, lecture=True)
        queryset = cls._queryset()
        if filtres.get("etat") == "actif":
            queryset = queryset.filter(archive=False)
        elif filtres.get("etat") == "archive":
            queryset = queryset.filter(archive=True)
        if filtres.get("categorie"):
            queryset = queryset.filter(categorie=filtres["categorie"])
        capacite_min = filtres.get("capacite_min")
        if capacite_min and str(capacite_min).isdigit():
            queryset = queryset.filter(capacite__gte=int(capacite_min))
        recherche = filtres.get("recherche")
        if recherche:
            queryset = queryset.filter(intitule__icontains=recherche)
        queryset = cls._filtrer_disponibilite(
            queryset, filtres.get("disponible_du"), filtres.get("disponible_au")
        )
        queryset = queryset.order_by(cls._ordre(filtres.get("tri")))
        return paginer(queryset, page)

    @staticmethod
    def _filtrer_disponibilite(queryset, disponible_du, disponible_au):
        """§ 4 du Prompt 14 : un lieu sort de la liste s'il porte une
        indisponibilité qui recouvre la période demandée. Bornes converties
        en instants de jour, `disponible_au` inclus jusqu'à minuit.
        """
        if not disponible_du or not disponible_au:
            return queryset
        debut_fenetre = timezone.make_aware(
            datetime.datetime.combine(disponible_du, datetime.time.min)
        )
        fin_fenetre = timezone.make_aware(
            datetime.datetime.combine(disponible_au + datetime.timedelta(days=1), datetime.time.min)
        )
        return queryset.exclude(
            filtre_recouvrement(
                "indisponibilites__debut", "indisponibilites__fin", debut_fenetre, fin_fenetre
            )
        )
