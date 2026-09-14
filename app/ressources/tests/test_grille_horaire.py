"""US-PLAN-12, Groupes A (grille), C (activation) et D2 — Prompt 29.
Données entièrement fictives.
"""

import datetime

import pytest
from django.db import IntegrityError, transaction
from django.utils import timezone

from administration.models import EntreeJournal, TypeAction
from noyau.exceptions import ErreurValidation
from ressources.models import CreneauType, GrilleHoraire, JourSemaine
from ressources.services.grille_horaire import ServiceGrilleHoraire


def _grille(intitule="Ordinaire", **supplement):
    return GrilleHoraire.objects.create(intitule=intitule, **supplement)


def _creneau(grille, jour=JourSemaine.LUNDI, ordre=1, debut="08:00", fin="09:45"):
    return CreneauType.objects.create(
        grille=grille, jour_semaine=jour, ordre=ordre, heure_debut=debut, heure_fin=fin
    )


def _activer(planificateur, intitule="Ordinaire"):
    grille = _grille(intitule)
    _creneau(grille)
    return ServiceGrilleHoraire.activer(planificateur, grille.pk)


# --- A1 — création nominale, journalisée ------------------------------------


def test_a1_creation_nominale_journalisee_grille_inactive_sans_date_activation(planificateur):
    grille = ServiceGrilleHoraire.creer(planificateur, "Ordinaire")

    assert grille.active is False
    assert grille.date_activation is None
    natures = list(
        EntreeJournal.objects.filter(objet_type="grille_horaire").values_list(
            "type_action", flat=True
        )
    )
    assert TypeAction.CREATION_ELEMENT_GESTION in natures


# --- A2 — unicité de l'intitulé, casse indifférente -------------------------


def test_a2_unicite_de_l_intitule_casse_indifferente(planificateur):
    ServiceGrilleHoraire.creer(planificateur, "Ordinaire")

    with pytest.raises(ErreurValidation):
        ServiceGrilleHoraire.creer(planificateur, "ORDINAIRE")


def test_a2_unicite_de_l_intitule_par_insertion_directe(planificateur):
    _grille("Ordinaire")

    with pytest.raises(IntegrityError), transaction.atomic():
        _grille("ordinaire")


# --- A3 — duplication --------------------------------------------------------


def test_a3_duplication_nouvelle_grille_inactive_tous_les_creneaux_copies(planificateur):
    source = _grille("Ordinaire")
    _creneau(source, JourSemaine.LUNDI, 1, "08:00", "09:45")
    _creneau(source, JourSemaine.LUNDI, 2, "10:10", "12:00")

    copie = ServiceGrilleHoraire.dupliquer(planificateur, source.pk, "Ramadan")

    assert copie.active is False
    assert copie.pk != source.pk
    assert copie.creneaux.count() == 2
    assert {
        (c.jour_semaine, c.ordre, c.heure_debut, c.heure_fin) for c in copie.creneaux.all()
    } == {(c.jour_semaine, c.ordre, c.heure_debut, c.heure_fin) for c in source.creneaux.all()}
    source.refresh_from_db()
    assert source.creneaux.count() == 2


# --- A4/A5/A6 — suppression --------------------------------------------------


def test_a4_suppression_d_une_grille_jamais_activee_acceptee(planificateur):
    grille = _grille("Brouillon")

    ServiceGrilleHoraire.supprimer(planificateur, grille.pk)

    assert not GrilleHoraire.objects.filter(pk=grille.pk).exists()


def test_a5_suppression_d_une_grille_deja_activee_par_le_passe_refusee(planificateur):
    grille = _activer(planificateur, "Ordinaire")
    autre = _grille("Ramadan")
    _creneau(autre)
    ServiceGrilleHoraire.activer(planificateur, autre.pk)
    grille.refresh_from_db()
    assert grille.active is False
    assert grille.date_activation is not None

    with pytest.raises(ErreurValidation, match="archiv"):
        ServiceGrilleHoraire.supprimer(planificateur, grille.pk)

    assert GrilleHoraire.objects.filter(pk=grille.pk).exists()


def test_a6_suppression_de_la_grille_active_refusee(planificateur):
    grille = _activer(planificateur, "Ordinaire")

    with pytest.raises(ErreurValidation):
        ServiceGrilleHoraire.supprimer(planificateur, grille.pk)

    assert GrilleHoraire.objects.filter(pk=grille.pk).exists()


# --- A7/A8 — archivage --------------------------------------------------------


def test_a7_archivage_de_la_grille_active_refuse(planificateur):
    grille = _activer(planificateur, "Ordinaire")

    with pytest.raises(ErreurValidation):
        ServiceGrilleHoraire.archiver(planificateur, grille.pk)


def test_a8_archivage_d_une_grille_inactive_accepte_reste_consultable(planificateur):
    grille = _grille("Obsolète")
    _creneau(grille)

    archivee = ServiceGrilleHoraire.archiver(planificateur, grille.pk)

    assert archivee.archive is True
    assert GrilleHoraire.objects.filter(pk=grille.pk).exists()
    assert ServiceGrilleHoraire.obtenir(grille.pk).intitule == "Obsolète"


# --- C1/C2 — activation nominale et RG-62 -----------------------------------


