"""`ServiceEvaluation` — CU-P6-01, US-EVAL-01, Prompt 35. Orchestre la
création d'une évaluation : contrôle du module et du périmètre, insertion
de la séance verrouillée d'un contrôle à venir par la porte unique
(`ServiceEcritureSeance.inserer_seance_de_controle`, D-177/A3), ou
enregistrement direct sans séance (certificative, ou contrôle déclaré après
coup avec motif).

Aucune règle métier dans les vues ni les formulaires — voir
.claude/rules/services.md. Le périmètre (A1) et la date d'un contrôle à
venir (A2) ne sont jamais stockés en double : voir `evaluations.models.
Evaluation`.
"""

import dataclasses
import datetime

from django.db import transaction
from django.utils import timezone

from administration.habilitations import verifier_habilitation
from administration.models import TypeAction
from administration.services.journal import DonneesEntreeJournal, ServiceJournal
from evaluations.models import Evaluation, TypeEvaluation
from evaluations.services.conflits import conflits_de_l_epreuve
from noyau.exceptions import ErreurIntrouvable, ErreurValidation
from noyau.services.base import ServiceBase
from noyau.services.gestion import avertissement, valider_instance
from planification.models import ProgrammeHebdomadaire
from planification.selectors import JOUR_SEMAINE_PAR_ISO, seances_recouvertes
from planification.services.contraintes import Candidate
from planification.services.ecriture import ServiceEcritureSeance

PERMISSION_LECTURE = "noyau.evaluations_lecture"
PERMISSION_ECRITURE = "noyau.evaluations_ecriture"


@dataclasses.dataclass(frozen=True)
class Perimetre:
    """Regroupe le module et le rattachement choisi — `.claude/rules/
    python.md`, § 5 paramètres max : les trois voyagent ensemble dans
    presque toute la création d'une évaluation. Exactement un de `session`/
    `brigade` est renseigné, vérifié par `_verifier_perimetre` avant que
    cet objet n'existe."""

    element: object
    session: object = None
    brigade: object = None

    @property
    def session_visee(self):
        """La session directement rattachée, ou celle de la brigade — jamais
        la brigade elle-même, qui ne porte ni `formation` ni les bornes."""
        return self.session or self.brigade.session

    @property
    def formation(self):
        return self.session_visee.formation

    @property
    def brigades_visees(self):
        return list(self.session.brigades.all()) if self.session else [self.brigade]


def _verifier_perimetre(session, brigade):
    """C3, RG-52 : exactement un des deux — même exigence que la contrainte
    en base (`ck_evaluation_perimetre_exclusif`), vérifiée ici en amont pour
    un message clair plutôt qu'un `IntegrityError`."""
    if bool(session) == bool(brigade):
        raise ErreurValidation(
            "Choisissez exactement un périmètre pour l'évaluation : une session, ou une brigade."
        )


def _verifier_module(perimetre):
    """C2, E1 : le module doit appartenir au référentiel de la formation
    concernée par le périmètre choisi — règle inter-tables, hors de portée
    d'une contrainte en base (§ 3, Prompt 35)."""
    if perimetre.element.formation_id != perimetre.formation.pk:
        raise ErreurValidation(
            f"« {perimetre.element} » n'appartient pas au référentiel de {perimetre.formation} : "
            "choisissez un élément du référentiel de la formation concernée."
        )


def _verifier_bornes(jour, perimetre):
    """C8 : la date tombe dans les bornes de la session visée par le
    périmètre — celle du rattachement direct, ou celle de la session de la
    brigade rattachée."""
    cible = perimetre.session_visee
    if not (cible.date_debut <= jour <= cible.date_fin):
        raise ErreurValidation(
            f"{jour:%d/%m/%Y} est hors des bornes de {cible} "
            f"({cible.date_debut:%d/%m/%Y} — {cible.date_fin:%d/%m/%Y})."
        )


def _verifier_jour(creneau_type, jour):
    if JOUR_SEMAINE_PAR_ISO[creneau_type.jour_semaine] != jour.isoweekday():
        raise ErreurValidation(
            f"Le créneau choisi ({creneau_type.get_jour_semaine_display()}) ne correspond pas "
            f"au jour sélectionné ({jour:%d/%m/%Y})."
        )


def _projeter(creneau_type, jour):
    debut = timezone.make_aware(datetime.datetime.combine(jour, creneau_type.heure_debut))
    fin = timezone.make_aware(datetime.datetime.combine(jour, creneau_type.heure_fin))
    return debut, fin


def _lundi(jour):
    return jour - datetime.timedelta(days=jour.weekday())


def _journaliser(agissant, evaluation):
    ServiceJournal.enregistrer_detaillee(
        DonneesEntreeJournal(
            type_action=TypeAction.CREATION_ELEMENT_GESTION,
            identifiant_saisi=str(evaluation),
            auteur=agissant,
            objet_type="evaluation",
            objet_identifiant=str(evaluation.pk),
        )
    )


