"""Orchestration de l'état `complet` — Prompt 51, Temps 2. Un seul point
d'entrée (`charger_etat_complet`), appelé par la commande de gestion une
fois le jeu `socle` chargé (inchangé, § 2 : « `--etat complet` = l'état
`socle` inchangé, plus ce qui suit »).

Ordre d'appel délibéré, chaque étape ayant besoin de la précédente :
référentiel (§ 2.1) -> instructeurs/lieux/indisponibilité (§ 2.2, sans
brigade) -> organisation (§ 2.3) -> calendrier (§ 2.2, le bivouac cible une
brigade) -> programmes et contrôles E1/E2/E5 (§ 2.4-2.5, chronologie
simulée) -> évaluations E3/E4 et notes de E1/E5 (§ 2.5) -> suivi (§ 2.6, a
besoin des programmes affichés).

`Bootstrap` porte les constantes communes à toutes les étapes (comptes du
socle, date de référence, graine, sortie) ; `ContexteComplet`
(`contexte.py`) ne peut être construit qu'une fois le référentiel, les
ressources et l'organisation chargés — lui seul sert les étapes § 2.4 à
§ 2.6, qui en ont le plus besoin."""

import dataclasses

from evaluations.jeu_recette import (
    evaluations_complet,
    organisation_complet,
    programme_complet,
    referentiel_complet,
    ressources_complet,
    suivi_complet,
)
from evaluations.jeu_recette.contexte import ContexteComplet


@dataclasses.dataclass(frozen=True)
class _Bootstrap:
    objets_socle: dict
    comptes: dict
    date_reference: object
    graine: int
    stdout: object

    @property
    def agissant_ped(self):
        return self.comptes["u_ped"]

    @property
    def agissant_plan(self):
        return self.comptes["u_plan"]


def _charger_referentiel(bootstrap):
    agissant_ped = bootstrap.agissant_ped
    stdout = bootstrap.stdout
    matieres_complet = referentiel_complet.charger_matieres_complet(agissant_ped, stdout)
    formation_f6 = referentiel_complet.charger_formation_f6(
        agissant_ped, bootstrap.objets_socle["types"], stdout
    )
    elements_f6 = referentiel_complet.charger_composition_f6(
        agissant_ped, formation_f6, bootstrap.objets_socle["matieres"], matieres_complet, stdout
    )
    referentiel_complet.charger_prerequis_f6(agissant_ped, formation_f6, elements_f6, stdout)
    referentiel_complet.charger_objectifs_m6(agissant_ped, matieres_complet, stdout)
    return {
        "matieres_complet": matieres_complet,
        "formation_f6": formation_f6,
        "elements_f6": elements_f6,
    }


def _charger_ressources(bootstrap, referentiel):
    agissant_ped, agissant_plan = bootstrap.agissant_ped, bootstrap.agissant_plan
    stdout = bootstrap.stdout
    toutes_matieres = {**bootstrap.objets_socle["matieres"], **referentiel["matieres_complet"]}
    instructeurs_complet = ressources_complet.charger_instructeurs_complet(agissant_ped, stdout)
    ressources_complet.charger_qualifications_complet(
        agissant_ped,
        instructeurs_complet,
        bootstrap.objets_socle["instructeurs"],
        toutes_matieres,
        stdout,
    )
    lieux_complet = ressources_complet.charger_lieux_complet(agissant_plan, stdout)
    ressources_complet.charger_indisponibilite_i3(
        agissant_plan,
        bootstrap.objets_socle["instructeurs"]["I3"],
        bootstrap.date_reference,
        stdout,
    )
    return {
        "instructeurs_complet": instructeurs_complet,
        "lieux_complet": lieux_complet,
        "toutes_instructeurs": {**bootstrap.objets_socle["instructeurs"], **instructeurs_complet},
        "toutes_lieux": {**bootstrap.objets_socle["lieux"], **lieux_complet},
    }


