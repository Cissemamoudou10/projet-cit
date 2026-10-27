"""`--etat complet --verifier` — Prompt 51, § 2.8. Lecture seule, ne crée
ni ne modifie rien. Réutilise le patron de rapport du jeu `socle`
(`verification.py::LigneRapport`/`_ligne`/`_imprimer`) : même format de
sortie, un seul `N/N conformes` à la fin, comme l'exige la règle commune
n° 8 du prompt."""

from django.utils import timezone

from evaluations.jeu_recette.donnees_complet import (
    BRIGADES_COMPLET,
    INSTRUCTEURS_COMPLET,
    LIEUX_COMPLET,
    MATIERES_COMPLET,
    SESSIONS_COMPLET,
)
from evaluations.jeu_recette.semaines import semaine
from evaluations.jeu_recette.verification import _imprimer, _ligne
from evaluations.models import Evaluation, Note, OrganisationEpreuve, Sujet, TypeEvaluation
from organisation.models import Brigade, Session, Stagiaire
from planification.models import EtatProgramme, NonExecution, ProgrammeHebdomadaire
from referentiel.models import Formation, Matiere
from ressources.models import Instructeur, Lieu, Qualification


def verifier_complet(stdout):
    lignes = (
        _verifier_referentiel_complet()
        + _verifier_ressources_complet()
        + _verifier_organisation_complet()
        + _verifier_programmes_complet()
        + _verifier_evaluations_complet()
        + _verifier_suivi_complet()
    )
    _imprimer(stdout, "État du jeu de recette, ajouts de l'état complet (§ 2)", lignes)


def _verifier_referentiel_complet():
    lignes = []
    for code in MATIERES_COMPLET:
        lignes += _ligne(Matiere.objects.filter(code=code).exists(), f"Matière {code} présente")
    formation = Formation.objects.filter(intitule__startswith="F6").first()
    lignes += _ligne(formation is not None, "Formation F6 présente")
    if formation is not None:
        elements = formation.elements_referentiel.all()
        lignes += _ligne(elements.count() == 7, "Référentiel F6 complet (7 éléments)")
        volume_total = sum(e.volume_horaire_prescrit for e in elements)
        lignes += _ligne(volume_total == 200, f"Référentiel F6 : {volume_total}/200 h")
        element_m8 = elements.filter(matiere__code="M8").first()
        lignes += _ligne(
            element_m8 is not None
            and element_m8.prerequis_directs.filter(element_prerequis__matiere__code="M6").exists(),
            "M6 déclaré prérequis de M8",
        )
        element_m6 = elements.filter(matiere__code="M6").first()
        lignes += _ligne(
            element_m6 is not None and element_m6.matiere.objectifs_pedagogiques.count() == 2,
            "Deux objectifs pédagogiques sur M6",
        )
    return lignes


def _verifier_ressources_complet():
    lignes = []
    for donnees in INSTRUCTEURS_COMPLET:
        lignes += _ligne(
            Instructeur.objects.filter(nom=donnees.code).exists(),
            f"Instructeur {donnees.code} présent",
        )
    lignes += _ligne(
        Qualification.objects.filter(instructeur__nom="I3", matiere__code="M1").exists(),
        "Qualification M1 ajoutée à I3",
    )
    for donnees in LIEUX_COMPLET:
        lignes += _ligne(
            Lieu.objects.filter(intitule=donnees.libelle).exists(), f"Lieu {donnees.code} présent"
        )
    return lignes


def _verifier_organisation_complet():
    lignes = []
    for donnees in SESSIONS_COMPLET:
        lignes += _ligne(
            Session.objects.filter(intitule=donnees.intitule).exists(),
            f"Session {donnees.code} présente",
        )
    for donnees in BRIGADES_COMPLET:
        lignes += _ligne(
            Brigade.objects.filter(designation=donnees.code).exists(),
            f"Brigade {donnees.code} présente",
        )
    lignes += _ligne(
        Stagiaire.objects.filter(nom="S1").count() == 39,
        "39 stagiaires créés pour S1 (35 affectés + 3 non affectés + 1 radié)",
    )
    lignes += _ligne(
        Stagiaire.objects.filter(nom="S1", radie=True).count() == 1, "1 stagiaire radié sur S1"
    )
    return lignes


