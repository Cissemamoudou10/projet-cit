"""Remise à zéro de la base de démonstration J2 — Prompt 43, § A3 :
« rejouable, elle remet la base de démonstration à zéro à chaque appel ».

Contrairement aux deux jeux existants (qui ne vident que leur propre
catalogue, jamais exercé en écriture après coup), CETTE base reçoit en
direct tout ce que le fil A1 produit pendant la démonstration — programme,
séances, avenant, indisponibilité, évaluations, sujets, organisation
d'épreuve. L'ordre respecte les `PROTECT` du modèle (`.claude/rules/
modeles.md`) : l'avenant et l'évaluation avant la séance (chacun la
protège), la ligne de programme avant la brigade (RG-32), la session avant
la formation. Comptes et journal jamais touchés (RG-27, même raison que les
deux jeux existants). Les évaluations se vident par
`ResolveurReinitialisationEvaluations` : `planification` ne peut pas
importer `evaluations` (DEPENDANCES_AUTORISEES, sens interdit) — même
patron que `ResolveurOccupationsEpreuves`. Les séances se vident par
`modification.supprimer_seances_regenerables` : seule la génération et les
modules de support de la porte unique ont le droit d'effacer une séance ou
une ligne (test d'architecture H2, `tests/architecture/test_circuit.py`) —
ni ce module ni aucun autre jeu de données n'en est une exception."""

from noyau.services.parametres import ResolveurReinitialisationEvaluations
from organisation.models import AffectationBrigade, Brigade, Session, Stagiaire
from planification.models import Avenant, ProgrammeHebdomadaire, Seance
from planification.services.modification import supprimer_seances_regenerables
from referentiel.models import ElementReferentiel, Formation, Matiere, TypeFormation
from ressources.models import IndisponibiliteInstructeur, Instructeur, Lieu, Qualification


def vider_donnees_demonstration(stdout):
    Avenant.objects.all().delete()
    ResolveurReinitialisationEvaluations.resoudre()  # cascade : Sujet, OrganisationEpreuve, Surveillance
    supprimer_seances_regenerables(Seance.objects.all())  # cascade : LigneProgramme
    ProgrammeHebdomadaire.objects.all().delete()
    IndisponibiliteInstructeur.objects.all().delete()
    Qualification.objects.all().delete()
    AffectationBrigade.objects.all().delete()
    Stagiaire.objects.all().delete()
    Brigade.objects.all().delete()
    Session.objects.all().delete()
    Instructeur.objects.all().delete()
    Lieu.objects.all().delete()
    ElementReferentiel.objects.all().delete()
    Formation.objects.all().delete()
    Matiere.objects.all().delete()
    TypeFormation.objects.all().delete()
    stdout.write("Base de démonstration remise à zéro (comptes et journal conservés — RG-27).")
