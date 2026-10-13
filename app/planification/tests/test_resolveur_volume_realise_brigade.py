"""R6, US-SUI-01 (prompt 44, Temps 3, D-108 refermé) — fermeture RÉELLE,
via le résolveur de `noyau` câblé par `planification.apps.
PlanificationConfig.ready()`. Ce test vit ici, jamais côté `organisation`,
qui ne peut pas construire de `Seance` (sens de dépendance interdit, même
motif que `test_resolveur_qualification.py`). Données entièrement fictives.
"""

import datetime

from django.utils import timezone

from noyau.services.parametres import ResolveurVolumeRealiseBrigade
from organisation.services.affectation import ServiceAffectation
from organisation.services.stagiaire import ServiceStagiaire
from organisation.tests.conftest import donnees_stagiaire
from planification.models import ProgrammeHebdomadaire
from planification.selectors_suivi import volume_realise_total_brigade
from planification.services.circuit import ServiceCircuitProgramme
from planification.tests.aide_circuit import seance_dans
from planification.tests.conftest import instant

SIGNATAIRE_ESSAI = "Signataire essai résolveur"


def _brigade_avec_realise(circuit, heures=2):
    lundi_passe = datetime.date.today() - datetime.timedelta(weeks=4)
    lundi_passe -= datetime.timedelta(days=lundi_passe.weekday())
    programme_passe = ProgrammeHebdomadaire.objects.create(lundi_de_semaine=lundi_passe)
    seance_dans(
        programme_passe,
        circuit.cours,
        circuit.brigade,
        instant(lundi_passe, 0, 8),
        duree_min=heures * 60,
    )
    acteurs = circuit.acteurs
    ServiceCircuitProgramme.soumettre(acteurs.planificateur, programme_passe)
    ServiceCircuitProgramme.valider(acteurs.pedagogique, programme_passe)
    ServiceCircuitProgramme.enregistrer_signature(
        acteurs.planificateur, programme_passe, timezone.localdate(), SIGNATAIRE_ESSAI
    )
    ServiceCircuitProgramme.afficher(acteurs.planificateur, programme_passe)
    return circuit.brigade


def test_le_fournisseur_de_planification_est_installe_au_demarrage():
    assert ResolveurVolumeRealiseBrigade._fournisseur is volume_realise_total_brigade


def test_resoudre_rend_le_total_toutes_matieres_confondues(circuit):
    brigade = _brigade_avec_realise(circuit, heures=2)

    assert ResolveurVolumeRealiseBrigade.resoudre(brigade) == 2.0


def test_resoudre_rend_zero_sans_programme_affiche(circuit):
    assert ResolveurVolumeRealiseBrigade.resoudre(circuit.brigade) == 0.0


def test_c6_affectation_signale_le_volume_deja_realise(circuit, session_formation):
    brigade = _brigade_avec_realise(circuit, heures=3)
    stagiaire = ServiceStagiaire.creer(
        circuit.acteurs.pedagogique, session_formation, donnees_stagiaire(matricule="M900")
    )

    affectation = ServiceAffectation.affecter(circuit.acteurs.pedagogique, stagiaire, brigade)

    codes = [a["code"] for a in affectation.avertissements]
    assert "volume_deja_realise" in codes
    message = next(
        a["message"] for a in affectation.avertissements if a["code"] == "volume_deja_realise"
    )
    assert "3.00 h" in message


def test_affectation_sans_realise_n_avertit_pas(circuit, session_formation):
    stagiaire = ServiceStagiaire.creer(
        circuit.acteurs.pedagogique, session_formation, donnees_stagiaire(matricule="M901")
    )

    affectation = ServiceAffectation.affecter(
        circuit.acteurs.pedagogique, stagiaire, circuit.brigade
    )

    codes = [a["code"] for a in affectation.avertissements]
    assert "volume_deja_realise" not in codes
