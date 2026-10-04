"""Données constantes du jeu de démonstration — Prompt 15, § 1.1.

Noms, intitulés et matricules sont entièrement inventés : aucun ne désigne
une personne, un grade nominatif ou une formation réels du CIT. Les volumes
horaires du référentiel ne sont volontairement pas ici : ils se calculent au
chargement à partir de `VOLUME_HORAIRE_HEBDOMADAIRE_REFERENCE` (§ 4 du
prompt — une valeur écrite en dur vieillirait avec les réglages du terrain,
même si ce n'est pas une date).
"""

from dataclasses import dataclass, field

from administration.models import Profil
from referentiel.models import CategorieLieu as CategorieLieuReferentiel
from referentiel.models import TypeLieuPartage as TypeLieuPartageReferentiel
from ressources.models import CategorieLieu as CategorieLieuRessource
from ressources.models import Statut
from ressources.models import TypeLieuPartage as TypeLieuPartageRessource

MOT_DE_PASSE_COMMUN = "Transmissions#2026"


# --------------------------------------------------------------------- #
# Comptes — § 3.1
# --------------------------------------------------------------------- #


@dataclass(frozen=True)
class DonneesCompte:
    identifiant: str
    profil: str
    grade: str
    nom: str
    prenom: str


IDENTIFIANT_INACTIF = "ped.inactif"
IDENTIFIANT_NOUVEAU = "ped.nouveau"
IDENTIFIANT_VERROUILLE = "ver.demo"

COMPTES = (
    DonneesCompte("adm.demo", Profil.ADMINISTRATEUR, "Col", "El Amrovic", "Rachid"),
    DonneesCompte("ped.demo", Profil.CELLULE_PEDAGOGIQUE, "Cdt", "Bramvel", "Yasmine"),
    DonneesCompte("pla.demo", Profil.CELLULE_PLANIFICATION, "Cne", "Chraibi", "Omar"),
    DonneesCompte("exa.demo", Profil.CELLULE_EXAMENS, "Lt", "Idrissi", "Sara"),
    DonneesCompte("dir.demo", Profil.DIRECTION_FORMATION, "Gal", "Alaoui", "Hicham"),
    DonneesCompte(IDENTIFIANT_INACTIF, Profil.CELLULE_PEDAGOGIQUE, "Lt", "Bouzid", "Nadia"),
    DonneesCompte(IDENTIFIANT_NOUVEAU, Profil.CELLULE_PEDAGOGIQUE, "S/Lt", "Sabri", "Anas"),
    DonneesCompte(IDENTIFIANT_VERROUILLE, Profil.CELLULE_PEDAGOGIQUE, "Adj", "Lahlou", "Imane"),
)


# --------------------------------------------------------------------- #
# Types de formation et matières — § 3.2, § 3.4
# --------------------------------------------------------------------- #

TYPES_FORMATION = ("Officiers", "Sous-officiers", "CAT-2")
TYPE_FORMATION_ARCHIVE = "Perfectionnement civil"

MATIERES = (
    "Procédures radio",
    "Chiffre et sécurité",
    "Topographie",
    "Réseaux de campagne",
    "Ordre serré",
    "Éducation physique",
    "Transmissions de données",
    "Protection électronique",
    "Secourisme",
    "Règlement de discipline",
    "Anglais technique",
    "Entretien du matériel",
)
MATIERE_ARCHIVEE = "Entretien du matériel"
MATIERE_SANS_INSTRUCTEUR = "Règlement de discipline"
MATIERE_ORPHELINE = "Anglais technique"

OBJECTIFS = {
    "Transmissions de données": (
        "Configurer un poste radio tactique en réseau de campagne",
        "Établir une liaison de données chiffrée point à point",
        "Diagnostiquer une panne de transmission courante",
        "Rédiger un compte rendu de liaison conforme au canevas du centre",
    ),
    "Procédures radio": (
        "Appliquer les procédures phonie réglementaires",
        "Utiliser l'alphabet international dans une transmission",
    ),
    "Topographie": ("Lire une carte d'état-major et s'orienter au compas",),
}


# --------------------------------------------------------------------- #
# Formations et composition des référentiels — § 3.3, § 3.5, § 3.7
# --------------------------------------------------------------------- #


@dataclass(frozen=True)
class ElementDemo:
    matiere: str
    categorie_lieu: str
    type_lieu_partage: str | None = None


@dataclass(frozen=True)
class FormationDemo:
    intitule: str
    specialite: str
    duree_semaines: int
    type_formation: str
    archive: bool = False
    facteur_volume: float = 1.0
    composition: tuple[ElementDemo, ...] = field(default_factory=tuple)


