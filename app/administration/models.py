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

    `CONSULTATION_SUJETS` (US-EVAL-03, A6) — une extension de plus, sur le
    même patron que `GENERATION_PROGRAMME` : RG-51/BNF-02 exigent de
    journaliser chaque AFFICHAGE de l'écran des sujets (une consultation,
    pas une modification), même précédent qu'`EXPORT_DONNEES` pour
    journaliser une LECTURE. `SELECTION_SUJET`, déjà déclarée ci-dessus
    (US-ADM-04, jamais atteinte avant cette story), porte la sélection et le
    changement du sujet retenu (A3/A4) — voir docs/suivi/DECISIONS.md.

    `DECLARATION_NON_EXECUTION` (US-SUI-05, S6, prompt 44) — une extension de
    plus : aucune nature existante ne porte la déclaration ou l'annulation
    d'une non-exécution de séance, qui ne passe pas par le patron de gestion.
    Une seule nature pour les deux gestes (`detail` les distingue), comme
    `TRANSITION_PROGRAMME` distingue ses transitions — voir
    docs/suivi/DECISIONS.md.

    `CONSULTATION_NOTES` (US-EVAL-05, N5, prompt 46) — une extension de
    plus, même patron que `CONSULTATION_SUJETS` : BNF-02 exige de
    journaliser chaque AFFICHAGE de la grille des notes, pas seulement leur
    saisie — `SAISIE_NOTE`/`MODIFICATION_NOTE` (déjà déclarées ci-dessus,
    RG-26) ne portent que l'écriture.

    `GENERATION_PROCES_VERBAL` (US-EVAL-07, V4, prompt 46) — même patron
    que `GENERATION_PROGRAMME` : un `ProcesVerbal` ne passe pas par le
    patron de gestion (`CREATION_ELEMENT_GESTION` ne convient pas), sa
    génération est un acte distinct, daté et verrouillant.
    `TELECHARGEMENT_PROCES_VERBAL` (US-EVAL-07, V10) — même patron que
    `CONSULTATION_SUJETS`/`CONSULTATION_NOTES` : donnée sensible, chaque
    téléchargement journalisé (D-219 cas a), pas seulement la génération.
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
    CONSULTATION_SUJETS = "consultation_sujets", "Consultation des sujets d'examen"
    TRANSITION_PROGRAMME = "transition_programme", "Transition d'un programme"
    DECLARATION_NON_EXECUTION = (
        "declaration_non_execution",
        "Déclaration de non-exécution d'une séance",
    )
    CONSULTATION_NOTES = "consultation_notes", "Consultation des notes"
    GENERATION_PROCES_VERBAL = "generation_proces_verbal", "Génération d'un procès-verbal"
    TELECHARGEMENT_PROCES_VERBAL = (
        "telechargement_proces_verbal",
        "Téléchargement d'un procès-verbal",
    )


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


class TypeDocument(models.TextChoices):
    """RG-58 (US-SUI-06, prompt 45, P5) : un type par document produit par
    `ServiceDocument`. Le type lui-même est fixé par le code (ce que
    `ServiceDocument` sait produire), seul son CONTENU (`GabaritDocument`)
    est éditable par l'administrateur — à la différence de
    `NatureEvenement`, le terrain n'en ajoute pas.

    `PROCES_VERBAL` (US-SUI-06, anticipation d'US-EVAL-07) prévoyait un seul
    type — V8 d'US-EVAL-07 (prompt 46, point 3) en demande deux, l'en-tête
    et les mentions pouvant différer entre un procès-verbal de fin de
    formation (toute la session) et celui d'une seule évaluation. Scindé ici
    avant toute donnée réelle (seule la commande d'initialisation le
    consommait) — voir docs/suivi/DECISIONS.md."""

    PROGRESSION_REALISEE = "progression_realisee", "Progression réalisée hebdomadaire"
    PROCES_VERBAL_FIN_FORMATION = (
        "proces_verbal_fin_formation",
        "Procès-verbal de fin de formation",
    )
    PROCES_VERBAL_EVALUATION = "proces_verbal_evaluation", "Procès-verbal d'évaluation"


class GabaritDocument(ModeleHorodate):
    """En-tête, mentions et bloc de signature d'un type de document — des
    DONNÉES, jamais du texte en dur dans un gabarit Django (P5). Un jeu
    initial est chargé par la commande `initialiser_gabarits_documents`,
    jamais par une migration de données (leçon de D-122 : une migration de
    données ne survit pas à `transactional_db`)."""

    type_document = models.CharField(
        max_length=30,
        choices=TypeDocument.choices,
        unique=True,
        verbose_name="type de document",
    )
    en_tete = models.TextField(verbose_name="en-tête")
    mentions = models.TextField(blank=True, verbose_name="mentions")
    bloc_signature = models.TextField(blank=True, verbose_name="bloc de signature")

    class Meta:
        db_table = "administration_gabarit_document"
        verbose_name = "gabarit de document"
        verbose_name_plural = "gabarits de document"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(type_document__in=TypeDocument.values),
                name="ck_gabarit_document_type",
            ),
        ]

    def __str__(self):
        return self.get_type_document_display()
