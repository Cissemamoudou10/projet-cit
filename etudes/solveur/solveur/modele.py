"""Modèle CP-SAT — Prompt 32 § 5. Décomposition booléenne : une variable par
(brigade, créneau, module), liée à une variable (brigade, créneau, module,
instructeur) restreinte aux qualifiés (RG-35), et une variable (brigade,
créneau, module, lieu) restreinte aux séances exigeant un lieu partagé
(RG-37).

« Une séance par créneau » (simplification déclarée, PROTOCOLE.md § 5) : les
créneaux ne se chevauchent jamais, ce qui réduit RG-34/RG-37 d'une
contrainte d'intervalle (`AddNoOverlap`/`AddCumulative`) à une simple
capacité PAR CRÉNEAU DISCRET — un instructeur ou un lieu séquentiel une fois
par créneau, un lieu simultané borné en somme d'effectifs par créneau.
"""

import collections
import dataclasses

from ortools.sat.python import cp_model

from solveur.instance import DUREE_CRENEAU_HEURES
from solveur.preparation import modules_programmables

REGIME_SATISFACTION = "SATISFACTION"
REGIME_REMPLISSAGE = "REMPLISSAGE"
REGIME_EQUILIBRAGE = "EQUILIBRAGE"


@dataclasses.dataclass
class VariablesModele:
    x: dict  # (brigade_id, creneau_id, module_id) -> BoolVar
    z: dict  # (brigade_id, creneau_id, module_id, instructeur_id) -> BoolVar
    u: dict  # (brigade_id, creneau_id, module_id, lieu_id) -> BoolVar
    charge: dict  # instructeur_id -> IntVar
    borne_charge: int  # = nombre de créneaux — borne haute connue de `charge`


def _lieux_du_type(instance, type_lieu):
    return [lieu for lieu in instance.lieux_partages if lieu.type == type_lieu]


def _creer_x(modele, instance, preparation):
    x = {}
    for brigade in instance.brigades:
        for module_id in preparation.modules_par_brigade[brigade.id]:
            for creneau in instance.creneaux:
                x[brigade.id, creneau.id, module_id] = modele.NewBoolVar(
                    f"x_{brigade.id}_{creneau.id}_{module_id}"
                )
    return x


def _au_plus_un(modele, variables):
    """`cp_model.LinearExpr.Sum` plutôt que le `sum()` natif de Python
    partout dans ce module (voir `_configurer_objectif`) : même à quelques
    dizaines de termes, l'un des appels a produit une variable de domaine
    corrompu (`.Proto()` illisible) sous cette version d'ortools — signalé
    dans PROTOCOLE.md. Coût négligeable, élimine le risque partout."""
    if variables:
        modele.Add(cp_model.LinearExpr.Sum(variables) <= 1)


def _contraindre_une_seance_par_creneau(modele, instance, x):
    groupes = collections.defaultdict(list)
    for (brigade_id, creneau_id, _module_id), var in x.items():
        groupes[brigade_id, creneau_id].append(var)
    for variables in groupes.values():
        _au_plus_un(modele, variables)


def _contraindre_programme_cible(modele, instance, x):
    """PROGRAMME CIBLE — au plus `programme_cible[module]` créneaux de ce
    module pour cette brigade cette semaine : c'est ce qui rend la demande
    en lieux partagés EXOGÈNE (revue du 2026-09-18) au lieu de laisser le
    solveur choisir les modules qui l'arrangent."""
    for brigade in instance.brigades:
        for module_id, quota in brigade.programme_cible.items():
            variables = [
                x[brigade.id, creneau.id, module_id]
                for creneau in instance.creneaux
                if (brigade.id, creneau.id, module_id) in x
            ]
            if variables:
                modele.Add(cp_model.LinearExpr.Sum(variables) <= quota)


def _creer_z(modele, instance, preparation, x):
    z = {}
    for (brigade_id, creneau_id, module_id), var_x in x.items():
        qualifies = preparation.qualifies_par_module.get(module_id, [])
        variables_z = []
        for instructeur_id in qualifies:
            var_z = modele.NewBoolVar(f"z_{brigade_id}_{creneau_id}_{module_id}_{instructeur_id}")
            z[brigade_id, creneau_id, module_id, instructeur_id] = var_z
            variables_z.append(var_z)
        modele.Add(cp_model.LinearExpr.Sum(variables_z) == var_x)
    return z


