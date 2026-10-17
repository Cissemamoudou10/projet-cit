"""`ServiceNote` — US-EVAL-05, RG-54, RG-55, CU-P6-05, prompt 46.

A5/N5 : visibilité réservée à `evaluations_ecriture`, jamais une permission
de lecture séparée — même patron que `ServiceSujet` (D-206) : les notes sont
une donnée sensible (BNF-02, D-219 cas a), refusées à la Direction de
Formation comme aux autres cellules. Chaque affichage de la grille
journalise une consultation (`CONSULTATION_NOTES`), jamais le récapitulatif
de vérification (N3) : ce dernier ne montre rien d'enregistré, seulement ce
qui est sur le point de l'être.

Double vérification (N3, CU-P6-05 étapes 5-6) : `verifier` ne touche jamais
la base ; `confirmer` revalide intégralement puis écrit en une transaction —
même principe que l'import de stagiaires, jamais réécrit ici (l'état entre
les deux requêtes passe par `noyau.services.etat_transitoire`, câblé dans
`evaluations.views_notes`, pas dans ce service qui ignore HTTP).

Aucune règle métier dans les vues ni les formulaires — voir
.claude/rules/services.md.
"""

import dataclasses
import decimal

from django.db import transaction

from administration.habilitations import verifier_habilitation
from administration.models import TypeAction
from administration.services.journal import DonneesEntreeJournal, ServiceJournal
from evaluations.models import Note
from noyau.exceptions import ErreurValidation
from noyau.services.base import ServiceBase
from noyau.services.gestion import valider_instance
from organisation.selectors import stagiaires_actifs_des_brigades

PERMISSION_ECRITURE = "noyau.evaluations_ecriture"


@dataclasses.dataclass(frozen=True)
class LigneNote:
    """Une ligne résolue et validée — jamais ce qui a été soumis tel quel."""

    stagiaire: object
    valeur: decimal.Decimal | None = None
    absent: bool = False


@dataclasses.dataclass(frozen=True)
class RapportNotes:
    """N3 : ce que l'étape de vérification montre — notes saisies, absences,
    manquants, valeurs extrêmes, moyenne de l'évaluation. Rien n'y est
    enregistré."""

    saisies: list
    absences: list
    manquants: list
    minimum: decimal.Decimal | None
    maximum: decimal.Decimal | None
    moyenne: decimal.Decimal | None


def _stagiaires_eligibles(evaluation):
    """N2 : résolus à la lecture, jamais stockés — ceux du périmètre de
    l'évaluation (session ou brigade), non radiés. Deux requêtes au plus,
    jamais une par stagiaire."""
    if evaluation.session_id:
        ids_brigades = list(evaluation.session.brigades.values_list("pk", flat=True))
    else:
        ids_brigades = [evaluation.brigade_id]
    return list(stagiaires_actifs_des_brigades(ids_brigades))


def _valeur_decimale(stagiaire, brute):
    try:
        return decimal.Decimal(brute.replace(",", "."))
    except decimal.InvalidOperation as erreur:
        raise ErreurValidation(
            f"{stagiaire} : « {brute} » n'est pas une valeur numérique valide."
        ) from erreur


def _verifier_bornes(stagiaire, valeur, note_maximale):
    if valeur < 0:
        raise ErreurValidation(f"{stagiaire} : une note ne peut pas être négative.")
    if valeur > note_maximale:
        raise ErreurValidation(
            f"{stagiaire} : {valeur} dépasse la note maximale de l'évaluation "
            f"({note_maximale})."
        )


def _resoudre(evaluation, donnees_brutes) -> tuple[list, list, list]:
    """N1/N2/N3 : résout et valide chaque ligne soumise contre le périmètre
    RÉEL de l'évaluation — jamais la confiance dans ce que le client
    prétend. Un stagiaire hors périmètre (forgé, ou radié depuis l'ouverture
    de l'écran) refuse l'ensemble de la soumission plutôt que de l'ignorer
    silencieusement."""
    eligibles = {str(stagiaire.pk): stagiaire for stagiaire in _stagiaires_eligibles(evaluation)}
    inconnus = set(donnees_brutes) - set(eligibles)
    if inconnus:
        raise ErreurValidation(
            "Un ou plusieurs stagiaires soumis ne font pas partie du périmètre de cette "
            "évaluation, ou ont été radiés depuis l'ouverture de l'écran : reprenez la "
            "saisie depuis le début."
        )
    saisies, absences, manquants = [], [], []
    for cle, stagiaire in eligibles.items():
        brute = donnees_brutes.get(cle) or {}
        if brute.get("absent"):
            absences.append(LigneNote(stagiaire=stagiaire, absent=True))
            continue
        valeur_brute = (brute.get("valeur") or "").strip()
        if not valeur_brute:
            manquants.append(stagiaire)
            continue
        valeur = _valeur_decimale(stagiaire, valeur_brute)
        _verifier_bornes(stagiaire, valeur, evaluation.note_maximale)
        saisies.append(LigneNote(stagiaire=stagiaire, valeur=valeur))
    return saisies, absences, manquants


