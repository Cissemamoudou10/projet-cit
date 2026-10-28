"""Orchestration du jeu volumineux — Prompt 51, Temps 3. Un seul point
d'entrée (`charger_etat_volume`), appelé par la commande de gestion. Base
dédiée (`pfe_cit_volume`) : contrairement à l'état `complet`, ce jeu ne
repose sur AUCUN objet du jeu `socle` — tout est créé ici, depuis zéro
(§ 3, tableau « Jeu / Base »).

Ordre d'appel délibéré, chaque étape ayant besoin de la précédente :
comptes -> référentiel (§ 3.1) -> instructeurs/lieux/indisponibilités
(sans brigade) -> organisation (sessions, brigades, stagiaires) ->
calendrier (le bivouac cible des brigades) -> évaluations des sessions
terminées (procès-verbal, § 3.1) -> programmes des brigades actives,
mesurés (§ 3.2) -> évaluations des brigades actives et certificatives à
venir (indépendantes de la génération, voir `evaluations_volume.py`)."""

import dataclasses

from django.core.management import call_command

from evaluations.jeu_recette.calendrier_volume import charger_calendrier_volume
from evaluations.jeu_recette.comptes_volume import charger_comptes_volume
from evaluations.jeu_recette.donnees_volume import SEMAINES_PASSEES_AFFICHEES, codes_formations_ouvrables
from evaluations.jeu_recette.evaluations_volume import (
    ContexteEvaluationsVolume,
    charger_certificatives_a_venir_volume,
    charger_formatives_actives_volume,
    charger_formatives_terminees_volume,
    charger_proces_verbaux_volume,
)
from evaluations.jeu_recette.organisation_volume import (
    AgissantsOrganisationVolume,
    charger_brigades_volume,
    charger_sessions_actives_volume,
    charger_sessions_terminees_volume,
    charger_stagiaires_volume,
    planifier_sessions_actives,
    volumes_cibles_par_formation,
)
from evaluations.jeu_recette.programme_volume import (
    AgissantsProgrammeVolume,
    OptionsProgrammesVolume,
    charger_programmes_volume,
)
from evaluations.jeu_recette.referentiel_volume import (
    charger_composition_volume,
    charger_formations_volume,
    charger_matieres_volume,
    charger_types_formation_volume,
    combiner_formations_et_cibles,
)
from evaluations.jeu_recette.ressources_volume import (
    charger_indisponibilites_volume,
    charger_instructeurs_volume,
    charger_lieux_volume,
    charger_qualifications_volume,
)


@dataclasses.dataclass(frozen=True)
class _BootstrapVolume:
    comptes: dict
    generateur: object
    date_reference: object
    stdout: object

    @property
    def agissant_ped(self):
        return self.comptes["v_ped"]

    @property
    def agissant_plan(self):
        return self.comptes["v_plan"]

    @property
    def agissant_examens(self):
        return self.comptes["v_exa"]


def _charger_referentiel(bootstrap, plans_sessions_actives):
    agissant_ped, stdout = bootstrap.agissant_ped, bootstrap.stdout
    types = charger_types_formation_volume(agissant_ped, stdout)
    matieres = charger_matieres_volume(agissant_ped, bootstrap.generateur, stdout)
    formations = charger_formations_volume(agissant_ped, bootstrap.generateur, types, stdout)
    volumes_cibles = volumes_cibles_par_formation(plans_sessions_actives)
    formations_avec_cible = combiner_formations_et_cibles(formations, volumes_cibles)
    elements = charger_composition_volume(agissant_ped, bootstrap.generateur, formations_avec_cible, matieres, stdout)
    return {"types": types, "matieres": matieres, "formations": formations, "elements": elements}


def _charger_ressources(bootstrap, referentiel):
    agissant_ped, agissant_plan, stdout = bootstrap.agissant_ped, bootstrap.agissant_plan, bootstrap.stdout
    instructeurs = charger_instructeurs_volume(agissant_ped, bootstrap.generateur, stdout)
    charger_qualifications_volume(agissant_ped, bootstrap.generateur, instructeurs, referentiel["matieres"], stdout)
    lieux = charger_lieux_volume(agissant_plan, bootstrap.generateur, stdout)
    charger_indisponibilites_volume(agissant_plan, bootstrap.generateur, instructeurs, bootstrap.date_reference, stdout)
    return {"instructeurs": instructeurs, "lieux": lieux}


