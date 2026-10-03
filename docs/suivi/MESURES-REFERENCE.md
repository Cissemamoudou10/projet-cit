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

## Mesure non obtenue

Aucune. Les quatre points demandés par le bloc G ont chacun une source
vérifiée (test relancé ou fichier de suivi existant) — rien n'est estimé.
