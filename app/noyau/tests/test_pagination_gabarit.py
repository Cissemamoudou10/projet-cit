"""Fenêtre de pagination — Prompt 17, § 1. `Paginator` sur une liste Python
pure : aucune base nécessaire pour vérifier l'arithmétique de la fenêtre.

Le test qui compare le balisage entre le journal, les comptes et une liste
du référentiel vit dans `referentiel/tests/` : `noyau` ne peut dépendre
d'aucune application (test d'architecture), donc pas d'un test qui importe
`administration.models` ici.
"""

from django.core.paginator import Paginator

from noyau.templatetags.pagination import pagination

TAILLE_PAGE = 20


def _page(numero, total_elements):
    return Paginator(range(total_elements), TAILLE_PAGE).get_page(numero)


def test_23_pages_page_1_fenetre_de_cinq_puis_omission_puis_derniere():
    contexte = pagination(_page(1, 23 * TAILLE_PAGE))

    assert list(contexte["fenetre"]) == [1, 2, 3, 4, 5]
    assert contexte["montrer_premiere"] is False
    assert contexte["omission_avant"] is False
    assert contexte["montrer_derniere"] is True
    assert contexte["omission_apres"] is True


def test_23_pages_page_12_fenetre_centree_premiere_et_derniere_atteignables():
    contexte = pagination(_page(12, 23 * TAILLE_PAGE))

    assert list(contexte["fenetre"]) == [10, 11, 12, 13, 14]
    assert contexte["montrer_premiere"] is True
    assert contexte["omission_avant"] is True
    assert contexte["montrer_derniere"] is True
    assert contexte["omission_apres"] is True


def test_23_pages_page_23_fenetre_de_cinq_en_fin_de_liste():
    contexte = pagination(_page(23, 23 * TAILLE_PAGE))

    assert list(contexte["fenetre"]) == [19, 20, 21, 22, 23]
    assert contexte["montrer_premiere"] is True
    assert contexte["omission_avant"] is True
    assert contexte["montrer_derniere"] is False
    assert contexte["omission_apres"] is False


def test_3_pages_tous_les_numeros_aucune_omission():
    contexte = pagination(_page(2, 3 * TAILLE_PAGE))

    assert list(contexte["fenetre"]) == [1, 2, 3]
    assert contexte["montrer_premiere"] is False
    assert contexte["omission_avant"] is False
    assert contexte["montrer_derniere"] is False
    assert contexte["omission_apres"] is False


def test_1_page_precedent_et_suivant_desactives():
    page = _page(1, 5)

    contexte = pagination(page)

    assert list(contexte["fenetre"]) == [1]
    assert not page.has_previous()
    assert not page.has_next()
