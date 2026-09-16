"""RG-39 — volume et prérequis, deux volets arbitrés au Prompt 30 § 4 (voir
docs/suivi/DECISIONS.md pour le détail des deux arbitrages) :

(a) le volume programmé compte tous les programmes NON REJETÉS, à
    l'exclusion du programme en cours d'évaluation (`ServiceContraintes.
    contexte`, `_charger_volumes`) ;
(b) un prérequis est « achevé » quand le volume programmé de la matière
    prérequise POUR CETTE BRIGADE atteint son volume prescrit — définition
    PROVISOIRE, rattachée à US-SUI-01/RG-60 (le volume RÉALISÉ, sprint 4,
    la remplacera).

Ne relit jamais le graphe de prérequis lui-même : `contexte.
prerequis_par_element` vient de `referentiel.models.Prerequis`, chargé une
fois (D-40, US-REF-06)."""

from planification.services.violations import violation


def verifier_rg39(candidate, contexte):
    violations = []
    violations += _verifier_volume(candidate, contexte)
    violations += _verifier_prerequis(candidate, contexte)
    return violations


def _verifier_volume(candidate, contexte):
    element = candidate.element_referentiel
    duree = (candidate.fin - candidate.debut).total_seconds() / 3600
    deja_programme = contexte.volume_programme_par_element.get(element.pk, 0)
    total = deja_programme + duree
    if total <= element.volume_horaire_prescrit:
        return []
    return [
        violation(
            "RG-39",
            f"Le volume programmé de {element.matiere} atteindrait {total:.2f} h, "
            f"au-delà du volume prescrit ({element.volume_horaire_prescrit} h).",
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
