# Revue du sprint 4

Prompt 49, Temps 6. Sprint du 12 au 24 octobre 2026, clos le 20 octobre,
quatre jours avant l'échéance. Même gabarit que `REVUE-SPRINT-3.md`.

## Stories livrées et points

**Quatorze stories sur quatorze livrées — périmètre entièrement rempli.**
55 points (25 Must, 30 Should) — recompte indépendant (checkboxes de
`sprint-4.md` et `git log`, voir `AVANCEMENT.md`, « Recompte daté
2026-10-20, Temps 5.3 »), pas une copie du tableau de suivi.

| Story | Points | Commit de clôture |
|---|---|---|
| US-SUI-05 — Déclarer la non-exécution d'une séance | 2 | `0f6d63a` |
| US-SUI-01 — Consulter le rapprochement prescrit/programmé/réalisé | 5 | `987201c` |
| US-SUI-06 — Éditer la progression réalisée hebdomadaire | 3 | `bddf365` |
| US-EVAL-05 — Saisir et vérifier les notes | 5 | `0a03465` |
| US-EVAL-06 — Calculer moyennes et classement | 5 | `297171c` |
| US-EVAL-07 — Générer les procès-verbaux de résultats | 5 | `3b0609e` |
| US-PLAN-07 — Signaler les écarts de volume horaire | 3 | `10c5fa5` |
| US-VAL-05 — Consulter les programmes et l'historique des validations | 5 | `f2f2745` |
| US-SES-09 — Clôturer une session | 3 | `0e5246a` |
| US-SUI-02 — Être alerté des écarts significatifs | 3 | `7570b33` |
| US-SUI-03 — Consulter le tableau de bord des formations | 5 | `101146a` |
| US-INS-04 — Consulter la charge d'un instructeur | 3 | `567526c` |
| US-REF-09 — Historiser les modifications du référentiel | 3 | `81a1dcb` |
| US-PLAN-11 — Dupliquer un programme hebdomadaire | 5 | `6527068` |

Chaque commit nomme explicitement le code de sa story — aucun commit
porteur de deux stories distinctes, contrairement au P-41 du sprint 3.

**Périmètre Must entier (194 points cumulés) livré au prompt 46**, avant
même le milieu du sprint 4 ; les cinq stories Should restantes livrées au
prompt 48, avant le point de décision du 21 octobre (`sprint-4.md`,
« toute story Should non commencée à cette date passe en réserve ») —
aucune story n'est passée en réserve.

## Jalon J3

**Tenu le 20 octobre, quatre jours avant l'échéance du 24.** Temps 0 à 7 du
prompt 49 : correctif D-285 (identité stable du journal, D-287), correctif
P-51 (verrou contre deux exécutions concurrentes de la suite), mesure de
stabilité, quatre arbitrages hors backlog (D-288 à D-291), audit complet du
diagramme de classes contre le code réel (D-292 à D-294), recomptes
vérifiés (`AVANCEMENT.md`), revue (ce document).

## Heures et vélocité

Consolidation de `heures-sprint-4.md` (33 lignes) **telle quelle**. « Heures
humaines » : jamais renseignée (règle du registre v7, R23, prompt 44) —
absente sur toutes les lignes, comme au sprint 3.

**Lignes fiables** (session continue, aucune interruption signalée) :
Temps 0+1 du prompt 44 (P-42), US-SUI-05, correctifs du prompt 45 Temps 1,
reprise de US-SUI-06, US-EVAL-05, US-EVAL-06, US-EVAL-07, corrections du
prompt 47 Temps 1, US-SUI-02, US-SUI-03, US-PLAN-11.

**Lignes non fiables**, interruption explicite signalée (« session
interrompue par une pause demandée ») : US-SUI-01, début de US-SUI-06 (non
close), préalables du prompt 46 (§0), US-PLAN-07, US-SES-09, US-INS-04
(pause 02:04-12:12 explicite).

**Deux outliers à signaler**, aucune pause notée mais une durée
anormalement courte pour leurs points : US-VAL-05 (13 min pour 5 points) et
US-SUI-03 (27 min pour 5 points) — plausibles si le gabarit d'un écran
voisin a été largement réutilisé (H1/H2 de US-VAL-05 lisent un journal déjà
écrit par d'autres stories, B2-B4 de US-SUI-03 réutilisent des sélecteurs
déjà posés), mais non confirmées par un relevé indépendant.

