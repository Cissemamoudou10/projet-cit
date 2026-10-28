"""`--verifier` du jeu volumineux — Prompt 51, Temps 3, § 3.2 : « mêmes
invariants que l'état `complet`, à l'échelle ». Lecture seule. Réutilise le
patron de rapport du jeu `socle` (`verification.py::LigneRapport`/
`_ligne`/`_imprimer`).

Les six contraintes dures (RG-34 à RG-39) sont déjà l'implantation UNIQUE de
`ServiceContraintes`, appelée par la génération et par toute modification
manuelle (`.claude/rules/services.md`) : un objet en base ne peut donc pas
les violer, sauf défaut du chargeur lui-même. Les contrôles ci-dessous sont
des contre-mesures de ce défaut-là (une anomalie DANS CE CHARGEUR), pas une
réimplémentation des règles elles-mêmes — jamais dupliquées ailleurs
(`.claude/rules/services.md`, « duplication »)."""

from django.db.models import Count
from django.utils import timezone

from evaluations.jeu_recette.donnees_volume import (
    NOMBRE_BRIGADES_ACTIVES,
    NOMBRE_CERTIFICATIVES_A_VENIR,
    NOMBRE_FORMATIONS,
    NOMBRE_FORMATIONS_ARCHIVEES,
    NOMBRE_INSTRUCTEURS,
    NOMBRE_MATIERES_CATALOGUE,
    NOMBRE_SALLES_ATTITREES,
    NOMBRE_SESSIONS_A_VENIR,
    NOMBRE_SESSIONS_ACTIVES,
    NOMBRE_SESSIONS_TERMINEES,
    NOMBRE_SESSIONS_TERMINEES_AVEC_PV,
    SEMAINES_PASSEES_AFFICHEES,
)
from evaluations.jeu_recette.verification import _imprimer, _ligne
from evaluations.models import Evaluation, ProcesVerbal, TypeEvaluation
from organisation.models import Brigade, Session, Stagiaire
from planification.models import LigneProgramme, ProgrammeHebdomadaire
from referentiel.models import Formation, Matiere
from ressources.models import Instructeur, Lieu, SalleAttitree


def verifier_volume(stdout):
    lignes = (
        _verifier_volumes_cibles()
        + _verifier_programmes_volume()
        + _verifier_evaluations_volume()
        + _verifier_contraintes_dures()
    )
    _imprimer(stdout, "État du jeu volumineux (§ 3.1, § 3.2)", lignes)


def _verifier_volumes_cibles():
    lignes = []
    lignes += _ligne(Matiere.objects.count() >= NOMBRE_MATIERES_CATALOGUE, "Catalogue des matières au complet")
    lignes += _ligne(Formation.objects.count() == NOMBRE_FORMATIONS, f"{NOMBRE_FORMATIONS} formations")
    lignes += _ligne(
        Formation.objects.filter(archive=True).count() == NOMBRE_FORMATIONS_ARCHIVEES,
        f"{NOMBRE_FORMATIONS_ARCHIVEES} formation archivée",
    )
    lignes += _ligne(Instructeur.objects.count() == NOMBRE_INSTRUCTEURS, f"{NOMBRE_INSTRUCTEURS} instructeurs")
    lignes += _ligne(
        SalleAttitree.objects.count() >= NOMBRE_BRIGADES_ACTIVES, "Chaque brigade active a sa salle attitrée"
    )
    lignes += _ligne(Lieu.objects.count() >= NOMBRE_SALLES_ATTITREES, f"{NOMBRE_SALLES_ATTITREES} salles attitrées")
    lignes += _ligne(
        Session.objects.count() == NOMBRE_SESSIONS_ACTIVES + NOMBRE_SESSIONS_A_VENIR + NOMBRE_SESSIONS_TERMINEES,
        f"{NOMBRE_SESSIONS_ACTIVES} sessions actives échelonnées + {NOMBRE_SESSIONS_A_VENIR} à venir "
        f"+ {NOMBRE_SESSIONS_TERMINEES} terminées",
    )
    lignes += _ligne(
        Brigade.objects.filter(session__intitule__startswith="SV-A").count() == NOMBRE_BRIGADES_ACTIVES,
        f"{NOMBRE_BRIGADES_ACTIVES} brigades actives",
    )
    lignes += _ligne(Stagiaire.objects.count() >= 800, "≈900 stagiaires chargés")
    lignes += _ligne(Stagiaire.objects.filter(radie=True).count() > 0, "Des stagiaires radiés présents")
    return lignes


