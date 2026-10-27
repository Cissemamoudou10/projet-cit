"""État `volume` du jeu de recette — Prompt 51, Temps 3. Données
entièrement fictives. Validation par étapes (référentiel/ressources/
organisation/calendrier d'abord, programmes ensuite — coûteux) avant
l'orchestration complète."""

import datetime
import io
import sys

import pytest
from django.core.management import call_command

from evaluations.jeu_recette.alea import nouveau_generateur
from evaluations.jeu_recette.calendrier_volume import charger_calendrier_volume
from evaluations.jeu_recette.comptes_volume import charger_comptes_volume
from evaluations.jeu_recette.organisation_volume import (
    AgissantsOrganisationVolume,
    charger_brigades_volume,
    charger_sessions_volume,
    charger_stagiaires_volume,
)
from evaluations.jeu_recette.referentiel_volume import (
    charger_composition_volume,
    charger_formations_volume,
    charger_matieres_volume,
    charger_types_formation_volume,
)
from evaluations.jeu_recette.ressources_volume import (
    charger_indisponibilites_volume,
    charger_instructeurs_volume,
    charger_lieux_volume,
    charger_qualifications_volume,
)
from organisation.models import Brigade, Session, Stagiaire
from referentiel.models import Formation, Matiere
from ressources.models import CategorieLieu, Instructeur, Lieu

pytestmark = pytest.mark.django_db


def _construire_organisation_volume():
    call_command("initialiser_habilitations")
    call_command("initialiser_natures_evenement")
    comptes = charger_comptes_volume(io.StringIO())
    ped, plan, examens = comptes["v_ped"], comptes["v_plan"], comptes["v_exa"]
    agissants = AgissantsOrganisationVolume(ped, plan)
    call_command("initialiser_grilles_horaires")
    call_command("initialiser_gabarits_documents")

    generateur = nouveau_generateur(2026)
    date_reference = datetime.date(2026, 10, 27)
    stdout = io.StringIO()

    types = charger_types_formation_volume(ped, stdout)
    matieres = charger_matieres_volume(ped, generateur, stdout)
    formations = charger_formations_volume(ped, generateur, types, stdout)
    elements = charger_composition_volume(ped, generateur, formations, matieres, stdout)

    instructeurs = charger_instructeurs_volume(ped, generateur, stdout)
    charger_qualifications_volume(ped, generateur, instructeurs, matieres, stdout)

    lieux = charger_lieux_volume(plan, generateur, stdout)
    charger_indisponibilites_volume(plan, generateur, instructeurs, date_reference, stdout)

    groupe_sessions_actives, groupe_sessions_terminees = charger_sessions_volume(
        ped, generateur, formations, date_reference, stdout
    )
    groupe_brigades = charger_brigades_volume(agissants, groupe_sessions_actives, groupe_sessions_terminees, lieux, stdout)
    charger_stagiaires_volume(ped, generateur, groupe_sessions_actives.sessions, groupe_brigades, stdout)
    charger_calendrier_volume(plan, generateur, date_reference, groupe_brigades.actives, stdout)
    return (
        ped, plan, examens, generateur, date_reference, groupe_brigades,
        groupe_sessions_actives.sessions, groupe_sessions_terminees.sessions, elements, stdout,
    )


def test_referentiel_ressources_organisation_calendrier_volume():
    (
        ped, plan, examens, generateur, date_reference, groupe_brigades,
        sessions_actives, sessions_terminees, elements, stdout,
    ) = _construire_organisation_volume()

    assert Matiere.objects.count() == 70
    assert Formation.objects.count() == 10
    assert Formation.objects.filter(archive=True).count() == 1
    assert Instructeur.objects.count() == 80
    assert Lieu.objects.filter(categorie=CategorieLieu.SALLE_ATTITREE).count() == 36
    assert Session.objects.count() == 18
    assert len(groupe_brigades.actives) == 32
    assert Brigade.objects.count() >= 32 + 6
    assert Stagiaire.objects.filter(radie=True).count() == 20
    assert Stagiaire.objects.filter(affectations__isnull=True).distinct().count() >= 15


