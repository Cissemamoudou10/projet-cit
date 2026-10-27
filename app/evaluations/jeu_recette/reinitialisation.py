"""Réinitialisation du jeu de recette — Prompt 34, § 4.

NE TOUCHE NI AU JOURNAL NI AUX COMPTES (RG-27, voir `comptes.py`).

LIMITE STRUCTURELLE, à consigner : `organisation.models.Session.formation`
est en `on_delete=PROTECT` (`.claude/rules/modeles.md`, « PROTECT par défaut
sur toute clé étrangère vers une entité de référence »). Si un contrôle du
cahier a déjà ouvert une session sur `F1`/`F2`/`F4` (§ 1 du prompt : c'est
précisément ce que ces contrôles font), supprimer ces formations échoue —
Django lève `ProtectedError`. Ce n'est PAS contourné : cette fonction laisse
l'erreur se produire et la retraduit en message actionnable (§ 2 du prompt,
« dis-le-moi, ne contourne pas »). Les sessions du SPRINT 2 ne sont sinon
jamais supprimées par cette commande — seule leur formation porteuse
pourrait bloquer sa propre suppression, jamais l'inverse. Seules les
sessions de la formation `F5` (`--pagination`, créées PAR cette commande)
sont supprimées ici.
"""

from django.core.management.base import CommandError
from django.db.models import ProtectedError

from evaluations.jeu_recette.donnees import (
    FORMATIONS,
    INSTRUCTEURS,
    LIBELLE_FORMATION_PAGINATION,
    LIEUX,
    MATIERES,
    TYPES_FORMATION,
)
from organisation.models import Session
from referentiel.models import ElementReferentiel, Formation, Matiere, Prerequis, TypeFormation
from ressources.models import Instructeur, Lieu, Qualification

MESSAGE_FORMATIONS_PROTEGEES = (
    "Réinitialisation impossible : au moins une session du sprint 2 référence encore "
    "une formation de ce jeu (F1/F2/F4) — {detail}. Supprimez d'abord ces sessions "
    "(et leurs brigades/stagiaires éventuels) depuis les écrans de l'application, "
    "puis relancez --reinitialiser. Voir docs/suivi/JEU-RECETTE.md."
)

LIBELLES_FORMATIONS = [donnees.libelle for donnees in FORMATIONS] + [LIBELLE_FORMATION_PAGINATION]
LIBELLES_TYPES = list(TYPES_FORMATION.values())
CODES_MATIERES = list(MATIERES.keys())
CODES_INSTRUCTEURS = [donnees.code for donnees in INSTRUCTEURS]
LIBELLES_LIEUX = [donnees.libelle for donnees in LIEUX]


def vider_donnees_recette(stdout):
    _vider_sessions_pagination(stdout)
    Prerequis.objects.filter(element__formation__intitule__in=LIBELLES_FORMATIONS).delete()
    ElementReferentiel.objects.filter(formation__intitule__in=LIBELLES_FORMATIONS).delete()
    Qualification.objects.filter(instructeur__nom__in=CODES_INSTRUCTEURS).delete()
    Instructeur.objects.filter(nom__in=CODES_INSTRUCTEURS).delete()
    Lieu.objects.filter(intitule__in=LIBELLES_LIEUX).delete()
    _supprimer_formations()
    TypeFormation.objects.filter(intitule__in=LIBELLES_TYPES).delete()
    Matiere.objects.filter(code__in=CODES_MATIERES).delete()
    stdout.write("Données de recette vidées (comptes et journal conservés — RG-27).")


def _vider_sessions_pagination(stdout):
    total, _ = Session.objects.filter(formation__intitule=LIBELLE_FORMATION_PAGINATION).delete()
    if total:
        stdout.write(f"  {total} session(s) de pagination supprimée(s).")


def _supprimer_formations():
    try:
        Formation.objects.filter(intitule__in=LIBELLES_FORMATIONS).delete()
    except ProtectedError as erreur:
        formations = sorted({str(objet) for objet in erreur.protected_objects})
        raise CommandError(
            MESSAGE_FORMATIONS_PROTEGEES.format(detail=", ".join(formations))
        ) from erreur
