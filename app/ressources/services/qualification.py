"""Matrice de qualification — CU-P4-02, RG-21, RG-22.

Pas `ServiceGestion` : ni archivage (§ 3.1 du Prompt 13), ni écran
liste/créer classique — deux entrées symétriques sur la même table (§ 2),
même famille que `ServicePrerequis`. Un service ne connaît pas la requête
HTTP — voir .claude/rules/services.md.
"""

from django.db import IntegrityError, transaction

from administration.habilitations import verifier_habilitation
from administration.models import TypeAction
from administration.services.journal import DonneesEntreeJournal, ServiceJournal
from noyau.exceptions import ErreurIntrouvable, ErreurValidation
from noyau.services.base import ServiceBase
from referentiel.services.matiere import ServiceMatiere
from ressources.models import Qualification
from ressources.services.instructeur import ServiceInstructeur

OBJET_TYPE = "qualification"
PERMISSION_LECTURE = "noyau.instructeurs_qualifications_lecture"
PERMISSION_ECRITURE = "noyau.instructeurs_qualifications_ecriture"


def _journaliser(agissant, nature, qualification):
    identifiant = str(qualification)
    ServiceJournal.enregistrer_detaillee(
        DonneesEntreeJournal(
            type_action=nature,
            identifiant_saisi=identifiant,
            auteur=agissant,
            objet_type=OBJET_TYPE,
            objet_identifiant=identifiant,
        )
    )


class ServiceQualification:
    DOMAINE = "instructeurs_qualifications"
    PERMISSION_LECTURE = PERMISSION_LECTURE
    PERMISSION_ECRITURE = PERMISSION_ECRITURE

    @staticmethod
    def obtenir(pk):
        try:
            return Qualification.objects.select_related("instructeur", "matiere").get(pk=pk)
        except Qualification.DoesNotExist as erreur:
            raise ErreurIntrouvable(f"Qualification introuvable (identifiant {pk}).") from erreur

    @staticmethod
    def matieres_avec_etat(agissant, instructeur, filtres, page):
        """Entrée instructeur (§ 7.2) : le catalogue, chaque ligne marquée
        qualifiée ou non pour cet instructeur — un seul ensemble déjà
        qualifié, jamais une requête par ligne (python.md).
        """
        verifier_habilitation(agissant, PERMISSION_LECTURE)
        page_matieres = ServiceMatiere.lister(agissant, filtres, page)
        qualifications = dict(
            Qualification.objects.filter(instructeur=instructeur).values_list("matiere_id", "pk")
        )
        for matiere in page_matieres:
            matiere.qualification_pk = qualifications.get(matiere.pk)
            matiere.est_qualifiee = matiere.qualification_pk is not None
        return page_matieres

    @staticmethod
    def instructeurs_avec_etat(agissant, matiere):
        """Entrée matière (§ 7.3, A1) — symétrique, sur les instructeurs non
        archivés : la même donnée, l'autre sens (§ 2)."""
        verifier_habilitation(agissant, PERMISSION_LECTURE)
        instructeurs = list(
            ServiceInstructeur.disponibles_pour_selection().order_by("nom", "prenom")
        )
        qualifications = dict(
            Qualification.objects.filter(matiere=matiere).values_list("instructeur_id", "pk")
        )
        for instructeur in instructeurs:
            instructeur.qualification_pk = qualifications.get(instructeur.pk)
            instructeur.est_qualifie = instructeur.qualification_pk is not None
        return instructeurs

    @staticmethod
    def ajouter(agissant, instructeur, matiere):
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        qualification = Qualification(instructeur=instructeur, matiere=matiere)
        try:
            with transaction.atomic():
                ServiceBase.creer(qualification, agissant)
                _journaliser(agissant, TypeAction.CREATION_ELEMENT_GESTION, qualification)
        except IntegrityError as erreur:
            raise ErreurValidation(
                f"« {instructeur} » est déjà qualifié pour « {matiere} »."
            ) from erreur
        return qualification

    @staticmethod
    def seances_futures(_qualification):
        """§ 3.2 : rend une liste vide aujourd'hui — les séances arrivent au
        sprint 3, US-PLAN-03 remplira cette méthode, sans en changer la
        signature."""
        return []

    @staticmethod
    def laisserait_la_matiere_non_couverte(qualification):
        """§ 3.4, E2 — vrai si `qualification` est le dernier lien qualifiant
        sa matière : le retrait aboutira quand même, avec un avertissement,
        jamais un refus (décision de commandement, pas une erreur de saisie).
        """
        return qualification.matiere.qualifications.count() == 1

    @staticmethod
    def retirer(agissant, qualification):
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        bloquantes = ServiceQualification.seances_futures(qualification)
        if bloquantes:
            elements = ", ".join(str(seance) for seance in bloquantes)
            raise ErreurValidation(
                f"Impossible de retirer cette qualification : {qualification.instructeur} "
                f"est affecté à des séances futures de {qualification.matiere} ({elements}). "
                "Réaffectez-les avant de retirer la qualification."
            )
        with transaction.atomic():
            _journaliser(agissant, TypeAction.SUPPRESSION_ELEMENT_GESTION, qualification)
            qualification.delete()
