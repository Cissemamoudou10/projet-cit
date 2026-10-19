"""US-REF-09, E2 (prompt 48) : « les écritures passent par les services du
référentiel ; un test d'architecture vérifie qu'aucune n'y échappe » — sans
quoi l'historisation (E1, le journal) resterait contournable par un import
ou une commande qui construirait `Formation`/`Matiere`/`ElementReferentiel`/
`Prerequis` directement. Même patron que `tests/architecture/test_couches.py::
test_seule_la_porte_d_ecriture_instancie_seance_ou_ligne_programme`.
"""

import pathlib
import re

RACINE = pathlib.Path(__file__).resolve().parents[2]
SRC = RACINE / "app"

SERVICES_REFERENTIEL = {
    SRC / "referentiel" / "services" / "formation.py",
    SRC / "referentiel" / "services" / "matiere.py",
    SRC / "referentiel" / "services" / "referentiel.py",
    SRC / "referentiel" / "services" / "prerequis.py",
}
MODELES = SRC / "referentiel" / "models.py"

MOTIFS = (
    "Formation(",
    "Matiere(",
    "ElementReferentiel(",
    "Prerequis(",
    "Formation.objects.create(",
    "Matiere.objects.create(",
    "ElementReferentiel.objects.create(",
    "Prerequis.objects.create(",
)


def _fichiers():
    if not SRC.exists():
        return []
    return [c for c in SRC.rglob("*.py") if "migrations" not in c.parts]


def test_toute_ecriture_du_referentiel_passe_par_ses_services():
    """E2 : formation, matière du catalogue, élément de référentiel et
    prérequis — les quatre entités de ce périmètre, jamais `TypeFormation`
    ni `ObjectifPedagogique`, hors du périmètre de cette story."""
    fautifs = []
    for chemin in _fichiers():
        if chemin in SERVICES_REFERENTIEL or chemin == MODELES or "tests" in chemin.parts:
            continue
        texte = chemin.read_text(encoding="utf-8")
        for i, ligne in enumerate(texte.splitlines(), 1):
            if ligne.lstrip().startswith("#"):
                continue
            for motif in MOTIFS:
                if re.search(r"(?<![A-Za-z0-9_])" + re.escape(motif), ligne):
                    fautifs.append(
                        "%s ligne %d : %s" % (chemin.relative_to(RACINE), i, ligne.strip())
                    )
    assert not fautifs, (
        "Instanciation d'une entité du référentiel hors de ses services :\n"
        + "\n".join(fautifs)
    )
