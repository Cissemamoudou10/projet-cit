from ortools.sat.python import cp_model
from solveur.generateur import ParametresInstance, generer
from solveur.modele import (
    DUREE_CRENEAU_HEURES,
    REGIME_EQUILIBRAGE,
    REGIME_REMPLISSAGE,
    REGIME_SATISFACTION,
    construire,
    nombre_de_variables,
    resoudre,
)

BORNE_TEMPS_TEST = 30


def _instance_controle(graine=1, **overrides):
    parametres = ParametresInstance(
        taille="CONTROLE",
        demande_lieux_partages=0.15,
        densite_qualification=4,
        fraction_modules_rares=0.05,
        graine=graine,
        **overrides,
    )
    return generer(parametres)


def test_taille_controle_est_realisable_en_satisfaction():
    modele, variables = construire(_instance_controle())
    solveur, statut = resoudre(modele, variables, REGIME_SATISFACTION, BORNE_TEMPS_TEST)
    assert statut in (cp_model.OPTIMAL, cp_model.FEASIBLE)


def test_aucun_instructeur_affecte_deux_fois_sur_le_meme_creneau():
    """RG-34 — vérifié sur la solution retournée, pas seulement supposé de
    la contrainte : une contrainte mal indexée resterait invisible sinon."""
    instance = _instance_controle()
    modele, variables = construire(instance)
    solveur, statut = resoudre(modele, variables, REGIME_REMPLISSAGE, BORNE_TEMPS_TEST)
    assert statut in (cp_model.OPTIMAL, cp_model.FEASIBLE)

    occupations = {}
    for (brigade_id, creneau_id, module_id, instructeur_id), var in variables.z.items():
        if solveur.Value(var):
            cle = (instructeur_id, creneau_id)
            occupations.setdefault(cle, []).append((brigade_id, module_id))
    doublons = {cle: v for cle, v in occupations.items() if len(v) > 1}
    assert not doublons, f"Instructeur affecté deux fois au même créneau : {doublons}"


def test_aucun_module_ne_depasse_son_volume_prescrit():
    """RG-39(a) — plafond global vérifié sur la solution."""
    instance = _instance_controle()
    modele, variables = construire(instance)
    solveur, statut = resoudre(modele, variables, REGIME_REMPLISSAGE, BORNE_TEMPS_TEST)
    assert statut in (cp_model.OPTIMAL, cp_model.FEASIBLE)

    heures_par_module = {}
    for (_b, _c, module_id), var in variables.x.items():
        if solveur.Value(var):
            heures_par_module[module_id] = (
                heures_par_module.get(module_id, 0) + DUREE_CRENEAU_HEURES
            )
    modules_par_id = {m.id: m for m in instance.modules}
    for module_id, heures in heures_par_module.items():
        module = modules_par_id[module_id]
        assert heures + module.volume_deja_programme <= module.volume_prescrit + 1e-9


def test_remplissage_n_est_jamais_pire_que_satisfaction():
    """REMPLISSAGE maximise explicitement le nombre de cases pourvues —
    doit au moins égaler ce qu'une solution SATISFACTION quelconque atteint."""
    instance = _instance_controle(graine=7)

    modele_sat, variables_sat = construire(instance)
    _, statut_sat = resoudre(modele_sat, variables_sat, REGIME_SATISFACTION, BORNE_TEMPS_TEST)
    assert statut_sat in (cp_model.OPTIMAL, cp_model.FEASIBLE)

    modele_rem, variables_rem = construire(instance)
    solveur_rem, statut_rem = resoudre(
        modele_rem, variables_rem, REGIME_REMPLISSAGE, BORNE_TEMPS_TEST
    )
    assert statut_rem == cp_model.OPTIMAL
    assert solveur_rem.ObjectiveValue() >= 1


