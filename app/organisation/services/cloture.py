"""Clôture d'une session — US-SES-09, prompt 47, Temps 4.

Classe séparée de `ServiceSession` (`session.py`), par taille de fichier
(`.claude/rules/python.md`, 400 lignes / 200 lignes de classe), PAS par
politique d'habilitation distincte : mêmes `PERMISSION_LECTURE`/
`PERMISSION_ECRITURE` que `ServiceSession` (`organisation_lecture`/
`organisation_ecriture`), réimportées telles quelles — à la différence du
motif `ServiceSujet`/`ServiceNote` (D-206), qui sépare pour une
confidentialité réellement différente.
"""

from django.db import transaction
from django.utils import timezone

from administration.habilitations import verifier_habilitation
from administration.models import TypeAction
from administration.services.journal import DonneesEntreeJournal, ServiceJournal
from noyau.exceptions import ErreurValidation
from noyau.services.base import ServiceBase
from noyau.services.parametres import ResolveurEvaluationsNonFinalisees
from organisation.models import EtatSession
from organisation.services.session import PERMISSION_ECRITURE, PERMISSION_LECTURE

OBJET_TYPE = "session"


class ServiceClotureSession:
    DOMAINE = "organisation"
    PERMISSION_LECTURE = PERMISSION_LECTURE
    PERMISSION_ECRITURE = PERMISSION_ECRITURE

    @classmethod
    def evaluations_non_finalisees(cls, agissant, session):
        """C2, aperçu avant clôture : mêmes évaluations que `cloturer`
        refuserait, sans rien écrire — l'écran de confirmation les énumère
        et désactive le bouton si la liste n'est pas vide."""
        verifier_habilitation(agissant, cls.PERMISSION_LECTURE)
        return ResolveurEvaluationsNonFinalisees.resoudre(session)

    @classmethod
    def cloturer(cls, agissant, session):
        """C2 : refuse et énumère les évaluations dont les notes ne sont
        pas verrouillées par un procès-verbal. C3 : aucune suppression,
        seul l'état change — `ServiceSession.disponibles_pour_selection`
        retire aussitôt la session des sélections actives (génération,
        création d'évaluation, affectation des stagiaires) ; brigades,
        programmes et résultats restent consultables ailleurs, inchangés.
        C6 : aucune réouverture — une clôture erronée se corrige hors de
        l'interface (limite assumée, D-281)."""
        verifier_habilitation(agissant, cls.PERMISSION_ECRITURE)
        if session.etat == EtatSession.CLOTUREE:
            raise ErreurValidation(f"« {session} » est déjà clôturée.")
        non_finalisees = ResolveurEvaluationsNonFinalisees.resoudre(session)
        if non_finalisees:
            detail = "; ".join(str(evaluation) for evaluation in non_finalisees)
            raise ErreurValidation(
                f"{len(non_finalisees)} évaluation(s) non finalisée(s) (notes non "
                f"verrouillées par un procès-verbal) : {detail} — générez leur "
                "procès-verbal avant de clôturer la session."
            )
        with transaction.atomic():
            session.etat = EtatSession.CLOTUREE
            session.date_cloture = timezone.localdate()
            ServiceBase.modifier(session, agissant)
            ServiceJournal.enregistrer_detaillee(
                DonneesEntreeJournal(
                    type_action=TypeAction.CLOTURE_SESSION,
                    identifiant_saisi=str(session),
                    auteur=agissant,
                    objet_type=OBJET_TYPE,
                    objet_identifiant=str(session.pk),
                )
            )
        return session
