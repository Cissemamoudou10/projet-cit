"""`ServiceCircuitProgramme` — machine à états du programme hebdomadaire
(US-VAL-03, ETA-01, RG-41 à RG-47).

Seul module qui affecte `ProgrammeHebdomadaire.etat` (V1, test H1). Les cases
admises vivent dans UNE table, `TRANSITIONS` (V2) : chaque méthode la consulte,
aucune ne recode sa propre condition d'état. La table est la traduction de
`docs/conception/ETA-01_table_transitions.md` § 4.1 ; le test de concordance
vérifie qu'elle ne diverge pas du document.

Chaque transition verrouille le programme (`select_for_update`) puis relit son
état dans sa propre transaction (V4) : un état lu avant le verrou serait périmé
dès qu'une autre transaction l'a changé entre-temps.

La garde de modification (V3) ne vérifie PAS l'habilitation : chaque porte
d'écriture la vérifie déjà pour son propre domaine. La cellule examens insère
un contrôle avec `evaluations_ecriture` seulement (D-174) ; sa demande passe
pourtant par la même garde.
"""

from dataclasses import dataclass

from django.db import transaction
from django.utils import timezone

from administration.habilitations import verifier_habilitation
from administration.models import TypeAction
from administration.services.journal import DonneesEntreeJournal, ServiceJournal
from noyau.services.base import ServiceBase
from planification.exceptions import TransitionProgrammeRefusee
from planification.models import EtatProgramme, ProgrammeHebdomadaire, Seance

PERMISSION_PLANIFICATION = "noyau.programme_ecriture"
PERMISSION_PEDAGOGIQUE = "noyau.programme_validation_ecriture"
OBJET_TYPE = "programme"

SOUMETTRE = "soumettre"
RETIRER_SOUMISSION = "retirer_soumission"
VALIDER = "valider"
REJETER = "rejeter"
REPRENDRE = "reprendre"
SIGNER = "signer"
AFFICHER = "afficher"
ANNULER_VALIDATION = "annuler_validation"
PORTER_AVENANT = "porter_avenant"
ECRIRE_SEANCE = "ecrire_seance"
GENERER = "generer"

DECLENCHEUR_SEANCE = "saisie d'une séance"
DECLENCHEUR_GENERATION = "génération"
DECLENCHEUR_CONTROLE = "insertion d'un contrôle"
DECLENCHEUR_DUPLICATION = "duplication"

PERMISSION_PAR_EVENEMENT = {
    SOUMETTRE: PERMISSION_PLANIFICATION,
    RETIRER_SOUMISSION: PERMISSION_PLANIFICATION,
    VALIDER: PERMISSION_PEDAGOGIQUE,
    REJETER: PERMISSION_PEDAGOGIQUE,
    REPRENDRE: PERMISSION_PLANIFICATION,
    SIGNER: PERMISSION_PLANIFICATION,
    AFFICHER: PERMISSION_PLANIFICATION,
    ANNULER_VALIDATION: PERMISSION_PLANIFICATION,
    PORTER_AVENANT: PERMISSION_PLANIFICATION,
    ECRIRE_SEANCE: PERMISSION_PLANIFICATION,
    GENERER: PERMISSION_PLANIFICATION,
}

LIBELLES_EVENEMENTS = {
    SOUMETTRE: "La soumission",
    RETIRER_SOUMISSION: "Le retrait de la soumission",
    VALIDER: "La validation",
    REJETER: "Le rejet",
    REPRENDRE: "La reprise en correction",
    SIGNER: "La signature",
    AFFICHER: "L'affichage",
    ANNULER_VALIDATION: "L'annulation de la validation",
    PORTER_AVENANT: "Un avenant",
    ECRIRE_SEANCE: "La modification d'une séance",
    GENERER: "La génération",
}


@dataclass(frozen=True)
class Transition:
    """Une case admise de ETA-01 § 4.1. `numero` : T2 à T10 ; « T6 » pour une
    écriture précédée de la reprise implicite ; vide pour une écriture qui ne
    change pas d'état. `nature` : nature de journal de la transition, `None`
    pour une écriture (journalisée par sa porte ou par la génération).
    """

    numero: str
    arrivee: str
    nature: TypeAction | None = None


_BROUILLON = EtatProgramme.BROUILLON
_SOUMIS = EtatProgramme.SOUMIS
_VALIDE = EtatProgramme.VALIDE
_REJETE = EtatProgramme.REJETE
_AFFICHE = EtatProgramme.AFFICHE
_JOURNAL_TRANSITION = TypeAction.TRANSITION_PROGRAMME

