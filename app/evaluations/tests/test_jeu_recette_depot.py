"""Garde : la suite de jeu_recette ne réécrit jamais docs/recette/fichiers-import/
(fichiers suivis, recette figée — P-40). Module sans `django_db` : la suite
lancée en sous-processus ne partage aucune connexion avec ce test.
"""

import hashlib
import subprocess
import sys

from django.conf import settings

from evaluations.jeu_recette.fichiers_import.constructeur import DOSSIER


def _empreintes():
    return {
        fichier.name: (
            hashlib.sha256(fichier.read_bytes()).hexdigest(),
            fichier.stat().st_mtime_ns,
        )
        for fichier in sorted(DOSSIER.iterdir())
    }


def test_suite_jeu_recette_ne_modifie_pas_le_depot():
    avant = _empreintes()

    subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "app/evaluations/tests/test_jeu_recette.py",
            "-q",
            "-p",
            "no:cacheprovider",
        ],
        cwd=settings.BASE_DIR.parent,
        check=True,
    )

    assert _empreintes() == avant
