"""Gestion des instructeurs — CU-P4-01.

Premier service hors du référentiel à hériter de `ServiceGestion` : le
patron s'applique tel quel (D-19), sans aucun ajout dans `noyau`.

`CHAMP_UNICITE = "nom"`, pas `"matricule"` : `matricule` est nul pour un
vacataire ou un civil (§ 2 du Prompt 12), et `ServiceGestion` s'en sert pour
le tri par défaut et l'identifiant du journal — un vacataire sans matricule y
apparaîtrait comme « None », exactement le défaut déjà corrigé en P-24
(docs/suivi/PROBLEMES.md). `_erreur_unicite` est donc surchargée pour
désigner le `matricule`, seule contrainte d'unicité réelle du modèle.
"""

from django.db.models import Count, Exists, OuterRef, Q
from django.utils import timezone

from administration.habilitations import verifier_habilitation
from administration.models import TypeAction
from administration.services.journal import DonneesEntreeJournal, ServiceJournal
from noyau.exceptions import ErreurValidation
from noyau.services.gestion import ServiceGestion, valider_instance
from ressources.models import IndisponibiliteInstructeur, Instructeur, Statut


class ServiceInstructeur(ServiceGestion):
    DOMAINE = "instructeurs_qualifications"
    MODELE = Instructeur
    CHAMP_UNICITE = "nom"
    CHAMPS_RECHERCHE = ("nom", "prenom", "matricule")
    CHAMPS_FILTRABLES = ("statut", "specialite")
    CHAMPS_JOURNALISES = ("nom", "prenom", "matricule", "grade", "specialite", "statut")
    OBJET_TYPE = "instructeur"

    PERMISSION_LECTURE = "noyau.instructeurs_qualifications_lecture"
    PERMISSION_ECRITURE = "noyau.instructeurs_qualifications_ecriture"
    VERIFIER_HABILITATION = staticmethod(verifier_habilitation)
    ENREGISTRER_JOURNAL = staticmethod(ServiceJournal.enregistrer_detaillee)
    DONNEES_JOURNAL = DonneesEntreeJournal
    NATURE_CREATION = TypeAction.CREATION_ELEMENT_GESTION
    NATURE_MODIFICATION = TypeAction.MODIFICATION_ELEMENT_GESTION
    NATURE_ARCHIVAGE = TypeAction.ARCHIVAGE_ELEMENT_GESTION
    NATURE_SUPPRESSION = TypeAction.SUPPRESSION_ELEMENT_GESTION

    @classmethod
    def _queryset(cls):
        """Prompt 17, § 2.4 : nombre de qualifications. § 7, Prompt 27 :
        colonne symétrique à celle des lieux (`ServiceLieu._queryset`) —
        `est_indisponible_maintenant` (`Exists`, sous-requête corrélée) et
        `nombre_indisponibilites_a_venir` (`Count` filtré), une seule
        requête pour toute la page, jamais une par ligne. `distinct=True`
        sur LES DEUX `Count` : combiner deux agrégats sur deux relations
        inverses différentes (qualifications, indisponibilités) sans lui
        gonflerait chacun par le produit cartésien de l'autre jointure."""
        maintenant = timezone.now()
        return cls.MODELE.objects.annotate(
            nombre_qualifications=Count("qualifications", distinct=True),
            est_indisponible_maintenant=Exists(
                IndisponibiliteInstructeur.objects.filter(
                    instructeur=OuterRef("pk"), debut__lte=maintenant, fin__gt=maintenant
                )
            ),
            nombre_indisponibilites_a_venir=Count(
                "indisponibilites", filter=Q(indisponibilites__fin__gt=maintenant), distinct=True
            ),
        )

    @staticmethod
    def choix_statut():
        """Choix pour la liste déroulante et le filtre — la vue ne doit
        jamais importer `ressources.models` directement, voir
        .claude/rules/vues.md (même patron que `ServiceReferentiel.
        categories_lieu`).
        """
        return Statut.choices

    @staticmethod
    def libelle_statut(valeur):
        return Statut(valeur).label

    @staticmethod
    def _valider(instance):
        """R00-RES-02 (recette, NC mineur) : `ck_instructeur_matricule_
        militaire` n'existe qu'en contrainte base, jamais vérifiée par
        `valider_instance` (`validate_constraints=False`, voir `noyau.
        services.gestion`) — sans ce contrôle explicite, sa violation
        remonte comme une `IntegrityError` générique, attrapée par
        `ServiceGestion.creer`/`modifier` et réinterprétée par
        `_erreur_unicite` (recherche d'un doublon de matricule nul), un
        message sans rapport avec la cause réelle."""
        if instance.statut == Statut.MILITAIRE_DU_CENTRE and not instance.matricule:
            raise ErreurValidation(
                "Le matricule est obligatoire pour un militaire du centre. Saisissez-le, "
                "ou choisissez le statut vacataire."
            )
        valider_instance(instance)

    @classmethod
    def _erreur_unicite(cls, instance):
        existant = (
            cls.MODELE.objects.filter(matricule=instance.matricule).exclude(pk=instance.pk).first()
        )
        return ErreurValidation(f"« {instance.matricule} » est déjà attribué à {existant}.")

    @classmethod
    def valeurs_specialite_distinctes(cls):
        """§ 4.2 du Prompt 12 : le filtre se construit sur les valeurs
        réellement enregistrées, jamais sur une nomenclature figée — la
        spécialité reste un texte libre tant qu'aucune table de référence
        commune avec `Formation.specialite` n'a été arbitrée.
        """
        return (
            cls.MODELE.objects.exclude(specialite="")
            .order_by("specialite")
            .values_list("specialite", flat=True)
            .distinct()
        )
