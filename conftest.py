"""Reproduit dans `test_pfe_cit` les privilèges du rôle applicatif de
production — voir Prompt 04, § 2.1 et 2.2.

`ALTER DEFAULT PRIVILEGES` (posé dans `infra/postgres/init/01_roles.sh`) ne
s'applique qu'à la base où il s'exécute (`pfe_cit`) : il ne se propage pas à
`test_pfe_cit`, une base distincte créée après coup par `pfe_cit_migration`.
Sans ce correctif, `pfe_cit_app` n'a strictement aucun privilège sur
`test_pfe_cit` — un test qui prétendrait prouver la révocation RG-27 y
prouverait en réalité l'absence totale de droits, INSERT et SELECT compris.

Regreffe donc les mêmes privilèges qu'en production une fois la base de test
migrée, puis rejoue la révocation ciblée de la migration 0007 — l'état final
de `test_pfe_cit` reproduit exactement celui de `pfe_cit`.

Pose aussi un verrou de fichier (P-51, prompt 49, Temps 2) : deux exécutions
simultanées de la suite sur la même base provoquent un blocage PostgreSQL
(deadlock) lors de la création concurrente des groupes d'habilitation —
refusé au démarrage plutôt que laissé à PostgreSQL.
"""

import os
import pathlib
import tempfile
import time

import pytest
from django.db import connection

# Hérité par tout sous-processus (`subprocess.run` transmet `os.environ` par
# défaut) : `test_jeu_recette_depot.py` relance délibérément pytest en
# sous-processus PENDANT la suite — un enfant légitime du même arbre, pas
# une seconde exécution indépendante. Sans ce repère, le verrou ci-dessous
# le refuserait à tort (observé au prompt 49, Temps 2).
VARIABLE_ENV_VERROU = "PFE_CIT_PYTEST_VERROU_POSE"

REGREFFER_PRIVILEGES = """
    GRANT USAGE ON SCHEMA public TO pfe_cit_app;
    GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO pfe_cit_app;
    GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO pfe_cit_app;
"""
REVOQUER_ECRITURE_JOURNAL = (
    "REVOKE UPDATE, DELETE ON administration_entree_journal FROM pfe_cit_app;"
)

# P-51 (prompt 49, Temps 2) : bien au-delà de la durée observée de la suite
# complète (~12 min) — un verrou plus vieux que ce seuil vient d'une
# exécution interrompue sans nettoyage, pas d'une exécution toujours en
# cours.
SEUIL_VERROU_PERIME_SECONDES = 30 * 60


def _chemin_verrou():
    nom_base = connection.settings_dict["NAME"]
    return pathlib.Path(tempfile.gettempdir()) / f"pfe_cit_pytest_en_cours_{nom_base}.lock"


def _poser_verrou():
    """P-51 : deux exécutions INDÉPENDANTES de la suite lancées en même
    temps sur la même base provoquent un blocage PostgreSQL (deadlock) lors
    de la création concurrente des groupes d'habilitation par les fixtures
    — pas un défaut de code, un défaut de méthode. Refuse de démarrer
    plutôt que de laisser PostgreSQL trancher de façon imprévisible.

    Rend `None` sans rien poser si `VARIABLE_ENV_VERROU` est déjà présente
    dans l'environnement : un sous-processus pytest légitime, enfant d'une
    exécution déjà protégée (`test_jeu_recette_depot.py`), pas une seconde
    exécution indépendante."""
    if os.environ.get(VARIABLE_ENV_VERROU):
        return None
    verrou = _chemin_verrou()
    if verrou.exists():
        age = time.time() - verrou.stat().st_mtime
        if age < SEUIL_VERROU_PERIME_SECONDES:
            pytest.exit(
                f"Une autre exécution de la suite semble déjà en cours sur cette base "
                f"(verrou {verrou} posé il y a {age:.0f} s) — relancez une fois qu'elle "
                "est terminée. Si elle a été interrompue sans nettoyage, supprimez ce fichier.",
                returncode=1,
            )
    verrou.touch()
    os.environ[VARIABLE_ENV_VERROU] = "1"
    return verrou


@pytest.fixture(scope="session")
def django_db_setup(django_db_setup, django_db_blocker):  # noqa: ARG001 — patron pytest-django : surcharge par redéclaration du même nom
    verrou = _poser_verrou()
    with django_db_blocker.unblock(), connection.cursor() as curseur:
        curseur.execute(REGREFFER_PRIVILEGES)
        curseur.execute(REVOQUER_ECRITURE_JOURNAL)
    yield
    if verrou is not None:
        verrou.unlink(missing_ok=True)
