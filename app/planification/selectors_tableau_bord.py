"""Tableau de bord des formations — US-SUI-03, BF-SUI-03 (prompt 48).

B2 : taux d'avancement = réalisé cumulé ÷ prescrit cumulé, sur la même
fonction du réalisé qu'US-SUI-01 (`volumes_realises_par_element_brigade`,
`services/contraintes.py`) — aucun second calcul. B3 : achevée / en cours /
non commencée reprend la règle du prérequis achevé de RG-39
(`services/regles_volume.py::_verifier_prerequis`) : réalisé ≥ prescrit,
0 < réalisé < prescrit (bornes exclues), réalisé nul. B4 : le nombre
d'alertes réutilise `alertes()` de la story 1 (US-SUI-02), un seul appel,
jamais un par brigade.
"""

import dataclasses

from django.utils import timezone

from organisation.models import Brigade, EtatSession
from planification.selectors_alerte_ecart import alertes
from planification.services.contraintes import volumes_realises_par_element_brigade
from referentiel.models import ElementReferentiel


@dataclasses.dataclass(frozen=True)
class BrigadeTableauBord:
    """Jamais stockée (`.claude/rules/modeles.md`) : recalculée à chaque
    consultation de l'écran."""

    brigade: object
    taux_avancement: float
    nombre_achevees: int
    nombre_en_cours: int
    nombre_non_commencees: int
    nombre_alertes: int


def _brigades_en_cours(a_la_date):
    """B1 : brigade d'une session NON CLÔTURÉE dont la période couvre la
    date du jour."""
    return list(
        Brigade.objects.select_related("session__formation__type_formation")
        .exclude(session__etat=EtatSession.CLOTUREE)
        .filter(session__date_debut__lte=a_la_date, session__date_fin__gte=a_la_date)
        .order_by("session__intitule", "designation")
    )


def _elements_par_formation(formation_ids):
    elements_par_formation: dict = {}
    for element in ElementReferentiel.objects.filter(formation_id__in=formation_ids):
        elements_par_formation.setdefault(element.formation_id, []).append(element)
    return elements_par_formation


def _comptes_alertes_par_brigade(brigades):
    """B4 : un seul appel à `alertes()`, filtré en mémoire sur les brigades
    du tableau de bord — jamais un appel par brigade."""
    ids_affiches = {brigade.pk for brigade in brigades}
    return {
        groupe.brigade.pk: len(groupe.lignes) for groupe in alertes() if groupe.brigade.pk in ids_affiches
    }


def _ligne_de_brigade(brigade, elements, realise_par_cle, nombre_alertes):
    achevees = en_cours = non_commencees = 0
    prescrit_cumule = realise_cumule = 0.0
    for element in elements:
        realise = realise_par_cle.get((element.pk, brigade.pk), 0)
        prescrit_cumule += element.volume_horaire_prescrit
        realise_cumule += realise
        if realise >= element.volume_horaire_prescrit:
            achevees += 1
        elif realise > 0:
            en_cours += 1
        else:
            non_commencees += 1
    taux = (realise_cumule / prescrit_cumule * 100) if prescrit_cumule else 0.0
    return BrigadeTableauBord(
        brigade=brigade,
        taux_avancement=taux,
        nombre_achevees=achevees,
        nombre_en_cours=en_cours,
        nombre_non_commencees=non_commencees,
        nombre_alertes=nombre_alertes,
    )


def tableau_de_bord(a_la_date=None) -> list:
    """B5 : groupé par session, puis par type de formation — comme au
    programme (`selectors.grille_consultation`) ; une session ne porte
    qu'une seule formation, donc un seul type, c'est le même regroupement
    que la session elle-même."""
    a_la_date = a_la_date or timezone.localdate()
    brigades = _brigades_en_cours(a_la_date)
    if not brigades:
        return []
    brigade_ids = [brigade.pk for brigade in brigades]
    elements_par_formation = _elements_par_formation({b.session.formation_id for b in brigades})
    realise_par_cle = volumes_realises_par_element_brigade(a_la_date, brigade_ids=brigade_ids)
    alertes_par_brigade = _comptes_alertes_par_brigade(brigades)

    brigades_par_session: dict = {}
    for brigade in brigades:
        brigades_par_session.setdefault(brigade.session_id, []).append(brigade)

    groupes = []
    for brigades_de_la_session in brigades_par_session.values():
        session = brigades_de_la_session[0].session
        lignes = [
            _ligne_de_brigade(
                brigade,
                elements_par_formation.get(brigade.session.formation_id, []),
                realise_par_cle,
                alertes_par_brigade.get(brigade.pk, 0),
            )
            for brigade in brigades_de_la_session
        ]
        groupes.append(
            {
                "session": session,
                "type_formation": session.formation.type_formation,
                "lignes": lignes,
            }
        )
    return groupes
