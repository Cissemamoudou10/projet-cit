# -*- coding: utf-8 -*-
"""Contrôle des dépendances.

Le poste de déploiement est un réseau isolé : chaque paquet doit être téléchargé
et validé avant la coupure. Une dépendance ajoutée sans arbitrage rend
l'installation impossible sur place.

Pour ajouter un paquet : le proposer, obtenir l'accord, l'inscrire ici ET dans
requirements.txt, dans le même commit.
"""

import pathlib
import re

RACINE = pathlib.Path(__file__).resolve().parents[2]

DEPENDANCES_VALIDEES = {
    "django",
    "djangorestframework",
    "psycopg",
    "psycopg2-binary",
    "ortools",
    "weasyprint",
    "openpyxl",
    "pytest",
    "pytest-django",
    "ruff",
    "python-dateutil",
    "gunicorn",
    "whitenoise",
}


def test_requirements_ne_contient_que_des_paquets_valides():
    fichier = RACINE / "requirements.txt"
    if not fichier.exists():
        return
    inconnus = []
    for ligne in fichier.read_text(encoding="utf-8").splitlines():
        ligne = ligne.strip()
        if not ligne or ligne.startswith("#") or ligne.startswith("-"):
            continue
        nom = re.split(r"[=<>!~\[]", ligne)[0].strip().lower()
        if nom and nom not in DEPENDANCES_VALIDEES:
            inconnus.append(nom)
    assert not inconnus, (
        "Dépendance non validée : %s.\n"
        "Le poste cible est isolé (BNF-06). Faire valider le paquet, puis "
        "l'inscrire dans DEPENDANCES_VALIDEES et dans requirements.txt." % ", ".join(inconnus)
    )


def test_aucun_cdn_dans_les_gabarits():
    """Aucune ressource en ligne à l'exécution : ni CSS, ni police, ni script."""
    src = RACINE / "app"
    if not src.exists():
        return
    fautifs = []
    for chemin in src.rglob("*.html"):
        texte = chemin.read_text(encoding="utf-8")
        for i, ligne in enumerate(texte.splitlines(), 1):
            if re.search(r'(src|href)\s*=\s*["\']https?://', ligne):
                fautifs.append("%s ligne %d" % (chemin.relative_to(RACINE), i))
    assert not fautifs, "Ressource externe dans un gabarit :\n" + "\n".join(fautifs)


def test_aucune_mise_en_cache_dans_le_referentiel():
    """US-REF-07, § 2.2 : la consultation lit la base à chaque fois. Un cache,
    une vue matérialisée ou un instantané romprait la fraîcheur du critère 4
    sans qu'aucun test fonctionnel ne le détecte forcément à coup sûr."""
    src = RACINE / "app" / "referentiel"
    if not src.exists():
        return
    motif = re.compile(r"django\.core\.cache|cache_page|cache_control|\bcache\.(get|set)\(")
    fautifs = []
    for chemin in list(src.rglob("*.py")) + list(src.rglob("*.html")):
        for i, ligne in enumerate(chemin.read_text(encoding="utf-8").splitlines(), 1):
            if motif.search(ligne):
                fautifs.append("%s ligne %d" % (chemin.relative_to(RACINE), i))
    assert not fautifs, "Mise en cache interdite dans le référentiel :\n" + "\n".join(fautifs)
