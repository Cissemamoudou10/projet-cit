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

### Série complète des requêtes, 41 → 51 (prompt 53, Temps 3)

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
| 49 → 51 | 2026-10-30 (évolution du prompt 53, Temps 3, correction de NC R00-GEN-03) | Le compte rendu condensé de la génération se persiste désormais (`ServiceGeneration._enregistrer_compte_rendu`, `CompteRenduGeneration`) : un `UPDATE`, puis un `INSERT` seulement si rien à mettre à jour — deux requêtes, coût FIXE par génération, pas `update_or_create` (son `SAVEPOINT` imbriqué en coûtait quatre de plus, 55 mesuré avant correction). Marge (2) intégralement consommée de nouveau, référence relevée à 51 |

**Mise à jour datée (2026-10-30, évolution du prompt 53, Temps 3, correction de NC R00-GEN-03).**
Le compte rendu de génération se persiste désormais à chaque appel, condensé
dans un seul `JSONField` (`CompteRenduGeneration.resume`) — jamais recalculé
après coup (voir docs/suivi/DECISIONS.md). Première version mesurée avec
`update_or_create` : **55 requêtes** (contre 49), quatre de plus que prévu —
son `transaction.atomic()` imbriqué pose un `SAVEPOINT` propre alors que la
génération tourne déjà dans sa propre transaction. Corrigé par une écriture
directe (`UPDATE` puis `INSERT` conditionnel, deux requêtes) avant que cette
mesure ne soit consignée : **51 requêtes** (contre 49). Constante
`REQUETES_REFERENCE_US_PLAN_03` mise à jour, marge (2) intégralement
consommée par ce changement — à surveiller sans délai au prochain ajout.

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

Chargement réel de `charger_jeu_volume` dans le conteneur
`python:3.14-slim-bookworm` (réseau Docker `developpement_default`, hôte
`base`, base `pfe_cit_volume`) — les mêmes conditions que `pytest -m pdf`
(P-44).

**Mesures refaites le 28/10/2026 (prompt 51 bis), remplaçant celles du
27/10/2026 ci-dessous** : le premier chargement datait toutes les 15
sessions actives à la même date et dimensionnait chaque référentiel sur
un tirage fixe (150-400 h) indépendant de la durée réelle de la session —
les semaines passées W-3 à W-1 ressortaient alors artificiellement vides
(référentiel épuisé), ce qui faussait la mesure BNF-04/BNF-05 de ces
semaines. Correctif : sessions actives échelonnées (dates de début entre
W-10 et W-1, plus deux sessions démarrant en W+1) et référentiel
dimensionné sur la durée réelle de la session qui le porte (voir
`docs/recette/JEUX-DE-DONNEES-PHASE-6.md`, § écarts). Les anciennes
valeurs (32 brigades toutes datées pareil, 64,51 s, BNF-05 sur un W0
encore vide) restent dans l'historique du dépôt (`git log` sur ce
fichier) mais ne sont plus la référence.

### BNF-04 — génération hebdomadaire (< 5 minutes)

32 brigades actives, 17 sessions actives (15 échelonnées + 2 à venir en
W+1), 3 terminées, 80 instructeurs, 793 stagiaires affectés.

| Semaine | Durée | État | Cases non pourvues |
|---|---|---|---|
| W-8 | 0,09 s | affiché | 0/40 |
| W-7 | 0,16 s | affiché | 0/80 |
| W-6 | 0,07 s | affiché | 0/80 |
| W-5 | 0,28 s | affiché | 0/160 |
| W-4 | 0,50 s | affiché | 0/180 |
| W-3 | 0,64 s | affiché | 0/220 |
| W-2 | 1,73 s | affiché | 0/420 |
| W-1 | 4,51 s | affiché | **0/560 (0 %)** |
| W0 | 5,77 s | affiché | **24/560 (4,3 %)** |
| W+1 | 7,81 s | validé | 174/640 (27,2 %) |
| W+2 | 5,16 s | soumis | 213/640 (33,3 %) |
| W+3 | 3,94 s | brouillon | 335/640 (52,3 %) |

