"""Option `--pagination` — Prompt 34, § 6. Vingt-cinq sessions sur une
formation DÉDIÉE (`F5`), pour R2-SES01-17 seul : séparé du chargement par
défaut, sur sa propre formation, pour n'apparaître dans AUCUN autre contrôle.
"""

import datetime

from django.utils import timezone

from evaluations.jeu_recette.donnees import (
    CODE_FORMATION_PAGINATION,
    LIBELLE_FORMATION_PAGINATION,
    MATIERE_FORMATION_PAGINATION,
    NOMBRE_SESSIONS_PAGINATION,
    SPECIALITE_PAR_DEFAUT,
    VOLUME_FORMATION_PAGINATION,
)
from organisation.services.session import ServiceSession
from referentiel.models import CategorieLieu
from referentiel.services.formation import ServiceFormation
from referentiel.services.referentiel import ServiceReferentiel

DUREE_SEMAINES_SESSION_PAGINATION = 10
DELAI_AVANT_SESSION_PAGINATION_JOURS = 30
EFFECTIF_ATTENDU_PAGINATION = 20


def _formation_pagination(agissant, types, matieres):
    formation = ServiceFormation.creer(
        agissant,
        {
            "intitule": LIBELLE_FORMATION_PAGINATION,
            "specialite": SPECIALITE_PAR_DEFAUT,
            "duree_semaines": DUREE_SEMAINES_SESSION_PAGINATION,
            "type_formation": next(iter(types.values())),
        },
    )
    ServiceReferentiel.rattacher(
        agissant,
        formation,
        matieres[MATIERE_FORMATION_PAGINATION],
        {
            "volume_horaire_prescrit": VOLUME_FORMATION_PAGINATION,
            "categorie_lieu": CategorieLieu.AUCUN_LIEU,
            "type_lieu_partage": None,
        },
    )
    return formation


def charger_pagination(agissant, types, matieres, stdout):
    formation = _formation_pagination(agissant, types, matieres)
    date_debut = timezone.now().date() + datetime.timedelta(
        days=DELAI_AVANT_SESSION_PAGINATION_JOURS
    )
    date_fin = date_debut + datetime.timedelta(weeks=DUREE_SEMAINES_SESSION_PAGINATION)
    for indice in range(1, NOMBRE_SESSIONS_PAGINATION + 1):
        ServiceSession.creer(
            agissant,
            {
                "intitule": f"{CODE_FORMATION_PAGINATION} — Session pagination {indice:02d}",
                "formation": formation,
                "date_debut": date_debut,
                "date_fin": date_fin,
                "effectif_attendu": EFFECTIF_ATTENDU_PAGINATION,
            },
        )
    stdout.write(
        f"  Formation {CODE_FORMATION_PAGINATION} créée, "
        f"{NOMBRE_SESSIONS_PAGINATION} sessions de pagination ouvertes."
    )
