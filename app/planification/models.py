"""Programme hebdomadaire, séances et lignes de programme — CU-P5-01,
CU-P5-02, RG-31 à RG-40. Paquetage P5.

Ces trois modèles se posent à US-PLAN-04 (charge déplacée depuis US-PLAN-03,
voir docs/suivi/DECISIONS.md) : le contrôleur de contraintes dures ne peut
rien vérifier sans eux.

Aucune règle métier ici : voir .claude/rules/modeles.md.
"""

import datetime

from django.conf import settings
from django.db import models
from django.db.models.functions import Cast

from noyau.models import ModeleHorodate
from organisation.models import Brigade
from referentiel.models import ElementReferentiel
from ressources.models import CreneauType, Instructeur, Lieu


class EtatProgramme(models.TextChoices):
    """CLS-04 — cinq états. Les transitions vivent dans
    `planification.services.circuit` (ETA-01, US-VAL-03) : seul ce service
    affecte `etat`. La base ne vérifie que la cohérence des faits attachés à
    chaque état (voir `Meta.constraints`), jamais les transitions, qui
    exigeraient l'ancien état."""

    BROUILLON = "brouillon", "Brouillon"
    SOUMIS = "soumis", "Soumis"
    VALIDE = "valide", "Validé"
    REJETE = "rejete", "Rejeté"
    AFFICHE = "affiche", "Affiché"


class ProgrammeHebdomadaire(ModeleHorodate):
    """Programme d'une semaine — RG-33 bis : « un seul programme par
    semaine pour le centre », jamais un programme par brigade. Les champs
    de validation/signature/affichage sont tous facultatifs et jamais
    renseignés par cette story — US-VAL-03, sprint 3, les remplira.
    """

    lundi_de_semaine = models.DateField(verbose_name="lundi de la semaine")
    etat = models.CharField(
        max_length=20,
        choices=EtatProgramme.choices,
        default=EtatProgramme.BROUILLON,
        verbose_name="état",
    )
    date_soumission = models.DateTimeField(null=True, blank=True, verbose_name="date de soumission")
    date_validation = models.DateTimeField(null=True, blank=True, verbose_name="date de validation")
    motif_rejet = models.TextField(null=True, blank=True, verbose_name="motif de rejet")
    date_signature = models.DateField(null=True, blank=True, verbose_name="date de signature")
    signataire = models.CharField(max_length=150, null=True, blank=True, verbose_name="signataire")
    date_affichage = models.DateTimeField(null=True, blank=True, verbose_name="date d'affichage")
    valide_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="programmes_valides",
        verbose_name="validé par",
    )

    class Meta:
        db_table = "planification_programme_hebdomadaire"
        verbose_name = "programme hebdomadaire"
        verbose_name_plural = "programmes hebdomadaires"
        constraints = [
            models.UniqueConstraint(
                fields=["lundi_de_semaine"], name="uq_programme_hebdomadaire_lundi"
            ),
            models.CheckConstraint(
                condition=models.Q(etat__in=EtatProgramme.values), name="ck_programme_etat"
            ),
            models.CheckConstraint(
                condition=models.Q(lundi_de_semaine__iso_week_day=1),
                name="ck_programme_lundi_est_un_lundi",
            ),
            # ETA-01 § 4.3 — les sept contraintes d'état de US-VAL-03.
            models.CheckConstraint(
                condition=~models.Q(etat=EtatProgramme.REJETE)
                | (models.Q(motif_rejet__isnull=False) & models.Q(motif_rejet__regex=r"\S")),
                name="ck_programme_rejet_motive",
            ),
            models.CheckConstraint(
                condition=~models.Q(etat__in=[EtatProgramme.SOUMIS, EtatProgramme.VALIDE,
                                              EtatProgramme.AFFICHE])
                | models.Q(motif_rejet__isnull=True)
                | models.Q(motif_rejet__regex=r"^\s*$"),
                name="ck_programme_motif_hors_circuit",
            ),
            models.CheckConstraint(
                condition=~models.Q(etat__in=[EtatProgramme.SOUMIS, EtatProgramme.VALIDE,
                                              EtatProgramme.REJETE, EtatProgramme.AFFICHE])
                | models.Q(date_soumission__isnull=False),
                name="ck_programme_soumission_datee",
            ),
            models.CheckConstraint(
                condition=~models.Q(etat__in=[EtatProgramme.VALIDE, EtatProgramme.AFFICHE])
                | models.Q(valide_par__isnull=False, date_validation__isnull=False),
                name="ck_programme_validation_nominative",
            ),
            models.CheckConstraint(
                condition=models.Q(date_signature__isnull=True, signataire__isnull=True)
                | models.Q(date_signature__isnull=False, signataire__isnull=False),
                name="ck_programme_signature_complete",
            ),
            models.CheckConstraint(
                condition=models.Q(date_signature__isnull=True)
                | models.Q(
                    date_validation__isnull=False,
                    date_signature__gte=Cast("date_validation", models.DateField()),
                ),
                name="ck_programme_signature_sur_validation",
            ),
            models.CheckConstraint(
                condition=~models.Q(etat=EtatProgramme.AFFICHE)
                | models.Q(
                    date_signature__isnull=False,
                    signataire__isnull=False,
                    date_affichage__isnull=False,
                ),
                name="ck_programme_affichage_signe",
            ),
        ]

    def __str__(self):
        return f"Semaine du {self.lundi_de_semaine:%d/%m/%Y}"


