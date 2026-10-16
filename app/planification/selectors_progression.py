"""Progression réalisée hebdomadaire — US-SUI-06 (prompt 45, Temps 2).

R7 (même principe qu'US-SUI-01) : sept requêtes au total, jamais une par
brigade ni par matière — brigades, éléments de référentiel, programmé de la
semaine, dispensé, non-exécutions, avenants (une requête de plus, son
préchargement des lignes/brigades par `prefetch_related`).
"""

import dataclasses
import datetime

from django.utils import timezone

from organisation.models import Brigade
from planification.models import Avenant, NonExecution
from planification.services.contraintes import (
    volume_programme_de_la_semaine,
    volumes_realises_par_element_brigade,
)
from referentiel.models import ElementReferentiel


@dataclasses.dataclass(frozen=True)
class LigneProgression:
    """C1 : programmé de la semaine et dispensé, jamais stockés."""

    element_referentiel: object
    programme_semaine: float
    dispense: float


@dataclasses.dataclass(frozen=True)
class EcartProgression:
    """C2 : une non-exécution ou un avenant de la semaine, avec motif."""

    matiere: str
    libelle: str
    motif: str


@dataclasses.dataclass(frozen=True)
class GroupeBrigadeProgression:
    brigade: object
    lignes: list
    ecarts: list


def _fin_de_semaine(programme):
    lundi_suivant = programme.lundi_de_semaine + datetime.timedelta(weeks=1)
    return timezone.make_aware(datetime.datetime.combine(lundi_suivant, datetime.time.min))


def _ecarts_de_la_semaine(programme) -> dict:
    """P3 : une séance reportée dans la semaine se lit sur son avenant de
    nature « déplacement » — aucune entité de report. Deux requêtes, jamais
    une par brigade."""
    resultat: dict = {}
    non_executions = NonExecution.objects.filter(ligne__seance__programme=programme).select_related(
        "ligne__brigade", "ligne__seance__element_referentiel__matiere"
    )
    for non_execution in non_executions:
        ligne = non_execution.ligne
        resultat.setdefault(ligne.brigade_id, []).append(
            EcartProgression(
                matiere=str(ligne.seance.element_referentiel.matiere),
                libelle="Non-exécution",
                motif=non_execution.motif,
            )
        )
    avenants = (
        Avenant.objects.filter(seance__programme=programme)
        .select_related("seance__element_referentiel__matiere")
        .prefetch_related("seance__lignes__brigade")
    )
    for avenant in avenants:
        matiere = str(avenant.seance.element_referentiel.matiere)
        for ligne in avenant.seance.lignes.all():
            resultat.setdefault(ligne.brigade_id, []).append(
                EcartProgression(
                    matiere=matiere, libelle=avenant.get_nature_display(), motif=avenant.motif
                )
            )
    return resultat


def _elements_de_la_semaine(element_ids) -> dict:
    return {
        element.pk: element
        for element in ElementReferentiel.objects.filter(pk__in=element_ids).select_related(
            "matiere"
        )
    }


def _brigades_du_programme(programme):
    return (
        Brigade.objects.filter(lignes_programme__seance__programme=programme)
        .distinct()
        .select_related("session__formation__type_formation")
        .order_by("session__formation__type_formation__intitule", "designation")
    )


def _lignes_de_la_brigade(brigade, element_ids, elements, programme_par_cle, dispense_par_cle):
    return [
        LigneProgression(
            element_referentiel=elements[element_id],
            programme_semaine=programme_par_cle.get((element_id, brigade.pk), 0),
            dispense=dispense_par_cle.get((element_id, brigade.pk), 0),
        )
        for element_id in element_ids
        if (element_id, brigade.pk) in programme_par_cle
    ]


def progression_realisee(programme, instant_edition=None) -> dict:
    """P2 : T = fin de la semaine, ou l'instant de l'édition si celui-ci la
    précède — une séance pas encore terminée ne compte jamais au dispensé.
    Rend un dict `type_formation -> [GroupeBrigadeProgression, ...]`, dans
    l'ordre des brigades (P6 : groupées par type de formation, comme le
    programme)."""
    instant_edition = instant_edition or timezone.now()
    a_la_date = min(instant_edition, _fin_de_semaine(programme))

    programme_par_cle = volume_programme_de_la_semaine(programme)
    dispense_par_cle = volumes_realises_par_element_brigade(a_la_date, programme_id=programme.pk)
    ecarts_par_brigade = _ecarts_de_la_semaine(programme)

    element_ids = {element_id for element_id, _ in programme_par_cle}
    elements = _elements_de_la_semaine(element_ids)

    groupes: dict = {}
    for brigade in _brigades_du_programme(programme):
        groupes.setdefault(brigade.session.formation.type_formation, []).append(
            GroupeBrigadeProgression(
                brigade=brigade,
                lignes=_lignes_de_la_brigade(
                    brigade, element_ids, elements, programme_par_cle, dispense_par_cle
                ),
                ecarts=ecarts_par_brigade.get(brigade.pk, []),
            )
        )
    return groupes
