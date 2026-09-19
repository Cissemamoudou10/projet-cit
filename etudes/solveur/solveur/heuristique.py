"""Réimplantation courte de la stratégie gloutonne — Prompt 32 § 6. Reprend
l'ESPRIT de la règle de priorité d'`app/planification/generation/tri.py`
(cinq lignes, Prompt 31 § 15 — citation partielle, coupes marquées « [...] »
pour les critères non repris dans une instance synthétique) :

    On place d'abord ce qui est le plus difficile à placer. Une matière que
    peu d'instructeurs savent enseigner, ou qui exige une salle rare, passe
    avant une matière que n'importe qui peut donner n'importe où. Une
    matière en retard sur son volume [...] passe avant une matière
    confortable. Entre deux instructeurs également possibles, on retient
    celui qui a le moins de séances cette semaine [...]. À égalité stricte,
    l'identifiant tranche.

LIMITE DÉCLARÉE (§ 6) : cette réimplantation peut diverger de celle de
l'application — pas de `session.date_fin` dans une instance synthétique
(l'urgence se mesure ici au volume restant seul, pas rapporté au temps
restant de la session) ; aucune notion d'indisponibilité (RG-36 non
modélisée, PROTOCOLE.md § 5). La comparaison porte sur les APPROCHES, pas
sur les implantations.
"""

import dataclasses

from solveur.instance import JOURS_OUVRES
from solveur.preparation import modules_programmables

SENTINELLE_AUCUN_LIEU = 10**6
SENTINELLE_BRIGADE_SANS_MODULE = (10**6, 10**6, 10**6, "")


@dataclasses.dataclass(frozen=True)
class ResultatHeuristique:
    placements: list  # (brigade_id, creneau_id, module_id, instructeur_id, lieu_id|None)
    cases_ouvertes: int


@dataclasses.dataclass
class EtatHeuristique:
    volume_restant: dict  # module_id -> heures restantes
    charge_instructeur: dict  # instructeur_id -> heures cette semaine
    instructeur_occupe: set  # (instructeur_id, creneau_id)
    lieu_occupe_sequentiel: set  # (lieu_id, creneau_id)
    lieu_charge_simultane: dict  # (lieu_id, creneau_id) -> effectif déjà admis
    quota_restant: dict  # (brigade_id, module_id) -> créneaux encore à pourvoir


def _etat_initial(instance):
    return EtatHeuristique(
        volume_restant={
            m.id: m.volume_prescrit - m.volume_deja_programme for m in instance.modules
        },
        charge_instructeur={i.id: 0.0 for i in instance.instructeurs},
        instructeur_occupe=set(),
        lieu_occupe_sequentiel=set(),
        lieu_charge_simultane={},
        quota_restant={
            (b.id, module_id): quota
            for b in instance.brigades
            for module_id, quota in b.programme_cible.items()
        },
    )


def _rarete_lieu(module, lieux_par_type):
    if not module.necessite_lieu_partage:
        return SENTINELLE_AUCUN_LIEU
    return len(lieux_par_type.get(module.type_lieu_partage, [])) or SENTINELLE_AUCUN_LIEU


def _instructeurs_disponibles(module_id, creneau_id, preparation, etat):
    return [
        i
        for i in preparation.qualifies_par_module.get(module_id, [])
        if (i, creneau_id) not in etat.instructeur_occupe
    ]


def _poids_module(module, creneau_id, preparation, etat, lieux_par_type):
    """EXPÉRIENCE du 2026-09-19 (revue, point 3) : la charge des instructeurs
    qualifiés pèse désormais dans le CHOIX DE LA MATIÈRE (`charge_min_
    disponible`, insérée après les deux critères de difficulté et avant
    l'urgence — elle ne les remplace jamais, elle ne fait que départager entre
    matières de difficulté comparable), et non plus seulement dans le
    départage à matière déjà choisie (`_tenter_placement`, inchangé). Version
    mesurée dans la matrice v3 : sans ce critère — voir `RESULTATS.md`,
    section « Expérience — charge dans le choix du contenu »."""
    disponibles = _instructeurs_disponibles(module.id, creneau_id, preparation, etat)
    charge_min_disponible = min((etat.charge_instructeur[i] for i in disponibles), default=0)
    return (
        len(disponibles),
        _rarete_lieu(module, lieux_par_type),
        charge_min_disponible,
        -etat.volume_restant[module.id],
        module.id,
    )