def _verifier_programmes_volume():
    nombre_attendu = SEMAINES_PASSEES_AFFICHEES + 4  # W-8..W-1, W0, W+1, W+2, W+3
    lignes = []
    lignes += _ligne(
        ProgrammeHebdomadaire.objects.count() == nombre_attendu, f"{nombre_attendu} programmes hebdomadaires"
    )
    doublons = (
        ProgrammeHebdomadaire.objects.values("lundi_de_semaine")
        .order_by()
        .annotate(nombre=Count("id"))
        .filter(nombre__gt=1)
    )
    lignes += _ligne(not doublons.exists(), "Un seul programme par semaine")
    return lignes


def _verifier_evaluations_volume():
    """`brigades_demarrees` : une brigade dont la session démarre en W+1
    (correctif du 27/10/2026) n'a droit à aucune formative encore — seule
    une comparaison à `aujourd'hui`, pas à `NOMBRE_BRIGADES_ACTIVES`, est
    juste (même réserve que `_verifier_programmes_complet` : valide si
    `--verifier` tourne le jour même du chargement)."""
    lignes = []
    brigades_demarrees = Brigade.objects.filter(
        session__intitule__startswith="SV-A", session__date_debut__lte=timezone.localdate()
    ).count()
    lignes += _ligne(
        Evaluation.objects.filter(type=TypeEvaluation.FORMATIVE, brigade__session__intitule__startswith="SV-A").count()
        == brigades_demarrees,
        f"Une formative par brigade active déjà démarrée ({brigades_demarrees})",
    )
    lignes += _ligne(
        Evaluation.objects.filter(type=TypeEvaluation.CERTIFICATIVE, session__isnull=False).count()
        == NOMBRE_CERTIFICATIVES_A_VENIR,
        f"{NOMBRE_CERTIFICATIVES_A_VENIR} certificatives à venir",
    )
    lignes += _ligne(
        ProcesVerbal.objects.count() == NOMBRE_SESSIONS_TERMINEES_AVEC_PV,
        f"{NOMBRE_SESSIONS_TERMINEES_AVEC_PV} procès-verbaux de fin de formation",
    )
    return lignes


def _verifier_rg34():
    """Un instructeur sur deux séances DISTINCTES à la même heure de début
    — proxy délibérément simplifié (même `debut` exact, pas un chevauchement
    quelconque) : suffisant pour une génération sur grille, voir docstring
    du module."""
    doublons = (
        LigneProgramme.objects.values("seance__instructeur_id", "seance__debut")
        .order_by()
        .annotate(nombre_seances=Count("seance_id", distinct=True))
        .filter(nombre_seances__gt=1, seance__instructeur_id__isnull=False)
    )
    return _ligne(not doublons.exists(), "RG-34 : aucun instructeur sur deux séances distinctes au même instant")


def _verifier_rg13():
    """RG-13/14 : capacité de la salle attitrée jamais dépassée par
    l'effectif prévisionnel de sa brigade — déjà garanti à l'écriture par
    `ServiceSalleAttitree.attribuer`, recontrôlé ici en lecture."""
    depassements = [
        salle for salle in SalleAttitree.objects.select_related("brigade", "lieu")
        if salle.brigade.effectif_previsionnel > salle.lieu.capacite
    ]
    return _ligne(not depassements, "RG-13/14 : aucune salle attitrée sous-capacitaire")


def _verifier_contraintes_dures():
    return _verifier_rg34() + _verifier_rg13()
