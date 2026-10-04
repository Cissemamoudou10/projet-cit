"""Modification manuelle d'une séance, suppression, déverrouillage et avenant —
US-PLAN-05 (prompt 41, M1 à M9).

Appelé par la porte unique (`ServiceEcritureSeance`), jamais directement par
une vue. Chaque opération suit le même ordre : habilitation, lecture du
programme sous verrou, garde de modification (avec l'avenant si l'appel en
porte un), contrôle des six contraintes sur la séance résultante, écriture,
journal. Une séance modifiée à la main est verrouillée (M7).
"""

import dataclasses
import datetime

from django.db import transaction
from django.db.models import ProtectedError
from django.utils import timezone

from administration.habilitations import verifier_habilitation
from administration.models import TypeAction
from administration.services.journal import DonneesEntreeJournal, ServiceJournal
from noyau.exceptions import ErreurValidation
from noyau.services.base import ServiceBase
from planification.models import (
    Avenant,
    EtatProgramme,
    NatureAvenant,
    ProgrammeHebdomadaire,
    Seance,
)
from planification.services.circuit import DECLENCHEUR_SEANCE, ServiceCircuitProgramme
from planification.services.contraintes import Candidate, ServiceContraintes
from planification.services.temps import duree_heures
from referentiel.models import CategorieLieu

PERMISSION_ECRITURE = "noyau.programme_ecriture"
OBJET_TYPE = "seance"
CHAMPS_MODIFIABLES = ("element_referentiel", "instructeur", "lieu", "debut", "fin")

MESSAGE_COMMENCEE = "Une séance commencée ne se modifie plus : elle a eu lieu ou a commencé (M6)."
MESSAGE_AFFICHEE = (
    "Une séance affichée ne se supprime pas : une séance qui n'aura pas lieu relève de la "
    "non-exécution (sprint 4). Un avenant décrit ce qui a changé (M4)."
)
MESSAGE_CONTROLE = (
    "Une séance de contrôle ne se supprime pas et ne se déverrouille pas : elle peut être "
    "déplacée, la date de l'évaluation suit (M7)."
)
MESSAGE_HORS_SEMAINE = (
    "Déplacement hors de la semaine du programme : supprimez la séance, puis ajoutez-la dans "
    "la semaine cible (M5)."
)
MESSAGE_AVENANT = "Un avenant exige un motif et une nature (M3)."
MESSAGE_LIEU_REQUIS = (
    "Cette matière exige un lieu : une bascule sans lieu n'est possible que pour une matière "
    "sans lieu requis (M9). Choisissez un lieu, ou une matière sans lieu."
)
MESSAGE_REGROUPEMENT = (
    "Séance regroupée : toutes ses brigades sont touchées ({brigades}). Confirmez la modification."
)


@dataclasses.dataclass(frozen=True)
class Avenantage:
    """Motif et nature d'un avenant, portés ensemble par l'appelant."""

    motif: str
    nature: str


def _verrouiller_programme(programme):
    return ProgrammeHebdomadaire.objects.select_for_update().get(pk=programme.pk)


def _refuser_si_commencee(seance):
    if seance.debut <= timezone.now():
        raise ErreurValidation(MESSAGE_COMMENCEE)


def _verifier_semaine(programme, changements):
    if "debut" not in changements:
        return
    jour = timezone.localtime(changements["debut"]).date()
    lundi = programme.lundi_de_semaine
    if not lundi <= jour < lundi + datetime.timedelta(days=7):
        raise ErreurValidation(MESSAGE_HORS_SEMAINE)


def _verifier_avenantage(avenant):
    if avenant is None:
        return
    if not (avenant.motif or "").strip() or avenant.nature not in NatureAvenant.values:
        raise ErreurValidation(MESSAGE_AVENANT)


def _verifier_lieu_requis(seance, changements):
    """A9 (M9) : une matière qui exige un lieu ne perd pas son lieu. Sans ce
    contrôle, un lieu vide serait lu comme « la salle attitrée » et la bascule
    serait admise d'office."""
    element = changements.get("element_referentiel", seance.element_referentiel)
    lieu = changements.get("lieu", seance.lieu)
    if lieu is None and element.categorie_lieu != CategorieLieu.AUCUN_LIEU:
        raise ErreurValidation(MESSAGE_LIEU_REQUIS)


