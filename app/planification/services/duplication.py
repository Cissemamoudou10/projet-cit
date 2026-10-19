"""`ServiceDuplication` — US-PLAN-11, duplication d'un programme hebdomadaire
sur une semaine cible (prompt 48, Story 4).

D1, porte unique : chaque séance dupliquée s'écrit par
`ServiceEcritureSeance.creer_seances`, jamais par une instanciation directe
(`tests/architecture/test_couches.py::
test_seule_la_porte_d_ecriture_instancie_seance_ou_ligne_programme` le
vérifie déjà, sans test dédié de plus). La garde d'état de la cible
réutilise l'ÉVÉNEMENT `GENERER` du circuit (pas un nouvel événement) :
D1 demande exactement le même comportement que la génération — BROUILLON
admis, REJETÉ ramené au brouillon par la reprise implicite (T6), les autres
états refusés — `docs/conception/ETA-01_table_transitions.md` § 4.1 n'a
donc pas à changer.

D4, regroupement : chaque candidate d'un même groupe (même séance source)
est évaluée INDÉPENDAMMENT contre le contexte ET les candidates déjà
acceptées des groupes précédents — si une seule brigade d'un groupe est
refusée, les autres sont quand même dupliquées ; le groupe entier n'est
abandonné que si TOUTES ses candidates sont refusées.
"""

import dataclasses
import datetime

from django.db import transaction
from django.utils import timezone

from administration.habilitations import verifier_habilitation
from administration.models import TypeAction
from administration.services.journal import DonneesEntreeJournal, ServiceJournal
from noyau.services.parametres import ResolveurSeancesDeControle
from planification.models import LigneProgramme, ProgrammeHebdomadaire
from planification.services.circuit import DECLENCHEUR_DUPLICATION, GENERER, ServiceCircuitProgramme
from planification.services.contraintes import Candidate, ServiceContraintes
from planification.services.ecriture import ServiceEcritureSeance
from planification.services.temps import valider_lundi

PERMISSION_ECRITURE = ServiceEcritureSeance.PERMISSION_ECRITURE

MOTIF_CONTROLE = "séance d'un contrôle, liée à une évaluation datée (D3)"
MOTIF_NON_EXECUTEE = "séance déclarée non exécutée (D3)"


@dataclasses.dataclass(frozen=True)
class SeanceExclue:
    """D3 : jamais dupliquée, listée avec son motif."""

    seance: object
    motif: str


@dataclasses.dataclass(frozen=True)
class CandidateRefusee:
    """D4 : une candidate refusée par une contrainte dure, listée avec ses
    violations — les autres candidates du même groupe ne sont pas perdues."""

    brigade: object
    element_referentiel: object
    violations: list


@dataclasses.dataclass(frozen=True)
class CompteRenduDuplication:
    programme_source: object
    programme_cible: object
    nombre_creees: int
    exclues: list
    refusees: list


def _instant_equivalent(instant_source, lundi_cible):
    """D2 : même jour de semaine, mêmes heures — heures réelles de la
    séance source, grille active jamais consultée."""
    local = timezone.localtime(instant_source)
    jour = lundi_cible + datetime.timedelta(days=local.isoweekday() - 1)
    return timezone.make_aware(datetime.datetime.combine(jour, local.time()))


def _candidate(ligne, lundi_cible):
    seance = ligne.seance
    return Candidate(
        brigade=ligne.brigade,
        element_referentiel=seance.element_referentiel,
        instructeur=seance.instructeur,
        lieu=seance.lieu,
        debut=_instant_equivalent(seance.debut, lundi_cible),
        fin=_instant_equivalent(seance.fin, lundi_cible),
        cle_regroupement=seance.pk,
    )


