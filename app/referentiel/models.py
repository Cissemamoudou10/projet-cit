"""Référentiel de formation — CU-P2-01, CU-P2-02.

Aucune règle métier ici : voir .claude/rules/modeles.md.
"""

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F
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


class Formation(ModeleHorodate, ModeleArchivable):
    """Catalogue des formations dispensées par le centre — CU-P2-02.

    Porte le référentiel (matières, volumes) à partir d'US-REF-03 — RG-05 :
    aucune matière n'est jamais rattachée directement à une brigade ni à une
    session, seulement à la formation. Cette classe n'en pose que le
    porteur, le référentiel lui-même restant vide jusqu'à cette story.

    L'unité de `duree_semaines` — la semaine — n'est écrite dans aucun
    livrable ; Prompt 06, § 2.2, la propose et la consigne comme question
    ouverte pour le terrain dans docs/suivi/DECISIONS.md.
    """

    intitule = models.CharField(max_length=150, verbose_name="intitulé")
    specialite = models.CharField(max_length=150, verbose_name="spécialité")
    duree_semaines = models.PositiveSmallIntegerField(
        verbose_name="durée (semaines)", validators=[MinValueValidator(1)]
    )
    type_formation = models.ForeignKey(
        TypeFormation,
        on_delete=models.PROTECT,
        related_name="formations",
        verbose_name="type de formation",
    )

    class Meta:
        db_table = "referentiel_formation"
        verbose_name = "formation"
        verbose_name_plural = "formations"
        constraints = [
            models.UniqueConstraint(
                F("type_formation"), Upper("intitule"), name="uq_formation_type_intitule"
            ),
            models.CheckConstraint(
                condition=models.Q(duree_semaines__gt=0), name="ck_formation_duree_positive"
            ),
        ]

    def __str__(self):
        return self.intitule