# Une seule source des cases admises : toute case absente est refusée.
TRANSITIONS = {
    (SOUMETTRE, _BROUILLON): Transition("T2", _SOUMIS, _JOURNAL_TRANSITION),
    (RETIRER_SOUMISSION, _SOUMIS): Transition("T3", _BROUILLON, _JOURNAL_TRANSITION),
    (VALIDER, _SOUMIS): Transition("T4", _VALIDE, TypeAction.VALIDATION_PROGRAMME),
    (REJETER, _SOUMIS): Transition("T5", _REJETE, TypeAction.REJET_PROGRAMME),
    (REPRENDRE, _REJETE): Transition("T6", _BROUILLON, _JOURNAL_TRANSITION),
    (SIGNER, _VALIDE): Transition("T7", _VALIDE, _JOURNAL_TRANSITION),
    (AFFICHER, _VALIDE): Transition("T8", _AFFICHE, _JOURNAL_TRANSITION),
    (ANNULER_VALIDATION, _VALIDE): Transition("T9", _BROUILLON, _JOURNAL_TRANSITION),
    (PORTER_AVENANT, _AFFICHE): Transition("T10", _AFFICHE, _JOURNAL_TRANSITION),
    (ECRIRE_SEANCE, _BROUILLON): Transition("", _BROUILLON),
    (ECRIRE_SEANCE, _REJETE): Transition("T6", _BROUILLON),
    (GENERER, _BROUILLON): Transition("", _BROUILLON),
    (GENERER, _REJETE): Transition("T6", _BROUILLON),
}

MESSAGE_SANS_SEANCE = "Le programme n'a aucune séance : générez-le avant de le soumettre (A9)."
MESSAGE_MOTIF_REJET = "Le rejet exige un motif (RG-45) : indiquez ce qui doit être corrigé."
MESSAGE_SIGNATAIRE = "La signature exige le nom du signataire (RG-47)."
MESSAGE_SIGNATURE_SANS_DATE = "La signature exige une date (RG-47)."
MESSAGE_SIGNATURE_FUTURE = "La date de signature ne peut pas être postérieure à aujourd'hui."
MESSAGE_SIGNATURE_AVANT_VALIDATION = "La date de signature ne peut pas précéder la validation (A5)."
MESSAGE_AFFICHAGE_NON_SIGNE = (
    "L'affichage exige un programme signé : enregistrez la signature (T7) avant "
    "d'afficher (RG-46)."
)
MESSAGE_ANNULATION = "L'annulation de la validation exige une confirmation et un motif (T9)."

MARCHES_PAR_EVENEMENT = {
    SIGNER: "La signature suit la validation (T4) : le programme doit être validé.",
    AFFICHER: "L'affichage suit la signature : le programme doit être validé et signé (T7).",
    ANNULER_VALIDATION: (
        "Seul un programme validé s'annule (T9) ; un programme affiché se modifie par avenant (T10)."
    ),
    PORTER_AVENANT: "Seul un programme affiché reçoit un avenant (T10).",
    REPRENDRE: "Seul un programme rejeté se reprend en correction (T6).",
}
MARCHES_ECRITURE = {
    _SOUMIS: "Retirez la soumission (T3) avant de modifier les séances.",
    _VALIDE: "Annulez la validation (T9) : jamais d'annulation implicite.",
    _AFFICHE: "Portez un avenant (T10) depuis la modification de la séance.",
}
MARCHES_PAR_ETAT = {
    (SOUMETTRE, _SOUMIS): "Il est déjà soumis : retirez la soumission (T3) pour le corriger.",
    (SOUMETTRE, _REJETE): "Reprenez-le en correction (T6) avant de le soumettre.",
    (SOUMETTRE, _VALIDE): "Annulez d'abord la validation (T9).",
    (SOUMETTRE, _AFFICHE): "Un programme affiché ne se soumet plus : il se modifie par avenant.",
    (RETIRER_SOUMISSION, _VALIDE): "Annulez la validation (T9) : seule la soumission se retire.",
    (VALIDER, _BROUILLON): "Il doit d'abord être soumis (T2).",
    (REJETER, _VALIDE): "VALIDÉ → REJETÉ n'existe pas : annulez la validation (T9).",
    **{
        (evenement, etat): marche
        for evenement in (ECRIRE_SEANCE, GENERER)
        for etat, marche in MARCHES_ECRITURE.items()
    },
}


