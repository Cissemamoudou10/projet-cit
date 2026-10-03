"""RG-34 à RG-36 — unicité d'affectation, qualification, disponibilité de
l'instructeur. Fonctions pures : candidate + contexte (+ lot pour RG-34) en
entrée, liste de violations en sortie — jamais d'écriture, voir
`planification.services.contraintes`.
"""

from noyau.intervalles import se_recouvrent
from planification.services.violations import violation


def _rg34_conflits_existants(candidate, seances_existantes):
    violations = []
    for seance in seances_existantes:
        if seance.instructeur_id != candidate.instructeur.pk:
            continue
        if not se_recouvrent(candidate.debut, candidate.fin, seance.debut, seance.fin):
            continue
        brigades = ", ".join(str(ligne.brigade) for ligne in seance.lignes.all())
        violations.append(
            violation(
                "RG-34",
                f"{candidate.instructeur} est déjà affecté à une séance de "
                f"{seance.element_referentiel.matiere} ({brigades}) le "
                f"{seance.debut:%d/%m %H:%M}–{seance.fin:%H:%M}.",
                origine="base",
            )
        )
    return violations


def _rg34_conflits_lot(candidate, lot_acceptees):
    violations = []
    for autre in lot_acceptees:
        if autre.instructeur.pk != candidate.instructeur.pk:
            continue
        if (
            candidate.cle_regroupement is not None
            and candidate.cle_regroupement == autre.cle_regroupement
        ):
            continue
        if not se_recouvrent(candidate.debut, candidate.fin, autre.debut, autre.fin):
            continue
        violations.append(
            violation(
                "RG-34",
                f"{candidate.instructeur} est déjà retenu, dans ce même lot, pour "
                f"{autre.element_referentiel.matiere} ({autre.brigade}) le "
                f"{autre.debut:%d/%m %H:%M}–{autre.fin:%H:%M}.",
                origine="lot",
            )
        )
    return violations


def verifier_rg34(candidate, contexte, lot_acceptees):
    """Unicité d'affectation de l'instructeur, toutes brigades et TOUTES
    SESSIONS confondues — portée centre entier obtenue par construction
    (`Seance.programme` couvre déjà tout le centre, RG-33 bis). EXCEPTION :
    la séance regroupée (même `cle_regroupement` non nul) n'est pas un
    conflit."""
    return _rg34_conflits_existants(candidate, contexte.seances_existantes) + _rg34_conflits_lot(
        candidate, lot_acceptees
    )


def verifier_rg35(candidate, contexte):
    """Qualification pour la MATIÈRE DU CATALOGUE, jamais pour l'élément de
    référentiel — « l'habilitation est indépendante de la formation »
    (CLS-03)."""
    matiere = candidate.element_referentiel.matiere
    cle = (candidate.instructeur.pk, matiere.pk)
    if cle in contexte.qualifications:
        return []
    return [
        violation(
            "RG-35",
            f"{candidate.instructeur} n'est pas qualifié pour {matiere}.",
        )
    ]


def verifier_rg36(candidate, contexte):
    """Aucun recouvrement avec une indisponibilité déclarée — bornes
    semi-ouvertes, alignées sur US-INS-03."""
    indisponibilites = contexte.indisponibilites_instructeur.get(candidate.instructeur.pk, [])
    violations = []
    for debut, fin in indisponibilites:
        if se_recouvrent(candidate.debut, candidate.fin, debut, fin):
            violations.append(
                violation(
                    "RG-36",
                    f"{candidate.instructeur} est déclaré indisponible du "
                    f"{debut:%d/%m %H:%M} au {fin:%d/%m %H:%M}.",
                )
            )
    return violations