def _charger_organisation(bootstrap, referentiel, ressources):
    agissant_ped, agissant_plan = bootstrap.agissant_ped, bootstrap.agissant_plan
    stdout = bootstrap.stdout
    toutes_formations = {**bootstrap.objets_socle["formations"], "F6": referentiel["formation_f6"]}
    sessions = organisation_complet.charger_sessions_complet(
        agissant_ped, toutes_formations, bootstrap.date_reference, stdout
    )
    brigades = organisation_complet.charger_brigades_complet(
        agissant_ped, agissant_plan, sessions, ressources["toutes_lieux"], stdout
    )
    organisation_complet.charger_stagiaires_complet(
        agissant_ped, sessions, brigades, bootstrap.date_reference, stdout
    )
    # § 2.2 (suite) — le bivouac cible la brigade EXP2 : calendrier posé
    # après l'organisation, pas avant.
    ressources_complet.charger_periodes_complet(
        agissant_plan, brigades, bootstrap.date_reference, stdout
    )
    return {"sessions": sessions, "brigades": brigades}


def _construire_contexte(bootstrap, referentiel, ressources, organisation):
    return ContexteComplet(
        agissant_plan=bootstrap.agissant_plan,
        agissant_ped=bootstrap.agissant_ped,
        agissant_examens=bootstrap.comptes["u_exa"],
        brigades=organisation["brigades"],
        lieux=ressources["toutes_lieux"],
        instructeurs=ressources["toutes_instructeurs"],
        elements_f6=referentiel["elements_f6"],
        element_m4_socle=bootstrap.objets_socle["elements"][("F2", "M4")],
        date_reference=bootstrap.date_reference,
        graine=bootstrap.graine,
        stdout=bootstrap.stdout,
    )


def _charger_programmes_et_evaluations(contexte, organisation):
    programmes, evaluation_e1, _evaluation_e2, evaluation_e5 = (
        programme_complet.charger_programmes_complet(contexte)
    )
    evaluations_complet.charger_notes_e1(contexte, evaluation_e1)
    evaluations_complet.charger_notes_e5(contexte, evaluation_e5)
    evaluations_complet.charger_evaluation_e3(contexte, organisation["sessions"]["S1"])
    evaluations_complet.charger_evaluation_e4(contexte, organisation["sessions"]["S1"])
    return programmes


def _charger_suivi(contexte, programmes):
    suivi_complet.charger_non_executions_complet(contexte, programmes["W-2"], programmes["W-1"])
    suivi_complet.charger_progression_realisee_complet(contexte, programmes["W-2"])


def _compteurs(referentiel, ressources, organisation, programmes):
    return {
        "Matières ajoutées (M6-M9)": len(referentiel["matieres_complet"]),
        "Formations ajoutées (F6)": 1,
        "Instructeurs ajoutés (I6-I9)": len(ressources["instructeurs_complet"]),
        "Lieux ajoutés (L7-L9)": len(ressources["lieux_complet"]),
        "Sessions ajoutées (S1-S3)": len(organisation["sessions"]),
        "Brigades ajoutées": len(organisation["brigades"]),
        "Programmes (W-2 à W+1)": len(programmes),
    }


def charger_etat_complet(objets_socle, date_reference, graine, stdout):
    """`objets_socle` : dict `{"comptes", "types", "formations", "matieres",
    "elements", "instructeurs", "lieux"}`, tous indexés par code — ce que le
    chargement (ou la récupération) du jeu `socle` a produit. Rend un dict
    de compteurs, au même titre que `socle` (`charger_jeu_recette.py::
    _charger`)."""
    bootstrap = _Bootstrap(objets_socle, objets_socle["comptes"], date_reference, graine, stdout)
    referentiel = _charger_referentiel(bootstrap)
    ressources = _charger_ressources(bootstrap, referentiel)
    organisation = _charger_organisation(bootstrap, referentiel, ressources)
    contexte = _construire_contexte(bootstrap, referentiel, ressources, organisation)
    programmes = _charger_programmes_et_evaluations(contexte, organisation)
    _charger_suivi(contexte, programmes)
    return _compteurs(referentiel, ressources, organisation, programmes)
