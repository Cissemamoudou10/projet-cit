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
| Requêtes SQL | **41, constantes** (pente nulle de 40 à 200 séances — corrigé de 1 239, 6/séance, par P-38) |
| Appels à `ServiceContraintes.verifier` | 360 |
| Taux de remplissage | 100 % (200/200) |

Bien en deçà des cinq minutes de BNF-04.

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

## Suite de tests — progression depuis la clôture du sprint 1

| | Valeur |
|---|---|
| Total au 2026-09-08 (clôture sprint 1) | 738 |
| Total au 2026-09-30 | **1 430** |
| Écart | +692 |
| Progression | **+93,8 %** |

## Impression — voir `docs/suivi/IMPRESSION-ANALYSE.md`, § 11

Consolidé séparément (déjà à jour, mesuré au fil du sprint pour chaque
story) : trois écrans en dette au sprint 4 (Instructeurs et Lieux —
paysage suffit ; Programme hebdomadaire — mode par journée nécessaire,
ni le portrait ni le paysage ne suffisent pour la semaine entière), tous
les autres écrans mesurés tiennent déjà en portrait.

## Mesure non obtenue

Aucune. Les quatre points demandés par le bloc G ont chacun une source
vérifiée (test relancé ou fichier de suivi existant) — rien n'est estimé.
