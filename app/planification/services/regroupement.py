"""Regroupement de plusieurs brigades sur une même séance — US-PLAN-06
(prompt 42, partie 2, R1 à R5).

Appelé par la porte unique (`ServiceEcritureSeance`), jamais directement par
une vue. Réutilise les fonctions privées de `modification.py` (verrou, refus
d'une séance commencée, contexte sans la séance, avenant) : même rôle, même
porte, séparé dans son propre fichier pour rester sous 400 lignes (même
raison que la séparation de `modification.py` depuis `ecriture.py`, D-235).

C2, C3, C4 sont vrais par construction (une `Seance`, N `LigneProgramme`,
D-139) : ce module les prouve par ses tests, il ne les recode pas.
"""

from django.db import transaction

from administration.habilitations import verifier_habilitation
from administration.models import TypeAction
from administration.services.journal import DonneesEntreeJournal, ServiceJournal
from noyau.exceptions import ErreurValidation
from noyau.intervalles import se_recouvrent
from noyau.services.base import ServiceBase
from planification.models import EtatProgramme, LigneProgramme
from planification.services.circuit import DECLENCHEUR_SEANCE, ServiceCircuitProgramme
from planification.services.contraintes import Candidate, ServiceContraintes
from planification.services.modification import (
    MESSAGE_AFFICHEE,
    OBJET_TYPE,
    PERMISSION_ECRITURE,
    _contexte_sans_la_seance,
    _creer_avenant,
    _refuser_si_commencee,
    _verifier_avenantage,
    _verrouiller_programme,
)

MESSAGE_DERNIERE_BRIGADE = (
    "Retirer la dernière brigade reviendrait à supprimer la séance : utilisez la "
    "suppression (M1)."
)
MESSAGE_REGROUPEMENT_EXISTANT = (
    "Cette séance réunit déjà plusieurs brigades ({brigades}) : confirmez l'association."
)
MESSAGE_BRIGADE_DEJA_PRESENTE = "{brigade} est déjà sur cette séance."
MESSAGE_BRIGADE_ABSENTE = "{brigade} n'est pas sur cette séance : rien à retirer."


def _brigades_de(seance):
    return [ligne.brigade for ligne in seance.lignes.select_related("brigade")]


def _candidates_du_regroupement(seance, brigades_supplementaires):
    """Les candidates des lignes existantes (inchangées) et des brigades
    ajoutées, toutes sous le même `cle_regroupement` — la figure d'une séance
    regroupée avant qu'elle n'existe (docstring de `Candidate`)."""
    toutes = _brigades_de(seance) + list(brigades_supplementaires)
    return [
        Candidate(
            brigade=brigade,
            element_referentiel=seance.element_referentiel,
            instructeur=seance.instructeur,
            debut=seance.debut,
            fin=seance.fin,
            lieu=seance.lieu,
            cle_regroupement=seance.pk,
        )
        for brigade in toutes
    ]


def _verifier_brigades_libres(programme, seance, brigades):
    """« Brigades libres sur le créneau » (R1) : aucune des six contraintes
    dures ne porte sur la brigade elle-même (RG-34 à RG-39 portent sur
    l'instructeur, le lieu, le calendrier et le volume) — vérifié ici, pas
    dans `ServiceContraintes`, qui en reste l'implantation exclusive."""
    conflits = LigneProgramme.objects.filter(
        brigade__in=brigades, seance__programme=programme
    ).exclude(seance=seance).select_related("seance__element_referentiel__matiere", "brigade")
    for ligne in conflits:
        autre = ligne.seance
        if se_recouvrent(seance.debut, seance.fin, autre.debut, autre.fin):
            raise ErreurValidation(
                f"{ligne.brigade} n'est pas libre sur ce créneau : elle est déjà en séance de "
                f"{autre.element_referentiel.matiere} le {autre.debut:%d/%m %H:%M}"
                f"–{autre.fin:%H:%M}."
            )


