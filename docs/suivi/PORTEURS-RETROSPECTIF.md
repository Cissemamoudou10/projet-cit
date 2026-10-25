# Attribution rétrospective des porteurs

**Attribution reconstituée après coup, le 25/10/2026, par le binôme. Elle
est déclarée rétrospective : aucune ligne existante des suivis de sprint ni
de `DECISIONS.md` n'a été réécrite. Motif : la colonne Porteur n'a pas été
tenue pendant les sprints (registre v8, R16).**

## Méthode

Sprint, code et titre repris des fichiers `sprint-N.md`. Commit de clôture
recherché par `git log --all --grep="CODE"` (recherche insensible à la
casse, sur l'historique complet) — chaque correspondance a été relue en
entier avant d'être retenue, pour écarter les commits qui ne font que
*citer* un autre code en passant (report, renvoi) sans le clore.
**« NON TROUVÉ » signifie que le code n'apparaît dans le message d'aucun
commit** — la story a bien été livrée (voir `sprint-N.md`), seul son
commit ne la cite pas littéralement ; aucune reconstitution n'a été
tentée par un autre moyen.

**Porteur** et **Second** sont laissés vides : c'est l'étudiant et son
binôme qui les rempliront. Aucun moyen de connaître ici la contribution
réelle, et la répartition prévue en phase 3 n'est pas la répartition
réelle.

## Sprint 1 — 15 stories

| Code | Titre | Points | Commit de clôture | Porteur | Second | Observations |
|---|---|---|---|---|---|---|
| US-ADM-01 | S'authentifier au système | 3 | NON TROUVÉ | | | |
| US-ADM-02 | Gérer les comptes utilisateurs | 5 | NON TROUVÉ | | | |
| US-ADM-03 | Restreindre l'accès selon le profil | 5 | `fa7f14e` | | | Commit partagé avec US-REF-07 (table unique de refus d'habilitation, bloc D.2 du prompt 19, clôture du sprint 1) — même situation que P-41, deux stories sur un commit |
| US-ADM-04 | Journaliser les actions sensibles | 3 | NON TROUVÉ | | | |
| US-REF-00 | Gérer les types de formation | 2 | NON TROUVÉ | | | Cité seulement en passant dans le commit `f357230` (US-REF-02) : « TypeFormation.code, jamais implémenté depuis US-REF-00 » — pas sa propre clôture |
| US-REF-01 | Gérer les formations | 3 | `26a71ac` | | | |
| US-REF-02 | Gérer le catalogue des matières | 3 | `f357230` | | | |
| US-REF-03 | Composer le référentiel d'une formation | 8 | NON TROUVÉ | | | Seule mention littérale dans tout l'historique : `5dc9179`, un correctif du **sprint 4** (P-45, prompt 46 — coefficient et poids manquants). La livraison d'origine, au sprint 1, ne cite jamais le code |
| US-REF-04 | Déclarer la catégorie de lieu requise par matière | 3 | NON TROUVÉ | | | |
| US-REF-05 | Associer des objectifs pédagogiques aux matières | 3 | NON TROUVÉ | | | |
| US-REF-06 | Déclarer les prérequis d'un référentiel | 5 | `9c98cc6` | | | |
| US-REF-07 | Consulter le référentiel depuis les autres cellules | 2 | `fa7f14e` | | | Commit partagé avec US-ADM-03, voir ci-dessus |
| US-INS-01 | Gérer les instructeurs | 5 | `4d1d6b5` | | | |
| US-INS-02 | Établir la matrice de qualification | 5 | NON TROUVÉ | | | |
| US-PLAN-02 | Gérer les lieux d'enseignement | 3 | `0cbccf3` | | | |

## Sprint 2 — 12 stories

| Code | Titre | Points | Commit de clôture | Porteur | Second | Observations |
|---|---|---|---|---|---|---|
| US-SES-01 | Ouvrir une session de formation | 5 | NON TROUVÉ | | | Cité seulement en passant dans `26a71ac` (US-REF-01) : « critère 4 reporté à US-SES-01 » |
| US-SES-02 | Constituer les brigades d'une session | 5 | NON TROUVÉ | | | |
| US-SES-03 | Affecter une salle attitrée à chaque brigade | 3 | `13d8c6f` | | | |
| US-SES-04 | Consulter la composition d'une session | 3 | NON TROUVÉ | | | |
| US-SES-05 | Enregistrer les stagiaires d'une session | 5 | NON TROUVÉ | | | |
| US-SES-06 | Affecter les stagiaires aux brigades | 5 | `50b7bdb` | | | |
| US-SES-07 | Consulter la liste des stagiaires | 3 | NON TROUVÉ | | | |
| US-INS-03 | Enregistrer les indisponibilités transmises | 3 | NON TROUVÉ | | | |
| US-PLAN-01 | Élaborer le calendrier académique annuel | 8 | NON TROUVÉ | | | |
| US-PLAN-03 | Générer le programme hebdomadaire d'une brigade | 8 | NON TROUVÉ | | | Cité seulement en passant dans `4d1d6b5` (US-INS-01) : « report du critère 4 vers US-PLAN-03 » |
| US-PLAN-04 | Garantir le respect des contraintes dures | 8 | `9fa38fb` | | | |
| US-PLAN-12 | Gérer les grilles horaires et désigner la grille active | 5 | NON TROUVÉ | | | |

