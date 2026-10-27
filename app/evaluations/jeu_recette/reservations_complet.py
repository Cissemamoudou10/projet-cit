"""Réservation, avant toute génération, des séances dont le budget d'heures
(RG-39) ou le regroupement (RG-40) ne survivrait pas à un ajustement après
coup — Prompt 51, § 2.4-2.5. Voir le docstring de `programme_complet.py`
pour la raison d'ensemble (horloge simulée, préservation des séances
verrouillées par la génération)."""

import dataclasses
import datetime

from django.core.management.base import CommandError
from django.utils import timezone

from evaluations.jeu_recette.creneaux import creneau_libre
from planification.services.contraintes import Candidate
from planification.services.ecriture import ServiceEcritureSeance


@dataclasses.dataclass(frozen=True)
class SpecificationControle:
    programme: object
    element_referentiel: object
    brigade: object
    jour: object
    instructeur: object
    lieu: object
    creneaux: list
    libelle: str


def inserer_controle(contexte, spec):
    """Insère la séance verrouillée d'un contrôle formatif (E1/E2/E5,
    § 2.5) — DOIT s'exécuter pendant que `spec.programme` (celui de la
    semaine visée) est encore BROUILLON (voir docstring du module)."""
    from evaluations.models import TypeEvaluation
    from evaluations.services.evaluation import ServiceEvaluation

    jour_iso = spec.jour.isoweekday()
    creneau = creneau_libre(spec.programme, spec.brigade, jour_iso, spec.creneaux)
    if creneau is None:
        raise CommandError(
            f"{spec.libelle} : aucun créneau libre le {spec.jour.isoformat()} pour "
            f"{spec.brigade} — ajustez la génération ou le jour visé."
        )
    evaluation = ServiceEvaluation.creer(
        contexte.agissant_examens,
        {
            "element_referentiel": spec.element_referentiel,
            "brigade": spec.brigade,
            "type": TypeEvaluation.FORMATIVE,
            "date": spec.jour,
            "creneau_type": creneau,
            "instructeur": spec.instructeur,
            "lieu": spec.lieu,
        },
    )
    contexte.stdout.write(f"  {spec.libelle} créée (séance verrouillée, {spec.jour.isoformat()}).")
    return evaluation


def reserver_m2_regroupe(contexte, programme_vide, jour, creneau):
    """§ 2.4, W-1 : une séance de M2 regroupant EXP1 et EXP2 dans L9,
    réservée directement comme une séance à deux lignes — jamais produite en
    espérant que la génération place indépendamment un M2 pour chaque
    brigade sur le même créneau : RG-16 (progression décalée) ne le garantit
    jamais, et une tentative d'ajustement après coup (supprimer la séance
    d'EXP2, regrouper sur celle d'EXP1) échoue dès que l'une des deux
    brigades n'a aucune séance M2 cette semaine-là. `creer_seance`
    verrouille d'office (comme `inserer_seance_de_controle`) : la
    génération qui suit la préserve et comble le reste autour."""
    debut = timezone.make_aware(datetime.datetime.combine(jour, creneau.heure_debut))
    fin = timezone.make_aware(datetime.datetime.combine(jour, creneau.heure_fin))
    cle_regroupement = object()
    candidates = [
        Candidate(
            brigade=brigade,
            element_referentiel=contexte.elements_f6["M2"],
            instructeur=contexte.instructeurs["I1"],
            debut=debut,
            fin=fin,
            lieu=contexte.lieux["L9"],
            cle_regroupement=cle_regroupement,
        )
        for brigade in (contexte.exp1, contexte.exp2)
    ]
    ServiceEcritureSeance.creer_seance(contexte.agissant_plan, programme_vide, candidates)
    contexte.stdout.write(
        f"  Séance M2 d'EXP1 et EXP2 réservée, regroupée dans L9 ({jour.isoformat()})."
    )
