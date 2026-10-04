"""Aides des tests du circuit du programme (US-VAL-03). Données fictives.

Les états se conduisent par le chemin réel du circuit (`ServiceCircuitProgramme`),
jamais en écrivant `etat` à la main : une fixture qui pose l'état directement
masquerait un défaut du service (.claude/rules/tests.md, P-21). Seules les
séances sont créées par l'ORM : elles sont la matière du programme, pas son
circuit.
"""

import datetime

from django.utils import timezone

from planification.models import EtatProgramme, LigneProgramme, Seance
from planification.services.circuit import ServiceCircuitProgramme
from planification.services.contraintes import Candidate
from planification.tests.conftest import instant

MOTIF_REJET = "Créneaux à reprendre."
MOTIF_ANNULATION = "Erreur de créneau."
SIGNATAIRE = "Signataire fictif"


def seance_dans(programme, cours, brigade, debut, duree_min=120):
    fin = debut + datetime.timedelta(minutes=duree_min)
    seance = Seance.objects.create(
        programme=programme,
        element_referentiel=cours.element,
        instructeur=cours.instructeur,
        debut=debut,
        fin=fin,
    )
    LigneProgramme.objects.create(seance=seance, brigade=brigade)
    return seance


def candidature(brigade, cours, debut, duree_min=120):
    fin = debut + datetime.timedelta(minutes=duree_min)
    return Candidate(
        brigade=brigade,
        element_referentiel=cours.element,
        instructeur=cours.instructeur,
        debut=debut,
        fin=fin,
    )


def _soumettre_valider(etat, programme, acteurs):
    ServiceCircuitProgramme.soumettre(acteurs.planificateur, programme)
    if etat == EtatProgramme.REJETE:
        ServiceCircuitProgramme.rejeter(acteurs.pedagogique, programme, MOTIF_REJET)
    if etat in (EtatProgramme.VALIDE, EtatProgramme.AFFICHE):
        ServiceCircuitProgramme.valider(acteurs.pedagogique, programme)


def amener_a(etat, circuit):
    """Conduit `circuit.programme` à `etat` par le chemin réel du circuit, et
    rend l'objet relu. Une séance est créée d'abord : A9 interdit de soumettre
    un programme vide."""
    programme, acteurs = circuit.programme, circuit.acteurs
    seance_dans(
        programme, circuit.cours, circuit.brigade, instant(programme.lundi_de_semaine, 0, 8)
    )
    if etat != EtatProgramme.BROUILLON:
        _soumettre_valider(etat, programme, acteurs)
    if etat == EtatProgramme.AFFICHE:
        ServiceCircuitProgramme.enregistrer_signature(
            acteurs.planificateur, programme, timezone.localdate(), SIGNATAIRE
        )
        ServiceCircuitProgramme.afficher(acteurs.planificateur, programme)
    programme.refresh_from_db()
    return programme
