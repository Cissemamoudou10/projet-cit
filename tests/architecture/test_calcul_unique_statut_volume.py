"""US-PLAN-07 (prompt 47) et US-SUI-02 (prompt 48, Temps 0, D-282) partagent
une seule fonction de statut d'écart de volume horaire — `statut_volume`,
`app/planification/statut_volume.py`. Aucun des deux appelants ne doit en
redéfinir une seconde implantation (même patron que
`test_calcul_unique_progression.py`, `test_calcul_unique_ecart_volume.py`).
"""

import pathlib

RACINE = pathlib.Path(__file__).resolve().parents[2]
SRC = RACINE / "app"
DEFINITION = SRC / "planification" / "statut_volume.py"
PLAN07 = SRC / "planification" / "selectors_ecart_volume.py"
SUI02 = SRC / "planification" / "selectors_alerte_ecart.py"


def test_une_seule_definition_de_statut_volume():
    occurrences = [
        chemin
        for chemin in SRC.rglob("*.py")
        if "def statut_volume(" in chemin.read_text(encoding="utf-8")
    ]
    assert occurrences == [DEFINITION], (
        "statut_volume doit être défini une seule fois, dans planification/statut_volume.py :\n"
        + "\n".join(str(chemin.relative_to(RACINE)) for chemin in occurrences)
    )


def test_plan07_et_sui02_appellent_la_fonction_partagee():
    for chemin in (PLAN07, SUI02):
        texte = chemin.read_text(encoding="utf-8")
        assert "from planification.statut_volume import" in texte, (
            f"{chemin.relative_to(RACINE)} doit importer statut_volume depuis "
            "planification/statut_volume.py, pas en redéfinir une copie."
        )
