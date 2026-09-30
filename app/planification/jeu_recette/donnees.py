"""Données constantes du jeu de recette — Prompt 34, § 2. Reprend EXACTEMENT
le § 4.2 du cahier de recette du sprint 2 : un objet de plus fausserait un
compte de contrôle, un objet manquant en bloquerait un autre.

Chaque objet porte son code (§ 2 : « visible à l'écran, dans l'intitulé si
nécessaire ») — préfixé dans l'intitulé pour les formations/matières/lieux,
posé en `nom` pour les instructeurs (le `prenom` porte alors le rôle, jamais
de nom réel du CIT, comme le jeu de démonstration).

Toutes fictives (aucun nom, matricule ou intitulé réel du CIT).
"""

from dataclasses import dataclass, field

from administration.models import Profil
from referentiel.models import CategorieLieu as CategorieLieuReferentiel
from referentiel.models import TypeLieuPartage as TypeLieuPartageReferentiel
from ressources.models import CategorieLieu as CategorieLieuRessource
from ressources.models import ModePartage as ModePartageRessource
from ressources.models import TypeLieuPartage as TypeLieuPartageRessource

MOT_DE_PASSE_COMMUN = "Transmissions#2026"


# --------------------------------------------------------------------- #
# Comptes
# --------------------------------------------------------------------- #


@dataclass(frozen=True)
class DonneesCompte:
    identifiant: str
    profil: str
    grade: str
    nom: str
    prenom: str


COMPTES = (
    DonneesCompte("u_ped", Profil.CELLULE_PEDAGOGIQUE, "Lt", "Recette", "Pédagogique"),
    DonneesCompte("u_plan", Profil.CELLULE_PLANIFICATION, "Lt", "Recette", "Planification"),
    DonneesCompte("u_exa", Profil.CELLULE_EXAMENS, "Lt", "Recette", "Examens"),
    DonneesCompte("u_df", Profil.DIRECTION_FORMATION, "Col", "Recette", "Direction"),
    DonneesCompte("u_adm", Profil.ADMINISTRATEUR, "Cne", "Recette", "Administrateur"),
)
IDENTIFIANT_ADMINISTRATEUR = "u_adm"


# --------------------------------------------------------------------- #
# Types de formation, matières — § 2
# --------------------------------------------------------------------- #

# code -> intitulé complet (visible à l'écran, le code en préfixe)
TYPES_FORMATION = {
    "TF1": "TF1 — Formation initiale",
    "TF2": "TF2 — Formation de spécialité",
}

MATIERES = {
    "M1": ("M1 — Procédures de recette (salle attitrée)", CategorieLieuReferentiel.SALLE_ATTITREE),
    "M2": (
        "M2 — Travaux pratiques de recette (lieu partagé)",
        CategorieLieuReferentiel.LIEU_PARTAGE,
    ),
    "M3": ("M3 — Théorie de recette (sans lieu)", CategorieLieuReferentiel.AUCUN_LIEU),
    "M4": ("M4 — Module de recette A (salle attitrée)", CategorieLieuReferentiel.SALLE_ATTITREE),
    "M5": ("M5 — Module de recette B (salle attitrée)", CategorieLieuReferentiel.SALLE_ATTITREE),
}
# M2 est un lieu partagé (§ 2 ne précise pas le type) : amphithéâtre, pour
# qu'un lieu du § 2 puisse réellement l'accueillir — voir L4 dans `LIEUX`.
TYPE_LIEU_PARTAGE_M2 = TypeLieuPartageReferentiel.AMPHITHEATRE


# --------------------------------------------------------------------- #
# Formations et référentiels — § 2
# --------------------------------------------------------------------- #

SPECIALITE_PAR_DEFAUT = "Recette"
DUREE_SEMAINES_PAR_DEFAUT = 10


@dataclass(frozen=True)
class FormationDemo:
    code: str
    libelle: str
    type_formation: str
    archive: bool = False
    # (code_matiere, volume_horaire) ; l'ordre fixe l'ordre d'affichage.
    composition: tuple = field(default_factory=tuple)


