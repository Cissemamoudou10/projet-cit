"""Onglets de la rubrique « Administration » — voir docs/suivi/DECISIONS.md,
D-58. Seul le groupe Administrateur détient les trois permissions aujourd'hui
(§ 11.2), donc aucun profil réel n'exerce l'asymétrie que le filtrage par
permission autorise (contrairement à `ressources`).
"""

from django.urls import reverse


def test_les_trois_onglets_apparaissent_sur_chaque_ecran(client, administrateur):
    client.force_login(administrateur)

    for nom_url in ("liste_comptes", "habilitations", "journal"):
        reponse = client.get(reverse(f"administration:{nom_url}")).content.decode()
        assert "Comptes" in reponse
        assert "Habilitations" in reponse
        assert "Journal" in reponse


def test_l_onglet_actif_correspond_a_l_ecran_courant(client, administrateur):
    client.force_login(administrateur)

    correspondance = {
        "liste_comptes": "comptes",
        "habilitations": "habilitations",
        "journal": "journal",
    }
    for nom_url, slug_attendu in correspondance.items():
        reponse = client.get(reverse(f"administration:{nom_url}"))
        assert reponse.context["onglet_actif"] == slug_attendu
