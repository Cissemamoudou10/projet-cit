"""Modèle d'utilisateur du système — RG-01, RG-03.

`EntreeJournal` remonte dès US-ADM-01 : RG-26 exige la journalisation d'une
authentification échouée, une postcondition du scénario CU-P1-01. L'écran de
consultation, les filtres et la révocation UPDATE/DELETE (RG-27) restent
pour US-ADM-04 — la table n'a pas encore de données de test.
"""

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models

from noyau.models import ModeleHorodate


class Profil(models.TextChoices):
    """Au niveau du module, pas imbriquée dans `Utilisateur` : une classe
    imbriquée (`Meta`) ne voit pas les autres attributs du corps de classe
    qui la contient — seule la portée globale du module lui est accessible.
    Alias posé sur `Utilisateur.Profil` juste après la classe, pour l'accès
    habituel `Utilisateur.Profil.ADMINISTRATEUR`.
    """

    ADMINISTRATEUR = "administrateur", "Administrateur"
    CELLULE_PEDAGOGIQUE = "cellule_pedagogique", "Cellule pédagogique"
    CELLULE_PLANIFICATION = "cellule_planification", "Cellule planification"
    CELLULE_EXAMENS = "cellule_examens", "Cellule examens"
    DIRECTION_FORMATION = "direction_formation", "Direction de formation"


class Utilisateur(AbstractUser):
    """Étend AbstractUser plutôt que de le remplacer : authentification,
    hachage des mots de passe (BNF-03) et gestion de session sont acquis
    du framework.
    """

    grade = models.CharField(max_length=50, verbose_name="grade")
    profil = models.CharField(max_length=30, choices=Profil.choices, verbose_name="profil")
    echecs_consecutifs = models.PositiveSmallIntegerField(
        default=0, verbose_name="échecs consécutifs"
    )
    verrouille_jusqu_a = models.DateTimeField(
        null=True, blank=True, verbose_name="verrouillé jusqu'à"
    )
    doit_changer_mot_de_passe = models.BooleanField(
        default=True, verbose_name="doit changer son mot de passe"
    )

    class Meta:
        db_table = "administration_utilisateur"
        verbose_name = "utilisateur"
        verbose_name_plural = "utilisateurs"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(profil__in=Profil.values),
                name="ck_utilisateur_profil",
            ),
        ]

    def __str__(self):
        return self.get_full_name() or self.username


Utilisateur.Profil = Profil


class TypeAction(models.TextChoices):
    """Au niveau du module — même raison que `Profil` : voir sa docstring.

    RG-26 énumère cinq natures ; trois portent sur des objets qui n'existent
    pas encore (note, programme, sujet). L'énumération les déclare
    néanmoins dès US-ADM-04 (§ 2.5 du Prompt 04), pour que les stories des
    sprints 2 à 4 n'aient qu'à s'y rattacher — aucune n'est encore
    atteignable depuis un service ou une vue.

    Cinq natures s'ajoutent, hors RG-26 — voir docs/suivi/DECISIONS.md :
    `ACCES_REFUSE` (US-ADM-03), `MODIFICATION_HABILITATIONS` (US-ADM-03,
    jamais signalée comme extension en son temps — corrigé en D-16),
    `CONSULTATION_JOURNAL` (US-ADM-04), les natures génériques du patron
    de gestion (US-REF-00, D-18 ; `SUPPRESSION_ELEMENT_GESTION` ajoutée à
    US-REF-05, la première story du patron où une suppression est réelle,
    pas seulement théorique) — `CREATION_ELEMENT_GESTION`,
    `MODIFICATION_ELEMENT_GESTION`, `ARCHIVAGE_ELEMENT_GESTION`,
    `SUPPRESSION_ELEMENT_GESTION` comptent pour une seule extension au sens
    de RG-26, bien que quatre valeurs d'énumération : elles ne se
    distinguent pas par nature d'action mais par `objet_type`, réutilisées
    telles quelles par les stories qui partagent le patron — et
    `EXPORT_DONNEES` (US-SES-07), la première nature qui journalise une
    LECTURE plutôt qu'une écriture : un export fait sortir des données
    nominatives du périmètre du système, RG-26 s'applique à ce geste-là,
    pas à la simple consultation d'un écran (voir docs/suivi/DECISIONS.md).

    `GENERATION_PROGRAMME` (US-PLAN-03) — une extension de plus : RG-26
    n'énumère que la validation et le rejet d'un programme, jamais sa
    génération. `ServiceGeneration` journalise l'ACTE (semaine, brigades
    sélectionnées, comptes créés/supprimés, auteur), jamais le détail des
    séances — voir docs/suivi/DECISIONS.md.
    """

    ECHEC_AUTHENTIFICATION = "echec_authentification", "Échec d'authentification"
    CREATION_COMPTE = "creation_compte", "Création de compte"
    MODIFICATION_COMPTE = "modification_compte", "Modification de compte"
    CHANGEMENT_PROFIL = "changement_profil", "Changement de profil"
    DESACTIVATION_COMPTE = "desactivation_compte", "Désactivation de compte"
    REACTIVATION_COMPTE = "reactivation_compte", "Réactivation de compte"
    SAISIE_NOTE = "saisie_note", "Saisie d'une note"
    MODIFICATION_NOTE = "modification_note", "Modification d'une note"
    VALIDATION_PROGRAMME = "validation_programme", "Validation d'un programme"
    REJET_PROGRAMME = "rejet_programme", "Rejet d'un programme"
    SELECTION_SUJET = "selection_sujet", "Sélection d'un sujet d'examen"
    ACCES_REFUSE = "acces_refuse", "Accès refusé"
    MODIFICATION_HABILITATIONS = "modification_habilitations", "Modification des habilitations"
    CONSULTATION_JOURNAL = "consultation_journal", "Consultation du journal"
    CREATION_ELEMENT_GESTION = "creation_element_gestion", "Création d'un élément de gestion"
    MODIFICATION_ELEMENT_GESTION = (
        "modification_element_gestion",
        "Modification d'un élément de gestion",
    )
    ARCHIVAGE_ELEMENT_GESTION = "archivage_element_gestion", "Archivage d'un élément de gestion"
    SUPPRESSION_ELEMENT_GESTION = (
        "suppression_element_gestion",
        "Suppression d'un élément de gestion",
    )
    EXPORT_DONNEES = "export_donnees", "Export de données"
    GENERATION_PROGRAMME = "generation_programme", "Génération d'un programme"


