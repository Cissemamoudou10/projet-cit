"""US-PLAN-12, Groupe B — créneaux types, non-recouvrement (E1) en services,
absence de date, CASCADE (Prompt 29, § 5). Données entièrement fictives.
"""

import datetime

import pytest
from django.db import IntegrityError, transaction

from administration.models import EntreeJournal, TypeAction
from noyau.exceptions import ErreurValidation
from ressources.models import CreneauType, GrilleHoraire, JourSemaine
from ressources.services.grille_horaire import ServiceCreneauType, ServiceGrilleHoraire


def _grille(intitule="Ordinaire"):
    return GrilleHoraire.objects.create(intitule=intitule)


def _heure(texte):
    heure, minute = texte.split(":")
    return datetime.time(int(heure), int(minute))


def _donnees(jour=JourSemaine.LUNDI, ordre=1, debut="08:00", fin="09:45"):
    """`heure_debut`/`heure_fin` sont des `datetime.time` — comme ce que
    livre `FormulaireCreneauType.cleaned_data`, jamais des chaînes brutes
    (.claude/rules/tests.md : ne jamais fournir au service un type que la
    vue ne lui donnerait pas non plus)."""
    return {
        "jour_semaine": jour,
        "ordre": ordre,
        "heure_debut": _heure(debut),
        "heure_fin": _heure(fin),
    }


# --- B1 — ajout nominal, journalisé ------------------------------------------


def test_b1_ajout_nominal_journalise(planificateur):
    grille = _grille()

    creneau = ServiceCreneauType.ajouter(planificateur, grille, _donnees())

    assert creneau.grille_id == grille.pk
    natures = list(
        EntreeJournal.objects.filter(objet_type="creneau_type").values_list(
            "type_action", flat=True
        )
    )
    assert TypeAction.CREATION_ELEMENT_GESTION in natures


# --- B2 — E1 : recouvrement même jour, même grille — refus -------------------


def test_b2_deux_creneaux_du_meme_jour_qui_se_recouvrent_refuses(planificateur):
    grille = _grille()
    ServiceCreneauType.ajouter(planificateur, grille, _donnees(debut="08:00", fin="09:45"))

    with pytest.raises(ErreurValidation, match="08:00|09:45"):
        ServiceCreneauType.ajouter(
            planificateur, grille, _donnees(ordre=2, debut="09:00", fin="10:00")
        )


# --- B3 — bornes contiguës acceptées ------------------------------------------


def test_b3_creneaux_contigus_fin_de_l_un_egale_au_debut_du_suivant_acceptes(planificateur):
    grille = _grille()
    ServiceCreneauType.ajouter(planificateur, grille, _donnees(ordre=1, debut="08:00", fin="09:45"))

    second = ServiceCreneauType.ajouter(
        planificateur, grille, _donnees(ordre=2, debut="09:45", fin="11:00")
    )

    assert second.heure_debut.strftime("%H:%M") == "09:45"


# --- B4 — même recouvrement, deux jours différents — accepté -----------------


def test_b4_meme_recouvrement_horaire_sur_deux_jours_differents_accepte(planificateur):
    grille = _grille()
    ServiceCreneauType.ajouter(
        planificateur, grille, _donnees(JourSemaine.LUNDI, 1, "08:00", "09:45")
    )

    mardi = ServiceCreneauType.ajouter(
        planificateur, grille, _donnees(JourSemaine.MARDI, 1, "08:00", "09:45")
    )

    assert mardi.jour_semaine == JourSemaine.MARDI


# --- B5 — même recouvrement, deux grilles différentes — accepté --------------


def test_b5_meme_recouvrement_horaire_meme_jour_deux_grilles_differentes_accepte(planificateur):
    premiere = _grille("Ordinaire")
    seconde = _grille("Ramadan")
    ServiceCreneauType.ajouter(planificateur, premiere, _donnees(debut="08:00", fin="09:45"))

    creneau = ServiceCreneauType.ajouter(
        planificateur, seconde, _donnees(debut="08:00", fin="09:45")
    )

    assert creneau.grille_id == seconde.pk


