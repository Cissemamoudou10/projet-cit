"""RG-39 — volume et prérequis, deux volets arbitrés au Prompt 30 § 4 (voir
docs/suivi/DECISIONS.md pour le détail des deux arbitrages) :

(a) le volume programmé compte tous les programmes, rejetés compris (V7,
    US-VAL-03), à l'exclusion du programme en cours d'évaluation (`ServiceContraintes.
    contexte`, `_charger_volumes`). Modifiée prompt 56 (R01-VAL03-03, défaut
    latent révélé par la preuve sur la session entière, docs/suivi/
    DECISIONS.md) : une séance se place tant que le volume déjà programmé
    (base + lot) de la matière, pour cette brigade, reste strictement
    inférieur au prescrit — même si la durée de CETTE séance fait dépasser
    le prescrit. Dès que le déjà-programmé atteint ou dépasse le prescrit,
    plus aucune séance de cette matière. Le dépassement final est donc
    toujours strictement inférieur à la durée d'une séance — hypothèse à
    faire valider par la cellule planification. Sans cette tolérance, une
    matière dont le reste exact ne correspond à aucun créneau existant ne
    pouvait plus jamais atteindre son prescrit (RG-39 b, ci-dessous, devenait
    inatteignable) ;
(b) un prérequis est « achevé » quand le volume RÉALISÉ (RG-60, US-SUI-01,
    prompt 44, R2) de la matière prérequise POUR CETTE BRIGADE, avant le
    début de la semaine générée, atteint son volume prescrit — définition
    provisoire (volume programmé) remplacée par celle-ci au sprint 4 :
    `contexte.volume_realise_par_element_brigade`
    (`planification.services.contraintes.volumes_realises_par_element_brigade`).
    Conséquence assumée : une semaine dont le programme n'est pas encore
    affiché ne fournit aucun prérequis à la suivante. Inchangée par le
    prompt 56 : le seuil restait déjà `>=`, désormais atteignable.

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
    """Prompt 55 (correction R01-VAL03-03) : filtré aussi par brigade — sans
    quoi deux brigades de la même session plaçant chacune la même matière
    dans le même lot se bloqueraient mutuellement, exactement le défaut
    corrigé ci-dessous pour `deja_programme`."""
    element = candidate.element_referentiel
    return sum(
        duree_heures(autre.debut, autre.fin)
        for autre in lot_acceptees
        if autre.element_referentiel.pk == element.pk and autre.brigade.pk == candidate.brigade.pk
    )


def _verifier_volume(candidate, contexte, lot_acceptees):
    """RG-39 a), modifiée prompt 56 : le volume déjà programmé (base + lot)
    d'une matière POUR UNE BRIGADE doit être strictement inférieur au
    prescrit pour qu'une séance supplémentaire se place — pas le total après
    cette séance. Une matière qui n'atteint jamais exactement son prescrit
    (reste plus petit que tout créneau existant) peut ainsi tout de même
    l'achever, au prix d'un dépassement toujours inférieur à la durée d'une
    séance (docs/suivi/DECISIONS.md, R01-VAL03-03, défaut latent révélé par
    la preuve sur la session entière). `volume_programme_par_element_
    brigade`, jamais un cumul par élément seul (corrigé prompt 55)."""
    element = candidate.element_referentiel
    deja_programme = contexte.volume_programme_par_element_brigade.get(
        (element.pk, candidate.brigade.pk), 0
    )
    avant = deja_programme + _volume_lot(candidate, lot_acceptees)
    if avant < element.volume_horaire_prescrit:
        return []
    origine = "base" if deja_programme >= element.volume_horaire_prescrit else "lot"
    return [
        violation(
            "RG-39",
            f"Le volume programmé de {element.matiere} a atteint {avant:.2f} h, "
            f"au moins le volume prescrit ({element.volume_horaire_prescrit} h) : "
            "plus aucune séance.",
            origine=origine,
        )
    ]


def _verifier_prerequis(candidate, contexte):
    element = candidate.element_referentiel
    prerequis = contexte.prerequis_par_element.get(element.pk, [])
    violations = []
    for element_prerequis in prerequis:
        cle = (element_prerequis.pk, candidate.brigade.pk)
        realise = contexte.volume_realise_par_element_brigade.get(cle, 0)
        if realise >= element_prerequis.volume_horaire_prescrit:
            continue
        violations.append(
            violation(
                "RG-39",
                f"{element_prerequis.matiere} est prérequise à {element.matiere} pour "
                f"{candidate.brigade} : {realise:.2f} h réalisées sur "
                f"{element_prerequis.volume_horaire_prescrit} h prescrites.",
            )
        )
    return violations
