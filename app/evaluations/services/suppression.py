"""Suppression d'une évaluation — US-PLAN-05, M8 (report de US-EVAL-01, D-181).

Une évaluation organisée, ou dont un sujet est retenu, ne se supprime pas. Une
formative rattachée à une séance supprime l'évaluation puis sa séance, par la
porte d'écriture (garde comprise). Une séance de contrôle n'est jamais effacée
en dehors de cette voie (M7).
"""

from django.db import transaction

from administration.habilitations import verifier_habilitation
from administration.models import TypeAction
from administration.services.journal import DonneesEntreeJournal, ServiceJournal
from evaluations.models import OrganisationEpreuve, Sujet
from noyau.exceptions import ErreurValidation
from planification.models import Seance
from planification.services.ecriture import ServiceEcritureSeance

PERMISSION_ECRITURE = "noyau.evaluations_ecriture"
MESSAGE_ORGANISEE = "Une évaluation organisée ne se supprime pas : désorganisez-la d'abord (M8)."
MESSAGE_SUJET_RETENU = "Une évaluation dont un sujet est retenu ne se supprime pas (M8)."


def _verifier_supprimable(evaluation):
    if OrganisationEpreuve.objects.filter(evaluation=evaluation).exists():
        raise ErreurValidation(MESSAGE_ORGANISEE)
    if Sujet.objects.filter(evaluation=evaluation, retenu=True).exists():
        raise ErreurValidation(MESSAGE_SUJET_RETENU)


def _journaliser(agissant, identifiant, pk):
    ServiceJournal.enregistrer_detaillee(
        DonneesEntreeJournal(
            type_action=TypeAction.SUPPRESSION_ELEMENT_GESTION,
            identifiant_saisi=identifiant,
            auteur=agissant,
            objet_type="evaluation",
            objet_identifiant=str(pk),
        )
    )


def supprimer_evaluation(agissant, evaluation):
    verifier_habilitation(agissant, PERMISSION_ECRITURE)
    with transaction.atomic():
        _verifier_supprimable(evaluation)
        seance_pk, identifiant, pk = evaluation.seance_id, str(evaluation), evaluation.pk
        evaluation.delete()
        if seance_pk is not None:
            # Relue après suppression : l'évaluation n'existe plus, la séance n'est plus contrôle.
            ServiceEcritureSeance.supprimer_seance_de_controle(agissant, Seance.objects.get(pk=seance_pk))
        _journaliser(agissant, identifiant, pk)
