"""Ouverture des sessions de formation — CU-P3-01, RG-11, RG-65.

Aucune règle métier ici : voir .claude/rules/modeles.md.
"""

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models.functions import Upper

from noyau.models import ModeleHorodate
from referentiel.models import Formation


class EtatSession(models.TextChoices):
    OUVERTE = "ouverte", "Ouverte"
    CLOTUREE = "cloturee", "Clôturée"


class Session(ModeleHorodate):
    """Ouverture d'une session sur une formation — CU-P3-01.

    Pas `ModeleArchivable` : `etat` porte un état métier (ouverte/clôturée),
    pas un indicateur d'archivage — même raisonnement que D-37 et D-49, voir
    docs/suivi/DECISIONS.md.

    Ne recopie JAMAIS le référentiel de la formation (Prompt 20, § 2) :
    aucun champ, aucune table, aucune méthode dénormalisée. Le critère 2
    (« le référentiel de la formation est repris automatiquement ») est
    satisfait par construction, et seulement par construction, en lisant le
    référentiel via la relation `formation` — voir
    `organisation.services.session.ServiceSession.referentiel_resume`.
    Une copie invaliderait silencieusement le critère 6 d'US-REF-02 (D-29,
    transposé).

    `formation` en `PROTECT` : referme le critère 4 d'US-REF-01 (D-23) sans
    aucune ligne de code dans `referentiel` — une formation portant une
    session, ouverte ou clôturée, ne peut être supprimée.

    Aucune contrainte de non-chevauchement de périodes, ni en base ni en
    services : deux sessions d'une même formation peuvent se chevaucher
    (enchaînement A1 de CU-P3-01), le partage des ressources s'arbitrant à
    la planification.
    """

    formation = models.ForeignKey(
        Formation,
        on_delete=models.PROTECT,
        related_name="sessions",
        verbose_name="formation",
    )
    intitule = models.CharField(max_length=150, verbose_name="intitulé")
    date_debut = models.DateField(verbose_name="date de début")
    date_fin = models.DateField(verbose_name="date de fin")
    effectif_attendu = models.PositiveIntegerField(
        verbose_name="effectif attendu", validators=[MinValueValidator(1)]
    )
    etat = models.CharField(
        max_length=20,
        choices=EtatSession.choices,
        default=EtatSession.OUVERTE,
        verbose_name="état",
    )
    date_cloture = models.DateField(null=True, blank=True, verbose_name="date de clôture")

    class Meta:
        db_table = "organisation_session"
        verbose_name = "session"
        verbose_name_plural = "sessions"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(date_fin__gt=models.F("date_debut")), name="ck_session_dates"
            ),
            models.CheckConstraint(
                condition=models.Q(effectif_attendu__gt=0), name="ck_session_effectif"
            ),
            models.CheckConstraint(
                condition=models.Q(etat__in=EtatSession.values), name="ck_session_etat"
            ),
            models.UniqueConstraint(
                models.F("formation"), Upper("intitule"), name="uq_session_formation_intitule"
            ),
        ]

    def __str__(self):
        return f"{self.intitule} — {self.formation}"


class Brigade(ModeleHorodate):
    """Brigade constituée au sein d'une session — CU-P3-02, RG-12.

    Saisie manuelle uniquement : RG-12 interdit tout calcul de composition
    — voir `organisation.services.brigade`. Pas de `ModeleArchivable` : une
    brigade se supprime ou se conserve, elle ne s'archive pas (Prompt 21,
    § 2).

    `session` en `PROTECT`, pas `CASCADE` : `.claude/rules/modeles.md` ne
    réserve `CASCADE` qu'à la composition stricte. Supprimer une session
    emporterait ses brigades, donc à terme les affectations de stagiaires,
    les programmes et les notes qui en dépendent — le refus explicite avec
    énumération des opposants est ce qu'exige E3 de la fiche générique.
    Conséquence assumée : une session constituée devient non supprimable
    tant que ses brigades existent.

    Aucun champ `effectif_reel` : attribut dérivé de CLS-00 (§ 9 du diagramme
    de classes — affectations ouvertes de stagiaires non radiés), non
    calculable avant `Stagiaire` (US-SES-05).
    """

    session = models.ForeignKey(
        Session,
        on_delete=models.PROTECT,
        related_name="brigades",
        verbose_name="session",
    )
    designation = models.CharField(max_length=50, verbose_name="désignation")
    effectif_previsionnel = models.PositiveIntegerField(
        verbose_name="effectif prévisionnel", validators=[MinValueValidator(1)]
    )

    class Meta:
        db_table = "organisation_brigade"
        verbose_name = "brigade"
        verbose_name_plural = "brigades"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(effectif_previsionnel__gt=0), name="ck_brigade_effectif"
            ),
            models.UniqueConstraint(
                models.F("session"), Upper("designation"), name="uq_brigade_session_designation"
            ),
        ]

    def __str__(self):
        return f"{self.designation} — {self.session}"