def test_evaluations_volume():
    """Formatives et certificatives seulement — aucune ne produit de PDF.
    Le procès-verbal (WeasyPrint, P-44) est isolé dans
    `test_proces_verbaux_volume`, marqué `pdf`."""
    from evaluations.jeu_recette.evaluations_volume import (
        ContexteEvaluationsVolume,
        charger_certificatives_a_venir_volume,
        charger_formatives_actives_volume,
        charger_formatives_terminees_volume,
    )
    from evaluations.models import Evaluation

    (
        ped, plan, examens, generateur, date_reference, groupe_brigades,
        sessions_actives, sessions_terminees, elements, stdout,
    ) = _construire_organisation_volume()
    contexte = ContexteEvaluationsVolume(examens, generateur, date_reference, stdout)

    charger_formatives_actives_volume(contexte, groupe_brigades.actives, elements)
    charger_formatives_terminees_volume(contexte, groupe_brigades.terminees, elements)
    charger_certificatives_a_venir_volume(contexte, sessions_actives)

    assert Evaluation.objects.filter(brigade__in=groupe_brigades.actives.values()).count() == len(
        groupe_brigades.actives
    )
    assert Evaluation.objects.filter(session__in=sessions_actives.values()).count() == 5


@pytest.mark.pdf
@pytest.mark.skipif(sys.platform.startswith("win"), reason="WeasyPrint exige ses bibliothèques natives (P-44).")
def test_proces_verbaux_volume():
    from evaluations.jeu_recette.evaluations_volume import (
        ContexteEvaluationsVolume,
        charger_formatives_terminees_volume,
        charger_proces_verbaux_volume,
    )
    from evaluations.models import ProcesVerbal

    (
        ped, plan, examens, generateur, date_reference, groupe_brigades,
        sessions_actives, sessions_terminees, elements, stdout,
    ) = _construire_organisation_volume()
    contexte = ContexteEvaluationsVolume(examens, generateur, date_reference, stdout)

    charger_formatives_terminees_volume(contexte, groupe_brigades.terminees, elements)
    charger_proces_verbaux_volume(contexte, sessions_terminees)

    assert ProcesVerbal.objects.count() == 2


def test_programmes_volume_sous_ensemble_reduit():
    """Mécanique de `programme_volume.py` validée sur 3 brigades plutôt que
    32 — la logique par semaine ne change pas avec le nombre de brigades,
    seule la durée en dépend (mesurée séparément, à l'échelle réelle)."""
    from evaluations.jeu_recette.programme_volume import (
        AgissantsProgrammeVolume,
        OptionsProgrammesVolume,
        charger_programmes_volume,
    )

    (
        ped, plan, examens, generateur, date_reference, groupe_brigades,
        sessions_actives, sessions_terminees, elements, stdout,
    ) = _construire_organisation_volume()
    agissants = AgissantsProgrammeVolume(plan, ped)
    sous_ensemble = dict(list(groupe_brigades.actives.items())[:3])
    options = OptionsProgrammesVolume(sous_ensemble, date_reference)
    mesures = charger_programmes_volume(agissants, generateur, options, stdout)
    assert len(mesures) == 12
    etats = [m.etat_final for m in mesures]
    # À 3 brigades (réduit pour le test), le référentiel peut s'épuiser avant
    # la fin des 9 semaines affichées — une semaine alors restée BROUILLON
    # (aucune séance, A9) est une mesure légitime (§ 3.2), jamais une erreur :
    # seul l'état de W+3 (toujours brouillon par construction) est fixe.
    assert all(etat in ("affiche", "valide", "soumis", "brouillon") for etat in etats)
    assert etats[-1] == "brouillon"


@pytest.mark.pdf
@pytest.mark.skipif(sys.platform.startswith("win"), reason="WeasyPrint exige ses bibliothèques natives (P-44).")
def test_charger_etat_volume_orchestration_complete():
    """`charger_etat_volume` dans son ENSEMBLE (pas les fonctions de bas
    niveau comme les autres tests de ce fichier) — seul chemin qui aurait
    révélé le défaut d'ordre réel trouvé par le chargement en conteneur :
    `initialiser_grilles_horaires` appelé avant que les comptes n'existent
    (RG-63). `semaines_passees=1` : assez pour exercer l'ordre complet,
    sans la durée d'un chargement pleine échelle."""
    from evaluations.jeu_recette.orchestration_volume import charger_etat_volume

    generateur = nouveau_generateur(2026)
    date_reference = datetime.date(2026, 10, 27)
    stdout = io.StringIO()

    compteurs, mesures = charger_etat_volume(generateur, date_reference, stdout, semaines_passees=1)

    assert compteurs["Comptes"] == 7
    assert compteurs["Brigades actives"] == 32
    assert len(mesures) == 1 + 4  # semaines_passees + (W0, W+1, W+2, W+3)


def test_commande_charger_jeu_volume_verifier_sur_base_vide():
    """Chemin `--verifier` de la vraie commande, lecture seule — ne crée
    rien, même sur une base vide (0/N conformes attendu, jamais une
    exception)."""
    sortie = io.StringIO()
    call_command("charger_jeu_volume", verifier=True, stdout=sortie)
    assert "conformes" in sortie.getvalue()
    assert Session.objects.count() == 0