def _groupes_sources(programme_source, brigades):
    """D3 : exclut les lignes déclarées non exécutées (par ligne — une
    séance regroupée dont une seule brigade est concernée garde les autres)
    puis les séances de contrôle (par séance entière, un seul appel au
    résolveur). Groupé par séance source, dans l'ordre chronologique :
    déterministe pour l'évaluation « sensible à l'ordre » des contraintes."""
    brigade_ids = {brigade.pk for brigade in brigades}
    lignes = (
        LigneProgramme.objects.filter(seance__programme=programme_source, brigade_id__in=brigade_ids)
        .select_related(
            "seance__element_referentiel__matiere",
            "seance__instructeur",
            "seance__lieu",
            "brigade",
            "non_execution",
        )
        .order_by("seance__debut", "seance_id")
    )
    exclues, par_seance = [], {}
    for ligne in lignes:
        if getattr(ligne, "non_execution", None) is not None:
            exclues.append(SeanceExclue(seance=ligne.seance, motif=MOTIF_NON_EXECUTEE))
            continue
        par_seance.setdefault(ligne.seance_id, []).append(ligne)

    ids_controle = ResolveurSeancesDeControle.resoudre(set(par_seance.keys()))
    groupes = []
    for seance_id, lignes_du_groupe in par_seance.items():
        if seance_id in ids_controle:
            exclues.append(SeanceExclue(seance=lignes_du_groupe[0].seance, motif=MOTIF_CONTROLE))
            continue
        groupes.append(lignes_du_groupe)
    return groupes, exclues


def _evaluer_groupes(groupes_lignes, lundi_cible, contexte):
    groupes_acceptes, refusees, provisoires = [], [], []
    for lignes_du_groupe in groupes_lignes:
        survivantes = []
        for ligne in lignes_du_groupe:
            candidate = _candidate(ligne, lundi_cible)
            verdict = ServiceContraintes.verifier(candidate, contexte, provisoires)
            if verdict.accepte:
                survivantes.append(candidate)
                provisoires.append(candidate)
            else:
                refusees.append(
                    CandidateRefusee(
                        brigade=candidate.brigade,
                        element_referentiel=candidate.element_referentiel,
                        violations=verdict.violations,
                    )
                )
        if survivantes:
            groupes_acceptes.append(survivantes)
    return groupes_acceptes, refusees


def _journaliser_acte(agissant, programme_cible, detail):
    ServiceJournal.enregistrer_detaillee(
        DonneesEntreeJournal(
            type_action=TypeAction.GENERATION_PROGRAMME,
            identifiant_saisi=str(programme_cible),
            auteur=agissant,
            objet_type="programme",
            objet_identifiant=str(programme_cible.pk),
            detail=detail,
        )
    )


class ServiceDuplication:
    DOMAINE = "programme"
    PERMISSION_ECRITURE = PERMISSION_ECRITURE

    @staticmethod
    def dupliquer(agissant, programme_source, lundi_cible, brigades) -> CompteRenduDuplication:
        """D6 : tout ou rien au niveau technique — une seule transaction,
        imbriquée dans celle de `ServiceEcritureSeance.creer_seances` (même
        patron que `ServiceGeneration.generer`). Les refus métier (D3, D4)
        écartent des candidates sans annuler l'opération."""
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        valider_lundi(lundi_cible)
        groupes_lignes, exclues = _groupes_sources(programme_source, brigades)
        with transaction.atomic():
            programme_cible, _ = ProgrammeHebdomadaire.objects.get_or_create(
                lundi_de_semaine=lundi_cible
            )
            programme_cible = ServiceCircuitProgramme.garde_modification(
                programme_cible, agissant, evenement=GENERER, declencheur=DECLENCHEUR_DUPLICATION
            )
            contexte = ServiceContraintes.contexte(programme_cible)
            groupes_acceptes, refusees = _evaluer_groupes(groupes_lignes, lundi_cible, contexte)
            ServiceEcritureSeance.creer_seances(agissant, programme_cible, groupes_acceptes)
            detail = (
                f"Depuis la semaine du {programme_source.lundi_de_semaine:%d/%m/%Y} — "
                f"{len(groupes_acceptes)} séance(s) créée(s), {len(exclues)} exclue(s) (D3), "
                f"{len(refusees)} candidate(s) refusée(s)."
            )
            _journaliser_acte(agissant, programme_cible, detail)
        return CompteRenduDuplication(
            programme_source=programme_source,
            programme_cible=programme_cible,
            nombre_creees=len(groupes_acceptes),
            exclues=exclues,
            refusees=refusees,
        )
