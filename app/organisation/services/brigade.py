"""Constitution des brigades d'une session — CU-P3-02, RG-12, RG-15, RG-16.

Sous-ressource composée depuis l'écran d'une session, comme `ElementReferentiel`
l'est depuis l'écran d'une formation (US-SES-01, étape 0.2) : pas de patron
`ServiceGestion` — pas d'écran de premier niveau, pas de pagination, pas de
recherche texte libre — mêmes fonctions libres de `noyau/services/gestion.py`
que `ServiceReferentiel`.

Un service ne connaît pas la requête HTTP — voir .claude/rules/services.md.
"""

from django.db import IntegrityError, transaction
from django.db.models import Sum
from django.db.models.deletion import ProtectedError
from django.utils import timezone

from administration.habilitations import verifier_habilitation
from administration.models import TypeAction
from administration.services.journal import DonneesEntreeJournal, ServiceJournal
from noyau.exceptions import ErreurIntrouvable, ErreurValidation
from noyau.services.base import ServiceBase
from noyau.services.gestion import avertissement, decrire_opposants, valider_instance
from organisation.models import Brigade
from organisation.services.session import PERMISSION_ECRITURE, PERMISSION_LECTURE

OBJET_TYPE = "brigade"


class ServiceBrigade:
    DOMAINE = "organisation"
    PERMISSION_LECTURE = PERMISSION_LECTURE
    PERMISSION_ECRITURE = PERMISSION_ECRITURE

    @staticmethod
    def lister(agissant, session):
        """`select_related("salle_attitree__lieu")` sur une chaîne de
        caractères, résolue par l'ORM au moment de la requête — jamais un
        `import ressources` (méthode D-52, US-SES-03) : c'est ce qui permet
        d'afficher la salle attitrée de chaque brigade sans une requête par
        ligne."""
        verifier_habilitation(agissant, PERMISSION_LECTURE)
        return session.brigades.select_related("salle_attitree__lieu").order_by("designation")

    @staticmethod
    def indicateur_effectif(session):
        """RG-15 — un état permanent, pas un avertissement qui passe (§ 5,
        Prompt 21) : recalculé à chaque affichage de l'écran des brigades,
        jamais posé une seule fois via le mécanisme `avertissement`."""
        somme = session.brigades.aggregate(total=Sum("effectif_previsionnel"))["total"] or 0
        return {
            "effectif_attendu": session.effectif_attendu,
            "somme_prevue": somme,
            "ecart": somme - session.effectif_attendu,
        }

    @staticmethod
    def obtenir(pk):
        try:
            return Brigade.objects.select_related("session").get(pk=pk)
        except Brigade.DoesNotExist as erreur:
            raise ErreurIntrouvable(f"Brigade introuvable (identifiant {pk}).") from erreur

    @staticmethod
    def creer(agissant, session, donnees):
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        brigade = Brigade(session=session, **donnees)
        valider_instance(brigade)
        try:
            with transaction.atomic():
                ServiceBase.creer(brigade, agissant)
                _journaliser(agissant, TypeAction.CREATION_ELEMENT_GESTION, brigade)
        except IntegrityError as erreur:
            raise _erreur_doublon(brigade) from erreur
        brigade.avertissements = _avertissements_a3(brigade)
        return brigade

    @staticmethod
    def modifier(agissant, brigade, donnees):
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        for champ, valeur in donnees.items():
            setattr(brigade, champ, valeur)
        valider_instance(brigade)
        try:
            with transaction.atomic():
                ServiceBase.modifier(brigade, agissant)
                _journaliser(agissant, TypeAction.MODIFICATION_ELEMENT_GESTION, brigade)
        except IntegrityError as erreur:
            raise _erreur_doublon(brigade) from erreur
        return brigade

    @staticmethod
    def supprimer(agissant, brigade):
        """Critère 2 (§ 4, Prompt 21) : refuse la suppression de la
        DERNIÈRE brigade d'une session avant même de tenter l'écriture —
        message désignant l'action corrective. `ProtectedError` reste le
        juge pour un programme en cours (critère 5, reporté à US-PLAN-03/04,
        § 9) : rien à écrire ici tant qu'aucun modèle ne pointe vers
        `Brigade` en `PROTECT`.
        """
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        if brigade.session.brigades.count() <= 1:
            raise ErreurValidation(
                f"« {brigade.designation} » est la seule brigade de cette session : "
                "constituez-en une autre avant de la supprimer, ou supprimez la session entière."
            )
        try:
            with transaction.atomic():
                brigade.delete()
                _journaliser(agissant, TypeAction.SUPPRESSION_ELEMENT_GESTION, brigade)
        except ProtectedError as erreur:
            raise ErreurValidation(
                decrire_opposants(brigade, erreur.protected_objects)
            ) from erreur


def _erreur_doublon(brigade):
    existant = (
        Brigade.objects.filter(session=brigade.session, designation__iexact=brigade.designation)
        .exclude(pk=brigade.pk)
        .first()
    )
    return ErreurValidation(
        f"« {brigade.designation} » est déjà attribué à {existant} de la même session."
    )


def _avertissements_a3(brigade):
    """Enchaînement A3 — une brigade créée après la date de début de sa
    session : avertissement rappelant que sa progression démarrera en
    décalage, jamais rattrapé (RG-16). Le volet « programme à régénérer »
    d'A3 suppose `ProgrammeHebdomadaire` : hors périmètre, voir § 9,
    Prompt 21."""
    session = brigade.session
    if timezone.localdate() <= session.date_debut:
        return []
    return [
        avertissement(
            "brigade_ouverte_en_decalage",
            f"La session a débuté le {session.date_debut:%d/%m/%Y} : la progression de "
            f"« {brigade.designation} » démarrera en décalage (RG-16).",
        )
    ]


def _journaliser(agissant, nature, brigade):
    identifiant = str(brigade)
    ServiceJournal.enregistrer_detaillee(
        DonneesEntreeJournal(
            type_action=nature,
            identifiant_saisi=identifiant,
            auteur=agissant,
            objet_type=OBJET_TYPE,
            objet_identifiant=identifiant,
        )
    )