def _journaliser_modification_date(agissant, evaluation, ancienne_date, nouvelle_date, motif):
    ServiceJournal.enregistrer_detaillee(
        DonneesEntreeJournal(
            type_action=TypeAction.MODIFICATION_ELEMENT_GESTION,
            identifiant_saisi=str(evaluation),
            auteur=agissant,
            objet_type="evaluation",
            objet_identifiant=str(evaluation.pk),
            valeur_avant={"date": str(ancienne_date)},
            valeur_apres={"date": str(nouvelle_date), "motif": motif},
        )
    )


def _verifier_modifiable(evaluation):
    """A6 : seules les certificatives se modifient ici — la date d'une
    formative avec séance se déplace avec sa séance (US-PLAN-05) ; celle
    d'une formative déclarée après coup est figée."""
    if evaluation.type == TypeEvaluation.CERTIFICATIVE:
        return
    if evaluation.seance_id:
        raise ErreurValidation(
            "La date d'un contrôle avec séance se déplace avec sa séance (US-PLAN-05), pas ici."
        )
    raise ErreurValidation("La date d'un contrôle déclaré après coup est figée.")


def _enregistrer(agissant, evaluation):
    valider_instance(evaluation)
    with transaction.atomic():
        ServiceBase.creer(evaluation, agissant)
        _journaliser(agissant, evaluation)


def _avertissements(session):
    """C9 : forme simplifiée de E2 (A8) — systématique, non bloquant, sur
    tout périmètre session. La mesure précise de l'écart de progression
    reste un report sans story (voir docs/suivi/AVANCEMENT.md)."""
    if session is None:
        return []
    return [
        avertissement(
            "A8",
            "Périmètre session : le sujet sera commun à toutes les brigades, dont les "
            "progressions peuvent être décalées.",
        )
    ]


def _avertissements_seances(perimetre, jour):
    """A7, C1/C5 : signalement, jamais une suppression — la date s'enregistre
    quoi qu'il arrive (C3). `jour` est une date, converti en journée pleine
    pour `seances_recouvertes`."""
    debut_jour = timezone.make_aware(datetime.datetime.combine(jour, datetime.time.min))
    fin_jour = debut_jour + datetime.timedelta(days=1)
    seances = seances_recouvertes(perimetre.brigades_visees, debut_jour, fin_jour)
    if not seances:
        return []
    noms = "; ".join(
        f"{seance.element_referentiel.matiere} {seance.debut:%H:%M}–{seance.fin:%H:%M} "
        f"(programme {seance.programme.get_etat_display()})"
        for seance in seances
    )
    return [
        avertissement("A7", f"Séance(s) déjà programmée(s) ce jour, non supprimée(s) : {noms}.")
    ]


def _candidates_formative(perimetre, instructeur, lieu, debut, fin):
    brigades_visees = perimetre.brigades_visees
    cle = object() if len(brigades_visees) > 1 else None
    return [
        Candidate(
            brigade=cible,
            element_referentiel=perimetre.element,
            instructeur=instructeur,
            debut=debut,
            fin=fin,
            lieu=lieu,
            cle_regroupement=cle,
        )
        for cible in brigades_visees
    ]


def _evaluation_du_perimetre(perimetre, **champs):
    return Evaluation(
        element_referentiel=perimetre.element,
        session=perimetre.session,
        brigade=perimetre.brigade,
        **champs,
    )


def _creer_formative_a_venir(agissant, perimetre, jour, donnees):
    """A3/D-177 : contrôle à date présente ou future — séance verrouillée
    insérée par la porte unique, dans la MÊME transaction que l'évaluation
    (l'échec de l'une annule l'autre)."""
    creneau_type = donnees.get("creneau_type")
    instructeur = donnees.get("instructeur")
    if creneau_type is None:
        raise ErreurValidation(
            "Un créneau de la grille active est obligatoire pour un contrôle à venir."
        )
    if instructeur is None:
        raise ErreurValidation("Un instructeur est obligatoire pour un contrôle à venir.")
    _verifier_jour(creneau_type, jour)
    _verifier_bornes(jour, perimetre)
    debut, fin = _projeter(creneau_type, jour)
    candidates = _candidates_formative(perimetre, instructeur, donnees.get("lieu"), debut, fin)
    with transaction.atomic():
        programme, _ = ProgrammeHebdomadaire.objects.get_or_create(lundi_de_semaine=_lundi(jour))
        seance = ServiceEcritureSeance.inserer_seance_de_controle(agissant, programme, candidates)
        evaluation = _evaluation_du_perimetre(
            perimetre, type=TypeEvaluation.FORMATIVE, seance=seance
        )
        valider_instance(evaluation)
        ServiceBase.creer(evaluation, agissant)
        _journaliser(agissant, evaluation)
    return evaluation