def _verifier_programmes_complet():
    """Dates recalculées depuis « aujourd'hui » (`timezone.localdate()`) :
    valide seulement si `--verifier` est lancé le même jour que le
    chargement (hypothèse du § 2.8 — les deux font partie de la même
    commande de recette, voir `JEUX-DE-DONNEES-PHASE-6.md`)."""
    aujourd_hui = timezone.localdate()
    lignes = []
    etats_attendus = {
        -2: EtatProgramme.AFFICHE,
        -1: EtatProgramme.AFFICHE,
        0: EtatProgramme.AFFICHE,
        1: EtatProgramme.BROUILLON,
    }
    for decalage, etat_attendu in etats_attendus.items():
        libelle = f"W{decalage:+d}".replace("+0", "0")
        programme = ProgrammeHebdomadaire.objects.filter(
            lundi_de_semaine=semaine(aujourd_hui, decalage)
        ).first()
        lignes += _ligne(programme is not None, f"Programme {libelle} présent")
        if programme is not None:
            lignes += _ligne(
                programme.etat == etat_attendu,
                f"Programme {libelle} état={etat_attendu} (réel : {programme.etat})",
            )
    return lignes


def _verifier_evaluations_existent():
    lignes = []
    for code_matiere, type_attendu in (
        ("M1", TypeEvaluation.FORMATIVE),
        ("M3", TypeEvaluation.CERTIFICATIVE),
        ("M4", TypeEvaluation.FORMATIVE),
        ("M6", TypeEvaluation.CERTIFICATIVE),
    ):
        existe = Evaluation.objects.filter(
            element_referentiel__matiere__code=code_matiere, type=type_attendu
        ).exists()
        lignes += _ligne(existe, f"Évaluation sur {code_matiere} ({type_attendu}) présente")
    lignes += _ligne(
        Evaluation.objects.filter(
            element_referentiel__matiere__code="M2", brigade__designation="EXP2"
        ).exists(),
        "E2 (M2, EXP2) présente",
    )
    return lignes


def _verifier_organisation_e3():
    lignes = []
    lignes += _ligne(
        Sujet.objects.filter(reference="SUJ-E3-A", retenu=True).exists(), "Sujet A de E3 retenu"
    )
    lignes += _ligne(
        Sujet.objects.filter(reference="SUJ-E3-B", retenu=False).exists(),
        "Sujet B de E3 présent, non retenu",
    )
    lignes += _ligne(
        OrganisationEpreuve.objects.filter(
            evaluation__element_referentiel__matiere__code="M6", brigade__designation="EXP1"
        ).exists(),
        "E3 : organisation d'EXP1 présente",
    )
    lignes += _ligne(
        not OrganisationEpreuve.objects.filter(
            evaluation__element_referentiel__matiere__code="M6", brigade__designation="EXP2"
        ).exists(),
        "E3 : EXP2 non organisée (exprès)",
    )
    return lignes


def _verifier_notes():
    lignes = []
    lignes += _ligne(
        Note.objects.filter(
            evaluation__element_referentiel__matiere__code="M1", absent=False
        ).count()
        == 19,
        "E1 : 19 notes saisies",
    )
    lignes += _ligne(
        Note.objects.filter(
            evaluation__element_referentiel__matiere__code="M1", absent=True
        ).count()
        == 1,
        "E1 : 1 absence",
    )
    lignes += _ligne(
        Note.objects.filter(
            evaluation__element_referentiel__matiere__code="M4", absent=False
        ).count()
        == 10,
        "E5 : 10 notes saisies (sur 12)",
    )
    return lignes


def _verifier_evaluations_complet():
    return _verifier_evaluations_existent() + _verifier_organisation_e3() + _verifier_notes()


def _verifier_suivi_complet():
    lignes = []
    lignes += _ligne(
        NonExecution.objects.count() >= 2, "Au moins 2 non-exécutions déclarées (§ 2.6)"
    )
    return lignes
