"""RG-37 (et RG-40, mode de partage) — lieu de la séance. Trois sous-cas
explicites (§ 4, Prompt 30) : matière sans lieu (aucun contrôle), salle
attitrée (capacité contre l'effectif réel, exclusivité déjà garantie par
US-SES-03), lieu partagé (occupation ET capacité, sauf regroupement
explicite — sous réserve du mode de partage, RG-40).

CAPACITÉ NON RENSEIGNÉE = REFUS, aux deux points d'application (salle
attitrée et lieu partagé) : « on ne sait pas » n'est jamais lu comme
« illimité » (CLS-03) — même contrainte qu'à RG-13/RG-19 (US-SES-03,
US-SES-06), voir docs/suivi/DECISIONS.md. MODE DE PARTAGE NON RENSEIGNÉ
traité de la même façon : au moins aussi restrictif qu'un lieu séquentiel,
jamais une autorisation implicite de simultanéité.
"""

from noyau.intervalles import se_recouvrent
from planification.services.violations import violation
from referentiel.models import CategorieLieu
from ressources.models import ModePartage


def verifier_rg37(candidate, contexte, lot_acceptees):
    violations = _verifier_epreuves_lieu(candidate, contexte)
    if candidate.element_referentiel.categorie_lieu == CategorieLieu.AUCUN_LIEU:
        return violations
    return violations + _verifier_categorie(candidate, contexte, lot_acceptees)


def _verifier_categorie(candidate, contexte, lot_acceptees):
    if candidate.element_referentiel.categorie_lieu == CategorieLieu.SALLE_ATTITREE:
        return _verifier_salle_attitree(candidate, contexte)
    return _verifier_lieu_partage(candidate, contexte, lot_acceptees)


def _verifier_epreuves_lieu(candidate, contexte):
    """A6 (P5 → P6), Prompt 38 : un lieu occupé par une épreuve est occupé,
    comme par une séance. Le lieu visé est celui de la candidate, ou la salle
    attitrée de sa brigade à défaut."""
    lieu = candidate.lieu
    if lieu is None and candidate.element_referentiel.categorie_lieu != CategorieLieu.AUCUN_LIEU:
        lieu = contexte.salles_attitrees.get(candidate.brigade.pk)
    if lieu is None:
        return []
    for occupation in contexte.occupations_epreuves:
        if lieu.pk in occupation["lieux"] and se_recouvrent(
            candidate.debut, candidate.fin, occupation["debut"], occupation["fin"]
        ):
            return [
                violation(
                    "RG-37",
                    f"{lieu} est occupé par « {occupation['libelle']} » "
                    f"le {occupation['debut']:%d/%m %H:%M}–{occupation['fin']:%H:%M}.",
                )
            ]
    return []


def _verifier_indisponibilite(candidate, contexte, lieu):
    """Lieu déclaré indisponible (§ 0.3, Prompt 30 — `IndisponibiliteLieu`
    fait partie des modèles dont les six contraintes dépendent) : bloque
    quel que soit le sous-cas, avant même la capacité."""
    for debut, fin in contexte.indisponibilites_lieu.get(lieu.pk, []):
        if se_recouvrent(candidate.debut, candidate.fin, debut, fin):
            return [
                violation(
                    "RG-37",
                    f"{lieu} est déclaré indisponible du {debut:%d/%m %H:%M} au "
                    f"{fin:%d/%m %H:%M}.",
                )
            ]
    return []


def _verifier_salle_attitree(candidate, contexte):
    """Exclusivité déjà garantie par US-SES-03/D-90 : seule la capacité se
    revérifie ici, sur l'EFFECTIF RÉEL (qui a pu croître depuis
    l'attribution) — c'est le rattrapage consigné à US-SES-03."""
    salle = contexte.salles_attitrees.get(candidate.brigade.pk)
    if salle is None:
        return []
    indisponibilite = _verifier_indisponibilite(candidate, contexte, salle)
    if indisponibilite:
        return indisponibilite
    if salle.capacite is None:
        return [
            violation(
                "RG-37",
                f"La capacité de la salle attitrée de {candidate.brigade} n'est pas "
                "renseignée ; renseignez-la avant d'y programmer une séance.",
            )
        ]
    effectif = contexte.effectifs_reels.get(candidate.brigade.pk, 0)
    if salle.capacite < effectif:
        return [
            violation(
                "RG-37",
                f"La salle attitrée de {candidate.brigade} (capacité {salle.capacite}) "
                f"est insuffisante pour l'effectif réel ({effectif}), écart de "
                f"{effectif - salle.capacite}.",
            )
        ]
    return []


