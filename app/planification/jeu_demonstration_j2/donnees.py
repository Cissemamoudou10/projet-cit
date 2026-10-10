"""Données constantes de la démonstration J2 — Prompt 43, § A1/A3.

Noms et intitulés entièrement inventés. Un seul fil fixe (A1) : le jeu reste
volontairement petit — juste assez pour que chaque étape ait de quoi
s'exercer, jamais un centre complet.
"""

from dataclasses import dataclass

from administration.models import Profil

MOT_DE_PASSE_COMMUN = "Transmissions-J2#2026"


# --------------------------------------------------------------------- #
# Comptes — un par profil (§ A3 : « un compte par profil »)
# --------------------------------------------------------------------- #


@dataclass(frozen=True)
class DonneesCompte:
    identifiant: str
    profil: str
    grade: str
    nom: str
    prenom: str


COMPTES = (
    DonneesCompte("adm.j2", Profil.ADMINISTRATEUR, "Cne", "Démonstration", "Administrateur"),
    DonneesCompte("ped.j2", Profil.CELLULE_PEDAGOGIQUE, "Lt", "Démonstration", "Pédagogique"),
    DonneesCompte("plan.j2", Profil.CELLULE_PLANIFICATION, "Lt", "Démonstration", "Planification"),
    DonneesCompte("exa.j2", Profil.CELLULE_EXAMENS, "Cne", "Démonstration", "Examens"),
    DonneesCompte("df.j2", Profil.DIRECTION_FORMATION, "Col", "Démonstration", "Direction"),
)
IDENTIFIANT_ADMINISTRATEUR = "adm.j2"


# --------------------------------------------------------------------- #
# Référentiel — une formation, deux matières
# --------------------------------------------------------------------- #

TYPE_FORMATION = "Formation J2"
FORMATION = "Transmetteur J2"
SPECIALITE = "Transmissions"
DUREE_SEMAINES = 20

# M1 porte le programme hebdomadaire (étapes 1, 5, 8). M2 porte le
# contrôle formatif (étape 2) et l'examen final certificatif (étape 9) —
# en SALLE ATTITRÉE (jamais AUCUN_LIEU) : aucune brigade de ce jeu n'en a
# une, la génération écarte donc M2 d'elle-même pour chacune
# (`_a_une_salle_attitree`, « pas de salle attitrée ») — sans quoi elle
# occuperait Beta, seul qualifié pour M2, sur toute la semaine. Intitulés
# courts : plusieurs champs d'affichage concatènent matière, formation,
# brigade et lieu dans une seule colonne bornée (varchar(150)).
MATIERE_PROGRAMME = ("Procédures radio J2", "J2-M1", 40)
MATIERE_EXAMENS = ("Transmission sécurisée J2", "J2-M2", 40)


# --------------------------------------------------------------------- #
# Instructeurs et qualifications
# --------------------------------------------------------------------- #


@dataclass(frozen=True)
class DonneesInstructeur:
    nom: str
    matricule: str
    qualifications: tuple[str, ...]


INSTRUCTEUR_TITULAIRE = DonneesInstructeur("Alpha (J2)", "J2-INS-01", ("J2-M1",))
INSTRUCTEUR_REMPLACANT = DonneesInstructeur("Gamma (J2)", "J2-INS-02", ("J2-M1",))
INSTRUCTEUR_EXAMENS = DonneesInstructeur("Beta (J2)", "J2-INS-03", ("J2-M2",))
INSTRUCTEURS = (INSTRUCTEUR_TITULAIRE, INSTRUCTEUR_REMPLACANT, INSTRUCTEUR_EXAMENS)
GRADE_INSTRUCTEUR = "Lt"


# --------------------------------------------------------------------- #
# Lieu
# --------------------------------------------------------------------- #

LIEU = "Salle J2"
LIEU_CAPACITE = 25


# --------------------------------------------------------------------- #
# Session, brigade, stagiaires
# --------------------------------------------------------------------- #

SESSION = "Session J2"
BRIGADE = "DEMO-J2"
EFFECTIF_STAGIAIRES = 18
UNITE_STAGIAIRES = "1er RTR (démonstration)"
GRADE_STAGIAIRES = "Sgt"

# Seconde brigade, non sélectionnée à la génération de l'étape 1 : la
# génération remplit tout créneau libre tant que le volume prescrit n'est
# pas atteint (RG-39, vérifié sur UNE seule exécution, pas encore mis à
# jour par la précédente) — aucun créneau de la semaine ne reste libre pour
# la brigade générée. Celle-ci reste entièrement libre pour le contrôle de
# l'étape 2.
BRIGADE_TEMOIN = "DEMO-J2-TEMOIN"
EFFECTIF_TEMOIN = 10
