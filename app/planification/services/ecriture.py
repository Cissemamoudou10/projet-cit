"""Porte d'écriture UNIQUE des séances et des lignes de programme — § 5,
Prompt 30, garde mécanique. Aucun autre module du projet n'a le droit
d'instancier ni de sauvegarder `Seance`/`LigneProgramme` (hors migrations et
fabriques de test) : `tests/architecture` le vérifie.

Deux points d'entrée, DEUX régimes de journalisation (§ 0.3/point 4,
Prompt 31 — voir docs/suivi/DECISIONS.md) :

- `creer_seance` (singulier) — saisie manuelle (US-PLAN-05) : un acte, une
  décision individuelle, un journal DÉTAILLÉ par séance créée. Recharge le
  contexte à chaque appel — acceptable, un seul appel par action utilisateur.
- `creer_seances` (pluriel) — génération (US-PLAN-03) : contexte chargé UNE
  FOIS pour tout le lot (I3, borné et indépendant du nombre de cases),
  écriture de plusieurs séances dans UNE transaction, et AUCUN journal par
  séance — une génération sur dix brigades produirait plusieurs centaines
  d'entrées à chaque lancement dans un journal immuable (RG-27), qui
  cesserait d'être consultable. L'appelant (`ServiceGeneration`) journalise
  l'ACTE de génération, pas le détail : c'est à lui de le faire, pas à cette
  porte d'écriture.
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


def _lever_si_refuse(verdicts):
    violations = [v for verdict in verdicts for v in verdict.violations]
    if violations:
        raise ErreurValidation(_message_violations(violations))


def _creer_une_seance(agissant, programme, candidates):
    premiere = candidates[0]
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
    return seance


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
        _lever_si_refuse(verdicts)
        with transaction.atomic():
            seance = _creer_une_seance(agissant, programme, candidates)
            _journaliser(agissant, seance)
        return seance

    @staticmethod
    def creer_seances(agissant, programme, groupes_de_candidates):
        """`groupes_de_candidates` : liste de groupes, chaque groupe une ou
        plusieurs `Candidate` destinées à UNE séance — voir `creer_seance`.
        Revérifie tout le lot À PLAT en une seule passe, dans l'ordre de
        soumission (même sémantique que `verifier_lot`, § 0.4) : c'est une
        seconde vérification, indépendante de celle déjà faite par la
        stratégie de génération — cette porte ne fait jamais confiance à
        l'appelant. Lève `ErreurValidation` si une seule candidate est
        refusée ; sinon écrit TOUTES les séances dans une seule transaction.
        """
        if not groupes_de_candidates:
            return []
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        contexte = ServiceContraintes.contexte(programme)
        candidates_a_plat = [
            candidate for groupe in groupes_de_candidates for candidate in groupe
        ]
        verdicts = ServiceContraintes.verifier_lot(candidates_a_plat, contexte)
        _lever_si_refuse(verdicts)
        with transaction.atomic():
            return [
                _creer_une_seance(agissant, programme, groupe) for groupe in groupes_de_candidates
            ]
