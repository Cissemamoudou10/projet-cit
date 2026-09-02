# -*- coding: utf-8 -*-
"""Contrôles de qualité du code.

La modularité se mesure. Un fichier de mille lignes n'est pas modulaire, quelle
que soit l'intention de son auteur. Ces tests rendent les limites opposables.

Lancer après chaque série d'éditions : pytest tests/architecture -q
"""
import ast
import pathlib

RACINE = pathlib.Path(__file__).resolve().parents[2]
APP = RACINE / "app"

LIGNES_MAX_FICHIER = 400
LIGNES_MAX_FONCTION = 40
LIGNES_MAX_CLASSE = 200
PARAMETRES_MAX = 5


def sources():
    if not APP.exists():
        return []
    return [
        c for c in APP.rglob("*.py")
        if "migrations" not in c.parts and "__pycache__" not in c.parts
    ]


def longueur(noeud, texte):
    fin = getattr(noeud, "end_lineno", None)
    return (fin - noeud.lineno + 1) if fin else 0


def test_aucun_fichier_ne_depasse_400_lignes():
    """Au-delà, scinder en module : services/generation.py, services/contraintes.py."""
    fautifs = []
    for chemin in sources():
        n = len(chemin.read_text(encoding="utf-8").splitlines())
        if n > LIGNES_MAX_FICHIER:
            fautifs.append("%s : %d lignes" % (chemin.relative_to(RACINE), n))
    assert not fautifs, (
        "Fichier trop long — scinder en module :\n" + "\n".join(fautifs))


def test_aucune_fonction_ne_depasse_40_lignes():
    """Au-delà, extraire des fonctions nommées."""
    fautifs = []
    for chemin in sources():
        texte = chemin.read_text(encoding="utf-8")
        for noeud in ast.walk(ast.parse(texte)):
            if isinstance(noeud, (ast.FunctionDef, ast.AsyncFunctionDef)):
                n = longueur(noeud, texte)
                if n > LIGNES_MAX_FONCTION:
                    fautifs.append("%s ligne %d : %s, %d lignes"
                                   % (chemin.relative_to(RACINE), noeud.lineno, noeud.name, n))
    assert not fautifs, (
        "Fonction trop longue — extraire :\n" + "\n".join(fautifs))


def test_aucune_classe_ne_depasse_200_lignes():
    fautifs = []
    for chemin in sources():
        texte = chemin.read_text(encoding="utf-8")
        for noeud in ast.walk(ast.parse(texte)):
            if isinstance(noeud, ast.ClassDef):
                n = longueur(noeud, texte)
                if n > LIGNES_MAX_CLASSE:
                    fautifs.append("%s ligne %d : %s, %d lignes"
                                   % (chemin.relative_to(RACINE), noeud.lineno, noeud.name, n))
    assert not fautifs, (
        "Classe trop longue — déplacer la logique dans un service :\n" + "\n".join(fautifs))


def test_aucune_fonction_n_a_plus_de_cinq_parametres():
    """Au-delà, regrouper dans un objet."""
    fautifs = []
    for chemin in sources():
        texte = chemin.read_text(encoding="utf-8")
        for noeud in ast.walk(ast.parse(texte)):
            if isinstance(noeud, (ast.FunctionDef, ast.AsyncFunctionDef)):
                args = noeud.args
                n = len(args.args) + len(args.kwonlyargs) + len(args.posonlyargs)
                if args.args and args.args[0].arg in ("self", "cls"):
                    n -= 1
                if n > PARAMETRES_MAX:
                    fautifs.append("%s ligne %d : %s, %d paramètres"
                                   % (chemin.relative_to(RACINE), noeud.lineno, noeud.name, n))
    assert not fautifs, "Trop de paramètres :\n" + "\n".join(fautifs)


def test_aucune_regle_metier_dans_un_signal():
    """Un signal exécute du code invisible depuis l'appelant : intraçable et fragile."""
    fautifs = []
    for chemin in sources():
        texte = chemin.read_text(encoding="utf-8")
        if "@receiver" not in texte and "post_save.connect" not in texte:
            continue
        if "service" in texte.lower():
            fautifs.append(str(chemin.relative_to(RACINE)))
    assert not fautifs, (
        "Appel de service depuis un signal — le rendre explicite :\n" + "\n".join(fautifs))


def test_aucun_import_generique_ni_print():
    fautifs = []
    for chemin in sources():
        if "settings" in chemin.name:
            continue
        for i, ligne in enumerate(chemin.read_text(encoding="utf-8").splitlines(), 1):
            nu = ligne.strip()
            if nu.startswith("from ") and nu.endswith("import *"):
                fautifs.append("%s ligne %d : import générique" % (chemin.relative_to(RACINE), i))
            if nu.startswith("print("):
                fautifs.append("%s ligne %d : print — utiliser le journal"
                               % (chemin.relative_to(RACINE), i))
    assert not fautifs, "\n".join(fautifs)


def test_nommage_des_contraintes_de_migration():
    """ck_ pour une vérification, uq_ pour une unicité, ex_ pour une exclusion, idx_ pour un index."""
    import re
    prefixes = {"CheckConstraint": "ck_", "UniqueConstraint": "uq_", "ExclusionConstraint": "ex_"}
    fautifs = []
    if not APP.exists():
        return
    for chemin in APP.rglob("migrations/*.py"):
        texte = chemin.read_text(encoding="utf-8")
        for classe, prefixe in prefixes.items():
            for bloc in re.finditer(classe + r"\((.{0,400}?)\)", texte, re.S):
                nom = re.search(r'name\s*=\s*["\']([^"\']+)["\']', bloc.group(1))
                if nom and not nom.group(1).startswith(prefixe):
                    fautifs.append("%s : %s devrait commencer par %s"
                                   % (chemin.relative_to(RACINE), nom.group(1), prefixe))
        for bloc in re.finditer(r"models\.Index\((.{0,300}?)\)", texte, re.S):
            nom = re.search(r'name\s*=\s*["\']([^"\']+)["\']', bloc.group(1))
            if nom and not nom.group(1).startswith("idx_"):
                fautifs.append("%s : %s devrait commencer par idx_"
                               % (chemin.relative_to(RACINE), nom.group(1)))
    assert not fautifs, "Nommage de contrainte non conforme :\n" + "\n".join(fautifs)
