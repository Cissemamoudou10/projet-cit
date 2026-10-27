"""Chargement des instructeurs et qualifications de recette — Prompt 34, § 2."""

from evaluations.jeu_recette.donnees import (
    GRADE_INSTRUCTEUR_PAR_DEFAUT,
    INSTRUCTEURS,
    SPECIALITE_INSTRUCTEUR_PAR_DEFAUT,
)
from ressources.models import Statut
from ressources.services.instructeur import ServiceInstructeur
from ressources.services.qualification import ServiceQualification


def charger_instructeurs(agissant, stdout):
    instructeurs = {}
    for donnees in INSTRUCTEURS:
        instructeur = ServiceInstructeur.creer(
            agissant,
            {
                "nom": donnees.code,
                "prenom": "Recette",
                "matricule": donnees.matricule,
                "grade": GRADE_INSTRUCTEUR_PAR_DEFAUT,
                "specialite": SPECIALITE_INSTRUCTEUR_PAR_DEFAUT,
                "statut": Statut.MILITAIRE_DU_CENTRE,
            },
        )
        if donnees.archive:
            instructeur = ServiceInstructeur.archiver(agissant, instructeur.pk)
        instructeurs[donnees.code] = instructeur
    nb_archives = sum(1 for donnees in INSTRUCTEURS if donnees.archive)
    stdout.write(f"  {len(instructeurs)} instructeurs créés ({nb_archives} archivé).")
    return instructeurs


def charger_qualifications(agissant, instructeurs, matieres, stdout):
    total = 0
    for donnees in INSTRUCTEURS:
        instructeur = instructeurs[donnees.code]
        for code_matiere in donnees.qualifications:
            ServiceQualification.ajouter(agissant, instructeur, matieres[code_matiere])
            total += 1
    stdout.write(f"  {total} qualifications accordées.")
