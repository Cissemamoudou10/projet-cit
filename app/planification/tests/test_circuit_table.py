"""US-VAL-03, groupe A — oracle des transitions (V2, ETA-01 § 4.1).

Les 55 cas se lisent dans `docs/conception/ETA-01_table_transitions.md` : chaque
case porte le nom de son test. Le document fait foi ; la constante `TRANSITIONS`
doit le reproduire exactement, ni plus ni moins (test de concordance).
"""

from pathlib import Path

import pytest

from planification.models import EtatProgramme
from planification.services.circuit import (
    AFFICHER,
    ANNULER_VALIDATION,
    ECRIRE_SEANCE,
    GENERER,
    PORTER_AVENANT,
    REJETER,
    REPRENDRE,
    RETIRER_SOUMISSION,
    SIGNER,
    SOUMETTRE,
    TRANSITIONS,
    VALIDER,
    motif_refus_action,
)

DOCUMENT = (
    Path(__file__).resolve().parents[3] / "docs" / "conception" / "ETA-01_table_transitions.md"
)

ETATS_DU_DOCUMENT = [
    EtatProgramme.BROUILLON,
    EtatProgramme.SOUMIS,
    EtatProgramme.REJETE,
    EtatProgramme.VALIDE,
    EtatProgramme.AFFICHE,
]

# Libellé de ligne du document → événement de la table. Le préfixe suffit.
EVENEMENTS_DU_DOCUMENT = [
    ("soumettre", SOUMETTRE),
    ("retirer la soumission", RETIRER_SOUMISSION),
    ("valider", VALIDER),
    ("rejeter", REJETER),
    ("reprendre en correction", REPRENDRE),
    ("enregistrer la signature", SIGNER),
    ("afficher", AFFICHER),
    ("annuler la validation", ANNULER_VALIDATION),
    ("porter un avenant", PORTER_AVENANT),
    ("modifier / ajouter / supprimer une séance", ECRIRE_SEANCE),
    ("générer", GENERER),
]

LIGNE_EVENEMENT = "| **"
LIGNE_NOMS_DE_TESTS = "| ↳ tests |"


def _cellules(ligne):
    return [cellule.strip() for cellule in ligne.strip().strip("|").split("|")]


def _evenement_du_libelle(libelle):
    for prefixe, evenement in EVENEMENTS_DU_DOCUMENT:
        if libelle.startswith(prefixe):
            return evenement
    raise AssertionError(f"Événement inconnu dans ETA-01 : « {libelle} »")


def _cas_du_document():
    """(nom du test, état, événement, admis) pour chaque cellule du § 4.1.
    Une cellule commençant par « refus » est refusée ; les autres sont admises
    (« T<n> → », « admis », « T<n>, reste… »)."""
    cas = []
    evenement, resultats = None, []
    for ligne in DOCUMENT.read_text(encoding="utf-8").splitlines():
        if ligne.startswith(LIGNE_EVENEMENT):
            libelle = ligne.split("**")[1]
            evenement = _evenement_du_libelle(libelle)
            resultats = _cellules(ligne)[1:]
        elif ligne.startswith(LIGNE_NOMS_DE_TESTS):
            noms = [nom.strip("`") for nom in _cellules(ligne)[1:]]
            for etat, resultat, nom in zip(ETATS_DU_DOCUMENT, resultats, noms, strict=True):
                cas.append((nom, etat, evenement, not resultat.startswith("refus")))
    return cas


CAS = _cas_du_document()


def test_le_document_compte_55_cas():
    assert len(CAS) == 55


@pytest.mark.parametrize(
    "nom,etat,evenement,admis",
    CAS,
    ids=[cas[0] for cas in CAS],
)
def test_cas_du_document_est_celui_de_la_table(nom, etat, evenement, admis):
    assert ((evenement, etat) in TRANSITIONS) is admis
    assert (motif_refus_action(evenement, etat) is None) is admis


def test_la_table_ne_contient_que_les_cases_admises_du_document():
    """Concordance : document et constante ne peuvent plus diverger sans faire
    échouer la suite (V2)."""
    admises_du_document = {(evenement, etat) for _, etat, evenement, admis in CAS if admis}
    assert set(TRANSITIONS) == admises_du_document


def test_les_transitions_t2_a_t10_sont_toutes_presentes():
    numeros = {transition.numero for transition in TRANSITIONS.values()}
    assert {f"T{n}" for n in range(2, 11)} <= numeros
