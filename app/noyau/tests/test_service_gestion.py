"""Patron `ServiceGestion` — Prompt 05, § 7, table « Le patron ». Testé sur
un modèle dédié (`essai_patron_gestion`), pas sur `TypeFormation` : « un
patron testé à travers un seul usage n'est pas un patron ».
"""

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.core.management import call_command
from django.db.models import Count
from essai_patron_gestion.models import DependantGestionTest, ElementGestionTest
from essai_patron_gestion.services import ServiceElementGestionTest

from noyau.exceptions import ErreurHabilitation, ErreurModificationConcurrente, ErreurValidation


@pytest.fixture
def redacteur(db):
    call_command("initialiser_habilitations")
    modele = get_user_model()
    utilisateur = modele.objects.create_user(
        username="redacteur", password="x", grade="Lt", profil=modele.Profil.CELLULE_PEDAGOGIQUE
    )
    utilisateur.groups.add(Group.objects.get(name="Cellule pédagogique"))
    return utilisateur


@pytest.fixture
def sans_habilitation(db):
    modele = get_user_model()
    return modele.objects.create_user(
        username="personne", password="x", grade="Lt", profil=modele.Profil.CELLULE_EXAMENS
    )


def test_liste_paginee_au_dela_de_vingt_elements(redacteur):
    for i in range(25):
        ServiceElementGestionTest.creer(redacteur, {"intitule": f"Élément {i:02d}"})

    page = ServiceElementGestionTest.lister(redacteur, {}, None)

    assert page.has_next()
    assert page.paginator.count == 25


def test_recherche_restreint_le_resultat(redacteur):
    ServiceElementGestionTest.creer(redacteur, {"intitule": "Officiers"})
    ServiceElementGestionTest.creer(redacteur, {"intitule": "Sous-officiers"})

    page = ServiceElementGestionTest.lister(redacteur, {"recherche": "Sous"}, None)

    assert [element.intitule for element in page] == ["Sous-officiers"]


def test_les_archives_sont_masques_de_la_selection_visibles_en_consultation(redacteur):
    element = ServiceElementGestionTest.creer(redacteur, {"intitule": "Archivable"})
    ServiceElementGestionTest.archiver(redacteur, element.pk)

    disponibles = ServiceElementGestionTest.disponibles_pour_selection()
    page_consultation = ServiceElementGestionTest.lister(redacteur, {}, None)

    assert element.pk not in disponibles.values_list("pk", flat=True)
    assert element.pk in [ligne.pk for ligne in page_consultation]


def test_champ_obligatoire_manquant_refuse_avec_cause(redacteur):
    with pytest.raises(ErreurValidation) as info:
        ServiceElementGestionTest.creer(redacteur, {"intitule": ""})

    assert "vide" in str(info.value)


def test_violation_unicite_designe_l_element_existant(redacteur):
    ServiceElementGestionTest.creer(redacteur, {"intitule": "Doublon"})

    with pytest.raises(ErreurValidation) as info:
        ServiceElementGestionTest.creer(redacteur, {"intitule": "doublon"})

    assert "Doublon" in str(info.value)


def test_element_reference_empeche_la_suppression_avec_enumeration(redacteur):
    """§ 2.3 : l'archivage reste toujours possible ; seule la suppression
    est conditionnelle — voir docs/suivi/DECISIONS.md pour l'écart avec le
    libellé de cette ligne dans le Prompt 05, § 7.
    """
    element = ServiceElementGestionTest.creer(redacteur, {"intitule": "Référencé"})
    DependantGestionTest.objects.create(element=element)

    with pytest.raises(ErreurValidation) as info:
        ServiceElementGestionTest.supprimer(redacteur, element.pk)

    assert "Référencé" in str(info.value)
    assert ElementGestionTest.objects.filter(pk=element.pk).exists()


def test_habilitation_insuffisante_refuse(sans_habilitation):
    with pytest.raises(ErreurHabilitation):
        ServiceElementGestionTest.lister(sans_habilitation, {}, None)


def test_modifie_le_obsolete_leve_erreur_avec_auteur_nomme(redacteur):
    element = ServiceElementGestionTest.creer(redacteur, {"intitule": "Original"})
    ServiceElementGestionTest.modifier(
        redacteur, element.pk, {"intitule": "Modifié"}, element.modifie_le
    )

    with pytest.raises(ErreurModificationConcurrente) as info:
        ServiceElementGestionTest.modifier(
            redacteur, element.pk, {"intitule": "Rejeu"}, element.modifie_le
        )

    assert redacteur.username in str(info.value)


def test_lister_filtre_sur_un_champ_declare_dans_champs_filtrables(redacteur):
    """Prompt 06, § remontées au patron : un filtre d'égalité générique, en
    plus de `etat` et de la recherche libre — sert le filtre par type de
    formation d'US-REF-01, sans y être propre.
    """
    ServiceElementGestionTest.creer(redacteur, {"intitule": "Alpha"})
    ServiceElementGestionTest.creer(redacteur, {"intitule": "Beta"})

    page = ServiceElementGestionTest.lister(redacteur, {"intitule": "Alpha"}, None)

    assert [element.intitule for element in page] == ["Alpha"]


def test_lister_ignore_un_filtre_declare_mais_vide(redacteur):
    ServiceElementGestionTest.creer(redacteur, {"intitule": "Alpha"})
    ServiceElementGestionTest.creer(redacteur, {"intitule": "Beta"})

    page = ServiceElementGestionTest.lister(redacteur, {"intitule": ""}, None)

    assert page.paginator.count == 2


class _ServiceElementGestionTestAnnote(ServiceElementGestionTest):
    """Local au test : prouve que `_queryset()` est le point d'extension
    attendu pour une annotation, sans modifier le service partagé.
    """

    @classmethod
    def _queryset(cls):
        return super()._queryset().annotate(nombre_dependants=Count("dependants"))


def test_queryset_surchargee_permet_d_annoter_sans_requete_en_boucle(redacteur):
    element = ServiceElementGestionTest.creer(redacteur, {"intitule": "Annoté"})
    DependantGestionTest.objects.create(element=element)

    page = _ServiceElementGestionTestAnnote.lister(redacteur, {}, None)

    assert page[0].nombre_dependants == 1


def test_deux_ecritures_concurrentes_la_seconde_echoue(redacteur):
    element = ServiceElementGestionTest.creer(redacteur, {"intitule": "Concurrence"})
    modifie_le_initial = element.modifie_le

    ServiceElementGestionTest.modifier(
        redacteur, element.pk, {"intitule": "Première"}, modifie_le_initial
    )

    with pytest.raises(ErreurModificationConcurrente):
        ServiceElementGestionTest.modifier(
            redacteur, element.pk, {"intitule": "Seconde"}, modifie_le_initial
        )

    element.refresh_from_db()
    assert element.intitule == "Première"
