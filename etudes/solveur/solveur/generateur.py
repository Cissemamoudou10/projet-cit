"""Générateur d'instances — Prompt 32 § 3/§ 4/§ 6. Paramétré par la taille
(§ 3) et les deux axes de sensibilité (§ 4), graine aléatoire fixée et
consignée dans `meta`.

Simplifications déclarées (PROTOCOLE.md § 5) : pas de regroupement de
brigades, une séance par créneau, prérequis pré-filtrés, aucune
indisponibilité (RG-36) ni période bloquante (RG-38), salle attitrée
toujours suffisante (RG-37, sous-cas hors modèle).

DEMANDE EN LIEUX PARTAGÉS (§ 4) — corrigée le 2026-09-18 : le paramètre
s'applique aux SÉANCES À POURVOIR (le programme cible de chaque brigade),
exactement `round(demande × nb_créneaux)` par brigade, et non plus aux
modules du catalogue. Appliqué au catalogue, il laissait le solveur choisir
librement les modules et éviter ceux qui exigent un lieu : la demande
effective tombait à 3-11 % pour 10-25 % annoncés. La capacité nominale des
lieux partagés vaut désormais exactement espaces × créneaux (un lieu
SIMULTANÉ ne reçoit qu'une brigade non regroupée), comme au § 2.
"""

import collections
import dataclasses
import random

