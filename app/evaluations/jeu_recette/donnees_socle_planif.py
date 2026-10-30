"""Données constantes de l'état `socle-planif` — Prompt 53, Temps 1.

Reprend EXACTEMENT ce que les sections 3 à 7 de RECETTE-00 construisent par
l'interface (session, brigades, import de stagiaires, calendrier,
indisponibilités, objectifs pédagogiques), pour que RECETTE-00 bis dispose
d'un état de départ propre, sans aucun programme. Réutilise le référentiel,
les instructeurs et les lieux du socle (F1, I1-I5, L1-L5) : aucun nouvel
objet de ce côté. Toutes données fictives.
"""

from dataclasses import dataclass

CODE_SESSION = "S0"
INTITULE_SESSION = "S0 — Exploitant radio (socle-planif)"
CODE_FORMATION_SESSION = "F1"
DECALAGE_SEMAINE_DEBUT_SESSION = -1  # lundi de W-1
DECALAGE_SEMAINE_FIN_SESSION = 10  # vendredi de W+10
EFFECTIF_ATTENDU_SESSION = 40


@dataclass(frozen=True)
class BrigadeSoclePlanif:
    code: str
    effectif_previsionnel: int
    code_lieu_attitre: str


BRIGADES_SOCLE_PLANIF = (
    BrigadeSoclePlanif("EXP1", 20, "L1"),
    BrigadeSoclePlanif("EXP2", 15, "L2"),
)

# Deux fichiers de recette existants (`fichiers_import/constructeur.py`),
# importés par le SERVICE D'IMPORT — jamais par création directe de
# `Stagiaire` : 10 + 45 = 55 (§ Temps 1).
FICHIERS_IMPORT_STAGIAIRES = ("01-valide-10.csv", "03-valide-45-colonnes-permutees.csv")
NOMBRE_STAGIAIRES_IMPORTES = 55

NOMBRE_AFFECTES_EXP1 = 20
NOMBRE_AFFECTES_EXP2 = 15
NOMBRE_RADIES = 1
NOMBRE_NON_AFFECTES = (
    NOMBRE_STAGIAIRES_IMPORTES - NOMBRE_AFFECTES_EXP1 - NOMBRE_AFFECTES_EXP2 - NOMBRE_RADIES
)  # 19

MOTIF_RADIATION = "Inaptitude médicale constatée (recette, prompt 53)."

# R00-SES-14/15 (traité à la séance de corrections) : une affectation faite
# le jour même ne peut être déplacée qu'un jour plus tard — le jeu ne doit
# pas en hériter. Les 35 affectations (EXP1 + EXP2) sont donc datées au
# lundi de W-1 par horloge simulée, jamais au jour du chargement réel.
DECALAGE_SEMAINE_AFFECTATION = -1

# Calendrier — centre entier dans les deux cas.
NATURE_CONFERENCE = "Conférence"
INTITULE_CONFERENCE = "Conférence centre entier (socle-planif)"
DECALAGE_SEMAINE_CONFERENCE = 1  # mardi de W+1
HEURE_DEBUT_CONFERENCE = (8, 0)
HEURE_FIN_CONFERENCE = (9, 45)

NATURE_CONGE = "Congé"
INTITULE_CONGE = "Congé centre entier (socle-planif)"
DECALAGE_SEMAINE_CONGE = 3  # vendredi de W+3

# Indisponibilités.
MOTIF_INDISPONIBILITE_I1 = "Mission (recette, prompt 53)."
MOTIF_INDISPONIBILITE_L5 = "Indisponibilité de recette (prompt 53)."

# Objectifs pédagogiques — deux, ordres 1 et 2, sur M3.
CODE_MATIERE_OBJECTIFS = "M3"
OBJECTIFS_PEDAGOGIQUES_M3 = (
    "Identifier les procédures de recette.",
    "Appliquer les procédures de recette.",
)
