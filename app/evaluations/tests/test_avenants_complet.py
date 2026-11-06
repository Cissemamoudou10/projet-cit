"""K6, prompt 58 (RECETTE-01 B1) : fiabilité de l'avenant « déplacement »
posé sur W0 par le chargeur `complet`, même quand la semaine est saturée
(aucun créneau naturellement libre pour EXP1 — le cas réel observé en
recette). Données entièrement fictives."""

import datetime
from types import SimpleNamespace

import pytest
from django.core.management import call_command
from django.utils import timezone

from evaluations.jeu_recette.avenants_complet import (
    JEUDI_ISO,
    LUNDI_ISO,
    MARDI_ISO,
    VENDREDI_ISO,
    _choisir_seance_a_liberer,
)
from evaluations.jeu_recette.semaines import semaine
from organisation.models import Brigade
from planification.models import Avenant, NatureAvenant, ProgrammeHebdomadaire


def _ligne(jour_iso, heure=8):
    """Fausse `LigneProgramme` : seul `ligne.seance.debut` est lu par
    `_choisir_seance_a_liberer`, inutile de créer de vraies séances ici."""
    base = datetime.date(2026, 11, 2)  # un lundi
    jour = base + datetime.timedelta(days=jour_iso - 1)
    debut = timezone.make_aware(datetime.datetime.combine(jour, datetime.time(heure, 0)))
    return SimpleNamespace(seance=SimpleNamespace(debut=debut))


def test_choisit_une_seance_du_jour_prefere_hors_jour_de_m6():
    lignes = [_ligne(MARDI_ISO), _ligne(JEUDI_ISO), _ligne(VENDREDI_ISO)]
    a_liberer = _choisir_seance_a_liberer(lignes, jour_actuel_m6_iso=LUNDI_ISO)
    assert timezone.localtime(a_liberer.debut).isoweekday() == JEUDI_ISO


def test_exclut_le_jour_actuel_de_m6_meme_si_c_est_le_jour_prefere():
    """Si M6 est déjà jeudi, libérer une autre séance de jeudi ne déplacerait
    pas réellement M6 — le jour suivant par ordre de préférence (vendredi)
    est retenu à la place."""
    lignes = [_ligne(JEUDI_ISO), _ligne(VENDREDI_ISO)]
    a_liberer = _choisir_seance_a_liberer(lignes, jour_actuel_m6_iso=JEUDI_ISO)
    assert timezone.localtime(a_liberer.debut).isoweekday() == VENDREDI_ISO


def test_accepte_le_jour_de_m6_si_aucun_autre_jour_n_est_disponible():
    lignes = [_ligne(JEUDI_ISO, heure=10)]
    a_liberer = _choisir_seance_a_liberer(lignes, jour_actuel_m6_iso=JEUDI_ISO)
    assert a_liberer is not None


def test_sans_aucune_autre_seance_rend_none():
    assert _choisir_seance_a_liberer([], jour_actuel_m6_iso=JEUDI_ISO) is None


@pytest.mark.django_db
def test_chargement_complet_pose_exactement_deux_avenants_sur_m6_exp1_w0():
    """Preuve de bout en bout (K6) : même semaine W0 saturée (aucun créneau
    naturellement libre pour EXP1, confirmé en recette, RECETTE-01 B1), le
    chargeur pose malgré tout les deux avenants attendus sur UNE SEULE
    séance M6 d'EXP1 — sans échouer, sans se contenter d'un avertissement
    muet, et sans qu'aucune heure hors grille ne subsiste."""
    call_command("charger_jeu_recette", etat="complet")
    exp1 = Brigade.objects.get(designation="EXP1")
    programme_w0 = ProgrammeHebdomadaire.objects.get(
        lundi_de_semaine=semaine(timezone.localdate(), 0)
    )
    avenants = Avenant.objects.filter(
        seance__programme=programme_w0,
        seance__element_referentiel__matiere__code="M6",
        seance__lignes__brigade=exp1,
    ).distinct()
    assert avenants.count() == 2
    natures = sorted(a.nature for a in avenants)
    assert natures == sorted([NatureAvenant.DEPLACEMENT, NatureAvenant.REMPLACEMENT_INSTRUCTEUR])

    deplacement = avenants.get(nature=NatureAvenant.DEPLACEMENT)
    heure_debut = timezone.localtime(deplacement.seance.debut).time()
    assert heure_debut >= datetime.time(8, 0), "M6 ne doit jamais atterrir hors grille (avant 8h)"
