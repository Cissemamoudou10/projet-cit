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

Les deux proportions (matières sans instructeur, brigades sans salle
attitrée) sont exprimées en douzièmes, comme la charte § 3.34 (« barre
prescrit/programmé/réalisé ») : le gabarit choisit une fraction Tailwind
parmi douze, jamais une largeur en ligne.
"""

import dataclasses
import datetime

from django.utils import timezone

from evaluations.selectors import evaluations_a_venir_non_pretes
from noyau.habilitations import a_permission
from organisation.models import Brigade, EtatSession, Session, Stagiaire
from planification.models import EtatProgramme, LigneProgramme, ProgrammeHebdomadaire, Seance
from planification.selectors_alerte_ecart import compte_alertes
from planification.selectors_circuit import compte_en_attente_validation_ou_signature
from referentiel.models import Formation, Matiere
from ressources.models import Instructeur, Lieu


def douzieme(partie, total):
    """Charte § 3.34 : même fonction, pour les mêmes raisons (aucune
    largeur en ligne, le gabarit choisit parmi les fractions Tailwind)."""
    if not total:
        return 0
    return min(12, round(12 * partie / total))


@dataclasses.dataclass(frozen=True)
class EtatProgrammeSemaine:
    lundi: datetime.date
    etat: str | None
    etat_libelle: str | None
    nombre_seances: int
    nombre_brigades: int


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
    douzieme_matieres_sans_instructeur: int | None
    nombre_brigades_sans_salle: int | None
    douzieme_brigades_sans_salle: int | None
    nombre_instructeurs_indisponibles_semaine: int | None
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


def _matieres_sans_instructeur(nombre_matieres):
    nombre = Matiere.objects.filter(archive=False).exclude(qualifications__isnull=False).count()
    return nombre, douzieme(nombre, nombre_matieres)


def _brigades_sans_salle():
    """Brigades des sessions OUVERTES seulement — une session clôturée n'a
    plus besoin de salle. Une seule requête de comptage pour le total, une
    pour celles sans `salle_attitree` (`OneToOneField`, RG-13/RG-14)."""
    brigades_actives = Brigade.objects.filter(session__etat=EtatSession.OUVERTE)
    total = brigades_actives.count()
    sans_salle = brigades_actives.filter(salle_attitree__isnull=True).count()
    return total, sans_salle, douzieme(sans_salle, total)


def _instructeurs_indisponibles_semaine(lundi_courant):
    fin_semaine = lundi_courant + datetime.timedelta(days=7)
    debut_semaine = timezone.make_aware(datetime.datetime.combine(lundi_courant, datetime.time.min))
    fin_semaine = timezone.make_aware(datetime.datetime.combine(fin_semaine, datetime.time.min))
    return (
        Instructeur.objects.filter(
            archive=False,
            indisponibilites__debut__lt=fin_semaine,
            indisponibilites__fin__gt=debut_semaine,
        )
        .distinct()
        .count()
    )


def _chiffres_ressources(utilisateur, nombre_matieres, lundi_courant):
    instructeurs = matieres_sans_instructeur = douzieme_mat = None
    indisponibles = None
    lieux = brigades_total = brigades_sans_salle = douzieme_brig = None
    if a_permission(utilisateur, "noyau.instructeurs_qualifications_lecture"):
        instructeurs = Instructeur.objects.filter(archive=False).count()
        matieres_sans_instructeur, douzieme_mat = _matieres_sans_instructeur(nombre_matieres)
        indisponibles = _instructeurs_indisponibles_semaine(lundi_courant)
    if a_permission(utilisateur, "noyau.lieux_calendrier_lecture"):
        lieux = Lieu.objects.filter(archive=False).count()
        brigades_total, brigades_sans_salle, douzieme_brig = _brigades_sans_salle()
    return {
        "instructeurs": instructeurs,
        "matieres_sans_instructeur": matieres_sans_instructeur,
        "douzieme_matieres_sans_instructeur": douzieme_mat,
        "indisponibles": indisponibles,
        "lieux": lieux,
        "brigades_sans_salle": brigades_sans_salle,
        "douzieme_brigades_sans_salle": douzieme_brig,
    }


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


def _detail_programme(programme):
    """Nombre de séances et de brigades couvertes par un programme — deux
    requêtes bornées, jamais une par séance."""
    if programme is None:
        return 0, 0
    seances = Seance.objects.filter(programme=programme).count()
    brigades = (
        LigneProgramme.objects.filter(seance__programme=programme)
        .values("brigade_id")
        .distinct()
        .count()
    )
    return seances, brigades


def _etat_de_la_semaine(lundi, programmes):
    programme = programmes.get(lundi)
    etat = programme.etat if programme else None
    libelle = EtatProgramme(programme.etat).label if programme else None
    nombre_seances, nombre_brigades = _detail_programme(programme)
    return EtatProgrammeSemaine(
        lundi=lundi,
        etat=etat,
        etat_libelle=libelle,
        nombre_seances=nombre_seances,
        nombre_brigades=nombre_brigades,
    )


def _etat_des_deux_semaines(utilisateur, lundi_courant):
    if not a_permission(utilisateur, "noyau.programme_lecture"):
        return None, None
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


def _points_attention(utilisateur):
    alertes = programmes_en_attente = evaluations_non_pretes = None
    if a_permission(utilisateur, "noyau.suivi_lecture"):
        alertes = compte_alertes()
    if a_permission(utilisateur, "noyau.programme_validation_lecture"):
        programmes_en_attente = compte_en_attente_validation_ou_signature()
    if a_permission(utilisateur, "noyau.evaluations_lecture"):
        evaluations_non_pretes = evaluations_a_venir_non_pretes()
    return alertes, programmes_en_attente, evaluations_non_pretes


def tableau_de_bord_accueil(utilisateur) -> TableauBordAccueil:
    lundi_courant = _lundi_de_la_semaine(timezone.localdate())
    formations, matieres = _chiffres_referentiel(utilisateur)
    ressources = _chiffres_ressources(utilisateur, matieres, lundi_courant)
    en_cours, cloturees, stagiaires_actifs = _chiffres_organisation(utilisateur)
    semaine_courante, semaine_suivante = _etat_des_deux_semaines(utilisateur, lundi_courant)
    alertes, programmes_en_attente, evaluations_non_pretes = _points_attention(utilisateur)
    return TableauBordAccueil(
        nombre_formations=formations,
        nombre_matieres=matieres,
        nombre_instructeurs=ressources["instructeurs"],
        nombre_lieux=ressources["lieux"],
        nombre_sessions_en_cours=en_cours,
        nombre_sessions_cloturees=cloturees,
        nombre_stagiaires_actifs=stagiaires_actifs,
        nombre_matieres_sans_instructeur=ressources["matieres_sans_instructeur"],
        douzieme_matieres_sans_instructeur=ressources["douzieme_matieres_sans_instructeur"],
        nombre_brigades_sans_salle=ressources["brigades_sans_salle"],
        douzieme_brigades_sans_salle=ressources["douzieme_brigades_sans_salle"],
        nombre_instructeurs_indisponibles_semaine=ressources["indisponibles"],
        nombre_alertes_ecart=alertes,
        nombre_programmes_en_attente=programmes_en_attente,
        nombre_evaluations_non_pretes=evaluations_non_pretes,
        semaine_courante=semaine_courante,
        semaine_suivante=semaine_suivante,
    )
