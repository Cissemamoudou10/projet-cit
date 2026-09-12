"""US-SES-04 — cycle HTTP réel de la fiche de session, Groupe B (Prompt 23,
§ 11). B1 (contenu réel avec une salle attitrée et un taux calculé) et B3
(moitié planification) exigent un vrai `SalleAttitree` : `organisation` ne
peut pas en construire un (D-85, sens de dépendance) — ils vivent dans
`app/ressources/tests/test_composition_session_ecran.py`, seule application
autorisée à importer les deux côtés. Ici : tout ce qui ne suppose aucune
salle attitrée réelle.
"""

import pytest
from django.urls import reverse


def test_a6_session_sans_aucune_brigade_signalement_affiche_pas_de_tableau_vide(
    client, redacteur, session
):
    client.force_login(redacteur)

    reponse = client.get(reverse("organisation:detail_session", args=[session.pk]))

    assert "Aucune brigade constituée" in reponse.content.decode()


@pytest.mark.parametrize(
    "nom_utilisateur", ["redacteur", "lecteur", "planificateur", "direction_formation"]
)
def test_b1_ges_fiche_accessible_et_contenu_de_base_present(
    client, request, nom_utilisateur, session, brigade
):
    client.force_login(request.getfixturevalue(nom_utilisateur))

    reponse = client.get(reverse("organisation:detail_session", args=[session.pk]))
    contenu = reponse.content.decode()

    assert reponse.status_code == 200
    assert brigade.designation in contenu
    assert str(brigade.effectif_previsionnel) in contenu


def test_b2_direction_de_formation_acces_accorde_et_aucune_commande_d_ecriture(
    client, direction_formation, session, brigade
):
    client.force_login(direction_formation)

    reponse = client.get(reverse("organisation:detail_session", args=[session.pk]))
    contenu = reponse.content.decode()

    assert reponse.status_code == 200
    assert reverse("organisation:modifier_session", args=[session.pk]) not in contenu
    assert reverse("organisation:brigades_session", args=[session.pk]) not in contenu
    assert reverse("ressources:affecter_salle", args=[brigade.pk]) not in contenu


def test_b3_pedagogique_voit_le_lien_vers_les_brigades_pas_celui_de_la_salle(
    client, redacteur, session, brigade
):
    client.force_login(redacteur)

    reponse = client.get(reverse("organisation:detail_session", args=[session.pk]))
    contenu = reponse.content.decode()

    assert reverse("organisation:brigades_session", args=[session.pk]) in contenu
    assert reverse("ressources:affecter_salle", args=[brigade.pk]) not in contenu


def test_b3_planification_voit_le_lien_vers_la_salle_pas_celui_des_brigades(
    client, planificateur, session, brigade
):
    client.force_login(planificateur)

    reponse = client.get(reverse("organisation:detail_session", args=[session.pk]))
    contenu = reponse.content.decode()

    assert reverse("ressources:affecter_salle", args=[brigade.pk]) in contenu
    assert reverse("organisation:brigades_session", args=[session.pk]) not in contenu


def test_b4_administrateur_refuse(client, administrateur, session):
    client.force_login(administrateur)

    reponse = client.get(reverse("organisation:detail_session", args=[session.pk]))

    assert reponse.status_code == 403


def test_b5_navigation_presente_pour_direction_de_formation(client, direction_formation):
    client.force_login(direction_formation)

    reponse = client.get(reverse("noyau:accueil"))

    assert "Sessions" in reponse.content.decode()