def _verifier_regroupement(seance, confirmee):
    brigades = [ligne.brigade for ligne in seance.lignes.select_related("brigade")]
    if len(brigades) > 1 and not confirmee:
        noms = ", ".join(str(brigade) for brigade in brigades)
        raise ErreurValidation(MESSAGE_REGROUPEMENT.format(brigades=noms))


def _candidates_de(seance, changements):
    valeurs = {
        champ: changements.get(champ, getattr(seance, champ)) for champ in CHAMPS_MODIFIABLES
    }
    return [
        Candidate(
            brigade=ligne.brigade,
            element_referentiel=valeurs["element_referentiel"],
            instructeur=valeurs["instructeur"],
            debut=valeurs["debut"],
            fin=valeurs["fin"],
            lieu=valeurs["lieu"],
            cle_regroupement=seance.pk,
        )
        for ligne in seance.lignes.select_related("brigade")
    ]


def _contexte_sans_la_seance(programme, seance):
    """Le contexte des contraintes, sans la séance elle-même (sinon elle se
    heurterait à sa propre position d'origine). Les AUTRES séances du même
    programme comptent au volume (RG-39 a), `_charger_volumes` ne les prend
    pas, il est fait pour la régénération."""
    contexte = ServiceContraintes.contexte(programme)
    autres = [s for s in contexte.seances_existantes if s.pk != seance.pk]
    par_element = dict(contexte.volume_programme_par_element)
    par_element_brigade = dict(contexte.volume_programme_par_element_brigade)
    for autre in autres:
        heures = duree_heures(autre.debut, autre.fin)
        par_element[autre.element_referentiel_id] = (
            par_element.get(autre.element_referentiel_id, 0) + heures
        )
        for ligne in autre.lignes.all():
            cle = (autre.element_referentiel_id, ligne.brigade_id)
            par_element_brigade[cle] = par_element_brigade.get(cle, 0) + heures
    return dataclasses.replace(
        contexte,
        seances_existantes=autres,
        volume_programme_par_element=par_element,
        volume_programme_par_element_brigade=par_element_brigade,
    )


def _verifier_contraintes(programme, seance, changements):
    contexte = _contexte_sans_la_seance(programme, seance)
    verdicts = ServiceContraintes.verifier_lot(_candidates_de(seance, changements), contexte)
    violations = [v for verdict in verdicts for v in verdict.violations]
    if violations:
        lignes = (f"{v['code']} : {v['message']}" for v in violations)
        raise ErreurValidation("Modification refusée — " + " ".join(lignes))


def _libelle(valeur):
    if valeur is None:
        return "sans lieu"
    if isinstance(valeur, datetime.datetime):
        return timezone.localtime(valeur).strftime("%d/%m/%Y %H:%M")
    return str(valeur)


def _appliquer_changements(seance, changements):
    """Pose les nouvelles valeurs et rend le détail « ancienne → nouvelle »."""
    detail = []
    for champ, nouvelle in changements.items():
        ancienne = getattr(seance, champ)
        if ancienne != nouvelle:
            detail.append(f"{champ} : {_libelle(ancienne)} → {_libelle(nouvelle)}")
        setattr(seance, champ, nouvelle)
    return detail


def _journaliser(agissant, seance, detail):
    ServiceJournal.enregistrer_detaillee(
        DonneesEntreeJournal(
            type_action=TypeAction.MODIFICATION_ELEMENT_GESTION,
            identifiant_saisi=str(seance),
            detail=detail,
            auteur=agissant,
            objet_type=OBJET_TYPE,
            objet_identifiant=str(seance.pk),
        )
    )


