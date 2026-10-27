"""Orchestration du chargement complet — appelée par la commande de gestion
(`preparer_demonstration`) ET par le test de scénario
(`tests/scenarios/test_demonstration_j2.py`) : une seule source pour ce que
contient la base avant l'étape 1, jamais deux jeux de données qui
divergent."""

from django.contrib.auth import get_user_model
from django.core.management import call_command

from planification.jeu_demonstration_j2.comptes import charger_comptes, recuperer_comptes
from planification.jeu_demonstration_j2.donnees import IDENTIFIANT_ADMINISTRATEUR
from planification.jeu_demonstration_j2.instructeurs import (
    charger_instructeurs,
    charger_qualifications,
)
from planification.jeu_demonstration_j2.lieux import charger_lieu
from planification.jeu_demonstration_j2.organisation import charger_organisation
from planification.jeu_demonstration_j2.referentiel import charger_referentiel


def charger_tout(stdout):
    """Rend un dict `{"comptes", "formation", "element_programme",
    "element_examens", "session", "brigade", "instructeurs", "lieu"}` —
    tout ce que les dix étapes du fil A1 referont vivre.

    Les comptes ne sont jamais recréés dès qu'ils existent déjà (RG-27,
    même raison que les deux jeux existants) : seul le DOMAINE est remis à
    zéro à chaque appel (§ A3, « rejouable »), jamais les comptes ni le
    journal."""
    call_command("initialiser_habilitations")
    deja_present = get_user_model().objects.filter(username=IDENTIFIANT_ADMINISTRATEUR).exists()
    comptes = recuperer_comptes(stdout) if deja_present else charger_comptes(stdout)
    # Par domaine (§ 11.2) : l'administrateur ne porte que l'administration
    # elle-même — référentiel, instructeurs/qualifications et organisation
    # reviennent à la pédagogique, lieux/calendrier à la planification
    # (mêmes comptes agissants que `evaluations.jeu_recette`).
    pedagogique, planification = comptes["ped.j2"], comptes["plan.j2"]

    formation, element_programme, element_examens = charger_referentiel(pedagogique, stdout)
    instructeurs = charger_instructeurs(pedagogique, stdout)
    charger_qualifications(pedagogique, instructeurs, stdout)
    lieu = charger_lieu(planification, stdout)
    session, brigade, brigade_temoin = charger_organisation(pedagogique, formation, stdout)

    call_command("initialiser_grilles_horaires")

    return {
        "comptes": comptes,
        "formation": formation,
        "element_programme": element_programme,
        "element_examens": element_examens,
        "session": session,
        "brigade": brigade,
        "brigade_temoin": brigade_temoin,
        "instructeurs": instructeurs,
        "lieu": lieu,
    }