from solveur.instance import (
    DUREE_CRENEAU_HEURES,
    JOURS_OUVRES,
    Brigade,
    Creneau,
    Instance,
    Instructeur,
    LieuPartage,
    Module,
)
from solveur.preparation import modules_eligibles

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
    return [
        Creneau(id=i, jour=JOURS_OUVRES[i % len(JOURS_OUVRES)], ordre=i // len(JOURS_OUVRES) + 1)
        for i in range(n)
    ]


def _capacite_lieu(rng, mode):
    """Un lieu SIMULTANÉ reçoit UNE brigade non regroupée, jamais deux :
    capacité entre l'effectif maximal et le double de l'effectif minimal
    (exclu). Aligne la capacité sur le décompte du § 2 (espaces × créneaux) ;
    le regroupement, qui seul justifierait d'accueillir deux brigades, n'est
    pas modélisé (PROTOCOLE.md § 5)."""
    if mode == "SEQUENTIEL":
        return 1
    return rng.randint(EFFECTIF_MAX, 2 * EFFECTIF_MIN - 1)


def _lieux_partages(rng, n):
    lieux = []
    for i in range(n):
        mode = "SIMULTANE" if i % 2 == 0 else "SEQUENTIEL"
        lieux.append(
            LieuPartage(
                id=f"LP{i}",
                type=TYPES_LIEU_PARTAGE[i % len(TYPES_LIEU_PARTAGE)],
                capacite=_capacite_lieu(rng, mode),
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
    """Pondéré par le nombre d'espaces de chaque type : la demande se répartit
    comme la capacité, sans quoi le seul terrain (un espace) saturerait dès
    15 % de demande globale, bien avant la capacité agrégée du § 2."""
    comptes = collections.Counter(lieu.type for lieu in lieux_partages)
    types = sorted(comptes)
    return rng.choices(types, weights=[comptes[t] for t in types])[0]


def _necessite_lieu(rng, rang, parametres):
    """Garanties structurelles, par formation : le module de rang 0 n'exige
    jamais de lieu (une matière toujours programmable sans lieu) ; celui de
    rang 1 en exige toujours un dès que la demande est non nulle (de quoi
    porter le programme cible en lieux). Au-delà, tirage au taux demandé —
    sans conséquence sur la demande, qui se règle sur les séances à pourvoir."""
    if rang == 0:
        return False
    if rang == 1:
        return parametres.demande_lieux_partages > 0
    return rng.random() < parametres.demande_lieux_partages


def _modules(rng, formations, n, lieux_partages, parametres):
    modules, dernier_par_formation, rang_par_formation = [], {}, {}
    for i in range(n):
        formation_id = formations[i % len(formations)]
        rang = rang_par_formation.get(formation_id, 0)
        rang_par_formation[formation_id] = rang + 1
        necessite_lieu = _necessite_lieu(rng, rang, parametres)
        precedent = dernier_par_formation.get(formation_id)
        # Un module à lieu n'a jamais de prérequis : toujours éligible, il
        # peut porter exactement la part de lieux demandée.
        prerequis_id = (
            precedent.id
            if precedent and not necessite_lieu and rng.random() < PROBABILITE_PREREQUIS
            else None
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
        par_module[module.id] = sorted(rng.sample(instructeurs_ids, taille))
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
    # `sorted` : un `set` de chaînes s'itère dans un ordre qui dépend de la graine de
    # hachage du PROCESSUS ; itéré avec un tirage aléatoire par élément, il rendait
    # l'instance différente d'un processus à l'autre (défaut constaté le 2026-09-19).
    prerequis_ids = sorted({m.prerequis_id for m in modules if m.prerequis_id})
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


def _programme_cible(rng, eligibles, modules_par_id, parametres, nb_creneaux):
    """`nb_creneaux` séances à pourvoir, dont exactement
    `round(demande × nb_creneaux)` dans un module à lieu partagé : la
    demande du § 4 s'applique ICI, aux séances à pourvoir."""
    avec_lieu = [m for m in eligibles if modules_par_id[m].necessite_lieu_partage]
    sans_lieu = [m for m in eligibles if not modules_par_id[m].necessite_lieu_partage]
    nb_avec_lieu = round(parametres.demande_lieux_partages * nb_creneaux) if avec_lieu else 0
    tirages = [rng.choice(avec_lieu) for _ in range(nb_avec_lieu)]
    tirages += [rng.choice(sans_lieu) for _ in range(nb_creneaux - nb_avec_lieu)]
    return dict(collections.Counter(tirages))


def _volumes_couvrant_les_programmes(modules, brigades):
    """Le plafond de volume (RG-39 a) ne doit pas être ce qui limite le
    remplissage : le volume prescrit d'un module couvre au moins la somme des
    séances que les programmes cibles y placent. Le plafond reste dans le
    modèle, sans jamais mordre — l'axe étudié est ailleurs (§ 4)."""
    total = collections.Counter()
    for brigade in brigades:
        total.update(brigade.programme_cible)
    return [
        dataclasses.replace(
            m, volume_prescrit=max(m.volume_prescrit, total[m.id] * DUREE_CRENEAU_HEURES)
        )
        for m in modules
    ]


def _progression_recalee(brigades, modules):
    """Relève la progression acquise sur les prérequis au nouveau volume
    prescrit (`_volumes_couvrant_les_programmes` peut l'avoir augmenté) : un
    prérequis acquis reste acquis."""
    par_id = {m.id: m for m in modules}
    return [
        dataclasses.replace(
            b,
            volume_deja_programme={m: par_id[m].volume_prescrit for m in b.volume_deja_programme},
        )
        for b in brigades
    ]


def _demande_realisee(brigades, modules):
    par_id = {m.id: m for m in modules}
    total = sum(sum(b.programme_cible.values()) for b in brigades)
    avec_lieu = sum(
        n
        for b in brigades
        for m, n in b.programme_cible.items()
        if par_id[m].necessite_lieu_partage
    )
    return {
        "seances_a_pourvoir": total,
        "seances_a_pourvoir_avec_lieu": avec_lieu,
        "demande_lieux_realisee": avec_lieu / total if total else 0.0,
    }


def _completer_programmes_cibles(
    rng, creneaux, lieux_partages, modules, brigades, instructeurs, parametres
):
    """Deuxième passe : le programme cible de chaque brigade (§ 4, demande en
    lieux EXOGÈNE) ne peut se tirer qu'une fois les modules ÉLIGIBLES connus —
    d'où une `Instance` provisoire, seulement pour ce calcul. Relève ensuite le
    volume prescrit pour qu'il couvre les programmes cibles (RG-39 a ne doit
    jamais être ce qui limite le remplissage : l'axe étudié est ailleurs) et
    recale la progression acquise en conséquence."""
    provisoire = Instance(
        meta={},
        creneaux=creneaux,
        lieux_partages=lieux_partages,
        modules=modules,
        brigades=brigades,
        instructeurs=instructeurs,
    )
    eligibles = modules_eligibles(provisoire)
    modules_par_id = {m.id: m for m in modules}
    brigades = [
        dataclasses.replace(
            b,
            programme_cible=_programme_cible(
                rng, eligibles[b.id], modules_par_id, parametres, len(creneaux)
            ),
        )
        for b in brigades
    ]
    modules = _volumes_couvrant_les_programmes(modules, brigades)
    brigades = _progression_recalee(brigades, modules)
    return modules, brigades


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
    modules, brigades = _completer_programmes_cibles(
        rng, creneaux, lieux_partages, modules, brigades, instructeurs, parametres
    )

    return Instance(
        meta={**dataclasses.asdict(parametres), **_demande_realisee(brigades, modules)},
        creneaux=creneaux,
        lieux_partages=lieux_partages,
        modules=modules,
        brigades=brigades,
        instructeurs=instructeurs,
    )
