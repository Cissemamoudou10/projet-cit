"""Onglets de la rubrique « Référentiel » — voir docs/suivi/DECISIONS.md,
D-58. Les trois catalogues partagent la même permission de lecture, aucun
cas d'accès partiel à tester ici (contrairement à `ressources`).
"""

from django.urls import reverse


def test_les_trois_onglets_apparaissent_sur_chaque_ecran(client, redacteur):
    client.force_login(redacteur)

    for nom_url in ("liste_types_formation", "liste_formations", "liste_matieres"):
        reponse = client.get(reverse(f"referentiel:{nom_url}")).content.decode()
        assert "Types de formation" in reponse
        assert "Formations" in reponse
        assert "Matières" in reponse


def test_l_onglet_actif_correspond_a_l_ecran_courant(client, redacteur):
    client.force_login(redacteur)

    correspondance = {
        "liste_types_formation": "types_formation",
        "liste_formations": "formations",
        "liste_matieres": "matieres",
    }
    for nom_url, slug_attendu in correspondance.items():
        reponse = client.get(reverse(f"referentiel:{nom_url}"))
        assert reponse.context["onglet_actif"] == slug_attendu
