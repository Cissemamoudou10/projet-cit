"""Immuabilité du journal — RG-27, Prompt 04 § 2.1, § 2.2.

Ces tests ouvrent une connexion PostgreSQL distincte, sous le rôle
applicatif `pfe_cit_app` — pas sous `pfe_cit_migration`, celui de la suite
de tests, qui a le droit de modifier la table et prouverait donc le
contraire de ce qu'on cherche à démontrer. Sans le correctif du
`conftest.py` racine (privilèges regreffés sur `test_pfe_cit`, voir
docs/suivi/DECISIONS.md, D-13), `pfe_cit_app` n'aurait aucun privilège du
tout ici — INSERT et SELECT compris — et un test d'UPDATE refusé passerait
en prouvant l'absence totale de droits, pas la révocation ciblée.
"""

import importlib
import inspect
import os

import psycopg
import pytest
from django.db import connection


def _connexion_app():
    parametres = connection.settings_dict
    return psycopg.connect(
        host=parametres["HOST"] or "localhost",
        port=parametres["PORT"] or "5432",
        dbname=parametres["NAME"],
        user=os.environ.get("BASE_UTILISATEUR", "pfe_cit_app"),
        password=os.environ.get("BASE_MOT_DE_PASSE", "developpement_local_app"),
    )


def test_update_refuse_sous_pfe_cit_app(db):
    """Le refus de PostgreSQL porte sur le privilège de la table, avant
    même d'évaluer la clause WHERE — inutile qu'une ligne existe réellement.
    """
    connexion_app = _connexion_app()
    try:
        with pytest.raises(psycopg.errors.InsufficientPrivilege), connexion_app.cursor() as curseur:
            curseur.execute(
                "UPDATE administration_entree_journal SET detail = %s WHERE id = %s",
                ["modifie", 1],
            )
    finally:
        connexion_app.close()


def test_delete_refuse_sous_pfe_cit_app(db):
    connexion_app = _connexion_app()
    try:
        with pytest.raises(psycopg.errors.InsufficientPrivilege), connexion_app.cursor() as curseur:
            curseur.execute("DELETE FROM administration_entree_journal WHERE id = %s", [1])
    finally:
        connexion_app.close()


def test_insert_et_select_restent_possibles_sous_pfe_cit_app(db):
    """Jamais de commit : rien de ce test ne doit persister dans
    `test_pfe_cit` au-delà de son exécution.
    """
    connexion_app = _connexion_app()
    try:
        with connexion_app.cursor() as curseur:
            curseur.execute(
                "INSERT INTO administration_entree_journal "
                "(type_action, cible, identifiant_saisi, detail, objet_type, "
                "objet_identifiant, cree_le, modifie_le) "
                "VALUES ('echec_authentification', '', %s, '', '', '', now(), now())",
                ["essai-immuabilite"],
            )
            curseur.execute(
                "SELECT identifiant_saisi FROM administration_entree_journal "
                "WHERE identifiant_saisi = %s",
                ["essai-immuabilite"],
            )
            assert curseur.fetchone()[0] == "essai-immuabilite"
    finally:
        connexion_app.rollback()
        connexion_app.close()


def test_migration_de_revocation_est_reversible():
    """Assertion statique, sans toucher la base : `reverse_sql` porte bien
    le GRANT symétrique, pas un no-op.
    """
    module = importlib.import_module("administration.migrations.0007_revoquer_ecriture_journal")
    operation = module.Migration.operations[0]
    assert operation.reverse_sql == module.RETABLIR
    assert "GRANT" in operation.reverse_sql
    assert "UPDATE" in operation.reverse_sql
    assert "DELETE" in operation.reverse_sql


def test_service_journal_n_expose_aucune_ecriture_hors_insertion():
    from administration.services.journal import ServiceJournal

    methodes_ecriture = {"enregistrer", "enregistrer_detaillee"}
    for nom, membre in inspect.getmembers(ServiceJournal):
        if nom.startswith("_") or not inspect.isfunction(membre):
            continue
        if nom in methodes_ecriture or nom in (
            "consulter",
            "natures_disponibles",
            "objet_types_disponibles",
        ):
            continue
        pytest.fail(f"Méthode inattendue sur ServiceJournal : {nom}")


def test_aucune_vue_de_modification_ou_suppression_du_journal():
    from administration.views import journal as module_vue

    fonctions_publiques = [
        nom
        for nom, membre in inspect.getmembers(module_vue, inspect.isfunction)
        if membre.__module__ == module_vue.__name__ and not nom.startswith("_")
    ]
    assert fonctions_publiques == ["vue_journal"]
