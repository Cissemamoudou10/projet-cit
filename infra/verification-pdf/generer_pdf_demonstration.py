#!/usr/bin/env python3
"""Vérification hors ligne du rendu PDF — Prompt 18, § 5.

Script autonome, hors périmètre applicatif : ServiceDocument n'existe pas
avant le sprint 4, aucun service ne produit encore de PDF. Appelle
WeasyPrint directement sur gabarit_demonstration.html, qui emploie les
neuf polices (polices.css) et la mise en page paginée réservée à
l'impression (document_pdf.css) — objet unique : prouver qu'un PDF correct
sort du conteneur, hors ligne, polices embarquées et non substituées.

Usage, dans le conteneur applicatif, après collectstatic :
    python infra/verification-pdf/generer_pdf_demonstration.py
"""

import sys
from pathlib import Path

from weasyprint import HTML

ICI = Path(__file__).resolve().parent
RACINE_STATIQUES_DEFAUT = Path("/app/staticfiles")


def generer(racine_statiques: Path, sortie: Path) -> None:
    gabarit = (ICI / "gabarit_demonstration.html").read_text(encoding="utf-8")
    base_url = racine_statiques.as_uri() + "/"
    HTML(string=gabarit, base_url=base_url).write_pdf(str(sortie))


if __name__ == "__main__":
    racine = Path(sys.argv[1]) if len(sys.argv) > 1 else RACINE_STATIQUES_DEFAUT
    sortie = Path(sys.argv[2]) if len(sys.argv) > 2 else ICI / "demonstration.pdf"

    if not racine.exists():
        raise SystemExit(
            f"Racine des statiques introuvable : {racine} — collectstatic a-t-il été exécuté ?"
        )

    generer(racine, sortie)
    print(f"PDF généré : {sortie.resolve()}")
