"""US-SES-01 — cycle HTTP réel (`reverse()` + `client`), Groupe C (Prompt 20,
§ 11). Le refus d'habilitation en écriture (C2) et le test de garde
mécanique (C4) sont couverts une fois pour toutes par
tests/architecture/test_ecrans_ecriture.py, sur le même principe que
referentiel/tests/test_refus_ecriture_direct.py.
"""

import pytest
from django.urls import reverse

from organisation.models import Session
from referentiel.models import CategorieLieu, ElementReferentiel, Formation, Matiere


def test_c1_creer_par_l_ecran_cree_reellement_la_session(client, redacteur, formation):
    client.force_login(redacteur)

    assert client.get(reverse("organisation:liste_sessions")).status_code == 200
    assert client.get(reverse("organisation:creer_session")).status_code == 200

    reponse = client.post(
        reverse("organisation:creer_session"),
        {
            "formation": formation.pk,
            "intitule": "Session HTTP",
            "date_debut": "2026-01-05",
            "date_fin": "2026-03-27",
            "effectif_attendu": 24,
        },
    )

    assert reponse.status_code == 302
    assert Session.objects.filter(intitule="Session HTTP").exists()


def test_c1_modifier_par_l_ecran_modifie_reellement_la_session(client, redacteur, session):
    client.force_login(redacteur)

    reponse = client.post(
        reverse("organisation:modifier_session", args=[session.pk]),
        {
            "formation": session.formation.pk,
            "intitule": "Session modifiée",
            "date_debut": "2026-01-05",
            "date_fin": "2026-03-27",
            "effectif_attendu": 30,
            "modifie_le_attendu": session.modifie_le.isoformat(),
        },
    )

    assert reponse.status_code == 302
    session.refresh_from_db()
    assert session.intitule == "Session modifiée"
    assert session.effectif_attendu == 30


def test_c1_supprimer_par_l_ecran_supprime_reellement_la_session(client, redacteur, session):
    client.force_login(redacteur)

    reponse = client.post(reverse("organisation:supprimer_session", args=[session.pk]))

    assert reponse.status_code == 302
    assert not Session.objects.filter(pk=session.pk).exists()


@pytest.mark.parametrize(
    "nom_utilisateur", ["redacteur", "lecteur", "planificateur", "direction_formation"]
)
def test_c3_lecture_accordee_aux_quatre_profils_habilites(
    client, request, session, nom_utilisateur
):
    client.force_login(request.getfixturevalue(nom_utilisateur))

    assert client.get(reverse("organisation:liste_sessions")).status_code == 200
    assert client.get(reverse("organisation:detail_session", args=[session.pk])).status_code == 200


def test_c3_lecture_refusee_a_l_administrateur(client, administrateur, session):
    client.force_login(administrateur)

    assert client.get(reverse("organisation:liste_sessions")).status_code == 403
    assert client.get(reverse("organisation:detail_session", args=[session.pk])).status_code == 403


def test_c5_navigation_presente_pour_profil_habilite(client, redacteur):
    client.force_login(redacteur)

    reponse = client.get(reverse("noyau:accueil"))

    assert "Sessions" in reponse.content.decode()


def test_c5_navigation_absente_pour_administrateur(client, administrateur):
    client.force_login(administrateur)

    reponse = client.get(reverse("noyau:accueil"))

    assert "Sessions" not in reponse.content.decode()


@pytest.fixture
def formation_intensive(type_officiers):
    formation = Formation.objects.create(
        intitule="Formation intensive HTTP",
        specialite="Transmissions",
        duree_semaines=1,
        type_formation=type_officiers,
    )
    ElementReferentiel.objects.create(
        formation=formation,
        matiere=Matiere.objects.create(intitule="Cryptographie HTTP", code="CRYH1"),
        volume_horaire_prescrit=200,
        categorie_lieu=CategorieLieu.SALLE_ATTITREE,
        type_lieu_partage=None,
    )
    return formation


def test_c6_avertissement_e2_visible_dans_la_reponse_http(client, redacteur, formation_intensive):
    client.force_login(redacteur)

    reponse = client.post(
        reverse("organisation:creer_session"),
        {
            "formation": formation_intensive.pk,
            "intitule": "Session intensive",
            "date_debut": "2026-01-05",
            "date_fin": "2026-01-12",
            "effectif_attendu": 24,
        },
        follow=True,
    )

    assert reponse.status_code == 200
    assert "RG-65" in reponse.content.decode()


def test_c7_bloc_referentiel_applique_affiche_les_valeurs_reelles(client, redacteur, session):
    client.force_login(redacteur)

    reponse = client.get(reverse("organisation:detail_session", args=[session.pk]))
    contenu = reponse.content.decode()

    assert "<dd>1</dd>" in contenu
    assert "40 h" in contenu


def test_bloc_evaluations_lie_les_proces_verbaux_pour_la_direction_de_formation(
    client, direction_formation, session
):
    """Correctif de navigation, prompt 49 (hors backlog) : la fiche session
    ne liait vers aucun écran d'`evaluations` — Direction de Formation
    porte `evaluations_lecture`, jamais `evaluations_ecriture` (matrice
    § 11.2), donc les procès-verbaux mais pas les moyennes."""
    client.force_login(direction_formation)

    reponse = client.get(reverse("organisation:detail_session", args=[session.pk]))
    contenu = reponse.content.decode()

    assert "Procès-verbaux" in contenu
    assert "Moyennes et classement" not in contenu


def test_bloc_evaluations_absent_sans_aucune_permission_du_domaine(client, redacteur, session):
    client.force_login(redacteur)

    reponse = client.get(reverse("organisation:detail_session", args=[session.pk]))
    contenu = reponse.content.decode()

    assert "Procès-verbaux" not in contenu
    assert "Moyennes et classement" not in contenu
