"""US-PLAN-02 — Gérer les lieux d'enseignement, CU-P4-06. Le modèle, ses
contraintes en base et le service — les écrans sont dans test_lieu_ecran.py,
les indisponibilités dans test_indisponibilite_lieu.py.
"""

import datetime

import pytest
from django.db import IntegrityError, transaction
from django.utils import timezone

from administration.models import EntreeJournal, TypeAction
from noyau.exceptions import ErreurHabilitation, ErreurValidation
from referentiel.models import CategorieLieu as CategorieLieuReferentiel
from ressources.models import CategorieLieu, Lieu, TypeLieuPartage
from ressources.services.indisponibilite_lieu import ServiceIndisponibiliteLieu
from ressources.services.lieu import ServiceLieu


def _donnees(**supplement):
    donnees = {
        "intitule": "Salle 101",
        "capacite": 30,
        "categorie": CategorieLieu.SALLE_ATTITREE,
    }
    donnees.update(supplement)
    return donnees


def test_creation_avec_intitule_capacite_et_categorie(planificateur):
    """Critère 1."""
    lieu = ServiceLieu.creer(planificateur, _donnees())

    assert lieu.pk is not None
    assert lieu.intitule == "Salle 101"
    assert lieu.capacite == 30
    assert lieu.categorie == CategorieLieu.SALLE_ATTITREE


def test_lieu_partage_precise_son_type(planificateur):
    """Critère 2."""
    lieu = ServiceLieu.creer(
        planificateur,
        _donnees(categorie=CategorieLieu.LIEU_PARTAGE, type_partage=TypeLieuPartage.AMPHITHEATRE),
    )

    assert lieu.type_partage == TypeLieuPartage.AMPHITHEATRE


def test_intitule_duplique_est_refuse_en_base(db):
    Lieu.objects.create(**_donnees())

    with pytest.raises(IntegrityError), transaction.atomic():
        Lieu.objects.create(**_donnees())


def test_capacite_nulle_est_refusee_en_base(db):
    with pytest.raises(IntegrityError), transaction.atomic():
        Lieu.objects.create(**_donnees(capacite=0))


def test_capacite_negative_est_refusee_en_base(db):
    with pytest.raises(IntegrityError), transaction.atomic():
        Lieu.objects.create(**_donnees(capacite=-5))


def test_capacite_nulle_est_refusee_par_le_service(planificateur):
    with pytest.raises(ErreurValidation) as info:
        ServiceLieu.creer(planificateur, _donnees(capacite=0))

    assert "None" not in str(info.value)


def test_capacite_negative_est_refusee_par_le_service(planificateur):
    with pytest.raises(ErreurValidation) as info:
        ServiceLieu.creer(planificateur, _donnees(capacite=-5))

    assert "None" not in str(info.value)


def test_lieu_partage_sans_type_est_refuse_en_base(db):
    with pytest.raises(IntegrityError), transaction.atomic():
        Lieu.objects.create(**_donnees(categorie=CategorieLieu.LIEU_PARTAGE))


def test_salle_attitrable_avec_un_type_est_refusee_en_base(db):
    with pytest.raises(IntegrityError), transaction.atomic():
        Lieu.objects.create(
            **_donnees(
                categorie=CategorieLieu.SALLE_ATTITREE, type_partage=TypeLieuPartage.LABORATOIRE
            )
        )


def test_lieu_partage_sans_type_est_refuse_par_le_service(planificateur):
    """Relecture de conception : le message générique du patron chercherait
    un doublon d'intitulé inexistant et produirait « ... attribué à None. »
    (même défaut que US-REF-05, voir test_objectif_pedagogique_ordre.py)."""
    with pytest.raises(ErreurValidation) as info:
        ServiceLieu.creer(planificateur, _donnees(categorie=CategorieLieu.LIEU_PARTAGE))

    assert "None" not in str(info.value)


