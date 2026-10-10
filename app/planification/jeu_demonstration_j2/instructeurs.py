"""Chargement des instructeurs et qualifications de la démonstration J2.

Trois instructeurs, un rôle chacun dans le fil A1 : le titulaire programmé
à l'étape 1, le remplaçant proposé à l'étape 8 (indisponibilité), celui des
examens aux étapes 2 et 9 — jamais le même qualifié pour deux matières, pour
que la liste des remplaçants (US-PLAN-09) n'en propose jamais qu'un seul.
"""

from planification.jeu_demonstration_j2.donnees import GRADE_INSTRUCTEUR, INSTRUCTEURS
from referentiel.models import Matiere
from ressources.models import Statut
from ressources.services.instructeur import ServiceInstructeur
from ressources.services.qualification import ServiceQualification


def charger_instructeurs(agissant, stdout):
    instructeurs = {}
    for donnees in INSTRUCTEURS:
        instructeurs[donnees.nom] = ServiceInstructeur.creer(
            agissant,
            {
                "nom": donnees.nom,
                "prenom": "Démonstration",
                "matricule": donnees.matricule,
                "grade": GRADE_INSTRUCTEUR,
                "specialite": "Transmissions",
                "statut": Statut.MILITAIRE_DU_CENTRE,
            },
        )
    stdout.write(f"  {len(instructeurs)} instructeurs créés.")
    return instructeurs


def charger_qualifications(agissant, instructeurs, stdout):
    total = 0
    for donnees in INSTRUCTEURS:
        instructeur = instructeurs[donnees.nom]
        for code_matiere in donnees.qualifications:
            matiere = Matiere.objects.get(code=code_matiere)
            ServiceQualification.ajouter(agissant, instructeur, matiere)
            total += 1
    stdout.write(f"  {total} qualifications accordées.")