def motif_refus_action(evenement, etat):
    """Message de refus d'une action sur un programme dans cet état, ou
    `None` si l'action est admise. Pur (sans base) : l'écran de lancement
    s'en sert pour dire pourquoi le bouton est indisponible (V8)."""
    if (evenement, etat) in TRANSITIONS:
        return None
    libelle_etat = EtatProgramme(etat).label.lower()
    message = (
        f"{LIBELLES_EVENEMENTS[evenement]} n'est pas possible sur un programme {libelle_etat}."
    )
    marche = MARCHES_PAR_ETAT.get((evenement, etat)) or MARCHES_PAR_EVENEMENT.get(evenement)
    return f"{message} {marche}" if marche else message


def _transition_admise(programme, evenement):
    transition = TRANSITIONS.get((evenement, programme.etat))
    if transition is None:
        raise TransitionProgrammeRefusee(motif_refus_action(evenement, programme.etat))
    return transition


def _transition(agissant, programme, evenement):
    verifier_habilitation(agissant, PERMISSION_PAR_EVENEMENT[evenement])
    return _transition_admise(programme, evenement)


def _verrouiller(programme):
    """Relit le programme sous verrou : à appeler dans une transaction."""
    return ProgrammeHebdomadaire.objects.select_for_update().get(pk=programme.pk)


def _vider_circuit(programme):
    """Un retour à BROUILLON efface les faits du circuit précédent : la
    journalisation garde la trace, le programme repart propre."""
    programme.date_soumission = None
    programme.date_validation = None
    programme.valide_par = None
    programme.motif_rejet = None
    programme.date_signature = None
    programme.signataire = None


def _libelle_detail(transition, detail):
    return f"{transition.numero} — {detail}" if detail else transition.numero


def _journaliser(agissant, programme, transition, ancien, detail):
    ServiceJournal.enregistrer_detaillee(
        DonneesEntreeJournal(
            type_action=transition.nature,
            identifiant_saisi=str(programme),
            detail=_libelle_detail(transition, detail),
            auteur=agissant,
            objet_type=OBJET_TYPE,
            objet_identifiant=str(programme.pk),
            objet_cle=str(programme.pk),
            valeur_avant={"etat": ancien},
            valeur_apres={"etat": programme.etat},
        )
    )


def _appliquer(programme, transition, agissant, champs=None, detail=""):
    """Applique une transition admise : champs, nouvel état, journal. Appelée
    uniquement sous verrou et après contrôle de la table."""
    ancien = programme.etat
    for nom, valeur in (champs or {}).items():
        setattr(programme, nom, valeur)
    programme.etat = transition.arrivee
    if transition.arrivee == _BROUILLON and ancien != _BROUILLON:
        _vider_circuit(programme)
    ServiceBase.modifier(programme, agissant)
    if transition.nature is not None:
        _journaliser(agissant, programme, transition, ancien, detail)
    return programme


def _motif_obligatoire(motif, message):
    texte = (motif or "").strip()
    if not texte:
        raise TransitionProgrammeRefusee(message)
    return texte


def _verifier_signature(programme, date_signature, signataire):
    if date_signature is None:
        raise TransitionProgrammeRefusee(MESSAGE_SIGNATURE_SANS_DATE)
    if not signataire:
        raise TransitionProgrammeRefusee(MESSAGE_SIGNATAIRE)
    aujourd_hui = timezone.localdate()
    if date_signature > aujourd_hui:
        raise TransitionProgrammeRefusee(MESSAGE_SIGNATURE_FUTURE)
    if date_signature < timezone.localdate(programme.date_validation):
        raise TransitionProgrammeRefusee(MESSAGE_SIGNATURE_AVANT_VALIDATION)


def _verifier_affichable(programme):
    if programme.date_signature is None or not programme.signataire:
        raise TransitionProgrammeRefusee(MESSAGE_AFFICHAGE_NON_SIGNE)