def _contraindre_unicite_instructeur(modele, instance, z):
    """RG-34 — un instructeur, au plus une brigade, par créneau."""
    groupes = collections.defaultdict(list)
    for (_b, creneau_id, _m, instructeur_id), var in z.items():
        groupes[instructeur_id, creneau_id].append(var)
    for variables in groupes.values():
        _au_plus_un(modele, variables)


def _creer_u(modele, instance, x, modules_par_id):
    u = {}
    for (brigade_id, creneau_id, module_id), var_x in x.items():
        module = modules_par_id[module_id]
        if not module.necessite_lieu_partage:
            continue
        lieux = _lieux_du_type(instance, module.type_lieu_partage)
        variables_u = []
        for lieu in lieux:
            var_u = modele.NewBoolVar(f"u_{brigade_id}_{creneau_id}_{module_id}_{lieu.id}")
            u[brigade_id, creneau_id, module_id, lieu.id] = var_u
            variables_u.append(var_u)
        modele.Add(cp_model.LinearExpr.Sum(variables_u) == var_x)
    return u


def _contraindre_capacite_lieu(modele, instance, u):
    """RG-37 — lieu partagé : SÉQUENTIEL (au plus une brigade par créneau,
    comme RG-34) ou SIMULTANÉ (somme des effectifs bornée par la capacité)."""
    effectif = {b.id: b.effectif for b in instance.brigades}
    modes = {lieu.id: lieu for lieu in instance.lieux_partages}
    groupes = collections.defaultdict(list)
    for (brigade_id, creneau_id, _m, lieu_id), var in u.items():
        groupes[lieu_id, creneau_id].append((brigade_id, var))
    for (lieu_id, _creneau_id), entrees in groupes.items():
        lieu = modes[lieu_id]
        if lieu.mode == "SEQUENTIEL":
            _au_plus_un(modele, [var for _b, var in entrees])
        else:
            termes = [var for _b, var in entrees]
            coefficients = [effectif[b] for b, _var in entrees]
            modele.Add(cp_model.LinearExpr.WeightedSum(termes, coefficients) <= lieu.capacite)


def _contraindre_volume_plafond(modele, instance, x):
    """RG-39(a) — plafond GLOBAL par module, toutes brigades et créneaux
    confondus (portée confirmée dans `regles_volume.py` de l'application)."""
    for module in instance.modules:
        variables = [var for (_b, _c, m), var in x.items() if m == module.id]
        if not variables:
            continue
        marge_creneaux = int(
            (module.volume_prescrit - module.volume_deja_programme) // DUREE_CRENEAU_HEURES
        )
        modele.Add(cp_model.LinearExpr.Sum(variables) <= max(marge_creneaux, 0))


def _creer_charge(modele, instance, z):
    """Une variable de charge par instructeur MOBILISABLE seulement — ayant
    au moins une variable `z` : un instructeur qualifié sur rien de ce qu'on
    a à pourvoir reste à zéro quoi qu'on fasse, et l'inclure faisait de
    l'« écart de charge » la charge maximale (revue du 2026-09-18)."""
    par_instructeur = collections.defaultdict(list)
    for (_b, _c, _m, instructeur_id), var in z.items():
        par_instructeur[instructeur_id].append(var)
    charge = {}
    for instructeur in instance.instructeurs:
        variables = par_instructeur.get(instructeur.id)
        if not variables:
            continue
        var_charge = modele.NewIntVar(0, len(instance.creneaux), f"charge_{instructeur.id}")
        modele.Add(var_charge == cp_model.LinearExpr.Sum(variables))
        charge[instructeur.id] = var_charge
    return charge


