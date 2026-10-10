"""Chargement de la session, des brigades et des stagiaires de la
démonstration J2 — ce que le jeu de recette et le jeu de démonstration du
sprint 1 ne posent pas, et dont l'étape 1 (générer le programme d'une
semaine) a besoin pour avoir une brigade à programmer.

Deux brigades dans la même session : `BRIGADE` est celle que l'étape 1
génère ; `BRIGADE_TEMOIN`, jamais sélectionnée à la génération, reste
entièrement libre pour le contrôle formatif de l'étape 2 (voir
`donnees.py` — la génération remplit tout créneau libre de la semaine).

Session déjà en cours (`date_debut` dans le passé) et longue (`date_fin`
loin dans le futur) : la semaine que choisira l'opérateur à l'étape 1 et la
date de l'examen final à l'étape 9 doivent toutes deux tomber dans ses
bornes, quel que soit le jour où la démonstration est jouée."""

import datetime

from django.utils import timezone

from organisation.services.affectation import ServiceAffectation
from organisation.services.brigade import ServiceBrigade
from organisation.services.session import ServiceSession
from organisation.services.stagiaire import ServiceStagiaire
from planification.jeu_demonstration_j2.donnees import (
    BRIGADE,
    BRIGADE_TEMOIN,
    EFFECTIF_STAGIAIRES,
    EFFECTIF_TEMOIN,
    GRADE_STAGIAIRES,
    SESSION,
    UNITE_STAGIAIRES,
)

SEMAINES_DEBUT_AVANT_AUJOURDHUI = 4
SEMAINES_FIN_APRES_AUJOURDHUI = 30


def charger_organisation(agissant, formation, stdout):
    """Rend `(session, brigade, brigade_temoin)`."""
    aujourd_hui = timezone.localdate()
    session = ServiceSession.creer(
        agissant,
        {
            "formation": formation,
            "intitule": SESSION,
            "date_debut": aujourd_hui - datetime.timedelta(weeks=SEMAINES_DEBUT_AVANT_AUJOURDHUI),
            "date_fin": aujourd_hui + datetime.timedelta(weeks=SEMAINES_FIN_APRES_AUJOURDHUI),
            "effectif_attendu": EFFECTIF_STAGIAIRES + EFFECTIF_TEMOIN,
        },
    )
    brigade = ServiceBrigade.creer(
        agissant, session, {"designation": BRIGADE, "effectif_previsionnel": EFFECTIF_STAGIAIRES}
    )
    brigade_temoin = ServiceBrigade.creer(
        agissant,
        session,
        {"designation": BRIGADE_TEMOIN, "effectif_previsionnel": EFFECTIF_TEMOIN},
    )
    _affecter_stagiaires(agissant, session, brigade, "J2", EFFECTIF_STAGIAIRES)
    _affecter_stagiaires(agissant, session, brigade_temoin, "J2T", EFFECTIF_TEMOIN)
    stdout.write(f"  Session « {session} », deux brigades (« {brigade} », « {brigade_temoin} »).")
    return session, brigade, brigade_temoin


def _affecter_stagiaires(agissant, session, brigade, prefixe, effectif):
    for rang in range(1, effectif + 1):
        stagiaire = ServiceStagiaire.creer(
            agissant,
            session,
            {
                "matricule": f"{prefixe}-{rang:04d}",
                "nom": "Démonstration",
                "prenom": f"Stagiaire {rang}",
                "grade": GRADE_STAGIAIRES,
                "unite": UNITE_STAGIAIRES,
            },
        )
        ServiceAffectation.affecter(agissant, stagiaire, brigade)
