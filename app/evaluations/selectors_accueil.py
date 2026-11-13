"""Tableau de bord de la page d'accueil — US-IHM-01, prompt 64.

Vit dans `evaluations`, en tête de la chaîne de dépendance
(`tests/architecture/test_couches.py`) : c'est la seule application qui
peut lire `referentiel`, `organisation`, `ressources`, `planification` ET
`evaluations` elle-même. Installée comme fournisseur de
`noyau.services.parametres.ResolveurTableauBordAccueil` au démarrage de
l'application (`EvaluationsConfig.ready`), sur le même principe que les
autres résolveurs (A9/A2, prompts 35-38).

Chaque chiffre est gardé par sa PROPRE permission de lecture (`a_permission`,
silencieuse) : un profil qui n'a pas `instructeurs_qualifications_lecture`
(la cellule examens, par exemple) ne voit ni le nombre d'instructeurs ni les
matières sans instructeur qualifié, même si d'autres chiffres lui restent
visibles — jamais un bloc tout-ou-rien. Nombre de requêtes borné, indépendant
du volume de données (un `.count()`/`.exists()` par chiffre, jamais une
boucle) ; `compte_alertes`/`evaluations_non_pretes` sont déjà bornées par
leurs propres règles (voir leurs modules).
"""

import dataclasses
import datetime

from django.utils import timezone

from evaluations.selectors import evaluations_a_venir_non_pretes
from noyau.habilitations import a_permission
from organisation.models import EtatSession, Session, Stagiaire
from planification.models import EtatProgramme, ProgrammeHebdomadaire
from planification.selectors_alerte_ecart import compte_alertes
from planification.selectors_circuit import compte_en_attente_validation_ou_signature
from referentiel.models import Formation, Matiere
from ressources.models import Instructeur, Lieu


@dataclasses.dataclass(frozen=True)
class EtatProgrammeSemaine:
    lundi: datetime.date
    etat_libelle: str | None


@dataclasses.dataclass(frozen=True)
class TableauBordAccueil:
    nombre_formations: int | None
    nombre_matieres: int | None
    nombre_instructeurs: int | None
    nombre_lieux: int | None
    nombre_sessions_en_cours: int | None
    nombre_sessions_cloturees: int | None
    nombre_stagiaires_actifs: int | None
    nombre_matieres_sans_instructeur: int | None
    nombre_alertes_ecart: int | None
    nombre_programmes_en_attente: int | None
    nombre_evaluations_non_pretes: int | None
    semaine_courante: EtatProgrammeSemaine | None
    semaine_suivante: EtatProgrammeSemaine | None


def _chiffres_referentiel(utilisateur):
    if not a_permission(utilisateur, "noyau.referentiel_lecture"):
        return None, None
    return (
        Formation.objects.filter(archive=False).count(),
        Matiere.objects.filter(archive=False).count(),
    )


def _chiffres_ressources(utilisateur):
    instructeurs = lieux = matieres_sans_instructeur = None
    if a_permission(utilisateur, "noyau.instructeurs_qualifications_lecture"):
        instructeurs = Instructeur.objects.filter(archive=False).count()
        matieres_sans_instructeur = (
            Matiere.objects.filter(archive=False).exclude(qualifications__isnull=False).count()
        )
    if a_permission(utilisateur, "noyau.lieux_calendrier_lecture"):
        lieux = Lieu.objects.filter(archive=False).count()
    return instructeurs, lieux, matieres_sans_instructeur


def _chiffres_organisation(utilisateur):
    if not a_permission(utilisateur, "noyau.organisation_lecture"):
        return None, None, None
    return (
        Session.objects.filter(etat=EtatSession.OUVERTE).count(),
        Session.objects.filter(etat=EtatSession.CLOTUREE).count(),
        Stagiaire.objects.filter(radie=False).count(),
    )


def _lundi_de_la_semaine(date):
    return date - datetime.timedelta(days=date.weekday())


def _etat_des_deux_semaines(utilisateur):
    if not a_permission(utilisateur, "noyau.programme_lecture"):
        return None, None
    lundi_courant = _lundi_de_la_semaine(timezone.localdate())
    lundi_suivant = lundi_courant + datetime.timedelta(days=7)
    programmes = {
        programme.lundi_de_semaine: programme
        for programme in ProgrammeHebdomadaire.objects.filter(
            lundi_de_semaine__in=(lundi_courant, lundi_suivant)
        )
    }
    return (
        _etat_de_la_semaine(lundi_courant, programmes),
        _etat_de_la_semaine(lundi_suivant, programmes),
    )


def _etat_de_la_semaine(lundi, programmes):
    programme = programmes.get(lundi)
    libelle = EtatProgramme(programme.etat).label if programme else None
    return EtatProgrammeSemaine(lundi=lundi, etat_libelle=libelle)


def _points_attention(utilisateur, matieres_sans_instructeur):
    alertes = programmes_en_attente = evaluations_non_pretes = None
    if a_permission(utilisateur, "noyau.suivi_lecture"):
        alertes = compte_alertes()
    if a_permission(utilisateur, "noyau.programme_validation_lecture"):
        programmes_en_attente = compte_en_attente_validation_ou_signature()
    if a_permission(utilisateur, "noyau.evaluations_lecture"):
        evaluations_non_pretes = evaluations_a_venir_non_pretes()
    return matieres_sans_instructeur, alertes, programmes_en_attente, evaluations_non_pretes


def tableau_de_bord_accueil(utilisateur) -> TableauBordAccueil:
    formations, matieres = _chiffres_referentiel(utilisateur)
    instructeurs, lieux, matieres_sans_instructeur = _chiffres_ressources(utilisateur)
    en_cours, cloturees, stagiaires_actifs = _chiffres_organisation(utilisateur)
    semaine_courante, semaine_suivante = _etat_des_deux_semaines(utilisateur)
    matieres_sans_instructeur, alertes, programmes_en_attente, evaluations_non_pretes = (
        _points_attention(utilisateur, matieres_sans_instructeur)
    )
    return TableauBordAccueil(
        nombre_formations=formations,
        nombre_matieres=matieres,
        nombre_instructeurs=instructeurs,
        nombre_lieux=lieux,
        nombre_sessions_en_cours=en_cours,
        nombre_sessions_cloturees=cloturees,
        nombre_stagiaires_actifs=stagiaires_actifs,
        nombre_matieres_sans_instructeur=matieres_sans_instructeur,
        nombre_alertes_ecart=alertes,
        nombre_programmes_en_attente=programmes_en_attente,
        nombre_evaluations_non_pretes=evaluations_non_pretes,
        semaine_courante=semaine_courante,
        semaine_suivante=semaine_suivante,
    )