class Seance(ModeleHorodate):
    """Case remplie du programme — porte ses heures RÉELLES, jamais
    déduites du créneau type (RG-64) : une séance peut couvrir plusieurs
    créneaux consécutifs, être placée hors grille, et survivre sans
    changement à un changement de grille active.

    `programme` en `CASCADE` : composition stricte, une séance n'existe pas
    hors de son programme — même dérogation motivée qu'à US-PLAN-12 pour
    `CreneauType` vers `GrilleHoraire` (docs/suivi/DECISIONS.md).

    `instructeur`/`lieu` en `PROTECT` : referment respectivement D-45 et le
    volet séance de D-54 (docs/suivi/DECISIONS.md). `creneau_type` en
    `SET_NULL`, conformément à `.claude/rules/modeles.md` (« séance vers
    créneau type ») ET à RG-64, qui exige que la référence reste facultative.
    """

    programme = models.ForeignKey(
        ProgrammeHebdomadaire,
        on_delete=models.CASCADE,
        related_name="seances",
        verbose_name="programme",
    )
    element_referentiel = models.ForeignKey(
        ElementReferentiel,
        on_delete=models.PROTECT,
        related_name="seances",
        verbose_name="élément de référentiel",
    )
    instructeur = models.ForeignKey(
        Instructeur,
        on_delete=models.PROTECT,
        related_name="seances",
        verbose_name="instructeur",
    )
    lieu = models.ForeignKey(
        Lieu,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="seances",
        verbose_name="lieu",
    )
    creneau_type = models.ForeignKey(
        CreneauType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="seances",
        verbose_name="créneau type d'origine",
    )
    debut = models.DateTimeField(verbose_name="début")
    fin = models.DateTimeField(verbose_name="fin")
    verrouillee = models.BooleanField(default=False, verbose_name="verrouillée")

    class Meta:
        db_table = "planification_seance"
        verbose_name = "séance"
        verbose_name_plural = "séances"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(fin__gt=models.F("debut")), name="ck_seance_bornes"
            ),
        ]
        indexes = [
            # .claude/rules/migrations.md, « Index de performance » : la
            # génération (US-PLAN-03) lit toutes les séances de la semaine,
            # BNF-04 borne cette lecture à cinq minutes. `idx_seance_element`
            # et `idx_ligne_brigade` du même tableau ne sont PAS repris ici :
            # une clé étrangère simple porte déjà un index automatique en
            # Django, un second index nommé sur la même colonne serait un
            # doublon pur.
            models.Index(fields=["debut", "fin"], name="idx_seance_debut_fin"),
            models.Index(fields=["instructeur", "debut"], name="idx_seance_instructeur_debut"),
            models.Index(fields=["lieu", "debut"], name="idx_seance_lieu_debut"),
        ]

    def __str__(self):
        return f"{self.element_referentiel} — {self.debut:%d/%m/%Y %H:%M}"

    @property
    def duree_heures(self):
        """Dérivé, jamais stocké (.claude/rules/modeles.md)."""
        return (self.fin - self.debut) / datetime.timedelta(hours=1)

    @property
    def est_regroupee(self):
        """Vrai si plus d'une ligne de programme — plusieurs brigades
        voient la même séance (RG-32)."""
        return self.lignes.count() > 1


class LigneProgramme(ModeleHorodate):
    """Une ligne par brigade sur une séance — RG-32, structurante : « le
    programme porte une ligne par brigade, y compris lorsque plusieurs
    brigades partagent la même séance ». La structure du regroupement
    existe dès ce modèle, même si le cas d'utilisation qui l'exploite
    (US-PLAN-06) n'arrive qu'au sprint 3.
    """

    seance = models.ForeignKey(
        Seance, on_delete=models.CASCADE, related_name="lignes", verbose_name="séance"
    )
    brigade = models.ForeignKey(
        Brigade, on_delete=models.PROTECT, related_name="lignes_programme", verbose_name="brigade"
    )

    class Meta:
        db_table = "planification_ligne_programme"
        verbose_name = "ligne de programme"
        verbose_name_plural = "lignes de programme"
        constraints = [
            models.UniqueConstraint(
                fields=["seance", "brigade"], name="uq_ligne_programme_seance_brigade"
            ),
        ]

    def __str__(self):
        return f"{self.brigade} — {self.seance}"

    @property
    def volume_cumule(self):
        """Dérivé, jamais stocké : volume dispensé à cette brigade pour
        cette matière, à la date de cette séance — somme des durées des
        séances de même élément de référentiel vues par cette brigade,
        jusqu'à la date de celle-ci incluse (§ « /volumeCumule », CLS-04).
        """
        total = datetime.timedelta()
        for ligne in LigneProgramme.objects.filter(
            brigade=self.brigade,
            seance__element_referentiel=self.seance.element_referentiel,
            seance__debut__lte=self.seance.debut,
        ).select_related("seance"):
            total += ligne.seance.fin - ligne.seance.debut
        return total / datetime.timedelta(hours=1)