## Sprint 3 — 11 stories

| Code | Titre | Points | Commit de clôture | Porteur | Second | Observations |
|---|---|---|---|---|---|---|
| US-PLAN-05 | Modifier manuellement une affectation | 8 | `c7ace31` + `97e5cf7` | | | Deux commits : `c7ace31` (04/10, modification manuelle et avenant), `97e5cf7` (07/10, ajout manuel et périodes bloquantes — « fin prompt 42 partie 1 ») |
| US-PLAN-06 | Regrouper plusieurs brigades sur une même séance | 5 | `031ea98` | | | |
| US-PLAN-09 | Traiter une indisponibilité déclarée | 5 | `d5c4b51` | | | |
| US-VAL-03 | Gérer les états du programme | 5 | `04c3465` | | | |
| US-VAL-01 | Soumettre un programme à validation | 3 | `335d257` | | | Porte aussi le code d'écran d'US-VAL-04 (voir P-41, `docs/suivi/PROBLEMES.md`) |
| US-VAL-02 | Valider ou rejeter un programme | 5 | `c51b353` | | | |
| US-VAL-04 | Empêcher l'affichage d'un programme non validé | 2 | `a2fae81` | | | **Cas P-41** : le code d'écran de cette story est porté par `335d257` (commit d'US-VAL-01, `git add` ayant stagé tout le paquetage) — `a2fae81` est le commit qui cite littéralement « US-VAL-04 » (tests, note de clôture, D-234). Les deux hashes sont donnés pour que l'arbitrage reste au binôme |
| US-EVAL-01 | Créer une évaluation selon son type | 5 | `a6df84b` + `f5ecb2a` | | | `f5ecb2a` = « chore(suivi): cloture US-EVAL-01 » |
| US-EVAL-02 | Saisir la date d'un examen final | 2 | `3b91c89` | | | |
| US-EVAL-03 | Enregistrer les sujets transmis et sélectionner celui retenu | 5 | `705ac44` + `497ce01` | | | `497ce01` aligne l'heure de clôture sur `705ac44` |
| US-EVAL-04 | Organiser une épreuve | 5 | `4b6dbd2` | | | Titre du commit : « ... clôture US-EVAL-04 » |

## Sprint 4 — 14 stories

| Code | Titre | Points | Commit de clôture | Porteur | Second | Observations |
|---|---|---|---|---|---|---|
| US-SUI-05 | Déclarer la non-exécution d'une séance | 2 | `0f6d63a` | | | |
| US-SUI-01 | Consulter le rapprochement prescrit et réalisé | 5 | `987201c` | | | |
| US-SUI-06 | Éditer la progression réalisée hebdomadaire | 3 | `bddf365` | | | |
| US-EVAL-05 | Saisir et vérifier les notes | 5 | `0a03465` | | | |
| US-EVAL-06 | Calculer moyennes et classement | 5 | `297171c` | | | |
| US-EVAL-07 | Générer les procès-verbaux de résultats | 5 | `3b0609e` | | | |
| US-PLAN-07 | Signaler les écarts de volume horaire | 3 | `10c5fa5` | | | |
| US-VAL-05 | Consulter les programmes et l'historique des validations | 5 | `f2f2745` | | | |
| US-SES-09 | Clôturer une session | 3 | `0e5246a` | | | |
| US-SUI-02 | Être alerté des écarts significatifs | 3 | `7570b33` | | | |
| US-SUI-03 | Consulter le tableau de bord des formations | 5 | `101146a` | | | |
| US-INS-04 | Consulter la charge d'un instructeur | 3 | `567526c` | | | |
| US-REF-09 | Historiser les modifications du référentiel | 3 | `81a1dcb` | | | |
| US-PLAN-11 | Dupliquer un programme hebdomadaire | 5 | `6527068` | | | |

## Contrôle de cohérence

**52 lignes : 15 + 12 + 11 + 14.** Confirmé par comptage des quatre
tableaux ci-dessus.

**Codes que `git log` n'a pas retrouvés littéralement (17) :** US-ADM-01,
US-ADM-02, US-ADM-04, US-REF-00, US-REF-03 (livraison d'origine —
mentionné seulement par un correctif du sprint 4), US-REF-04, US-REF-05,
US-INS-02, US-SES-01, US-SES-02, US-SES-04, US-SES-05, US-SES-07,
US-INS-03, US-PLAN-01, US-PLAN-03, US-PLAN-12. Tous appartiennent aux
sprints 1 et 2, antérieurs à l'adoption systématique de la convention
« citer le code dans le message de commit » — visible dans l'historique
lui-même (les tout premiers commits du dépôt ne citent aucun code,
contrairement aux sprints 3 et 4). Aucune de ces stories n'est en doute
sur sa livraison : chacune est cochée dans son `sprint-N.md` et son code
existe dans le dépôt — seul le commit qui l'a close ne la cite pas par son
identifiant.

**Rappel : les colonnes Porteur et Second attendent le binôme.** Rien dans
le dépôt ne permet de les remplir de façon fiable.
