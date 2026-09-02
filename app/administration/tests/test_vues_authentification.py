"""Vues de connexion et de déconnexion."""

import logging

from django.urls import reverse


def test_connexion_valide_redirige_vers_l_accueil(client, utilisateur, mot_de_passe):
    reponse = client.post(
        reverse("administration:connexion"),
        {"identifiant": utilisateur.username, "mot_de_passe": mot_de_passe},
    )

    assert reponse.status_code == 302
    assert reponse.url == reverse("noyau:accueil")


def test_session_deja_ouverte_redirige_directement(client, utilisateur):
    client.force_login(utilisateur)

    reponse = client.get(reverse("administration:connexion"))

    assert reponse.status_code == 302
    assert reponse.url == reverse("noyau:accueil")


def test_deconnexion_en_post_invalide_la_session(client, utilisateur):
    client.force_login(utilisateur)

    reponse = client.post(reverse("administration:deconnexion"))

    assert reponse.status_code == 302
    assert "_auth_user_id" not in client.session


def test_deconnexion_en_get_est_refusee(client, utilisateur):
    client.force_login(utilisateur)

    reponse = client.get(reverse("administration:deconnexion"))

    assert reponse.status_code == 405


def test_page_protegee_sans_session_conserve_next(client):
    reponse = client.get(reverse("noyau:accueil"))

    assert reponse.status_code == 302
    assert reponse.url.startswith(reverse("administration:connexion"))
    assert "next=" in reponse.url


def test_next_vers_un_domaine_externe_est_ignore(client, utilisateur, mot_de_passe):
    reponse = client.post(
        reverse("administration:connexion"),
        {
            "identifiant": utilisateur.username,
            "mot_de_passe": mot_de_passe,
            "next": "https://exemple-externe.test/",
        },
    )

    assert reponse.url == reverse("noyau:accueil")


def test_message_d_echec_identique_pour_les_deux_causes(client, utilisateur):
    reponse_inexistant = client.post(
        reverse("administration:connexion"),
        {"identifiant": "personne", "mot_de_passe": "peu-importe"},
    )
    reponse_mauvais_mdp = client.post(
        reverse("administration:connexion"),
        {"identifiant": utilisateur.username, "mot_de_passe": "mauvais"},
    )

    messages_inexistant = [str(m) for m in reponse_inexistant.context["messages"]]
    messages_mauvais_mdp = [str(m) for m in reponse_mauvais_mdp.context["messages"]]
    assert messages_inexistant == messages_mauvais_mdp
    assert len(messages_inexistant) == 1


def test_aucun_mot_de_passe_dans_les_journaux_applicatifs(client, utilisateur, caplog):
    secret = "mot-de-passe-secret-a-chercher-dans-les-journaux"
    with caplog.at_level(logging.DEBUG):
        client.post(
            reverse("administration:connexion"),
            {"identifiant": utilisateur.username, "mot_de_passe": secret},
        )

    assert secret not in caplog.text
