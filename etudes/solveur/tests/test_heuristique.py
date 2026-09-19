from solveur.generateur import ParametresInstance, generer
from solveur.heuristique import generer as generer_placements
from solveur.modele import DUREE_CRENEAU_HEURES


def _instance_controle(graine=1):
    parametres = ParametresInstance(
        taille="CONTROLE",
        demande_lieux_partages=0.15,
        densite_qualification=4,
        fraction_modules_rares=0.05,
        graine=graine,
    )
    return generer(parametres)


def test_produit_au_moins_un_placement():
    resultat = generer_placements(_instance_controle(), DUREE_CRENEAU_HEURES)
    assert resultat.placements
    assert resultat.cases_ouvertes > 0


def test_aucun_instructeur_affecte_deux_fois_sur_le_meme_creneau():
    resultat = generer_placements(_instance_controle(graine=5), DUREE_CRENEAU_HEURES)
    occupations = {}
    for _brigade_id, creneau_id, _module_id, instructeur_id, _lieu_id in resultat.placements:
        cle = (instructeur_id, creneau_id)
        occupations[cle] = occupations.get(cle, 0) + 1
    doublons = {cle: n for cle, n in occupations.items() if n > 1}
    assert not doublons


def test_aucune_brigade_n_a_deux_seances_sur_le_meme_creneau():
    resultat = generer_placements(_instance_controle(graine=9), DUREE_CRENEAU_HEURES)
    occupations = {}
    for brigade_id, creneau_id, _module_id, _instructeur_id, _lieu_id in resultat.placements:
        cle = (brigade_id, creneau_id)
        occupations[cle] = occupations.get(cle, 0) + 1
    doublons = {cle: n for cle, n in occupations.items() if n > 1}
    assert not doublons


def test_aucun_module_ne_depasse_son_volume_prescrit():
    instance = _instance_controle(graine=13)
    resultat = generer_placements(instance, DUREE_CRENEAU_HEURES)
    heures_par_module = {}
    for _b, _c, module_id, _i, _l in resultat.placements:
        heures_par_module[module_id] = heures_par_module.get(module_id, 0) + DUREE_CRENEAU_HEURES
    modules_par_id = {m.id: m for m in instance.modules}
    for module_id, heures in heures_par_module.items():
        module = modules_par_id[module_id]
        assert heures + module.volume_deja_programme <= module.volume_prescrit + 1e-9


def test_determinisme_meme_graine():
    instance = _instance_controle(graine=21)
    a = generer_placements(instance, DUREE_CRENEAU_HEURES)
    b = generer_placements(instance, DUREE_CRENEAU_HEURES)
    assert a.placements == b.placements


def test_l_heuristique_respecte_le_programme_cible_et_la_capacite_des_lieux():
    instance = generer(
        ParametresInstance(
            taille="REELLE",
            demande_lieux_partages=0.25,
            densite_qualification=4,
            fraction_modules_rares=0.05,
            graine=0,
        )
    )
    resultat = generer_placements(instance, DUREE_CRENEAU_HEURES)
    places = {}
    for brigade_id, _c, module_id, _i, _l in resultat.placements:
        places[brigade_id, module_id] = places.get((brigade_id, module_id), 0) + 1
    cibles = {b.id: b.programme_cible for b in instance.brigades}
    for (brigade_id, module_id), n in places.items():
        assert n <= cibles[brigade_id][module_id]
    capacite = len(instance.lieux_partages) * len(instance.creneaux)
    assert sum(1 for p in resultat.placements if p[4] is not None) <= capacite
