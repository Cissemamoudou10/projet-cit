"""Organisation ajoutée par l'état `complet` — Prompt 51, § 2.3.

`agissant_pedagogique` (u_ped) crée sessions/brigades/stagiaires ; les salles
attitrées sont affectées par `agissant_planification` (u_plan, RG-14 :
« affectée par la cellule planification » — même répartition que le reste du
chargeur). Les stagiaires N'APPELLENT PAS `jeu_recette.alea` : ce sont des
objets énumérés par le § 2.3 (39+12+8=59), pas une population en volume
(réservée à `--etat volume`)."""

import dataclasses
import datetime

from evaluations.jeu_recette.donnees_complet import (
    BRIGADES_COMPLET,
    GRADE_STAGIAIRES_PAR_DEFAUT,
    MOTIF_RADIATION,
    NOMBRE_NON_AFFECTES_S1,
    NOMBRE_RADIES_S1,
    PREFIXE_MATRICULE_STAGIAIRE,
    SESSIONS_COMPLET,
    UNITE_STAGIAIRES_PAR_DEFAUT,
)
from evaluations.jeu_recette.semaines import semaine
from organisation.services.affectation import ServiceAffectation
from organisation.services.brigade import ServiceBrigade
from organisation.services.session import ServiceSession
from organisation.services.stagiaire import ServiceStagiaire
from ressources.services.salle_attitree import ServiceSalleAttitree


def charger_sessions_complet(agissant_pedagogique, formations, date_reference, stdout):
    sessions = {}
    for donnees in SESSIONS_COMPLET:
        sessions[donnees.code] = ServiceSession.creer(
            agissant_pedagogique,
            {
                "intitule": donnees.intitule,
                "formation": formations[donnees.code_formation],
                "date_debut": semaine(date_reference, donnees.decalage_semaine_debut),
                "date_fin": semaine(date_reference, donnees.decalage_semaine_fin)
                + datetime.timedelta(days=4),
                "effectif_attendu": sum(
                    b.effectif_previsionnel
                    for b in BRIGADES_COMPLET
                    if b.code_session == donnees.code
                ),
            },
        )
    stdout.write(f"  {len(sessions)} sessions ajoutées (S1, S2, S3).")
    return sessions


def charger_brigades_complet(agissant_pedagogique, agissant_planification, sessions, lieux, stdout):
    brigades = {}
    for donnees in BRIGADES_COMPLET:
        brigade = ServiceBrigade.creer(
            agissant_pedagogique,
            sessions[donnees.code_session],
            {"designation": donnees.code, "effectif_previsionnel": donnees.effectif_previsionnel},
        )
        ServiceSalleAttitree.attribuer(agissant_planification, brigade, lieux[donnees.code_lieu])
        brigades[donnees.code] = brigade
    stdout.write(f"  {len(brigades)} brigades ajoutées, chacune avec sa salle attitrée.")
    return brigades


@dataclasses.dataclass(frozen=True)
class SpecificationStagiaires:
    code_session: str
    prefixe_rang: str
    effectif: int
    brigade: object = None


def _creer_stagiaires(agissant, session, spec):
    stagiaires = []
    for rang in range(1, spec.effectif + 1):
        stagiaire = ServiceStagiaire.creer(
            agissant,
            session,
            {
                "matricule": (
                    f"{PREFIXE_MATRICULE_STAGIAIRE}-{spec.code_session}-{spec.prefixe_rang}"
                    f"{rang:04d}"
                ),
                "nom": f"{spec.code_session}",
                "prenom": f"Stagiaire {spec.prefixe_rang}{rang}",
                "grade": GRADE_STAGIAIRES_PAR_DEFAUT,
                "unite": UNITE_STAGIAIRES_PAR_DEFAUT,
            },
        )
        if spec.brigade is not None:
            ServiceAffectation.affecter(agissant, stagiaire, spec.brigade)
        stagiaires.append(stagiaire)
    return stagiaires


def _charger_stagiaires_s1(agissant, session_s1, brigades, date_reference, stdout):
    stagiaires_exp1 = _creer_stagiaires(
        agissant, session_s1, SpecificationStagiaires("S1", "A", 20, brigades["EXP1"])
    )
    stagiaires_exp2 = _creer_stagiaires(
        agissant, session_s1, SpecificationStagiaires("S1", "B", 15, brigades["EXP2"])
    )
    non_affectes = _creer_stagiaires(
        agissant, session_s1, SpecificationStagiaires("S1", "N", NOMBRE_NON_AFFECTES_S1)
    )
    radies = _creer_stagiaires(
        agissant, session_s1, SpecificationStagiaires("S1", "R", NOMBRE_RADIES_S1)
    )
    date_radiation = semaine(date_reference, -2)
    for stagiaire in radies:
        ServiceStagiaire.radier(agissant, stagiaire, MOTIF_RADIATION, date_radiation)
    stdout.write(
        f"  {len(stagiaires_exp1) + len(stagiaires_exp2) + len(non_affectes) + len(radies)} "
        "stagiaires ajoutés pour S1 (35 affectés + 3 non affectés + 1 radié)."
    )


def charger_stagiaires_complet(agissant_pedagogique, sessions, brigades, date_reference, stdout):
    """S1 : 35 affectés (20 EXP1 + 15 EXP2) + 3 non affectés + 1 radié.
    S2 : 12 affectés (CDP1). S3 : 8 affectés (CDP9), aucune évaluation
    (§ 2.3, § 2.7)."""
    _charger_stagiaires_s1(agissant_pedagogique, sessions["S1"], brigades, date_reference, stdout)
    stagiaires_s2 = _creer_stagiaires(
        agissant_pedagogique,
        sessions["S2"],
        SpecificationStagiaires("S2", "A", 12, brigades["CDP1"]),
    )
    stagiaires_s3 = _creer_stagiaires(
        agissant_pedagogique,
        sessions["S3"],
        SpecificationStagiaires("S3", "A", 8, brigades["CDP9"]),
    )
    stdout.write(
        f"  {len(stagiaires_s2)} stagiaires ajoutés pour S2, {len(stagiaires_s3)} pour S3."
    )
