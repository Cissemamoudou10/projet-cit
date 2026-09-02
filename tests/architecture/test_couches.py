# -*- coding: utf-8 -*-
"""Contrôles d'architecture.

Ces tests vérifient ce que les consignes ne garantissent pas. Une instruction
écrite est suivie la plupart du temps ; un test qui échoue l'est toujours.

Lancer après chaque série d'éditions : pytest tests/architecture -q
"""
import ast
import pathlib
import re

RACINE = pathlib.Path(__file__).resolve().parents[2]
SRC = RACINE / "app"

APPLICATIONS = [
    "noyau", "administration", "referentiel", "organisation",
    "ressources", "planification", "evaluations",
]

# Ordre de dépendance arrêté en conception : une application ne peut importer
# que celles qui la précèdent.
DEPENDANCES_AUTORISEES = {
    "noyau": set(),
    "administration": {"noyau"},
    "referentiel": {"noyau", "administration"},
    "ressources": {"noyau", "administration", "referentiel"},
    "organisation": {"noyau", "administration", "referentiel", "ressources"},
    "planification": {"noyau", "administration", "referentiel", "ressources", "organisation"},
    "evaluations": {"noyau", "administration", "referentiel", "ressources", "organisation", "planification"},
}

ATTRIBUTS_DERIVES = [
    "volume_programme", "volume_realise", "volume_restant", "effectif_reel",
    "charge_hebdomadaire", "portee", "duree_heures", "est_regroupee",
    "volume_cumule",
]


def fichiers(motif):
    if not SRC.exists():
        return []
    return [c for c in SRC.rglob(motif) if "migrations" not in c.parts]


def application_de(chemin):
    for partie in chemin.parts:
        if partie in APPLICATIONS:
            return partie
    return None


def test_aucune_vue_n_importe_un_modele():
    """Une vue appelle un service ; elle ne touche pas aux modèles."""
    fautifs = []
    for chemin in fichiers("views.py") + fichiers("views/*.py"):
        texte = chemin.read_text(encoding="utf-8")
        for noeud in ast.walk(ast.parse(texte)):
            if isinstance(noeud, ast.ImportFrom) and noeud.module:
                if noeud.module.endswith("models") or ".models" in noeud.module:
                    fautifs.append("%s ligne %d : %s" % (chemin.relative_to(RACINE), noeud.lineno, noeud.module))
    assert not fautifs, "Import de modèle dans une vue :\n" + "\n".join(fautifs)


def test_aucun_service_ne_manipule_la_requete():
    """Un service ignore HTTP : il reçoit des objets, retourne des objets."""
    interdits = ("HttpResponse", "HttpRequest", "redirect(", "render(", "messages.")
    fautifs = []
    for chemin in fichiers("services.py") + fichiers("services/*.py"):
        texte = chemin.read_text(encoding="utf-8")
        for i, ligne in enumerate(texte.splitlines(), 1):
            if ligne.lstrip().startswith("#"):
                continue
            for terme in interdits:
                if terme in ligne:
                    fautifs.append("%s ligne %d : %s" % (chemin.relative_to(RACINE), i, terme))
    assert not fautifs, "Objet HTTP dans un service :\n" + "\n".join(fautifs)


def test_aucun_attribut_derive_n_est_un_champ():
    """Les neuf grandeurs dérivées se calculent et ne sont jamais stockées."""
    fautifs = []
    for chemin in fichiers("models.py") + fichiers("models/*.py"):
        texte = chemin.read_text(encoding="utf-8")
        for i, ligne in enumerate(texte.splitlines(), 1):
            for nom in ATTRIBUTS_DERIVES:
                if re.match(r"\s*%s\s*=\s*models\." % nom, ligne):
                    fautifs.append("%s ligne %d : %s" % (chemin.relative_to(RACINE), i, nom))
    assert not fautifs, "Attribut dérivé stocké en base :\n" + "\n".join(fautifs)


def test_aucune_note_en_flottant():
    """Une moyenne en flottant peut donner 11,999999 : la mention change."""
    fautifs = []
    for chemin in fichiers("models.py") + fichiers("models/*.py"):
        texte = chemin.read_text(encoding="utf-8")
        for i, ligne in enumerate(texte.splitlines(), 1):
            if "FloatField" in ligne:
                fautifs.append("%s ligne %d" % (chemin.relative_to(RACINE), i))
    assert not fautifs, "FloatField employé — utiliser DecimalField :\n" + "\n".join(fautifs)


def test_ordre_des_dependances_entre_applications():
    """P1 → P2 → P3/P4 → P5 → P6. Aucune dépendance inverse."""
    fautifs = []
    for chemin in fichiers("*.py"):
        app = application_de(chemin.relative_to(SRC))
        if app is None:
            continue
        autorisees = DEPENDANCES_AUTORISEES[app] | {app}
        texte = chemin.read_text(encoding="utf-8")
        for noeud in ast.walk(ast.parse(texte)):
            module = getattr(noeud, "module", None)
            if isinstance(noeud, ast.ImportFrom) and module:
                for autre in APPLICATIONS:
                    if module.split(".")[0] == autre and autre not in autorisees:
                        fautifs.append("%s ligne %d : %s importe %s"
                                       % (chemin.relative_to(RACINE), noeud.lineno, app, autre))
    assert not fautifs, "Dépendance inverse entre applications :\n" + "\n".join(fautifs)
