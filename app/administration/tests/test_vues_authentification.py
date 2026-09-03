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


def test_racine_sans_session_redirige_vers_la_connexion(client):
    """La racine "/" n'a pas de gabarit propre — elle relaie vers l'accueil,
    qui redirige lui-même vers la connexion en l'absence de session. Sans
    ce relais, "/" n'était mappée à aucune vue et affichait une erreur 404.
    """
    reponse = client.get("/")

    assert reponse.status_code == 302
    assert reponse.url == reverse("noyau:accueil")

    reponse_suivante = client.get(reponse.url)
    assert reponse_suivante.status_code == 302
    assert reponse_suivante.url.startswith(reverse("administration:connexion"))


def test_racine_avec_session_ouverte_mene_a_l_accueil(client, utilisateur):
    client.force_login(utilisateur)

    reponse = client.get("/", follow=True)

    assert reponse.status_code == 200
    assert reponse.redirect_chain[-1][0] == reverse("noyau:accueil")


def test_toute_page_protegee_de_l_applicatif_redirige_vers_la_connexion(client):
    """Généralise `test_page_protegee_sans_session_conserve_next` au-delà de
    `noyau:accueil` (seule vue à porter `@login_required` explicitement) :
    sans `ConnexionObligatoireMiddleware`, une session expirée sur un écran
    du référentiel tombait sur le 403 d'`exige_habilitation`
    (`ErreurHabilitation` ne distingue pas « non connecté » de « connecté
    sans le droit »), pas sur l'écran de connexion.
    """
    reponse = client.get(reverse("referentiel:liste_types_formation"))

    assert reponse.status_code == 302
    assert reponse.url.startswith(reverse("administration:connexion"))
    assert "next=" in reponse.url


def test_utilisateur_connecte_sans_le_droit_recoit_toujours_un_403(client, non_administrateur):
    """`ConnexionObligatoireMiddleware` ne doit intercepter que l'anonyme —
    un compte authentifié mais dépourvu de la permission demandée doit
    toujours obtenir le refus d'`exige_habilitation`, pas une redirection.
    """
    client.force_login(non_administrateur)

    reponse = client.get(reverse("administration:liste_comptes"))

    assert reponse.status_code == 403


def test_deconnexion_reste_accessible_meme_sans_session(client):
    """Exemptée du nouvel intergiciel : se déconnecter alors qu'on l'est
    déjà (session expirée entre-temps) ne doit pas détourner par l'écran de
    connexion — `logout()` est sans effet sur une session déjà anonyme.
    """
    reponse = client.post(reverse("administration:deconnexion"))

    assert reponse.status_code == 302
    assert reponse.url == reverse("administration:connexion")


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
