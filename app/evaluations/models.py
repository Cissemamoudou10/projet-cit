"""Évaluations — CU-P6-01, RG-48, RG-52, RG-52 bis, CLS-05, Prompt 35.

Aucune règle métier ici : voir .claude/rules/modeles.md.
"""

from django.db import models
from django.utils import timezone

from noyau.models import ModeleHorodate
from organisation.models import Brigade, Session
from planification.models import Seance
from referentiel.models import ElementReferentiel


class TypeEvaluation(models.TextChoices):
    """RG-48 : deux valeurs, et deux seulement — le backlog v9 en propose
    trois par endroits (critères contradictoires, corrigés par le terrain du
    25 août) ; CU-P6-01 et BF-EVAL-01 n'en retiennent que deux (D-174 et
    suivantes, docs/suivi/DECISIONS.md)."""

    FORMATIVE = "formative", "Formative"
    CERTIFICATIVE = "certificative", "Certificative"


class Evaluation(ModeleHorodate):
    """Le périmètre (A1, D-175) n'est PAS stocké : il se déduit de celui des
    deux rattachements — `session` ou `brigade` — qui est renseigné,
    exactement un des deux (`ck_evaluation_perimetre_exclusif`). Idem pour
    `date` (A2, D-176) : une formative future/présente lit sa date sur
    `seance`, jamais recopiée — `date` n'est renseignée que sans séance
    (certificative, ou formative déclarée après coup avec motif).
    """

    element_referentiel = models.ForeignKey(
        ElementReferentiel,
        on_delete=models.PROTECT,
        related_name="evaluations",
        verbose_name="élément de référentiel",
    )
    session = models.ForeignKey(
        Session,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="evaluations",
        verbose_name="session",
    )
    brigade = models.ForeignKey(
        Brigade,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="evaluations",
        verbose_name="brigade",
    )
    type = models.CharField(max_length=20, choices=TypeEvaluation.choices, verbose_name="type")
    date = models.DateField(null=True, blank=True, verbose_name="date")
    seance = models.OneToOneField(
        Seance,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="evaluation",
        verbose_name="séance",
    )
    motif_date_passee = models.TextField(
        blank=True, default="", verbose_name="motif de la date passée"
    )

    class Meta:
        db_table = "evaluations_evaluation"
        verbose_name = "évaluation"
        verbose_name_plural = "évaluations"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(type__in=TypeEvaluation.values),
                name="ck_evaluation_type_connu",
            ),
            models.CheckConstraint(
                condition=(
                    (models.Q(session__isnull=False) & models.Q(brigade__isnull=True))
                    | (models.Q(session__isnull=True) & models.Q(brigade__isnull=False))
                ),
                name="ck_evaluation_perimetre_exclusif",
            ),
            models.CheckConstraint(
                condition=(
                    (models.Q(date__isnull=False) & models.Q(seance__isnull=True))
                    | (models.Q(date__isnull=True) & models.Q(seance__isnull=False))
                ),
                name="ck_evaluation_date_ou_seance",
            ),
            models.CheckConstraint(
                condition=(
                    ~models.Q(type=TypeEvaluation.CERTIFICATIVE) | models.Q(seance__isnull=True)
                ),
                name="ck_evaluation_certificative_sans_seance",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(motif_date_passee="")
                    | (models.Q(type=TypeEvaluation.FORMATIVE) & models.Q(seance__isnull=True))
                ),
                name="ck_evaluation_motif_formative",
            ),
        ]

    def __str__(self):
        return f"{self.element_referentiel} — {self.get_type_display()}"

    @property
    def perimetre(self):
        """A1 : propriété calculée, jamais stockée — `session` ou `brigade`,
        celui des deux qui est renseigné."""
        return self.session or self.brigade

    @property
    def est_formative(self):
        return self.type == TypeEvaluation.FORMATIVE

    @property
    def est_certificative(self):
        return self.type == TypeEvaluation.CERTIFICATIVE

    @property
    def date_echue(self):
        """A6, Prompt 36 : un examen déjà tenu ne change plus de date."""
        return bool(self.date) and self.date < timezone.localdate()
