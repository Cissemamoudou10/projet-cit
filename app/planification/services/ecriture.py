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
from django.utils import timezone

from administration.habilitations import verifier_habilitation
from administration.models import TypeAction
from administration.services.journal import DonneesEntreeJournal, ServiceJournal
from noyau.exceptions import ErreurValidation
from noyau.services.base import ServiceBase
from planification.models import LigneProgramme, Seance
from planification.services.circuit import (
    DECLENCHEUR_CONTROLE,
    DECLENCHEUR_GENERATION,
    DECLENCHEUR_SEANCE,
    ServiceCircuitProgramme,
)
from planification.services.contraintes import ServiceContraintes

OBJET_TYPE = "seance"
PERMISSION_LECTURE = "noyau.programme_lecture"
PERMISSION_ECRITURE = "noyau.programme_ecriture"
PERMISSION_EVALUATIONS_ECRITURE = "noyau.evaluations_ecriture"


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


def _creer_une_seance(agissant, programme, candidates, verrouillee=False):
    premiere = candidates[0]
    seance = Seance(
        programme=programme,
        element_referentiel=premiere.element_referentiel,
        instructeur=premiere.instructeur,
        lieu=premiere.lieu,
        debut=premiere.debut,
        fin=premiere.fin,
        verrouillee=verrouillee,
    )
    ServiceBase.creer(seance, agissant)
    for candidate in candidates:
        ligne = LigneProgramme(seance=seance, brigade=candidate.brigade)
        ServiceBase.creer(ligne, agissant)
    return seance


def _verifier_et_creer(programme, candidates, agissant, verrouillee=False):
    """La garde d'état (V3) précède le contrôle des contraintes, sous le même
    verrou : une reprise implicite (T6) est annulée avec le reste si la
    séance est refusée."""
    declencheur = DECLENCHEUR_CONTROLE if verrouillee else DECLENCHEUR_SEANCE
    with transaction.atomic():
        verrouille = ServiceCircuitProgramme.garde_modification(
            programme, agissant, declencheur=declencheur
        )
        contexte = ServiceContraintes.contexte(verrouille)
        _lever_si_refuse(ServiceContraintes.verifier_lot(candidates, contexte))
        seance = _creer_une_seance(agissant, verrouille, candidates, verrouillee)
        _journaliser(agissant, seance)
    return seance


def _horodater(instance, agissant, maintenant):
    """`bulk_create` n'appelle jamais `save()` : ni `auto_now_add`/`auto_now`
    (`ModeleHorodate`) ni `cree_par`/`modifie_par` (`ServiceBase.creer`) ne
    sont posés automatiquement — vérifié réellement, `_prepare_for_bulk_
    create` laisse ces quatre champs à `None`. Posés ici, une fois, la même
    valeur de `maintenant` pour tout le lot (P-38, revue du Prompt 32)."""
    instance.cree_le = maintenant
    instance.modifie_le = maintenant
    instance.cree_par = agissant
    instance.modifie_par = agissant
    return instance


def _construire_seances(programme, groupes_de_candidates, agissant, maintenant):
    return [
        _horodater(
            Seance(
                programme=programme,
                element_referentiel=groupe[0].element_referentiel,
                instructeur=groupe[0].instructeur,
                lieu=groupe[0].lieu,
                debut=groupe[0].debut,
                fin=groupe[0].fin,
            ),
            agissant,
            maintenant,
        )
        for groupe in groupes_de_candidates
    ]


def _construire_lignes(seances, groupes_de_candidates, agissant, maintenant):
    return [
        _horodater(LigneProgramme(seance=seance, brigade=candidate.brigade), agissant, maintenant)
        for seance, groupe in zip(seances, groupes_de_candidates, strict=True)
        for candidate in groupe
    ]


class ServiceEcritureSeance:
    DOMAINE = "programme"
    PERMISSION_LECTURE = PERMISSION_LECTURE
    PERMISSION_ECRITURE = PERMISSION_ECRITURE
    PERMISSION_EVALUATIONS_ECRITURE = PERMISSION_EVALUATIONS_ECRITURE

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
        return _verifier_et_creer(programme, candidates, agissant)

    @staticmethod
    def inserer_seance_de_controle(agissant, programme, candidates):
        """A3/D-177, Prompt 35 : second point d'entrée de la porte unique,
        réservé à `evaluations` (US-EVAL-01) — un utilisateur de la cellule
        examens n'a jamais `noyau.programme_ecriture` (`creer_seance` lui
        est fermé, D-174), seulement `noyau.evaluations_ecriture`, vérifiée
        ici. Toujours verrouillée D'OFFICE : aucun paramètre ne permet de
        l'écrire non verrouillée, un contrôle ne se déverrouille pas par
        inadvertance. Mêmes contrôles, même transaction, même journalisation
        que `creer_seance` — voir `_verifier_et_creer`, aucune logique
        d'écriture dupliquée.

        Test d'architecture associé (F3, Prompt 35) : cette méthode n'est
        appelée que depuis `app/evaluations/` —
        `tests/architecture/test_couches.py::
        test_inserer_seance_de_controle_n_est_appelee_que_depuis_evaluations`.
        """
        verifier_habilitation(agissant, PERMISSION_EVALUATIONS_ECRITURE)
        return _verifier_et_creer(programme, candidates, agissant, verrouillee=True)

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

        Écrit par LOT (`bulk_create`, deux requêtes au total) plutôt qu'une
        boucle de `ServiceBase.creer` — P-38 (revue du Prompt 32) : la boucle
        coûtait 6 requêtes par séance, indépendamment du nombre de cases
        évaluées mais PAS du nombre de séances écrites, ce que I3
        (US-PLAN-03) exigeait borné. `bulk_create` sur PostgreSQL renvoie les
        objets avec leur `pk` posé (clause `RETURNING`), nécessaire pour lier
        les lignes de programme à leur séance.
        """
        if not groupes_de_candidates:
            return []
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        candidates_a_plat = [candidate for groupe in groupes_de_candidates for candidate in groupe]
        with transaction.atomic():
            verrouille = ServiceCircuitProgramme.garde_modification(
                programme, agissant, declencheur=DECLENCHEUR_GENERATION
            )
            contexte = ServiceContraintes.contexte(verrouille)
            _lever_si_refuse(ServiceContraintes.verifier_lot(candidates_a_plat, contexte))
            maintenant = timezone.now()
            seances = Seance.objects.bulk_create(
                _construire_seances(verrouille, groupes_de_candidates, agissant, maintenant)
            )
            LigneProgramme.objects.bulk_create(
                _construire_lignes(seances, groupes_de_candidates, agissant, maintenant)
            )
            return seances