class ServiceCircuitProgramme:
    DOMAINE = "programme"

    @staticmethod
    def soumettre(agissant, programme):
        """T2 — refusée sans séance (A9) : un programme vide ne se soumet pas."""
        with transaction.atomic():
            verrouille = _verrouiller(programme)
            transition = _transition(agissant, verrouille, SOUMETTRE)
            if not Seance.objects.filter(programme=verrouille).exists():
                raise TransitionProgrammeRefusee(MESSAGE_SANS_SEANCE)
            return _appliquer(
                verrouille, transition, agissant, champs={"date_soumission": timezone.now()}
            )

    @staticmethod
    def retirer_soumission(agissant, programme):
        """T3."""
        with transaction.atomic():
            verrouille = _verrouiller(programme)
            transition = _transition(agissant, verrouille, RETIRER_SOUMISSION)
            return _appliquer(verrouille, transition, agissant)

    @staticmethod
    def valider(agissant, programme):
        """T4 — cellule pédagogique, sur un programme soumis."""
        with transaction.atomic():
            verrouille = _verrouiller(programme)
            transition = _transition(agissant, verrouille, VALIDER)
            champs = {"date_validation": timezone.now(), "valide_par": agissant}
            return _appliquer(verrouille, transition, agissant, champs=champs)

    @staticmethod
    def rejeter(agissant, programme, motif):
        """T5 — cellule pédagogique ; le motif est obligatoire (RG-45)."""
        with transaction.atomic():
            verrouille = _verrouiller(programme)
            transition = _transition(agissant, verrouille, REJETER)
            motif_propre = _motif_obligatoire(motif, MESSAGE_MOTIF_REJET)
            return _appliquer(
                verrouille,
                transition,
                agissant,
                champs={"motif_rejet": motif_propre},
                detail=motif_propre,
            )

    @staticmethod
    def reprendre(agissant, programme):
        """T6 explicite. La reprise implicite (écriture sur un programme rejeté)
        passe par `garde_modification` et laisse la même entrée de journal."""
        with transaction.atomic():
            verrouille = _verrouiller(programme)
            transition = _transition(agissant, verrouille, REPRENDRE)
            return _appliquer(verrouille, transition, agissant, detail="reprise explicite")

    @staticmethod
    def enregistrer_signature(agissant, programme, date_signature, signataire):
        """T7 — le programme reste VALIDÉ. Date comprise entre la validation et
        aujourd'hui (A5), signataire obligatoire (RG-47)."""
        with transaction.atomic():
            verrouille = _verrouiller(programme)
            transition = _transition(agissant, verrouille, SIGNER)
            nom = (signataire or "").strip()
            _verifier_signature(verrouille, date_signature, nom)
            champs = {"date_signature": date_signature, "signataire": nom}
            detail = f"date de signature : {date_signature:%d/%m/%Y}"
            return _appliquer(verrouille, transition, agissant, champs=champs, detail=detail)

    @staticmethod
    def afficher(agissant, programme):
        """T8 — refusée sans signature (RG-46)."""
        with transaction.atomic():
            verrouille = _verrouiller(programme)
            transition = _transition(agissant, verrouille, AFFICHER)
            _verifier_affichable(verrouille)
            return _appliquer(
                verrouille, transition, agissant, champs={"date_affichage": timezone.now()}
            )

    @staticmethod
    def annuler_validation(agissant, programme, motif, confirmee):
        """T9 — jamais implicite : une confirmation et un motif sont exigés."""
        with transaction.atomic():
            verrouille = _verrouiller(programme)
            transition = _transition(agissant, verrouille, ANNULER_VALIDATION)
            if not confirmee or not (motif or "").strip():
                raise TransitionProgrammeRefusee(MESSAGE_ANNULATION)
            return _appliquer(verrouille, transition, agissant, detail=motif.strip())

    @staticmethod
    def garde_modification(
        programme, agissant, evenement=ECRIRE_SEANCE, declencheur=DECLENCHEUR_SEANCE, avenant=False
    ):
        """V3 — appelée par chaque porte d'écriture et par la suppression de la
        régénération, AVANT toute écriture. Sous verrou : BROUILLON passe ;
        REJETÉ déclenche la reprise implicite (T6), journalisée, puis passe ;
        les autres états refusent, avec la marche à suivre. Doit être appelée
        dans la transaction de l'appelant (le verrou l'exige), qui annule tout
        si la suite échoue. Retourne le programme relu.

        M2 (prompt 41) : `avenant=True` admet l'écriture sur un programme affiché.
        """
        verrouille = _verrouiller(programme)
        if avenant:
            _transition_admise(verrouille, PORTER_AVENANT)
            return verrouille
        _transition_admise(verrouille, evenement)
        if verrouille.etat == _REJETE:
            reprise = TRANSITIONS[(REPRENDRE, _REJETE)]
            _appliquer(
                verrouille,
                reprise,
                agissant,
                detail=f"implicite, déclenchée par : {declencheur}",
            )
        return verrouille