**Une anomalie trouvée** : la ligne US-REF-09 (13:46 le 19/10 → 23:30 le
20/10, ≈ 33 h 44) ne porte **aucune mention d'interruption**, contrairement
à toutes les autres sessions à cheval sur deux jours dans ce fichier — à
vérifier auprès de l'étudiant avant de la citer comme un temps de travail
continu. Non corrigée ici : ce fichier ne se réécrit pas après coup, même
pour signaler un doute (même principe que `REVUE-SPRINT-3.md`).

**Vélocité** : non recalculée à ce prompt — l'échantillon et sa fragilité
(aucune heure humaine, lignes non fiables mêlées aux fiables) restent ceux
déjà discutés au sprint 3 ; rien de nouveau ne justifierait de réviser la
clé actuelle (1,3 h/point) sur un sprint de plus avec le même défaut de
méthode.

## Reports : fermés et restant ouverts

Six reports ouverts à la clôture du sprint 3 (`REVUE-SPRINT-3.md`) :
D-108, D-133 (RG-64), D-182, D-212, D-215, Présélection (ECARTS 25).
Revérifiés un par un contre `DECISIONS.md` (D-259 à D-294) et
`ECARTS-LIVRABLES-SPRINT-4.md` — voir `AVANCEMENT.md`, « Recompte à la
clôture du sprint 4, prompt 49, Temps 5.2 » pour le détail :

- **D-108** fermé pendant US-SUI-01 (commit `987201c`) — jamais marqué
  dans `AVANCEMENT.md` avant ce prompt, corrigé ici.
- **D-133 (RG-64)** et **Présélection (ECARTS 25)** fermés par décision
  hors backlog de ce prompt (D-288/D-293 et D-290) — consignés comme
  limites ou dette assumées, sans implantation, conformément à l'arbitrage
  du prompt 49.
- **D-182, D-212, D-215** restent ouverts, intacts depuis la clôture du
  sprint 3 — aucune story du sprint 4 ne les a touchés, confirmés orphelins
  du backlog v10/v11.

**Net à la clôture du sprint 4 : trois reports ouverts**, aucun
n'appartenant au périmètre des quatorze stories livrées.

Aucun nouveau report ne s'est ouvert pendant le sprint 4 lui-même — les
sept décisions hors backlog de ce prompt de clôture (D-288 à D-294) ferment
ou consignent, aucune n'ouvre de dépendance vers une story future.

## Plage des décisions

**D-259 à D-294**, trente-six numéros, **aucun sauté**. Dernière décision
du sprint 3 : D-258 (2026-10-07). Première du sprint 4 : D-259 (2026-10-12,
correctif P-42). Les sept dernières (D-288 à D-294) sont le travail hors
backlog de ce prompt de clôture lui-même, pas une story du sprint.

**Anomalie mineure signalée, non corrigée** : D-269 (`ElementReferentiel`,
valeurs par défaut du coefficient et des deux poids) est rangée hors ordre
chronologique dans le fichier, entre D-276 et D-275, sans en être un numéro
manquant — un classement incohérent, pas un trou de traçabilité.

## Écarts consignés

**16 écarts** dans `ECARTS-LIVRABLES-SPRINT-4.md` (numérotés 1 à 16, sans
trou, reprise à 1 — convention propre au sprint 4) :

- Écarts 1 à 5 : consignés au fil des stories (US-SUI-05, US-SUI-01,
  US-SUI-06, US-REF-03 rétroactivement, US-EVAL-07).
- Écarts 6 à 8 : audit en lecture seule du prompt 47, **tranchés** à ce
  prompt (D-293) — limites assumées, aucune implantation.