def _occupant_brigade_et_effectif(contexte, occupant):
    """`occupant` est soit une `Seance` existante (brigades via ses lignes
    de programme), soit une `Candidate` déjà acceptée du même lot (une
    seule brigade)."""
    if hasattr(occupant, "lignes"):
        lignes = list(occupant.lignes.all())
        libelle = ", ".join(str(ligne.brigade) for ligne in lignes)
        effectif = sum(contexte.effectifs_reels.get(ligne.brigade_id, 0) for ligne in lignes)
        return libelle, effectif
    return str(occupant.brigade), contexte.effectifs_reels.get(occupant.brigade.pk, 0)


def _cle_regroupement(occupant):
    return occupant.pk if hasattr(occupant, "lignes") else occupant.cle_regroupement


def _occupants_du_lieu(candidate, contexte, lot_acceptees):
    occupants = []
    for seance in contexte.seances_existantes:
        if seance.lieu_id == candidate.lieu.pk and se_recouvrent(
            candidate.debut, candidate.fin, seance.debut, seance.fin
        ):
            occupants.append((seance, "base"))
    for autre in lot_acceptees:
        if (
            autre.lieu is not None
            and autre.lieu.pk == candidate.lieu.pk
            and se_recouvrent(candidate.debut, candidate.fin, autre.debut, autre.fin)
        ):
            occupants.append((autre, "lot"))
    return occupants


def _verifier_occupation(candidate, contexte, occupants, mode):
    """Rend `(violations, effectif_regroupe)` : une occupation non
    conciliable (pas le même regroupement, ou lieu séquentiel/mode
    inconnu) refuse immédiatement ; un regroupement simultané valide
    ajoute son effectif au total à comparer à la capacité."""
    effectif_regroupe = contexte.effectifs_reels.get(candidate.brigade.pk, 0)
    for occupant, origine in occupants:
        meme_regroupement = (
            candidate.cle_regroupement is not None
            and candidate.cle_regroupement == _cle_regroupement(occupant)
        )
        if meme_regroupement and mode == ModePartage.SIMULTANE:
            _, effectif_occupant = _occupant_brigade_et_effectif(contexte, occupant)
            effectif_regroupe += effectif_occupant
            continue
        libelle, _ = _occupant_brigade_et_effectif(contexte, occupant)
        return (
            [
                violation(
                    "RG-37",
                    f"{candidate.lieu} est déjà occupé le {candidate.debut:%d/%m %H:%M}–"
                    f"{candidate.fin:%H:%M} par {libelle}.",
                    origine=origine,
                )
            ],
            effectif_regroupe,
        )
    return [], effectif_regroupe


def _verifier_capacite_partagee(candidate, effectif_regroupe):
    if candidate.lieu.capacite is None:
        return [
            violation(
                "RG-37",
                f"La capacité de {candidate.lieu} n'est pas renseignée ; renseignez-la "
                "avant d'y programmer une séance.",
            )
        ]
    if candidate.lieu.capacite < effectif_regroupe:
        return [
            violation(
                "RG-37",
                f"{candidate.lieu} (capacité {candidate.lieu.capacite}) est insuffisant "
                f"pour l'effectif regroupé ({effectif_regroupe}), écart de "
                f"{effectif_regroupe - candidate.lieu.capacite}.",
            )
        ]
    return []


def _verifier_lieu_partage(candidate, contexte, lot_acceptees):
    indisponibilite = _verifier_indisponibilite(candidate, contexte, candidate.lieu)
    if indisponibilite:
        return indisponibilite
    occupants = _occupants_du_lieu(candidate, contexte, lot_acceptees)
    violations, effectif_regroupe = _verifier_occupation(
        candidate, contexte, occupants, candidate.lieu.mode_partage
    )
    if violations:
        return violations
    return _verifier_capacite_partagee(candidate, effectif_regroupe)
