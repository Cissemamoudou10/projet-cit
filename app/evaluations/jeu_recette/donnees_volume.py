"""Paramètres de dimensionnement du jeu volumineux — Prompt 51, Temps 3,
§ 3.1. Calés sur `etudes/solveur/HYPOTHESES.md` là où il diverge du § 3.1
littéral (écart de calibrage, pas une décision de conception — consigné
dans `docs/recette/JEUX-DE-DONNEES-PHASE-6.md`, jamais dans DECISIONS.md) :

- Instructeurs : 80 (borne basse de la plage 80-120 d'HYPOTHESES.md, contre
  ≈55 au § 3.1) — à nombre de brigades égal, moins d'instructeurs est le cas
  le plus contraint pour la génération, celui qu'il faut mesurer.
- Sessions actives : 15 (contre 7 au § 3.1), pour 32 brigades — ≈2,1
  brigades par session, conforme à la moyenne de 2,2 d'HYPOTHESES.md.
  Plusieurs formations portent alors deux sessions simultanées (CU-P3-01,
  cas A1, autorisé).

Le reste du § 3.1 est inchangé : 3 sessions terminées, ≈900 stagiaires,
36 salles attitrées, 8 lieux partagés, 70 matières au catalogue.
"""

NOMBRE_TYPES_FORMATION = 4
NOMBRE_FORMATIONS = 10
NOMBRE_FORMATIONS_ARCHIVEES = 1
NOMBRE_MATIERES_CATALOGUE = 70
MATIERES_PAR_REFERENTIEL = (8, 15)  # (min, max) inclus
VOLUME_HORAIRE_REFERENTIEL = (150, 400)  # heures totales d'un référentiel
PROFONDEUR_PREREQUIS = (2, 3)

NOMBRE_INSTRUCTEURS = 80  # HYPOTHESES.md (80-120), borne basse retenue
QUALIFICATIONS_PAR_INSTRUCTEUR = (2, 5)
PROPORTION_INSTRUCTEURS_ARCHIVES = 0.1  # « quelques » (§ 3.1) — environ 8/80

NOMBRE_SALLES_ATTITREES = 36
CAPACITE_SALLE_ATTITREE = (15, 30)
NOMBRE_LIEUX_PARTAGES_AMPHI_SIMULTANE = 2
NOMBRE_LIEUX_PARTAGES_LABO_SEQUENTIEL = 3
NOMBRE_LIEUX_PARTAGES_SALLE_SPECIALISEE = 3
CAPACITE_LIEU_PARTAGE = (25, 60)

NOMBRE_SESSIONS_ACTIVES = 15  # HYPOTHESES.md (ratio 2,2 brigades/session), contre 7 au § 3.1
NOMBRE_SESSIONS_TERMINEES = 3
NOMBRE_BRIGADES_ACTIVES = 32  # § 3.1, cohérent avec HYPOTHESES.md (30-35)

NOMBRE_STAGIAIRES_CIBLE = 900
NOMBRE_STAGIAIRES_RADIES = 20
NOMBRE_STAGIAIRES_NON_AFFECTES = 15

NOMBRE_INDISPONIBILITES = 40

# § 3.1 : 8 semaines passées affichées (W-8 à W-1), ≈5 % d'avenants,
# ≈3 % de non-exécutions ; W0 affichée ; W+1 validée ; W+2 soumise ;
# W+3 brouillon.
SEMAINES_PASSEES_AFFICHEES = 8
PROPORTION_SEANCES_AVEC_AVENANT = 0.05
PROPORTION_SEANCES_NON_EXECUTEES = 0.03

NOMBRE_SESSIONS_TERMINEES_AVEC_PV = 2
NOMBRE_CERTIFICATIVES_A_VENIR = 5

# BNF-04 : génération < 5 min (par semaine, mesurée ici par semaine ET en
# cumulé). BNF-05 : rendu d'écran < 2 s.
SECONDES_MAX_GENERATION_HEBDOMADAIRE = 300
SECONDES_MAX_RENDU_ECRAN = 2
SECONDES_MAX_CHARGEMENT_TOTAL = 1800  # § 3.2 : au-delà, proposer --semaines N
