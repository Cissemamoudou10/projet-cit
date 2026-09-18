from solveur.generateur import ParametresInstance, generer
from solveur.mesures import mesurer_heuristique, mesurer_solveur
from solveur.modele import DUREE_CRENEAU_HEURES, REGIME_EQUILIBRAGE, REGIME_REMPLISSAGE

BORNE_TEMPS_TEST = 30


def _instance_controle():
    return generer(
        ParametresInstance(
            taille="CONTROLE",
            demande_lieux_partages=0.15,
            densite_qualification=4,
            fraction_modules_rares=0.05,
            graine=1,
        )
    )


def test_mesurer_solveur_rapporte_un_temps_de_premiere_solution():
    mesure = mesurer_solveur(_instance_controle(), REGIME_REMPLISSAGE, BORNE_TEMPS_TEST)
    assert mesure.statut in ("OPTIMAL", "FEASIBLE")
    assert mesure.temps_premiere_solution is not None
    assert mesure.temps_premiere_solution <= mesure.temps_final
    assert 0 < mesure.taux_remplissage <= 1


def test_mesurer_solveur_equilibrage_rapporte_un_ecart_de_charge():
    mesure = mesurer_solveur(_instance_controle(), REGIME_EQUILIBRAGE, BORNE_TEMPS_TEST)
    assert mesure.statut in ("OPTIMAL", "FEASIBLE")
    assert mesure.ecart_charge is not None


def test_mesurer_heuristique_rapporte_un_temps_et_un_remplissage():
    mesure = mesurer_heuristique(_instance_controle(), DUREE_CRENEAU_HEURES)
    assert mesure.temps_total > 0
    assert 0 < mesure.taux_remplissage <= 1
