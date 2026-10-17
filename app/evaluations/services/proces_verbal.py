"""`ServiceProcesVerbal` — US-EVAL-07, RG-58, RG-59, CU-P6-07, prompt 46,
point 3.

V10 : générer suit `evaluations_ecriture` (cellule examens seule) ;
consulter et télécharger suivent `evaluations_lecture` (examens ET
Direction de Formation) — à la différence des notes/sujets/moyennes,
réservés à la seule écriture : un résultat déjà officialisé n'a plus la
confidentialité d'une note brute.

V2 : le PDF est CONSERVÉ — télécharger ne recalcule jamais, c'est le seul
moyen d'être réellement « à l'identique » quand le gabarit a changé entre
la génération et la consultation. V4 : calcul, production du PDF et
verrouillage dans une seule transaction — si le PDF échoue, rien n'est
écrit ni verrouillé (le rendu se fait hors transaction, avant qu'elle ne
s'ouvre). V7 : « corriger » n'écrase jamais une version, `generer` en crée
une nouvelle (version + 1) — l'ancienne reste consultable.

Aucune règle métier dans les vues ni les formulaires — voir
.claude/rules/services.md.
"""

import dataclasses
import decimal

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from administration.habilitations import verifier_habilitation
from administration.models import TypeAction, TypeDocument
from administration.services.document import ServiceDocument
from administration.services.journal import DonneesEntreeJournal, ServiceJournal
from evaluations.models import ProcesVerbal, TypeProcesVerbal
from evaluations.services.moyenne import ServiceMoyenne, evaluations_de_la_session
from noyau.exceptions import ErreurIntrouvable, ErreurValidation
from noyau.services.base import ServiceBase
from noyau.services.gestion import valider_instance

PERMISSION_ECRITURE = "noyau.evaluations_ecriture"
PERMISSION_LECTURE = "noyau.evaluations_lecture"

GABARIT_PDF_PROCES_VERBAL = "evaluations/pdf/proces_verbal.html"

_TYPE_DOCUMENT_PAR_TYPE_PV = {
    TypeProcesVerbal.FIN_DE_FORMATION: TypeDocument.PROCES_VERBAL_FIN_FORMATION,
    TypeProcesVerbal.EVALUATION: TypeDocument.PROCES_VERBAL_EVALUATION,
}


@dataclasses.dataclass(frozen=True)
class LigneDecision:
    stagiaire: object
    brigade: object
    valeur: decimal.Decimal
    rang_session: int
    rang_brigade: int
    decision: str


@dataclasses.dataclass(frozen=True)
class ApercuProcesVerbal:
    lignes: list
    manquants: list
    seuil: decimal.Decimal


def _seuil_admission() -> decimal.Decimal:
    return decimal.Decimal(settings.SEUIL_ADMISSION_PROCES_VERBAL)


def _decision(valeur, seuil) -> str:
    return "Admis" if valeur >= seuil else "Ajourné"


def _valeur_resultat(resultat):
    """`ResultatStagiaire.moyenne` (fin de formation) ou
    `ResultatModule.note` (une évaluation) — même forme sinon."""
    return resultat.moyenne if hasattr(resultat, "moyenne") else resultat.note


def _rapport(agissant, session, evaluation):
    if evaluation is None:
        return ServiceMoyenne.calculer(agissant, session)
    return ServiceMoyenne.calculer_module(agissant, session, evaluation.element_referentiel)


def _apercu(agissant, session, evaluation):
    rapport = _rapport(agissant, session, evaluation)
    seuil = _seuil_admission()
    lignes = [
        LigneDecision(
            stagiaire=resultat.stagiaire,
            brigade=resultat.brigade,
            valeur=_valeur_resultat(resultat),
            rang_session=resultat.rang_session,
            rang_brigade=resultat.rang_brigade,
            decision=_decision(_valeur_resultat(resultat), seuil),
        )
        for resultat in rapport.resultats
    ]
    return ApercuProcesVerbal(lignes=lignes, manquants=rapport.manquants, seuil=seuil)


def _message_manquants(manquants):
    detail = "; ".join(
        f"{manquant.module.matiere} — {manquant.brigade} — {manquant.stagiaire}"
        for manquant in manquants
    )
    return (
        f"{len(manquants)} note(s) manquante(s), par module et par brigade : {detail} — "
        "complétez la saisie avant de générer (M5)."
    )


def _evaluations_a_verrouiller(session, type_pv, evaluation):
    if type_pv == TypeProcesVerbal.EVALUATION:
        return [evaluation]
    return evaluations_de_la_session(session)


def _rendre_pdf(type_pv, session, evaluation, apercu, metadonnees):
    contexte = {
        "session": session,
        "evaluation": evaluation,
        "lignes": apercu.lignes,
        "seuil": apercu.seuil,
        **metadonnees,
    }
    return ServiceDocument.produire(
        _TYPE_DOCUMENT_PAR_TYPE_PV[type_pv], GABARIT_PDF_PROCES_VERBAL, contexte
    )