def _rapport(saisies, absences, manquants) -> RapportNotes:
    valeurs = [ligne.valeur for ligne in saisies]
    return RapportNotes(
        saisies=saisies,
        absences=absences,
        manquants=manquants,
        minimum=min(valeurs) if valeurs else None,
        maximum=max(valeurs) if valeurs else None,
        moyenne=(sum(valeurs) / len(valeurs)) if valeurs else None,
    )


def _verifier_non_verrouillee(evaluation):
    """N7, RG-55 : refuse toute écriture sur une note d'une évaluation déjà
    couverte par un procès-verbal — prédicat CALCULÉ (CLS-05 porte un
    booléen `notesVerrouillees` stocké, écart D-270/D-273), jamais stocké :
    l'existence d'une ligne dans `evaluations_couvertes` suffit, câblé
    réellement depuis US-EVAL-07 (D-270)."""
    if evaluation.proces_verbaux_verrouillants.exists():
        raise ErreurValidation(
            f"{evaluation} : les notes sont verrouillées par un procès-verbal déjà généré — "
            "une correction relève de la réglementation (CU-P6-05 A4), pas de la ressaisie."
        )


def _valeur_affichee(note):
    """Formatage fixe à deux décimales (`DecimalField`) : la valeur « avant »
    vient d'une relecture en base, déjà quantifiée ; la valeur « après »
    vient directement de la saisie, pas encore round-trippée — sans ce
    format explicite, le journal afficherait « 10.00 » puis « 14 » pour la
    même grandeur."""
    return "absent" if note.absent else f"{note.valeur:.2f}"


def _journaliser(agissant, type_action, note, ancienne=None, nouvelle=None):
    ServiceJournal.enregistrer_detaillee(
        DonneesEntreeJournal(
            type_action=type_action,
            identifiant_saisi=str(note),
            auteur=agissant,
            objet_type="note",
            objet_identifiant=str(note.pk),
            valeur_avant={"valeur": ancienne} if ancienne is not None else None,
            valeur_apres={"valeur": nouvelle} if nouvelle is not None else None,
        )
    )


def _journaliser_consultation(agissant, evaluation):
    ServiceJournal.enregistrer_detaillee(
        DonneesEntreeJournal(
            type_action=TypeAction.CONSULTATION_NOTES,
            identifiant_saisi=getattr(agissant, "username", ""),
            auteur=agissant,
            objet_type="evaluation",
            objet_identifiant=str(evaluation.pk),
        )
    )


def _enregistrer_une_note(agissant, evaluation, ligne):
    note = Note.objects.filter(evaluation=evaluation, stagiaire=ligne.stagiaire).first()
    if note is None:
        note = Note(
            evaluation=evaluation,
            stagiaire=ligne.stagiaire,
            valeur=ligne.valeur,
            absent=ligne.absent,
        )
        valider_instance(note)
        ServiceBase.creer(note, agissant)
        _journaliser(agissant, TypeAction.SAISIE_NOTE, note)
        return note
    if note.valeur == ligne.valeur and note.absent == ligne.absent:
        return note
    ancienne = _valeur_affichee(note)
    note.valeur, note.absent = ligne.valeur, ligne.absent
    valider_instance(note)
    ServiceBase.modifier(note, agissant)
    _journaliser(agissant, TypeAction.MODIFICATION_NOTE, note, ancienne, _valeur_affichee(note))
    return note


class ServiceNote:
    DOMAINE = "evaluations"
    PERMISSION_ECRITURE = PERMISSION_ECRITURE

    @staticmethod
    def consulter(agissant, evaluation):
        """N5 : chaque appel qui passe le contrôle journalise une
        consultation, qu'il y ait ou non une note à afficher. Deux requêtes,
        jamais une par stagiaire."""
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        stagiaires = _stagiaires_eligibles(evaluation)
        notes = {
            note.stagiaire_id: note
            for note in Note.objects.filter(evaluation=evaluation, stagiaire__in=stagiaires)
        }
        _journaliser_consultation(agissant, evaluation)
        return stagiaires, notes

    @staticmethod
    def verifier(agissant, evaluation, donnees_brutes) -> RapportNotes:
        """N3, étape 1 : contrôlée, sans rien écrire."""
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        saisies, absences, manquants = _resoudre(evaluation, donnees_brutes)
        return _rapport(saisies, absences, manquants)

    @staticmethod
    def confirmer(agissant, evaluation, donnees_brutes) -> RapportNotes:
        """N3, étape 2 : revalide intégralement (jamais confiance dans la
        vérification précédente, qui a pu dater) puis écrit en une seule
        transaction (A3 : saisie partielle admise, les manquants restent
        manquants)."""
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        _verifier_non_verrouillee(evaluation)
        saisies, absences, manquants = _resoudre(evaluation, donnees_brutes)
        with transaction.atomic():
            for ligne in saisies + absences:
                _enregistrer_une_note(agissant, evaluation, ligne)
        return _rapport(saisies, absences, manquants)
