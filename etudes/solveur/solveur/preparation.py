"""Modules programmables par brigade — même pré-filtre que `app/
planification/generation/candidats.py::matieres_programmables`, partagé par
le modèle CP-SAT et l'heuristique de comparaison (Prompt 32 § 6) pour que
les deux lisent le même domaine, la divergence portant sur la STRATÉGIE de
placement, pas sur l'éligibilité.

Deux niveaux, distincts depuis la revue du 2026-09-18 :
- `modules_eligibles` : volume restant et prérequis (RG-39) — ce que fait
  l'application ;
- `modules_programmables` : les éligibles qui figurent au PROGRAMME CIBLE de
  la brigade (`Brigade.programme_cible`), c'est-à-dire ce qu'il y a
  réellement à pourvoir cette semaine.
"""

import dataclasses


@dataclasses.dataclass(frozen=True)
class Preparation:
    modules_par_brigade: dict  # brigade_id -> [module_id, ...] (programme cible)
    qualifies_par_module: dict  # module_id -> [instructeur_id, ...]
    # Instructeurs qualifiés sur au moins un module d'un programme cible :
    # les seuls dont la charge PEUT être répartie. Un instructeur qualifié
    # sur rien de ce qu'on a à pourvoir reste à zéro quoi qu'on fasse — le
    # compter dans l'écart de charge mesurerait la charge maximale, pas
    # l'équilibre (constaté sur la première matrice, 4 instructeurs sur 100).
    mobilisables: frozenset


def _volume_restant(module):
    return module.volume_prescrit - module.volume_deja_programme


def _prerequis_acheve(module, brigade, modules_par_id):
    if module.prerequis_id is None:
        return True
    acquis = brigade.volume_deja_programme.get(module.prerequis_id, 0.0)
    return acquis >= modules_par_id[module.prerequis_id].volume_prescrit


def _modules_eligibles(brigade, modules_de_la_formation, modules_par_id):
    eligibles = []
    for module in modules_de_la_formation.get(brigade.formation_id, []):
        if _volume_restant(module) <= 0:
            continue
        if not _prerequis_acheve(module, brigade, modules_par_id):
            continue
        eligibles.append(module.id)
    return eligibles


def _qualifies_par_module(instructeurs):
    par_module = {}
    for instructeur in instructeurs:
        for module_id in instructeur.modules_qualifies:
            par_module.setdefault(module_id, []).append(instructeur.id)
    return par_module


def modules_eligibles(instance):
    modules_par_id = {m.id: m for m in instance.modules}
    modules_de_la_formation = {}
    for module in instance.modules:
        modules_de_la_formation.setdefault(module.formation_id, []).append(module)
    return {
        brigade.id: _modules_eligibles(brigade, modules_de_la_formation, modules_par_id)
        for brigade in instance.brigades
    }


def modules_programmables(instance):
    eligibles = modules_eligibles(instance)
    modules_par_brigade = {
        brigade.id: [
            module_id
            for module_id in eligibles[brigade.id]
            if brigade.programme_cible.get(module_id, 0) > 0
        ]
        for brigade in instance.brigades
    }
    qualifies_par_module = _qualifies_par_module(instance.instructeurs)
    mobilisables = frozenset(
        instructeur_id
        for module_ids in modules_par_brigade.values()
        for module_id in module_ids
        for instructeur_id in qualifies_par_module.get(module_id, [])
    )
    return Preparation(
        modules_par_brigade=modules_par_brigade,
        qualifies_par_module=qualifies_par_module,
        mobilisables=mobilisables,
    )
