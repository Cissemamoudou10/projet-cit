"""US-REF-03 + US-REF-04 — Composer le référentiel d'une formation,
CU-P2-04, CU-P2-05. Le modèle et ses contraintes, en base, en contournant
l'ORM — le déroulement et les écrans sont dans test_referentiel_ecran.py.
"""

import pytest
from django.db import IntegrityError, transaction

from noyau.exceptions import ErreurValidation
from referentiel.models import CategorieLieu, ElementReferentiel, Formation, TypeLieuPartage
from referentiel.services.referentiel import ServiceReferentiel
from referentiel.tests.conftest import donnees_element_referentiel as _donnees


def test_une_matiere_rattachee_deux_fois_a_la_meme_formation_est_refusee_en_base(
    formation, matiere
):
    ElementReferentiel.objects.create(formation=formation, matiere=matiere, **_donnees())

    with pytest.raises(IntegrityError), transaction.atomic():
        ElementReferentiel.objects.create(formation=formation, matiere=matiere, **_donnees())


def test_la_meme_matiere_dans_deux_formations_avec_volumes_differents_est_acceptee(
    db, matiere, type_officiers
):
    autre_formation = Formation.objects.create(
        intitule="Formation continue",
        specialite="Transmissions",
        duree_semaines=4,
        type_formation=type_officiers,
    )
    formation_un = Formation.objects.create(
        intitule="Formation initiale",
        specialite="Transmissions",
        duree_semaines=10,
        type_formation=type_officiers,
    )
    ElementReferentiel.objects.create(
        formation=formation_un, matiere=matiere, **_donnees(volume_horaire_prescrit=40)
    )

    ElementReferentiel.objects.create(
        formation=autre_formation, matiere=matiere, **_donnees(volume_horaire_prescrit=12)
    )  # ne lève pas


@pytest.mark.parametrize("volume", [0, -5])
def test_volume_nul_ou_negatif_est_refuse_en_base(formation, matiere, volume):
    with pytest.raises(IntegrityError), transaction.atomic():
        ElementReferentiel.objects.create(
            formation=formation, matiere=matiere, **_donnees(volume_horaire_prescrit=volume)
        )


def test_categorie_lieu_partage_sans_type_est_refusee_en_base(formation, matiere):
    with pytest.raises(IntegrityError), transaction.atomic():
        ElementReferentiel.objects.create(
            formation=formation,
            matiere=matiere,
            **_donnees(categorie_lieu=CategorieLieu.LIEU_PARTAGE, type_lieu_partage=None),
        )


def test_categorie_aucun_lieu_avec_un_type_renseigne_est_refusee_en_base(formation, matiere):
    with pytest.raises(IntegrityError), transaction.atomic():
        ElementReferentiel.objects.create(
            formation=formation,
            matiere=matiere,
            **_donnees(
                categorie_lieu=CategorieLieu.AUCUN_LIEU,
                type_lieu_partage=TypeLieuPartage.AMPHITHEATRE,
            ),
        )


def test_categorie_lieu_partage_avec_type_chaine_vide_n_est_pas_arretee_par_la_contrainte(
    formation, matiere
):
    """Preuve du trou que le service doit combler : une chaîne vide n'est
    pas `NULL`, la contrainte de cohérence ne l'intercepte donc pas — c'est
    pour ça que `ServiceReferentiel._donnees_coherentes` normalise `''` en
    `None` avant toute écriture, plutôt que de compter sur la seule base.
    """
    ElementReferentiel.objects.create(
        formation=formation,
        matiere=matiere,
        **_donnees(categorie_lieu=CategorieLieu.LIEU_PARTAGE, type_lieu_partage=""),
    )  # ne lève pas — la base seule ne suffit pas


def test_rattacher_lieu_partage_avec_type_chaine_vide_est_refuse_par_le_service(
    redacteur, formation, matiere
):
    with pytest.raises(ErreurValidation) as info:
        ServiceReferentiel.rattacher(
            redacteur,
            formation,
            matiere,
            _donnees(categorie_lieu=CategorieLieu.LIEU_PARTAGE, type_lieu_partage=""),
        )

    assert "obligatoire" in str(info.value).lower()
    assert not ElementReferentiel.objects.filter(formation=formation, matiere=matiere).exists()


def test_rattacher_lieu_partage_sans_type_est_refuse_par_le_service(redacteur, formation, matiere):
    with pytest.raises(ErreurValidation):
        ServiceReferentiel.rattacher(
            redacteur,
            formation,
            matiere,
            _donnees(categorie_lieu=CategorieLieu.LIEU_PARTAGE, type_lieu_partage=None),
        )


def test_modifier_vers_lieu_partage_sans_type_est_refuse_par_le_service(
    redacteur, formation, matiere
):
    element = ServiceReferentiel.rattacher(redacteur, formation, matiere, _donnees())

    with pytest.raises(ErreurValidation):
        ServiceReferentiel.modifier_volume(
            redacteur,
            element,
            _donnees(categorie_lieu=CategorieLieu.LIEU_PARTAGE, type_lieu_partage=""),
        )


def test_suppression_d_une_matiere_rattachee_est_refusee(formation, matiere):
    ElementReferentiel.objects.create(formation=formation, matiere=matiere, **_donnees())

    with pytest.raises(IntegrityError), transaction.atomic():
        matiere.delete()


def test_suppression_d_une_formation_efface_son_referentiel(formation, matiere):
    element = ElementReferentiel.objects.create(formation=formation, matiere=matiere, **_donnees())

    formation.delete()

    assert not ElementReferentiel.objects.filter(pk=element.pk).exists()


def test_element_referentiel_ne_duplique_aucun_attribut_de_matiere():
    """Test de non-présence, § 3.2 : le référentiel référence la matière, il
    ne la recopie jamais — dont dépend le critère 6 d'US-REF-02.
    """
    noms_champs_matiere = {"intitule", "code"}
    noms_champs_element = {champ.name for champ in ElementReferentiel._meta.get_fields()}
    assert not (noms_champs_matiere & noms_champs_element)


def test_element_referentiel_ne_porte_pas_de_cle_composite():
    """Note d'implémentation § 4.1 : identifiant technique, pas composite."""
    champ_id = ElementReferentiel._meta.get_field("id")
    assert champ_id.primary_key is True
