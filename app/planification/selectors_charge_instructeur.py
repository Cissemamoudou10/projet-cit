"""Heures d'enseignement par instructeur — US-INS-04, C1 (prompt 48).

Fournisseur de `noyau.services.parametres.ResolveurHeuresEnseignementParInstructeur`,
installé par `PlanificationConfig.ready()`. `ressources` (le domaine
Instructeurs) ne peut pas importer `planification` directement (sens de
dépendance interdit), seulement passer par ce résolveur.
"""

import datetime

from planification.models import Seance


def heures_enseignement_par_instructeur(debut, fin) -> dict:
    """C1 : toutes les séances dont le DÉBUT tombe dans `[debut, fin)`,
    sans filtre d'état de programme — à la différence du réalisé
    (US-SUI-01), qui ne compte que les programmes affichés. Une requête,
    agrégation en mémoire (même patron que
    `services/contraintes.py::_agreger_par_element_et_par_element_brigade`)."""
    lignes = Seance.objects.filter(debut__gte=debut, debut__lt=fin).values(
        "instructeur_id", "debut", "fin", "element_referentiel__matiere__intitule"
    )
    par_cle: dict = {}
    for ligne in lignes:
        duree = (ligne["fin"] - ligne["debut"]) / datetime.timedelta(hours=1)
        cle = (ligne["instructeur_id"], ligne["element_referentiel__matiere__intitule"])
        par_cle[cle] = par_cle.get(cle, 0.0) + duree

    resultat: dict = {}
    for (instructeur_id, matiere), heures in par_cle.items():
        resultat.setdefault(instructeur_id, []).append({"matiere": matiere, "heures": heures})
    return resultat
