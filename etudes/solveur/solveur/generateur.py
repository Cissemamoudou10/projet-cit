"""Générateur d'instances — Prompt 32 § 3/§ 4/§ 6. Paramétré par la taille
(§ 3) et les deux axes de sensibilité (§ 4), graine aléatoire fixée et
consignée dans `meta`.

Simplifications déclarées (PROTOCOLE.md § 5) : pas de regroupement de
brigades, une séance par créneau, prérequis pré-filtrés, aucune
indisponibilité (RG-36) ni période bloquante (RG-38), salle attitrée
toujours suffisante (RG-37, sous-cas hors modèle).
"""

import dataclasses
import random

from solveur.instance import Brigade, Creneau, Instance, Instructeur, LieuPartage, Module

TAILLES = {
    "CONTROLE": {
        "nb_sessions": 1,
        "nb_brigades": 3,
        "nb_instructeurs": 9,
        "nb_modules": 8,
        "nb_lieux_partages": 1,
        "nb_creneaux": 20,
    },
    "REELLE": {
        "nb_sessions": 15,
        "nb_brigades": 33,
        "nb_instructeurs": 100,
        "nb_modules": 85,
        "nb_lieux_partages": 7,
        "nb_creneaux": 20,
    },
    "HAUTE": {
        "nb_sessions": 15,
        "nb_brigades": 35,
        "nb_instructeurs": 120,
        "nb_modules": 100,
        "nb_lieux_partages": 8,
        "nb_creneaux": 20,
    },
}

TYPES_LIEU_PARTAGE = ["amphitheatre", "laboratoire", "garage", "terrain"]
VOLUME_PRESCRIT_MIN, VOLUME_PRESCRIT_MAX = 20, 40
EFFECTIF_MIN, EFFECTIF_MAX = 15, 25
PROBABILITE_PREREQUIS = 0.3
PROBABILITE_PREREQUIS_ACQUIS = 0.7


@dataclasses.dataclass(frozen=True)
class ParametresInstance:
    """`.claude/rules/python.md`, § 5 paramètres max — les quatre axes du
    prompt (taille + deux de sensibilité + graine) voyagent ensemble."""

    taille: str
    demande_lieux_partages: float
    densite_qualification: int
    fraction_modules_rares: float
    graine: int


def _creneaux(n):
    jours = ["lundi", "mardi", "mercredi", "jeudi", "vendredi"]
    return [Creneau(id=i, jour=jours[i % len(jours)], ordre=i // len(jours) + 1) for i in range(n)]


def _lieux_partages(rng, n):
    lieux = []
    for i in range(n):
        mode = "SIMULTANE" if i % 2 == 0 else "SEQUENTIEL"
        lieux.append(
            LieuPartage(
                id=f"LP{i}",
                type=TYPES_LIEU_PARTAGE[i % len(TYPES_LIEU_PARTAGE)],
                capacite=rng.randint(20, 40) if mode == "SIMULTANE" else 1,
                mode=mode,
            )
        )
    return lieux


def _formations(n):
    return [f"F{i}" for i in range(n)]


def _brigades(rng, formations, n):
    return [
        Brigade(
            id=f"B{i}",
            formation_id=formations[i % len(formations)],
            effectif=rng.randint(EFFECTIF_MIN, EFFECTIF_MAX),
            volume_deja_programme={},
        )
        for i in range(n)
    ]


def _type_lieu_pour(rng, lieux_partages):
    types_disponibles = sorted({lieu.type for lieu in lieux_partages})
    return rng.choice(types_disponibles)


def _modules(rng, formations, n, lieux_partages, parametres):
    modules, dernier_par_formation = [], {}
    for i in range(n):
        formation_id = formations[i % len(formations)]
        necessite_lieu = rng.random() < parametres.demande_lieux_partages
        precedent = dernier_par_formation.get(formation_id)
        prerequis_id = (
            precedent.id if precedent and rng.random() < PROBABILITE_PREREQUIS else None
        )
        module = Module(
            id=f"M{i}",
            formation_id=formation_id,
            volume_prescrit=float(rng.randint(VOLUME_PRESCRIT_MIN, VOLUME_PRESCRIT_MAX)),
            necessite_lieu_partage=necessite_lieu,
            type_lieu_partage=_type_lieu_pour(rng, lieux_partages) if necessite_lieu else None,
            prerequis_id=prerequis_id,
            volume_deja_programme=0.0,
        )
        modules.append(module)
        dernier_par_formation[formation_id] = module
    return modules


def _instructeurs_qualifies(rng, modules, instructeurs_ids, parametres):
    """RG-35 — une fraction `fraction_modules_rares` des modules n'a qu'UN
    SEUL instructeur qualifié ; les autres en ont `densite_qualification`."""
    par_module = {}
    for module in modules:
        rare = rng.random() < parametres.fraction_modules_rares
        taille = 1 if rare else min(parametres.densite_qualification, len(instructeurs_ids))
        par_module[module.id] = set(rng.sample(instructeurs_ids, taille))
    return par_module


def _instructeurs(rng, modules, n, parametres):
    ids = [f"I{i}" for i in range(n)]
    qualifies_par_module = _instructeurs_qualifies(rng, modules, ids, parametres)
    modules_par_instructeur = {i: [] for i in ids}
    for module_id, qualifies in qualifies_par_module.items():
        for instructeur_id in qualifies:
            modules_par_instructeur[instructeur_id].append(module_id)
    return [Instructeur(id=i, modules_qualifies=modules_par_instructeur[i]) for i in ids]


def _progression_prerequis(rng, brigades, modules):
    """RG-39(b) — pour chaque module servant de prérequis, chaque brigade a
    une probabilité `PROBABILITE_PREREQUIS_ACQUIS` de l'avoir déjà acquis en
    entier avant cette semaine (sans quoi son module dépendant resterait
    injouable pour TOUTE instance, ce qui ne renseignerait rien)."""
    par_id = {m.id: m for m in modules}
    prerequis_ids = {m.prerequis_id for m in modules if m.prerequis_id}
    resultat = []
    for brigade in brigades:
        acquis = {}
        for prerequis_id in prerequis_ids:
            module = par_id[prerequis_id]
            if module.formation_id != brigade.formation_id:
                continue
            if rng.random() < PROBABILITE_PREREQUIS_ACQUIS:
                acquis[prerequis_id] = module.volume_prescrit
        resultat.append(dataclasses.replace(brigade, volume_deja_programme=acquis))
    return resultat


def generer(parametres: ParametresInstance) -> Instance:
    rng = random.Random(parametres.graine)
    taille = TAILLES[parametres.taille]

    creneaux = _creneaux(taille["nb_creneaux"])
    lieux_partages = _lieux_partages(rng, taille["nb_lieux_partages"])
    formations = _formations(taille["nb_sessions"])
    brigades = _brigades(rng, formations, taille["nb_brigades"])
    modules = _modules(rng, formations, taille["nb_modules"], lieux_partages, parametres)
    instructeurs = _instructeurs(rng, modules, taille["nb_instructeurs"], parametres)
    brigades = _progression_prerequis(rng, brigades, modules)

    return Instance(
        meta=dataclasses.asdict(parametres),
        creneaux=creneaux,
        lieux_partages=lieux_partages,
        modules=modules,
        brigades=brigades,
        instructeurs=instructeurs,
    )
