"""Calendrier académique annuel — CU-P4-05, RG-28 à RG-30 bis, Prompt 28.

Aucune règle métier ici : voir .claude/rules/modeles.md. Le contrôle du
chevauchement (RG-29) est en couche services — voir
`ressources.services.periode_calendrier` — car il porte sur deux relations
multiples, qu'aucune contrainte SQL déclarative ne sait exprimer (§ 4,
Prompt 28).
"""

from django.db import models
from django.db.models.functions import Upper

from noyau.models import ModeleHorodate
from organisation.models import Brigade, Session


class EffetPeriode(models.TextChoices):
    """RG-29 : l'effet est DISSOCIÉ de la nature — chaque nature porte une
    valeur par défaut, surchargeable événement par événement (§ 3, Prompt 28).
    """

    BLOQUANT = "bloquant", "Bloquant"
    INFORMATIF = "informatif", "Informatif"


class NatureEvenement(ModeleHorodate):
    """Nature paramétrable d'un événement de calendrier — CLS-03 la marque
    `<<paramétrable>>` : c'est une TABLE avec son écran de gestion, pas une
    énumération, pour que le terrain ajoute une nature sans intervention sur
    le code (.claude/rules/modeles.md). Aucun mixin d'archivage : le
    diagramme ne porte pas d'attribut `archive` pour cette classe — une
    nature devenue obsolète est protégée de la suppression tant qu'une
    période l'utilise (`PeriodeCalendrier.nature`, `on_delete=PROTECT`),
    jamais archivée.
    """

    libelle = models.CharField(max_length=100, verbose_name="libellé")
    effet_par_defaut = models.CharField(
        max_length=20, choices=EffetPeriode.choices, verbose_name="effet par défaut"
    )

    class Meta:
        db_table = "ressources_nature_evenement"
        verbose_name = "nature d'événement"
        verbose_name_plural = "natures d'événement"
        constraints = [
            models.UniqueConstraint(Upper("libelle"), name="uq_nature_evenement_libelle"),
            models.CheckConstraint(
                condition=models.Q(effet_par_defaut__in=EffetPeriode.values),
                name="ck_nature_evenement_effet",
            ),
        ]

    def __str__(self):
        return self.libelle


