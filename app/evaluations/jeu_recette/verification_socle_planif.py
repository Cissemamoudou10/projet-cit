"""`--etat socle-planif --verifier` — Prompt 53, Temps 1. Lecture seule, ne
crée ni ne modifie rien. Réutilise le patron de rapport du jeu `socle`
(`verification.py::LigneRapport`/`_ligne`/`_imprimer`)."""

from evaluations.jeu_recette.donnees_socle_planif import (
    BRIGADES_SOCLE_PLANIF,
    CODE_MATIERE_OBJECTIFS,
    CODE_SESSION,
    EFFECTIF_ATTENDU_SESSION,
    INTITULE_SESSION,
    NOMBRE_AFFECTES_EXP1,
    NOMBRE_AFFECTES_EXP2,
    NOMBRE_NON_AFFECTES,
    NOMBRE_RADIES,
    NOMBRE_STAGIAIRES_IMPORTES,
    OBJECTIFS_PEDAGOGIQUES_M3,
)
from evaluations.jeu_recette.verification import _imprimer, _ligne
from organisation.models import AffectationBrigade, Brigade, Session, Stagiaire
from planification.models import ProgrammeHebdomadaire
from referentiel.models import Matiere
from ressources.models import IndisponibiliteInstructeur, IndisponibiliteLieu, PeriodeCalendrier


def verifier_socle_planif(stdout):
    lignes = (
        _verifier_organisation_planif()
        + _verifier_calendrier_planif()
        + _verifier_objectifs_planif()
        + _verifier_aucun_programme()
    )
    _imprimer(stdout, "État du jeu de recette, ajouts de l'état socle-planif (Prompt 53)", lignes)


def _verifier_session_et_brigades(session):
    lignes = _ligne(
        session.effectif_attendu == EFFECTIF_ATTENDU_SESSION,
        f"Session {CODE_SESSION} effectif attendu={EFFECTIF_ATTENDU_SESSION}",
    )
    for donnees in BRIGADES_SOCLE_PLANIF:
        lignes += _ligne(
            Brigade.objects.filter(session=session, designation=donnees.code).exists(),
            f"Brigade {donnees.code} présente",
        )
    return lignes


def _verifier_stagiaires(session):
    lignes = _ligne(
        Stagiaire.objects.filter(session=session).count() == NOMBRE_STAGIAIRES_IMPORTES,
        f"{NOMBRE_STAGIAIRES_IMPORTES} stagiaires importés pour {CODE_SESSION}",
    )
    lignes += _ligne(
        Stagiaire.objects.filter(session=session, radie=True).count() == NOMBRE_RADIES,
        f"{NOMBRE_RADIES} stagiaire radié sur {CODE_SESSION}",
    )
    lignes += _ligne(
        AffectationBrigade.objects.filter(brigade__session=session, brigade__designation="EXP1")
        .count()
        == NOMBRE_AFFECTES_EXP1,
        f"{NOMBRE_AFFECTES_EXP1} stagiaires affectés à EXP1",
    )
    lignes += _ligne(
        AffectationBrigade.objects.filter(brigade__session=session, brigade__designation="EXP2")
        .count()
        == NOMBRE_AFFECTES_EXP2,
        f"{NOMBRE_AFFECTES_EXP2} stagiaires affectés à EXP2",
    )
    nombre_affecte = AffectationBrigade.objects.filter(brigade__session=session).count()
    nombre_non_affectes = (
        Stagiaire.objects.filter(session=session, radie=False).count() - nombre_affecte
    )
    lignes += _ligne(
        nombre_non_affectes == NOMBRE_NON_AFFECTES,
        f"{NOMBRE_NON_AFFECTES} stagiaires non affectés",
    )
    return lignes


def _verifier_organisation_planif():
    lignes = _ligne(
        Session.objects.filter(intitule=INTITULE_SESSION).exists(),
        f"Session {CODE_SESSION} présente",
    )
    session = Session.objects.filter(intitule=INTITULE_SESSION).first()
    if session is None:
        return lignes
    return lignes + _verifier_session_et_brigades(session) + _verifier_stagiaires(session)


def _verifier_calendrier_planif():
    lignes = _ligne(
        PeriodeCalendrier.objects.filter(intitule__icontains="socle-planif").count() == 2,
        "2 périodes de calendrier ajoutées (conférence, congé)",
    )
    lignes += _ligne(
        IndisponibiliteInstructeur.objects.filter(instructeur__nom="I1").exists(),
        "Indisponibilité ajoutée pour I1",
    )
    lignes += _ligne(
        IndisponibiliteLieu.objects.filter(lieu__intitule__startswith="L5").exists(),
        "Indisponibilité ajoutée pour L5",
    )
    return lignes


def _verifier_objectifs_planif():
    matiere_m3 = Matiere.objects.filter(code=CODE_MATIERE_OBJECTIFS).first()
    nombre_attendu = len(OBJECTIFS_PEDAGOGIQUES_M3)
    return _ligne(
        matiere_m3 is not None and matiere_m3.objectifs_pedagogiques.count() == nombre_attendu,
        f"{nombre_attendu} objectifs pédagogiques sur {CODE_MATIERE_OBJECTIFS}",
    )


def _verifier_aucun_programme():
    return _ligne(
        not ProgrammeHebdomadaire.objects.exists(), "Aucun programme hebdomadaire (Temps 1)"
    )
