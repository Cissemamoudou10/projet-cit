"""US-PLAN-01, Groupe G — cycle HTTP réel du calendrier académique annuel
(Prompt 28, § 9). G7 (garde du sprint 1) est couvert une fois pour toutes
par tests/architecture/test_ecrans_ecriture.py, vérifié passer sans
modification — non dupliqué ici. Données entièrement fictives.
"""

import datetime

import pytest
from django.urls import reverse

from ressources.models import PeriodeCalendrier
from ressources.services.periode_calendrier import DonneesPeriode, ServicePeriodeCalendrier


def _instant(jour, heure, minute=0):
    return datetime.datetime(2026, 11, jour, heure, minute, tzinfo=datetime.UTC)


def _champs_formulaire(nature, **supplement):
    base = {
        "nature": nature.pk,
        "intitule": "Période HTTP",
        "debut": _instant(2, 8).strftime("%Y-%m-%dT%H:%M"),
        "fin": _instant(5, 8).strftime("%Y-%m-%dT%H:%M"),
        "effet": "",
        "sessions": [],
        "brigades": [],
    }
    base.update(supplement)
    return base


def _creer_periode(planificateur, nature, intitule, jour, **supplement):
    base = {
        "nature": nature,
        "intitule": intitule,
        "debut": _instant(jour, 8),
        "fin": _instant(jour, 10),
        "effet": "",
        "sessions": [],
        "brigades": [],
    }
    base.update(supplement)
    return ServicePeriodeCalendrier.creer(planificateur, DonneesPeriode(**base))


# --- G1 — chemin nominal, profil planification, chaque adresse d'écriture --


def test_g1_declaration_modification_suppression_d_une_periode_reussissent(
    client, planificateur, nature_evenement, session, brigade
):
    client.force_login(planificateur)

    reponse_creation = client.post(
        reverse("ressources:declarer_periode_calendrier"),
        _champs_formulaire(nature_evenement, sessions=[session.pk], brigades=[brigade.pk]),
    )
    assert reponse_creation.status_code == 302
    periode = PeriodeCalendrier.objects.get(intitule="Période HTTP")
    assert list(periode.sessions.all()) == [session]

    reponse_modification = client.post(
        reverse("ressources:modifier_periode_calendrier", args=[periode.pk]),
        {
            **_champs_formulaire(nature_evenement, intitule="Période HTTP modifiée"),
            "modifie_le_attendu": periode.modifie_le.isoformat(),
        },
    )
    assert reponse_modification.status_code == 302
    periode.refresh_from_db()
    assert periode.intitule == "Période HTTP modifiée"

    reponse_suppression = client.post(
        reverse("ressources:supprimer_periode_calendrier", args=[periode.pk])
    )
    assert reponse_suppression.status_code == 302
    assert not PeriodeCalendrier.objects.filter(pk=periode.pk).exists()


def test_g1_natures_d_evenement_crud_reussit(client, planificateur):
    client.force_login(planificateur)

    reponse_creation = client.post(
        reverse("ressources:creer_nature_evenement"),
        {"libelle": "Manifestation", "effet_par_defaut": "informatif"},
    )
    assert reponse_creation.status_code == 302

    from ressources.models import NatureEvenement

    nature = NatureEvenement.objects.get(libelle="Manifestation")
    reponse_suppression = client.post(
        reverse("ressources:supprimer_nature_evenement", args=[nature.pk])
    )
    assert reponse_suppression.status_code == 302
    assert not NatureEvenement.objects.filter(pk=nature.pk).exists()


# --- G2 — vue annuelle, vue mensuelle, fiche : 200 et contenu réel ---------


def test_g2_vue_annuelle_vue_mensuelle_et_fiche_affichent_le_contenu_reel(
    client, planificateur, nature_evenement, session
):
    periode = ServicePeriodeCalendrier.creer(
        planificateur,
        DonneesPeriode(
            nature=nature_evenement,
            intitule="Bivouac visible",
            debut=_instant(2, 8),
            fin=_instant(6, 8),
            effet="",
            sessions=[session],
            brigades=[],
        ),
    )
    client.force_login(planificateur)
    annee = periode.debut.year if periode.debut.month >= 9 else periode.debut.year - 1

    reponse_annuelle = client.get(reverse("ressources:calendrier_annuel"), {"annee": annee})
    reponse_mensuelle = client.get(
        reverse("ressources:calendrier_mensuel"), {"annee": annee, "mois": periode.debut.month}
    )
    reponse_fiche = client.get(reverse("ressources:detail_periode_calendrier", args=[periode.pk]))

    assert reponse_annuelle.status_code == 200
    assert b"Bivouac visible" in reponse_annuelle.content
    assert reponse_mensuelle.status_code == 200
    assert b"Bivouac visible" in reponse_mensuelle.content
    assert reponse_fiche.status_code == 200
    assert session.intitule.encode() in reponse_fiche.content


