"""Données constantes ajoutées par l'état `complet` — Prompt 51, Temps 2.
Reprend EXACTEMENT le § 2 du prompt : un objet de plus ou de moins fausserait
`--verifier` ou un cahier de recette qui s'appuie sur ce jeu.

Ne redéfinit RIEN du jeu `socle` (`donnees.py`, inchangé) : les formations
`F2` (session `S2`/`S3`) et les lieux `L1`/`L2` (brigades `EXP1`/`EXP2`) du
socle sont réutilisés tels quels, importés depuis `donnees.py`.

Toutes les données sont fictives (§ 7, règle commune) — codes courts (`I6`,
`EXP1`…) à la manière du jeu `socle`, pas de syllabes générées ici : ce sont
des objets énumérés par le prompt, pas une population en volume (réservée au
jeu `--etat volume`, Temps 3, où `jeu_recette.alea` prend le relais).
"""

from dataclasses import dataclass

from referentiel.models import CategorieLieu as CategorieLieuReferentiel
from referentiel.models import TypeLieuPartage as TypeLieuPartageReferentiel
from ressources.models import CategorieLieu as CategorieLieuRessource
from ressources.models import ModePartage as ModePartageRessource
from ressources.models import TypeLieuPartage as TypeLieuPartageRessource

# --------------------------------------------------------------------- #
# § 2.1 — Référentiel ajouté
# --------------------------------------------------------------------- #

MATIERES_COMPLET = {
    # Libellés courts : la chaîne « matière — formation — type » (évaluation,
    # organisation d'épreuve) se concatène sur plusieurs niveaux de __str__
    # (ElementReferentiel -> Evaluation -> OrganisationEpreuve -> Brigade ->
    # Session) jusqu'à heurter la limite de 150 caractères d'un champ de
    # journal (`administration_entree_journal.identifiant_saisi`) — vérifié
    # en pratique, pas en théorie.
    "M6": ("M6 — Procédures avancées", CategorieLieuReferentiel.SALLE_ATTITREE),
    "M7": ("M7 — Travaux pratiques avancés", CategorieLieuReferentiel.LIEU_PARTAGE),
    "M8": ("M8 — Module avancé A", CategorieLieuReferentiel.SALLE_ATTITREE),
    "M9": ("M9 — Module avancé B", CategorieLieuReferentiel.SALLE_ATTITREE),
}
# M7 est un lieu partagé : laboratoire, pour que L9 (amphithéâtre, § 2.2) ne
# soit pas son seul lieu possible — cohérent avec le § 2.4 (la séance
# regroupée du programme porte M2, pas M7, et vit dans L9).
TYPE_LIEU_PARTAGE_M7 = TypeLieuPartageReferentiel.LABORATOIRE

CODE_FORMATION_F6 = "F6"
LIBELLE_FORMATION_F6 = "F6 — Transmissions"
TYPE_FORMATION_F6 = "TF1"  # réutilise le type TF1 du socle, déjà chargé


@dataclass(frozen=True)
class ElementReferentielF6:
    code_matiere: str
    volume_horaire: int
    coefficient: int = 1
    poids_formatif: int = 1
    poids_certificatif: int = 1


# Total 200 h (§ 2.1) : plus de six semaines pleines, pour qu'aucune des
# quatre semaines du § 2.4 n'épuise le référentiel — à la différence de F1
# (40 h, socle), qui s'épuise exprès dans RECETTE-00.
COMPOSITION_F6 = (
    ElementReferentielF6("M1", 40, coefficient=3, poids_formatif=1, poids_certificatif=2),
    ElementReferentielF6("M2", 30),
    ElementReferentielF6("M3", 20),
    ElementReferentielF6("M6", 40, coefficient=2),
    ElementReferentielF6("M7", 30),
    ElementReferentielF6("M8", 20),
    ElementReferentielF6("M9", 20),
)
VOLUME_TOTAL_F6 = sum(element.volume_horaire for element in COMPOSITION_F6)
assert VOLUME_TOTAL_F6 == 200, f"§ 2.1 attend 200 h, calcul = {VOLUME_TOTAL_F6} h"

# M6 prérequis de M8 (§ 2.1), dans le référentiel de F6.
PREREQUIS_COMPLET = (("F6", "M8", "M6"),)

# Deux objectifs pédagogiques sur M6 (§ 2.1) — libellés fictifs, visiblement
# de recette.
OBJECTIFS_PEDAGOGIQUES_M6 = (
    "Objectif de recette 1 sur M6",
    "Objectif de recette 2 sur M6",
)


# --------------------------------------------------------------------- #
# § 2.2 — Ressources ajoutées
# --------------------------------------------------------------------- #


@dataclass(frozen=True)
class InstructeurComplet:
    code: str
    matricule: str
    qualifications: tuple


INSTRUCTEURS_COMPLET = (
    InstructeurComplet("I6", "REC-INS-06", ("M6", "M8")),
    InstructeurComplet("I7", "REC-INS-07", ("M7",)),
    InstructeurComplet("I8", "REC-INS-08", ("M6", "M9")),
    InstructeurComplet("I9", "REC-INS-09", ("M3", "M9")),
)
# I3 existe déjà (socle, qualifié M2) : M1 lui est ajouté, pas recréé.
QUALIFICATION_AJOUTEE_I3 = ("I3", "M1")