def test_salle_attitrable_avec_un_type_est_refusee_par_le_service(planificateur):
    with pytest.raises(ErreurValidation) as info:
        ServiceLieu.creer(
            planificateur,
            _donnees(
                categorie=CategorieLieu.SALLE_ATTITREE, type_partage=TypeLieuPartage.LABORATOIRE
            ),
        )

    assert "None" not in str(info.value)


def test_la_categorie_de_lieu_compte_deux_valeurs_pas_trois():
    """§ 2 du Prompt 14 : pas de troisième valeur, contrairement à la
    catégorie de lieu du référentiel."""
    assert len(CategorieLieu.choices) == 2
    assert {valeur for valeur, _ in CategorieLieu.choices} == {"salle_attitree", "lieu_partage"}


def test_la_categorie_de_lieu_n_est_pas_celle_du_referentiel():
    """§ 2 : deux notions distinctes qui se ressemblent — pas la même classe."""
    assert CategorieLieu is not CategorieLieuReferentiel
    assert len(CategorieLieuReferentiel.choices) == 3


def test_ecriture_refusee_a_la_cellule_pedagogique(redacteur):
    """Matrice § 11.2 : inversion des habilitations par rapport aux stories
    précédentes — la cellule pédagogique ne lit ici que."""
    with pytest.raises(ErreurHabilitation):
        ServiceLieu.creer(redacteur, _donnees())


def test_lecture_ouverte_a_la_cellule_pedagogique(redacteur, planificateur):
    ServiceLieu.creer(planificateur, _donnees())

    page = ServiceLieu.lister(redacteur, {}, None)  # ne lève pas

    assert len(page) == 1


def test_lecture_ouverte_a_examens_et_direction(
    planificateur, cellule_examens, direction_formation
):
    ServiceLieu.creer(planificateur, _donnees())

    ServiceLieu.lister(cellule_examens, {}, None)  # ne lève pas
    ServiceLieu.lister(direction_formation, {}, None)  # ne lève pas


def test_intitule_duplique_est_refuse_par_le_service(planificateur):
    ServiceLieu.creer(planificateur, _donnees())

    with pytest.raises(ErreurValidation):
        ServiceLieu.creer(planificateur, _donnees())


def test_colonne_indisponibilites_a_venir_exclut_les_passees(planificateur):
    """Prompt 17, § 2.5 : les indisponibilités passées n'intéressent
    personne à la consultation."""
    lieu = ServiceLieu.creer(planificateur, _donnees())
    maintenant = timezone.now()
    ServiceIndisponibiliteLieu.declarer(
        planificateur,
        lieu,
        maintenant - datetime.timedelta(days=10),
        maintenant - datetime.timedelta(days=9),
        "Passée",
    )
    ServiceIndisponibiliteLieu.declarer(
        planificateur,
        lieu,
        maintenant + datetime.timedelta(days=5),
        maintenant + datetime.timedelta(days=6),
        "À venir",
    )

    page = ServiceLieu.lister(planificateur, {}, None)
    ligne = next(candidat for candidat in page if candidat.pk == lieu.pk)

    assert ligne.nombre_indisponibilites_a_venir == 1


def test_liste_paginee_au_dela_de_vingt_lieux(planificateur):
    for i in range(21):
        ServiceLieu.creer(planificateur, _donnees(intitule=f"Salle {i:02d}"))

    page = ServiceLieu.lister(planificateur, {}, None)

    assert page.has_next()


def test_filtre_par_categorie(planificateur):
    ServiceLieu.creer(planificateur, _donnees())
    ServiceLieu.creer(
        planificateur,
        _donnees(
            intitule="Amphi A",
            categorie=CategorieLieu.LIEU_PARTAGE,
            type_partage=TypeLieuPartage.AMPHITHEATRE,
        ),
    )

    page = ServiceLieu.lister(planificateur, {"categorie": CategorieLieu.LIEU_PARTAGE}, None)

    assert [lieu.intitule for lieu in page] == ["Amphi A"]


