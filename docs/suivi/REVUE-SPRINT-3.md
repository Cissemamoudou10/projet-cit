# Revue du sprint 3

Prompt 43, § B1. Sprint du 28 septembre au 10 octobre 2026. Les reports
ont été reparcourus dans `DECISIONS.md` en entier sur toute la plage du
sprint (D-165 à D-258), pas seulement recomptés à la chaîne — voir
`AVANCEMENT.md`, section « Recompte intégral du sprint 3 », qui a corrigé
trois fermetures jamais marquées (D-39, D-121 E2 et A3, D-181), découvertes
par cette relecture.

## Stories livrées et points

**Onze stories sur onze livrées — périmètre entièrement rempli.** 50
points (47 au cadrage initial, +3 : US-PLAN-05 réestimée à 8 points pour
l'avenant, D-237, prompt 41).

| Story | Points | Commit de clôture |
|---|---|---|
| US-EVAL-01 — Créer une évaluation selon son type | 5 | `a6df84b` |
| US-EVAL-02 — Saisir la date d'un examen final | 2 | `3b91c89` |
| US-EVAL-03 — Enregistrer les sujets transmis et sélectionner celui retenu | 5 | `705ac44` |
| US-EVAL-04 — Organiser une épreuve | 5 | `df221be` (+ clôture 2026-10-04) |
| US-VAL-03 — Gérer les états du programme | 5 | prompt 39 |
| US-VAL-01 — Soumettre un programme à validation | 3 | prompt 40 |
| US-VAL-02 — Valider ou rejeter un programme | 5 | prompt 40 |
| US-VAL-04 — Empêcher l'affichage d'un programme non validé | 2 | prompt 40 |
| US-PLAN-05 — Modifier manuellement une affectation | 8 | prompt 41 + 42 partie 1 |
| US-PLAN-06 — Regrouper plusieurs brigades sur une même séance | 5 | `031ea98` |
| US-PLAN-09 — Traiter une indisponibilité déclarée | 5 | `d5c4b51` |

## Jalon J2

**Tenu le jour même, samedi 10 octobre.** Démonstration de mi-parcours
préparée (prompt 43, partie A) : scénario HTTP complet
(`tests/scenarios/test_demonstration_j2.py`, passé), commande
`preparer_demonstration` (base dédiée `pfe_cit_demo_j2`, rejouable, vérifiée
par trois exécutions réelles), guide `docs/demonstration/DEMO-J2.md`.
Décision go/no-go sur l'optimisation (US-PLAN-08) : **sans objet**,
arbitrée au sprint 2 (D-164 — renoncement retenu, US-PLAN-08 déclassée en
perspective d'évolution).

## Heures et vélocité (§ B2)

Consolidation de `heures-sprint-3.md` **tel quel** — rien n'y est
reconstitué, chaque ligne incomplète reste nommée comme telle. « Heures
humaines » : colonne jamais renseignée sur les seize lignes du fichier,
notée *absente* partout ci-dessous plutôt que répétée seize fois.

| Élément | Session | Points | Fiable pour la vélocité ? |
|---|---|---|---|
| ETA-01 (transverse) | 27 min | 0 | oui, mais hors points (tâche transverse) |
| US-EVAL-01 | 63 min | 5 | **oui** |
| US-EVAL-02 | 9 h 22 (562 min, à cheval sur minuit) | 2 | **oui** (session réellement continue, mais pèse 61 % du temps mesuré pour 8 % des points — outlier) |
| Temps 1 — correctif P-38 (transverse) | 48 min | 0 | oui, mais hors points |
| US-EVAL-03 | 25 h 22 nominal | 5 | **non** — le fichier lui-même signale une coupure non mesurée entre le début et la fin, pas un temps de travail continu |
| US-EVAL-04 (étapes 1-4) | — | 0 (story non close à cette ligne) | non — début non noté |
| US-EVAL-04 (clôture) | — | 0 (déjà compté) | non — début et fin non alignés |
| US-VAL-03 | — | 5 | non — début et fin non relevés |
| US-VAL-01 | — | 3 | non — début non relevé |
| US-VAL-02 | — | 5 | non — début non relevé |
| US-VAL-04 | — | 2 | non — début non relevé |
| US-PLAN-05 (prompt 41 + fin prompt 42 partie 1, deux lignes combinées) | 100 + 33 = 133 min | 8 | **oui** |
| US-PLAN-06 | 32 min | 5 | **oui** |
| US-PLAN-09 | 134 min | 5 | **oui** |
| J2 — cette clôture | en cours | 0 (transverse) | — |

**Vélocité mesurée** sur les cinq lignes fiables (US-EVAL-01, 02,
US-PLAN-05, 06, 09) : 924 minutes (15 h 24) pour 25 points, soit **≈ 1,62
point/heure (≈ 0,62 h/point)**. Sans US-EVAL-02 (l'outlier à 9 h 22) :
362 minutes (6 h 03) pour 23 points, soit **≈ 3,8 points/heure (≈ 0,26
h/point)** — un facteur 6 d'écart selon qu'on retient ou non une seule
ligne, sur un échantillon de cinq. **Ni l'une ni l'autre valeur ne justifie
de réviser la clé actuelle (1,3 h/point)** : l'échantillon est trop petit
et trop hétérogène pour trancher, et surtout, aucune heure humaine n'existe
pour corriger le biais de la mesure en heures de session (sprint 2,
`HEURES-SPRINT-2.md`) — la même conclusion qu'au sprint 2, pour la même
raison.

## Reports : ouverts au début, fermés, ouverts à la fin

Le premier relevé disponible DANS le sprint est daté du 2026-10-02 (prompt
37, quatre jours après son démarrage) : **quatorze reports ouverts** à
cette date — aucun relevé antérieur, daté du 28 septembre lui-même, n'a été
retrouvé (voir « ce qui n'a pas pu être vérifié »). De ces quatorze :

- **Onze** appartenaient au périmètre des stories du sprint 3 et sont
  **tous fermés** à sa clôture : D-39 (US-REF-06, volet saisie manuelle),
  D-119 (deux volets), D-121 (deux volets), D-171, D-172, D-170 (rattaché,
  pas une décision de plus), D-181, D-193, D-202.
- **Trois** étaient déjà orphelins ou hors périmètre à cette date
  (D-108 → sprint 4, D-133 → orpheline, D-182 → backlog v10) et le restent.

**Neuf reports se sont ouverts pendant le sprint** (US-EVAL-01 à 04) : six
avant le relevé du 2 octobre (D-171, D-172, D-181, D-182, D-193, D-202—
cinq déjà comptés ci-dessus comme fermés, D-182 excepté) et trois après
(D-212, D-215, et l'écart de présélection — ECARTS 25 — pendant US-EVAL-04),
ces trois derniers restant ouverts, hors périmètre des stories livrées.

**Net à la clôture : six reports ouverts**, aucun n'appartenant au
périmètre des onze stories livrées :

| Report | Objet | Story cible |
|---|---|---|
| D-108 | Volume horaire dispensé signalé à l'affectation | US-SUI-01 (sprint 4) |
| D-133 | RG-64, relation facultative séance↔créneau type | orpheline |
| D-182 | Mesure de l'écart de progression entre brigades | backlog v10 |
| D-212 | Badge « à vérifier » après changement de date | backlog v10 |
| D-215 | Badge de liste sur la complétude | backlog v10 |
| Présélection (ECARTS 25) | La présélection de génération ignore les épreuves | dette sprint 4 |

Deux écarts (au sens `ECARTS-LIVRABLES-SPRINT-3.md`, pas un « report » au
sens de ce tableau) restent également ouverts côté mémoire : CU-P5-04 A2/A3
(US-PLAN-06, D-248) et CU-P5-07 A4 (US-PLAN-09, D-256).

## Plage des décisions

**D-165 à D-258**, quatre-vingt-quatorze numéros — **D-252 non utilisé**
(saut de numérotation sans décision manquante, repéré en écrivant ce
rendu).

## Écarts consignés

**44 écarts** dans `ECARTS-LIVRABLES-SPRINT-3.md` (numérotés 1 à 44, sans
trou), répartis sur les livrables ETA-01, US-EVAL-01 à 04, US-PLAN-05, 06
et 09.

## Suite de tests, début et fin

- **Début du sprint** (commit de clôture du sprint 2, `e05a1c3`,
  `recette-sprint-2`) : **1432 tests** collectés (mesuré directement,
  `pytest --collect-only -q` sur un arbre de travail séparé à ce commit).
- **Fin du sprint** (ce commit) : **1977 tests** collectés, dont 1976
  passés lors de la dernière exécution propre de la suite entière (le
  1977e est le scénario de démonstration ajouté par ce prompt lui-même).
- **Net : +545 tests** sur le sprint.

## Mesures de requêtes de la génération — 41 → 47

`test_mesures_de_reference_us_plan_03_paragraphe_10`
(`REQUETES_REFERENCE_US_PLAN_03`) — quatre pas, chacun avec sa cause,
retrouvée dans `DECISIONS.md` et l'historique Git :

| Valeur | Cause | Décision | Commit |
|---|---|---|---|
| 41 (mesuré, non asserté) | Référence d'origine, sprint 2 | — | — |
| → 43 | RG-38 gagne une seconde source (`ResolveurJoursExamen`, interrogé même sans examen) | D-192 | — (US-EVAL-02) |
| 43 figée en assertion | Garde réelle ajoutée à la mesure (P-38/P-39, aucune assertion ne protégeait encore ce nombre) | — | `1970b3c` |
| → 45 | RG-53 dans les deux sens (`ResolveurOccupationsEpreuves`, lieu ET instructeur) | D-211 | `e1a31e9` |
| → 47 | Garde de modification (US-VAL-03) appelée désormais par la génération elle-même | — | `04c3465` |

**Inchangée depuis** (vérifiée par exécution réelle à la clôture d'US-PLAN-09,
prompt 42 partie 3, et de nouveau pour ce rendu) : US-PLAN-05, 06 et 09 ne
touchent pas `generation.py` — aucune note datée supplémentaire à ajouter.

## Ce qui reste en dette pour le sprint 4

- Les six reports ouverts listés ci-dessus (D-108, D-133, D-182, D-212,
  D-215, présélection/ECARTS 25).
- Les deux écarts de mémoire ouverts (CU-P5-04 A2/A3, CU-P5-07 A4).
- **P-42** (nouveau, § A5 de ce prompt) : le lot d'US-PLAN-09
  (`traiter_lot_remplacement`) peut verrouiller plusieurs programmes dans
  un ordre non déterministe — défaut de conception latent, pas seulement
  un artefact de test ; correction proposée : trier les séances du lot par
  `programme_id` avant la boucle.
- L'instabilité de la suite complète sous exécutions prolongées
  (interblocages PostgreSQL intermittents, non reproductibles isolément) —
  voir `RISQUES-PROPOSITIONS-J2.md`.
- US-PLAN-08 (optimisation) reste déclassée en perspective d'évolution
  (D-164, sans changement ce sprint).

## Ce qui n'a pas pu être vérifié

Le nombre de reports ouverts **au tout premier jour** du sprint (28
septembre) n'a pas pu être établi : aucun relevé n'est daté de ce jour-là
dans `DECISIONS.md` ou `AVANCEMENT.md` ; le premier relevé disponible est
celui du 2 octobre (quatorze). La valeur « 41 requêtes » d'origine
(avant D-192) n'est elle-même pas une assertion de test figée, seulement
une mesure journalisée citée par D-192 — non rejouable à l'identique
aujourd'hui (le code d'alors n'existe plus sur `master`).
