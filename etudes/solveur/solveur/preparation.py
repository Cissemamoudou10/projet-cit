"""Modules programmables par brigade — même pré-filtre que `app/
planification/generation/candidats.py::matieres_programmables`, partagé par
le modèle CP-SAT et l'heuristique de comparaison (Prompt 32 § 6) pour que
les deux lisent le même domaine, la divergence portant sur la STRATÉGIE de
placement, pas sur l'éligibilité.
"""

import dataclasses


@dataclasses.dataclass(frozen=True)
class Preparation:
    modules_par_brigade: dict  # brigade_id -> [module_id, ...]
    qualifies_par_module: dict  # module_id -> [instructeur_id, ...]


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


def modules_programmables(instance):
    modules_par_id = {m.id: m for m in instance.modules}
    modules_de_la_formation = {}
    for module in instance.modules:
        modules_de_la_formation.setdefault(module.formation_id, []).append(module)

    modules_par_brigade = {
        brigade.id: _modules_eligibles(brigade, modules_de_la_formation, modules_par_id)
        for brigade in instance.brigades
    }

    return Preparation(
        modules_par_brigade=modules_par_brigade,
        qualifies_par_module=_qualifies_par_module(instance.instructeurs),
    )
