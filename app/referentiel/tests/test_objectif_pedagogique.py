"""US-REF-05 — Associer des objectifs pédagogiques aux matières, CU-P2-06.
Modèle, contraintes de base et service — le réordonnancement (contrainte
différée) est dans test_objectif_pedagogique_ordre.py, les écrans dans
test_objectif_pedagogique_ecran.py.
"""

import pytest
from django.db import IntegrityError, transaction

from administration.models import EntreeJournal, TypeAction
from noyau.exceptions import ErreurHabilitation
from referentiel.models import ElementReferentiel, Formation, Matiere, ObjectifPedagogique
from referentiel.services.objectif_pedagogique import ServiceObjectifPedagogique


def test_une_matiere_porte_plusieurs_objectifs(redacteur, matiere):
    ServiceObjectifPedagogique.ajouter(redacteur, matiere, "Premier objectif")
    ServiceObjectifPedagogique.ajouter(redacteur, matiere, "Second objectif")

    objectifs = ServiceObjectifPedagogique.lister_pour_matiere(redacteur, matiere)

    assert [o.libelle for o in objectifs] == ["Premier objectif", "Second objectif"]


def test_libelle_vide_est_refuse_en_base(matiere):
    """`ck_objectif_libelle_non_vide` n'est pas différée — vérifiée à
    chaque écriture, contrairement à l'unicité de l'ordre.
    """
    with pytest.raises(IntegrityError), transaction.atomic():
        ObjectifPedagogique.objects.create(matiere=matiere, libelle="", ordre=1)


def test_ajouter_calcule_l_ordre_sans_le_demander(redacteur, matiere):
    premier = ServiceObjectifPedagogique.ajouter(redacteur, matiere, "Premier")
    second = ServiceObjectifPedagogique.ajouter(redacteur, matiere, "Second")

    assert premier.ordre == 1
    assert second.ordre == 2


def test_suppression_d_un_objectif_laisse_la_matiere_et_les_autres_intacts(redacteur, matiere):
    premier = ServiceObjectifPedagogique.ajouter(redacteur, matiere, "Premier")
    second = ServiceObjectifPedagogique.ajouter(redacteur, matiere, "Second")

    ServiceObjectifPedagogique.supprimer(redacteur, premier.pk)

    matiere.refresh_from_db()
    assert Matiere.objects.filter(pk=matiere.pk).exists()
    assert ObjectifPedagogique.objects.filter(pk=second.pk).exists()


def test_suppression_du_numero_deux_sur_cinq_ne_renumerote_rien(redacteur, matiere):
    objectifs = [
        ServiceObjectifPedagogique.ajouter(redacteur, matiere, f"Objectif {i}") for i in range(1, 6)
    ]

    ServiceObjectifPedagogique.supprimer(redacteur, objectifs[1].pk)

    ordres = list(
        ObjectifPedagogique.objects.filter(matiere=matiere)
        .order_by("ordre")
        .values_list("ordre", flat=True)
    )
    assert ordres == [1, 3, 4, 5]


def test_suppression_d_une_matiere_efface_ses_objectifs(redacteur, matiere):
    objectif = ServiceObjectifPedagogique.ajouter(redacteur, matiere, "Premier")

    matiere.delete()

    assert not ObjectifPedagogique.objects.filter(pk=objectif.pk).exists()


def test_ne_porte_aucune_cle_vers_formation_ni_element_referentiel():
    """Test de non-présence, § 2.1 : l'objectif appartient à la matière,
    jamais au référentiel — un objectif rattaché à une formation ou à un
    élément de référentiel violerait « une compétence ne change pas selon
    la formation qui la dispense ».
    """
    cibles = {
        champ.related_model
        for champ in ObjectifPedagogique._meta.get_fields()
        if champ.is_relation and getattr(champ, "many_to_one", False)
    }
    assert Formation not in cibles
    assert ElementReferentiel not in cibles


def test_n_a_pas_de_champ_d_archivage():
    """Test de non-présence, § 2.3 : seule entité du projet à user d'une
    suppression réelle — le mixin d'archivage ne doit jamais y apparaître.
    """
    noms_champs = {champ.name for champ in ObjectifPedagogique._meta.get_fields()}
    assert "archive" not in noms_champs
    assert "archive_le" not in noms_champs


def test_creation_modification_suppression_sont_journalisees(redacteur, matiere):
    objectif = ServiceObjectifPedagogique.ajouter(redacteur, matiere, "Premier objectif")
    ServiceObjectifPedagogique.modifier_libelle(redacteur, objectif, "Objectif modifié")
    ServiceObjectifPedagogique.supprimer(redacteur, objectif.pk)

    natures = list(
        EntreeJournal.objects.filter(
            objet_type="objectif_pedagogique",
            objet_identifiant__icontains="objectif",
        )
        .order_by("cree_le")
        .values_list("type_action", flat=True)
    )
    assert TypeAction.CREATION_ELEMENT_GESTION in natures
    assert TypeAction.MODIFICATION_ELEMENT_GESTION in natures
    assert TypeAction.SUPPRESSION_ELEMENT_GESTION in natures


def test_cellule_pedagogique_ecrit(redacteur, matiere):
    ServiceObjectifPedagogique.ajouter(redacteur, matiere, "Premier objectif")  # ne lève pas


def test_planification_examens_direction_lisent_seulement(lecteur, matiere):
    ServiceObjectifPedagogique.lister_pour_matiere(lecteur, matiere)  # ne lève pas

    with pytest.raises(ErreurHabilitation):
        ServiceObjectifPedagogique.ajouter(lecteur, matiere, "Premier objectif")
