"""Instructeurs, leurs indisponibilités et leurs qualifications — CU-P4-01,
CU-P4-02, CU-P4-03.

Aucune règle métier ici : voir .claude/rules/modeles.md.
"""

from django.contrib.postgres.constraints import ExclusionConstraint
from django.contrib.postgres.fields import DateTimeRangeField, RangeBoundary, RangeOperators
from django.db import models
from django.utils import timezone

from noyau.models import ModeleArchivable, ModeleHorodate
from referentiel.models import Matiere


class _PeriodeTstz(models.Func):
    """`TSTZRANGE(debut, fin, '[)')` — borne inférieure incluse, supérieure
    exclue : deux périodes contiguës (la fin de l'une égale au début de
    l'autre) ne se chevauchent pas. Fonction nommée, jamais recopiée en
    ligne : c'est l'expression que `ExclusionConstraint` évalue pour RG-24.
    """

    function = "TSTZRANGE"
    output_field = DateTimeRangeField()


class Statut(models.TextChoices):
    """§ 3.2 du Prompt 12 : trois valeurs, et trois seulement."""

    MILITAIRE_DU_CENTRE = "militaire_du_centre", "Militaire du centre"
    VACATAIRE = "vacataire", "Vacataire"
    CIVIL = "civil", "Civil"


class Instructeur(ModeleHorodate, ModeleArchivable):
    """Un instructeur n'est pas un utilisateur du système (§ 3.1 du Prompt
    12, critères d'US-INS-03) : aucune clé étrangère vers `Utilisateur`,
    aucune saisie par l'instructeur lui-même.

    `matricule` est nul pour un vacataire ou un civil, obligatoire et unique
    pour un militaire du centre (§ 2 du Prompt 12, arbitrage validé) : voir
    `ck_instructeur_matricule_militaire` et `uq_instructeur_matricule` —
    PostgreSQL n'unicise jamais deux valeurs nulles entre elles, la
    contrainte simple suffit donc à laisser coexister plusieurs instructeurs
    sans matricule.
    """

    nom = models.CharField(max_length=150, verbose_name="nom")
    prenom = models.CharField(max_length=150, verbose_name="prénom")
    matricule = models.CharField(max_length=20, null=True, blank=True, verbose_name="matricule")
    grade = models.CharField(max_length=50, verbose_name="grade")
    specialite = models.CharField(max_length=150, verbose_name="spécialité")
    statut = models.CharField(max_length=20, choices=Statut.choices, verbose_name="statut")

    class Meta:
        db_table = "ressources_instructeur"
        verbose_name = "instructeur"
        verbose_name_plural = "instructeurs"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(statut__in=Statut.values), name="ck_instructeur_statut"
            ),
            models.UniqueConstraint(models.F("matricule"), name="uq_instructeur_matricule"),
            models.CheckConstraint(
                condition=~models.Q(statut=Statut.MILITAIRE_DU_CENTRE)
                | models.Q(matricule__isnull=False),
                name="ck_instructeur_matricule_militaire",
            ),
        ]

    def __str__(self):
        return f"{self.grade} {self.nom} {self.prenom}"