def _verifier_brigades_nouvelles(seance, brigades):
    """Une brigade déjà sur la séance (reposée depuis un formulaire périmé,
    ou une association concurrente) ne doit jamais atteindre la boucle
    d'écriture : `uq_ligne_programme_seance_brigade` la refuserait par une
    `IntegrityError` brute, pas par un refus métier."""
    deja = {brigade.pk for brigade in _brigades_de(seance)}
    vues = set()
    for brigade in brigades:
        if brigade.pk in deja or brigade.pk in vues:
            raise ErreurValidation(MESSAGE_BRIGADE_DEJA_PRESENTE.format(brigade=brigade))
        vues.add(brigade.pk)


def _verifier_contraintes_association(programme, seance, brigades):
    contexte = _contexte_sans_la_seance(programme, seance)
    candidates = _candidates_du_regroupement(seance, brigades)
    verdicts = ServiceContraintes.verifier_lot(candidates, contexte)
    violations = [v for verdict in verdicts for v in verdict.violations]
    if violations:
        lignes = (f"{v['code']} : {v['message']}" for v in violations)
        raise ErreurValidation("Association refusée — " + " ".join(lignes))


def _verifier_confirmation(seance, confirmee):
    brigades = _brigades_de(seance)
    if len(brigades) > 1 and not confirmee:
        noms = ", ".join(str(brigade) for brigade in brigades)
        raise ErreurValidation(MESSAGE_REGROUPEMENT_EXISTANT.format(brigades=noms))


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


def associer_brigades(agissant, seance, brigades, confirmee=False, avenant=None):
    """R1, R4, C1 à C5 : ajoute une ou plusieurs brigades à une séance en lieu
    partagé. La charge de l'instructeur n'est comptée qu'une fois (C4) : une
    seule `Seance`, une `LigneProgramme` de plus par brigade (D-139)."""
    verifier_habilitation(agissant, PERMISSION_ECRITURE)
    _verifier_avenantage(avenant)
    with transaction.atomic():
        programme = _verrouiller_programme(seance.programme)
        ServiceCircuitProgramme.garde_modification(
            programme, agissant, declencheur=DECLENCHEUR_SEANCE, avenant=avenant is not None
        )
        seance.refresh_from_db()
        _refuser_si_commencee(seance)
        _verifier_confirmation(seance, confirmee)
        _verifier_brigades_nouvelles(seance, brigades)
        _verifier_brigades_libres(programme, seance, brigades)
        _verifier_contraintes_association(programme, seance, brigades)
        for brigade in brigades:
            ServiceBase.creer(LigneProgramme(seance=seance, brigade=brigade), agissant)
        noms = ", ".join(str(brigade) for brigade in brigades)
        if avenant is not None:
            _creer_avenant(agissant, seance, avenant, [f"association : {noms}"])
        _journaliser(agissant, seance, f"association : {noms}")
    return seance


def retirer_brigade(agissant, seance, brigade):
    """R2 : supprime la ligne de la brigade retirée, jamais une séance
    autonome (inexprimable : même instructeur, même créneau, RG-34
    l'interdirait). Le créneau de la brigade redevient libre, à replanifier
    par ajout manuel ou régénération. R4 : refusé sur un programme affiché,
    comme la suppression (renvoi à la non-exécution)."""
    verifier_habilitation(agissant, PERMISSION_ECRITURE)
    with transaction.atomic():
        programme = _verrouiller_programme(seance.programme)
        if programme.etat == EtatProgramme.AFFICHE:
            raise ErreurValidation(MESSAGE_AFFICHEE)
        ServiceCircuitProgramme.garde_modification(
            programme, agissant, declencheur=DECLENCHEUR_SEANCE
        )
        seance.refresh_from_db()
        _refuser_si_commencee(seance)
        ligne = seance.lignes.select_related("brigade").filter(brigade=brigade).first()
        if ligne is None:
            raise ErreurValidation(MESSAGE_BRIGADE_ABSENTE.format(brigade=brigade))
        if seance.lignes.count() == 1:
            raise ErreurValidation(MESSAGE_DERNIERE_BRIGADE)
        ligne.delete()
        _journaliser(agissant, seance, f"retrait de la brigade {brigade}")
    return seance
