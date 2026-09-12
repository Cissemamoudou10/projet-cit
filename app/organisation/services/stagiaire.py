"""Gestion des stagiaires d'une session — CU-P3-05, RG-17.

Sous-ressource composée depuis l'écran d'une session, comme `Brigade`
(US-SES-02, étape 0.2) : pas de patron `ServiceGestion`. Pagination et
recherche propres (§ 9, Prompt 24) : à la différence des brigades, une
session compte couramment plus de vingt stagiaires — BNF-15 s'applique
réellement ici.
"""

from django.db import IntegrityError, transaction
from django.db.models import OuterRef, Subquery
from django.db.models.deletion import ProtectedError
from django.utils import timezone

from administration.habilitations import verifier_habilitation
from administration.models import TypeAction
from administration.services.journal import DonneesEntreeJournal, ServiceJournal
from noyau.exceptions import ErreurIntrouvable, ErreurValidation
from noyau.pagination import paginer
from noyau.services.base import ServiceBase
from noyau.services.gestion import decrire_opposants, valider_instance
from organisation.import_stagiaires.constantes import (
    CHAMPS_OBLIGATOIRES,
    libelle_champ,
    normaliser_texte,
)
from organisation.models import AffectationBrigade, Stagiaire
from organisation.services.session import PERMISSION_ECRITURE, PERMISSION_LECTURE

OBJET_TYPE = "stagiaire"
OBJET_TYPE_EXPORT = "export_stagiaires"

NON_AFFECTES = "non_affectes"


