# Hypothèses de dimensionnement — étude de faisabilité CP-SAT (R6)

**Écrit et figé le 2026-09-17.** Prompt 32 § 2. Dépouillement des emplois du
temps et des progressions d'instruction du centre, conduit le 17 septembre
2026.

RÈGLE ABSOLUE (rappel) : ce fichier n'est plus réécrit après la première
mesure. Toute correction se fait par une ligne ajoutée, datée, dans la section
« Ajouts postérieurs », jamais par modification d'une ligne existante.

## Relevé sur les documents du centre

| Grandeur | Valeur |
|---|---|
| Sessions de formation actives simultanément | 15 |
| Brigades actives, toutes sessions confondues | 30 à 35 (1 à 3 par session, moyenne ≈ 2,2) |
| Instructeurs | 80 à 120 |
| Modules au catalogue | 70 à 100 |
| Lieux | 40 à 45 salles au total, dont 4 à 5 spécialisées ou communes, plus 2 à 3 espaces extérieurs (garage, terrain) |
| Créneaux hebdomadaires | grille ordinaire : 4 créneaux du lundi au jeudi, vendredi plus court — 19 à 20 créneaux |

## Déduit de ces relevés

| Grandeur | Calcul | Valeur |
|---|---|---|
| Salles ordinaires disponibles pour les salles attitrées | 40–45 − (4–5 spécialisées) − (2–3 extérieures) | 32 à 38 |
| Cases à pourvoir par semaine | brigades × créneaux | 570 à 700 |
| Capacité brute en créneaux-instructeur | instructeurs × créneaux | 1 520 à 2 400 par semaine |
| Capacité des lieux partagés | (6 à 8 espaces) × (19 à 20 créneaux) | 114 à 160 créneaux-lieu par semaine |

## Non encore relevé — traité en axe de sensibilité (§ 4 du protocole)

- proportion des séances exigeant un lieu spécialisé ou extérieur
- densité de la matrice de qualification : nombre moyen d'instructeurs
  qualifiés par module, et proportion de modules n'en comptant qu'un ou deux
- nombre de modules programmables par brigade sur une semaine donnée
- densité des indisponibilités d'instructeurs et des périodes bloquantes

## Observation de terrain — hors mesure, à porter au mémoire

**32 à 38 salles ordinaires pour 30 à 35 brigades.** Dans la combinaison la
plus défavorable (32 salles, 35 brigades), il en manque. Le centre fonctionne
donc à la limite de sa capacité en salles attitrées : RG-14 est presque
saturée en permanence, et ouvrir une session supplémentaire peut échouer faute
de salle — indépendamment de tout solveur. Ce n'est pas un résultat de
mesure ; à signaler séparément au chef de projet et à porter au mémoire
(voir aussi `RECOMMANDATION.md` une fois l'étude close, qui la reprendra sans
la mêler aux tableaux de mesure).

## Ajouts postérieurs

*(vide au 2026-09-17 — toute correction ultérieure s'ajoute ici, datée, sans
toucher aux lignes ci-dessus)*

**2026-09-19 — la « proportion des séances exigeant un lieu spécialisé ou
extérieur » se compte sur les SÉANCES À POURVOIR.** Le paramètre du § 4 (10,
15, 20, 25 %) a d'abord été appliqué au CATALOGUE des modules ; le solveur,
libre de choisir quels modules placer, évitait ceux qui exigent un lieu, et
la demande effective mesurée n'atteignait que 3,3 / 7,4 / 9,2 / 11,2 % des
séances (22 / 49 / 61 / 74 séances à lieu, contre 66 / 99 / 132 / 165
annoncées). La première matrice n'a donc jamais exercé cet axe (archivée :
`archives/matrice-v1-2026-09-18/`). Hypothèse retenue désormais : chaque
brigade a un programme cible de 20 séances dont exactement
`round(demande × 20)` exigent un lieu partagé — soit 66 / 99 / 132 / 165 à la
taille RÉELLE. Capacité nominale des lieux partagés : espaces × créneaux
(7 × 20 = 140 à la taille RÉELLE, 8 × 20 = 160 à la taille HAUTE), une
brigade non regroupée par espace et par créneau — le décompte du § 2. À 25 %,
165 séances pour 140 places : le remplissage ne peut pas dépasser 635/660.

**2026-09-19 — la prédiction « INFAISABLE à 25 % » (§ 4) était mal posée, pas
fausse.** Toutes les contraintes dures du modèle sont des plafonds (au plus une
séance par instructeur et par créneau, au plus le volume prescrit, au plus
la capacité du lieu) : ne rien placer les satisfait toutes, le problème n'est
donc JAMAIS infaisable. Ce qu'une demande supérieure à la capacité produit,
c'est un remplissage plafonné — et RG-31 / AD-GROUPEMENT font d'une case vide
un état normal. Le problème du CIT est un problème d'optimisation, pas de
satisfaction.
