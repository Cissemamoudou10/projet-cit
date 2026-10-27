"""Contexte partagé des chargeurs de l'état `complet` — Prompt 51, Temps 2.
Un seul objet, plutôt que reporter sur chaque fonction la dizaine de valeurs
(agissants, brigades, lieux, instructeurs, éléments de référentiel…) dont la
plupart des étapes de § 2.4-2.6 ont besoin — `.claude/rules/python.md`,
§ Taille, « cinq paramètres, au-delà regrouper dans un objet »."""

import dataclasses


@dataclasses.dataclass(frozen=True)
class ContexteComplet:
    agissant_plan: object
    agissant_ped: object
    agissant_examens: object
    brigades: dict
    lieux: dict
    instructeurs: dict
    elements_f6: dict
    element_m4_socle: object
    date_reference: object
    graine: int
    stdout: object

    @property
    def exp1(self):
        return self.brigades["EXP1"]

    @property
    def exp2(self):
        return self.brigades["EXP2"]

    @property
    def cdp1(self):
        return self.brigades["CDP1"]

    @property
    def toutes_brigades(self):
        return [self.exp1, self.exp2, self.cdp1]
