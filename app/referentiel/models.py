"""Référentiel de formation — CU-P2-01, CU-P2-02, CU-P2-03, CU-P2-04, CU-P2-05.

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


class Matiere(ModeleHorodate, ModeleArchivable):
    """Catalogue des matières — CU-P2-03, RG-05.

    Indépendant des formations à dessein (écart 1, Prompt 07 § 3) : aucune
    clé étrangère vers `Formation` ici, sous aucun prétexte — c'est le
    référentiel d'US-REF-03 qui établira le lien, en référençant la matière,
    jamais en recopiant son intitulé (§ 2 : sans quoi une modification ne se
    répercuterait jamais sur les formations qui l'utilisent).

    Ni catégorie de lieu (elle se déclare au rattachement, CU-P2-04) ni
    objectif pédagogique (entité propre, US-REF-05) : Prompt 07 § 3.
    """

    intitule = models.CharField(max_length=150, verbose_name="intitulé")
    code = models.CharField(max_length=20, blank=True, verbose_name="code")

    class Meta:
        db_table = "referentiel_matiere"
        verbose_name = "matière"
        verbose_name_plural = "matières"
        constraints = [
            models.UniqueConstraint(Upper("intitule"), name="uq_matiere_intitule"),
            models.UniqueConstraint(
                Upper("code"),
                condition=~models.Q(code=""),
                name="uq_matiere_code",
            ),
        ]

    def __str__(self):
        return self.intitule


class CategorieLieu(models.TextChoices):
    """§ 6.2 — libellés du centre (BNF-08), à afficher tels quels."""

    SALLE_ATTITREE = "salle_attitree", "Salle attitrée de la brigade"
    LIEU_PARTAGE = "lieu_partage", "Lieu partagé"
    AUCUN_LIEU = "aucun_lieu", "Aucun lieu requis"


class TypeLieuPartage(models.TextChoices):
    AMPHITHEATRE = "amphitheatre", "Amphithéâtre"
    LABORATOIRE = "laboratoire", "Laboratoire"
    SALLE_SPECIALISEE = "salle_specialisee", "Salle spécialisée"


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


class ElementReferentiel(ModeleHorodate):
    """Classe d'association entre `Formation` et `Matiere` — CU-P2-04,
    CU-P2-05, RG-05 à RG-08. Le pivot du référentiel : c'est cette classe,
    et jamais `Matiere` directement, que référenceront les séances
    programmées et le rapprochement prescrit/réalisé des sprints suivants.

    Clé primaire technique, pas composite (note d'implémentation, § 4.1) :
    quatre autres tables la référenceront à terme (prérequis, séance,
    évaluation, désignation de chef de module).

    Pas de `ModeleArchivable` : le retrait est une suppression protégée
    (RG-07), jamais un archivage — rien dans la fiche ne prévoit un
    « rattachement archivé ».

    Ne duplique aucun attribut de `Matiere` (Prompt 08, § 3.2) : le
    référentiel référence la matière, il ne la recopie jamais — c'est ce
    dont dépend le critère 6 d'US-REF-02 (une modification de la matière se
    répercute pour toutes les formations qui l'utilisent).
    """

    formation = models.ForeignKey(
        Formation,
        on_delete=models.CASCADE,
        related_name="elements_referentiel",
        verbose_name="formation",
    )
    matiere = models.ForeignKey(
        Matiere,
        on_delete=models.PROTECT,
        related_name="elements_referentiel",
        verbose_name="matière",
    )
    volume_horaire_prescrit = models.PositiveIntegerField(
        verbose_name="volume horaire prescrit (heures)", validators=[MinValueValidator(1)]
    )
    categorie_lieu = models.CharField(
        max_length=20, choices=CategorieLieu.choices, verbose_name="catégorie de lieu"
    )
    type_lieu_partage = models.CharField(
        max_length=20,
        choices=TypeLieuPartage.choices,
        null=True,
        blank=True,
        verbose_name="type de lieu partagé",
    )

    class Meta:
        db_table = "referentiel_element_referentiel"
        verbose_name = "élément de référentiel"
        verbose_name_plural = "éléments de référentiel"
        constraints = [
            models.UniqueConstraint(
                fields=["formation", "matiere"], name="uq_element_referentiel_formation_matiere"
            ),
            models.CheckConstraint(
                condition=models.Q(volume_horaire_prescrit__gt=0),
                name="ck_element_referentiel_volume_positif",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(
                        categorie_lieu=CategorieLieu.LIEU_PARTAGE, type_lieu_partage__isnull=False
                    )
                    | (
                        ~models.Q(categorie_lieu=CategorieLieu.LIEU_PARTAGE)
                        & models.Q(type_lieu_partage__isnull=True)
                    )
                ),
                name="ck_element_referentiel_type_lieu_coherent",
            ),
        ]

    def __str__(self):
        return f"{self.matiere} — {self.formation}"
