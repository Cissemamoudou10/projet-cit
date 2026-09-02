"""Réglages de configuration — points non négociables du socle."""


def test_auth_user_model_est_administration_utilisateur(settings):
    assert settings.AUTH_USER_MODEL == "administration.Utilisateur"


def test_reglages_de_fuseau(settings):
    assert settings.USE_TZ is True
    assert settings.TIME_ZONE == "Africa/Casablanca"
