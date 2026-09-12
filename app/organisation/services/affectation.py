"""Affectation des stagiaires aux brigades — CU-P3-06, RG-19, RG-20, Prompt 25.

Trois contrôles à l'affectation individuelle (§ 4), dans cet ordre — tous
REFUS : stagiaire radié ; RG-20, déjà affecté dans la session (la brigade
actuelle est nommée, le déplacement est l'enchaînement distinct qu'offre
`deplacer`) ; RG-19, capacité de la salle atteinte (marge chiffrée, BNF-10).
Deux AVERTISSEMENTS, jamais des refus : effectif déclaré dépassé (RG-65,
comme RG-15 à US-SES-02) ; brigade sans salle attitrée, RG-19 alors
invérifiable.

Sous-ressource composée depuis l'écran d'une session, comme `ServiceBrigade`
et `ServiceStagiaire` : pas de patron `ServiceGestion`.
"""

from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError, transaction
from django.db.models import Prefetch
from django.utils import timezone

from administration.habilitations import verifier_habilitation
from administration.models import TypeAction
from administration.services.journal import DonneesEntreeJournal, ServiceJournal
from noyau.exceptions import ErreurValidation
from noyau.services.base import ServiceBase
from noyau.services.gestion import avertissement
from organisation.models import AffectationBrigade
from organisation.services.brigade import ServiceBrigade
from organisation.services.session import PERMISSION_ECRITURE, PERMISSION_LECTURE

OBJET_TYPE = "affectation_brigade"

AVERTISSEMENT_DEPLACEMENT = avertissement(
    "deplacement_historique",
    "Les évaluations et la progression du stagiaire restent rattachées à son "
    "parcours : sa brigade d'origine figurera dans son historique d'affectations.",
)


class ServiceAffectation:
    DOMAINE = "organisation"
    PERMISSION_LECTURE = PERMISSION_LECTURE
    PERMISSION_ECRITURE = PERMISSION_ECRITURE

    @staticmethod
    def affectation_ouverte(stagiaire):
        return (
            stagiaire.affectations.filter(date_fin__isnull=True).select_related("brigade").first()
        )

    @staticmethod
    def brigades_avec_affectations(agissant, session):
        """Brigades de la session, chacune avec ses affectations OUVERTES de
        stagiaires non radiés déjà chargées (`brigade.affectations_ouvertes`)
        — écran de répartition (§ 7, Prompt 25), `Prefetch` pour ne jamais
        payer une requête par brigade (`python.md`)."""
        affectations_ouvertes = (
            AffectationBrigade.objects.filter(date_fin__isnull=True, stagiaire__radie=False)
            .select_related("stagiaire")
            .order_by("stagiaire__nom", "stagiaire__prenom")
        )
        return ServiceBrigade.lister(agissant, session).prefetch_related(
            Prefetch(
                "affectations", queryset=affectations_ouvertes, to_attr="affectations_ouvertes"
            )
        )

    @staticmethod
    def historique(agissant, stagiaire):
        """RG-20 : consultable, dates d'effet et de fin — le conserver sans
        pouvoir le lire ne servirait à rien (§ 7, Prompt 25)."""
        verifier_habilitation(agissant, PERMISSION_LECTURE)
        return stagiaire.affectations.select_related("brigade").order_by("-date_effet")

    @classmethod
    def affecter(cls, agissant, stagiaire, brigade, date_effet=None):
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        date_effet = date_effet or timezone.localdate()
        cls._verifier_date_effet(date_effet)
        avertissements = cls.verifier_controles(stagiaire, brigade)
        avertissements += avertissement_affectation_tardive(stagiaire.session)
        instance = AffectationBrigade(stagiaire=stagiaire, brigade=brigade, date_effet=date_effet)
        try:
            with transaction.atomic():
                ServiceBase.creer(instance, agissant)
                _journaliser(agissant, TypeAction.CREATION_ELEMENT_GESTION, instance)
        except IntegrityError as erreur:
            raise ErreurValidation(
                f"{stagiaire} a déjà une affectation ouverte : reprenez depuis la liste "
                "des stagiaires."
            ) from erreur
        instance.avertissements = avertissements
        return instance

    @classmethod
    def deplacer(cls, agissant, stagiaire, nouvelle_brigade, date_effet):
        """RG-20, enchaînement A2 : ferme l'affectation en cours à
        `date_effet`, en ouvre une seconde — jamais une ligne écrasée."""
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        actuelle = cls.affectation_ouverte(stagiaire)
        if actuelle is None:
            raise ErreurValidation(f"{stagiaire} n'a aucune affectation ouverte à déplacer.")
        cls._verifier_date_effet(date_effet)
        if date_effet <= actuelle.date_effet:
            raise ErreurValidation(
                "La date d'effet du déplacement doit être postérieure à celle de "
                f"l'affectation en cours ({actuelle.date_effet:%d/%m/%Y})."
            )
        avertissements = cls.verifier_controles(stagiaire, nouvelle_brigade, exclut=actuelle)
        nouvelle = AffectationBrigade(
            stagiaire=stagiaire, brigade=nouvelle_brigade, date_effet=date_effet
        )
        with transaction.atomic():
            actuelle.date_fin = date_effet
            ServiceBase.modifier(actuelle, agissant)
            ServiceBase.creer(nouvelle, agissant)
            _journaliser_deplacement(
                agissant, stagiaire, actuelle.brigade, nouvelle_brigade, date_effet
            )
        nouvelle.avertissements = [*avertissements, AVERTISSEMENT_DEPLACEMENT]
        return nouvelle

    @staticmethod
    def retirer(agissant, stagiaire, date_fin=None):
        """Retrait pur et simple, sans nouvelle ouverture — le cas d'un
        stagiaire radié en cours de session (§ 6, Prompt 25). Geste manuel,
        distinct de la radiation elle-même : radier ne ferme jamais
        l'affectation automatiquement (DECISIONS.md).

        `date_fin` jamais future, même principe que `_verifier_date_effet`
        (D-106) : une affectation FERMÉE doit l'être réellement aujourd'hui,
        pas par anticipation — sans quoi l'effectif réel resterait faux
        jusqu'à cette date future."""
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        actuelle = ServiceAffectation.affectation_ouverte(stagiaire)
        if actuelle is None:
            raise ErreurValidation(f"{stagiaire} n'a aucune affectation ouverte à retirer.")
        date_fin = date_fin or timezone.localdate()
        ServiceAffectation._verifier_date_effet(date_fin)
        if date_fin <= actuelle.date_effet:
            raise ErreurValidation(
                "La date de fin doit être postérieure à la date d'effet "
                f"({actuelle.date_effet:%d/%m/%Y})."
            )
        with transaction.atomic():
            actuelle.date_fin = date_fin
            ServiceBase.modifier(actuelle, agissant)
            _journaliser_retrait(agissant, stagiaire, actuelle.brigade, date_fin)
        return actuelle

    @classmethod
    def verifier_controles(cls, stagiaire, brigade, exclut=None):
        if stagiaire.radie:
            raise ErreurValidation(
                f"{stagiaire} a été radié : impossible de l'affecter à une brigade."
            )
        actuelle = cls.affectation_ouverte(stagiaire)
        if actuelle is not None and actuelle != exclut:
            raise ErreurValidation(
                f"{stagiaire} est déjà affecté à « {actuelle.brigade.designation} » : "
                "déplacez-le plutôt que de créer une nouvelle affectation."
            )
        return cls._verifier_capacite(brigade)

    @staticmethod
    def _verifier_capacite(brigade):
        try:
            salle = brigade.salle_attitree
        except ObjectDoesNotExist:
            return [
                avertissement(
                    "brigade_sans_salle",
                    f"« {brigade.designation} » n'a pas encore de salle attitrée : le "
                    "contrôle de capacité (RG-19) ne peut pas s'appliquer.",
                )
            ]
        capacite = salle.lieu.capacite
        if not capacite:
            return []
        effectif_actuel = ServiceBrigade.effectif_reel(brigade)
        if effectif_actuel + 1 > capacite:
            marge = max(0, capacite - effectif_actuel)
            raise ErreurValidation(
                f"« {brigade.designation} » a atteint la capacité de sa salle "
                f"({capacite} places) : marge restante {marge}."
            )
        if effectif_actuel + 1 > brigade.effectif_previsionnel:
            return [
                avertissement(
                    "effectif_declare_depasse",
                    f"« {brigade.designation} » dépasse son effectif déclaré "
                    f"({brigade.effectif_previsionnel}).",
                )
            ]
        return []

    @staticmethod
    def _verifier_date_effet(date):
        if date > timezone.localdate():
            raise ErreurValidation(
                "Cette date ne peut pas être future : un changement d'affectation (ouverture "
                "ou fermeture) doit être vrai aujourd'hui."
            )


