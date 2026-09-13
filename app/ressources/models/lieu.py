"""Lieux, leurs indisponibilités et les salles attitrées aux brigades —
CU-P4-06, CU-P3-03.

Aucune règle métier ici : voir .claude/rules/modeles.md.
"""

from django.db import models

from noyau.models import ModeleArchivable, ModeleHorodate
from organisation.models import Brigade


class CategorieLieu(models.TextChoices):
    """§ 2 du Prompt 14 : deux valeurs, propriété physique du lieu — à ne pas
    confondre avec la catégorie de lieu du référentiel (`referentiel.models.
    CategorieLieu`, trois valeurs), qui exprime une exigence de matière. Le
    diagramme de classes portait encore une énumération unique à trois
    valeurs pour les deux notions ; corrigé par le terrain, voir
    docs/suivi/DECISIONS.md.
    """

    SALLE_ATTITREE = "salle_attitree", "Salle attitrable"
    LIEU_PARTAGE = "lieu_partage", "Lieu partagé"


class TypeLieuPartage(models.TextChoices):
    """Propre à `Lieu` — mêmes libellés que `referentiel.models.
    TypeLieuPartage` par coïncidence du vocabulaire du centre, sans lien
    entre les deux classes (§ 4, arbitrage du Prompt 14) : le rapprochement
    de RG-37 comparera des valeurs, jamais des classes.
    """

    AMPHITHEATRE = "amphitheatre", "Amphithéâtre"
    LABORATOIRE = "laboratoire", "Laboratoire"
    SALLE_SPECIALISEE = "salle_specialisee", "Salle spécialisée"


class Lieu(ModeleHorodate, ModeleArchivable):
    """Catalogue des lieux — CU-P4-06. `categorie` distingue une salle
    **attitrable** (elle *peut* être attitrée à une brigade, pas encore : ce
    sera US-SES-02, sprint 2) d'un lieu partagé, arbitré séance par séance.
    Aucune troisième valeur : une matière sans exigence de lieu ne consomme
    aucune ressource physique, voir § 2 du Prompt 14.
    """

    intitule = models.CharField(max_length=150, verbose_name="intitulé")
    capacite = models.PositiveIntegerField(verbose_name="capacité")
    categorie = models.CharField(
        max_length=20, choices=CategorieLieu.choices, verbose_name="catégorie"
    )
    type_partage = models.CharField(
        max_length=20,
        choices=TypeLieuPartage.choices,
        null=True,
        blank=True,
        verbose_name="type de lieu partagé",
    )

    class Meta:
        db_table = "ressources_lieu"
        verbose_name = "lieu"
        verbose_name_plural = "lieux"
        constraints = [
            models.UniqueConstraint(models.F("intitule"), name="uq_lieu_intitule"),
            models.CheckConstraint(
                condition=models.Q(capacite__gt=0), name="ck_lieu_capacite_positive"
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(categorie=CategorieLieu.LIEU_PARTAGE, type_partage__isnull=False)
                    | (
                        ~models.Q(categorie=CategorieLieu.LIEU_PARTAGE)
                        & models.Q(type_partage__isnull=True)
                    )
                ),
                name="ck_lieu_type_partage_coherent",
            ),
        ]

    def __str__(self):
        return self.intitule


class IndisponibiliteLieu(ModeleHorodate):
    """Période où `lieu` ne peut pas être occupé — § 3.1 du Prompt 14.
    Granularité horaire, comme pour l'instructeur. Pas de mixin
    d'archivage : une indisponibilité passée est un fait historique, jamais
    réactivé.
    """

    lieu = models.ForeignKey(
        Lieu, on_delete=models.CASCADE, related_name="indisponibilites", verbose_name="lieu"
    )
    debut = models.DateTimeField(verbose_name="début")
    fin = models.DateTimeField(verbose_name="fin")
    motif = models.TextField(verbose_name="motif")

    class Meta:
        db_table = "ressources_indisponibilite_lieu"
        verbose_name = "indisponibilité de lieu"
        verbose_name_plural = "indisponibilités de lieu"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(fin__gt=models.F("debut")), name="ck_indispo_lieu_periode"
            ),
            models.CheckConstraint(
                condition=~models.Q(motif=""), name="ck_indispo_lieu_motif_non_vide"
            ),
        ]

    def __str__(self):
        return f"{self.lieu} — {self.debut:%d/%m/%Y %H:%M} → {self.fin:%d/%m/%Y %H:%M}"


class SalleAttitree(ModeleHorodate):
    """Salle attitrée d'une brigade — CU-P3-03, RG-13, RG-14.

    Vit dans `ressources`, pas `organisation` (arbitrage § 0.1, Prompt 22,
    D-85) : l'acteur en écriture est la cellule planification, détentrice du
    catalogue des lieux, jamais de la brigade elle-même. `related_name=
    "salle_attitree"` permet à `organisation` de lire cette relation par
    l'inverse, sans jamais importer `ressources` — méthode D-52.

    `OneToOneField`, pas une clé étrangère simple : une brigade a AU PLUS une
    salle attitrée (`uq_salle_attitree_brigade`, généré par le champ lui-même).

    `PROTECT` des deux côtés : sur `lieu`, referme le volet brigade de D-54
    (« un lieu affecté à une brigade ne peut être supprimé ») ; sur
    `brigade`, une brigade dotée d'une salle ne se supprime pas en cascade
    silencieuse — c'est un refus explicite avec énumération (E3 générique).

    PAS d'historisation, à la différence d'`AffectationBrigade` (US-SES-06,
    RG-20) : RG-20 exige de dater les changements de brigade d'un stagiaire,
    RG-14 n'exige que la journalisation du changement de salle (A2) — le
    journal immuable suffit, une table d'historique ajouterait une structure
    que rien n'exige ici.

    PAS de dénormalisation de la période de la session, même pour rendre
    RG-14 exprimable en contrainte d'exclusion en base : même raisonnement
    que la note d'implémentation § 5.5 — une redondance à maintenir, qui
    divergerait à la première modification des dates d'une session.
    """

    brigade = models.OneToOneField(
        Brigade,
        on_delete=models.PROTECT,
        related_name="salle_attitree",
        verbose_name="brigade",
    )
    lieu = models.ForeignKey(
        Lieu,
        on_delete=models.PROTECT,
        related_name="brigades_attitrees",
        verbose_name="lieu",
    )

    class Meta:
        db_table = "ressources_salle_attitree"
        verbose_name = "salle attitrée"
        verbose_name_plural = "salles attitrées"

    def __str__(self):
        return f"{self.lieu} — {self.brigade}"

    @property
    def ecart_capacite(self):
        """Écart entre la capacité du lieu et l'effectif prévisionnel de la
        brigade, lisible depuis `organisation` par `brigade.salle_attitree.
        ecart_capacite`, sans le moindre `import ressources` (§ 4, Prompt 22).
        Non recalculé si l'effectif change après l'attribution : `organisation`
        ne peut pas rappeler `ServiceSalleAttitree` (sens de dépendance
        interdit) — l'écart se constate à la lecture, jamais par un refus au
        moment où l'effectif change. Limite consignée dans DECISIONS.md."""
        return self.lieu.capacite - self.brigade.effectif_previsionnel