# --- G3 — les avertissements sont réellement visibles dans la réponse -----


def test_g3_avertissement_de_chevauchement_visible_dans_la_reponse_http(
    client, planificateur, nature_evenement
):
    client.force_login(planificateur)
    client.post(
        reverse("ressources:declarer_periode_calendrier"), _champs_formulaire(nature_evenement)
    )

    reponse = client.post(
        reverse("ressources:declarer_periode_calendrier"),
        _champs_formulaire(
            nature_evenement,
            intitule="Chevauchante",
            debut=_instant(4, 8).strftime("%Y-%m-%dT%H:%M"),
            fin=_instant(7, 8).strftime("%Y-%m-%dT%H:%M"),
        ),
        follow=True,
    )

    assert reponse.status_code == 200
    assert b"Recouvre" in reponse.content


# --- G4 — filtre par cible, portée centre entier incluse -------------------


def test_g4_filtre_par_session_montre_les_periodes_ciblees_et_le_centre_entier(
    client, planificateur, nature_evenement, session, autre_session
):
    ciblee = _creer_periode(planificateur, nature_evenement, "Ciblée A", 2, sessions=[session])
    _creer_periode(planificateur, nature_evenement, "Centre entier", 3)
    _creer_periode(planificateur, nature_evenement, "Ciblée B", 4, sessions=[autre_session])
    client.force_login(planificateur)
    annee = ciblee.debut.year if ciblee.debut.month >= 9 else ciblee.debut.year - 1

    reponse = client.get(
        reverse("ressources:calendrier_annuel"), {"annee": annee, "session": session.pk}
    )

    contenu = reponse.content.decode()
    assert "Ciblée A" in contenu
    assert "Centre entier" in contenu
    assert "Ciblée B" not in contenu


# --- G5/G6 — asymétrie lecture/écriture sur les quatre profils habilités --


@pytest.mark.parametrize(
    "nom_profil", ["redacteur", "cellule_examens", "direction_formation", "administrateur"]
)
def test_g5_ecriture_refusee_hors_planification(client, request, nom_profil, nature_evenement):
    utilisateur = request.getfixturevalue(nom_profil)
    client.force_login(utilisateur)

    reponse = client.post(
        reverse("ressources:declarer_periode_calendrier"), _champs_formulaire(nature_evenement)
    )

    assert reponse.status_code == 403


def test_g6_lecture_accordee_aux_quatre_profils_habilites(
    client, planificateur, redacteur, cellule_examens, direction_formation
):
    for utilisateur in (planificateur, redacteur, cellule_examens, direction_formation):
        client.force_login(utilisateur)
        reponse = client.get(reverse("ressources:calendrier_annuel"))
        assert reponse.status_code == 200


def test_g6_lecture_refusee_a_l_administrateur(client, administrateur):
    client.force_login(administrateur)

    reponse = client.get(reverse("ressources:calendrier_annuel"))

    assert reponse.status_code == 403


# --- G8 — navigation --------------------------------------------------------


def test_g8_onglet_calendrier_atteignable_et_lien_de_declaration_selon_l_ecriture(
    client, planificateur, redacteur
):
    client.force_login(planificateur)
    reponse_planification = client.get(reverse("ressources:calendrier_annuel"))
    assert (
        reverse("ressources:declarer_periode_calendrier") in reponse_planification.content.decode()
    )

    client.force_login(redacteur)
    reponse_pedagogique = client.get(reverse("ressources:calendrier_annuel"))
    assert (
        reverse("ressources:declarer_periode_calendrier")
        not in reponse_pedagogique.content.decode()
    )
    slugs = {onglet["slug"] for onglet in reponse_pedagogique.context["onglets"]}
    assert "calendrier" in slugs
