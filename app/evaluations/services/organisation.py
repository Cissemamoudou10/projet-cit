"""`ServiceOrganisationEpreuve` — US-EVAL-04, RG-53, RG-53 bis, RG-37, CLS-05,
Prompt 38. Organise matériellement une certificative datée : créneau, une
organisation par brigade (lieu, effectif attendu), des surveillants. Aucune
règle métier dans les vues ni les formulaires (.claude/rules/services.md).

A1 : on organise sans sujet ; l'épreuve n'est prête (C10) qu'avec un sujet retenu.
A10 : toute écriture est refusée à partir de `date + heure_debut` (gel).
"""

from django.db import transaction
from django.utils import timezone

from administration.habilitations import verifier_habilitation
from administration.models import TypeAction
from administration.services.journal import DonneesEntreeJournal, ServiceJournal
from evaluations.models import OrganisationEpreuve, Surveillance, TypeEvaluation
from evaluations.services.conflits import conflits, conflits_de_l_epreuve
from evaluations.services.evaluation import PERMISSION_ECRITURE, Perimetre
from noyau.exceptions import ErreurIntrouvable, ErreurValidation
from noyau.intervalles import instant_de
from noyau.services.base import ServiceBase
from noyau.services.gestion import valider_instance


def _verifier_certificative(evaluation):
    if evaluation.type != TypeEvaluation.CERTIFICATIVE:
        raise ErreurValidation(
            "Une épreuve s'organise pour une certificative : une formative a sa séance."
        )


def _verifier_creneau_fixe(evaluation):
    if evaluation.heure_debut is None:
        raise ErreurValidation("Fixez d'abord le créneau horaire de l'épreuve.")


def _verifier_non_gele(evaluation):
    """A10 : à partir de `date + heure_debut`, plus aucune écriture."""
    if evaluation.heure_debut is None:
        return
    if instant_de(evaluation.date, evaluation.heure_debut) <= timezone.now():
        raise ErreurValidation("L'épreuve a commencé : l'organisation ne se modifie plus (RG-53).")


def _perimetre(evaluation):
    return Perimetre(
        element=evaluation.element_referentiel,
        session=evaluation.session,
        brigade=evaluation.brigade,
    )


def _verifier_perimetre(evaluation, brigade):
    """B3 : la brigade appartient au périmètre de l'épreuve."""
    if brigade.pk not in {visee.pk for visee in _perimetre(evaluation).brigades_visees}:
        raise ErreurValidation(f"« {brigade} » n'appartient pas au périmètre de cette épreuve.")


def _verifier_lieu_actif(lieu):
    if lieu.archive:
        raise ErreurValidation(f"« {lieu} » est archivé : choisissez un autre lieu.")


def _verifier_capacite(lieu, effectif):
    """B4 / E3 : la capacité du lieu couvre l'effectif attendu, sinon l'écart est nommé."""
    if lieu.capacite is None:
        raise ErreurValidation(f"La capacité de « {lieu} » n'est pas renseignée.")
    if effectif > lieu.capacite:
        raise ErreurValidation(
            f"« {lieu} » a une capacité de {lieu.capacite} : l'effectif attendu ({effectif}) "
            f"dépasse de {effectif - lieu.capacite}."
        )


def _verifier_disponibilite(evaluation, lieu, instructeurs=()):
    """C3 / C5 : aucun conflit sur le créneau, sinon refus nommant l'occupant."""
    messages = conflits(evaluation, {lieu.pk} if lieu else set(), set(instructeurs))
    if messages:
        raise ErreurValidation(" ".join(messages))


def _journaliser(agissant, type_action, objet_type, objet, **detail):
    ServiceJournal.enregistrer_detaillee(
        DonneesEntreeJournal(
            type_action=type_action,
            identifiant_saisi=str(objet),
            auteur=agissant,
            objet_type=objet_type,
            objet_identifiant=str(objet.pk),
            **detail,
        )
    )