def test_filtre_par_capacite_minimale(planificateur):
    ServiceLieu.creer(planificateur, _donnees(intitule="Petite salle", capacite=10))
    ServiceLieu.creer(planificateur, _donnees(intitule="Grande salle", capacite=80))

    page = ServiceLieu.lister(planificateur, {"capacite_min": "50"}, None)

    assert [lieu.intitule for lieu in page] == ["Grande salle"]


def test_filtre_par_disponibilite(planificateur):
    """Critère 5, arbitrage § 4 du Prompt 14 (D-55) : un lieu sort de la
    liste s'il porte une indisponibilité recouvrant la période interrogée."""
    ServiceLieu.creer(planificateur, _donnees(intitule="Salle libre"))
    occupee = ServiceLieu.creer(planificateur, _donnees(intitule="Salle occupée"))
    ServiceIndisponibiliteLieu.declarer(
        planificateur,
        occupee,
        timezone.make_aware(datetime.datetime(2027, 1, 4, 8, 0)),
        timezone.make_aware(datetime.datetime(2027, 1, 4, 12, 0)),
        "Réfection du sol",
    )

    page = ServiceLieu.lister(
        planificateur,
        {
            "disponible_du": datetime.date(2027, 1, 4),
            "disponible_au": datetime.date(2027, 1, 8),
        },
        None,
    )

    assert [lieu.intitule for lieu in page] == ["Salle libre"]


def test_methode_d_enumeration_des_bloquants_existe_et_ne_trouve_rien(planificateur):
    """Critère 4, § 3.3 du Prompt 14 : le blocage par une brigade attitrée
    (US-SES-02) ou par une séance (US-PLAN-03) n'est pas testable
    aujourd'hui — reports consignés dans docs/suivi/. La suppression ne doit
    rien trouver qui s'y oppose, en attendant.
    """
    lieu = ServiceLieu.creer(planificateur, _donnees())

    ServiceLieu.supprimer(planificateur, lieu.pk)  # ne lève pas

    assert not Lieu.objects.filter(pk=lieu.pk).exists()


def test_lieu_archive_absent_de_la_selection_present_en_consultation(planificateur, redacteur):
    lieu = ServiceLieu.creer(planificateur, _donnees())
    ServiceLieu.archiver(planificateur, lieu.pk)

    disponibles = ServiceLieu.disponibles_pour_selection()
    page_consultation = ServiceLieu.lister(redacteur, {}, None)

    assert lieu.pk not in disponibles.values_list("pk", flat=True)
    assert lieu.pk in [ligne.pk for ligne in page_consultation]


def test_creation_modification_archivage_sont_journalises(planificateur):
    lieu = ServiceLieu.creer(planificateur, _donnees())
    ServiceLieu.modifier(planificateur, lieu.pk, _donnees(capacite=45), lieu.modifie_le)
    ServiceLieu.archiver(planificateur, lieu.pk)

    natures = list(
        EntreeJournal.objects.filter(objet_type="lieu", objet_identifiant="Salle 101")
        .order_by("cree_le")
        .values_list("type_action", flat=True)
    )
    assert TypeAction.CREATION_ELEMENT_GESTION in natures
    assert TypeAction.MODIFICATION_ELEMENT_GESTION in natures
    assert TypeAction.ARCHIVAGE_ELEMENT_GESTION in natures


def test_suppression_est_journalisee(planificateur):
    """Prompt 16, cause racine n° 3, § 5 — relevé en relecture, voir
    referentiel/tests/test_type_formation.py."""
    lieu = ServiceLieu.creer(planificateur, _donnees())

    ServiceLieu.supprimer(planificateur, lieu.pk)

    assert EntreeJournal.objects.filter(
        objet_type="lieu",
        objet_identifiant="Salle 101",
        type_action=TypeAction.SUPPRESSION_ELEMENT_GESTION,
    ).exists()


def test_l_archivage_ne_supprime_rien(planificateur):
    lieu = ServiceLieu.creer(planificateur, _donnees())

    ServiceLieu.archiver(planificateur, lieu.pk)

    assert Lieu.objects.filter(pk=lieu.pk).exists()
