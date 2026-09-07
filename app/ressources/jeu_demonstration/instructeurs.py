"""Chargement des instructeurs et qualifications — Prompt 15, § 3.8, § 3.9."""

from ressources.jeu_demonstration.donnees import (
    INSTRUCTEUR_SANS_QUALIFICATION,
    INSTRUCTEURS,
    QUALIFICATIONS,
)
from ressources.services.instructeur import ServiceInstructeur
from ressources.services.qualification import ServiceQualification


def charger_instructeurs(agissant, stdout):
    instructeurs = {}
    for donnees in INSTRUCTEURS:
        instructeur = ServiceInstructeur.creer(
            agissant,
            {
                "nom": donnees.nom,
                "prenom": donnees.prenom,
                "matricule": donnees.matricule,
                "grade": donnees.grade,
                "specialite": donnees.specialite,
                "statut": donnees.statut,
            },
        )
        if donnees.archive:
            instructeur = ServiceInstructeur.archiver(agissant, instructeur.pk)
        instructeurs[donnees.cle] = instructeur
    _demontrer_modification(agissant, instructeurs)
    stdout.write(f"  {len(instructeurs)} instructeurs créés (1 archivé).")
    return instructeurs


def _demontrer_modification(agissant, instructeurs):
    """Corrige le grade de l'instructeur volontairement sans qualification —
    exerce `MODIFICATION_ELEMENT_GESTION`, sinon absent du chargement."""
    instructeur = instructeurs[INSTRUCTEUR_SANS_QUALIFICATION]
    ServiceInstructeur.modifier(agissant, instructeur.pk, {"grade": "Adjc"}, instructeur.modifie_le)


def charger_qualifications(agissant, instructeurs, matieres, stdout):
    total = 0
    for cle_instructeur, intitules in QUALIFICATIONS.items():
        instructeur = instructeurs[cle_instructeur]
        for intitule in intitules:
            ServiceQualification.ajouter(agissant, instructeur, matieres[intitule])
            total += 1
    stdout.write(f"  {total} qualifications accordées.")
