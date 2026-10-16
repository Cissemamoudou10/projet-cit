"""Suivi : prescrit, programmé, réalisé — US-SUI-05 (prompt 44, Temps 2) et
US-SUI-01 (prompt 44, Temps 3).

La non-exécution n'est pas une écriture de séance (S3) : elle ne passe pas
par `ServiceEcritureSeance` (la porte unique de `Seance`/`LigneProgramme`),
mais par ce service dédié, qui vérifie l'état du programme et ne touche
jamais `Seance` ni `LigneProgramme` — seulement `NonExecution`, rattachée à
la ligne (CLS-05 § 6.7).

Le rapprochement (US-SUI-01) est gardé par `noyau.suivi_lecture` — la
matrice § 11.2 l'accorde à quatre profils (pédagogique, planification,
examens, Direction de formation) ; le critère C5 du backlog v10 n'en citait
que deux, omission corrigée au backlog, pas à la matrice (D-265, qui révise
D-264 — voir `administration/constantes.py::MATRICE`).
"""

from django.db import transaction
from django.utils import timezone

from administration.habilitations import verifier_habilitation
from administration.models import TypeAction, TypeDocument
from administration.services.document import ServiceDocument
from administration.services.journal import DonneesEntreeJournal, ServiceJournal
from noyau.exceptions import ErreurValidation
from noyau.services.base import ServiceBase
from planification.models import EditionProgression, EtatProgramme, NonExecution
from planification.selectors_progression import progression_realisee as _progression_realisee
from planification.selectors_rapprochement import rapprochement as _rapprochement

PERMISSION_ECRITURE = "noyau.programme_ecriture"
PERMISSION_LECTURE = "noyau.suivi_lecture"
OBJET_TYPE = "ligne_programme"
OBJET_TYPE_EDITION = "edition_progression"
GABARIT_PDF_PROGRESSION = "planification/pdf/progression_realisee.html"

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
MESSAGE_PROGRAMME_NON_AFFICHE_PROGRESSION = (
    "La progression réalisée ne s'édite que pour un programme affiché (RG-60) : ce "
    "programme est encore {etat}."
)
MESSAGE_SIGNATURE_INCOMPLETE = "La signature exige une date et un nom de signataire, les deux."
MESSAGE_SIGNATURE_FUTURE = "La date de signature ne peut pas être postérieure à aujourd'hui."


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


def _verifier_programme_affiche_progression(programme):
    if programme.etat != EtatProgramme.AFFICHE:
        raise ErreurValidation(
            MESSAGE_PROGRAMME_NON_AFFICHE_PROGRESSION.format(
                etat=programme.get_etat_display().lower()
            )
        )


def _journaliser_edition(agissant, edition, nature, detail):
    ServiceJournal.enregistrer_detaillee(
        DonneesEntreeJournal(
            type_action=nature,
            identifiant_saisi=str(edition),
            detail=detail,
            auteur=agissant,
            objet_type=OBJET_TYPE_EDITION,
            objet_identifiant=str(edition.pk),
        )
    )


class ServiceSuivi:
    DOMAINE = "suivi"
    PERMISSION_ECRITURE = PERMISSION_ECRITURE
    PERMISSION_LECTURE = PERMISSION_LECTURE

    @staticmethod
    def rapprochement(
        agissant, formation_id=None, session_id=None, brigade_id=None, periode_fin=None
    ):
        """C5 : lecture seule, pédagogique et Direction de formation."""
        verifier_habilitation(agissant, PERMISSION_LECTURE)
        return _rapprochement(
            formation_id=formation_id,
            session_id=session_id,
            brigade_id=brigade_id,
            periode_fin=periode_fin,
        )

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

    @staticmethod
    def editer_progression(agissant, programme):
        """P1, P4 : une édition de plus, jamais une réécriture — plusieurs
        éditions d'une même semaine coexistent, la plus récente fait foi
        (`derniere_edition`). Refusée hors programme affiché (RG-60)."""
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        _verifier_programme_affiche_progression(programme)
        edition = EditionProgression(programme=programme)
        ServiceBase.creer(edition, agissant)
        _journaliser_edition(
            agissant, edition, TypeAction.CREATION_ELEMENT_GESTION, "progression réalisée éditée"
        )
        return edition

    @staticmethod
    def derniere_edition(programme):
        return programme.editions_progression.order_by("-cree_le").first()

    @staticmethod
    def enregistrer_signature_progression(agissant, edition, date_signature, signataire):
        """P1 : les deux ou aucun (garanti en base), jamais future."""
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        nom = (signataire or "").strip()
        if date_signature is None or not nom:
            raise ErreurValidation(MESSAGE_SIGNATURE_INCOMPLETE)
        if date_signature > timezone.localdate():
            raise ErreurValidation(MESSAGE_SIGNATURE_FUTURE)
        edition.date_signature = date_signature
        edition.signataire = nom
        ServiceBase.modifier(edition, agissant)
        _journaliser_edition(
            agissant,
            edition,
            TypeAction.MODIFICATION_ELEMENT_GESTION,
            f"signature enregistrée : {nom}",
        )
        return edition

    @staticmethod
    def produire_pdf_progression(agissant, edition):
        """C4, C6 : rien n'est saisi deux fois — le PDF est recalculé à
        chaque production, à la date de CETTE édition (`cree_le`), jamais
        « maintenant » : deux éditions de la même semaine restent
        distinctes même après coup."""
        verifier_habilitation(agissant, PERMISSION_LECTURE)
        groupes = _progression_realisee(edition.programme, instant_edition=edition.cree_le)
        return ServiceDocument.produire(
            TypeDocument.PROGRESSION_REALISEE,
            GABARIT_PDF_PROGRESSION,
            {"programme": edition.programme, "edition": edition, "groupes": groupes},
        )