def _lieu_libre(lieu, creneau_id, brigade, etat):
    if lieu.mode == "SEQUENTIEL":
        return (lieu.id, creneau_id) not in etat.lieu_occupe_sequentiel
    charge = etat.lieu_charge_simultane.get((lieu.id, creneau_id), 0)
    return charge + brigade.effectif <= lieu.capacite


def _choisir_lieu(module, creneau_id, brigade, instance, etat):
    if not module.necessite_lieu_partage:
        return None
    lieux = [lieu for lieu in instance.lieux_partages if lieu.type == module.type_lieu_partage]
    return next((lieu for lieu in lieux if _lieu_libre(lieu, creneau_id, brigade, etat)), None)


def _occuper(etat, module, instructeur_id, creneau_id, lieu, brigade, duree_heures):
    etat.quota_restant[brigade.id, module.id] -= 1
    etat.instructeur_occupe.add((instructeur_id, creneau_id))
    etat.charge_instructeur[instructeur_id] += duree_heures
    etat.volume_restant[module.id] -= duree_heures
    if lieu is not None:
        if lieu.mode == "SEQUENTIEL":
            etat.lieu_occupe_sequentiel.add((lieu.id, creneau_id))
        else:
            cle = (lieu.id, creneau_id)
            etat.lieu_charge_simultane[cle] = (
                etat.lieu_charge_simultane.get(cle, 0) + brigade.effectif
            )


def _tenter_placement(brigade, creneau, instance, preparation, etat, lieux_par_type, duree_heures):
    modules = preparation.modules_par_brigade.get(brigade.id, [])
    candidats = sorted(
        (
            m
            for m in instance.modules
            if m.id in modules
            and etat.quota_restant.get((brigade.id, m.id), 0) > 0
            and etat.volume_restant[m.id] >= duree_heures
        ),
        key=lambda m: _poids_module(m, creneau.id, preparation, etat, lieux_par_type),
    )
    for module in candidats:
        disponibles = _instructeurs_disponibles(module.id, creneau.id, preparation, etat)
        if not disponibles:
            continue
        lieu = _choisir_lieu(module, creneau.id, brigade, instance, etat)
        if module.necessite_lieu_partage and lieu is None:
            continue
        instructeur_id = min(disponibles, key=lambda i: (etat.charge_instructeur[i], i))
        _occuper(etat, module, instructeur_id, creneau.id, lieu, brigade, duree_heures)
        return module.id, instructeur_id, lieu.id if lieu else None
    return None


def _cle_chronologique(creneau):
    return (JOURS_OUVRES.index(creneau.jour), creneau.ordre)


def _poids_brigade(brigade, premier_creneau, instance, preparation, etat, lieux_par_type):
    """Comme `StrategieGloutonne._poids_brigade` : la brigade dont la matière
    la plus difficile est la plus difficile passe en premier."""
    modules = [m for m in instance.modules if m.id in preparation.modules_par_brigade[brigade.id]]
    if not modules:
        return SENTINELLE_BRIGADE_SANS_MODULE
    return min(
        _poids_module(m, premier_creneau.id, preparation, etat, lieux_par_type) for m in modules
    )


def _cases_ordonnees(instance, preparation, etat, lieux_par_type):
    """Même ordre que `StrategieGloutonne._ordonner_cases` : d'abord le poids
    de la brigade, puis le temps, puis l'identifiant — et NON l'ordre de
    saisie des brigades (revue du 2026-09-18, équité de la comparaison)."""
    creneaux = sorted(instance.creneaux, key=_cle_chronologique)
    poids = {
        b.id: _poids_brigade(b, creneaux[0], instance, preparation, etat, lieux_par_type)
        for b in instance.brigades
    }
    cases = [(b, c) for b in instance.brigades for c in creneaux]
    return sorted(cases, key=lambda bc: (poids[bc[0].id], _cle_chronologique(bc[1]), bc[0].id))


def generer(instance, duree_creneau_heures):
    preparation = modules_programmables(instance)
    lieux_par_type = {}
    for lieu in instance.lieux_partages:
        lieux_par_type.setdefault(lieu.type, []).append(lieu)
    etat = _etat_initial(instance)

    placements = []
    for brigade, creneau in _cases_ordonnees(instance, preparation, etat, lieux_par_type):
        resultat = _tenter_placement(
            brigade, creneau, instance, preparation, etat, lieux_par_type, duree_creneau_heures
        )
        if resultat:
            module_id, instructeur_id, lieu_id = resultat
            placements.append((brigade.id, creneau.id, module_id, instructeur_id, lieu_id))

    cases_ouvertes = len(instance.brigades) * len(instance.creneaux)
    return ResultatHeuristique(placements=placements, cases_ouvertes=cases_ouvertes)
