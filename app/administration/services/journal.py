"""Journal des actions sensibles — RG-26, RG-27, CU-P1-03.

Un service ne connaît pas la requête HTTP — voir .claude/rules/services.md.
"""

from dataclasses import dataclass

from django.db import transaction

from administration.models import EntreeJournal, TypeAction
from noyau.pagination import paginer
from noyau.services.base import ServiceBase

PERMISSION_CONSULTATION_JOURNAL = "noyau.administration_lecture"

LIBELLES_OBJET_TYPE = {
    "type_formation": "Type de formation",
    "formation": "Formation",
    "matiere": "Matière",
    "objectif_pedagogique": "Objectif pédagogique",
    "prerequis": "Prérequis",
    "instructeur": "Instructeur",
    "lieu": "Lieu",
    "indisponibilite_lieu": "Indisponibilité de lieu",
    "qualification": "Qualification",
    "utilisateur": "Compte",
}


@dataclass
class DonneesEntreeJournal:
    """Un appel à `enregistrer_detaillee` — regroupe les neuf champs pour
    rester sous la limite de cinq paramètres par fonction
    (.claude/rules/python.md) sans réduire ce qu'une entrée peut porter.

    `objet_type`/`objet_identifiant` : le couple qui désigne l'objet
    concerné (CU-P1-03), distinct de `cible` — voir la docstring
    d'`EntreeJournal`. `valeur_avant`/`valeur_apres` : liste blanche de
    champs choisie par l'appelant, jamais une sérialisation complète — voir
    § 2.6 du Prompt 04, BNF-03.
    """

    type_action: str
    identifiant_saisi: str
    detail: str = ""
    auteur: object = None
    cible: str = ""
    objet_type: str = ""
    objet_identifiant: str = ""
    valeur_avant: dict | None = None
    valeur_apres: dict | None = None


class ServiceJournal:
    """`DOMAINE` déclaré (§ 2.4) pour la cohérence architecturale — l'app
    propriétaire est `administration`. `enregistrer`/`enregistrer_detaillee`
    n'exigent aucune permission : le journal est écrit par les autres
    services. `consulter`, si : RG-26 réserve la consultation à
    l'administrateur.
    """

    DOMAINE = "administration"

    @staticmethod
    @transaction.atomic
    def enregistrer(type_action, identifiant_saisi, detail="", auteur=None, cible=""):
        """Forme minimale, historique — cinq champs, sans objet concerné ni
        valeur avant/après. Voir `enregistrer_detaillee` pour les actions
        qui en ont besoin.
        """
        return ServiceJournal.enregistrer_detaillee(
            DonneesEntreeJournal(
                type_action=type_action,
                identifiant_saisi=identifiant_saisi,
                detail=detail,
                auteur=auteur,
                cible=cible,
            )
        )

    @staticmethod
    @transaction.atomic
    def enregistrer_detaillee(donnees: DonneesEntreeJournal):
        """Aucun utilisateur authentifié ne « crée » techniquement une
        entrée de journal : `cree_par` reste vide, `auteur` porte le compte
        concerné — voir la docstring de `EntreeJournal`.
        """
        entree = EntreeJournal(
            type_action=donnees.type_action,
            cible=donnees.cible,
            auteur=donnees.auteur,
            identifiant_saisi=donnees.identifiant_saisi,
            detail=donnees.detail,
            objet_type=donnees.objet_type,
            objet_identifiant=donnees.objet_identifiant,
            valeur_avant=donnees.valeur_avant,
            valeur_apres=donnees.valeur_apres,
        )
        return ServiceBase.creer(entree, utilisateur=None)

    CHAMPS_TRIABLES = {"horodatage": "cree_le"}

    @staticmethod
    def natures_disponibles():
        """La vue ne doit jamais importer `administration.models` — voir
        .claude/rules/vues.md.
        """
        return TypeAction.choices

    @staticmethod
    def objet_types_disponibles():
        """Liste déroulante du filtre « objet » (Prompt 17, § 3.1) : les
        valeurs réellement présentes dans le journal, jamais une
        nomenclature figée qui dériverait des services qui la posent —
        `administration` ne peut importer aucune des applications qui
        déclarent `OBJET_TYPE` (ordre des dépendances). Un identifiant
        saisi à la main était incompris (l'agent y cherchait une nature
        d'action) ; une liste déroulante empêche la confusion.
        """
        valeurs = (
            EntreeJournal.objects.exclude(objet_type="")
            .order_by("objet_type")
            .values_list("objet_type", flat=True)
            .distinct()
        )
        return [(valeur, LIBELLES_OBJET_TYPE.get(valeur, valeur)) for valeur in valeurs]

    @staticmethod
    def consulter(agissant, filtres, page):
        """CU-P1-03 : présente les entrées les plus récentes, paginées,
        filtrables par nature, auteur, période et objet concerné. § 2.4 :
        la consultation elle-même se journalise une fois par requête, pas
        une fois par ligne affichée — les filtres utilisés sont enregistrés,
        jamais le contenu retourné.

        Import différé : `administration.habilitations` importe déjà
        `ServiceJournal` pour journaliser un refus — un import en tête de
        module créerait un cycle. Voir docs/suivi/DECISIONS.md, D-14.
        """
        from administration.habilitations import verifier_habilitation

        verifier_habilitation(agissant, PERMISSION_CONSULTATION_JOURNAL)

        resultat = paginer(ServiceJournal._filtrer(filtres), page)
        ServiceJournal.enregistrer(
            type_action=TypeAction.CONSULTATION_JOURNAL,
            identifiant_saisi=getattr(agissant, "username", ""),
            detail=ServiceJournal._decrire_filtres(filtres),
            auteur=agissant,
        )
        return resultat

    @staticmethod
    def _filtrer(filtres):
        queryset = EntreeJournal.objects.select_related("auteur").all()
        if filtres.get("nature"):
            queryset = queryset.filter(type_action=filtres["nature"])
        if filtres.get("auteur"):
            queryset = queryset.filter(auteur__username__icontains=filtres["auteur"])
        if filtres.get("debut"):
            queryset = queryset.filter(cree_le__date__gte=filtres["debut"])
        if filtres.get("fin"):
            queryset = queryset.filter(cree_le__date__lte=filtres["fin"])
        if filtres.get("objet_type"):
            queryset = queryset.filter(objet_type=filtres["objet_type"])
        if filtres.get("objet_identifiant"):
            queryset = queryset.filter(objet_identifiant=filtres["objet_identifiant"])
        champ = ServiceJournal.CHAMPS_TRIABLES.get(
            (filtres.get("tri") or "").lstrip("-"), "cree_le"
        )
        ordre = f"-{champ}" if (filtres.get("tri") or "-horodatage").startswith("-") else champ
        return queryset.order_by(ordre, "-pk")

    @staticmethod
    def _decrire_filtres(filtres):
        actifs = {cle: valeur for cle, valeur in filtres.items() if valeur and cle != "tri"}
        if not actifs:
            return "Aucun filtre."
        return "Filtres : " + ", ".join(f"{cle}={valeur}" for cle, valeur in actifs.items())
