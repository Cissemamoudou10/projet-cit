"""Interface de stratégie de génération — § 3, Prompt 31.

UNE ABSTRACTION ICI, AUCUNE AU PROMPT 27 (§ 3, à consigner tel quel dans
docs/suivi/DECISIONS.md) : là-bas, trois cas se ressemblaient sans qu'on
sache s'ils évolueraient ensemble — on n'abstrait pas sur une ressemblance.
Ici, la seconde implantation (`StrategieSolveur`, US-PLAN-08) est DÉJÀ
spécifiée — CU-P5-06 est formellement « extension de CU-P5-01 » — et la
comparaison des deux sur les mêmes données est un livrable attendu du
mémoire : on abstrait sur une variation connue.

La stratégie REÇOIT le contexte et les cases à pourvoir, RETOURNE des
placements retenus et des non-placements motivés. Elle N'ÉCRIT RIEN — c'est
`ServiceGeneration` qui écrit, par `ServiceEcritureSeance` — et n'évalue
JAMAIS elle-même une contrainte dure (C6, § 4) : toute décision passe par
`ServiceContraintes.verifier`.
"""

import abc
import dataclasses


@dataclasses.dataclass(frozen=True)
class Case:
    """Un créneau à pourvoir pour une brigade — projection d'un
    `CreneauType` de la grille active sur une date de la semaine, déjà
    purgée des créneaux bloqués par le calendrier (§ 4, étapes 1-2)."""

    brigade: object
    debut: object
    fin: object


@dataclasses.dataclass(frozen=True)
class TentativeRefusee:
    """Une candidate essayée pour une case et refusée — conservée pour le
    compte rendu détaillé (E3 : motif nominatif par instructeur)."""

    candidate: object
    violations: list


@dataclasses.dataclass(frozen=True)
class Placement:
    case: Case
    candidates: tuple


@dataclasses.dataclass(frozen=True)
class NonPlacement:
    case: Case
    tentatives: tuple
    motif_sans_candidate: str = ""
    proposition: str = ""


@dataclasses.dataclass(frozen=True)
class MatiereEcartee:
    """Critère 3 : une matière écartée D'EMBLÉE (§ 4, étape 3), avant même
    la premère case essayée — jamais une case non pourvue parmi d'autres."""

    brigade: object
    element: object
    motif: str


@dataclasses.dataclass(frozen=True)
class ResultatStrategie:
    placements: list
    non_placements: list
    matieres_ecartees: list
    interrompue_par_la_borne: bool = False


class Strategie(abc.ABC):
    """`generer` ne connaît jamais `ServiceEcritureSeance` ni aucun modèle
    Django en écriture — seulement `Contexte` (lecture) et
    `ServiceContraintes.verifier` (décision)."""

    @abc.abstractmethod
    def generer(self, contexte, cases, borne_temps_secondes) -> ResultatStrategie: ...
