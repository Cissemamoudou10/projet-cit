"""Orchestration des mesures — Prompt 32 § 8. Exécute le modèle CP-SAT et
l'heuristique de comparaison sur la même instance, capture les mesures
demandées. `resource` (mémoire) est POSIX — cohérent avec la machine de
mesure retenue (PROTOCOLE.md § 8 : conteneur `python:3.14.4-slim-bookworm`),
mais absent sous Windows : import protégé pour que la collecte `pytest` ne
casse jamais sur le poste de développement (`memoire_max_ko` vaut alors
`None`, jamais une valeur inventée).
"""

import dataclasses
import time

try:
    import resource
except ImportError:  # Windows — la mesure de mémoire ne s'y prend pas
    resource = None

from ortools.sat.python import cp_model

from solveur import modele as module_modele
from solveur.heuristique import generer as generer_heuristique


@dataclasses.dataclass(frozen=True)
class MesureSolveur:
    regime: str
    statut: str
    temps_premiere_solution: float | None
    temps_final: float
    taux_remplissage: float
    ecart_optimalite: float | None
    ecart_charge: int | None
    memoire_max_ko: int | None


@dataclasses.dataclass(frozen=True)
class MesureHeuristique:
    temps_total: float
    taux_remplissage: float
    ecart_charge: int


class _RappelPremiereSolution(cp_model.CpSolverSolutionCallback):
    """§ 8 : « temps jusqu'à la première solution admissible » — un
    `Solve` seul ne le rapporte pas, seul un rappel appelé à chaque
    amélioration le peut."""

    def __init__(self):
        super().__init__()
        self._depart = time.perf_counter()
        self.temps_premiere_solution = None

    def on_solution_callback(self):
        if self.temps_premiere_solution is None:
            self.temps_premiere_solution = time.perf_counter() - self._depart


def _memoire_max_ko():
    if resource is None:
        return None
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss


def _taux_remplissage(solveur, variables, cases_ouvertes):
    if cases_ouvertes == 0:
        return 0.0
    remplies = sum(solveur.Value(v) for v in variables.x.values())
    return remplies / cases_ouvertes


def _ecart_charge_solution(solveur, variables, regime):
    if regime != module_modele.REGIME_EQUILIBRAGE:
        return None
    charges = [solveur.Value(v) for v in variables.charge.values()]
    return (max(charges) - min(charges)) if charges else None


def _ecart_optimalite(solveur, regime):
    if regime == module_modele.REGIME_SATISFACTION:
        return None
    return abs(solveur.BestObjectiveBound() - solveur.ObjectiveValue())


def mesurer_solveur(instance, regime, borne_temps_secondes):
    modele, variables = module_modele.construire(instance)
    module_modele.configurer_objectif(modele, variables, regime)
    solveur = cp_model.CpSolver()
    solveur.parameters.max_time_in_seconds = borne_temps_secondes

    rappel = _RappelPremiereSolution()
    depart = time.perf_counter()
    statut = solveur.Solve(modele, rappel)  # `Solve` prend le rappel directement dans cette version
    temps_final = time.perf_counter() - depart

    cases_ouvertes = len(instance.brigades) * len(instance.creneaux)
    admissible = statut in (cp_model.OPTIMAL, cp_model.FEASIBLE)

    return MesureSolveur(
        regime=regime,
        statut=solveur.StatusName(statut),
        temps_premiere_solution=rappel.temps_premiere_solution,
        temps_final=temps_final,
        taux_remplissage=_taux_remplissage(solveur, variables, cases_ouvertes) if admissible else 0.0,
        ecart_optimalite=_ecart_optimalite(solveur, regime) if admissible else None,
        ecart_charge=_ecart_charge_solution(solveur, variables, regime) if admissible else None,
        memoire_max_ko=_memoire_max_ko(),
    )


def _charge_par_instructeur(placements):
    charge = {}
    for _brigade_id, _creneau_id, _module_id, instructeur_id, _lieu_id in placements:
        charge[instructeur_id] = charge.get(instructeur_id, 0) + 1
    return charge


def mesurer_heuristique(instance, duree_creneau_heures):
    depart = time.perf_counter()
    resultat = generer_heuristique(instance, duree_creneau_heures)
    temps_total = time.perf_counter() - depart

    taux = len(resultat.placements) / resultat.cases_ouvertes if resultat.cases_ouvertes else 0.0
    charges = list(_charge_par_instructeur(resultat.placements).values())
    ecart = (max(charges) - min(charges)) if charges else 0

    return MesureHeuristique(temps_total=temps_total, taux_remplissage=taux, ecart_charge=ecart)
