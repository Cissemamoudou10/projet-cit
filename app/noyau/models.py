"""Classe de base d'horodatage — BNF-14.

Aucune entité métier dans cette application : voir docs/conception/
15-dossier-architecture.md §3.3.
"""

from django.conf import settings
from django.db import models


class ModeleHorodate(models.Model):
    """Abstraite : n'engendre aucune table, aucune migration.

    L'auteur est renseigné par la couche services, jamais par un signal —
    voir noyau/services/base.py. Impérativement `settings.AUTH_USER_MODEL`,
    jamais un import direct de `administration.models.Utilisateur` : cet
    import inverserait le sens des couches, noyau ne dépendant de rien.

    `cree_par`/`modifie_par` portent `blank=True` en plus de `null=True` :
    ce sont deux préoccupations distinctes, la première pour la base, la
    seconde pour la validation de formulaire (`full_clean`). Ces deux champs
    ne sont jamais saisis par un formulaire, toujours posés après coup par
    `noyau.services.base.ServiceBase` — sans `blank=True`,
    `noyau.services.gestion.ServiceGestion._valider` (qui appelle
    `full_clean` avant l'écriture, pour E1) les traiterait comme obligatoires
    et refuserait toute création, quel que soit le champ réellement saisi.
    Vérifié réellement : `blank` ne touche pas la base, aucune migration
    n'en résulte pour les modèles déjà déployés.
    """

    cree_le = models.DateTimeField(auto_now_add=True, verbose_name="créé le")
    modifie_le = models.DateTimeField(auto_now=True, verbose_name="modifié le")
    cree_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="+",
        verbose_name="créé par",
    )
    modifie_par = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="+",
        verbose_name="modifié par",
    )

    class Meta:
        abstract = True


class ModeleArchivable(models.Model):
    """Abstraite — patron de gestion, Prompt 05, § 2.3.

    L'archivage remplace la suppression dès qu'un élément est référencé par
    une donnée historique : il disparaît des listes de sélection mais reste
    consultable et référencé. La suppression physique n'est offerte que pour
    un élément jamais utilisé — `noyau.services.gestion.ServiceGestion`
    s'appuie sur `on_delete=PROTECT` pour le garantir, pas sur ce mixin.
    """

    archive = models.BooleanField(default=False, verbose_name="archivé")
    archive_le = models.DateTimeField(null=True, blank=True, verbose_name="archivé le")

    class Meta:
        abstract = True


class Habilitation(models.Model):
    """Porte le catalogue des dix-huit permissions du domaine — RG-02, RG-02
    bis. Modèle sans table : `managed = False` et `default_permissions = ()`
    sont l'idiome Django pour des permissions qui ne portent sur aucune
    ligne. Aucune migration de table n'en résulte.

    Fondé sur les neuf domaines de docs/conception (§ 11.2 du dossier des
    cas d'utilisation), pas sur des permissions de modèle : sept des neuf
    domaines n'ont encore aucun modèle avant le sprint 2. Voir
    docs/suivi/DECISIONS.md pour le détail des noms de domaine composés
    (`instructeurs_qualifications`, `lieux_calendrier`).

    Vérifiable par `utilisateur.has_perm("noyau.<domaine>_lecture")` ou
    `"noyau.<domaine>_ecriture"` — toujours préfixé `noyau.`, ce modèle
    vivant ici.
    """

    class Meta:
        managed = False
        default_permissions = ()
        permissions = [
            ("administration_lecture", "Lecture sur Administration"),
            ("administration_ecriture", "Écriture sur Administration"),
            ("referentiel_lecture", "Lecture sur Référentiel"),
            ("referentiel_ecriture", "Écriture sur Référentiel"),
            ("organisation_lecture", "Lecture sur Organisation"),
            ("organisation_ecriture", "Écriture sur Organisation"),
            (
                "instructeurs_qualifications_lecture",
                "Lecture sur Instructeurs et qualifications",
            ),
            (
                "instructeurs_qualifications_ecriture",
                "Écriture sur Instructeurs et qualifications",
            ),
            ("lieux_calendrier_lecture", "Lecture sur Lieux et calendrier"),
            ("lieux_calendrier_ecriture", "Écriture sur Lieux et calendrier"),
            ("programme_lecture", "Lecture sur Génération et modification du programme"),
            ("programme_ecriture", "Écriture sur Génération et modification du programme"),
            ("programme_validation_lecture", "Lecture sur Validation du programme"),
            ("programme_validation_ecriture", "Écriture sur Validation du programme"),
            ("evaluations_lecture", "Lecture sur Évaluations"),
            ("evaluations_ecriture", "Écriture sur Évaluations"),
            ("suivi_lecture", "Lecture sur Suivi"),
            ("suivi_ecriture", "Écriture sur Suivi"),
        ]

    def __str__(self):
        return "Catalogue des habilitations"