class PeriodeCalendrier(ModeleHorodate):
    """Événement du calendrier académique annuel — CU-P4-05, RG-28, RG-30.

    GRANULARITÉ HORAIRE (RG-28, structurante) : « la journée n'est pas
    l'unité du calendrier » — `debut`/`fin` en `DateTimeField`, bornes
    semi-ouvertes `[début, fin)`, cohérentes avec `IndisponibiliteInstructeur`
    (US-INS-03, § 0.4 du Prompt 28) : deux périodes contiguës ne se
    chevauchent pas.

    AUCUN CHAMP `portee` (RG-30) : le diagramme le marque `/portee`, dérivé
    des deux ensembles de cibles, jamais stocké — un attribut renseigné
    indépendamment finirait par contredire des cibles vides. Voir la
    propriété `portee` ci-dessous, calculée à la lecture.

    `sessions`/`brigades` — relations multiples et INDÉPENDANTES (RG-30),
    par des tables d'association dédiées (`PeriodeCalendrierSession`,
    `PeriodeCalendrierBrigade`) : un `ManyToManyField` nu ne permet aucun
    `on_delete` sur ses lignes, alors que § 4 du Prompt 28 exige qu'une
    session ou une brigade ciblée ne puisse jamais disparaître sous une
    période existante (silencieusement élargie vers « centre entier »).
    Le `PROTECT` posé sur chaque table d'association suffit : Django lève
    `ProtectedError` à la suppression d'une `Session`/`Brigade` ciblée,
    sans le moindre import de `ressources` depuis `organisation` — même
    mécanisme que `SalleAttitree`, déjà anticipé par
    `ServiceBrigade.supprimer` (US-SES-02).

    `effet` STOCKÉ, pas recalculé : RG-29 le dissocie de la nature, il doit
    donc pouvoir diverger de `nature.effet_par_defaut` après coup.
    """

    nature = models.ForeignKey(
        NatureEvenement,
        on_delete=models.PROTECT,
        related_name="periodes",
        verbose_name="nature",
    )
    intitule = models.CharField(max_length=200, verbose_name="intitulé")
    debut = models.DateTimeField(verbose_name="début")
    fin = models.DateTimeField(verbose_name="fin")
    effet = models.CharField(max_length=20, choices=EffetPeriode.choices, verbose_name="effet")
    sessions = models.ManyToManyField(
        Session,
        through="PeriodeCalendrierSession",
        related_name="periodes_calendrier",
        blank=True,
        verbose_name="sessions ciblées",
    )
    brigades = models.ManyToManyField(
        Brigade,
        through="PeriodeCalendrierBrigade",
        related_name="periodes_calendrier",
        blank=True,
        verbose_name="brigades ciblées",
    )

    class Meta:
        db_table = "ressources_periode_calendrier"
        verbose_name = "période de calendrier"
        verbose_name_plural = "périodes de calendrier"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(fin__gt=models.F("debut")),
                name="ck_periode_calendrier_bornes",
            ),
            models.CheckConstraint(
                condition=models.Q(effet__in=EffetPeriode.values),
                name="ck_periode_calendrier_effet",
            ),
        ]

    def __str__(self):
        return f"{self.intitule} — {self.debut:%d/%m/%Y %H:%M} → {self.fin:%d/%m/%Y %H:%M}"

    @property
    def portee(self):
        """Dérivée, jamais stockée (RG-30) : les deux ensembles vides valent
        centre entier, sinon l'union des cibles déclarées, en toutes lettres
        (§ 13, Prompt 28) — jamais réduite à une seule des trois valeurs de
        l'énumération `Portee` du diagramme, qui ne prévoit pas le cas mixte
        (§ 4, session ET brigade simultanément, accepté par A2/C3)."""
        return decrire_cibles(list(self.sessions.all()), list(self.brigades.all()))


def decrire_cibles(sessions, brigades):
    """Même formule pour la portée d'une période (`PeriodeCalendrier.portee`)
    et pour nommer l'intersection dans un avertissement de chevauchement
    (`ressources.services.periode_calendrier`) — une seule implantation,
    jamais recopiée (.claude/rules/python.md)."""
    if not sessions and not brigades:
        return "Centre entier"
    fragments = []
    if sessions:
        mot = "Session" if len(sessions) == 1 else "Sessions"
        fragments.append(f"{mot} " + ", ".join(str(s) for s in sessions))
    if brigades:
        mot = "brigade" if len(brigades) == 1 else "brigades"
        fragments.append(f"{mot} " + ", ".join(str(b) for b in brigades))
    return " et ".join(fragments)


class PeriodeCalendrierSession(models.Model):
    """Table d'association `PeriodeCalendrier`—`Session` (§ 4, Prompt 28).
    `PROTECT` sur `session` : voir la docstring de `PeriodeCalendrier`."""

    periode = models.ForeignKey(PeriodeCalendrier, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.PROTECT)

    class Meta:
        db_table = "ressources_periode_calendrier_session"
        constraints = [
            models.UniqueConstraint(
                fields=["periode", "session"], name="uq_periode_calendrier_session"
            ),
        ]

    def __str__(self):
        return f"{self.periode} — {self.session}"


class PeriodeCalendrierBrigade(models.Model):
    """Table d'association `PeriodeCalendrier`—`Brigade` (§ 4, Prompt 28).
    `PROTECT` sur `brigade` : voir la docstring de `PeriodeCalendrier`."""

    periode = models.ForeignKey(PeriodeCalendrier, on_delete=models.CASCADE)
    brigade = models.ForeignKey(Brigade, on_delete=models.PROTECT)

    class Meta:
        db_table = "ressources_periode_calendrier_brigade"
        constraints = [
            models.UniqueConstraint(
                fields=["periode", "brigade"], name="uq_periode_calendrier_brigade"
            ),
        ]

    def __str__(self):
        return f"{self.periode} — {self.brigade}"
