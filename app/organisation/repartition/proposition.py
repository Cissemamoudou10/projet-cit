"""Proposition de répartition des stagiaires dans les brigades — CU-P3-06,
§ 2 et § 5, Prompt 25. TEMPS 1 : rien n'est écrit en base ici.

Remplissage SÉQUENTIEL jusqu'à l'effectif déclaré de chaque brigade — le
critère 1 du backlog l'exige contre la répartition ÉQUILIBRÉE de la fiche
CU-P3-06, qui recalculerait la composition des brigades, ce que RG-12
interdit explicitement au système. Voir docs/suivi/DECISIONS.md.

Ordre déterministe : brigades par désignation, stagiaires par nom — une
proposition qui change à chaque rafraîchissement serait inexploitable (A4).
"""

import json
from dataclasses import dataclass

from django.db.models import Exists, OuterRef

from organisation.models import AffectationBrigade


@dataclass(frozen=True)
class PropositionRepartition:
    affectations: tuple[tuple[int, int], ...]  # (stagiaire_id, brigade_id)
    non_affectes: tuple[int, ...]  # stagiaire_id sans brigade proposée


def stagiaires_sans_affectation_ouverte(session):
    """A5 : radiés exclus. A6 : déjà affectés (dans cette session) exclus.

    `Exists()`, jamais `.exclude(affectations__date_fin__isnull=True)` : ce
    dernier passe par un LEFT OUTER JOIN, dont le remplissage à `NULL` pour
    un stagiaire SANS AUCUNE affectation satisfait à tort `date_fin IS NULL`
    et l'exclurait lui aussi — piège Django classique sur une relation
    inverse à plusieurs valeurs."""
    ouverte = AffectationBrigade.objects.filter(stagiaire=OuterRef("pk"), date_fin__isnull=True)
    return session.stagiaires.filter(radie=False).exclude(Exists(ouverte))


def proposer(session) -> PropositionRepartition:
    stagiaires = list(stagiaires_sans_affectation_ouverte(session).order_by("nom", "prenom"))
    brigades = list(session.brigades.order_by("designation"))
    affectations = []
    index = 0
    for brigade in brigades:
        for _ in range(brigade.effectif_previsionnel):
            if index >= len(stagiaires):
                break
            affectations.append((stagiaires[index].pk, brigade.pk))
            index += 1
    non_affectes = tuple(stagiaire.pk for stagiaire in stagiaires[index:])
    return PropositionRepartition(affectations=tuple(affectations), non_affectes=non_affectes)


def ajuster(proposition, stagiaire_id, brigade_id):
    """Déplace un stagiaire vers `brigade_id`, ou le sort de toute brigade si
    `brigade_id` est `None` — critère 2, un formulaire à la fois (pas de
    glisser-déposer, § 7)."""
    affectations = [(s, b) for s, b in proposition.affectations if s != stagiaire_id]
    non_affectes = [s for s in proposition.non_affectes if s != stagiaire_id]
    if brigade_id is None:
        non_affectes.append(stagiaire_id)
    else:
        affectations.append((stagiaire_id, brigade_id))
    return PropositionRepartition(
        affectations=tuple(affectations), non_affectes=tuple(non_affectes)
    )


def serialiser(proposition: PropositionRepartition) -> bytes:
    structure = {
        "affectations": list(proposition.affectations),
        "non_affectes": list(proposition.non_affectes),
    }
    return json.dumps(structure).encode("utf-8")


def deserialiser(donnees: bytes) -> PropositionRepartition:
    structure = json.loads(donnees)
    return PropositionRepartition(
        affectations=tuple(tuple(paire) for paire in structure["affectations"]),
        non_affectes=tuple(structure["non_affectes"]),
    )