class ServiceStagiaire:
    DOMAINE = "organisation"
    PERMISSION_LECTURE = PERMISSION_LECTURE
    PERMISSION_ECRITURE = PERMISSION_ECRITURE

    @staticmethod
    def lister(agissant, session, filtres, page):
        queryset = ServiceStagiaire._queryset_filtree(agissant, session, filtres)
        return paginer(queryset, page)

    @staticmethod
    def lister_pour_export(agissant, session, filtres):
        """Mêmes filtres que `lister`, sans pagination — § 3, Prompt 26 :
        « ce qui est exporté, c'est exactement ce que l'écran montre »."""
        return ServiceStagiaire._queryset_filtree(agissant, session, filtres)

    @staticmethod
    def _queryset_filtree(agissant, session, filtres):
        """`brigade_designation` annoté par sous-requête corrélée (§ 9,
        Prompt 25) : la brigade d'affectation de chaque stagiaire, sans
        requête par ligne — US-SES-06 remplit cet emplacement, réservé
        implicitement par le modèle de liste avant que `AffectationBrigade`
        existe. Filtre de brigade (§ 2, Prompt 26) et recherche accent
        insensible (A5) ajoutés à US-SES-07."""
        verifier_habilitation(agissant, PERMISSION_LECTURE)
        brigade_ouverte = AffectationBrigade.objects.filter(
            stagiaire=OuterRef("pk"), date_fin__isnull=True
        ).values("brigade__designation")[:1]
        queryset = session.stagiaires.annotate(brigade_designation=Subquery(brigade_ouverte))
        filtres = filtres or {}
        etat = filtres.get("etat")
        if etat == "actifs":
            queryset = queryset.filter(radie=False)
        elif etat == "radies":
            queryset = queryset.filter(radie=True)
        brigade = filtres.get("brigade")
        if brigade == NON_AFFECTES:
            queryset = queryset.filter(brigade_designation__isnull=True)
        elif brigade:
            queryset = queryset.filter(
                affectations__brigade_id=brigade, affectations__date_fin__isnull=True
            )
        queryset = queryset.order_by("nom", "prenom")
        recherche = filtres.get("recherche")
        if recherche:
            queryset = queryset.filter(pk__in=_pks_correspondant(queryset, recherche))
        return queryset

    @staticmethod
    def compter(agissant, session):
        """Nombre de stagiaires enregistrés, pour la fiche de session (§ 9,
        Prompt 24) — l'emplacement « effectif réel » réservé par US-SES-04
        reste réservé : il dépend des affectations (US-SES-06), pas du
        nombre d'enregistrements."""
        verifier_habilitation(agissant, PERMISSION_LECTURE)
        return session.stagiaires.count()

    @staticmethod
    def obtenir(pk):
        try:
            return Stagiaire.objects.select_related("session").get(pk=pk)
        except Stagiaire.DoesNotExist as erreur:
            raise ErreurIntrouvable(f"Stagiaire introuvable (identifiant {pk}).") from erreur

    @classmethod
    def creer(cls, agissant, session, donnees):
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        cls._verifier_champs_obligatoires(donnees)
        stagiaire = Stagiaire(session=session, **donnees)
        valider_instance(stagiaire)
        try:
            with transaction.atomic():
                ServiceBase.creer(stagiaire, agissant)
                _journaliser(agissant, TypeAction.CREATION_ELEMENT_GESTION, stagiaire)
        except IntegrityError as erreur:
            raise _erreur_doublon(stagiaire) from erreur
        return stagiaire

    @classmethod
    def modifier(cls, agissant, stagiaire, donnees):
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        cls._verifier_champs_obligatoires(donnees)
        for champ, valeur in donnees.items():
            setattr(stagiaire, champ, valeur)
        valider_instance(stagiaire)
        try:
            with transaction.atomic():
                ServiceBase.modifier(stagiaire, agissant)
                _journaliser(agissant, TypeAction.MODIFICATION_ELEMENT_GESTION, stagiaire)
        except IntegrityError as erreur:
            raise _erreur_doublon(stagiaire) from erreur
        return stagiaire

    @staticmethod
    def radier(agissant, stagiaire, motif, date_radiation):
        """RADIER — constater qu'un stagiaire quitte la formation, jamais
        destructif (§ 7, Prompt 24) : à distinguer de `supprimer`, réservé à
        la correction d'une erreur de saisie."""
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        if not (motif or "").strip():
            raise ErreurValidation("Le motif de la radiation est obligatoire.")
        avant = _capturer_radiation(stagiaire)
        stagiaire.radie = True
        stagiaire.motif_radiation = motif.strip()
        stagiaire.date_radiation = date_radiation or timezone.localdate()
        with transaction.atomic():
            ServiceBase.modifier(stagiaire, agissant)
            _journaliser(
                agissant,
                TypeAction.MODIFICATION_ELEMENT_GESTION,
                stagiaire,
                valeur_avant=avant,
                valeur_apres=_capturer_radiation(stagiaire),
            )
        return stagiaire

    @staticmethod
    def deradier(agissant, stagiaire):
        """Défait une radiation saisie par erreur (§ 7, Prompt 24) : sans
        cette voie, la seule correction possible serait la suppression —
        donc la perte de l'historique que la radiation visait à préserver."""
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        avant = _capturer_radiation(stagiaire)
        stagiaire.radie = False
        stagiaire.motif_radiation = None
        stagiaire.date_radiation = None
        with transaction.atomic():
            ServiceBase.modifier(stagiaire, agissant)
            _journaliser(
                agissant,
                TypeAction.MODIFICATION_ELEMENT_GESTION,
                stagiaire,
                valeur_avant=avant,
                valeur_apres=_capturer_radiation(stagiaire),
            )
        return stagiaire

    @staticmethod
    def supprimer(agissant, stagiaire):
        """SUPPRIMER — corriger une erreur de saisie ou d'import, autorisé
        tant qu'aucune affectation ni note ne référence le stagiaire ; le
        `PROTECT` que poseront US-SES-06 et le paquetage Évaluations le
        bloquera automatiquement, sans une ligne de plus ici (D-23)."""
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        identifiant = str(stagiaire)
        try:
            with transaction.atomic():
                stagiaire.delete()
                ServiceJournal.enregistrer_detaillee(
                    DonneesEntreeJournal(
                        type_action=TypeAction.SUPPRESSION_ELEMENT_GESTION,
                        identifiant_saisi=identifiant,
                        auteur=agissant,
                        objet_type=OBJET_TYPE,
                        objet_identifiant=identifiant,
                    )
                )
        except ProtectedError as erreur:
            raise ErreurValidation(
                decrire_opposants(stagiaire, erreur.protected_objects)
            ) from erreur

    @staticmethod
    def exporter(agissant, session, filtres, description_filtre):
        """Un export fait sortir des données nominatives du périmètre du
        système (§ 6, Prompt 26) : journalisé, avec le contexte et le
        compte, JAMAIS les identités — même règle qu'à l'import (RG-27,
        D-98). Retourne les stagiaires à écrire, l'appelant choisit le
        format."""
        stagiaires = list(ServiceStagiaire.lister_pour_export(agissant, session, filtres))
        ServiceJournal.enregistrer_detaillee(
            DonneesEntreeJournal(
                type_action=TypeAction.EXPORT_DONNEES,
                identifiant_saisi=f"Export des stagiaires — {session}",
                auteur=agissant,
                objet_type=OBJET_TYPE_EXPORT,
                objet_identifiant=str(session.pk),
                valeur_apres={
                    "session": str(session),
                    "filtre": description_filtre,
                    "nombre_lignes": len(stagiaires),
                },
            )
        )
        return stagiaires

    @staticmethod
    def _verifier_champs_obligatoires(donnees):
        """BNF-10 : nomme le champ manquant, pas un refus générique — même
        exigence que le compte rendu d'import (A4, § 12, Prompt 24)."""
        for champ in CHAMPS_OBLIGATOIRES:
            if not (donnees.get(champ) or "").strip():
                raise ErreurValidation(f"Le champ « {libelle_champ(champ)} » est obligatoire.")


