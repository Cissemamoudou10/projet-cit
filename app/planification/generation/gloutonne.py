"""`StrategieGloutonne` — § 4, Prompt 31. Une candidate à la fois, AUCUN
RETOUR EN ARRIÈRE (§ 4, INTERDITS) : place la première candidate acceptée
par `ServiceContraintes`, ne révise jamais un placement antérieur — limite
assumée, que `StrategieSolveur` (US-PLAN-08) viendra peut-être corriger.

Classe sous 200 lignes (I4) : construction des candidates déléguée à
`candidats.py`, tri à `tri.py`, cette classe ne porte que la boucle de
placement et l'ordonnancement des cases.
"""

import time

from noyau.intervalles import se_recouvrent
from planification.generation.candidats import candidates_pour_case
from planification.generation.strategie import (
    NonPlacement,
    Placement,
    ResultatStrategie,
    Strategie,
    TentativeRefusee,
)
from planification.generation.tri import cle_tri_candidate, poids_matiere
from planification.services.contraintes import ServiceContraintes

SENTINELLE_BRIGADE_SANS_MATIERE = (10**6, 10**6, 10**6, 10**6)


def _motif_sans_candidate(case, matieres):
    if not matieres:
        return f"Aucune matière programmable pour {case.brigade} (voir les matières écartées)."
    return (
        f"Aucun instructeur qualifié ni lieu compatible disponible pour une matière "
        f"programmable de {case.brigade} sur ce créneau."
    )


def _lieu_libre(lieu, debut, fin, contexte, provisoires):
    for seance in contexte.seances_existantes:
        if seance.lieu_id == lieu.pk and se_recouvrent(debut, fin, seance.debut, seance.fin):
            return False
    for candidate in provisoires:
        if candidate.lieu is not None and candidate.lieu.pk == lieu.pk:
            if se_recouvrent(debut, fin, candidate.debut, candidate.fin):
                return False
    return True


def _tentative_lieu_occupe(tentative):
    if tentative.candidate.lieu is None:
        return False
    return any(v["code"] == "RG-37" and "occupé" in v["message"] for v in tentative.violations)


def _proposer_alternative(tentatives, cases, contexte, provisoires):
    """E4, § 6, Prompt 31 : UNE PROPOSITION, jamais une action — un autre
    créneau de la semaine où le lieu contesté est libre, ou le report de la
    matière s'il ne l'est nulle part."""
    tentative = next((t for t in tentatives if _tentative_lieu_occupe(t)), None)
    if tentative is None:
        return ""
    lieu, refuse = tentative.candidate.lieu, tentative.candidate
    for autre_case in cases:
        if autre_case.debut == refuse.debut and autre_case.brigade.pk == refuse.brigade.pk:
            continue
        if _lieu_libre(lieu, autre_case.debut, autre_case.fin, contexte, provisoires):
            return f"{lieu} est libre le {autre_case.debut:%d/%m %H:%M}, ou reportez la matière."
    return f"{lieu} n'est libre à aucun autre créneau de la semaine — envisagez un report."


class StrategieGloutonne(Strategie):
    def __init__(self, preparation):
        self._preparation = preparation
        self._matieres_par_brigade = preparation.matieres_par_brigade
        self._cases_de_la_semaine = ()  # posé par `generer` — nécessaire à E4

    def generer(self, contexte, cases, borne_temps_secondes):
        depart = time.monotonic()
        placements, non_placements, provisoires = [], [], []
        interrompue = False
        cases_ordonnees = self._ordonner_cases(cases, contexte)
        self._cases_de_la_semaine = cases_ordonnees
        for case in cases_ordonnees:
            if time.monotonic() - depart > borne_temps_secondes:
                interrompue = True
                break
            resultat = self._pourvoir_case(case, contexte, provisoires)
            if isinstance(resultat, Placement):
                placements.append(resultat)
                provisoires.extend(resultat.candidates)
            else:
                non_placements.append(resultat)
        return ResultatStrategie(
            placements=placements,
            non_placements=non_placements,
            matieres_ecartees=self._preparation.matieres_ecartees,
            interrompue_par_la_borne=interrompue,
        )

    def _pourvoir_case(self, case, contexte, provisoires):
        matieres = self._matieres_par_brigade.get(case.brigade.pk, [])
        candidates = candidates_pour_case(case, matieres, contexte, self._preparation)
        if not candidates:
            return NonPlacement(
                case=case, tentatives=(), motif_sans_candidate=_motif_sans_candidate(case, matieres)
            )
        tentatives = []
        for candidate in self._trier_candidates(case, matieres, candidates, contexte, provisoires):
            verdict = ServiceContraintes.verifier(candidate, contexte, tuple(provisoires))
            if verdict.accepte:
                return Placement(case=case, candidates=(candidate,))
            tentatives.append(TentativeRefusee(candidate=candidate, violations=verdict.violations))
        proposition = _proposer_alternative(
            tentatives, self._cases_de_la_semaine, contexte, provisoires
        )
        return NonPlacement(case=case, tentatives=tuple(tentatives), proposition=proposition)

    def _trier_candidates(self, case, matieres, candidates, contexte, provisoires):
        poids_par_element = {
            element.pk: poids_matiere(element, case.brigade, case, contexte, self._preparation)
            for element in matieres
        }
        return sorted(
            candidates,
            key=lambda c: cle_tri_candidate(
                c, poids_par_element[c.element_referentiel.pk], contexte, provisoires
            ),
        )

    def _ordonner_cases(self, cases, contexte):
        cases_stables = sorted(cases, key=lambda c: (c.debut, c.brigade.pk))
        poids_brigade = {}
        for case in cases_stables:
            if case.brigade.pk not in poids_brigade:
                poids_brigade[case.brigade.pk] = self._poids_brigade(case, contexte)
        return sorted(cases_stables, key=lambda c: (poids_brigade[c.brigade.pk], c.debut, c.brigade.pk))

    def _poids_brigade(self, case, contexte):
        matieres = self._matieres_par_brigade.get(case.brigade.pk, [])
        if not matieres:
            return SENTINELLE_BRIGADE_SANS_MATIERE
        return min(
            poids_matiere(element, case.brigade, case, contexte, self._preparation)
            for element in matieres
        )
