"""`--verifier` — Prompt 34, § 5. Ne crée ni ne modifie rien : lecture seule,
rend un rapport. Lancé par le recetteur avant chaque journée de recette.
"""

from dataclasses import dataclass

from django.contrib.auth import get_user_model

from administration.models import Profil
from evaluations.jeu_recette.donnees import (
    CODE_LIEU_IMPOSSIBLE,
    COMPTES,
    FORMATIONS,
    INSTRUCTEURS,
    LIBELLE_FORMATION_PAGINATION,
    LIEUX,
    MATIERES,
    MOTIF_LIEU_IMPOSSIBLE,
    PREREQUIS,
    TYPES_FORMATION,
)
from evaluations.jeu_recette.fichiers_import.constructeur import (
    DOSSIER as DOSSIER_FICHIERS_IMPORT,
)
from evaluations.jeu_recette.fichiers_import.constructeur import NOMS_FICHIERS
from organisation.models import Brigade, Session, Stagiaire
from planification.models import ProgrammeHebdomadaire
from referentiel.models import Formation, Matiere, Prerequis, TypeFormation
from ressources.management.commands.initialiser_grilles_horaires import (
    GRILLE_ACTIVEE_PAR_DEFAUT,
    GRILLES_INITIALES,
    JOURS_OUVRES,
)
from ressources.models import CreneauType, GrilleHoraire, Instructeur, Lieu, PeriodeCalendrier


@dataclass(frozen=True)
class LigneRapport:
    ok: bool
    libelle: str


def verifier(stdout, etat="socle"):
    lignes = (
        _verifier_objets_section2()
        + _verifier_grilles()
        + _verifier_comptes()
        + _verifier_fichiers_import()
    )
    _imprimer(stdout, "État du jeu de recette, socle (§ 2, § 4.2 du cahier)", lignes)
    if etat == "complet":
        from evaluations.jeu_recette.verification_complet import verifier_complet

        verifier_complet(stdout)
        return
    _imprimer_objets_sprint2(stdout)


def _ligne(ok, libelle):
    return [LigneRapport(ok, libelle)]


def _verifier_objets_section2():
    return (
        _verifier_types_formation()
        + _verifier_formations()
        + _verifier_matieres()
        + _verifier_instructeurs()
        + _verifier_lieux()
        + _verifier_prerequis()
    )


def _verifier_types_formation():
    lignes = []
    for code, libelle in TYPES_FORMATION.items():
        lignes += _ligne(
            TypeFormation.objects.filter(intitule=libelle).exists(), f"Type {code} présent"
        )
    return lignes


def _verifier_formations():
    lignes = []
    for donnees in FORMATIONS:
        formation = Formation.objects.filter(intitule=donnees.libelle).first()
        lignes += _ligne(formation is not None, f"Formation {donnees.code} présente")
        if formation is None:
            continue
        lignes += _ligne(
            formation.archive == donnees.archive,
            f"Formation {donnees.code} archivée={donnees.archive}",
        )
        a_des_elements = formation.elements_referentiel.exists()
        attendu = bool(donnees.composition)
        lignes += _ligne(
            a_des_elements == attendu,
            f"Formation {donnees.code} référentiel {'composé' if attendu else 'vide'}",
        )
    return lignes


def _verifier_matieres():
    return [
        LigneRapport(Matiere.objects.filter(code=code).exists(), f"Matière {code} présente")
        for code in MATIERES
    ]


def _verifier_instructeurs():
    lignes = []
    for donnees in INSTRUCTEURS:
        instructeur = Instructeur.objects.filter(nom=donnees.code).first()
        lignes += _ligne(instructeur is not None, f"Instructeur {donnees.code} présent")
        if instructeur is not None:
            lignes += _ligne(
                instructeur.archive == donnees.archive,
                f"Instructeur {donnees.code} archivé={donnees.archive}",
            )
    return lignes


def _verifier_lieux():
    lignes = []
    for donnees in LIEUX:
        lieu = Lieu.objects.filter(intitule=donnees.libelle).first()
        lignes += _ligne(lieu is not None, f"Lieu {donnees.code} présent")
        if lieu is None:
            continue
        lignes += _ligne(
            lieu.archive == donnees.archive, f"Lieu {donnees.code} archivé={donnees.archive}"
        )
        if donnees.mode_partage is not None:
            lignes += _ligne(
                lieu.mode_partage == donnees.mode_partage,
                f"Lieu {donnees.code} mode de partage={donnees.mode_partage}",
            )
    lignes += _ligne(
        not Lieu.objects.filter(intitule__startswith=f"{CODE_LIEU_IMPOSSIBLE} —").exists(),
        f"Lieu {CODE_LIEU_IMPOSSIBLE} absent — impossible à produire ({MOTIF_LIEU_IMPOSSIBLE})",
    )
    return lignes


