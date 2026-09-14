"""US-PLAN-12, Groupe G1 — chargement des deux grilles de départ (Prompt 29,
§ 6) : heures EXACTES, grille ordinaire active, samedi et dimanche vides,
idempotence (P-37 : jamais une migration de données). Données fictives, mais
les horaires eux-mêmes viennent du terrain (§ 6) et ne doivent pas être
« corrigés ».
"""

import datetime

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command

from ressources.models import GrilleHoraire, JourSemaine


@pytest.fixture
def administrateur_systeme(db):
    modele = get_user_model()
    return modele.objects.create_superuser(
        username="bootstrap-technique",
        password="x",
        grade="Lt",
        profil=modele.Profil.ADMINISTRATEUR,
    )


def _heures(grille, jour):
    return [
        (c.heure_debut, c.heure_fin)
        for c in grille.creneaux.filter(jour_semaine=jour).order_by("ordre")
    ]


def test_g1_aucun_administrateur_leve_une_erreur_actionnable(db):
    from django.core.management.base import CommandError

    with pytest.raises(CommandError, match="administrateur"):
        call_command("initialiser_grilles_horaires")


def test_g1_les_deux_grilles_sont_presentes_avec_leurs_heures_exactes(administrateur_systeme):
    call_command("initialiser_grilles_horaires")

    ordinaire = GrilleHoraire.objects.get(intitule="Ordinaire")
    ramadan = GrilleHoraire.objects.get(intitule="Ramadan")

    assert _heures(ordinaire, JourSemaine.LUNDI) == [
        (datetime.time(8, 0), datetime.time(9, 45)),
        (datetime.time(10, 10), datetime.time(12, 0)),
        (datetime.time(13, 0), datetime.time(14, 15)),
        (datetime.time(14, 40), datetime.time(16, 0)),
    ]
    assert _heures(ramadan, JourSemaine.VENDREDI) == [
        (datetime.time(8, 30), datetime.time(9, 50)),
        (datetime.time(10, 0), datetime.time(11, 20)),
        (datetime.time(11, 30), datetime.time(12, 50)),
        (datetime.time(13, 10), datetime.time(14, 30)),
    ]


def test_g1_la_grille_ordinaire_est_active_ramadan_ne_l_est_pas(administrateur_systeme):
    call_command("initialiser_grilles_horaires")

    ordinaire = GrilleHoraire.objects.get(intitule="Ordinaire")
    ramadan = GrilleHoraire.objects.get(intitule="Ramadan")

    assert ordinaire.active is True
    assert ordinaire.activee_par == administrateur_systeme
    assert ramadan.active is False


def test_g1_samedi_et_dimanche_n_ont_aucun_creneau(administrateur_systeme):
    call_command("initialiser_grilles_horaires")

    for intitule in ("Ordinaire", "Ramadan"):
        grille = GrilleHoraire.objects.get(intitule=intitule)
        assert _heures(grille, JourSemaine.SAMEDI) == []
        assert _heures(grille, JourSemaine.DIMANCHE) == []


def test_g1_idempotence_un_second_appel_ne_duplique_ni_ne_reactive(administrateur_systeme):
    call_command("initialiser_grilles_horaires")
    ordinaire = GrilleHoraire.objects.get(intitule="Ordinaire")
    date_premiere_activation = ordinaire.date_activation

    from ressources.services.grille_horaire import ServiceGrilleHoraire

    ramadan = GrilleHoraire.objects.get(intitule="Ramadan")
    ServiceGrilleHoraire.activer(administrateur_systeme, ramadan.pk)

    call_command("initialiser_grilles_horaires")

    assert GrilleHoraire.objects.count() == 2
    ordinaire.refresh_from_db()
    ramadan.refresh_from_db()
    assert ordinaire.date_activation == date_premiere_activation
    assert ramadan.active is True
    assert ordinaire.active is False


# --- pas d'hypothèse « exactement deux grilles » (§ 6, directive utilisateur)


def test_aucun_libelle_en_dur_ne_suppose_exactement_deux_grilles(administrateur_systeme):
    """Une troisième grille doit pouvoir être créée sans toucher au code —
    ce test ne compte que les deux grilles de départ elles-mêmes, jamais un
    total figé du catalogue."""
    call_command("initialiser_grilles_horaires")

    GrilleHoraire.objects.create(intitule="Horaire d'été")

    assert GrilleHoraire.objects.count() == 3
    assert GrilleHoraire.objects.filter(intitule__in=["Ordinaire", "Ramadan"]).count() == 2
