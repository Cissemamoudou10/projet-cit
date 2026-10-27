"""Organisation du jeu volumineux — Prompt 51, Temps 3, § 3.1. 15 sessions
actives + 3 terminées, 32 brigades actives (chacune avec sa salle
attitrée) + quelques brigades sur les sessions terminées, ≈900 stagiaires.

Les stagiaires sont le seul objet de ce module sans règle au-delà des
contraintes de base (RG-17 : unicité du matricule PAR SESSION, assurée ici
par construction, jamais par une requête de plus) — créés directement,
`full_clean()` sans vérification d'unicité puis `bulk_create`, comme les
règles communes du prompt l'autorisent explicitement (§ 1). L'AFFECTATION,
elle, porte une règle réelle (RG-20, une seule brigade à la fois) : elle
reste un appel de service, un par stagiaire affecté."""

import dataclasses
import datetime

from evaluations.jeu_recette.donnees_volume import (
    CAPACITE_SALLE_ATTITREE,
    NOMBRE_BRIGADES_ACTIVES,
    NOMBRE_SESSIONS_ACTIVES,
    NOMBRE_SESSIONS_TERMINEES,
    NOMBRE_STAGIAIRES_NON_AFFECTES,
    NOMBRE_STAGIAIRES_RADIES,
)
from organisation.models import Stagiaire
from organisation.services.affectation import ServiceAffectation
from organisation.services.brigade import ServiceBrigade
from organisation.services.session import ServiceSession
from ressources.models import CategorieLieu
from ressources.services.salle_attitree import ServiceSalleAttitree

GRADES_STAGIAIRES = ("2cl", "1cl", "Sgt", "Sgt-chef")
UNITE_PAR_DEFAUT = "CIT (volumineux)"
MOTIF_RADIATION = "Radiation (jeu volumineux, § 3.1)."
BRIGADES_PAR_SESSION_TERMINEE = 2


@dataclasses.dataclass(frozen=True)
class PlanBrigade:
    code: str
    effectif: int


@dataclasses.dataclass(frozen=True)
class GroupeSessionsVolume:
    """Une session créée avec son plan de brigades (`PlanBrigade`, décidé
    AVANT la session — voir `_planifier`) — voyagent toujours ensemble
    entre `charger_sessions_volume` et `charger_brigades_volume`
    (`.claude/rules/python.md`, § 5 paramètres max)."""

    sessions: dict
    plan: list


@dataclasses.dataclass(frozen=True)
class GroupeBrigadesVolume:
    actives: dict
    terminees: dict

    def toutes(self):
        return {**self.actives, **self.terminees}


@dataclasses.dataclass(frozen=True)
class AgissantsOrganisationVolume:
    agissant_ped: object
    agissant_plan: object


def _formations_ouvrables(formations):
    return [formation for formation in formations.values() if not formation.archive]


def _repartir_brigades_par_session(generateur, nombre_sessions, nombre_brigades):
    """Au moins une brigade par session, le reste distribué au hasard —
    reproduit le ratio ≈2,2 brigades/session d'HYPOTHESES.md sans jamais
    descendre à zéro."""
    repartition = [1] * nombre_sessions
    for _ in range(nombre_brigades - nombre_sessions):
        repartition[generateur.randrange(nombre_sessions)] += 1
    return repartition


def _planifier(generateur, nombre_sessions, nombre_brigades, prefixe):
    """Décide à l'avance combinaison (nombre de brigades, effectif de
    chacune) par session — pour que la session connaisse son effectif
    attendu RÉEL dès sa création, jamais une valeur à corriger après
    coup."""
    repartition = _repartir_brigades_par_session(generateur, nombre_sessions, nombre_brigades)
    plan = []
    for indice_session, nombre in enumerate(repartition):
        brigades_session = [
            PlanBrigade(
                f"{prefixe}{indice_session + 1:02d}-{n}",
                generateur.randint(*CAPACITE_SALLE_ATTITREE),  # jamais plus que la plus grande salle
            )
            for n in range(1, nombre + 1)
        ]
        plan.append(brigades_session)
    return plan


def charger_sessions_volume(agissant, generateur, formations, date_reference, stdout):
    formations_ouvrables = _formations_ouvrables(formations)
    plan_actives = _planifier(generateur, NOMBRE_SESSIONS_ACTIVES, NOMBRE_BRIGADES_ACTIVES, "B")
    plan_terminees = _planifier(
        generateur, NOMBRE_SESSIONS_TERMINEES,
        NOMBRE_SESSIONS_TERMINEES * BRIGADES_PAR_SESSION_TERMINEE, "BT",
    )
    sessions_actives = {}
    for indice, brigades_session in enumerate(plan_actives, start=1):
        code = f"SV-A{indice:02d}"
        formation = formations_ouvrables[(indice - 1) % len(formations_ouvrables)]
        sessions_actives[code] = ServiceSession.creer(
            agissant,
            {
                "intitule": code,
                "formation": formation,
                "date_debut": date_reference - datetime.timedelta(weeks=16),
                "date_fin": date_reference + datetime.timedelta(weeks=20),
                "effectif_attendu": sum(b.effectif for b in brigades_session),
            },
        )
    sessions_terminees = {}
    for indice, brigades_session in enumerate(plan_terminees, start=1):
        code = f"SV-T{indice:02d}"
        formation = formations_ouvrables[(indice - 1) % len(formations_ouvrables)]
        sessions_terminees[code] = ServiceSession.creer(
            agissant,
            {
                "intitule": code,
                "formation": formation,
                "date_debut": date_reference - datetime.timedelta(weeks=60),
                "date_fin": date_reference - datetime.timedelta(weeks=20),
                "effectif_attendu": sum(b.effectif for b in brigades_session),
            },
        )
    stdout.write(
        f"  {len(sessions_actives)} sessions actives, {len(sessions_terminees)} terminées."
    )
    return GroupeSessionsVolume(sessions_actives, plan_actives), GroupeSessionsVolume(sessions_terminees, plan_terminees)