class EntreeJournal(ModeleHorodate):
    """Journal des actions sensibles — RG-26.

    `cree_par`/`modifie_par` (`ModeleHorodate`) restent toujours vides : une
    entrée de journal n'est jamais « créée » par un utilisateur authentifié
    au sens technique de l'ORM, même quand un administrateur agit.

    **Le sens de `auteur` dépend de `type_action`** — voir docs/suivi/DECISIONS.md,
    D-06 :
    - `echec_authentification` : le compte **visé** par la tentative, nullable
      (un identifiant saisi peut ne désigner aucun compte existant).
    - `creation_compte`, `modification_compte`, `changement_profil`,
      `desactivation_compte`, `reactivation_compte` : l'administrateur **agissant**.
      Le compte visé va dans `cible`.

    `objet_type`/`objet_identifiant` (US-ADM-04, CU-P1-03) désignent l'objet
    concerné par un couple, jamais une clé étrangère : les objets journalisés
    appartiennent à six applications, dont cinq n'existent pas encore, et une
    FK les rendrait toutes dépendantes d'`administration` — voir
    docs/suivi/DECISIONS.md, D-15. Distincts de `cible`, qui garde son sens
    d'origine (voir D-04) : `cible` reste inchangé pour ne pas casser les
    tests des stories précédentes qui le lisent directement.

    `valeur_avant`/`valeur_apres` reçoivent une **liste blanche de champs**
    déclarée par le service appelant, jamais une sérialisation complète d'un
    objet — sans quoi le condensat d'un mot de passe finirait dans une table
    lisible par un administrateur (BNF-03).
    """

    type_action = models.CharField(
        max_length=30, choices=TypeAction.choices, verbose_name="type d'action"
    )
    cible = models.CharField(max_length=100, blank=True, verbose_name="cible")
    auteur = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="+",
        verbose_name="auteur",
    )
    identifiant_saisi = models.CharField(max_length=150, verbose_name="identifiant saisi")
    detail = models.TextField(blank=True, verbose_name="détail")
    objet_type = models.CharField(max_length=50, blank=True, verbose_name="type d'objet")
    objet_identifiant = models.CharField(
        max_length=100, blank=True, verbose_name="identifiant de l'objet"
    )
    valeur_avant = models.JSONField(null=True, blank=True, verbose_name="valeur avant")
    valeur_apres = models.JSONField(null=True, blank=True, verbose_name="valeur après")

    class Meta:
        db_table = "administration_entree_journal"
        verbose_name = "entrée de journal"
        verbose_name_plural = "entrées de journal"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(type_action__in=TypeAction.values),
                name="ck_entree_journal_type_action",
            ),
        ]
        indexes = [
            models.Index(fields=["-cree_le"], name="idx_journal_horodatage"),
            models.Index(fields=["type_action", "auteur"], name="idx_journal_nature_auteur"),
        ]

    def __str__(self):
        return f"{self.get_type_action_display()} — {self.identifiant_saisi}"