@dataclass(frozen=True)
class LieuComplet:
    code: str
    libelle: str
    capacite: int
    categorie: str
    type_partage: str | None = None
    mode_partage: str | None = None


LIEUX_COMPLET = (
    LieuComplet("L7", "L7 — Salle de recette 7", 12, CategorieLieuRessource.SALLE_ATTITREE),
    LieuComplet("L8", "L8 — Salle de recette 8", 20, CategorieLieuRessource.SALLE_ATTITREE),
    LieuComplet(
        "L9",
        "L9 — Amphithéâtre de recette 2",
        60,
        CategorieLieuRessource.LIEU_PARTAGE,
        TypeLieuPartageRessource.AMPHITHEATRE,
        ModePartageRessource.SIMULTANE,
    ),
)

# Indisponibilité passée (§ 2.2) : I3, tout le mardi de W-1, motif « stage ».
# Bornes posées par le chargeur sur la journée entière du mardi concerné
# (00:00 -> 00:00 le lendemain) : le § 2.2 dit « tout le mardi », pas une
# plage horaire précise.
MOTIF_INDISPONIBILITE_I3 = "stage"

# Calendrier (§ 2.2) : nature -> (intitulé, décalage_semaine, jour_iso_debut,
# heure_debut, jour_iso_fin, heure_fin, portée). Portée : "centre" (aucune
# cible) ou ("brigade", code) — jamais une session ciblée dans ce § 2.2.
PORTEE_CENTRE_ENTIER = "centre"


@dataclass(frozen=True)
class PeriodeComplet:
    nature: str
    intitule: str
    decalage_semaine_debut: int
    jour_iso_debut: int
    heure_debut: tuple  # (heure, minute) ou None pour 00:00
    decalage_semaine_fin: int
    jour_iso_fin: int
    heure_fin: tuple | None  # None = fin de journée (00:00 le jour suivant)
    cible_brigade: str | None = None


PERIODES_COMPLET = (
    PeriodeComplet(
        "Conférence",
        "Conférence centre entier (recette, § 2.2)",
        -1,
        3,
        (8, 0),
        -1,
        3,
        (9, 45),
    ),
    PeriodeComplet(
        "Congé",
        "Congé centre entier (recette, § 2.2)",
        3,
        5,
        None,
        3,
        5,
        None,
    ),
    PeriodeComplet(
        "Bivouac",
        "Bivouac — brigade EXP2 (recette, § 2.2)",
        2,
        4,
        None,
        2,
        5,
        None,
        cible_brigade="EXP2",
    ),
)


# --------------------------------------------------------------------- #
# § 2.3 — Organisation
# --------------------------------------------------------------------- #


@dataclass(frozen=True)
class SessionComplet:
    code: str
    intitule: str
    code_formation: str
    decalage_semaine_debut: int
    decalage_semaine_fin: int


SESSIONS_COMPLET = (
    # Intitulés courts — même raison que MATIERES_COMPLET ci-dessus (limite
    # de 150 caractères sur `identifiant_saisi` du journal, atteinte par la
    # concaténation Session -> Brigade -> Evaluation/OrganisationEpreuve).
    # S1 sert à la clôture REFUSÉE (évaluations E3/E4 non finalisées, § 2.7).
    SessionComplet("S1", "S1", "F6", -3, 8),
    SessionComplet("S2", "S2", "F2", -3, 6),
    # S3 sert à la clôture RÉUSSIE (US-SES-09) : aucune évaluation (§ 2.3).
    SessionComplet("S3", "S3 (close)", "F2", -12, -5),
)


@dataclass(frozen=True)
class BrigadeComplet:
    code: str
    code_session: str
    effectif_previsionnel: int
    code_lieu: str  # salle attitrée — peut référencer un lieu du socle (L1/L2)


BRIGADES_COMPLET = (
    BrigadeComplet("EXP1", "S1", 20, "L1"),
    BrigadeComplet("EXP2", "S1", 15, "L2"),
    BrigadeComplet("CDP1", "S2", 12, "L7"),
    BrigadeComplet("CDP9", "S3", 8, "L8"),
)

# Stagiaires de S1 (§ 2.3) : 35 affectés (répartis EXP1/EXP2 selon leur
# effectif prévisionnel : 20 + 15), 3 non affectés, 1 radié. EXP1/EXP2 étant
# déjà à capacité pleine (salles L1/L2, 20/15 places), le radié n'est jamais
# affecté avant sa radiation — rien dans le § 2.3 ne l'exige, et une
# affectation puis radiation immédiate dépasserait la capacité de la salle.
# Préfixe de matricule distinct par session, dans le style du socle
# (`REC-INS-xx`) : `REC-STG-S1-xxxx`, etc. — jamais un nom généré par
# `jeu_recette.alea` ici, réservé au jeu volumineux.
PREFIXE_MATRICULE_STAGIAIRE = "REC-STG"
GRADE_STAGIAIRES_PAR_DEFAUT = "2cl"
UNITE_STAGIAIRES_PAR_DEFAUT = "CIT"
NOMBRE_NON_AFFECTES_S1 = 3
NOMBRE_RADIES_S1 = 1
MOTIF_RADIATION = "Radiation (recette, § 2.3)."
