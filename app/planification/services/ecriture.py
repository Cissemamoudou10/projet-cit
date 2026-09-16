"""Porte d'écriture UNIQUE des séances et des lignes de programme — § 5,
Prompt 30, garde mécanique. Aucun autre module du projet n'a le droit
d'instancier ni de sauvegarder `Seance`/`LigneProgramme` (hors migrations et
fabriques de test) : `tests/architecture` le vérifie.

Ni génération, ni modification, ni suppression ici (§ 6, Prompt 30) — cette
story ne livre que le POINT DE PASSAGE, la seule méthode qu'elle a besoin
d'exercer pour le prouver est la création. US-PLAN-03 branchera dessus.
"""

from django.db import transaction

from administration.habilitations import verifier_habilitation
from administration.models import TypeAction
from administration.services.journal import DonneesEntreeJournal, ServiceJournal
from noyau.exceptions import ErreurValidation
from noyau.services.base import ServiceBase
from planification.models import LigneProgramme, Seance
from planification.services.contraintes import ServiceContraintes

OBJET_TYPE = "seance"
PERMISSION_LECTURE = "noyau.programme_lecture"
PERMISSION_ECRITURE = "noyau.programme_ecriture"


def _message_violations(violations):
    lignes = (f"{v['code']} : {v['message']}" for v in violations)
    return "Affectation refusée — " + " ".join(lignes)


def _journaliser(agissant, seance):
    ServiceJournal.enregistrer_detaillee(
        DonneesEntreeJournal(
            type_action=TypeAction.CREATION_ELEMENT_GESTION,
            identifiant_saisi=str(seance),
            auteur=agissant,
            objet_type=OBJET_TYPE,
            objet_identifiant=str(seance.pk),
        )
    )


class ServiceEcritureSeance:
    DOMAINE = "programme"
    PERMISSION_LECTURE = PERMISSION_LECTURE
    PERMISSION_ECRITURE = PERMISSION_ECRITURE

    @staticmethod
    def creer_seance(agissant, programme, candidates):
        """`candidates` : une ou plusieurs `planification.services.
        contraintes.Candidate` — plusieurs pour une séance regroupée
        (même `cle_regroupement`, une ligne de programme par candidate).
        Contrôle TOUJOURS via `ServiceContraintes` avant d'écrire quoi que
        ce soit (§ 5) ; lève `ErreurValidation` listant toutes les
        violations si une seule candidate est refusée — tout ou rien, une
        séance regroupée ne s'écrit jamais à moitié.
        """
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        contexte = ServiceContraintes.contexte(programme)
        verdicts = ServiceContraintes.verifier_lot(candidates, contexte)
        violations = [v for verdict in verdicts for v in verdict.violations]
        if violations:
            raise ErreurValidation(_message_violations(violations))
        premiere = candidates[0]
        with transaction.atomic():
            seance = Seance(
                programme=programme,
                element_referentiel=premiere.element_referentiel,
                instructeur=premiere.instructeur,
                lieu=premiere.lieu,
                debut=premiere.debut,
                fin=premiere.fin,
            )
            ServiceBase.creer(seance, agissant)
            for candidate in candidates:
                ligne = LigneProgramme(seance=seance, brigade=candidate.brigade)
                ServiceBase.creer(ligne, agissant)
            _journaliser(agissant, seance)
        return seance
