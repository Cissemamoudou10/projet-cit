"""Onglets de la rubrique « Référentiel » — les trois catalogues (types de
formation, formations, matières) partagent la même permission de lecture
(`referentiel_lecture`) : contrairement à `ressources.navigation`, aucun
filtrage par onglet n'est nécessaire, tous apparaissent ensemble. Remplace
les liens croisés (`liens_associes`) posés au fil des stories US-REF-00/01/02,
unifiés ici pour ne pas dupliquer le même besoin de deux façons différentes.
Voir docs/suivi/DECISIONS.md, D-58.
"""

from django.urls import reverse


def onglets_referentiel(actif):
    onglets = [
        {
            "slug": "types_formation",
            "libelle": "Types de formation",
            "url": reverse("referentiel:liste_types_formation"),
        },
        {
            "slug": "formations",
            "libelle": "Formations",
            "url": reverse("referentiel:liste_formations"),
        },
        {
            "slug": "matieres",
            "libelle": "Matières",
            "url": reverse("referentiel:liste_matieres"),
        },
    ]
    return onglets, actif
