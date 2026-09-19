"""Pilote — une combinaison (demande=0.15, densité=4, le « repère de
calcul » du § 4 du prompt), une instance, les trois régimes, borne réelle
(BNF-04, 300 s). Mesure le temps réel avant d'engager la matrice complète
(60 instances). Résultat ponctuel, imprimé, pas un livrable."""

import sys

sys.path.insert(0, ".")

from solveur.generateur import ParametresInstance, generer
from solveur.mesures import mesurer_heuristique, mesurer_solveur
from solveur.modele import (
    DUREE_CRENEAU_HEURES,
    REGIME_EQUILIBRAGE,
    REGIME_REMPLISSAGE,
    REGIME_SATISFACTION,
)

BORNE_TEMPS_SECONDES = 300  # BNF-04

instance = generer(
    ParametresInstance(
        taille="REELLE",
        demande_lieux_partages=0.15,
        densite_qualification=4,
        fraction_modules_rares=0.05,
        graine=0,
    )
)
print(
    f"Instance : {len(instance.brigades)} brigades, {len(instance.modules)} modules, "
    f"{len(instance.instructeurs)} instructeurs, {len(instance.creneaux)} créneaux"
)

for regime in (REGIME_SATISFACTION, REGIME_REMPLISSAGE, REGIME_EQUILIBRAGE):
    mesure = mesurer_solveur(instance, regime, BORNE_TEMPS_SECONDES)
    print(
        f"{regime:12s} statut={mesure.statut:12s} "
        f"1ere_sol={mesure.temps_premiere_solution} "
        f"temps_final={mesure.temps_final:.1f}s "
        f"remplissage={mesure.taux_remplissage:.1%} "
        f"ecart_optimalite={mesure.ecart_optimalite} "
        f"ecart_charge={mesure.ecart_charge} "
        f"memoire={mesure.memoire_max_ko} Ko"
    )

mesure_heuristique = mesurer_heuristique(instance, DUREE_CRENEAU_HEURES)
print(
    f"HEURISTIQUE  temps={mesure_heuristique.temps_total:.3f}s "
    f"remplissage={mesure_heuristique.taux_remplissage:.1%} "
    f"ecart_charge={mesure_heuristique.ecart_charge}"
)