def _pks_correspondant(queryset, recherche):
    """Recherche insensible à la casse ET aux accents (A5, § 2, Prompt 26) :
    PostgreSQL n'a pas l'extension `unaccent` installée (seule `btree_gist`
    l'est, pour RG-24) — comparaison en Python avec la même normalisation
    que le lecteur de fichier d'US-SES-05 (`normaliser_texte`), au lieu
    d'introduire une nouvelle dépendance PostgreSQL pour une liste bornée à
    l'échelle d'une session."""
    cible = normaliser_texte(recherche)
    return [
        stagiaire.pk
        for stagiaire in queryset.only("pk", "matricule", "nom", "prenom")
        if cible in normaliser_texte(stagiaire.matricule)
        or cible in normaliser_texte(stagiaire.nom)
        or cible in normaliser_texte(stagiaire.prenom)
    ]


def _erreur_doublon(stagiaire):
    existant = (
        Stagiaire.objects.filter(session=stagiaire.session, matricule__iexact=stagiaire.matricule)
        .exclude(pk=stagiaire.pk)
        .first()
    )
    return ErreurValidation(
        f"« {stagiaire.matricule} » est déjà attribué à {existant} de la même session."
    )


def _capturer_radiation(stagiaire):
    return {
        "radie": stagiaire.radie,
        "motif_radiation": stagiaire.motif_radiation,
        "date_radiation": (
            stagiaire.date_radiation.isoformat() if stagiaire.date_radiation else None
        ),
    }


def _journaliser(agissant, nature, stagiaire, *, valeur_avant=None, valeur_apres=None):
    identifiant = str(stagiaire)
    ServiceJournal.enregistrer_detaillee(
        DonneesEntreeJournal(
            type_action=nature,
            identifiant_saisi=identifiant,
            auteur=agissant,
            objet_type=OBJET_TYPE,
            objet_identifiant=identifiant,
            valeur_avant=valeur_avant,
            valeur_apres=valeur_apres,
        )
    )
