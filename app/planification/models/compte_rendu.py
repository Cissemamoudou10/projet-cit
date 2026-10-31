"""Compte rendu de la dernière génération d'un programme — correction de
NC R00-GEN-03 (évolution du prompt 53, Temps 3).

Aucune règle métier ici : voir .claude/rules/modeles.md.
"""

from django.db import models

from noyau.models import ModeleHorodate
from planification.models.programme import ProgrammeHebdomadaire


class CompteRenduGeneration(ModeleHorodate):
    """La dernière génération SEULEMENT (`OneToOneField`, écrasé à chaque
    nouvelle génération) — exception assumée à l'interdit des attributs
    dérivés : les motifs de non-placement dépendent des disponibilités
    d'instructeurs et de lieux AU MOMENT de la génération, qui ont changé
    dès la consultation suivante — ce n'est pas une grandeur recalculable,
    c'est la trace figée d'un acte passé (voir docs/suivi/DECISIONS.md).

    `resume` : un seul `JSONField` condensé (séances placées/non placées
    regroupées par motif, brigades traitées) — même patron qu'`EntreeJournal.
    valeur_avant`/`valeur_apres` (`administration/models.py`), jamais de
    tables relationnelles pour un condensé qui n'est ni filtré ni trié en
    SQL, seulement affiché. `programme` en `CASCADE` : le compte rendu n'a
    aucun sens sans le programme qu'il documente, et sa suppression
    (évolution du prompt 53, Temps 2) doit l'emporter avec lui.
    """

    programme = models.OneToOneField(
        ProgrammeHebdomadaire,
        on_delete=models.CASCADE,
        related_name="compte_rendu_generation",
        verbose_name="programme",
    )
    resume = models.JSONField(verbose_name="résumé condensé")

    class Meta:
        db_table = "planification_compte_rendu_generation"
        verbose_name = "compte rendu de génération"
        verbose_name_plural = "comptes rendus de génération"

    def __str__(self):
        return f"Compte rendu de génération — {self.programme}"
