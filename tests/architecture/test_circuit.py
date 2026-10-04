"""Architecture du circuit du programme (US-VAL-03, V1 et V3).

H1 — une seule main écrit l'état du programme : `ServiceCircuitProgramme`.
H2 — aucune suppression de séance hors de la génération, et la génération
     comme la porte d'écriture appellent la garde AVANT toute écriture.
"""

import ast
import pathlib

RACINE = pathlib.Path(__file__).resolve().parents[2]
SRC = RACINE / "app"
CIRCUIT = SRC / "planification" / "services" / "circuit.py"
GENERATION = SRC / "planification" / "services" / "generation.py"
ECRITURE = SRC / "planification" / "services" / "ecriture.py"

METHODES_D_ECRITURE = {
    "update",
    "create",
    "get_or_create",
    "update_or_create",
    "bulk_create",
    "bulk_update",
}


def _fichiers_de_production():
    return [
        chemin
        for chemin in SRC.rglob("*.py")
        if "migrations" not in chemin.parts and "tests" not in chemin.parts
    ]


def _arbre(chemin):
    return ast.parse(chemin.read_text(encoding="utf-8"))


def _nom_de_l_appel(appel):
    fonction = appel.func
    if isinstance(fonction, ast.Attribute):
        return fonction.attr
    if isinstance(fonction, ast.Name):
        return fonction.id
    return ""


def _affectations_de_l_etat(arbre):
    """Lignes où l'état est affecté : `x.etat = …`, ou `etat=` passé à une
    méthode d'écriture de l'ORM (`update`, `create`, …)."""
    lignes = []
    for noeud in ast.walk(arbre):
        if isinstance(noeud, ast.Assign | ast.AugAssign | ast.AnnAssign):
            cibles = noeud.targets if isinstance(noeud, ast.Assign) else [noeud.target]
            lignes += [
                c.lineno for c in cibles if isinstance(c, ast.Attribute) and c.attr == "etat"
            ]
        if isinstance(noeud, ast.Call):
            lignes += _affectations_par_appel(noeud)
    return lignes


def _affectations_par_appel(appel):
    """`etat=` passé à l'ORM, `ProgrammeHebdomadaire(etat=…)`, `setattr(x,
    "etat", …)` et `defaults={"etat": …}` : quatre façons d'affecter l'état."""
    nom = _nom_de_l_appel(appel)
    lignes = []
    if nom in METHODES_D_ECRITURE or nom == "ProgrammeHebdomadaire":
        lignes += [k.lineno for k in appel.keywords if k.arg == "etat"]
    if nom == "setattr" and len(appel.args) >= 2:
        if isinstance(appel.args[1], ast.Constant) and appel.args[1].value == "etat":
            lignes.append(appel.lineno)
    for argument in appel.keywords:
        if argument.arg == "defaults" and isinstance(argument.value, ast.Dict):
            lignes += [
                cle.lineno
                for cle in argument.value.keys
                if isinstance(cle, ast.Constant) and cle.value == "etat"
            ]
    return lignes


def test_h1_aucune_affectation_de_l_etat_hors_du_service_du_circuit():
    fautifs = []
    for chemin in _fichiers_de_production():
        if chemin == CIRCUIT:
            continue
        for ligne in _affectations_de_l_etat(_arbre(chemin)):
            fautifs.append(f"{chemin.relative_to(RACINE)} ligne {ligne}")
    assert not fautifs, "État du programme affecté hors de ServiceCircuitProgramme :\n" + "\n".join(
        fautifs
    )


def test_h1_le_service_du_circuit_affecte_bien_l_etat():
    """Garde-fou du garde-fou : le motif de détection voit la vraie affectation."""
    assert _affectations_de_l_etat(_arbre(CIRCUIT)), "le détecteur ne voit plus l'affectation"


def test_h2_seules_les_suppressions_de_seances_passent_par_la_generation():
    fautifs = []
    for chemin in _fichiers_de_production():
        texte = chemin.read_text(encoding="utf-8")
        arbre = ast.parse(texte)
        for noeud in ast.walk(arbre):
            if not (isinstance(noeud, ast.Call) and _nom_de_l_appel(noeud) == "delete"):
                continue
            if not isinstance(noeud.func, ast.Attribute):
                continue
            segment = ast.get_source_segment(texte, noeud.func.value) or ""
            if ("Seance" in segment or "seance" in segment.lower()) and chemin != GENERATION:
                fautifs.append(f"{chemin.relative_to(RACINE)} ligne {noeud.lineno}")
    assert not fautifs, "Suppression de séance hors de la génération :\n" + "\n".join(fautifs)


def _lignes_d_appel(chemin, nom_appele, nom_fonction=None):
    arbre = _arbre(chemin)
    portees = [arbre]
    if nom_fonction is not None:
        portees = [
            noeud
            for noeud in ast.walk(arbre)
            if isinstance(noeud, ast.FunctionDef) and noeud.name == nom_fonction
        ]
    return sorted(
        noeud.lineno
        for portee in portees
        for noeud in ast.walk(portee)
        if isinstance(noeud, ast.Call) and _nom_de_l_appel(noeud) == nom_appele
    )


def test_h2_la_generation_appelle_la_garde_avant_la_suppression():
    gardes = _lignes_d_appel(GENERATION, "garde_modification", "_generer_dans_programme")
    suppressions = _lignes_d_appel(GENERATION, "_supprimer_seances_regenerees")
    assert gardes and suppressions
    assert gardes[0] < suppressions[0], "la garde doit précéder la suppression des séances"


def test_h2_la_porte_d_ecriture_appelle_la_garde_dans_chaque_chemin():
    """`_verifier_et_creer` (saisie et contrôle) et `creer_seances` (lot) : les
    deux chemins qui créent des séances passent par la garde."""
    assert _lignes_d_appel(ECRITURE, "garde_modification", "_verifier_et_creer")
    assert _lignes_d_appel(ECRITURE, "garde_modification", "creer_seances")
