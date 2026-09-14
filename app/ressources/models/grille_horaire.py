"""Grilles horaires et créneaux types — CU-P4-07, RG-62 à RG-64, Prompt 29.

Aucune règle métier ici : voir .claude/rules/modeles.md. Le non-recouvrement
des créneaux d'un même jour (E1) est en couche services — voir
ressources.services.grille_horaire, et docs/suivi/DECISIONS.md pour pourquoi
`btree_gist` ne s'applique pas ici comme aux trois autres modèles de période
du projet.
"""

from django.conf import settings
from django.db import models
from django.db.models.functions import Upper

from noyau.models import ModeleArchivable, ModeleHorodate


class JourSemaine(models.TextChoices):
    LUNDI = "lundi", "Lundi"
    MARDI = "mardi", "Mardi"
    MERCREDI = "mercredi", "Mercredi"
    JEUDI = "jeudi", "Jeudi"
    VENDREDI = "vendredi", "Vendredi"
    SAMEDI = "samedi", "Samedi"
    DIMANCHE = "dimanche", "Dimanche"


class GrilleHoraire(ModeleHorodate, ModeleArchivable):
    """Squelette de la semaine, sans matière ni instructeur — CLS-03.

    « CLÔTURER » UNE GRILLE EN SERVICE (critère 5, Prompt 29 § 3), C'EST
    L'ARCHIVER : `ModeleArchivable`, hérité, jamais un troisième état
    inventé — écart avec CLS-03, qui ne porte pas l'archivage sur cette
    classe ; le backlog l'exige en substance. Voir docs/suivi/DECISIONS.md.

    `activee_par` : facultative, `PROTECT` — CLS-03, « Utilisateur 0..1 --
    0..* GrilleHoraire : activée par ».
    """

    intitule = models.CharField(max_length=100, verbose_name="intitulé")
    active = models.BooleanField(default=False, verbose_name="active")
    date_activation = models.DateTimeField(null=True, blank=True, verbose_name="date d'activation")
    activee_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="grilles_activees",
        verbose_name="activée par",
    )

    class Meta:
        db_table = "ressources_grille_horaire"
        verbose_name = "grille horaire"
        verbose_name_plural = "grilles horaires"
        constraints = [
            models.UniqueConstraint(Upper("intitule"), name="uq_grille_horaire_intitule"),
            models.UniqueConstraint(
                fields=["active"],
                condition=models.Q(active=True),
                name="uq_grille_horaire_une_seule_active",
            ),
            models.CheckConstraint(
                condition=(
                    models.Q(active=False)
                    | (
                        models.Q(active=True)
                        & models.Q(date_activation__isnull=False)
                        & models.Q(activee_par__isnull=False)
                    )
                ),
                name="ck_grille_horaire_activation_coherente",
            ),
        ]

    def __str__(self):
        return self.intitule


class CreneauType(ModeleHorodate):
    """Case du squelette — AUCUNE DATE (§ 1, Prompt 29) : un jour de
    semaine, un rang, une heure de début et une heure de fin, répétés
    chaque semaine. Si un attribut de date apparaît ici, la conception est
    perdue.

    `on_delete=CASCADE` sur `grille`, À L'INVERSE de la règle générale du
    projet (`PROTECT` par défaut, .claude/rules/modeles.md) : un créneau
    type n'a aucune existence hors de sa grille — composition stricte,
    exactement le cas que la règle réserve à `CASCADE`.
    """

    grille = models.ForeignKey(
        GrilleHoraire, on_delete=models.CASCADE, related_name="creneaux", verbose_name="grille"
    )
    jour_semaine = models.CharField(
        max_length=10, choices=JourSemaine.choices, verbose_name="jour de semaine"
    )
    ordre = models.PositiveSmallIntegerField(verbose_name="rang")
    heure_debut = models.TimeField(verbose_name="heure de début")
    heure_fin = models.TimeField(verbose_name="heure de fin")

    class Meta:
        db_table = "ressources_creneau_type"
        verbose_name = "créneau type"
        verbose_name_plural = "créneaux types"
        constraints = [
            models.UniqueConstraint(
                fields=["grille", "jour_semaine", "ordre"],
                name="uq_creneau_type_grille_jour_ordre",
            ),
            models.CheckConstraint(
                condition=models.Q(heure_fin__gt=models.F("heure_debut")),
                name="ck_creneau_type_heures",
            ),
            models.CheckConstraint(
                condition=models.Q(jour_semaine__in=JourSemaine.values),
                name="ck_creneau_type_jour_semaine",
            ),
        ]

    def __str__(self):
        return (
            f"{self.grille} — {self.get_jour_semaine_display()} "
            f"{self.heure_debut:%H:%M}–{self.heure_fin:%H:%M}"
        )
