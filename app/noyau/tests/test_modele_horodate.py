"""`ModeleHorodate` — BNF-14.

Aucun modèle métier concret n'hérite encore de `ModeleHorodate` au socle :
les quatre champs sont vérifiés directement sur la classe abstraite plutôt
que sur un modèle jetable, qui aurait exigé une table hors périmètre.
"""

import pytest
from django.db import connection, models

from noyau.models import ModeleHorodate


def test_modele_horodate_est_abstraite():
    assert ModeleHorodate._meta.abstract is True


@pytest.mark.django_db
def test_modele_horodate_ne_produit_aucune_table():
    tables = connection.introspection.table_names()
    assert not [table for table in tables if table.startswith("noyau_")]


def test_modele_horodate_porte_les_quatre_champs():
    noms = {champ.name for champ in ModeleHorodate._meta.get_fields()}
    assert {"cree_le", "modifie_le", "cree_par", "modifie_par"} <= noms

    cree_le = ModeleHorodate._meta.get_field("cree_le")
    assert cree_le.auto_now_add is True

    modifie_le = ModeleHorodate._meta.get_field("modifie_le")
    assert modifie_le.auto_now is True

    for nom_champ in ("cree_par", "modifie_par"):
        champ = ModeleHorodate._meta.get_field(nom_champ)
        assert champ.null is True
        assert champ.remote_field.on_delete is models.PROTECT


def test_cree_le_est_conscient_du_fuseau(settings):
    """USE_TZ=True fait que `DateTimeField(auto_now_add=True)` horodate avec
    `timezone.now()`, toujours conscient du fuseau — note d'implémentation
    § 2.2. Aucun modèle concret n'existe encore pour observer une valeur
    réelle ; ce test vérifie le mécanisme dont `cree_le` dépend.
    """
    from django.utils import timezone

    assert settings.USE_TZ is True
    assert timezone.is_aware(timezone.now())