class IndisponibiliteInstructeur(ModeleHorodate):
    """Période où `instructeur` ne peut pas être affecté — CU-P4-03, RG-23,
    RG-24, Prompt 27.

    SAISIE DÉLÉGUÉE (RG-23) : l'instructeur n'a aucun accès au système,
    aucune relation ne le lie à `Utilisateur` (`ressources.tests.
    test_architecture` le vérifie explicitement). `cree_par`/`modifie_par`
    (`ModeleHorodate`) portent l'AGENT de la cellule planification qui
    saisit, jamais l'instructeur concerné — rien de spécial à coder, la
    classe de base porte déjà la règle.

    GRANULARITÉ HORAIRE (`DateTimeField`, pas `DateField`) : la fiche est
    explicite, une indisponibilité d'un après-midi doit coexister avec des
    séances du matin. `IndisponibiliteLieu` (US-PLAN-02) est déjà à cette
    granularité — aucune incohérence entre les deux modèles jumeaux.

    `motif` en texte libre, comme `IndisponibiliteLieu` : CLS-04 le dit
    explicitement (« motif : texte »), le diagramme de classes fait foi.

    Pas de mixin d'archivage : une indisponibilité passée est un fait
    historique, jamais réactivé — même raisonnement que sa jumelle.
    """

    instructeur = models.ForeignKey(
        Instructeur,
        on_delete=models.PROTECT,
        related_name="indisponibilites",
        verbose_name="instructeur",
    )
    debut = models.DateTimeField(verbose_name="début")
    fin = models.DateTimeField(verbose_name="fin")
    motif = models.TextField(verbose_name="motif")

    class Meta:
        db_table = "ressources_indisponibilite_instructeur"
        verbose_name = "indisponibilité d'instructeur"
        verbose_name_plural = "indisponibilités d'instructeur"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(fin__gt=models.F("debut")),
                name="ck_indisponibilite_instructeur_bornes",
            ),
            models.CheckConstraint(
                condition=~models.Q(motif=""), name="ck_indispo_instructeur_motif_non_vide"
            ),
            ExclusionConstraint(
                name="ex_indispo_instructeur_chevauchement",
                expressions=[
                    (_PeriodeTstz("debut", "fin", RangeBoundary()), RangeOperators.OVERLAPS),
                    ("instructeur", RangeOperators.EQUAL),
                ],
            ),
        ]

    def __str__(self):
        return f"{self.instructeur} — {self.debut:%d/%m/%Y %H:%M} → {self.fin:%d/%m/%Y %H:%M}"

    @property
    def est_passee(self):
        """Attribut dérivé, jamais stocké (.claude/rules/modeles.md) : à
        venir/en cours/passée se recalcule à la lecture, sur `timezone.now()`
        — distinction exigée à l'écran (§ 7, Prompt 27, critère 6)."""
        return self.fin <= timezone.now()

    @property
    def est_en_cours(self):
        return self.debut <= timezone.now() < self.fin


class Qualification(ModeleHorodate):
    """Associe un instructeur à une matière du **catalogue** — jamais à un
    élément du référentiel (§ 2 du Prompt 13) : un instructeur habilité pour
    une matière l'est indépendamment de la formation où elle est enseignée.
    Aucun niveau d'habilitation, aucune date de validité, aucun commentaire
    — le point de conception écarte explicitement toute anticipation.

    Pas de mixin d'archivage (§ 3.1) : un retrait est une suppression
    réelle, la seconde exception à la convention du patron après
    `ObjectifPedagogique` (D-37) — aucune séance programmée ne référence
    jamais la qualification elle-même, seulement l'instructeur et la
    matière, donc rien n'a besoin de la retrouver après coup.

    `matiere` en `PROTECT`, `instructeur` en `CASCADE` : une matière
    qualifiée ne peut plus être supprimée du catalogue (referme le second
    volet du report D-30, `docs/suivi/DECISIONS.md`) ; un instructeur
    supprimé — cas rare, l'archivage prévaut — emporte ses qualifications,
    qui n'ont pas de sens sans lui. `related_name="qualifications"` sur
    `matiere` : c'est par cette relation inverse que `referentiel` compte
    les instructeurs qualifiés sans jamais importer `ressources` (sens de
    dépendance interdit, voir `tests/architecture/test_couches.py`).
    """

    instructeur = models.ForeignKey(
        Instructeur,
        on_delete=models.CASCADE,
        related_name="qualifications",
        verbose_name="instructeur",
    )
    matiere = models.ForeignKey(
        Matiere,
        on_delete=models.PROTECT,
        related_name="qualifications",
        verbose_name="matière",
    )

    class Meta:
        db_table = "ressources_qualification"
        verbose_name = "qualification"
        verbose_name_plural = "qualifications"
        constraints = [
            models.UniqueConstraint(
                fields=["instructeur", "matiere"], name="uq_qualification_instructeur_matiere"
            ),
        ]

    def __str__(self):
        return f"{self.instructeur} — {self.matiere}"
