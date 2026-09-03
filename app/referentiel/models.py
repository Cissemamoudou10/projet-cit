"""Référentiel de formation — CU-P2-01.

Aucune règle métier ici : voir .claude/rules/modeles.md.
"""

from django.db import models
from django.db.models.functions import Upper

from noyau.models import ModeleArchivable, ModeleHorodate


class TypeFormation(ModeleHorodate, ModeleArchivable):
    """Classe le public d'une formation — officiers, sous-officiers, CAT-2…
    Un intitulé, rien d'autre (Prompt 05, § 1).

    Unicité insensible à la casse (Prompt 05, § 5) : deux intitulés qui ne
    diffèrent que par la casse désignent le même public aux yeux d'un
    utilisateur — les laisser coexister ouvrirait la porte à des doublons
    accidentels indiscernables à l'écran. La contrainte porte sur
    `UPPER(intitule)`, pas sur une transformation de la valeur stockée :
    l'intitulé affiché garde la casse choisie à la création.
    """

    intitule = models.CharField(max_length=100, verbose_name="intitulé")

    class Meta:
        db_table = "referentiel_type_formation"
        verbose_name = "type de formation"
        verbose_name_plural = "types de formation"
        constraints = [
            models.UniqueConstraint(Upper("intitule"), name="uq_type_formation_intitule"),
        ]

    def __str__(self):
        return self.intitule