def modifier_seance(agissant, seance, changements, avenant=None, confirmee=False):
    """M1, M2, M5, M6, M7, C1 à C3, C6 : modifie une séance, verrouillée ensuite.
    Avec `avenant`, l'écriture est admise sur un programme affiché (M2) et crée
    un avenant daté, motivé, de nature stockée (M3)."""
    verifier_habilitation(agissant, PERMISSION_ECRITURE)
    _verifier_avenantage(avenant)
    with transaction.atomic():
        programme = _verrouiller_programme(seance.programme)
        ServiceCircuitProgramme.garde_modification(
            programme, agissant, declencheur=DECLENCHEUR_SEANCE, avenant=avenant is not None
        )
        seance.refresh_from_db()
        _refuser_si_commencee(seance)
        _verifier_semaine(programme, changements)
        _verifier_regroupement(seance, confirmee)
        _verifier_lieu_requis(seance, changements)
        _verifier_contraintes(programme, seance, changements)
        detail = _appliquer_changements(seance, changements)
        seance.verrouillee = True
        ServiceBase.modifier(seance, agissant)
        if avenant is not None:
            _creer_avenant(agissant, seance, avenant, detail)
        _journaliser(agissant, seance, _libelle_journal(avenant, detail))
    return seance


def _libelle_journal(avenant, detail):
    texte = " ; ".join(detail) or "aucun champ modifié"
    if avenant is None:
        return f"modification : {texte}"
    return f"avenant ({avenant.nature}) : {avenant.motif.strip()} — {texte}"


def _creer_avenant(agissant, seance, avenant, detail):
    return ServiceBase.creer(
        Avenant(
            seance=seance,
            motif=avenant.motif.strip(),
            nature=avenant.nature,
            detail=" ; ".join(detail),
        ),
        agissant,
    )


def supprimer_seances_regenerables(seances):
    """Régénération (D-235) : efface en lot les séances remplacées. Appelée par la
    génération APRÈS la garde de modification, seul autre chemin de suppression."""
    Seance.objects.filter(pk__in=[seance.pk for seance in seances]).delete()


def supprimer_seance(agissant, seance, permission=PERMISSION_ECRITURE):
    """M4, M6, M7 et A4 : supprime une séance non affichée, non commencée et non
    rattachée à un contrôle. Le volume programmé de la matière diminue d'autant.
    `permission` : celle de la porte appelante (planification, ou évaluations pour
    la suppression d'une évaluation, M8)."""
    verifier_habilitation(agissant, permission)
    with transaction.atomic():
        programme = _verrouiller_programme(seance.programme)
        if programme.etat == EtatProgramme.AFFICHE:
            raise ErreurValidation(MESSAGE_AFFICHEE)
        ServiceCircuitProgramme.garde_modification(
            programme, agissant, declencheur=DECLENCHEUR_SEANCE
        )
        seance.refresh_from_db()
        _refuser_si_commencee(seance)
        if seance.est_un_controle:
            raise ErreurValidation(MESSAGE_CONTROLE)
        identifiant = str(seance)
        _supprimer(seance)
        ServiceJournal.enregistrer_detaillee(
            DonneesEntreeJournal(
                type_action=TypeAction.SUPPRESSION_ELEMENT_GESTION,
                identifiant_saisi=identifiant,
                auteur=agissant,
                objet_type=OBJET_TYPE,
                objet_identifiant=str(seance.pk),
            )
        )


def _supprimer(seance):
    try:
        seance.delete()
    except ProtectedError as erreur:
        raise ErreurValidation(MESSAGE_CONTROLE) from erreur


def deverrouiller_seance(agissant, seance):
    """M7 : rend la séance à la régénération. Refusé pour un contrôle."""
    verifier_habilitation(agissant, PERMISSION_ECRITURE)
    with transaction.atomic():
        programme = _verrouiller_programme(seance.programme)
        ServiceCircuitProgramme.garde_modification(
            programme, agissant, declencheur=DECLENCHEUR_SEANCE
        )
        seance.refresh_from_db()
        if seance.est_un_controle:
            raise ErreurValidation(MESSAGE_CONTROLE)
        _refuser_si_commencee(seance)
        seance.verrouillee = False
        ServiceBase.modifier(seance, agissant)
        _journaliser(agissant, seance, "déverrouillage : la régénération pourra la remplacer")
    return seance
