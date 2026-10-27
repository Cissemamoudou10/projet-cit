# Mesures de référence consolidées — clôture du sprint 2 (Prompt 33, bloc G)

## US-PLAN-03, § 10 — jeu représentatif (trois sessions, dix brigades)

Version POST-P-38 (correction du 2026-09-19, revue du Prompt 32 — voir
`docs/suivi/DECISIONS.md`, D-161). Garanties par un test permanent :
`app/planification/tests/test_generation_performance.py::
test_mesures_de_reference_us_plan_03_paragraphe_10` — relancé le
2026-09-30, toujours vert.

| Mesure | Valeur |
|---|---|
| Temps total de génération | 0,389 s |
| Requêtes SQL | **43, constantes** (pente nulle de 40 à 200 séances — corrigé de 1 239, 6/séance, par P-38 ; **41 → 43 le 2026-10-02, note ci-dessous**) |
| Appels à `ServiceContraintes.verifier` | 360 |
| Taux de remplissage | 100 % (200/200) |

Bien en deçà des cinq minutes de BNF-04.

### Série complète des requêtes, 41 → 49 (prompt 45, Temps 1.2)

Chaque pas est constant (même mesure rejouée, jamais une dérive silencieuse)
et expliqué — c'est ce tableau qui le prouve, pas seulement le commentaire du
code.

| Requêtes | Date | Cause |
|---|---|---|
| 41 | 2026-09-19 | Référence post-P-38 (pente nulle de 40 à 200 séances, corrigée de 1 239/6 par séance) |
| 41 → 43 | 2026-10-02 (prompt 36, A8) | US-EVAL-02 : seconde source de RG-38 (`Contexte.jours_examen`, `ResolveurJoursExamen`), un appel de plus par chargement de `ServiceContraintes.contexte()`, même sans examen en base |
| 43 → 45 | 2026-10-03 (prompt 38, A6, D-211) | US-EVAL-04 : occupations d'épreuves (`ResolveurOccupationsEpreuves`), une requête de plus par chargement, deux chargements par génération |
| 45 → 47 | 2026-10-04 (US-VAL-03, D-222) | Garde de modification : deux verrous `select_for_update` — passage jamais consigné ici avant le prompt 45, seulement dans le commentaire du code (gap documentaire comblé a posteriori) |
| 47 → 49 | 2026-10-13 (prompt 44, Temps 3, US-SUI-01, R2) | Prérequis (RG-39 b) vérifié sur le réalisé plutôt que le programmé (`volumes_realises_par_element_brigade`), une requête de plus par chargement, deux chargements par génération — marge (2) intégralement consommée, référence relevée à 49 (prompt 45, Temps 1.2) pour ne pas la laisser s'épuiser en silence (règle du prompt 36, A8) |

**Mise à jour datée (2026-10-13, prompt 44, Temps 3, US-SUI-01, R2).** Le
prérequis (RG-39 b) se vérifie désormais sur le réalisé
(`volumes_realises_par_element_brigade`) plutôt que sur le programmé : une
requête de plus à chaque chargement de `ServiceContraintes.contexte()`,
deux chargements par génération — même mécanique que les deux mises à jour
ci-dessous. Mesuré : **49 requêtes** (contre 47). Constante
`REQUETES_REFERENCE_US_PLAN_03` mise à jour, marge (2) intégralement
consommée par ce changement — à surveiller sans délai au prochain ajout.
Écart constaté en préparant cette mise à jour : le passage **45 → 47**
(US-VAL-03, D-222, deux verrous `select_for_update` de la garde de
modification) n'avait jamais été consigné ici, seulement dans le
commentaire du code — gap documentaire antérieur à ce prompt, signalé
plutôt que corrigé rétroactivement avec des chiffres non revérifiés.

**Mise à jour datée (2026-10-03, prompt 38, A6, D-211).** Le contexte de contraintes
charge désormais les occupations d'épreuves (`ResolveurOccupationsEpreuves`) :
une requête de plus à chaque chargement, deux chargements par génération
(`generation.py`, `ecriture.py`). Mesuré : **45 requêtes** (contre 43). Constante
`REQUETES_REFERENCE_US_PLAN_03` mise à jour, marge inchangée.

