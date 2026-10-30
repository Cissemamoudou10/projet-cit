"""Orchestration de l'état `socle-planif` — Prompt 53, Temps 1. Un seul
point d'entrée (`charger_etat_socle_planif`), appelé par la commande de
gestion une fois le jeu `socle` chargé (inchangé). Produit exactement ce que
les sections 3 à 7 de RECETTE-00 construisent par l'interface, et AUCUN
programme — RECETTE-00 bis (sections 8-9) part d'un état vierge de ce côté.

Ordre d'appel délibéré : session -> brigades (ont besoin de la session et
des lieux du socle) -> import puis répartition des stagiaires (ont besoin
des brigades) -> calendrier et indisponibilités (indépendants de
l'organisation) -> objectifs pédagogiques (indépendants de tout le reste).
"""

from evaluations.jeu_recette import (
    organisation_socle_planif,
    referentiel_socle_planif,
    ressources_socle_planif,
)


def charger_etat_socle_planif(objets_socle, date_reference, stdout):
    """`objets_socle` : dict `{"comptes", "types", "formations", "matieres",
    "elements", "instructeurs", "lieux"}`, tels que rendus par le chargement
    (ou la récupération) du jeu `socle` — voir `charger_jeu_recette.py::
    _charger`/`_objets_socle`. Rend un dict de compteurs, au même titre que
    `socle` et `complet`."""
    agissant_ped = objets_socle["comptes"]["u_ped"]
    agissant_plan = objets_socle["comptes"]["u_plan"]
    formations = objets_socle["formations"]
    instructeurs = objets_socle["instructeurs"]
    lieux = objets_socle["lieux"]
    matieres = objets_socle["matieres"]

    session = organisation_socle_planif.charger_session_socle_planif(
        agissant_ped, formations, date_reference, stdout
    )
    brigades = organisation_socle_planif.charger_brigades_socle_planif(
        agissant_ped, agissant_plan, session, lieux, stdout
    )
    organisation_socle_planif.importer_stagiaires_socle_planif(agissant_ped, session, stdout)
    organisation_socle_planif.repartir_stagiaires_socle_planif(
        agissant_ped, session, brigades, date_reference, stdout
    )
    ressources_socle_planif.charger_calendrier_socle_planif(agissant_plan, date_reference, stdout)
    ressources_socle_planif.charger_indisponibilites_socle_planif(
        agissant_plan, instructeurs, lieux, date_reference, stdout
    )
    referentiel_socle_planif.charger_objectifs_socle_planif(agissant_ped, matieres, stdout)

    return {
        "Sessions ajoutées (S0)": 1,
        "Brigades ajoutées (EXP1, EXP2)": len(brigades),
    }
