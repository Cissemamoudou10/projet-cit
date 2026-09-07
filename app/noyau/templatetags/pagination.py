"""Fenêtre de pagination bornée à cinq numéros — Prompt 17, § 1.

Le calcul du décalage aux extrémités n'a pas sa place dans un gabarit
(`.claude/rules/gabarits.md` : aucune logique, pas même arithmétique) — d'où
cette balise d'inclusion, seul point du système qui calcule `fenetre`.
`{% pagination page %}` remplace l'ancien `{% include "noyau/gestion/
_pagination.html" %}` partout, y compris sur les écrans d'administration
antérieurs au patron `ServiceGestion` (comptes, journal).
"""

from django import template

register = template.Library()

TAILLE_FENETRE = 5
DECALAGE = TAILLE_FENETRE // 2


@register.inclusion_tag("noyau/gestion/_pagination.html")
def pagination(page):
    """`page` : un objet `django.core.paginator.Page`, déjà construit par
    `noyau.pagination.paginer`. Renvoie la fenêtre centrée sur la page
    courante, décalée aux extrémités pour toujours en montrer cinq — sauf
    quand le total de pages est inférieur, auquel cas la fenêtre couvre déjà
    tout l'intervalle.
    """
    total = page.paginator.num_pages
    debut = page.number - DECALAGE
    fin = page.number + DECALAGE
    if debut < 1:
        fin += 1 - debut
        debut = 1
    if fin > total:
        debut -= fin - total
        fin = total
    debut = max(debut, 1)
    return {
        "page": page,
        "fenetre": range(debut, fin + 1),
        "montrer_premiere": debut > 1,
        "omission_avant": debut > 2,
        "montrer_derniere": fin < total,
        "omission_apres": fin < total - 1,
    }
