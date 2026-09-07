"""Indisponibilités de lieu — CU-P4-06, § 3.1 du Prompt 14.

Pas `ServiceGestion` : une déclaration ne s'archive pas, elle se consulte
depuis la fiche du lieu — même famille que `ServiceQualification`, voir
.claude/rules/services.md. Modifiable depuis Prompt 17, § 4 : `modifier`
reprend les mêmes contrôles que `declarer` (fin postérieure au début,
absence de chevauchement), en excluant la période **en cours de
modification** d'elle-même — sans quoi une modification qui ne déplace pas
les bornes se détecterait comme son propre conflit.
"""

from django.db import IntegrityError, transaction

from administration.habilitations import verifier_habilitation
from administration.models import TypeAction
from administration.services.journal import DonneesEntreeJournal, ServiceJournal
from noyau.exceptions import ErreurIntrouvable, ErreurValidation
from noyau.services.base import ServiceBase
from ressources.models import IndisponibiliteLieu

OBJET_TYPE = "indisponibilite_lieu"
PERMISSION_LECTURE = "noyau.lieux_calendrier_lecture"
PERMISSION_ECRITURE = "noyau.lieux_calendrier_ecriture"


def _valider_periode(debut, fin, motif):
    if fin <= debut:
        raise ErreurValidation("La fin de l'indisponibilité doit être postérieure au début.")
    if not motif.strip():
        raise ErreurValidation("Le motif de l'indisponibilité est obligatoire.")


def _verifier_absence_de_chevauchement(lieu, debut, fin, *, exclude_pk=None):
    conflits = lieu.indisponibilites.filter(debut__lt=fin, fin__gt=debut)
    if exclude_pk is not None:
        conflits = conflits.exclude(pk=exclude_pk)
    conflit = conflits.order_by("debut").first()
    if conflit:
        raise ErreurValidation(
            f"« {lieu} » est déjà indisponible du {conflit.debut:%d/%m/%Y %H:%M} "
            f"au {conflit.fin:%d/%m/%Y %H:%M} ({conflit.motif}). Modifiez la période saisie."
        )


def _capturer(indisponibilite):
    return {
        "debut": indisponibilite.debut.isoformat(),
        "fin": indisponibilite.fin.isoformat(),
        "motif": indisponibilite.motif,
    }


class ServiceIndisponibiliteLieu:
    DOMAINE = "lieux_calendrier"
    PERMISSION_LECTURE = PERMISSION_LECTURE
    PERMISSION_ECRITURE = PERMISSION_ECRITURE

    @staticmethod
    def obtenir(pk):
        try:
            return IndisponibiliteLieu.objects.select_related("lieu").get(pk=pk)
        except IndisponibiliteLieu.DoesNotExist as erreur:
            raise ErreurIntrouvable(f"Indisponibilité introuvable (identifiant {pk}).") from erreur

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
        _valider_periode(debut, fin, motif)
        _verifier_absence_de_chevauchement(lieu, debut, fin)

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

    @staticmethod
    def modifier(agissant, indisponibilite, debut, fin, motif):
        """Prompt 17, § 4 : mêmes contrôles que `declarer`, mais la période
        en cours de modification s'exclut elle-même de la recherche de
        chevauchement (`exclude_pk`) — sinon sa propre version enregistrée
        se détecterait comme un conflit dès qu'aucune borne ne bouge.
        """
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        _valider_periode(debut, fin, motif)
        _verifier_absence_de_chevauchement(
            indisponibilite.lieu, debut, fin, exclude_pk=indisponibilite.pk
        )

        avant = _capturer(indisponibilite)
        indisponibilite.debut = debut
        indisponibilite.fin = fin
        indisponibilite.motif = motif
        try:
            with transaction.atomic():
                ServiceBase.modifier(indisponibilite, agissant)
                ServiceJournal.enregistrer_detaillee(
                    DonneesEntreeJournal(
                        type_action=TypeAction.MODIFICATION_ELEMENT_GESTION,
                        identifiant_saisi=str(indisponibilite),
                        auteur=agissant,
                        objet_type=OBJET_TYPE,
                        objet_identifiant=str(indisponibilite.pk),
                        valeur_avant=avant,
                        valeur_apres=_capturer(indisponibilite),
                    )
                )
        except IntegrityError as erreur:
            raise ErreurValidation(
                f"« {indisponibilite.lieu} » porte déjà une période qui recouvre celle saisie."
            ) from erreur
        return indisponibilite

    @staticmethod
    def supprimer(agissant, indisponibilite):
        """Pas d'archivage (§ 3.1 : une déclaration ne se modifie ni ne se
        réactive) — la suppression physique est le seul moyen de corriger
        une saisie erronée, même famille que `ServiceQualification.retirer`.
        """
        verifier_habilitation(agissant, PERMISSION_ECRITURE)
        with transaction.atomic():
            ServiceJournal.enregistrer_detaillee(
                DonneesEntreeJournal(
                    type_action=TypeAction.SUPPRESSION_ELEMENT_GESTION,
                    identifiant_saisi=str(indisponibilite),
                    auteur=agissant,
                    objet_type=OBJET_TYPE,
                    objet_identifiant=str(indisponibilite.pk),
                )
            )
            indisponibilite.delete()