def _verifier_prerequis():
    lignes = []
    libelles_formations = {donnees.code: donnees.libelle for donnees in FORMATIONS}
    for code_formation, code_element, code_prerequis in PREREQUIS:
        existe = Prerequis.objects.filter(
            element__formation__intitule=libelles_formations[code_formation],
            element__matiere__code=code_element,
            element_prerequis__matiere__code=code_prerequis,
        ).exists()
        lignes += _ligne(
            existe, f"{code_prerequis} déclaré prérequis de {code_element} ({code_formation})"
        )
    return lignes


def _verifier_grilles():
    lignes = []
    for intitule, creneaux in GRILLES_INITIALES.items():
        grille = GrilleHoraire.objects.filter(intitule__iexact=intitule).first()
        lignes += _ligne(grille is not None, f"Grille « {intitule} » présente")
        if grille is None:
            continue
        active_attendue = intitule == GRILLE_ACTIVEE_PAR_DEFAUT
        lignes += _ligne(
            grille.active == active_attendue, f"Grille « {intitule} » active={active_attendue}"
        )
        nb_attendu = len(creneaux) * len(JOURS_OUVRES)
        nb_reel = CreneauType.objects.filter(grille=grille).count()
        lignes += _ligne(
            nb_reel == nb_attendu,
            f"Grille « {intitule} » : {nb_reel}/{nb_attendu} créneaux (R2-P12-02/03)",
        )
    return lignes


def _verifier_comptes():
    lignes = []
    for donnees in COMPTES:
        compte = get_user_model().objects.filter(username=donnees.identifiant).first()
        lignes += _ligne(compte is not None, f"Compte {donnees.identifiant} présent")
        if compte is None:
            continue
        libelle_profil = Profil(donnees.profil).label
        a_le_groupe = compte.groups.filter(name=libelle_profil).exists()
        lignes += _ligne(
            a_le_groupe, f"Compte {donnees.identifiant} porte le groupe « {libelle_profil} »"
        )
    return lignes


def _verifier_fichiers_import():
    lignes = []
    for nom in NOMS_FICHIERS:
        present = (DOSSIER_FICHIERS_IMPORT / nom).exists()
        lignes += _ligne(present, f"Fichier d'import {nom} présent")
    lignes += _ligne(
        (DOSSIER_FICHIERS_IMPORT / "00-LISEZ-MOI.md").exists(), "00-LISEZ-MOI.md présent"
    )
    return lignes


def _imprimer(stdout, titre, lignes):
    stdout.write(titre)
    for ligne in lignes:
        marque = "OK" if ligne.ok else "MANQUANT"
        stdout.write(f"  [{marque:8s}] {ligne.libelle}")
    nb_echecs = sum(1 for ligne in lignes if not ligne.ok)
    stdout.write(f"  {len(lignes) - nb_echecs}/{len(lignes)} contrôles conformes.")
    stdout.write("")


def _imprimer_objets_sprint2(stdout):
    """Compte les objets du SPRINT 2 déjà en base — JAMAIS supprimés ici
    (§ 5). Les sessions de la formation de pagination (`--pagination`) sont
    EXCLUES : elles sont créées par cette commande, pas par un contrôle du
    recetteur — les compter ici tromperait sur l'état réel de la recette."""
    sessions = Session.objects.exclude(formation__intitule=LIBELLE_FORMATION_PAGINATION).count()
    stdout.write("Objets du sprint 2 déjà en base (non supprimés) :")
    stdout.write(f"  Sessions (hors pagination) : {sessions}")
    stdout.write(f"  Brigades : {Brigade.objects.count()}")
    stdout.write(f"  Stagiaires : {Stagiaire.objects.count()}")
    stdout.write(f"  Périodes de calendrier : {PeriodeCalendrier.objects.count()}")
    stdout.write(f"  Programmes hebdomadaires : {ProgrammeHebdomadaire.objects.count()}")
    if Session.objects.filter(formation__intitule=LIBELLE_FORMATION_PAGINATION).exists():
        stdout.write(
            "  (+ des sessions de pagination existent — --pagination déjà exécuté, "
            "exclues du compte ci-dessus)"
        )
