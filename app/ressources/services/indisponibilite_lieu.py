"""Indisponibilités de lieu — CU-P4-06, § 3.1 du Prompt 14.

Pas `ServiceGestion` : une déclaration ne se modifie ni ne s'archive, elle se
consulte depuis la fiche du lieu — même famille que `ServiceQualification`,
voir .claude/rules/services.md.
"""

from django.db import IntegrityError, transaction

from administration.habilitations import verifier_habilitation
from administration.models import TypeAction
from administration.services.journal import DonneesEntreeJournal, ServiceJournal
from noyau.exceptions import ErreurValidation
from noyau.services.base import ServiceBase
from ressources.models import IndisponibiliteLieu

OBJET_TYPE = "indisponibilite_lieu"
PERMISSION_LECTURE = "noyau.lieux_calendrier_lecture"
PERMISSION_ECRITURE = "noyau.lieux_calendrier_ecriture"


class ServiceIndisponibiliteLieu:
    DOMAINE = "lieux_calendrier"
    PERMISSION_LECTURE = PERMISSION_LECTURE
    PERMISSION_ECRITURE = PERMISSION_ECRITURE

    @staticmethod
    def lister_pour_lieu(agissant, lieu):
        verifier_habilitation(agissant, PERMISSION_LECTURE)
        return lieu.indisponibilites.order_by("-debut")

    @staticmethod
    def declarer(agissant, lieu, debut, fin, motif):
        """Refuse un recouvrement avant d'écrire, en nommant la période
        existante (§ 8 du Prompt 14) — la contrainte d'exclusion
        `ex_indispo_lieu_chevauchement` reste le juge final, cette
        vérification préalable ne fait que produire un message exploitable.
        """
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        if fin <= debut:
            raise ErreurValidation("La fin de l'indisponibilité doit être postérieure au début.")
        if not motif.strip():
            raise ErreurValidation("Le motif de l'indisponibilité est obligatoire.")

        conflit = (
            lieu.indisponibilites.filter(debut__lt=fin, fin__gt=debut).order_by("debut").first()
        )
        if conflit:
            raise ErreurValidation(
                f"« {lieu} » est déjà indisponible du {conflit.debut:%d/%m/%Y %H:%M} "
                f"au {conflit.fin:%d/%m/%Y %H:%M} ({conflit.motif}). Modifiez la période saisie."
            )

        indisponibilite = IndisponibiliteLieu(lieu=lieu, debut=debut, fin=fin, motif=motif)
        try:
            with transaction.atomic():
                ServiceBase.creer(indisponibilite, agissant)
                ServiceJournal.enregistrer_detaillee(
                    DonneesEntreeJournal(
                        type_action=TypeAction.CREATION_ELEMENT_GESTION,
                        identifiant_saisi=str(indisponibilite),
                        auteur=agissant,
                        objet_type=OBJET_TYPE,
                        objet_identifiant=str(indisponibilite.pk),
                    )
                )
        except IntegrityError as erreur:
            raise ErreurValidation(
                f"« {lieu} » porte déjà une période qui recouvre celle saisie."
            ) from erreur
        return indisponibilite