- **Écart 4 fermé** à ce prompt : reconfirmé résolu depuis le prompt 46.
- Écarts 9 à 16 : **nouveaux**, trouvés par l'audit complet du diagramme de
  classes contre le code réel (Temps 5.1 de ce prompt) — `TypeFormation.
  code`, `Formation.dureeTheorique` vs `duree_semaines`, `Lieu.typologie`/
  `CategorieLieu` (deux valeurs en code contre trois au diagramme),
  `ElementReferentiel.type_lieu_partage`, l'archivage de `GrilleHoraire`,
  quatre champs du journal (`cible`, `identifiant_saisi`, `detail`,
  `objet_cle`), `Utilisateur.doit_changer_mot_de_passe`, `Avenant.nature`
  (énumération fermée) contre `natureModification` (texte libre au
  diagramme). Aucun n'a reçu de correction du diagramme lui-même à ce
  prompt — consignés, pas portés dans `13-diagramme-classes.md` (même
  convention que le diagramme pose lui-même à sa § 13 : « le report des
  corrections documentaires après la revue est un choix assumé »).

Deux points ouverts du diagramme (§ 12) ont en revanche été **fermés par
décision** plutôt que simplement consignés : le rattachement de
`ObjectifPedagogique` à `Matiere` (D-292) et le statut d'`EditionProgression`
au regard de l'interdit des attributs dérivés (D-294, § 1.4 du diagramme
devenu obsolète sur ce point précis).

## Suite de tests, début et fin

- **Début du sprint** (commit de clôture du sprint 3, cité par
  `REVUE-SPRINT-3.md`) : **1977 tests** collectés.
- **Fin du sprint** (`master`, avant le tag de clôture) : **2261 tests**
  collectés (`pytest --collect-only -q`, exécuté réellement à ce prompt).
- **Net : +284 tests** sur le sprint.

## Stabilité de la suite complète (Temps 3)

Cause du blocage PostgreSQL établie (P-51, Temps 2) avant toute mesure :
deux exécutions indépendantes de la suite sur la même base, pas un défaut
du code — corrigée par un verrou de fichier. Cinq exécutions complètes et
consécutives, puis `pytest -m pdf` en conteneur : **zéro échec partout**
(2251 passés/10 ignorés à chaque exécution, 10/10 en conteneur). Détail
complet, tableau des cinq exécutions et réserve sur la durée (machine
partagée avec les forks de ce même prompt) : `docs/suivi/
MESURES-REFERENCE.md`, section « Stabilité de la suite — clôture J3 ».

## Mesures de requêtes

Aucune mesure de requêtes nouvelle propre au sprint 4 hors de celles déjà
consolidées dans `MESURES-REFERENCE.md` au fil des stories (US-PLAN-11/D7 :
43 requêtes constantes de 2 à 10 brigades) — rien à ajouter ici, la série
41 → 49 de US-PLAN-03 appartient aux sprints 2-3 et n'a plus bougé depuis
le prompt 45.

## Ce qui reste en dette pour la phase 6

- Les trois reports ouverts (D-182, D-212, D-215) — orphelins du backlog
  v10/v11, aucune story ne les porte.
- Les dix écarts non corrigés dans le diagramme de classes lui-même
  (9 à 16, plus 6 à 8 annotés mais pas encore portés dans le fichier) —
  correction documentaire reportée au mémoire, par choix assumé du projet.
- La dette de présélection (ECARTS 25) et la limite RG-64 (D-133) :
  mesurées/consignées, jamais implantées, sans échéance.
- La dette d'impression du programme hebdomadaire (mode par journée,
  `IMPRESSION-ANALYSE.md`) — confirmée visuellement par un exemplaire réel
  à ce prompt (D-291), décision d'implantation toujours en attente du
  lecteur.
- US-PLAN-08 (solveur) reste déclassée en perspective d'évolution (D-164,
  réexamen tenu sans réouverture à ce prompt, D-289).
- Les deux anomalies de `heures-sprint-4.md` signalées ci-dessus (US-VAL-05/
  US-SUI-03 outliers, US-REF-09 sans pause notée) — à vérifier auprès de
  l'étudiant, pas corrigées ici.

## Ce qui n'a pas pu être vérifié

La cause exacte des deux outliers de durée (US-VAL-05, US-SUI-03) et
l'absence de mention de pause sur la ligne US-REF-09 n'ont pas pu être
confirmées sans interroger l'étudiant — `heures-sprint-4.md` ne se
reconstitue jamais après coup, ces trois lignes restent telles qu'écrites.
