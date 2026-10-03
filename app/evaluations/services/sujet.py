"""`ServiceSujet` — US-EVAL-03, RG-50, RG-50 bis, RG-51, CLS-05, Prompt 37.

Aucune règle métier dans les vues ni les formulaires — voir
.claude/rules/services.md. A1/CLS-05 : seule une référence est stockée,
jamais le sujet lui-même. A7 : le journal ne contient jamais une référence,
seulement le rang du sujet concerné.
"""

from django.db import transaction
from django.utils import timezone

from administration.habilitations import verifier_habilitation
from administration.models import TypeAction
from administration.services.journal import DonneesEntreeJournal, ServiceJournal
from evaluations.models import Sujet, TypeEvaluation
from noyau.exceptions import ErreurIntrouvable, ErreurValidation
from noyau.services.base import ServiceBase
from noyau.services.gestion import valider_instance

PERMISSION_ECRITURE = "noyau.evaluations_ecriture"


def _jour_epreuve(evaluation):
    return evaluation.seance.debut.date() if evaluation.seance_id else evaluation.date


def _verifier_avant_epreuve(evaluation):
    """A9 : à partir du jour de l'épreuve, sélection, changement et
    suppression sont refusés — la seule borne sûre sans l'heure de
    l'épreuve (US-EVAL-04)."""
    jour = _jour_epreuve(evaluation)
    if jour and jour <= timezone.localdate():
        raise ErreurValidation(
            f"{jour:%d/%m/%Y} : le jour de l'épreuve est atteint, cette action n'est plus "
            "possible (RG-51)."
        )


def _verifier_reference_disponible(evaluation, reference, exclu=None):
    queryset = evaluation.sujets.exclude(pk=exclu.pk if exclu else None)
    if queryset.filter(reference__iexact=reference.strip()).exists():
        raise ErreurValidation(
            f"« {reference} » désigne déjà un sujet de cette évaluation — choisissez une "
            "référence distincte."
        )


def _verifier_date_depot(date_depot):
    if date_depot and date_depot > timezone.localdate():
        raise ErreurValidation(
            f"{date_depot:%d/%m/%Y} est une date future : la date de dépôt ne peut être "
            "postérieure à aujourd'hui."
        )


def _journaliser(agissant, type_action, sujet, detail=""):
    ServiceJournal.enregistrer_detaillee(
        DonneesEntreeJournal(
            type_action=type_action,
            identifiant_saisi=str(sujet),
            detail=detail,
            auteur=agissant,
            objet_type="sujet",
            objet_identifiant=str(sujet.pk),
        )
    )


def _journaliser_consultation(agissant, evaluation):
    ServiceJournal.enregistrer_detaillee(
        DonneesEntreeJournal(
            type_action=TypeAction.CONSULTATION_SUJETS,
            identifiant_saisi=getattr(agissant, "username", ""),
            auteur=agissant,
            objet_type="evaluation",
            objet_identifiant=str(evaluation.pk),
        )
    )


def _prochain_rang(evaluation):
    maximum = max(evaluation.sujets.values_list("rang", flat=True), default=0)
    return maximum + 1


def _verifier_nombre_sujets(evaluation):
    """C2/RG-50, E1 : deux au plus pour une certificative, un seul pour une
    formative — le rang (A2) empêche un troisième en base, cette vérification
    donne un message clair avant l'IntegrityError."""
    limite = 2 if evaluation.type == TypeEvaluation.CERTIFICATIVE else 1
    if evaluation.sujets.count() >= limite:
        raise ErreurValidation(
            f"{evaluation} compte déjà {limite} sujet(s) — c'est le maximum pour une "
            f"évaluation {evaluation.get_type_display().lower()} (RG-50)."
        )


