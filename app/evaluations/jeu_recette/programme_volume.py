"""Programmes du jeu volumineux — Prompt 51, Temps 3, § 3.1 et § 3.2. Douze
semaines (W-8 à W+3) pour les 32 brigades actives : W-8 à W-1 affichées
(≈5 % d'avenants, ≈3 % de non-exécutions — § 3.1, ces deux proportions ne
visent QUE ces huit semaines, jamais W0) ; W0 affichée ; W+1 validée ; W+2
soumise ; W+3 brouillon.

Horloge simulée seulement pour les avenants (`_refuser_si_commencee` exige
`séance.debut > maintenant`, et les séances des semaines passées ont un
`debut` réellement passé) — gelée au lundi 00:01 de la semaine visée,
avant le premier créneau de la grille (08:00). Les transitions du circuit
(soumettre/valider/signer/afficher) et les non-exécutions, eux, ne
regardent que l'état du programme ou une séance déjà réellement terminée :
aucune horloge simulée n'y est nécessaire, à la différence de l'état
`complet` — simplification délibérée, propre au jeu volumineux (mesure de
performance, pas restitution d'un scénario métier), consignée dans
`docs/recette/JEUX-DE-DONNEES-PHASE-6.md`."""

import dataclasses
import datetime
import time

from django.utils import timezone

from evaluations.jeu_recette.creneaux import creneau_libre
from evaluations.jeu_recette.donnees_volume import (
    PROPORTION_SEANCES_AVEC_AVENANT,
    PROPORTION_SEANCES_NON_EXECUTEES,
    SEMAINES_PASSEES_AFFICHEES,
)
from evaluations.jeu_recette.semaines import semaine
from noyau.exceptions import ErreurValidation
from planification.models import LigneProgramme, NatureAvenant, Seance
from planification.selectors import grille_active_avec_creneaux
from planification.services.circuit import ServiceCircuitProgramme
from planification.services.ecriture import ServiceEcritureSeance
from planification.services.generation import ServiceGeneration
from planification.services.modification import Avenantage
from planification.services.suivi import ServiceSuivi

SIGNATAIRE = "Directeur de la formation (fictif, jeu volumineux)."
MOTIF_AVENANT = "Déplacement de séance (jeu volumineux, § 3.1)."
MOTIF_NON_EXECUTION = "Instructeur en mission (jeu volumineux, § 3.1)."
JOURS_OPERATIONNELS_ISO = (1, 2, 3, 4, 5, 6)


@dataclasses.dataclass(frozen=True)
class MesureSemaine:
    semaine: str
    duree_secondes: float
    cases_a_pourvoir: int
    cases_non_pourvues: int
    etat_final: str


@dataclasses.dataclass(frozen=True)
class AgissantsProgrammeVolume:
    """`.claude/rules/python.md`, § 5 paramètres max — les deux agissants
    voyagent toujours ensemble dans ce module."""

    agissant_plan: object
    agissant_ped: object


@dataclasses.dataclass(frozen=True)
class ParametresSemaine:
    lundi: datetime.date
    decalage: int
    brigades: list
    creneaux: list


@dataclasses.dataclass(frozen=True)
class ContextePose:
    """Ce qu'il faut pour chercher un créneau de repli — sans-objet pour
    `decalage`/`brigades`, propres au niveau de la semaine entière."""

    lundi: datetime.date
    creneaux: list


@dataclasses.dataclass(frozen=True)
class OptionsProgrammesVolume:
    """`semaines_passees` : repli `--semaines N` (§ 3.2) si le chargement
    complet dépasse 30 minutes — par défaut `SEMAINES_PASSEES_AFFICHEES`
    (les huit semaines du § 3.1), jamais davantage."""

    brigades_actives: dict
    date_reference: datetime.date
    semaines_passees: int = SEMAINES_PASSEES_AFFICHEES