# --- B6 — heure_fin <= heure_debut : refus, aussi en base --------------------


def test_b6_heure_fin_anterieure_ou_egale_refusee_par_le_service(planificateur):
    grille = _grille()

    with pytest.raises(ErreurValidation):
        ServiceCreneauType.ajouter(planificateur, grille, _donnees(debut="10:00", fin="09:00"))

    with pytest.raises(ErreurValidation):
        ServiceCreneauType.ajouter(planificateur, grille, _donnees(debut="10:00", fin="10:00"))


def test_b6_heure_fin_anterieure_ou_egale_refusee_par_insertion_directe(db):
    grille = _grille()

    with pytest.raises(IntegrityError), transaction.atomic():
        CreneauType.objects.create(
            grille=grille,
            jour_semaine=JourSemaine.LUNDI,
            ordre=1,
            heure_debut="10:00",
            heure_fin="10:00",
        )


# --- B7 — unicité du rang dans le jour, par insertion directe ----------------


def test_b7_unicite_du_rang_dans_le_jour_par_insertion_directe(db):
    grille = _grille()
    CreneauType.objects.create(
        grille=grille,
        jour_semaine=JourSemaine.LUNDI,
        ordre=1,
        heure_debut="08:00",
        heure_fin="09:45",
    )

    with pytest.raises(IntegrityError), transaction.atomic():
        CreneauType.objects.create(
            grille=grille,
            jour_semaine=JourSemaine.LUNDI,
            ordre=1,
            heure_debut="10:10",
            heure_fin="12:00",
        )


# --- B8 — A4 : samedi et dimanche vides, grille valide et activable ---------


def test_b8_grille_avec_samedi_et_dimanche_vides_est_valide_et_activable(planificateur):
    grille = _grille()
    for jour in [
        JourSemaine.LUNDI,
        JourSemaine.MARDI,
        JourSemaine.MERCREDI,
        JourSemaine.JEUDI,
        JourSemaine.VENDREDI,
    ]:
        ServiceCreneauType.ajouter(planificateur, grille, _donnees(jour, 1, "08:00", "09:45"))

    assert grille.creneaux.filter(jour_semaine=JourSemaine.SAMEDI).count() == 0
    assert grille.creneaux.filter(jour_semaine=JourSemaine.DIMANCHE).count() == 0

    activee = ServiceGrilleHoraire.activer(planificateur, grille.pk)
    assert activee.active is True


# --- B9 — aucun champ de date sur CreneauType --------------------------------


def test_b9_aucun_champ_de_date_sur_creneau_type():
    """`cree_le`/`modifie_le` (`ModeleHorodate`) tracent l'AGENT qui a saisi
    la fiche, présents sur tous les modèles — pas l'interdit du § 1, qui vise
    une date PROPRE au créneau (jour daté, échéance)."""
    noms_champs = {champ.name for champ in CreneauType._meta.get_fields()}
    champs_provenance = {"cree_le", "modifie_le"}
    types_date = {
        champ.name
        for champ in CreneauType._meta.get_fields()
        if champ.name not in champs_provenance
        and hasattr(champ, "get_internal_type")
        and champ.get_internal_type() in ("DateField", "DateTimeField")
    }
    assert not types_date, f"CreneauType porte un champ de date : {types_date}"
    assert "heure_debut" in noms_champs
    assert "heure_fin" in noms_champs


# --- B10 — suppression de la grille : ses créneaux disparaissent (CASCADE) --


def test_b10_suppression_de_la_grille_supprime_ses_creneaux_cascade(planificateur):
    grille = _grille("Brouillon")
    creneau = ServiceCreneauType.ajouter(planificateur, grille, _donnees())

    ServiceGrilleHoraire.supprimer(planificateur, grille.pk)

    assert not CreneauType.objects.filter(pk=creneau.pk).exists()
