"""Pagination — BNF-15.

Taille de page paramétrable (BNF-13), jamais en dur : voir
`settings.TAILLE_PAGE_DEFAUT`.
"""

from django.conf import settings
from django.core.paginator import Paginator


def paginer(queryset, numero_page, taille_page=None):
    """Pagine `queryset`. `taille_page` retombe sur `settings.TAILLE_PAGE_DEFAUT`
    si absent.
    """
    paginateur = Paginator(queryset, taille_page or settings.TAILLE_PAGE_DEFAUT)
    return paginateur.get_page(numero_page)
