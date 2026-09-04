"""Ressources humaines et matérielles du centre — CU-P4-01, CU-P4-02.

Aucune règle métier ici : voir .claude/rules/modeles.md.
"""

from django.db import models

from noyau.models import ModeleArchivable, ModeleHorodate
from referentiel.models import Matiere


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