def _creer_certificative(agissant, perimetre, date):
    """C7 : date obligatoire, ni passée (RG-49), jamais de séance."""
    if date is None:
        raise ErreurValidation("La date de l'examen final est obligatoire (RG-49).")
    _verifier_bornes(date, perimetre)
    if date < timezone.localdate():
        raise ErreurValidation(
            f"{date:%d/%m/%Y} est déjà passée : un examen final ne peut être daté dans le "
            "passé (RG-49)."
        )
    evaluation = _evaluation_du_perimetre(perimetre, type=TypeEvaluation.CERTIFICATIVE, date=date)
    _enregistrer(agissant, evaluation)
    return evaluation


def _creer_formative(agissant, perimetre, date, donnees):
    if date is None:
        raise ErreurValidation("La date du contrôle est obligatoire.")
    if date >= timezone.localdate():
        return _creer_formative_a_venir(agissant, perimetre, date, donnees)
    motif = (donnees.get("motif_date_passee") or "").strip()
    if not motif:
        raise ErreurValidation(
            "Un motif est obligatoire pour déclarer un contrôle à une date déjà passée "
            "(CU-P6-01 A2)."
        )
    evaluation = _evaluation_du_perimetre(
        perimetre, type=TypeEvaluation.FORMATIVE, date=date, motif_date_passee=motif
    )
    _enregistrer(agissant, evaluation)
    return evaluation


class ServiceEvaluation:
    DOMAINE = "evaluations"
    PERMISSION_LECTURE = PERMISSION_LECTURE
    PERMISSION_ECRITURE = PERMISSION_ECRITURE

    @staticmethod
    def creer(agissant, donnees):
        """A7 : type et périmètre immuables après création — aucune méthode
        de modification n'existe, une erreur se corrige par suppression et
        recréation (suppression reportée à US-PLAN-05, D-181)."""
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        session = donnees.get("session")
        brigade = donnees.get("brigade")
        _verifier_perimetre(session, brigade)
        perimetre = Perimetre(
            element=donnees["element_referentiel"], session=session, brigade=brigade
        )
        _verifier_module(perimetre)
        type_ = donnees["type"]
        date = donnees.get("date")
        if type_ == TypeEvaluation.CERTIFICATIVE:
            evaluation = _creer_certificative(agissant, perimetre, date)
            evaluation.avertissements = _avertissements(session) + _avertissements_seances(
                perimetre, date
            )
        else:
            evaluation = _creer_formative(agissant, perimetre, date, donnees)
            evaluation.avertissements = _avertissements(session)
        return evaluation

    @staticmethod
    def modifier_date_certificative(agissant, evaluation, nouvelle_date, motif):
        """A6/C2 : bornes, gel de la date déjà passée (actuelle ET nouvelle),
        motif obligatoire, journalisé avec l'ancienne et la nouvelle date
        (patron D-132). Seules les certificatives se modifient ici — A6."""
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        _verifier_modifiable(evaluation)
        motif = (motif or "").strip()
        if not motif:
            raise ErreurValidation(
                "Un motif est obligatoire pour modifier une date imposée par le 3e bureau "
                "(CU-P6-02)."
            )
        if evaluation.date < timezone.localdate():
            raise ErreurValidation(
                f"{evaluation.date:%d/%m/%Y} est déjà passée : cet examen est échu, sa date "
                "ne change plus."
            )
        perimetre = Perimetre(
            element=evaluation.element_referentiel,
            session=evaluation.session,
            brigade=evaluation.brigade,
        )
        _verifier_bornes(nouvelle_date, perimetre)
        if nouvelle_date < timezone.localdate():
            raise ErreurValidation(
                f"{nouvelle_date:%d/%m/%Y} est déjà passée : un examen final ne peut être "
                "daté dans le passé (RG-49)."
            )
        ancienne_date = evaluation.date
        with transaction.atomic():
            evaluation.date = nouvelle_date
            ServiceBase.modifier(evaluation, agissant)
            _journaliser_modification_date(
                agissant, evaluation, ancienne_date, nouvelle_date, motif
            )
        evaluation.avertissements = _avertissements_seances(perimetre, nouvelle_date) + (
            conflits_de_l_epreuve(evaluation)
        )
        return evaluation

    @staticmethod
    def obtenir(pk):
        try:
            return Evaluation.objects.select_related(
                "element_referentiel__formation",
                "element_referentiel__matiere",
                "session",
                "brigade",
                "seance",
            ).get(pk=pk)
        except Evaluation.DoesNotExist as erreur:
            raise ErreurIntrouvable(f"Évaluation introuvable (identifiant {pk}).") from erreur

    @staticmethod
    def lister():
        return Evaluation.objects.select_related(
            "element_referentiel__matiere",
            "element_referentiel__formation",
            "session__formation",
            "brigade__session__formation",
        ).order_by("-cree_le")

    @staticmethod
    def actions_disponibles(evaluation) -> list[str]:
        """C10 : reflète ce qui existe aujourd'hui — les sujets et
        l'organisation d'épreuve arrivent aux stories suivantes (US-EVAL-02
        à 04), pas une anticipation ici."""
        if evaluation.type == TypeEvaluation.FORMATIVE:
            return ["consulter_seance"] if evaluation.seance_id else ["consulter_motif"]
        return ["consulter_date"]