def _generer(agissant_plan, lundi, brigades):
    debut = time.monotonic()
    resultat = ServiceGeneration.generer(agissant_plan, lundi, brigades)
    duree = time.monotonic() - debut
    return resultat, duree


def _approuver(agissants: AgissantsProgrammeVolume, programme, jusqu_a):
    """A9 : un programme SANS AUCUNE SÉANCE refuse la soumission — référentiel
    épuisé ou semaine entièrement bloquée par le calendrier (RG-38) sont des
    MESURES à ce volume, pas des anomalies à masquer (§ 3.2) : la fonction
    rend alors `"brouillon"` au lieu de l'état demandé, sans lever."""
    if not Seance.objects.filter(programme=programme).exists():
        return programme, "brouillon"
    ServiceCircuitProgramme.soumettre(agissants.agissant_plan, programme)
    programme.refresh_from_db()
    if jusqu_a == "soumis":
        return programme, "soumis"
    ServiceCircuitProgramme.valider(agissants.agissant_ped, programme)
    programme.refresh_from_db()
    if jusqu_a == "valide":
        return programme, "valide"
    aujourd_hui = timezone.localdate()
    ServiceCircuitProgramme.enregistrer_signature(agissants.agissant_plan, programme, aujourd_hui, SIGNATAIRE)
    programme.refresh_from_db()
    ServiceCircuitProgramme.afficher(agissants.agissant_plan, programme)
    programme.refresh_from_db()
    return programme, "affiche"


def _candidats_jour_creneau(programme, brigade, contexte_pose: ContextePose):
    for jour_iso in JOURS_OPERATIONNELS_ISO:
        creneau = creneau_libre(programme, brigade, jour_iso, contexte_pose.creneaux)
        if creneau is not None:
            yield contexte_pose.lundi + datetime.timedelta(days=jour_iso - 1), creneau


def _tenter_deplacement(agissant_plan, programme, seance, brigade, contexte_pose: ContextePose):
    """Un créneau libre pour la brigade ne garantit pas l'absence d'une
    période de calendrier bloquante (RG-38) sur ce jour précis — plusieurs
    candidats sont donc essayés, le premier qui passe l'emporte, aucun
    n'étant une anomalie acceptée (≈5 %, au mieux)."""
    for jour_cible, creneau in _candidats_jour_creneau(programme, brigade, contexte_pose):
        seance.refresh_from_db()
        duree = seance.fin - seance.debut
        nouveau_debut = timezone.make_aware(datetime.datetime.combine(jour_cible, creneau.heure_debut))
        try:
            ServiceEcritureSeance.modifier_seance(
                agissant_plan,
                seance,
                {"debut": nouveau_debut, "fin": nouveau_debut + duree},
                avenant=Avenantage(motif=MOTIF_AVENANT, nature=NatureAvenant.DEPLACEMENT),
            )
        except ErreurValidation:
            continue
        return True
    return False


def _poser_avenants(agissant_plan, programme, lundi, generateur):
    """Gèle l'horloge au lundi 00:01 — avant le premier créneau (08:00) —
    pour que `_refuser_si_commencee` laisse passer la modification."""
    from freezegun import freeze_time

    seances = list(Seance.objects.filter(programme=programme))
    nombre = round(len(seances) * PROPORTION_SEANCES_AVEC_AVENANT)
    if nombre == 0 or not seances:
        return 0
    _, creneaux = grille_active_avec_creneaux()
    contexte_pose = ContextePose(lundi, creneaux)
    instant_gel = timezone.make_aware(datetime.datetime.combine(lundi, datetime.time(0, 1)))
    poses = 0
    with freeze_time(instant_gel):
        for seance in generateur.sample(seances, nombre):
            brigade = seance.lignes.first().brigade
            if _tenter_deplacement(agissant_plan, programme, seance, brigade, contexte_pose):
                poses += 1
    return poses