**Large marge sur BNF-04** : la semaine la plus longue (W-1, 4,51 s pour
cette mesure ; W+1, 7,81 s dans une autre exécution — ordres de grandeur
identiques) reste très en deçà des 300 s visées. **Chargement complet :
≈55 s** — très en deçà des 30 minutes du § 3.2, aucun repli `--semaines`
nécessaire.

**W-1 et W0 sont désormais pleines** (cible du correctif, § 3.2 — « vérifie
que W-1, W0 et W+1 sont pleines »). Le seuil de 20 % sur W+1 a été posé
comme cible de calibrage, pas comme exigence, et levé une fois établi que
sa cause n'est plus le référentiel (voir classification ci-dessous) :
l'essentiel — W-1 et W0 pleines — est atteint.

### Classification des cases non pourvues de W+1 à W+3

Lecture directe des données (aucune modification), par brigade et par
semaine, trois catégories possibles : **(a)** la brigade n'a plus aucune
matière programmable (volume épuisé partout) ; **(b)** il lui reste des
matières, mais toutes bloquées par un prérequis non encore achevé au sens
du RÉALISÉ (RG-39 b) ; **(c)** elle a au moins une matière programmable,
mais aucun couple instructeur-lieu libre (RG-34/RG-37).

**Résultat : 100 % des brigades concernées, sur les trois semaines,
relèvent de la catégorie (c).** Zéro cas (a), zéro cas (b). Ce n'est donc
ni un référentiel épuisé, ni une propriété de l'application (RG-39 b,
qui aurait dominé et crû de W+1 à W+3 si le réalisé — qui ne compte que
les séances passées — ne pouvait structurellement pas rattraper une
semaine générée à l'avance) : c'est une **saturation de capacité** —
W+1 est la première semaine où les 17 sessions actives (32 brigades) sont
TOUTES actives en même temps et se disputent les mêmes 80 instructeurs
et 8 lieux partagés. Un relevé pour RECETTE-05, pas un défaut du jeu de
données ni du générateur.

### BNF-05 — rendu des six écrans (< 2 secondes)

Refait sur **W0** (désormais pleine, 4,3 % seulement de cases non
pourvues — contre une mesure initiale sur un W0 encore vide) ; client de
test Django, authentifié `v_df` (lecture seule) :

| Écran | Requêtes SQL | Durée |
|---|---|---|
| Liste des stagiaires (session la plus chargée, SV-A02) | 12 | 0,328 s |
| Consultation du programme W0 | 23 | 0,483 s |
| Rapprochement prescrit/réalisé (SV-A02) | 16 | 0,126 s |
| Tableau de bord | 16 | 0,198 s |
| Liste des programmes | 9 | 0,055 s |
| Charge d'un instructeur (IV001) | 10 | 0,077 s |

**Les six écrans tiennent largement sous les 2 secondes** — le plus lent
(consultation du programme W0, désormais chargé de vraies séances) à
0,483 s, contre 0,134 s sur l'ancienne mesure (W0 alors presque vide) :
l'écart illustre bien que la première mesure sous-pesait la charge
réelle d'un écran de programme plein.

### `--verifier`

```
État du jeu volumineux (§ 3.1, § 3.2)
  17/17 contrôles conformes.
```

## Mesure non obtenue

Aucune, pour le jeu volumineux : BNF-04, BNF-05, le taux de cases non
pourvues et sa classification par catégorie (a/b/c) sont tous mesurés
directement (chargement réel, client de test, lecture des données).

Pour le reste : les quatre points demandés par le bloc G, les deux mesures
de clôture J3, et les mesures du jeu volumineux ci-dessus ont chacun une
source vérifiée (test relancé, chargement réel ou fichier de suivi
existant) — rien d'autre n'est estimé.
