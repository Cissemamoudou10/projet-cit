"""RG-39 — volume et prérequis, deux volets arbitrés au Prompt 30 § 4 (voir
docs/suivi/DECISIONS.md pour le détail des deux arbitrages) :

(a) le volume programmé compte tous les programmes, rejetés compris (V7,
    US-VAL-03), à l'exclusion du programme en cours d'évaluation (`ServiceContraintes.
    contexte`, `_charger_volumes`) ;
(b) un prérequis est « achevé » quand le volume programmé de la matière
    prérequise POUR CETTE BRIGADE atteint son volume prescrit — définition
    PROVISOIRE, rattachée à US-SUI-01/RG-60 (le volume RÉALISÉ, sprint 4,
    la remplacera).

CUMUL PROVISOIRE DU LOT — les deux volets ne s'y comportent PAS pareil
(Prompt 31 § 0.2, docs/suivi/DECISIONS.md, D-135 mis à jour) :

- le PLAFOND (a) le consulte : sans cela, deux candidates de la même
  génération plaçant la même matière ne verraient chacune que le volume déjà
  en base, passeraient toutes les deux, et la génération dépasserait le
  prescrit — le cas courant d'une heuristique gloutonne qui place plusieurs
  séances de la même matière dans la semaine.
- les PRÉREQUIS (b) ne le consultent PAS : une matière prérequise achevée par
  une candidate placée plus tôt dans la même génération ne doit pas débloquer
  sa dépendante plus tard dans la même génération — choix conservateur, qui
  évite aussi que le résultat dépende de l'ordre de placement.

Ne relit jamais le graphe de prérequis lui-même : `contexte.
prerequis_par_element` vient de `referentiel.models.Prerequis`, chargé une
fois (D-40, US-REF-06)."""

from planification.services.temps import duree_heures
from planification.services.violations import violation


def verifier_rg39(candidate, contexte, lot_acceptees):
    violations = []
    violations += _verifier_volume(candidate, contexte, lot_acceptees)
    violations += _verifier_prerequis(candidate, contexte)
    return violations


def _volume_lot(candidate, lot_acceptees):
    element = candidate.element_referentiel
    return sum(
        duree_heures(autre.debut, autre.fin)
        for autre in lot_acceptees
        if autre.element_referentiel.pk == element.pk
    )


def _verifier_volume(candidate, contexte, lot_acceptees):
    element = candidate.element_referentiel
    duree = duree_heures(candidate.debut, candidate.fin)
    deja_programme = contexte.volume_programme_par_element.get(element.pk, 0)
    volume_lot = _volume_lot(candidate, lot_acceptees)
    total = deja_programme + volume_lot + duree
    if total <= element.volume_horaire_prescrit:
        return []
    origine = "base" if deja_programme + duree > element.volume_horaire_prescrit else "lot"
    return [
        violation(
            "RG-39",
            f"Le volume programmé de {element.matiere} atteindrait {total:.2f} h, "
            f"au-delà du volume prescrit ({element.volume_horaire_prescrit} h).",
            origine=origine,
        )
    ]


def _verifier_prerequis(candidate, contexte):
    element = candidate.element_referentiel
    prerequis = contexte.prerequis_par_element.get(element.pk, [])
    violations = []
    for element_prerequis in prerequis:
        cle = (element_prerequis.pk, candidate.brigade.pk)
        programme = contexte.volume_programme_par_element_brigade.get(cle, 0)
        if programme >= element_prerequis.volume_horaire_prescrit:
            continue
        violations.append(
            violation(
                "RG-39",
                f"{element_prerequis.matiere} est prérequise à {element.matiere} pour "
                f"{candidate.brigade} : {programme:.2f} h programmées sur "
                f"{element_prerequis.volume_horaire_prescrit} h prescrites.",
            )
        )
    return violations
