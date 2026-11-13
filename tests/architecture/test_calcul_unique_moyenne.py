"""US-EVAL-12 (prompt 64) : `ServiceMoyenne.calculer` (liste des moyennes,
US-EVAL-06) et `ServiceMoyenne.detailler` (détail par module d'un
stagiaire, US-EVAL-12) — toutes deux dans `evaluations/services/moyenne.py`
— partagent le même moteur de calcul par module, `_note_module`, appelée
uniquement via `_resultat_stagiaire`, défini dans
`evaluations/services/calcul_moyenne.py`. Aucune des deux méthodes ne doit
réimplanter le calcul d'une note de module ou d'une moyenne pondérée (même
patron que test_calcul_unique_statut_volume.py,
test_calcul_unique_progression.py, test_calcul_unique_ecart_volume.py).
"""

import pathlib

RACINE = pathlib.Path(__file__).resolve().parents[2]
SRC = RACINE / "app"
MOTEUR = SRC / "evaluations" / "services" / "calcul_moyenne.py"
SERVICE = SRC / "evaluations" / "services" / "moyenne.py"
VUE = SRC / "evaluations" / "views_moyennes.py"


def test_une_seule_definition_du_calcul_de_module():
    occurrences = [
        chemin
        for chemin in SRC.rglob("*.py")
        if "def _note_module(" in chemin.read_text(encoding="utf-8")
    ]
    assert occurrences == [MOTEUR], (
        "_note_module doit être définie une seule fois, dans "
        "evaluations/services/calcul_moyenne.py :\n"
        + "\n".join(str(chemin.relative_to(RACINE)) for chemin in occurrences)
    )


def test_une_seule_definition_du_resultat_par_stagiaire():
    occurrences = [
        chemin
        for chemin in SRC.rglob("*.py")
        if "def _resultat_stagiaire(" in chemin.read_text(encoding="utf-8")
    ]
    assert occurrences == [MOTEUR], (
        "_resultat_stagiaire doit être définie une seule fois, dans "
        "evaluations/services/calcul_moyenne.py :\n"
        + "\n".join(str(chemin.relative_to(RACINE)) for chemin in occurrences)
    )


def test_le_service_importe_le_moteur_au_lieu_de_le_redefinir():
    texte = SERVICE.read_text(encoding="utf-8")
    assert "from evaluations.services.calcul_moyenne import" in texte, (
        "moyenne.py doit importer _resultat_stagiaire depuis calcul_moyenne.py, "
        "jamais en redéfinir une copie."
    )
    # `calculer()` l'appelle directement ; `detailler()` passe par
    # `_resultats_et_detail_stagiaire`, qui l'appelle à son tour — jamais une
    # troisième implantation du calcul.
    assert texte.count("_resultat_stagiaire(") >= 2, (
        "calculer() et _resultats_et_detail_stagiaire() (utilisée par detailler()) "
        "doivent toutes deux appeler _resultat_stagiaire — même moteur de calcul, "
        "jamais une moyenne réimplantée séparément."
    )
    assert "_resultats_et_detail_stagiaire(" in texte.split("def detailler(")[1], (
        "detailler() doit réutiliser _resultats_et_detail_stagiaire, jamais "
        "reparcourir les affectations avec une seconde implantation."
    )


def test_la_vue_ne_recalcule_jamais_une_note_de_module():
    texte = VUE.read_text(encoding="utf-8")
    for motif_interdit in ("poids_formatif", "poids_certificatif", "total_poids"):
        assert motif_interdit not in texte, (
            f"views_moyennes.py ne doit jamais manipuler {motif_interdit!r} — "
            "le calcul d'une note de module est le rôle exclusif de "
            "evaluations/services/moyenne.py::_note_module."
        )