def construire(instance):
    """Construit le modèle et retourne `(modele, variables)` — ne résout
    rien : `resoudre` (ci-dessous) choisit le régime et l'objectif."""
    modele = cp_model.CpModel()
    preparation = modules_programmables(instance)
    modules_par_id = {m.id: m for m in instance.modules}

    x = _creer_x(modele, instance, preparation)
    _contraindre_une_seance_par_creneau(modele, instance, x)
    _contraindre_programme_cible(modele, instance, x)
    z = _creer_z(modele, instance, preparation, x)
    _contraindre_unicite_instructeur(modele, instance, z)
    u = _creer_u(modele, instance, x, modules_par_id)
    _contraindre_capacite_lieu(modele, instance, u)
    _contraindre_volume_plafond(modele, instance, x)
    charge = _creer_charge(modele, instance, z)

    return modele, VariablesModele(
        x=x, z=z, u=u, charge=charge, borne_charge=len(instance.creneaux)
    )


def nombre_de_variables(variables: VariablesModele) -> int:
    return len(variables.x) + len(variables.z) + len(variables.u)


def _configurer_objectif(modele, variables, regime):
    if regime == REGIME_SATISFACTION:
        return
    # `cp_model.LinearExpr.Sum` plutôt que le `sum()` natif de Python : à la
    # taille RÉELLE, `variables.x` porte plusieurs milliers de termes,
    # l'arbre binaire imbriqué que construit `sum()` terme à terme est un
    # piège documenté de l'API Python d'ortools à cette échelle.
    remplissage = cp_model.LinearExpr.Sum(list(variables.x.values()))
    if regime == REGIME_REMPLISSAGE:
        modele.Maximize(remplissage)
        return
    if regime == REGIME_EQUILIBRAGE:
        ecart = _ecart_charge(modele, variables)
        objectif = cp_model.LinearExpr.WeightedSum(
            [remplissage, ecart], [_poids_remplissage(variables), -1]
        )
        modele.Maximize(objectif)
        return
    raise ValueError(f"Régime inconnu : {regime}")


def _poids_remplissage(variables):
    """Assez grand pour qu'aucune combinaison de charges ne compense une
    seule case en moins — l'équilibrage n'arbitre qu'ENTRE solutions à
    remplissage égal (§ 5 : « remplissage, PUIS » minimisation de l'écart,
    jamais un compromis entre les deux)."""
    return len(variables.x) + 1


def _ecart_charge(modele, variables):
    """`maximum`/`minimum` ne sont pas égalés aux vrais max/min par
    `AddMaxEquality`/`AddMinEquality` (crash natif reproductible avec cette
    combinaison ortools/Python 3.14, sous Windows ET sous Linux — signalé
    séparément, PROTOCOLE.md) : seulement bornés (`>=`/`<=` chacune des
    charges), ce qui suffit ICI puisque l'objectif MINIMISE leur écart —
    à l'optimum, le solveur les serre exactement sur le vrai max et le vrai
    min, sans qu'aucune contrainte d'égalité explicite soit nécessaire.

    `borne` vient de `variables.borne_charge` (connue dès `_creer_charge`),
    JAMAIS de `IntVar.Proto()` relu en cours de construction : ce second
    appel a été la cause RÉELLE du crash — corruption mémoire reproductible
    de variables déjà créées (`charge_*`) dès qu'on relit leur `.Proto()`
    puis qu'on ajoute encore des variables au modèle. Signalé séparément,
    PROTOCOLE.md."""
    charges = list(variables.charge.values())
    borne = variables.borne_charge
    maximum = modele.NewIntVar(0, borne, "charge_maximum")
    minimum = modele.NewIntVar(0, borne, "charge_minimum")
    for var_charge in charges:
        modele.Add(maximum >= var_charge)
        modele.Add(minimum <= var_charge)
    ecart = modele.NewIntVar(0, borne, "ecart_charge")
    modele.Add(ecart == maximum - minimum)
    return ecart


def configurer_objectif(modele, variables, regime):
    """Public — réutilisé par `mesures.py` (§ 8) pour appeler `Solve` avec
    un rappel de première solution, que `resoudre` n'expose pas."""
    _configurer_objectif(modele, variables, regime)


def resoudre(modele, variables, regime, borne_temps_secondes):
    configurer_objectif(modele, variables, regime)
    solveur = cp_model.CpSolver()
    solveur.parameters.max_time_in_seconds = borne_temps_secondes
    statut = solveur.Solve(modele)
    return solveur, statut
