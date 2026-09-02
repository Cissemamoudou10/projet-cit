"""ServiceAuthentification — RG-01, RG-03, RG-26, CU-P1-01."""

from datetime import timedelta

import pytest
from django.utils import timezone

from administration.models import EntreeJournal
from administration.services.authentification import (
    MESSAGE_IDENTIFIANTS_INVALIDES,
    ServiceAuthentification,
)
from noyau.exceptions import ErreurAuthentification, ErreurCompteDesactive, ErreurCompteVerrouille


def test_identifiants_valides_retourne_l_utilisateur(utilisateur, mot_de_passe):
    resultat = ServiceAuthentification.authentifier(utilisateur.username, mot_de_passe)
    assert resultat == utilisateur


def test_identifiant_inexistant_leve_erreur_authentification(db):
    with pytest.raises(ErreurAuthentification):
        ServiceAuthentification.authentifier("personne", "peu-importe")


def test_mot_de_passe_errone_leve_la_meme_exception_et_le_meme_message(utilisateur):
    with pytest.raises(ErreurAuthentification) as errone:
        ServiceAuthentification.authentifier(utilisateur.username, "mauvais-mot-de-passe")
    with pytest.raises(ErreurAuthentification) as inexistant:
        ServiceAuthentification.authentifier("personne", "peu-importe")

    assert str(errone.value) == str(inexistant.value) == MESSAGE_IDENTIFIANTS_INVALIDES


def test_compte_desactive_leve_erreur_compte_desactive(utilisateur, mot_de_passe):
    utilisateur.is_active = False
    utilisateur.save()

    with pytest.raises(ErreurCompteDesactive):
        ServiceAuthentification.authentifier(utilisateur.username, mot_de_passe)


def test_cinq_echecs_verrouille_le_compte(utilisateur):
    for _ in range(5):
        with pytest.raises(ErreurAuthentification):
            ServiceAuthentification.authentifier(utilisateur.username, "mauvais")

    utilisateur.refresh_from_db()
    assert utilisateur.echecs_consecutifs == 5
    assert utilisateur.verrouille_jusqu_a is not None
    assert utilisateur.verrouille_jusqu_a > timezone.now()


def test_quatre_echecs_puis_succes_remet_le_compteur_a_zero(utilisateur, mot_de_passe):
    for _ in range(4):
        with pytest.raises(ErreurAuthentification):
            ServiceAuthentification.authentifier(utilisateur.username, "mauvais")

    ServiceAuthentification.authentifier(utilisateur.username, mot_de_passe)

    utilisateur.refresh_from_db()
    assert utilisateur.echecs_consecutifs == 0
    assert utilisateur.verrouille_jusqu_a is None


def test_verrouillage_expire_redevient_authentifiable(utilisateur, mot_de_passe):
    utilisateur.echecs_consecutifs = 5
    utilisateur.verrouille_jusqu_a = timezone.now() - timedelta(seconds=1)
    utilisateur.save()

    resultat = ServiceAuthentification.authentifier(utilisateur.username, mot_de_passe)
    assert resultat == utilisateur


def test_compte_verrouille_avec_bon_mot_de_passe_reste_refuse(utilisateur, mot_de_passe):
    utilisateur.echecs_consecutifs = 5
    utilisateur.verrouille_jusqu_a = timezone.now() + timedelta(minutes=15)
    utilisateur.save()

    with pytest.raises(ErreurCompteVerrouille):
        ServiceAuthentification.authentifier(utilisateur.username, mot_de_passe)


def test_chaque_echec_produit_une_entree_de_journal(utilisateur):
    with pytest.raises(ErreurAuthentification):
        ServiceAuthentification.authentifier(utilisateur.username, "mauvais")

    assert EntreeJournal.objects.filter(identifiant_saisi=utilisateur.username).count() == 1


def test_echec_sur_identifiant_inexistant_journalise_sans_auteur(db):
    with pytest.raises(ErreurAuthentification):
        ServiceAuthentification.authentifier("personne", "peu-importe")

    entree = EntreeJournal.objects.get(identifiant_saisi="personne")
    assert entree.auteur is None


def test_mot_de_passe_absent_de_toute_entree_de_journal(utilisateur):
    secret = "un-mot-de-passe-tres-particulier-a-chercher"
    with pytest.raises(ErreurAuthentification):
        ServiceAuthentification.authentifier(utilisateur.username, secret)

    for entree in EntreeJournal.objects.all():
        assert secret not in entree.detail
        assert secret not in entree.identifiant_saisi
        assert secret not in entree.cible


def test_les_seuils_sont_lus_dans_les_reglages(utilisateur, settings):
    settings.AUTH_SEUIL_ECHECS = 2

    for _ in range(2):
        with pytest.raises(ErreurAuthentification):
            ServiceAuthentification.authentifier(utilisateur.username, "mauvais")

    utilisateur.refresh_from_db()
    assert utilisateur.verrouille_jusqu_a is not None