def _enregistrer(agissant, proces_verbal, type_pv, session, evaluation):
    """V4 : verrouillage et journalisation dans la MÊME transaction que
    l'enregistrement — le PDF, lui, a déjà été rendu avant cet appel."""
    with transaction.atomic():
        ServiceBase.creer(proces_verbal, agissant)
        proces_verbal.evaluations_couvertes.set(
            _evaluations_a_verrouiller(session, type_pv, evaluation)
        )
        _journaliser_generation(agissant, proces_verbal)


def _prochaine_version(type_pv, session, evaluation):
    derniere = (
        ProcesVerbal.objects.filter(type=type_pv, session=session, evaluation=evaluation)
        .order_by("-version")
        .first()
    )
    return (derniere.version + 1) if derniere else 1


def _journaliser_generation(agissant, proces_verbal):
    ServiceJournal.enregistrer_detaillee(
        DonneesEntreeJournal(
            type_action=TypeAction.GENERATION_PROCES_VERBAL,
            identifiant_saisi=str(proces_verbal),
            auteur=agissant,
            objet_type="proces_verbal",
            objet_identifiant=str(proces_verbal.pk),
        )
    )


def _journaliser_telechargement(agissant, proces_verbal):
    ServiceJournal.enregistrer_detaillee(
        DonneesEntreeJournal(
            type_action=TypeAction.TELECHARGEMENT_PROCES_VERBAL,
            identifiant_saisi=str(proces_verbal),
            auteur=agissant,
            objet_type="proces_verbal",
            objet_identifiant=str(proces_verbal.pk),
        )
    )


class ServiceProcesVerbal:
    DOMAINE = "evaluations"
    PERMISSION_ECRITURE = PERMISSION_ECRITURE
    PERMISSION_LECTURE = PERMISSION_LECTURE

    @staticmethod
    def apercu(agissant, session, evaluation=None) -> ApercuProcesVerbal:
        """V9 : aperçu avant génération — moyennes, rangs et décisions,
        sans rien écrire."""
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        return _apercu(agissant, session, evaluation)

    @staticmethod
    def generer(agissant, session, type_pv, evaluation=None, numero=""):
        """V4/V5/V7 : refuse sur note manquante (avant tout calcul coûteux
        ou écriture) ; rend le PDF hors transaction (si l'étape échoue,
        rien n'est écrit) ; verrouille les évaluations couvertes dans la
        même transaction que l'enregistrement."""
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        apercu = _apercu(agissant, session, evaluation)
        if apercu.manquants:
            raise ErreurValidation(_message_manquants(apercu.manquants))
        # Calculés AVANT le rendu : le PDF les affiche, mais la ligne
        # `ProcesVerbal` elle-même n'existe pas encore à ce stade (V4, le
        # PDF se rend hors transaction) — `genere_le` approxime `cree_le`
        # à quelques millisecondes, sans conséquence sur un horodatage
        # d'affichage.
        version = _prochaine_version(type_pv, session, evaluation)
        metadonnees = {
            "numero": numero,
            "version": version,
            "genere_le": timezone.now(),
            "genere_par": agissant,
        }
        pdf = _rendre_pdf(type_pv, session, evaluation, apercu, metadonnees)
        proces_verbal = ProcesVerbal(
            type=type_pv,
            session=session,
            evaluation=evaluation,
            numero=numero,
            version=version,
            fichier_pdf=pdf,
        )
        valider_instance(proces_verbal)
        _enregistrer(agissant, proces_verbal, type_pv, session, evaluation)
        return proces_verbal

    @staticmethod
    def lister(agissant, session):
        verifier_habilitation(agissant, PERMISSION_LECTURE)
        return (
            ProcesVerbal.objects.filter(session=session)
            .select_related("evaluation__element_referentiel__matiere")
            .order_by("type", "evaluation_id", "-version")
        )

    @staticmethod
    def evaluations_disponibles(agissant, session):
        """Pour le choix du type « une évaluation » à l'écran — le
        périmètre de la session, même résolution que le calcul lui-même
        (`evaluations_de_la_session`)."""
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        return evaluations_de_la_session(session)

    @staticmethod
    def obtenir(pk):
        try:
            return ProcesVerbal.objects.select_related(
                "session", "evaluation__element_referentiel__matiere"
            ).get(pk=pk)
        except ProcesVerbal.DoesNotExist as erreur:
            raise ErreurIntrouvable(f"Procès-verbal introuvable (identifiant {pk}).") from erreur

    @staticmethod
    def telecharger(agissant, proces_verbal) -> bytes:
        """V2 : rend le fichier ENREGISTRÉ, jamais un recalcul."""
        verifier_habilitation(agissant, PERMISSION_LECTURE)
        _journaliser_telechargement(agissant, proces_verbal)
        return bytes(proces_verbal.fichier_pdf)
