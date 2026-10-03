"""Évaluations — CU-P6-01, RG-48, RG-52, RG-52 bis, CLS-05, Prompt 35.

Aucune règle métier ici : voir .claude/rules/modeles.md.
"""

from django.db import models
from django.db.models import F
from django.db.models.functions import Upper
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


class Sujet(ModeleHorodate):
    """US-EVAL-03. A1, CLS-05 : seule une RÉFÉRENCE est stockée — jamais le
    sujet lui-même, qui reste sur papier hors système. `CASCADE` : composition
    stricte vers `Evaluation` (`.claude/rules/modeles.md`), un sujet n'a pas
    de sens sans son évaluation — attention toutefois à ne jamais offrir la
    suppression d'une évaluation tant que US-PLAN-05 (D-181) ne l'a pas
    arbitrée.

    Qui a retenu, quand (C3) : jamais de colonne ici (A4) — le journal
    (patron D-132) porte l'auteur et l'horodatage de la sélection, seul
    historique, complet dès le premier changement (C5)."""

    evaluation = models.ForeignKey(
        Evaluation,
        on_delete=models.CASCADE,
        related_name="sujets",
        verbose_name="évaluation",
    )
    rang = models.PositiveSmallIntegerField(verbose_name="rang")
    reference = models.CharField(max_length=200, verbose_name="référence")
    date_depot = models.DateField(verbose_name="date de dépôt")
    retenu = models.BooleanField(default=False, verbose_name="retenu")

    class Meta:
        db_table = "evaluations_sujet"
        verbose_name = "sujet"
        verbose_name_plural = "sujets"
        constraints = [
            models.CheckConstraint(condition=models.Q(rang__in=[1, 2]), name="ck_sujet_rang"),
            models.UniqueConstraint(fields=["evaluation", "rang"], name="uq_sujet_evaluation_rang"),
            models.UniqueConstraint(
                fields=["evaluation"],
                condition=models.Q(retenu=True),
                name="uq_sujet_un_seul_retenu",
            ),
            models.CheckConstraint(
                condition=models.Q(reference__regex=r"\S"),
                name="ck_sujet_reference_non_vide",
            ),
            models.UniqueConstraint(F("evaluation"), Upper("reference"), name="uq_sujet_reference"),
        ]

    def __str__(self):
        """A8 : jamais la référence — une trace ou un message d'erreur ne
        doit pas divulguer ce que le système ne stocke que pour la cellule
        examens."""
        return f"{self.evaluation} — sujet n° {self.rang}"