class ServiceSujet:
    DOMAINE = "evaluations"
    PERMISSION_ECRITURE = PERMISSION_ECRITURE

    @staticmethod
    def enregistrer(agissant, evaluation, donnees):
        """A2 : rang attribué par le service, jamais saisi — 1 puis 2."""
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        _verifier_nombre_sujets(evaluation)
        reference = (donnees.get("reference") or "").strip()
        _verifier_date_depot(donnees.get("date_depot"))
        _verifier_reference_disponible(evaluation, reference)
        sujet = Sujet(
            evaluation=evaluation,
            rang=_prochain_rang(evaluation),
            reference=reference,
            date_depot=donnees.get("date_depot"),
        )
        valider_instance(sujet)
        with transaction.atomic():
            ServiceBase.creer(sujet, agissant)
            _journaliser(agissant, TypeAction.CREATION_ELEMENT_GESTION, sujet)
        return sujet

    @staticmethod
    def corriger(agissant, sujet, donnees):
        """A10 : une formative se corrige à tout moment, y compris après
        l'épreuve — une certificative, seulement avant."""
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        if sujet.evaluation.type == TypeEvaluation.CERTIFICATIVE:
            _verifier_avant_epreuve(sujet.evaluation)
        reference = (donnees.get("reference") or "").strip()
        _verifier_date_depot(donnees.get("date_depot"))
        _verifier_reference_disponible(sujet.evaluation, reference, exclu=sujet)
        sujet.reference = reference
        sujet.date_depot = donnees.get("date_depot")
        valider_instance(sujet)
        with transaction.atomic():
            ServiceBase.modifier(sujet, agissant)
            _journaliser(agissant, TypeAction.MODIFICATION_ELEMENT_GESTION, sujet)
        return sujet

    @staticmethod
    def supprimer(agissant, sujet):
        """A10 : un sujet retenu ne se supprime jamais — changer d'abord la
        sélection (`changer_retenu`). Un sujet non retenu, avant l'épreuve
        seulement (B7)."""
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        if sujet.retenu:
            raise ErreurValidation(
                "Ce sujet est retenu : changez la sélection avant de le supprimer."
            )
        _verifier_avant_epreuve(sujet.evaluation)
        with transaction.atomic():
            _journaliser(agissant, TypeAction.SUPPRESSION_ELEMENT_GESTION, sujet)
            sujet.delete()

    @staticmethod
    def retenir(agissant, sujet, confirmation=False):
        """C4 : une certificative à un seul sujet exige une confirmation
        explicite — jamais un blocage, l'utilisateur peut toujours confirmer
        (RG-50 bis)."""
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        evaluation = sujet.evaluation
        if evaluation.type != TypeEvaluation.CERTIFICATIVE:
            raise ErreurValidation(
                "Une évaluation formative n'a qu'un sujet : il n'y a rien à retenir (RG-50)."
            )
        if evaluation.sujets.filter(retenu=True).exclude(pk=sujet.pk).exists():
            raise ErreurValidation(
                "Un sujet est déjà retenu pour cette évaluation : changez la sélection "
                "plutôt que d'en retenir un second."
            )
        _verifier_avant_epreuve(evaluation)
        derogation = evaluation.sujets.count() == 1
        if derogation and not confirmation:
            raise ErreurValidation(
                f"{evaluation} ne compte qu'un seul sujet enregistré : RG-50 en attend deux. "
                "Confirmez explicitement pour le retenir malgré tout."
            )
        detail = f"Sujet n° {sujet.rang} retenu."
        if derogation:
            detail += " Dérogation à RG-50 (un seul sujet enregistré), confirmée."
        with transaction.atomic():
            sujet.retenu = True
            ServiceBase.modifier(sujet, agissant)
            _journaliser(agissant, TypeAction.SELECTION_SUJET, sujet, detail)
        return sujet

    @staticmethod
    def changer_retenu(agissant, nouveau_sujet, motif):
        """C5 : motif obligatoire, mentionnant la décision de commission
        (RG-50 bis) — le journal porte l'ancien ET le nouveau rang (A7),
        jamais une référence."""
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        motif = (motif or "").strip()
        if not motif:
            raise ErreurValidation(
                "Un motif est obligatoire pour changer le sujet retenu, mentionnant la "
                "décision de la commission (RG-50 bis)."
            )
        evaluation = nouveau_sujet.evaluation
        _verifier_avant_epreuve(evaluation)
        ancien = evaluation.sujets.filter(retenu=True).exclude(pk=nouveau_sujet.pk).first()
        if ancien is None:
            raise ErreurValidation(
                "Aucun sujet n'est retenu pour cette évaluation : utilisez la retenue "
                "initiale plutôt qu'un changement."
            )
        detail = (
            f"Sujet retenu changé : n° {ancien.rang} → n° {nouveau_sujet.rang}. Motif : {motif}"
        )
        with transaction.atomic():
            ancien.retenu = False
            ServiceBase.modifier(ancien, agissant)
            nouveau_sujet.retenu = True
            ServiceBase.modifier(nouveau_sujet, agissant)
            _journaliser(agissant, TypeAction.SELECTION_SUJET, nouveau_sujet, detail)
        return nouveau_sujet

    @staticmethod
    def consulter(agissant, evaluation):
        """A5/A6 : visibilité réservée à `evaluations_ecriture` — pas de
        permission de lecture séparée pour les sujets. Chaque appel qui
        passe le contrôle journalise une consultation, qu'il y ait ou non
        un sujet à afficher (RG-51)."""
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        sujets = list(evaluation.sujets.order_by("rang"))
        _journaliser_consultation(agissant, evaluation)
        return sujets

    @staticmethod
    def sujet_retenu(evaluation):
        """A12 : prédicat exposé à US-EVAL-04 (report C9) — rend le sujet
        retenu, ou `None`."""
        return evaluation.sujets.filter(retenu=True).first()

    @staticmethod
    def obtenir(pk):
        try:
            return Sujet.objects.select_related("evaluation").get(pk=pk)
        except Sujet.DoesNotExist as erreur:
            raise ErreurIntrouvable(f"Sujet introuvable (identifiant {pk}).") from erreur