class ServiceOrganisationEpreuve:
    DOMAINE = "evaluations"
    PERMISSION_ECRITURE = PERMISSION_ECRITURE

    @staticmethod
    def obtenir_organisation(pk):
        try:
            return OrganisationEpreuve.objects.select_related("evaluation", "brigade", "lieu").get(pk=pk)
        except OrganisationEpreuve.DoesNotExist as erreur:
            raise ErreurIntrouvable(f"Organisation introuvable (identifiant {pk}).") from erreur

    @staticmethod
    def obtenir_surveillance(pk):
        try:
            return Surveillance.objects.select_related("organisation__evaluation").get(pk=pk)
        except Surveillance.DoesNotExist as erreur:
            raise ErreurIntrouvable(f"Surveillant introuvable (identifiant {pk}).") from erreur

    @staticmethod
    def fixer_creneau(agissant, evaluation, heure_debut, heure_fin):
        """C1 : un créneau pour toutes les brigades (C2 : épreuve simultanée).
        Un changement de créneau ne se refuse pas quand il crée un conflit : il se
        signale, comme la date (A9)."""
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        _verifier_certificative(evaluation)
        if evaluation.date < timezone.localdate():
            raise ErreurValidation("La date de cette épreuve est passée : son créneau est figé.")
        if heure_fin <= heure_debut:
            raise ErreurValidation("L'heure de fin doit être postérieure à l'heure de début.")
        if evaluation.heure_debut is not None:
            _verifier_non_gele(evaluation)
        if instant_de(evaluation.date, heure_debut) <= timezone.now():
            raise ErreurValidation("Le créneau proposé commence déjà : choisissez une heure à venir.")
        avant = (evaluation.heure_debut, evaluation.heure_fin)
        evaluation.heure_debut, evaluation.heure_fin = heure_debut, heure_fin
        with transaction.atomic():
            ServiceBase.modifier(evaluation, agissant)
            _journaliser(
                agissant,
                TypeAction.MODIFICATION_ELEMENT_GESTION,
                "evaluation",
                evaluation,
                valeur_avant={"creneau": str(avant)},
                valeur_apres={"creneau": f"{heure_debut}–{heure_fin}"},
            )
        evaluation.avertissements = conflits_de_l_epreuve(evaluation)
        return evaluation

    @staticmethod
    def ajouter_organisation(agissant, evaluation, brigade, lieu, effectif_attendu):
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        _verifier_certificative(evaluation)
        _verifier_creneau_fixe(evaluation)
        _verifier_non_gele(evaluation)
        _verifier_perimetre(evaluation, brigade)
        if lieu is not None:
            _verifier_lieu_actif(lieu)
            if OrganisationEpreuve.objects.filter(evaluation=evaluation, lieu=lieu).exists():
                raise ErreurValidation(
                    f"« {lieu} » est déjà attribué à une brigade de cette épreuve."
                )
            _verifier_capacite(lieu, effectif_attendu)
        _verifier_disponibilite(evaluation, lieu)
        organisation = OrganisationEpreuve(
            evaluation=evaluation, brigade=brigade, lieu=lieu, effectif_attendu=effectif_attendu
        )
        valider_instance(organisation)
        with transaction.atomic():
            ServiceBase.creer(organisation, agissant)
            _journaliser(
                agissant, TypeAction.CREATION_ELEMENT_GESTION, "organisation_epreuve", organisation
            )
        return organisation

    @staticmethod
    def modifier_organisation(agissant, organisation, lieu, effectif_attendu):
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        evaluation = organisation.evaluation
        _verifier_certificative(evaluation)
        _verifier_non_gele(evaluation)
        if lieu is not None:
            _verifier_lieu_actif(lieu)
            deja = OrganisationEpreuve.objects.filter(evaluation=evaluation, lieu=lieu)
            if deja.exclude(pk=organisation.pk).exists():
                raise ErreurValidation(
                    f"« {lieu} » est déjà attribué à une brigade de cette épreuve."
                )
            _verifier_capacite(lieu, effectif_attendu)
        _verifier_disponibilite(evaluation, lieu)
        avant = (str(organisation.lieu), organisation.effectif_attendu)
        organisation.lieu, organisation.effectif_attendu = lieu, effectif_attendu
        with transaction.atomic():
            ServiceBase.modifier(organisation, agissant)
            _journaliser(
                agissant,
                TypeAction.MODIFICATION_ELEMENT_GESTION,
                "organisation_epreuve",
                organisation,
                valeur_avant={"lieu_effectif": str(avant)},
                valeur_apres={"lieu_effectif": str((str(lieu), effectif_attendu))},
            )
        return organisation

    @staticmethod
    def retirer_organisation(agissant, organisation):
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        _verifier_non_gele(organisation.evaluation)
        with transaction.atomic():
            _journaliser(
                agissant,
                TypeAction.SUPPRESSION_ELEMENT_GESTION,
                "organisation_epreuve",
                organisation,
            )
            organisation.delete()

    @staticmethod
    def ajouter_surveillant(agissant, organisation, instructeur=None, nom_libre=""):
        """A7 : exactement une nature (instructeur référencé, ou nom libre). Un nom
        libre n'est soumis à aucun contrôle de disponibilité (C5)."""
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        evaluation = organisation.evaluation
        _verifier_certificative(evaluation)
        _verifier_creneau_fixe(evaluation)
        _verifier_non_gele(evaluation)
        nom = (nom_libre or "").strip()
        if (instructeur is None) == (not nom):
            raise ErreurValidation(
                "Un surveillant est soit un instructeur référencé, soit une personne extérieure "
                "désignée par son nom : jamais les deux, jamais aucun."
            )
        if instructeur is not None:
            if instructeur.archive:
                raise ErreurValidation(f"{instructeur} est archivé : il ne peut plus être affecté.")
            deja = Surveillance.objects.filter(
                organisation__evaluation=evaluation, instructeur=instructeur
            )
            if deja.exists():
                raise ErreurValidation(f"{instructeur} surveille déjà une salle de cette épreuve.")
            _verifier_disponibilite(evaluation, None, {instructeur.pk})
        surveillance = Surveillance(
            organisation=organisation, instructeur=instructeur, nom_libre=nom
        )
        valider_instance(surveillance)
        with transaction.atomic():
            ServiceBase.creer(surveillance, agissant)
            _journaliser(
                agissant, TypeAction.CREATION_ELEMENT_GESTION, "surveillance", surveillance
            )
        return surveillance

    @staticmethod
    def retirer_surveillant(agissant, surveillance):
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        _verifier_non_gele(surveillance.organisation.evaluation)
        with transaction.atomic():
            _journaliser(
                agissant, TypeAction.SUPPRESSION_ELEMENT_GESTION, "surveillance", surveillance
            )
            surveillance.delete()