def _charger_organisation(bootstrap, referentiel, ressources, plans_sessions_actives):
    agissants = AgissantsOrganisationVolume(bootstrap.agissant_ped, bootstrap.agissant_plan)
    stdout = bootstrap.stdout
    groupe_sessions_actives = charger_sessions_actives_volume(
        bootstrap.agissant_ped, bootstrap.generateur, plans_sessions_actives, referentiel["formations"], stdout
    )
    groupe_sessions_terminees = charger_sessions_terminees_volume(
        bootstrap.agissant_ped, bootstrap.generateur, referentiel["formations"], bootstrap.date_reference, stdout
    )
    groupe_brigades = charger_brigades_volume(
        agissants, groupe_sessions_actives, groupe_sessions_terminees, ressources["lieux"], stdout
    )
    charger_stagiaires_volume(
        bootstrap.agissant_ped, bootstrap.generateur, groupe_sessions_actives.sessions, groupe_brigades, stdout
    )
    charger_calendrier_volume(
        bootstrap.agissant_plan, bootstrap.generateur, bootstrap.date_reference, groupe_brigades.actives, stdout
    )
    return {
        "sessions_actives": groupe_sessions_actives.sessions,
        "sessions_terminees": groupe_sessions_terminees.sessions,
        "brigades": groupe_brigades,
    }


def _charger_evaluations_terminees(bootstrap, referentiel, organisation):
    contexte = ContexteEvaluationsVolume(
        bootstrap.agissant_examens, bootstrap.generateur, bootstrap.date_reference, bootstrap.stdout
    )
    charger_formatives_terminees_volume(contexte, organisation["brigades"].terminees, referentiel["elements"])
    charger_proces_verbaux_volume(contexte, organisation["sessions_terminees"])


def _charger_programmes(bootstrap, organisation, semaines_passees):
    agissants = AgissantsProgrammeVolume(bootstrap.agissant_plan, bootstrap.agissant_ped)
    options = OptionsProgrammesVolume(
        organisation["brigades"].actives, bootstrap.date_reference, semaines_passees
    )
    return charger_programmes_volume(agissants, bootstrap.generateur, options, bootstrap.stdout)


def _charger_evaluations_actives(bootstrap, referentiel, organisation):
    contexte = ContexteEvaluationsVolume(
        bootstrap.agissant_examens, bootstrap.generateur, bootstrap.date_reference, bootstrap.stdout
    )
    charger_formatives_actives_volume(contexte, organisation["brigades"].actives, referentiel["elements"])
    charger_certificatives_a_venir_volume(contexte, organisation["sessions_actives"])


def _compteurs(referentiel, ressources, organisation, mesures):
    return {
        "Comptes": 7,
        "Matières ajoutées": len(referentiel["matieres"]),
        "Formations ajoutées": len(referentiel["formations"]),
        "Instructeurs ajoutés": len(ressources["instructeurs"]),
        "Lieux ajoutés": len(ressources["lieux"]),
        "Sessions actives": len(organisation["sessions_actives"]),
        "Sessions terminées": len(organisation["sessions_terminees"]),
        "Brigades actives": len(organisation["brigades"].actives),
        "Brigades sur sessions terminées": len(organisation["brigades"].terminees),
        "Programmes générés": len(mesures),
    }


def charger_etat_volume(generateur, date_reference, stdout, semaines_passees=SEMAINES_PASSEES_AFFICHEES):
    """`semaines_passees` : repli `--semaines N` (§ 3.2). Rend
    `(compteurs, mesures)` — `mesures` sert `MESURES-REFERENCE.md` (BNF-04)
    et `imprimer_compte_rendu`."""
    call_command("initialiser_habilitations")
    call_command("initialiser_natures_evenement")
    call_command("initialiser_gabarits_documents")
    comptes = charger_comptes_volume(stdout)
    bootstrap = _BootstrapVolume(comptes, generateur, date_reference, stdout)
    # APRÈS les comptes, jamais avant : `initialiser_grilles_horaires` exige
    # qu'un compte administrateur existe déjà (RG-63) — même écart volontaire
    # que celui documenté dans `reinitialiser_base_recette.ps1`.
    call_command("initialiser_grilles_horaires")

    # Décidé avant même le référentiel (correctif du 27/10/2026) : chaque
    # formation a besoin de connaître la durée de la session la plus
    # longue qui la portera pour dimensionner son volume horaire — avant
    # qu'aucune session, ni même aucune formation, n'existe en base.
    plans_sessions_actives = planifier_sessions_actives(generateur, date_reference, codes_formations_ouvrables())

    referentiel = _charger_referentiel(bootstrap, plans_sessions_actives)
    ressources = _charger_ressources(bootstrap, referentiel)
    organisation = _charger_organisation(bootstrap, referentiel, ressources, plans_sessions_actives)
    _charger_evaluations_terminees(bootstrap, referentiel, organisation)
    mesures = _charger_programmes(bootstrap, organisation, semaines_passees)
    _charger_evaluations_actives(bootstrap, referentiel, organisation)

    return _compteurs(referentiel, ressources, organisation, mesures), mesures