**Mise à jour datée (2026-10-02, prompt 36, A8).** US-EVAL-02 ajoute une
seconde source à RG-38 (`Contexte.jours_examen`, résolue via
`ResolveurJoursExamen`) : un appel de plus dans `ServiceContraintes.
contexte()`, même sans aucun examen en base — d'où le passage mesuré de 41
à 43 (relancé le 2026-10-02, toujours vert, aucune assertion ne fixait ce
nombre, voir § suivant). `test_h6_...` (grand lot, 15 candidates) passe de
même de 11 à 12 requêtes, toujours sous la borne de 15 — aucune dérive
silencieuse (A8) : l'ajout est borné, vérifié indépendant du nombre
d'examens par `evaluations.tests.test_rg38_examen::test_f1_requetes_
verifier_lot_identiques_0_et_10_examens`.

## US-PLAN-04 — `verifier_lot`, nombre de requêtes (test H6)

`app/planification/tests/test_contrat_service.py::
test_h6_nombre_de_requetes_sql_borne_et_independant_du_nombre_de_candidates`
— relancé le 2026-09-30, vert.

Le test ne fixe pas un chiffre unique par conception (§ 12, Prompt 30) : il
prouve que le nombre de requêtes d'un lot de 3 candidates et d'un lot de 15
candidates est **identique** (`len(petit_lot) == len(grand_lot)`) et reste
**strictement inférieur à 15** (`len(grand_lot) < 15`) — c'est-à-dire borné
et indépendant de la taille du lot, l'exigence réelle de RG-34 à RG-39 sur
un programme complet. Le nombre exact de requêtes n'est volontairement pas
gravé dans l'assertion, pour ne pas transformer un refactor sans régression
en échec de test.

## US-PLAN-11 — `ServiceDuplication.dupliquer`, nombre de requêtes (D7, prompt 48)

`app/planification/tests/test_duplication.py::
test_requetes_constantes_avec_deux_et_dix_brigades` — mesuré le 2026-10-19,
vert.

Même patron que US-PLAN-04 (ci-dessus), « mesurée comme la génération » (D7
du prompt) : une séance regroupée à dix brigades, dupliquée pour 2 puis pour
les 10 — **43 requêtes dans les deux cas** (chauffe préalable sur une
semaine cible jetée, P-39). Deux chargements de `ServiceContraintes.
contexte()` par duplication (un pour évaluer les candidates, un second à
l'intérieur de `ServiceEcritureSeance.creer_seances`, qui ne fait jamais
confiance à l'appelant) — même double chargement que `ServiceGeneration.
generer`, pas une régression propre à la duplication.

## Suite de tests — progression depuis la clôture du sprint 1

| | Valeur |
|---|---|
| Total au 2026-09-08 (clôture sprint 1) | 738 |
| Total au 2026-09-30 | **1 430** |
| Écart | +692 |
| Progression | **+93,8 %** |

**Erratum (2026-10-01, prompt 35).** Le total réel du commit de clôture
`e05a1c3` est **1 432**, pas 1 430 — vérifié par `pytest --collect-only`
comparé au commit précédent (`fd13947`), via un worktree temporaire.
Les deux tests en cause,
`app/organisation/tests/test_stagiaire_ecran.py::
test_e1_deradier_stagiaire_par_l_ecran_deradie_reellement` et
`app/planification/tests/test_modeles.py::
test_d83_suppression_brigade_au_programme_refusee_par_le_vrai_chemin_de_
service`, ont été écrits tard dans la session de clôture — après que la
ligne ci-dessus a été calculée — mais sont entrés dans le même commit.
Écart donc de +694 (pas +692) et progression de +94,0 % (pas +93,8 %) par
rapport aux 738 du sprint 1. La ligne d'origine n'est pas corrigée : elle
reste la trace de ce qui a été écrit à ce moment-là.

## Impression — voir `docs/suivi/IMPRESSION-ANALYSE.md`, § 11

Consolidé séparément (déjà à jour, mesuré au fil du sprint pour chaque
story) : trois écrans en dette au sprint 4 (Instructeurs et Lieux —
paysage suffit ; Programme hebdomadaire — mode par journée nécessaire,
ni le portrait ni le paysage ne suffisent pour la semaine entière), tous
les autres écrans mesurés tiennent déjà en portrait.

## Stabilité de la suite — clôture J3 (prompt 49, Temps 2 et 3)

**Cause du blocage PostgreSQL (P-51), établie avant toute mesure** : deux
exécutions **indépendantes** de la suite lancées en même temps sur la même
base (`test_pfe_cit`) provoquent un interblocage lors de la création
concurrente des groupes d'habilitation par les fixtures — un défaut de
méthode d'exécution, jamais un défaut du code applicatif. Corrigé par un
verrou de fichier, session-scoped (`conftest.py::_poser_verrou`), qui
refuse de démarrer une seconde exécution plutôt que de laisser PostgreSQL
trancher ; une exception explicite laisse passer un sous-processus pytest
légitime (`test_jeu_recette_depot.py`), via une variable d'environnement
héritée (`PFE_CIT_PYTEST_VERROU_POSE`).

**Cinq exécutions complètes et consécutives**, mesurées le 2026-10-20 :

| Exécution | Début | Fin | Durée | Résultat |
|---|---|---|---|---|
| 1 | 19:42:39 | 19:52:57 | 618 s (10 min 18) | 2251 passés, 10 ignorés, **0 échec** |
| 2 | 19:52:57 | 20:01:07 | 490 s (8 min 10) | 2251 passés, 10 ignorés, **0 échec** |
| 3 | 20:01:07 | 20:11:49 | 642 s (10 min 42) | 2251 passés, 10 ignorés, **0 échec** |
| 4 | 20:11:49 | 20:23:09 | 680 s (11 min 20) | 2251 passés, 10 ignorés, **0 échec** |
| 5 | 20:23:09 | 20:34:23 | 674 s (11 min 14) | 2251 passés, 10 ignorés, **0 échec** |

**Zéro échec sur les cinq exécutions** — la cause corrigée (P-51) ne s'est
pas reproduite, et aucune autre cause de non-déterminisme ne s'est
manifestée. Même nombre de tests passés/ignorés à chaque exécution :
déterministe sur ce point aussi.

**Réserve honnête sur la durée, pas sur le résultat.** Ces cinq exécutions
n'ont PAS tourné sur une machine strictement oisive comme l'exigeait la
mesure : plusieurs agents de fond (recherche documentaire pour ce même
prompt) partageaient la machine pendant la mesure — découvert après coup,
voir `docs/suivi/RISQUES-PROPOSITIONS-J3.md`, « Point de méthode ». Durée
mesurée 490 à 680 s, contre ~245 s pour une exécution isolée plus tôt dans
la session (14:18-14:26, avant la contamination). Cette charge concurrente
ralentit l'exécution mais n'affecte pas la justesse d'un test PostgreSQL
(les contraintes et transactions restent correctes sous contention) : le
résultat « zéro échec » reste valide, la métrique de durée ne l'est pas
comme référence de performance.

**`pytest -m pdf`, conteneur `python:3.14-slim-bookworm`** (réseau Docker
`developpement_default`, hôte `base`), exécuté une fois après les cinq
répétitions : **10 passés, 0 échec** (WeasyPrint, 36,5 s) — confirme que
les dix tests marqués `pdf` (US-SUI-06 et US-EVAL-07) restent verts dans
l'environnement cible, comme à chaque story qui en dépendait.

## Jeu volumineux (Prompt 51, Temps 3) — pleine échelle

Chargement réel de `charger_jeu_volume` (32 brigades actives, 15 sessions
en cours, 3 terminées, 80 instructeurs, 787 stagiaires affectés), lancé le
2026-10-27 dans le conteneur `python:3.14-slim-bookworm` (réseau Docker
`developpement_default`, hôte `base`, base `pfe_cit_volume`) — les mêmes
conditions que `pytest -m pdf` (P-44).

### BNF-04 — génération hebdomadaire (< 5 minutes)

| Semaine | Durée | État | Cases non pourvues |
|---|---|---|---|
| W-8 | 9,01 s | affiché | 14/640 |
| W-7 | 6,72 s | affiché | 383/640 |
| W-6 | 0,60 s | affiché | 104/640 |
| W-5 | 2,28 s | affiché | 444/640 |
| W-4 | 1,07 s | affiché | 628/640 |
| W-3 | 0,67 s | **brouillon** (A9, aucune séance) | 640/640 |
| W-2 | 0,52 s | **brouillon** (A9) | 512/640 |
| W-1 | 0,57 s | **brouillon** (A9) | 640/640 |
| W0 | 0,67 s | brouillon | 640/640 |
| W+1 | 0,60 s | brouillon | 640/640 |
| W+2 | 0,55 s | brouillon | 512/640 |
| W+3 | 0,67 s | brouillon | 604/640 |

**Large marge sur BNF-04** : la semaine la plus longue (W-8, 9,01 s) reste
très en deçà des 300 s visées. **Chargement complet (32 brigades, référentiel,
ressources, organisation, calendrier, évaluations, 12 programmes,
procès-verbaux) : 64,51 s** — très en deçà des 30 minutes du § 3.2, aucun
repli `--semaines` nécessaire.

**Mesure, pas un défaut à masquer (§ 3.2)** : à partir de W-3, le
référentiel (calibré sur 80 instructeurs, la borne la plus contraignante
d'`HYPOTHESES.md`) est épuisé pour la plupart des brigades — les semaines
W-3 à W+3 restent largement ou totalement vides (640/640 à sept reprises).
C'est la conséquence directe et attendue du choix délibéré de mesurer le
cas le plus contraint (§ écart « calibrage » de
`docs/recette/JEUX-DE-DONNEES-PHASE-6.md`) : un référentiel de 150 à 400 h
par formation, réparti sur 15 sessions actives, s'épuise vite à 80
instructeurs quand 32 brigades sollicitent les mêmes ressources en
parallèle. Rien n'a été corrigé : c'est un relevé pour RECETTE-05.

### BNF-05 — rendu des six écrans (< 2 secondes)

Mesuré par le client de test Django (authentifié `v_df`, lecture seule),
sur la même base pleine échelle :

| Écran | Requêtes SQL | Durée |
|---|---|---|
| Liste des stagiaires (session la plus chargée, SV-A02) | 12 | 0,563 s |
| Consultation du programme W0 | 18 | 0,134 s |
| Rapprochement prescrit/réalisé (SV-A02) | 16 | 0,081 s |
| Tableau de bord | 16 | 0,123 s |
| Liste des programmes | 9 | 0,038 s |
| Charge d'un instructeur (IV001) | 10 | 0,035 s |

**Les six écrans tiennent largement sous les 2 secondes** — le plus lent
(liste des stagiaires, 787 au total) à 0,563 s.

### `--verifier`

```
État du jeu volumineux (§ 3.1, § 3.2)
  17/17 contrôles conformes.
```

## Mesure non obtenue

**Motifs dominants des cases non pourvues, par semaine (§ 3.2).** Le taux
global (tableau BNF-04 ci-dessus) est mesuré ; la répartition PAR MOTIF
(lieu saturé, instructeur non qualifié, RG-38...) que
`ServiceGeneration.generer` calcule bien (`CompteRendu.cases_non_pourvues
[].motifs`) n'a pas été conservée pendant ce chargement — seul le compte
agrégé l'a été. Pour W-3 à W+3 (640/640 ou proche), le motif dominant est
déductible sans ambiguïté (volume prescrit épuisé, A9) ; pour W-7/W-5/W-4
(taux intermédiaires, séances réellement placées), la répartition fine
entre RG-37 (lieux partagés saturés) et RG-39 (volume déjà consommé par
une autre brigade) n'est pas isolée — à obtenir par une relecture
instrumentée, si RECETTE-05 en a besoin.

Pour le reste : les quatre points demandés par le bloc G, les deux mesures
de clôture J3, et les mesures du jeu volumineux ci-dessus ont chacun une
source vérifiée (test relancé, chargement réel ou fichier de suivi
existant) — rien d'autre n'est estimé.
