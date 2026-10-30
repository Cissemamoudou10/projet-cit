"""Organisation ajoutée par l'état `socle-planif` — Prompt 53, Temps 1,
§ Session/Brigades/Stagiaires. `agissant_ped` (u_ped) crée session, brigade
et stagiaires (import) ; `agissant_plan` (u_plan) affecte la salle attitrée
(RG-14, même répartition que l'état `complet`).

L'import passe par le SERVICE D'IMPORT RÉEL (`organisation.import_stagiaires.
confirmation.confirmer`), jamais par une création directe de `Stagiaire` :
les deux fichiers de recette existants sont régénérés dans un dossier
temporaire (jamais le dépôt suivi), lus en octets, puis confirmés — exactement
le chemin qu'un recetteur suit à l'écran.
"""

import datetime
import tempfile
from pathlib import Path

from django.utils import timezone

from evaluations.jeu_recette.donnees_socle_planif import (
    BRIGADES_SOCLE_PLANIF,
    CODE_FORMATION_SESSION,
    CODE_SESSION,
    DECALAGE_SEMAINE_AFFECTATION,
    DECALAGE_SEMAINE_DEBUT_SESSION,
    DECALAGE_SEMAINE_FIN_SESSION,
    EFFECTIF_ATTENDU_SESSION,
    FICHIERS_IMPORT_STAGIAIRES,
    INTITULE_SESSION,
    MOTIF_RADIATION,
    NOMBRE_AFFECTES_EXP1,
    NOMBRE_AFFECTES_EXP2,
    NOMBRE_RADIES,
)
from evaluations.jeu_recette.fichiers_import import constructeur
from evaluations.jeu_recette.semaines import semaine
from organisation.import_stagiaires.confirmation import confirmer
from organisation.models import Stagiaire
from organisation.services.affectation import ServiceAffectation
from organisation.services.brigade import ServiceBrigade
from organisation.services.session import ServiceSession
from organisation.services.stagiaire import ServiceStagiaire
from ressources.services.salle_attitree import ServiceSalleAttitree


def charger_session_socle_planif(agissant_ped, formations, date_reference, stdout):
    session = ServiceSession.creer(
        agissant_ped,
        {
            "intitule": INTITULE_SESSION,
            "formation": formations[CODE_FORMATION_SESSION],
            "date_debut": semaine(date_reference, DECALAGE_SEMAINE_DEBUT_SESSION),
            "date_fin": semaine(date_reference, DECALAGE_SEMAINE_FIN_SESSION)
            + datetime.timedelta(days=4),
            "effectif_attendu": EFFECTIF_ATTENDU_SESSION,
        },
    )
    stdout.write(f"  Session {CODE_SESSION} ajoutée (F1, W-1 à W+10, effectif attendu 40).")
    return session


def charger_brigades_socle_planif(agissant_ped, agissant_plan, session, lieux, stdout):
    brigades = {}
    for donnees in BRIGADES_SOCLE_PLANIF:
        brigade = ServiceBrigade.creer(
            agissant_ped,
            session,
            {"designation": donnees.code, "effectif_previsionnel": donnees.effectif_previsionnel},
        )
        ServiceSalleAttitree.attribuer(agissant_plan, brigade, lieux[donnees.code_lieu_attitre])
        brigades[donnees.code] = brigade
    stdout.write(f"  {len(brigades)} brigades ajoutées (EXP1, EXP2), chacune avec sa salle attitrée.")
    return brigades


def importer_stagiaires_socle_planif(agissant_ped, session, stdout):
    """Régénère les fichiers de recette dans un dossier TEMPORAIRE (jamais
    `docs/recette/fichiers-import/`, suivi et figé) puis confirme les deux
    fichiers visés par le Temps 1 — 10 + 45 = 55 stagiaires, tous non
    affectés à ce stade (la répartition est un second geste, § Affectation)."""
    with tempfile.TemporaryDirectory() as dossier_temporaire:
        dossier = Path(dossier_temporaire)
        constructeur.generer(dossier, stdout)
        total_enregistres = 0
        for nom_fichier in FICHIERS_IMPORT_STAGIAIRES:
            contenu = (dossier / nom_fichier).read_bytes()
            rapport = confirmer(agissant_ped, session, contenu, nom_fichier)
            total_enregistres += len(rapport.lignes_valides)
    stdout.write(f"  {total_enregistres} stagiaires importés par le service d'import (01 + 03).")


def _stagiaires_par_matricule(session):
    return list(Stagiaire.objects.filter(session=session).order_by("matricule"))


def repartir_stagiaires_socle_planif(agissant_ped, session, brigades, date_reference, stdout):
    """R00-SES-14/15 : les 35 affectations sont datées au lundi de W-1 par
    horloge simulée, pour qu'un déplacement ou un retrait soit possible le
    jour de la recette — jamais le jour réel du chargement. La radiation,
    elle, n'est soumise à aucune contrainte de ce type (même précédent que
    l'état `complet`, `organisation_complet.py::_charger_stagiaires_s1`) :
    pas d'horloge simulée pour ce geste."""
    from freezegun import freeze_time

    stagiaires = _stagiaires_par_matricule(session)
    fin_exp1 = NOMBRE_AFFECTES_EXP1
    fin_exp2 = fin_exp1 + NOMBRE_AFFECTES_EXP2
    exp1 = stagiaires[:fin_exp1]
    exp2 = stagiaires[fin_exp1:fin_exp2]
    radie = stagiaires[fin_exp2 : fin_exp2 + NOMBRE_RADIES][0]

    lundi_w_moins_1 = semaine(date_reference, DECALAGE_SEMAINE_AFFECTATION)
    instant_affectation = timezone.make_aware(
        datetime.datetime.combine(lundi_w_moins_1, datetime.time(6, 0))
    )
    with freeze_time(instant_affectation):
        for stagiaire in exp1:
            ServiceAffectation.affecter(agissant_ped, stagiaire, brigades["EXP1"])
        for stagiaire in exp2:
            ServiceAffectation.affecter(agissant_ped, stagiaire, brigades["EXP2"])

    ServiceStagiaire.radier(agissant_ped, radie, MOTIF_RADIATION, lundi_w_moins_1)
    stdout.write(
        f"  Répartition : {len(exp1)} -> EXP1, {len(exp2)} -> EXP2, 1 radié "
        f"({len(stagiaires) - len(exp1) - len(exp2) - 1} non affectés)."
    )