def avertissement_affectation_tardive(session):
    """Part implantable de l'enchaînement A3 reporté (§ 9, Prompt 25) : un
    stagiaire affecté après la date de début de sa session, comme A3
    d'US-SES-02 pour une brigade créée tardivement."""
    if timezone.localdate() <= session.date_debut:
        return []
    return [
        avertissement(
            "affectation_tardive",
            f"La session a débuté le {session.date_debut:%d/%m/%Y} : ce stagiaire "
            "rejoint sa brigade en décalage.",
        )
    ]


def _journaliser(agissant, nature, affectation, *, valeur_avant=None, valeur_apres=None):
    ServiceJournal.enregistrer_detaillee(
        DonneesEntreeJournal(
            type_action=nature,
            identifiant_saisi=str(affectation),
            auteur=agissant,
            objet_type=OBJET_TYPE,
            objet_identifiant=str(affectation.pk),
            valeur_avant=valeur_avant,
            valeur_apres=valeur_apres,
        )
    )


def _journaliser_deplacement(agissant, stagiaire, ancienne_brigade, nouvelle_brigade, date_effet):
    ServiceJournal.enregistrer_detaillee(
        DonneesEntreeJournal(
            type_action=TypeAction.MODIFICATION_ELEMENT_GESTION,
            identifiant_saisi=f"Déplacement de {stagiaire}",
            auteur=agissant,
            objet_type=OBJET_TYPE,
            objet_identifiant=str(stagiaire.pk),
            valeur_avant={"brigade": str(ancienne_brigade)},
            valeur_apres={"brigade": str(nouvelle_brigade), "date_effet": date_effet.isoformat()},
        )
    )


def _journaliser_retrait(agissant, stagiaire, brigade, date_fin):
    ServiceJournal.enregistrer_detaillee(
        DonneesEntreeJournal(
            type_action=TypeAction.MODIFICATION_ELEMENT_GESTION,
            identifiant_saisi=f"Retrait de {stagiaire}",
            auteur=agissant,
            objet_type=OBJET_TYPE,
            objet_identifiant=str(stagiaire.pk),
            valeur_avant={"brigade": str(brigade), "ouverte": True},
            valeur_apres={"brigade": str(brigade), "date_fin": date_fin.isoformat()},
        )
    )