def _creer_brigades_pour(agissants: AgissantsOrganisationVolume, groupe: GroupeSessionsVolume, lieux_disponibles):
    """Brigades triées par effectif DÉCROISSANT, salles par capacité
    DÉCROISSANTE, appariées dans cet ordre — ne suffit pas seul à garantir
    RG-13 (deux tirages indépendants sur la même plage peuvent encore se
    croiser de peu) : l'effectif est borné à la capacité de la salle
    appariée, jamais l'inverse."""
    paires_session_brigade = [
        (session, planifiee)
        for (_, session), brigades_session in zip(groupe.sessions.items(), groupe.plan)
        for planifiee in brigades_session
    ]
    paires_session_brigade.sort(key=lambda paire: paire[1].effectif, reverse=True)
    lieux_tries = sorted(lieux_disponibles, key=lambda lieu: lieu.capacite, reverse=True)
    brigades = {}
    for (session, planifiee), lieu in zip(paires_session_brigade, lieux_tries):
        effectif = min(planifiee.effectif, lieu.capacite)
        brigade = ServiceBrigade.creer(
            agissants.agissant_ped, session, {"designation": planifiee.code, "effectif_previsionnel": effectif}
        )
        ServiceSalleAttitree.attribuer(agissants.agissant_plan, brigade, lieu)
        brigades[planifiee.code] = brigade
    return brigades


def charger_brigades_volume(
    agissants: AgissantsOrganisationVolume,
    groupe_actives: GroupeSessionsVolume,
    groupe_terminees: GroupeSessionsVolume,
    lieux,
    stdout,
):
    salles_attitrees = [lieu for lieu in lieux.values() if lieu.categorie == CategorieLieu.SALLE_ATTITREE]
    brigades_actives = _creer_brigades_pour(agissants, groupe_actives, salles_attitrees[:NOMBRE_BRIGADES_ACTIVES])
    brigades_terminees = _creer_brigades_pour(agissants, groupe_terminees, salles_attitrees)
    stdout.write(
        f"  {len(brigades_actives)} brigades actives, {len(brigades_terminees)} sur sessions terminées."
    )
    return GroupeBrigadesVolume(brigades_actives, brigades_terminees)


def _nouveau_stagiaire(session, code_brigade, rang, generateur):
    return Stagiaire(
        session=session,
        matricule=f"STGV-{session.pk}-{code_brigade}-{rang:04d}",
        nom=f"{code_brigade}",
        prenom=f"Stagiaire {rang}",
        grade=generateur.choice(GRADES_STAGIAIRES),
        unite=UNITE_PAR_DEFAUT,
    )


def _creer_et_affecter_brigade(agissant, generateur, brigade, code_brigade):
    session = brigade.session
    stagiaires = []
    for rang in range(1, brigade.effectif_previsionnel + 1):
        stagiaire = _nouveau_stagiaire(session, code_brigade, rang, generateur)
        stagiaire.full_clean(validate_unique=False)
        stagiaires.append(stagiaire)
    Stagiaire.objects.bulk_create(stagiaires)
    for stagiaire in Stagiaire.objects.filter(session=session, nom=code_brigade):
        ServiceAffectation.affecter(agissant, stagiaire, brigade)
    return len(stagiaires)


def _creer_non_affectes_et_radies(agissant, generateur, session_reference, stdout):
    extras = []
    for rang in range(1, NOMBRE_STAGIAIRES_NON_AFFECTES + 1):
        stagiaire = _nouveau_stagiaire(session_reference, "NA", rang, generateur)
        stagiaire.full_clean(validate_unique=False)
        extras.append(stagiaire)
    for rang in range(1, NOMBRE_STAGIAIRES_RADIES + 1):
        stagiaire = _nouveau_stagiaire(session_reference, "RD", rang, generateur)
        stagiaire.radie = True
        stagiaire.motif_radiation = MOTIF_RADIATION
        stagiaire.date_radiation = session_reference.date_debut
        stagiaire.full_clean(validate_unique=False)
        extras.append(stagiaire)
    Stagiaire.objects.bulk_create(extras)
    stdout.write(
        f"  {NOMBRE_STAGIAIRES_NON_AFFECTES} stagiaires non affectés et "
        f"{NOMBRE_STAGIAIRES_RADIES} radiés ajoutés (session {session_reference})."
    )


def charger_stagiaires_volume(agissant, generateur, sessions_actives, groupe_brigades: GroupeBrigadesVolume, stdout):
    total = 0
    for code_brigade, brigade in groupe_brigades.toutes().items():
        total += _creer_et_affecter_brigade(agissant, generateur, brigade, code_brigade)
    premiere_session_active = next(iter(sessions_actives.values()))
    _creer_non_affectes_et_radies(agissant, generateur, premiere_session_active, stdout)
    stdout.write(f"  {total} stagiaires affectés sur l'ensemble des brigades.")
    return total
