"""Suivi : prescrit, programmé, réalisé — US-SUI-05 (prompt 44, Temps 2).

La non-exécution n'est pas une écriture de séance (S3) : elle ne passe pas
par `ServiceEcritureSeance` (la porte unique de `Seance`/`LigneProgramme`),
mais par ce service dédié, qui vérifie l'état du programme et ne touche
jamais `Seance` ni `LigneProgramme` — seulement `NonExecution`, rattachée à
la ligne (CLS-05 § 6.7).
"""

from django.db import transaction
from django.utils import timezone

from administration.habilitations import verifier_habilitation
from administration.models import TypeAction
from administration.services.journal import DonneesEntreeJournal, ServiceJournal
from noyau.exceptions import ErreurValidation
from noyau.services.base import ServiceBase
from planification.models import EtatProgramme, NonExecution

PERMISSION_ECRITURE = "noyau.programme_ecriture"
OBJET_TYPE = "ligne_programme"

MESSAGE_MOTIF_OBLIGATOIRE = "Le motif de la non-exécution est obligatoire (RG-60)."
MESSAGE_PROGRAMME_NON_AFFICHE = (
    "La non-exécution ne se déclare que sur un programme affiché (RG-60) : ce "
    "programme est encore {etat}."
)
MESSAGE_SEANCE_FUTURE = (
    "Cette séance n'a pas encore eu lieu : seule une séance passée se déclare " "non exécutée."
)
MESSAGE_DEJA_DECLAREE = (
    "Cette ligne porte déjà une non-exécution : annulez-la avant d'en déclarer une autre."
)
MESSAGE_AUCUNE_DECLARATION = "Cette ligne ne porte aucune non-exécution à annuler."
MESSAGE_SESSION_CLOTUREE = (
    "La session est clôturée : la déclaration de non-exécution n'est plus réversible."
)


def _session_cloturee():
    """S4 : la clôture de session (US-SES-09) n'existe pas encore dans ce
    sprint — garde posée dès maintenant, toujours `False` jusqu'à ce
    qu'US-SES-09 la complète (report ouvert, voir docs/suivi/DECISIONS.md).
    Prendra alors la ligne en paramètre, pour remonter à sa session ;
    aucun paramètre deviné avant d'en avoir besoin."""
    return False


def _verifier_programme_affiche(ligne):
    programme = ligne.seance.programme
    if programme.etat != EtatProgramme.AFFICHE:
        raise ErreurValidation(
            MESSAGE_PROGRAMME_NON_AFFICHE.format(etat=programme.get_etat_display().lower())
        )


def _verifier_seance_passee(ligne, maintenant):
    if ligne.seance.fin > maintenant:
        raise ErreurValidation(MESSAGE_SEANCE_FUTURE)


def _journaliser(agissant, ligne, detail):
    ServiceJournal.enregistrer_detaillee(
        DonneesEntreeJournal(
            type_action=TypeAction.DECLARATION_NON_EXECUTION,
            identifiant_saisi=str(ligne),
            detail=detail,
            auteur=agissant,
            objet_type=OBJET_TYPE,
            objet_identifiant=str(ligne.pk),
        )
    )


class ServiceSuivi:
    DOMAINE = "suivi"
    PERMISSION_ECRITURE = PERMISSION_ECRITURE

    @staticmethod
    def declarer_non_execution(agissant, ligne, motif):
        """C1 à C3, C5 : refuse une séance future (S2) ou un programme pas
        affiché (S2, RG-60), puis retranche le volume de la ligne du
        réalisé — par construction, puisque le calcul du réalisé (US-SUI-01)
        exclut les lignes portant une non-exécution."""
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        motif_propre = (motif or "").strip()
        if not motif_propre:
            raise ErreurValidation(MESSAGE_MOTIF_OBLIGATOIRE)
        if getattr(ligne, "non_execution", None) is not None:
            raise ErreurValidation(MESSAGE_DEJA_DECLAREE)
        maintenant = timezone.now()
        with transaction.atomic():
            _verifier_programme_affiche(ligne)
            _verifier_seance_passee(ligne, maintenant)
            non_execution = NonExecution(ligne=ligne, motif=motif_propre)
            ServiceBase.creer(non_execution, agissant)
            _journaliser(agissant, ligne, f"déclarée — {motif_propre}")
        return non_execution

    @staticmethod
    def annuler_non_execution(agissant, ligne):
        """C4 : réversible sans condition tant qu'US-SES-09 n'existe pas
        (`_session_cloturee`)."""
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        non_execution = getattr(ligne, "non_execution", None)
        if non_execution is None:
            raise ErreurValidation(MESSAGE_AUCUNE_DECLARATION)
        with transaction.atomic():
            if _session_cloturee():
                raise ErreurValidation(MESSAGE_SESSION_CLOTUREE)
            non_execution.delete()
            _journaliser(agissant, ligne, "annulée")
        return ligne