def test_equilibrage_ne_degrade_pas_le_remplissage_optimal():
    """§ 5 : « remplissage, PUIS » — l'écart de charge ne doit jamais coûter
    une case par rapport à l'optimum de REMPLISSAGE seul."""
    instance = _instance_controle(graine=11)

    modele_rem, variables_rem = construire(instance)
    solveur_rem, statut_rem = resoudre(
        modele_rem, variables_rem, REGIME_REMPLISSAGE, BORNE_TEMPS_TEST
    )
    assert statut_rem == cp_model.OPTIMAL
    remplissage_optimal = round(solveur_rem.ObjectiveValue())

    modele_eq, variables_eq = construire(instance)
    solveur_eq, statut_eq = resoudre(modele_eq, variables_eq, REGIME_EQUILIBRAGE, BORNE_TEMPS_TEST)
    assert statut_eq == cp_model.OPTIMAL
    remplissage_obtenu = sum(solveur_eq.Value(v) for v in variables_eq.x.values())
    assert remplissage_obtenu == remplissage_optimal


def test_nombre_de_variables_reste_dans_l_ordre_de_grandeur_attendu():
    """PROTOCOLE.md § 5 : 10 000 à 50 000 variables booléennes attendues à
    la taille RÉELLE — vérifié ici sur CONTRÔLE, juste pour que la fonction
    de comptage elle-même soit exercée avant de s'y fier à l'échelle réelle."""
    _, variables = construire(_instance_controle())
    assert nombre_de_variables(variables) > 0


def _instance_controle_demande(demande, graine=1):
    return generer(
        ParametresInstance(
            taille="CONTROLE",
            demande_lieux_partages=demande,
            densite_qualification=4,
            fraction_modules_rares=0.05,
            graine=graine,
        )
    )


def test_aucune_brigade_ne_depasse_son_programme_cible():
    instance = _instance_controle_demande(0.25)
    modele, variables = construire(instance)
    solveur, statut = resoudre(modele, variables, REGIME_REMPLISSAGE, BORNE_TEMPS_TEST)
    assert statut in (cp_model.OPTIMAL, cp_model.FEASIBLE)

    places = {}
    for (brigade_id, _c, module_id), var in variables.x.items():
        if solveur.Value(var):
            places[brigade_id, module_id] = places.get((brigade_id, module_id), 0) + 1
    cibles = {b.id: b.programme_cible for b in instance.brigades}
    for (brigade_id, module_id), n in places.items():
        assert n <= cibles[brigade_id][module_id]


def test_une_demande_superieure_a_la_capacite_borne_le_remplissage():
    """Régression de la revue du 2026-09-18 : la première matrice affichait
    100 % de remplissage à 25 % de demande parce que le solveur évitait les
    modules à lieu. Ici 50 % de demande : 10 séances à lieu par brigade, 30 au
    total, pour 20 créneaux-lieu (1 espace × 20) — au plus 20 séances à lieu,
    donc au plus 50 cases sur 60. Le remplissage optimal DOIT être borné."""
    instance = _instance_controle_demande(0.5)
    assert instance.meta["seances_a_pourvoir_avec_lieu"] == 30
    capacite = len(instance.lieux_partages) * len(instance.creneaux)
    assert capacite == 20

    modele, variables = construire(instance)
    solveur, statut = resoudre(modele, variables, REGIME_REMPLISSAGE, BORNE_TEMPS_TEST)

    assert statut == cp_model.OPTIMAL
    remplies = sum(solveur.Value(v) for v in variables.x.values())
    avec_lieu = sum(solveur.Value(v) for v in variables.u.values())
    assert avec_lieu <= capacite
    assert remplies <= 60 - (30 - capacite)
    assert remplies < 60


def test_l_ecart_de_charge_ne_compte_que_les_instructeurs_mobilisables():
    from solveur.preparation import modules_programmables

    instance = _instance_controle_demande(0.15)
    _, variables = construire(instance)
    assert set(variables.charge) == set(modules_programmables(instance).mobilisables)