FORMATIONS = (
    FormationDemo(
        intitule="Formation initiale",
        specialite="Transmissions",
        duree_semaines=20,
        type_formation="Officiers",
        composition=(
            ElementDemo("Procédures radio", CategorieLieuReferentiel.SALLE_ATTITREE),
            ElementDemo("Transmissions de données", CategorieLieuReferentiel.SALLE_ATTITREE),
            ElementDemo("Protection électronique", CategorieLieuReferentiel.SALLE_ATTITREE),
            ElementDemo(
                "Topographie",
                CategorieLieuReferentiel.LIEU_PARTAGE,
                TypeLieuPartageReferentiel.SALLE_SPECIALISEE,
            ),
            ElementDemo("Chiffre et sécurité", CategorieLieuReferentiel.SALLE_ATTITREE),
            ElementDemo("Ordre serré", CategorieLieuReferentiel.AUCUN_LIEU),
            ElementDemo("Éducation physique", CategorieLieuReferentiel.AUCUN_LIEU),
            ElementDemo(
                "Secourisme",
                CategorieLieuReferentiel.LIEU_PARTAGE,
                TypeLieuPartageReferentiel.LABORATOIRE,
            ),
        ),
    ),
    FormationDemo(
        intitule="Formation initiale",
        specialite="Transmissions",
        duree_semaines=24,
        type_formation="Sous-officiers",
        composition=(
            ElementDemo("Procédures radio", CategorieLieuReferentiel.SALLE_ATTITREE),
            ElementDemo("Transmissions de données", CategorieLieuReferentiel.SALLE_ATTITREE),
            ElementDemo("Réseaux de campagne", CategorieLieuReferentiel.SALLE_ATTITREE),
            ElementDemo(
                "Secourisme",
                CategorieLieuReferentiel.LIEU_PARTAGE,
                TypeLieuPartageReferentiel.LABORATOIRE,
            ),
            ElementDemo("Éducation physique", CategorieLieuReferentiel.AUCUN_LIEU),
            ElementDemo("Ordre serré", CategorieLieuReferentiel.AUCUN_LIEU),
        ),
    ),
    FormationDemo(
        intitule="Perfectionnement radio",
        specialite="Procédures radio",
        duree_semaines=8,
        type_formation="CAT-2",
        composition=(
            ElementDemo("Procédures radio", CategorieLieuReferentiel.SALLE_ATTITREE),
            ElementDemo("Réseaux de campagne", CategorieLieuReferentiel.SALLE_ATTITREE),
            ElementDemo("Topographie", CategorieLieuReferentiel.SALLE_ATTITREE),
            ElementDemo("Ordre serré", CategorieLieuReferentiel.AUCUN_LIEU),
            ElementDemo(
                "Chiffre et sécurité",
                CategorieLieuReferentiel.LIEU_PARTAGE,
                TypeLieuPartageReferentiel.AMPHITHEATRE,
            ),
        ),
    ),
    FormationDemo(
        intitule="Spécialisation chiffre",
        specialite="Chiffre et sécurité",
        duree_semaines=6,
        type_formation="Officiers",
        facteur_volume=1.5,
        composition=(
            ElementDemo("Chiffre et sécurité", CategorieLieuReferentiel.SALLE_ATTITREE),
            ElementDemo(MATIERE_SANS_INSTRUCTEUR, CategorieLieuReferentiel.SALLE_ATTITREE),
            ElementDemo("Topographie", CategorieLieuReferentiel.SALLE_ATTITREE),
            ElementDemo("Protection électronique", CategorieLieuReferentiel.SALLE_ATTITREE),
            ElementDemo("Ordre serré", CategorieLieuReferentiel.AUCUN_LIEU),
        ),
    ),
    FormationDemo(
        intitule="Stage transmissions",
        specialite="Transmissions",
        duree_semaines=4,
        type_formation="CAT-2",
        archive=True,
    ),
)

# Officiers uniquement (§ 3.7) : chaîne de trois, plus un lien latéral pour
# que l'ordre topologique ne soit pas trivial. Perfectionnement radio n'en
# reçoit aucun — l'écran d'orientation vide se démontre par son absence.
PREREQUIS_OFFICIERS = (
    ("Transmissions de données", "Procédures radio"),
    ("Protection électronique", "Transmissions de données"),
    ("Protection électronique", "Chiffre et sécurité"),
)


# --------------------------------------------------------------------- #
# Instructeurs et qualifications — § 3.8, § 3.9
# --------------------------------------------------------------------- #


@dataclass(frozen=True)
class InstructeurDemo:
    cle: str
    nom: str
    prenom: str
    grade: str
    specialite: str
    statut: str
    matricule: str | None = None
    archive: bool = False