def _declarer_non_executions(agissant_plan, programme, generateur):
    """Horloge réelle : les semaines visées (W-8 à W-1) sont déjà
    réellement passées, `_verifier_seance_passee` passe sans simulation."""
    lignes = list(LigneProgramme.objects.filter(seance__programme=programme))
    nombre = round(len(lignes) * PROPORTION_SEANCES_NON_EXECUTEES)
    for ligne in generateur.sample(lignes, min(nombre, len(lignes))):
        if getattr(ligne, "non_execution", None) is not None:
            continue
        ServiceSuivi.declarer_non_execution(agissant_plan, ligne, MOTIF_NON_EXECUTION)
    return nombre


def _mesurer_remplissage(resultat, brigades, creneaux):
    cases_a_pourvoir = len(brigades) * len(creneaux)
    return cases_a_pourvoir, len(resultat.cases_non_pourvues)


def charger_semaine_passee_volume(agissants: AgissantsProgrammeVolume, generateur, parametres: ParametresSemaine, stdout):
    resultat, duree = _generer(agissants.agissant_plan, parametres.lundi, parametres.brigades)
    programme, etat_final = _approuver(agissants, resultat.programme, "affiche")
    nombre_avenants = (
        _poser_avenants(agissants.agissant_plan, programme, parametres.lundi, generateur)
        if etat_final == "affiche" else 0
    )
    nombre_non_executees = (
        _declarer_non_executions(agissants.agissant_plan, programme, generateur) if etat_final == "affiche" else 0
    )
    cases_a_pourvoir, cases_non_pourvues = _mesurer_remplissage(resultat, parametres.brigades, parametres.creneaux)
    stdout.write(
        f"  Semaine {parametres.decalage} générée en {duree:.2f} s, état {etat_final}, {nombre_avenants} avenant(s), "
        f"{nombre_non_executees} non-exécution(s), {cases_non_pourvues}/{cases_a_pourvoir} cases non pourvues."
    )
    return MesureSemaine(f"W{parametres.decalage}", duree, cases_a_pourvoir, cases_non_pourvues, etat_final)


def charger_semaine_future_volume(agissants: AgissantsProgrammeVolume, parametres: ParametresSemaine, jusqu_a, stdout):
    resultat, duree = _generer(agissants.agissant_plan, parametres.lundi, parametres.brigades)
    programme = resultat.programme
    etat_final = jusqu_a
    if jusqu_a != "brouillon":
        _, etat_final = _approuver(agissants, programme, jusqu_a)
    cases_a_pourvoir, cases_non_pourvues = _mesurer_remplissage(resultat, parametres.brigades, parametres.creneaux)
    stdout.write(
        f"  Semaine {parametres.decalage} générée en {duree:.2f} s, état {etat_final}, "
        f"{cases_non_pourvues}/{cases_a_pourvoir} cases non pourvues."
    )
    decalage = parametres.decalage
    libelle = f"W{'+' if decalage >= 0 else ''}{decalage}" if decalage else "W0"
    return MesureSemaine(libelle, duree, cases_a_pourvoir, cases_non_pourvues, etat_final)


def charger_programmes_volume(agissants: AgissantsProgrammeVolume, generateur, options: OptionsProgrammesVolume, stdout):
    brigades = list(options.brigades_actives.values())
    _, creneaux = grille_active_avec_creneaux()
    mesures = []
    for decalage in range(-options.semaines_passees, 0):
        lundi = semaine(options.date_reference, decalage)
        parametres = ParametresSemaine(lundi, decalage, brigades, creneaux)
        mesures.append(charger_semaine_passee_volume(agissants, generateur, parametres, stdout))
    plan_futur = ((0, "affiche"), (1, "valide"), (2, "soumis"), (3, "brouillon"))
    for decalage, jusqu_a in plan_futur:
        lundi = semaine(options.date_reference, decalage)
        parametres = ParametresSemaine(lundi, decalage, brigades, creneaux)
        mesures.append(charger_semaine_future_volume(agissants, parametres, jusqu_a, stdout))
    return mesures
