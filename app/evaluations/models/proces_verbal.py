"""Procès-verbaux de résultats — US-EVAL-07, RG-58, RG-59, CU-P6-07,
prompt 46, point 3.

Aucune règle métier ici : voir .claude/rules/modeles.md.
"""

from django.db import models

from evaluations.models.evaluation import Evaluation
from noyau.models import ModeleHorodate
from organisation.models import Session


class TypeProcesVerbal(models.TextChoices):
    FIN_DE_FORMATION = "fin_de_formation", "Fin de formation"
    EVALUATION = "evaluation", "Évaluation"


class ProcesVerbal(ModeleHorodate):
    """Document OFFICIEL : le PDF produit est CONSERVÉ (V2) — à la
    différence de la progression réalisée (US-SUI-06), qui se recalcule à
    chaque téléchargement, un procès-verbal ne doit jamais changer après
    coup, même si le gabarit est corrigé entre-temps. `PROTECT` partout :
    un procès-verbal est la trace d'une décision qui ne s'efface jamais
    silencieusement avec son origine (même motif que `Avenant`, D-237).

    Écarts avec CLS-05, consignés (docs/suivi/DECISIONS.md) :
    - le verrouillage (`Evaluation "0..*" -- "0..1" ProcesVerbal`) est
      porté ici en plusieurs-à-plusieurs (`evaluations_couvertes`), pas en
      clé étrangère simple — une évaluation peut être couverte par son
      propre procès-verbal puis par celui de fin de formation (V3).
    - `Evaluation.notesVerrouillees` (CLS-05) n'existe pas : le
      verrouillage est un prédicat CALCULÉ sur l'existence d'une ligne
      dans `evaluations_couvertes` (N7, D-270/D-273).
    - l'attribut `gabarit : texte` de CLS-05 n'existe pas : le mécanisme de
      gabarit administrable posé à US-SUI-06 (`GabaritDocument`) le
      remplace — un seul exemplaire par TYPE de document, jamais une copie
      par procès-verbal.
    """

    type = models.CharField(max_length=20, choices=TypeProcesVerbal.choices, verbose_name="type")
    session = models.ForeignKey(
        Session,
        on_delete=models.PROTECT,
        related_name="proces_verbaux",
        verbose_name="session",
    )
    evaluation = models.ForeignKey(
        Evaluation,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="proces_verbaux",
        verbose_name="évaluation",
    )
    evaluations_couvertes = models.ManyToManyField(
        Evaluation,
        related_name="proces_verbaux_verrouillants",
        db_table="evaluations_proces_verbal_couverture",
        verbose_name="évaluations couvertes",
    )
    numero = models.CharField(max_length=50, blank=True, default="", verbose_name="numéro")
    version = models.PositiveSmallIntegerField(default=1, verbose_name="version")
    fichier_pdf = models.BinaryField(verbose_name="document PDF")

    class Meta:
        db_table = "evaluations_proces_verbal"
        verbose_name = "procès-verbal"
        verbose_name_plural = "procès-verbaux"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(type__in=TypeProcesVerbal.values),
                name="ck_proces_verbal_type_connu",
            ),
            models.CheckConstraint(
                condition=(
                    (
                        models.Q(type=TypeProcesVerbal.EVALUATION)
                        & models.Q(evaluation__isnull=False)
                    )
                    | (
                        ~models.Q(type=TypeProcesVerbal.EVALUATION)
                        & models.Q(evaluation__isnull=True)
                    )
                ),
                name="ck_proces_verbal_evaluation_coherente",
            ),
            models.CheckConstraint(
                condition=models.Q(version__gt=0), name="ck_proces_verbal_version_positive"
            ),
            # Deux contraintes, pas une seule sur les quatre colonnes :
            # `evaluation` est NULL pour « fin de formation », et NULL
            # n'égale jamais NULL pour l'unicité SQL — une contrainte
            # unique qui l'inclurait ne contraindrait jamais ce type.
            models.UniqueConstraint(
                fields=["session", "version"],
                condition=models.Q(type=TypeProcesVerbal.FIN_DE_FORMATION),
                name="uq_proces_verbal_version_fin_formation",
            ),
            models.UniqueConstraint(
                fields=["evaluation", "version"],
                condition=models.Q(type=TypeProcesVerbal.EVALUATION),
                name="uq_proces_verbal_version_evaluation",
            ),
        ]

    def __str__(self):
        return f"Procès-verbal {self.get_type_display()} — {self.session} (v{self.version})"