INSTRUCTEURS = (
    InstructeurDemo(
        "zalbrok",
        "Zalbrok",
        "Kelvar",
        "Cne",
        "Transmissions",
        Statut.MILITAIRE_DU_CENTRE,
        matricule="INS-2031",
    ),
    InstructeurDemo(
        "fassi",
        "Fassi",
        "Yorgal",
        "Lt",
        "Chiffre",
        Statut.MILITAIRE_DU_CENTRE,
        matricule="INS-2032",
    ),
    InstructeurDemo(
        "ouazzani",
        "Ouazzani",
        "Sara",
        "Cdt",
        "Électronique",
        Statut.MILITAIRE_DU_CENTRE,
        matricule="INS-2033",
    ),
    InstructeurDemo(
        "berrada",
        "Berrada",
        "Hicham",
        "Cne",
        "Transmissions",
        Statut.MILITAIRE_DU_CENTRE,
        matricule="INS-2034",
    ),
    InstructeurDemo(
        "tazi", "Tazi", "Nadia", "Lt", "Sport", Statut.MILITAIRE_DU_CENTRE, matricule="INS-2035"
    ),
    InstructeurDemo(
        "belhaj",
        "Belhaj",
        "Omar",
        "Adj",
        "Langues",
        Statut.MILITAIRE_DU_CENTRE,
        matricule="INS-2036",
    ),
    InstructeurDemo(
        "sqalli",
        "Sqalli",
        "Imane",
        "Cne",
        "Électronique",
        Statut.MILITAIRE_DU_CENTRE,
        matricule="INS-2037",
        archive=True,
    ),
    InstructeurDemo("guessous", "Guessous", "Anas", "Formateur", "Langues", Statut.VACATAIRE),
    InstructeurDemo("rifai", "Rifai", "Salma", "Formatrice", "Sport", Statut.VACATAIRE),
    InstructeurDemo("kabbaj", "Kabbaj", "Mohammed", "Professeur", "Chiffre", Statut.CIVIL),
)
INSTRUCTEUR_SANS_QUALIFICATION = "belhaj"

# Une seule entrée qualifie « Protection électronique » (Ouazzani) — § 3.9,
# c'est elle que la recette retirera pour déclencher l'avertissement d'E2.
#
# Les deux vacataires et le civil reçoivent chacun une qualification : § 3.9
# ne prévoit qu'un seul instructeur « qualifié pour rien » (`belhaj`) — les
# laisser tous sans qualification aurait fait de chaque statut non-militaire
# un second cas de fiche vide, non prévu par le prompt. `sqalli` (archivé)
# n'en a délibérément aucune : archivé, il n'apparaît plus dans les écrans de
# qualification, sa fiche vide n'y est donc jamais visible.
QUALIFICATIONS = {
    "zalbrok": ("Procédures radio", "Transmissions de données", "Réseaux de campagne", "Secourisme"),
    "fassi": ("Chiffre et sécurité", "Topographie", "Secourisme"),
    "ouazzani": ("Protection électronique", "Topographie", "Réseaux de campagne"),
    "berrada": (
        "Procédures radio",
        "Transmissions de données",
        "Ordre serré",
        "Éducation physique",
    ),
    "tazi": ("Ordre serré", "Éducation physique", "Chiffre et sécurité"),
    "guessous": ("Topographie",),
    "rifai": ("Éducation physique",),
    "kabbaj": ("Chiffre et sécurité",),
}


# --------------------------------------------------------------------- #
# Lieux et indisponibilités — § 3.10
# --------------------------------------------------------------------- #


@dataclass(frozen=True)
class LieuDemo:
    intitule: str
    capacite: int
    categorie: str
    type_partage: str | None = None
    archive: bool = False


LIEUX = (
    LieuDemo("Salle 101", 20, CategorieLieuRessource.SALLE_ATTITREE),
    LieuDemo("Salle 102", 25, CategorieLieuRessource.SALLE_ATTITREE),
    LieuDemo("Salle 103", 25, CategorieLieuRessource.SALLE_ATTITREE),
    LieuDemo("Salle 104", 30, CategorieLieuRessource.SALLE_ATTITREE),
    LieuDemo("Salle 105", 32, CategorieLieuRessource.SALLE_ATTITREE),
    LieuDemo(
        "Amphithéâtre Ibn Khaldoun",
        150,
        CategorieLieuRessource.LIEU_PARTAGE,
        TypeLieuPartageRessource.AMPHITHEATRE,
    ),
    LieuDemo(
        "Laboratoire réseaux",
        16,
        CategorieLieuRessource.LIEU_PARTAGE,
        TypeLieuPartageRessource.LABORATOIRE,
    ),
    LieuDemo(
        "Laboratoire électronique",
        18,
        CategorieLieuRessource.LIEU_PARTAGE,
        TypeLieuPartageRessource.LABORATOIRE,
    ),
    LieuDemo(
        "Salle spécialisée chiffre",
        12,
        CategorieLieuRessource.LIEU_PARTAGE,
        TypeLieuPartageRessource.SALLE_SPECIALISEE,
    ),
    LieuDemo(
        "Salle spécialisée transmissions",
        24,
        CategorieLieuRessource.LIEU_PARTAGE,
        TypeLieuPartageRessource.SALLE_SPECIALISEE,
    ),
    LieuDemo("Salle 106", 20, CategorieLieuRessource.SALLE_ATTITREE, archive=True),
)
LIEU_INDISPONIBILITES = "Salle 101"
LIEU_RECOUVREMENT = "Salle 102"