def test_c1_activation_nominale_grille_active_date_et_agent_renseignes_journalisee(
    planificateur,
):
    grille = _grille("Ordinaire")
    _creneau(grille)

    activee = ServiceGrilleHoraire.activer(planificateur, grille.pk)

    assert activee.active is True
    assert activee.date_activation is not None
    assert activee.activee_par == planificateur
    natures = list(
        EntreeJournal.objects.filter(
            objet_type="grille_horaire", objet_identifiant=str(grille.pk)
        ).values_list("type_action", flat=True)
    )
    assert TypeAction.MODIFICATION_ELEMENT_GESTION in natures


def test_c2_activer_une_seconde_grille_desactive_la_premiere_une_seule_active(planificateur):
    premiere = _activer(planificateur, "Ordinaire")
    seconde = _grille("Ramadan")
    _creneau(seconde)

    ServiceGrilleHoraire.activer(planificateur, seconde.pk)

    premiere.refresh_from_db()
    seconde.refresh_from_db()
    assert premiere.active is False
    assert seconde.active is True
    assert GrilleHoraire.objects.filter(active=True).count() == 1


# --- C3 — transaction : échec au milieu de l'activation ----------------------


def test_c3_echec_au_milieu_de_l_activation_n_altere_aucune_grille(planificateur, monkeypatch):
    premiere = _activer(planificateur, "Ordinaire")
    seconde = _grille("Ramadan")
    _creneau(seconde)

    from noyau.services import base as service_base

    def _echoue(*args, **kwargs):
        raise RuntimeError("panne simulée")

    monkeypatch.setattr(service_base.ServiceBase, "modifier", staticmethod(_echoue))

    with pytest.raises(RuntimeError):
        ServiceGrilleHoraire.activer(planificateur, seconde.pk)

    premiere.refresh_from_db()
    seconde.refresh_from_db()
    assert premiere.active is True
    assert seconde.active is False
    assert GrilleHoraire.objects.filter(active=True).count() == 1


# --- C4 — contrainte en base : partielle, pas globale ------------------------


def test_c4_deux_grilles_actives_par_insertion_directe_rejetees(planificateur):
    _grille(
        "Une",
        active=True,
        date_activation=timezone.now(),
        activee_par=planificateur,
    )
    with pytest.raises(IntegrityError), transaction.atomic():
        _grille("Deux", active=True, date_activation=timezone.now(), activee_par=planificateur)


def test_c4_deux_grilles_inactives_acceptees_index_bien_partiel(db):
    _grille("Une")
    _grille("Deux")

    assert GrilleHoraire.objects.filter(active=False).count() == 2


# --- C5 — E3 : activation d'une grille sans créneau refusée ------------------


def test_c5_activation_d_une_grille_sans_creneau_refusee(planificateur):
    grille = _grille("Vide")

    with pytest.raises(ErreurValidation):
        ServiceGrilleHoraire.activer(planificateur, grille.pk)


# --- C6 — activation d'une grille archivée refusée ---------------------------


def test_c6_activation_d_une_grille_archivee_refusee(planificateur):
    grille = _grille("Obsolète")
    _creneau(grille)
    ServiceGrilleHoraire.archiver(planificateur, grille.pk)

    with pytest.raises(ErreurValidation):
        ServiceGrilleHoraire.activer(planificateur, grille.pk)


# --- C7 — date_activation de la grille désactivée conservée ------------------


def test_c7_date_activation_de_la_grille_desactivee_est_conservee(planificateur):
    premiere = _activer(planificateur, "Ordinaire")
    date_premiere_activation = premiere.date_activation
    seconde = _grille("Ramadan")
    _creneau(seconde)

    ServiceGrilleHoraire.activer(planificateur, seconde.pk)

    premiere.refresh_from_db()
    assert premiere.date_activation == date_premiere_activation
    assert premiere.date_activation is not None


# --- C8 — cohérence en base : active vrai sans date rejeté -------------------


def test_c8_active_vrai_sans_date_activation_rejete_par_insertion_directe(planificateur):
    with pytest.raises(IntegrityError), transaction.atomic():
        _grille("Invalide", active=True, date_activation=None)


def test_c8_active_vrai_sans_agent_rejete_par_insertion_directe(planificateur):
    with pytest.raises(IntegrityError), transaction.atomic():
        _grille("Invalide", active=True, date_activation=timezone.now(), activee_par=None)


# --- C9 — zéro grille active, état accepté -----------------------------------


def test_c9_zero_grille_active_est_un_etat_accepte(planificateur):
    _grille("Ordinaire")
    _grille("Ramadan")

    assert GrilleHoraire.objects.filter(active=True).count() == 0
    assert ServiceGrilleHoraire.volume_hebdomadaire_reference() is None


# --- D2 — créer une période de calendrier ne change aucune grille active ----


def test_d2_creer_une_periode_de_calendrier_ne_change_aucune_grille_active(
    planificateur, nature_evenement
):
    grille = _activer(planificateur, "Ordinaire")

    from ressources.services.periode_calendrier import DonneesPeriode, ServicePeriodeCalendrier

    ServicePeriodeCalendrier.creer(
        planificateur,
        DonneesPeriode(
            nature=nature_evenement,
            intitule="Congé général",
            debut=datetime.datetime(2026, 11, 2, tzinfo=datetime.UTC),
            fin=datetime.datetime(2026, 11, 3, tzinfo=datetime.UTC),
            effet="",
            sessions=[],
            brigades=[],
        ),
    )

    grille.refresh_from_db()
    assert grille.active is True
    assert GrilleHoraire.objects.filter(active=True).count() == 1
