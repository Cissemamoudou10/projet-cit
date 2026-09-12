"""Validation de la répartition — TEMPS 3, § 5, Prompt 25.

RÈGLE ABSOLUE, comme pour l'import de stagiaires (US-SES-05) : la proposition
ajustée n'est jamais une source de vérité. Chaque ligne est revalidée
intégralement contre les trois contrôles de `ServiceAffectation` au moment de
la validation, jamais contre l'état constaté au temps 1. Une ligne refusée
par un contrôle métier (RG-20, RG-19, radiation entre-temps) est exclue et
consignée, jamais une erreur technique brute (D3, D4, Prompt 25 § 10) — SEUL
un échec technique en cours d'écriture (`IntegrityError`) défait la
transaction entière (D2), sur le modèle de RG-18.
"""

from dataclasses import dataclass

from django.db import IntegrityError, transaction
from django.utils import timezone

from administration.habilitations import verifier_habilitation
from administration.models import TypeAction
from administration.services.journal import DonneesEntreeJournal, ServiceJournal
from noyau.exceptions import ErreurValidation
from noyau.services.base import ServiceBase
from organisation.models import AffectationBrigade
from organisation.repartition.proposition import stagiaires_sans_affectation_ouverte
from organisation.services.affectation import (
    OBJET_TYPE,
    ServiceAffectation,
    avertissement_affectation_tardive,
)
from organisation.services.session import PERMISSION_ECRITURE


@dataclass(frozen=True)
class LigneRefusee:
    stagiaire_id: int
    motif: str


@dataclass(frozen=True)
class RapportValidation:
    enregistrees: tuple
    refusees: tuple
    avertissements: tuple
    stagiaires_non_affectes: tuple


@dataclass(frozen=True)
class _Catalogue:
    """Regroupe les stagiaires et brigades de la session, chargés une seule
    fois — évite une requête par ligne de la proposition (`python.md`)."""

    stagiaires: dict
    brigades: dict


@dataclass(frozen=True)
class _ResultatLigne:
    affectation: object = None
    refus: LigneRefusee = None
    avertissements: tuple = ()


def valider(agissant, session, proposition) -> RapportValidation:
    verifier_habilitation(agissant, PERMISSION_ECRITURE)
    catalogue = _Catalogue(
        stagiaires={s.pk: s for s in session.stagiaires.all()},
        brigades={b.pk: b for b in session.brigades.all()},
    )
    enregistrees, refusees, avertissements = [], [], []
    try:
        with transaction.atomic():
            for stagiaire_id, brigade_id in proposition.affectations:
                resultat = _traiter_ligne(agissant, catalogue, stagiaire_id, brigade_id)
                if resultat.refus is not None:
                    refusees.append(resultat.refus)
                else:
                    enregistrees.append(resultat.affectation)
                    avertissements.extend(resultat.avertissements)
            _journaliser(agissant, session, enregistrees, refusees)
    except IntegrityError as erreur:
        raise ErreurValidation(
            "L'enregistrement a été interrompu par un conflit de données : aucune "
            "affectation n'a été enregistrée. Reprenez depuis la proposition."
        ) from erreur
    non_affectes = tuple(stagiaires_sans_affectation_ouverte(session).values_list("pk", flat=True))
    return RapportValidation(
        enregistrees=tuple(enregistrees),
        refusees=tuple(refusees),
        avertissements=tuple(avertissements),
        stagiaires_non_affectes=non_affectes,
    )


def _traiter_ligne(agissant, catalogue, stagiaire_id, brigade_id):
    stagiaire = catalogue.stagiaires.get(stagiaire_id)
    brigade = catalogue.brigades.get(brigade_id)
    if stagiaire is None or brigade is None:
        return _ResultatLigne(refus=LigneRefusee(stagiaire_id, "stagiaire ou brigade introuvable"))
    try:
        avertissements_ligne = ServiceAffectation.verifier_controles(stagiaire, brigade)
    except ErreurValidation as erreur:
        return _ResultatLigne(refus=LigneRefusee(stagiaire_id, str(erreur)))
    instance = AffectationBrigade(
        stagiaire=stagiaire, brigade=brigade, date_effet=timezone.localdate()
    )
    ServiceBase.creer(instance, agissant)
    _journaliser_ligne(agissant, instance)
    avertissements = (*avertissements_ligne, *avertissement_affectation_tardive(stagiaire.session))
    return _ResultatLigne(affectation=instance, avertissements=avertissements)


def _journaliser_ligne(agissant, instance):
    ServiceJournal.enregistrer_detaillee(
        DonneesEntreeJournal(
            type_action=TypeAction.CREATION_ELEMENT_GESTION,
            identifiant_saisi=str(instance),
            auteur=agissant,
            objet_type=OBJET_TYPE,
            objet_identifiant=str(instance.pk),
        )
    )


def _journaliser(agissant, session, enregistrees, refusees):
    ServiceJournal.enregistrer_detaillee(
        DonneesEntreeJournal(
            type_action=TypeAction.CREATION_ELEMENT_GESTION,
            identifiant_saisi=f"Validation de la répartition — {session}",
            auteur=agissant,
            objet_type="repartition",
            objet_identifiant=str(session.pk),
            valeur_apres={
                "session": str(session),
                "nombre_enregistrees": len(enregistrees),
                "nombre_refusees": len(refusees),
            },
        )
    )