FORMATIONS = (
    FormationDemo(
        "F1",
        "Exploitant radio",
        "TF1",
        composition=(("M1", 20), ("M2", 10), ("M3", 10)),
    ),
    FormationDemo(
        "F2",
        "Chef de poste",
        "TF2",
        composition=(("M4", 10), ("M5", 10)),
    ),
    FormationDemo(
        "F3",
        "Formation archivée",
        "TF1",
        archive=True,
        composition=(("M1", 10),),
    ),
    FormationDemo("F4", "Formation sans référentiel", "TF1"),
)

# M4 est déclaré prérequis de M5, dans le référentiel de F2 (§ 2).
PREREQUIS = (("F2", "M5", "M4"),)


# --------------------------------------------------------------------- #
# Instructeurs et qualifications — § 2
# --------------------------------------------------------------------- #


@dataclass(frozen=True)
class InstructeurDemo:
    code: str
    matricule: str
    qualifications: tuple
    archive: bool = False


INSTRUCTEURS = (
    InstructeurDemo("I1", "REC-INS-01", ("M1", "M2", "M3")),
    InstructeurDemo("I2", "REC-INS-02", ("M1",)),
    InstructeurDemo("I3", "REC-INS-03", ("M2",)),
    InstructeurDemo("I4", "REC-INS-04", ("M1",), archive=True),
    InstructeurDemo("I5", "REC-INS-05", ("M4", "M5")),
)
GRADE_INSTRUCTEUR_PAR_DEFAUT = "Lt"
SPECIALITE_INSTRUCTEUR_PAR_DEFAUT = "Recette"


# --------------------------------------------------------------------- #
# Lieux — § 2
# --------------------------------------------------------------------- #


@dataclass(frozen=True)
class LieuDemo:
    code: str
    libelle: str
    capacite: int
    categorie: str
    type_partage: str | None = None
    mode_partage: str | None = None
    archive: bool = False


# L3 (« salle attitrée, capacité non renseignée ») N'EST PAS ICI : impossible
# à produire — `ressources.models.Lieu.capacite` est un `PositiveIntegerField`
# obligatoire, avec une contrainte de base `ck_lieu_capacite_positive`. Ni le
# modèle ni le service ne permettent une capacité vide. Signalé (§ 2 du
# prompt : « NE CONTOURNE PAS : dis-le-moi »), documenté dans
# `docs/suivi/JEU-RECETTE.md`, jamais créé sous une forme approchante qui
# masquerait l'écart.
CODE_LIEU_IMPOSSIBLE = "L3"
MOTIF_LIEU_IMPOSSIBLE = (
    "capacité non renseignée demandée par le § 2, impossible : "
    "Lieu.capacite est un PositiveIntegerField obligatoire "
    "(contrainte ck_lieu_capacite_positive en base)."
)

LIEUX = (
    LieuDemo("L1", "L1 — Salle de recette 1", 20, CategorieLieuRessource.SALLE_ATTITREE),
    LieuDemo("L2", "L2 — Salle de recette 2", 15, CategorieLieuRessource.SALLE_ATTITREE),
    LieuDemo(
        "L4",
        "L4 — Amphithéâtre de recette",
        30,
        CategorieLieuRessource.LIEU_PARTAGE,
        TypeLieuPartageRessource.AMPHITHEATRE,
        ModePartageRessource.SIMULTANE,
    ),
    LieuDemo(
        "L5",
        "L5 — Laboratoire de recette",
        30,
        CategorieLieuRessource.LIEU_PARTAGE,
        TypeLieuPartageRessource.LABORATOIRE,
        ModePartageRessource.SEQUENTIEL,
    ),
    LieuDemo(
        "L6",
        "L6 — Salle de recette archivée",
        20,
        CategorieLieuRessource.SALLE_ATTITREE,
        archive=True,
    ),
)


# --------------------------------------------------------------------- #
# § 6 — option --pagination, formation dédiée F5
# --------------------------------------------------------------------- #

CODE_FORMATION_PAGINATION = "F5"
LIBELLE_FORMATION_PAGINATION = "F5 — Formation de pagination (--pagination uniquement)"
NOMBRE_SESSIONS_PAGINATION = 25
# F5 réutilise M3 (matière existante, « sans lieu », le référentiel le plus
# simple) pour être une formation valide sans introduire de sixième matière
# absente du § 2 — ServiceSession.creer refuse une formation sans référentiel
# composé (§ 4, Prompt 20).
MATIERE_FORMATION_PAGINATION = "M3"
VOLUME_FORMATION_PAGINATION = 10
