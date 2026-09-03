"""Critère 6 (§ 2.3, § 7, § 8) — le masquage est une conséquence, pas le
mécanisme : l'accès direct par URL est refusé avec la même rigueur que le
masquage de menu, et un refus ne journalise qu'une fois par tentative, jamais
par affichage.
"""

import pytest
from django.urls import reverse

from administration.habilitations import verifier_habilitation
from administration.models import EntreeJournal, TypeAction
from noyau.exceptions import ErreurHabilitation


def test_acces_direct_a_l_url_sans_permission_est_refuse(client, non_administrateur):
    client.force_login(non_administrateur)

    reponse = client.get(reverse("administration:habilitations"))

    assert reponse.status_code == 403


def test_acces_direct_a_l_url_avec_permission_est_accepte(client, administrateur):
    client.force_login(administrateur)

    reponse = client.get(reverse("administration:habilitations"))

    assert reponse.status_code == 200


def test_un_lien_de_retour_vers_les_comptes_est_present(client, administrateur):
    """Sans lien de retour, l'écran des habilitations est une impasse de
    navigation — seule la rubrique de tête ramène ailleurs, indirectement.
    """
    client.force_login(administrateur)

    reponse = client.get(reverse("administration:habilitations"))

    assert reverse("administration:liste_comptes").encode() in reponse.content


def test_la_rubrique_administration_est_masquee_sans_la_permission(client, non_administrateur):
    client.force_login(non_administrateur)

    reponse = client.get(reverse("noyau:accueil"))

    assert "Administration" not in reponse.content.decode()


def test_la_rubrique_administration_apparait_avec_la_permission(client, administrateur):
    client.force_login(administrateur)

    reponse = client.get(reverse("noyau:accueil"))

    assert "Administration" in reponse.content.decode()


def test_le_service_refuse_l_appel_meme_sans_passer_par_la_vue(non_administrateur):
    """Le masquage de bouton ne suffit pas : un appel direct au service qui
    contournerait la vue doit être refusé au même titre (§ 2.3).
    """
    with pytest.raises(ErreurHabilitation):
        verifier_habilitation(non_administrateur, "noyau.administration_ecriture")


def test_le_refus_est_journalise_une_fois_par_tentative_pas_par_affichage(
    client, non_administrateur
):
    client.force_login(non_administrateur)

    for _ in range(3):
        client.get(reverse("noyau:accueil"))  # affichage du menu, masquage silencieux
    assert not EntreeJournal.objects.filter(type_action=TypeAction.ACCES_REFUSE).exists()

    client.get(reverse("administration:habilitations"))  # une tentative réelle

    assert EntreeJournal.objects.filter(type_action=TypeAction.ACCES_REFUSE).count() == 1
