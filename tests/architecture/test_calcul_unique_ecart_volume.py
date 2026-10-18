"""US-PLAN-07 (prompt 47, Temps 2) : le signalement des écarts de volume
horaire réutilise le prescrit et le programmé posés à US-SUI-01, jamais un
second calcul — `.claude/rules/modeles.md` (aucun attribut dérivé, une seule
implantation) et `.claude/rules/services.md` (contrôles qui ont une seule
implantation). Même patron que
`test_calcul_unique_progression.py` (US-SUI-06).
"""

import pathlib

RACINE = pathlib.Path(__file__).resolve().parents[2]
CHEMIN_SELECTEUR = RACINE / "app" / "planification" / "selectors_ecart_volume.py"


def test_aucun_calcul_de_programme_hors_de_la_fonction_d_us_sui_01():
    texte = CHEMIN_SELECTEUR.read_text(encoding="utf-8")
    assert "volumes_programmes_par_element_brigade" in texte, (
        "selectors_ecart_volume.py doit appeler la fonction du programmé d'US-SUI-01, "
        "pas la redéfinir."
    )
    assert "LigneProgramme.objects" not in texte, (
        "Agrégation du programmé dupliquée dans selectors_ecart_volume.py : cette "
        "décision vit dans volumes_programmes_par_element_brigade (US-SUI-01), nulle "
        "part ailleurs."
    )
    assert "volumes_realises_par_element_brigade" not in texte, (
        "Le réalisé n'entre pas dans le périmètre d'US-PLAN-07 (prescrit/programmé "
        "seulement) : son calcul ne doit jamais être importé ici."
    )
