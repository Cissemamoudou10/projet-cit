"""US-SUI-06 (prompt 45, Temps 2) : le dispensé de la progression réalisée
réutilise la fonction du réalisé posée à US-SUI-01, jamais un second calcul
— `.claude/rules/modeles.md` (aucun attribut dérivé, une seule
implantation) et `.claude/rules/services.md` (contrôles qui ont une seule
implantation).
"""

import pathlib

RACINE = pathlib.Path(__file__).resolve().parents[2]
CHEMIN_SELECTEUR = RACINE / "app" / "planification" / "selectors_progression.py"


def test_aucun_calcul_de_dispense_hors_de_la_fonction_d_us_sui_01():
    texte = CHEMIN_SELECTEUR.read_text(encoding="utf-8")
    assert "volumes_realises_par_element_brigade" in texte, (
        "selectors_progression.py doit appeler la fonction du réalisé d'US-SUI-01, "
        "pas la redéfinir."
    )
    assert "EtatProgramme.AFFICHE" not in texte, (
        "Filtre sur l'état affiché dupliqué dans selectors_progression.py : "
        "cette décision vit dans volumes_realises_par_element_brigade (US-SUI-01), "
        "nulle part ailleurs."
    )
    assert "non_execution__isnull" not in texte, (
        "Exclusion des non-exécutions dupliquée dans selectors_progression.py : "
        "cette décision vit dans volumes_realises_par_element_brigade (US-SUI-01) — "
        "ce module ne fait que LISTER les non-exécutions (`_ecarts_de_la_semaine`), "
        "jamais les retrancher lui-même d'un volume."
    )
