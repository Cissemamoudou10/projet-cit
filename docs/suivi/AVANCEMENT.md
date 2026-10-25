# Avancement général

*Récapitulatif court. Le détail vit dans les fichiers de sprint.*

**Dernière mise à jour : 25 octobre 2026 (prompt 50).** Le développement est
clos depuis le 20 octobre (jalon J3, prompt 49, étiquette
`j3-fin-developpement`) : 52 stories, 224 points, cent pour cent du
périmètre planifié hors réserve, sur quatre sprints. La phase 6 (tests et
recette) s'ouvre le 26 octobre et s'achève au jalon C3 du 2 novembre ; le
déploiement s'achève au jalon C4 du 10 novembre. Le paragraphe du
2 octobre qu'il remplaçait est désormais périmé — le détail des sprints 1
à 4 reste dans les sections « Sprints » et les fichiers `sprint-N.md`.

## Où nous en sommes

| Phase | Période | État |
|---|---|---|
| 1 — Initiation | 27/07 – 01/08 | Close |
| 2 — Spécification | 03/08 – 14/08 | Close |
| 3 — Planification détaillée | 17/08 – 20/08 | Close |
| 4 — Analyse et conception | 20/08 – 30/08 | **Close** — 7 livrables, 23 figures, jalon J1 franchi |
| 5 — Développement | 31/08 – 24/10 | **Close** — J3 atteint le 20/10, quatre jours d'avance |
| 6 — Tests et recette | 26/10 – 02/11 | **En cours à partir du 26/10**, jalon C3 le 02/11 |
| 7 — Déploiement | 03/11 – 10/11 | Jalon C4 le 10/11 |
| 8 — Mémoire et soutenance | 11/11 – 25/12 | À venir |

## Sprints

| Sprint | Période | Stories | Points | Livrées | Jalon |
|---|---|---|---|---|---|
| 1 | 31/08 – 12/09 | 15 | 58 | 15 | C1 |
| 2 | 14/09 – 26/09 | 12 | 61 | **12** | **C2 — prononcé le 30/09, en retard** |
| 3 | 28/09 – 10/10 | 11 | 50 | **11** | J2 |
| 4 | 12/10 – 24/10 | 14 | 55 | **14** | **J3 — atteint le 20/10, quatre jours à l'avance** |
| Réserve | conditionnel | 9 | 39 | 0 | — |

**Périmètre total (backlog v10, 10/10) :** 61 stories, 263 points. 61 besoins
fonctionnels. Sprint 4 recompté par le backlog v10 (prompt 44) : 15 → 14
stories, 61 → 55 points — US-PLAN-08 déclassée en réserve (risque R6) et
US-EVAL-11 (nouvelle en v10) affectée directement à la réserve, voir
`docs/suivi/reserve.md`. Sprint 2 : périmètre entier livré (12/12 stories,
61/61 points), plus l'étude de faisabilité du solveur (Prompt 32, hors
points chiffrés).

## Indicateurs

| Indicateur | Valeur | Cible |
|---|---|---|
| Stories livrées | **52 / 52 planifiées** | — |
| Points livrés | **224 / 224 planifiés** | — |
| Vélocité mesurée | **Définitivement non mesurée** — aucune heure humaine n'a été relevée sur les 52 stories du projet (registre v8, R23). Quatre sprints livrés à 100 % de leur estimation en points est la seule mesure validée | aucune — un relevé rétrospectif déclaratif reste possible pour le mémoire, jamais une mesure contemporaine |
| Clé de conversion | 1,3 h/point, **non révisée, ne le sera plus en cours de projet** — aucune mesure fiable ne l'a jamais justifiée (registre v8, R23) | à présenter au mémoire comme hypothèse jamais vérifiée, avec sa cause |
| Marge avant dépôt | **9 jours ouvrés, plus l'avance gagnée au J3** (registre v8, O1) | La valeur « 14 jours ouvrés, intacte » affichée jusqu'ici était périmée depuis le 30/09, date à laquelle le registre v6 l'avait déjà ramenée à 9 — jamais répercutée ici. Trois jours d'avance supplémentaires gagnés au J3 (21 au 23 octobre), employés à la clôture et au démarrage de la recette. |

**Recalcul daté (2026-10-13, prompt 45, Temps 1.4).** Points livrés : 169
(avant le prompt 44) + 7 (US-SUI-05, 2 pts ; US-SUI-01, 5 pts) = **176**.
Dénominateur recalculé sur le périmètre v10 hors réserve : 263 − 39 = **224**
points, 61 − 9 = **52** stories (voir « Sprints » et `docs/suivi/reserve.md`
ci-dessus). Stories livrées : 15 (sprint 1) + 12 (sprint 2) + 10 (sprint 3,
ligne non revérifiée ici) + 2 (sprint 4, US-SUI-05/US-SUI-01) = **39**.

**Recalcul daté (2026-10-16, prompt 45, Temps 2).** US-SUI-06 (progression
réalisée hebdomadaire, 3 pts) livrée. Points livrés : 176 + 3 = **179** / 224.
Stories livrées : 39 + 1 = **40** / 52. Sprint 4 : 3 / 14 stories, 10 / 55
points.

**Recalcul daté (2026-10-17, prompt 46, point 1).** US-EVAL-05 (saisie et
vérification des notes, 5 pts) livrée. Points livrés : 179 + 5 = **184** / 224.
Stories livrées : 40 + 1 = **41** / 52. Sprint 4 : 4 / 14 stories, 15 / 55
points.

**Recalcul daté (2026-10-17, prompt 46, point 2).** US-EVAL-06 (moyennes et
classement, 5 pts) livrée. Points livrés : 184 + 5 = **189** / 224.
Stories livrées : 41 + 1 = **42** / 52. Sprint 4 : 5 / 14 stories, 20 / 55
points.

**Recalcul daté (2026-10-17, prompt 46, point 3).** US-EVAL-07 (procès-verbaux
de résultats, 5 pts) livrée — dernière story Must du projet. Points livrés :
189 + 5 = **194** / 224. Stories livrées : 42 + 1 = **43** / 52. Sprint 4 :
6 / 14 stories, 25 / 55 points. **Périmètre Must entier (194 points) livré.**

**Recalcul daté (2026-10-18/19, prompt 47).** Trois stories Should livrées :
US-PLAN-07 (écarts de volume horaire, 3 pts), US-VAL-05 (liste et historique
des programmes, 5 pts), US-SES-09 (clôture de session, 3 pts). Points
livrés : 194 + 3 + 5 + 3 = **205** / 224. Stories livrées : 43 + 3 = **46** /
52. Sprint 4 : 9 / 14 stories, 36 / 55 points. Point de décision du 21
octobre (§ « Ce qu'il faut surveiller ») non encore atteint à la livraison :
les cinq stories Should restantes du sprint 4 (US-SUI-02, US-SUI-03,
US-INS-04, US-REF-09, et le solde) restent à statuer à cette date. D-262
fermé par US-SES-09 (voir § reports ci-dessous). D-279 ouvre un arbitrage de
backlog non technique (chevauchement US-PLAN-07/US-SUI-02, à trancher par le
chef de projet — US-SUI-02 non décomptée ici tant que l'arbitrage n'est pas
rendu).

**Recalcul daté (2026-10-19, prompt 48, Temps 0 + Story 1).** D-279 fermée
par D-282 : US-SUI-02 reprend son périmètre propre (réalisé, en continu),
distinct d'US-PLAN-07 (programmé, avant soumission) — ni fusion ni retrait.
US-SUI-02 (alertes d'écart significatif, 3 pts) livrée. Points livrés :
205 + 3 = **208** / 224. Stories livrées : 46 + 1 = **47** / 52. Sprint 4 :
10 / 14 stories, 39 / 55 points. Point de décision du 21 octobre non encore
atteint à la livraison : quatre stories Should restent à statuer
(US-SUI-03, US-INS-04, US-PLAN-11, US-REF-09).

**Recalcul daté (2026-10-19, prompt 48, Story 2).** US-SUI-03 (tableau de
bord des formations, 5 pts) livrée. D-284 consignée (B6 : accès à quatre
profils, la matrice fait foi, le critère n'en citait que deux). Points
livrés : 208 + 5 = **213** / 224. Stories livrées : 47 + 1 = **48** / 52.
Sprint 4 : 11 / 14 stories, 44 / 55 points. Point de décision du 21 octobre
non encore atteint : trois stories Should restent à statuer (US-INS-04,
US-PLAN-11, US-REF-09).

**Recalcul daté (2026-10-19, prompt 48, Story 3).** US-INS-04 (charge
d'enseignement d'un instructeur, 3 pts) livrée. Hypothèse à confirmer avec
le terrain : seuil de charge hebdomadaire par défaut à 24 h/semaine (C2),
aucun livrable ne la fixe. Points livrés : 213 + 3 = **216** / 224. Stories
livrées : 48 + 1 = **49** / 52. Sprint 4 : 12 / 14 stories, 47 / 55 points.
Point de décision du 21 octobre non encore atteint : deux stories Should
restent à statuer (US-PLAN-11, US-REF-09).

**Recalcul daté (2026-10-19, prompt 48, Story 4).** US-PLAN-11 (duplication
d'un programme hebdomadaire, 5 pts) livrée — la plus complexe des cinq
stories du prompt. Aucune décision consignée (la garde de la cible
réutilise l'événement `GENERER` existant, sans toucher `TRANSITIONS` ni
`ETA-01_table_transitions.md`) ; P-50 consignée (écart de décompte
préexistant, sans rapport avec cette story). Points livrés : 216 + 5 =
**221** / 224. Stories livrées : 49 + 1 = **50** / 52. Sprint 4 :
13 / 14 stories, 52 / 55 points. Point de décision du 21 octobre non
encore atteint : une seule story Should reste à statuer (US-REF-09).

**Recalcul daté (2026-10-19/20, prompt 48, Story 5).** US-REF-09
(historique des modifications du référentiel, 3 pts) livrée — dernière
story du prompt 48. D-285 (limite au renommage) et D-286 (E4, aucune
reprise rétroactive) consignées. Points livrés : 221 + 3 = **224** / 224.
Stories livrées : 50 + 1 = **51** / 52. **Sprint 4 : 14 / 14 stories,
55 / 55 points — périmètre complet livré avant le point de décision du
21 octobre**, aucune story Should n'est passée en réserve.

**Recompte daté (2026-10-20, prompt 49, Temps 5.3) — correction d'un
écart d'une story.** Le recalcul du 2026-10-13 (ci-dessus) portait le
sprint 3 à « 10, ligne non revérifiée » sans jamais être recontrôlé
depuis. Recompte par un second angle indépendant (`.claude/rules/
tests.md`, « vérifier une absence ») : les onze cases du sprint 3
(`docs/suivi/sprint-3.md`) sont cochées `[x]`, et les onze codes de
story (US-PLAN-05, 06, 09 ; US-VAL-03, 01, 02, 04 ; US-EVAL-01 à 04)
apparaissent chacun dans au moins un commit de `master` — sprint 3 est
bien **11 / 11**, pas 10. L'écart n'était pas une story manquante mais un
compte jamais revérifié après l'avoir signalé comme tel. Total général
corrigé : 15 (sprint 1) + 12 (sprint 2) + 11 (sprint 3) + 14 (sprint 4) =
**52 / 52 stories**, 224 / 224 points — périmètre v10 hors réserve
intégralement livré. Confirmé indépendamment pour le sprint 4 par
`git log` (les quatorze codes de story y figurent chacun).

## Ce qu'il faut surveiller

**État au 25 octobre 2026 (prompt 50), d'après le registre des risques v8
du 23/10 (`docs/livrables/09_Registre_risques_v8_2026-10-23.md`), déposé
dans le dépôt. Remplace entièrement les points échus de ce même
paragraphe — rien d'autre dans ce fichier n'est réécrit.**

**Points de décision des 7 et 21 octobre — tous deux tenus.** Le 7 octobre :
US-VAL-01, US-VAL-02 et US-VAL-04 livrées avant l'échéance (voir « État
consolidé des reports » ci-dessous pour le détail). Le 21 octobre : aucune
story *Should* du sprint 4 n'a dû passer en réserve, le périmètre entier
étant déjà livré au prompt 48, avant l'échéance.

**R1 et R10 — réponses par défaut retenues le 16/10 (D-268, relu dans
`DECISIONS.md`).** Le circuit de validation ETA-01, construit sur les
réponses par défaut aux quatre questions posées aux cellules, fait
référence depuis cette date. Toute réponse tardive des cellules, si elle
diverge, sera traitée comme une demande d'évolution (R11), arbitrée
explicitement — jamais comme une correction due. Les deux risques
s'éteindront à la fin de la phase 6 (registre v8, § 6), avec ou sans séance
de recette.

**R6 — éteint (D-289, relu dans `DECISIONS.md`).** Le réexamen d'US-PLAN-08
tenu le 20 octobre maintient le déclassement du solveur ; le développement
étant clos, la question de faisabilité n'a plus d'objet.

**Risques actifs de la phase 6, d'après le registre v8 :**
- **R16, critique (12)** — 35 des 36 décisions du sprint 4 portent la
  mention « porteur non renseigné » : la trace de contribution individuelle
  s'est dégradée au lieu de se corriger. Mesure demandée avant le
  2 novembre : attribution rétrospective des porteurs — voir Temps 4 de ce
  prompt, `docs/suivi/PORTEURS-RETROSPECTIF.md`.
- **R29, nouveau (9)** — recette conduite sans les utilisateurs des
  cellules : la conformité peut être vérifiée par le binôme, l'adéquation
  au besoin ne peut l'être que par une séance avec les cellules, jamais
  obtenue à échéance depuis le 30 septembre.
- **R22, en hausse (6)** — impression du programme hebdomadaire, anomalie
  n° 1 du cahier de recette : l'exemplaire réel produit à la clôture du
  sprint 4 (D-291) déborde de la page A4 dès le troisième créneau, un
  défaut qu'aucun test automatisé ne peut voir.

**Décision du chef de projet du 25/10 (D-295, relue dans `DECISIONS.md`) —
déploiement sur machine virtuelle isolée.** Aucune installation sur un
serveur du CIT n'est envisagée pour ce projet. Le déploiement de la
phase 7 se fait sur une machine virtuelle isolée, hors ligne, reproduisant
le serveur du réseau interne, avec le protocole déjà éprouvé le
7 septembre (`INSTALLATION-HORS-LIGNE.md`). **R15 devient sans objet.** La
procédure livrée doit rester applicable telle quelle à un serveur du
centre.

## État consolidé des reports de critères — revue de clôture du sprint 2, prononcée le 30 septembre

**Mise à jour du 2026-09-30 (Prompt 33, bloc B).** Réécriture complète de
cette section : la précédente s'arrêtait au 2026-09-16 et comptait par
**décision**, pas par **critère/volet** — deux unités différentes, jamais
comparables terme à terme (voir plus bas). Reprise intégrale sur le code réel
d'aujourd'hui, jamais sur la déclaration d'une décision. Deux corrections
majeures par rapport à la dernière version :

- **D-23 était marqué « Ouvert — Session n'existe pas encore »**. C'est faux
  depuis US-SES-01 (`Session` existe, `Session.formation` en `PROTECT`,
  `app/organisation/models.py`). **Fermé**, trois tests réels
  (`app/organisation/tests/test_protection_formation.py`), dont un par le
  vrai cycle HTTP (leçon D-50) et un qui prouve que le `PROTECT` s'applique
  même à une session **clôturée**, pas seulement ouverte. Ce dernier point
  révèle un écart de libellé (D-69) : le critère 4 d'US-REF-01 ne parle que
  de « sessions ouvertes » — assumé, à corriger dans le backlog, voir
  `docs/suivi/ECARTS-LIVRABLES-SPRINT-2.md`.
- **Deux reports créés pendant le sprint 2 n'avaient jamais été ajoutés à ce
  tableau**, alors que les décisions qui les ouvrent (D-91, D-83, toutes deux
  du 2026-09-11) le demandaient explicitement elles-mêmes. Retrouvés en
  parcourant `DECISIONS.md` en entier plutôt qu'en se fiant à ce tableau :
  **D-91** (salle attitrée reprise par défaut à la génération, R2-GEN-07)
  était déjà fermé dans les faits, jamais coché ici. **D-83** (brigade au
  programme en cours non supprimable, R2-NRG-04/05) avait son mécanisme posé
  (`LigneProgramme.brigade` en `PROTECT`, US-PLAN-04) mais **aucun test ne
  l'exerçait par le vrai chemin de service** — l'ancien test de
  `organisation/tests/test_brigade.py` ne prouvait qu'une absence
  d'opposant, écrit avant que `LigneProgramme` existe. Par la règle même de
  ce bloc (« un report déclaré refermé sans test nommé est réputé ouvert »),
  D-83 était donc en réalité **encore ouvert** malgré son mécanisme déjà en
  place. Comblé ce même jour :
  `planification.tests.test_modeles::test_d83_suppression_brigade_au_
  programme_refusee_par_le_vrai_chemin_de_service`, qui appelle
  `ServiceBrigade.supprimer` (le chemin réel de l'écran), pas seulement
  `.delete()`. **Fermé.**
- **Un troisième report jamais ajouté, celui-là réellement ouvert** : D-108
  (volume horaire dispensé signalé à l'affectation d'un stagiaire, A3,
  US-SES-06) — aucune trace de « volume dispensé » dans `app/organisation/`,
  reste entièrement à faire. Pointe désormais vers US-SUI-01 (sprint 4), le
  volet séances d'US-PLAN-03 existant mais rien ne l'exploitant pour ce
  signal.

| Report | Critère(s)/volet | Story d'origine | Referme (prévu ou réel) | État vérifié le 2026-09-30 |
|---|---|---|---|---|
| D-22 | 2, 4 (type de la formation) | US-REF-00 | US-REF-01 | Fermé (sprint 1) |
| D-30 | 3 (fiche affiche les formations utilisatrices) | US-REF-02 | US-REF-03 | Fermé (sprint 1, D-64) |
| D-30 | 5 (suppression bloquée) | US-REF-02 | US-REF-03 / US-INS-02 | Fermé (sprint 1) |
| D-35 | 6/RG-07, source prérequis | US-REF-03 | US-REF-06 | Fermé (sprint 1, D-40) |
| D-35 | 6/RG-07, source séance | US-REF-03 | US-PLAN-03/04 (sprint 2) | **Fermé le 2026-09-16** — `test_c4_matiere_volume_epuise_et_matiere_prerequis_inacheve_motifs_distincts` |
| **D-35** | 6/RG-07, source évaluation | US-REF-03 | US-EVAL-01 (sprint 3) | **Fermé le 2026-10-01** — `test_g1_retirer_un_element_porteur_d_une_evaluation_refuse_evaluation_enumeree` (`evaluations.tests.test_reports`), `Evaluation.element_referentiel` en `PROTECT`, refus générique déjà porté par `ServiceReferentiel.retirer` (`decrire_opposants`), aucun code à ajouter |
| **D-23** | 4 (session bloque la suppression d'une formation) | US-REF-01 | US-SES-01 (sprint 2) | **Fermé — corrigé le 2026-09-30**, était marqué à tort « Ouvert ». `test_d1_formation_portant_une_session_ouverte_ne_peut_etre_supprimee`, `test_d2_meme_refus_par_le_vrai_cycle_http_...`, `test_d3_formation_portant_une_session_cloturee_est_aussi_protegee` (`app/organisation/tests/test_protection_formation.py`). Écart de libellé signalé : D-69 |
| D-34 | 3, 4 (catégorie de lieu au moteur) | US-REF-04 | moteur de génération (sprint 2) | Fermé le 2026-09-16 — `test_generation_lieux.py` |
| D-39 | 3, 4, volet moteur (prérequis exploités par le moteur) | US-REF-06 | moteur de génération (sprint 2) | Fermé le 2026-09-16 |
| D-39 | 3, 4, volet saisie manuelle | US-REF-06 | US-PLAN-05 (sprint 3) | **Fermé — jamais marqué, découvert en reparcourant le sprint au prompt 43** : `test_e_prerequis_non_acheve_refuse_une_modification_manuelle` (`modification.py::_verifier_contraintes`, réutilise `ServiceContraintes`/RG-39) |
| D-45 | 4 (instructeur affecté à un programme en cours) | US-INS-01 | séance programmée (sprint 2) | Fermé le 2026-09-15 — `test_a9_suppression_instructeur_portant_une_seance_refusee` |
| D-51 | E1 (retrait de qualification, instructeur à séances futures) | US-INS-02 | séance programmée (sprint 2) | Fermé le 2026-09-15 — reconfirmé 2026-09-30 : `test_retrait_refuse_si_une_seance_future_existe` (`app/planification/tests/test_resolveur_qualification.py`) teste bien le RETRAIT de qualification, pas le `PROTECT` sur `Seance.instructeur` |
| D-54 | 4, volet brigade (lieu affecté à une brigade) | US-PLAN-02 | US-SES-03 (sprint 2) | Fermé le 2026-09-11 |
| D-54 | 4, volet séance (lieu affecté à une séance) | US-PLAN-02 | séance programmée (sprint 2) | Fermé le 2026-09-15 |
| **D-91** | R2-GEN-07 (salle attitrée reprise par défaut à la génération) | US-SES-03 | moteur de génération (sprint 2) | **Fermé — jamais ajouté à ce tableau avant le 2026-09-30**, découvert en relisant `DECISIONS.md` en entier. `test_d1_matiere_salle_attitree_reprend_la_salle_de_la_brigade` (`test_generation_lieux.py`) |
| **D-83** | R2-NRG-04/05 (brigade au programme en cours non supprimable) | US-SES-02 | séance programmée (sprint 2) | **Fermé le 2026-09-30** — mécanisme posé depuis US-PLAN-04 mais jamais testé par le vrai chemin de service jusqu'à ce jour ; comblé (voir ci-dessus) |
| **D-108** | A3 (volume horaire dispensé signalé à l'affectation) | US-SES-06 | US-SUI-01 (sprint 4) | **Fermé le 2026-10-13, prompt 44 Temps 3 (R6), commit `987201c`** — `ResolveurVolumeRealiseBrigade`, avertissement non bloquant à l'affectation ; ligne jamais mise à jour depuis, corrigée au prompt 49, Temps 5.2 |
| D-119 | 4, RG-25 (indisponibilité, contrainte dure) | US-INS-03 | US-PLAN-04 (sprint 2) | Fermé le 2026-09-15 |
| D-119 | 5, pts 4-5 (séances impactées par une indisponibilité) | US-INS-03 | US-PLAN-09 (sprint 3) | **Fermé le 2026-10-07** — I2/C1 (D-257), `seances_impactees_par_indisponibilite` |
| D-119 | A3, A4 (restriction extension, séances passées) | US-INS-03 | sprint 3 | **Fermé le 2026-10-07** — I6 (D-253) : une extension relit le même sélecteur, les séances passées en sont exclues par construction |
| D-121 | 5, RG-38 (exclusion des périodes bloquantes) | US-PLAN-01 | US-PLAN-03/04 (sprint 2) | Fermé le 2026-09-15 |
| D-121 | E2 (période bloquante recouvrant des séances programmées) | US-PLAN-01 | US-PLAN-05 (sprint 3) | **Fermé le 2026-10-07, prompt 42 partie 1, par D-245** — ligne jamais mise à jour depuis, corrigée en reparcourant le sprint au prompt 43 |
| D-121 | A3 (séances redevenues programmables) | US-PLAN-01 | sprint 3 | **Fermé le 2026-10-07, prompt 42 partie 1, par D-246** — ligne jamais mise à jour depuis, corrigée en reparcourant le sprint au prompt 43 |
| D-133 | 6 (changer de grille active ne touche pas les séances passées) | US-PLAN-12 | US-PLAN-03 (sprint 2) | Fermé le 2026-09-16 |
| D-133 | RG-64 (relation facultative séance↔créneau type) | US-PLAN-12 | *aucune story assignée* | **Tranché le 2026-10-20, prompt 49 Temps 4c/5.1 (D-288, D-293)** — limite assumée et consignée, jamais implantée, sans échéance ; plus une orpheline silencieuse |
| D-133 | refus de générer sans grille active (E6) | US-PLAN-12 | US-PLAN-03 (sprint 2) | Fermé le 2026-09-16 |
| **D-171** | RG-39 a) révisée (volume programmé compte aussi REJETÉ) | US-PLAN-04 (D-140) | US-VAL-03 (sprint 3) | **Fermé le 2026-10-04, prompt 39, par V7 (D-225)** — créé le 2026-09-30, prompt 34 |
| **D-172** | lecture du programme par la cellule pédagogique (`programme_validation_lecture`) | US-PLAN-03 (D-154) | US-VAL-02 (sprint 3) | **Fermé le 2026-10-04, prompt 40, par US-VAL-02 (D-231)** — créé le 2026-09-30, prompt 34 |
| **D-181** | suppression d'une évaluation, et de sa séance verrouillée — jamais hors du service d'évaluation | US-EVAL-01 | US-PLAN-05 (sprint 3) | **Fermé le 2026-10-04, prompt 41, par D-240** (M8, D2, D3) — créé le 2026-10-01, prompt 35 ; ligne jamais mise à jour depuis, corrigée en reparcourant le sprint au prompt 43 |
| **D-182** | mesure de l'écart de progression entre brigades (A8, E2, forme simplifiée retenue) | US-EVAL-01 | *aucune story assignée* | **Ouvert, orphelin — créé le 2026-10-01, prompt 35**, à arbitrer au backlog v10 |
| **D-170** | insertion d'un contrôle refusée si le programme de la semaine est SOUMIS, VALIDÉ ou AFFICHÉ | US-EVAL-01 | US-VAL-03 (sprint 3) | **Fermé le 2026-10-04, prompt 39, par C4 (D-221)** — créé le 2026-10-01, prompt 35, cas à ajouter à l'oracle `ETA-01_table_transitions.md` quand la garde RG-41 (D-170) existera |
| **D-193** | une organisation d'épreuve devra être revérifiée quand la date d'une certificative change | US-EVAL-02 | US-EVAL-04 | **Fermé le 2026-10-04, prompt 38, par les tests E1 à E3 (`test_organisation_services.py`) : changement de date signalé, jamais refusé** : `modifier_date_certificative` ne touche à rien d'une organisation d'épreuve, qui n'existe pas encore (US-EVAL-04, sprint 3) — à vérifier dès que cette story existe |
| **D-202** | la borne RG-51 (jour de l'épreuve) devra se resserrer à l'heure de l'épreuve | US-EVAL-03 | US-EVAL-04 | **Fermé le 2026-10-03, prompt 38, par décision (A10, D-209)** : la borne reste le jour entier, à dessein, plus stricte que celle de l'organisation |
| **C9** (D-205) | aucune certificative organisée sans sujet retenu — garde `ServiceSujet.sujet_retenu`, à brancher au refus de l'organisation | US-EVAL-03 (c.7) | US-EVAL-04 | **Fermé le 2026-10-04 par A1 (D-208) : organiser sans sujet, prête seulement avec un sujet retenu (`est_prete`). Ouvert le 2026-10-02, prompt 37, absent de ce tableau jusqu'au 2026-10-03. Réinterprété par A1 du prompt 38 (D-208) : on organise sans sujet, l'épreuve n'est prête qu'avec un sujet retenu. ** |
| **D-212** (badge « à vérifier ») | après changement de date, une épreuve porte « à vérifier » dans la liste (A9, lecture du journal) | US-EVAL-04 (A9) | *aucune story assignée* | **Ouvert, sans story — à arbitrer au backlog v10** : non livré (aucun code, aucun test E3) |
| **D-215** (badge de liste sur la complétude) | le badge « non prête » de la liste doit porter la complétude (A4), en requête bornée pour toute la liste | US-EVAL-04 (A4) | *aucune story assignée* | **Ouvert, sans story — à arbitrer au backlog v10** : le badge porte encore sur le sujet seul (`evaluations_non_pretes`) |
| **Présélection** (ECARTS 25) | la présélection de génération (`construire_cases`) ignore les épreuves : une case sur le lieu d'une épreuve est engendrée puis refusée par RG-37 | US-EVAL-04 (A6) | *aucune story assignée* | **Mesuré le 2026-10-20, prompt 49 Temps 4a (D-290)** : 1 candidate perdue sur le jeu mesuré, aucune requête SQL supplémentaire — reste ouvert, dette sans échéance, plus un coût inconnu |
| **Lecture sans garde** (ECARTS 26) | convention des lectures | US-EVAL-04 (F4) | — | **Fermé le 2026-10-04 par D-219** : convention écrite, exceptions corrigées, test d'architecture |

### Compte final, vérifié le 2026-10-02 (mis à jour, prompt 37)

Recompté au prompt 36 : aucun report fermé, un report nouveau (D-193).
Recompté à nouveau ici, après US-EVAL-03 (prompt 37, Temps 2) : un second
report nouveau s'ouvre (D-202, vers US-EVAL-04 — même story que D-193,
deux reports distincts). D-121 E2 reste ouvert, complété d'un renvoi vers
le sélecteur posé à US-EVAL-02 (D-191) — l'arbitrage lui-même reste entier
à US-PLAN-05, ce renvoi n'en change pas le compte. Net : treize reports
avant ce prompt, plus un créé — **quatorze ouverts aujourd'hui**.

| | Compte |
|---|---|
| **Ouverts aujourd'hui** | **14** : D-39(saisie manuelle), D-119(pts 4-5), D-119(A3/A4), D-121(E2), D-121(A3), D-133(RG-64, orpheline), D-108, D-171, D-172, D-170(insertion contrôle), D-181, D-182, D-193, D-202 |
| **Refermés pendant le sprint 2** | **14** : D-23, D-34, D-35(séance), D-39(moteur), D-45, D-51, D-54(brigade), D-54(séance), D-91, D-83, D-119(RG-36), D-121(RG-38), D-133(constat d'absence), D-133(E6) |
| **Créés pendant le sprint 2** | **12** : D-91, D-83, D-108, D-119(×3), D-121(×3), D-133(×3) |
| **Créés pendant le sprint 3, à ce jour (prompts 34 à 37)** | **6** : D-171, D-172, D-181, D-182, D-193, D-202 — D-170 (insertion d'un contrôle) rattache un report à une décision déjà existante (ETA-01, prompt 34), pas une décision de plus |
| **Refermés pendant le sprint 3, à ce jour** | **1** : D-35 (volet évaluation, prompt 35) |

**Écart avec le décompte donné en revue du sprint 1** (« neuf reports, trois
refermés, six des sept ouverts se referment au sprint 2 ») : ce chiffre
comptait par **décision** (15 décisions distinctes ouvrent un report), le
tableau ci-dessus compte par **critère/volet** (26 lignes) — deux unités
différentes, jamais comparables terme à terme. Le chiffre de revue était de
toute façon interne-incohérent (9 − 3 = 6, pas 7) ; à signaler en séance,
pas à corriger silencieusement a posteriori.

### Recompte à la clôture d'US-EVAL-04, le 2026-10-04

Ferment : **D-193** (tests E1 à E3, changement de date signalé) et **C9** (A1, D-208 : organiser sans sujet). **D-202** avait déjà été fermé par D-209. Ouvrent, sans story : **D-212** (badge « à vérifier »), **D-215** (badge de liste sur la complétude), la **présélection** qui ignore les épreuves (ECARTS 25, dette à traiter au sprint 4) et la **lecture sans garde** (ECARTS 26) est fermée par D-219.

Net : quatorze ouverts avant cette clôture, moins deux fermés, plus quatre ouverts — **seize ouverts à la clôture**, puis **quinze** après la fermeture de l'écart 26 (D-219, qui n'est pas un report mais un écart).

### Recompte à la clôture d'US-VAL-03, le 2026-10-04

Ferment : **D-170** (insertion d'un contrôle refusée hors brouillon, C4, D-221) et **D-171** (volume programmé qui compte les rejetés, V7, D-225). Aucun report ne s'ouvre. Net : quinze ouverts avant cette clôture, moins deux fermés — **treize ouverts à la clôture**.

### Recompte à la clôture d'US-VAL-02, le 2026-10-04

Ferme : **D-172** (lecture du programme par la pédagogique, D-231). Aucun report ne s'ouvre. Net : **douze ouverts**.

### Recompte d'US-PLAN-05 (partielle), le 2026-10-04

Ferme : **D-181** (suppression d'une évaluation et de sa séance verrouillée, D-240). Reste ouvert : **D-121** (E2 et A3, périodes bloquantes, D-243). Net : **onze ouverts**.

### Recompte à la clôture d'US-PLAN-05, le 2026-10-07

Ferme : **D-121** (E2 par D-245, A3 par D-246). Aucun report ne s'ouvre. Net : **dix ouverts**.

### Recompte à la clôture d'US-PLAN-09, le 2026-10-07

Ferme : **D-119** (ses deux volets — pts 4-5 par D-257, A3/A4 par D-253), compté comme une seule décision qui se referme, même convention que D-121 ci-dessus. Aucun report ne s'ouvre. Net : dix ouverts avant cette clôture, moins un fermé — **neuf ouverts**.

### Recompte intégral du sprint 3, en reparcourant `DECISIONS.md` en entier (D-165 à D-258), le 2026-10-10

Prompt 43, § B1 — leçon 6 du sprint 2 : une chaîne de recomptes locaux (ci-dessus) peut se tromper si elle hérite d'une base déjà fausse sans jamais la revérifier contre la source. En relisant chaque décision du sprint une à une plutôt qu'en continuant la chaîne : **deux fermetures jamais décomptées**, toutes deux antérieures même à la clôture d'US-PLAN-05 (donc présentes dans tous les recomptes ci-dessus sans que personne ne les retire) :
- **D-39** (volet saisie manuelle, critère 4 US-REF-06) : fermé par la livraison d'US-PLAN-05 (`test_e_prerequis_non_acheve_refuse_une_modification_manuelle`), jamais marqué.
- **D-181** (suppression d'une évaluation) : fermé le 2026-10-04 par **D-240** (US-PLAN-05, M8), jamais marqué — la fermeture est antérieure à la partielle du 2026-10-04 elle-même.

Aucune autre ligne du tableau ci-dessus n'est en défaut : D-119, D-121 (les deux volets), D-171, D-172, D-170, D-193, D-202 sont bien fermés et désormais marqués comme tels ; D-108, D-133, D-182, D-212, D-215 et la présélection (ECARTS 25) sont bien de vrais reports orphelins ou de sprint 4, à raison hors du périmètre de ce sprint.

**Net réel, vérifié à la clôture du sprint 3 : six reports ouverts**, tous hors du périmètre des onze stories livrées (aucune story assignée, ou assignée au sprint 4) :

| Report | Objet | Story cible |
|---|---|---|
| D-108 | A3, volume horaire dispensé signalé à l'affectation | US-SUI-01 (sprint 4) |
| D-133 | RG-64, relation facultative séance↔créneau type | *aucune, orpheline* |
| D-182 | mesure de l'écart de progression entre brigades | *aucune, backlog v10* |
| D-212 | badge « à vérifier » après changement de date | *aucune, backlog v10* |
| D-215 | badge de liste sur la complétude | *aucune, backlog v10* |
| Présélection (ECARTS 25) | la présélection de génération ignore les épreuves | *aucune, dette sprint 4* |

La ligne « Ouverts aujourd'hui » du prompt 37 comptait quatorze reports. Trois d'entre eux (D-108, D-133, D-182) étaient déjà orphelins ou hors sprint 3 à cette date, et le restent. Les onze autres (D-39, D-119 ×2, D-121 ×2, D-171, D-172, D-170, D-181, D-193, D-202) appartenaient tous au périmètre du sprint 3 et sont désormais tous fermés. Trois reports supplémentaires se sont ouverts après le prompt 37, pendant US-EVAL-04 (D-212, D-215, Présélection/ECARTS 25) — eux aussi hors du périmètre des stories du sprint 3 (backlog v10 ou dette sprint 4). D'où les six ouverts du tableau ci-dessus : 3 + 3, aucun n'appartenant au périmètre livré.

### Report ouvert pendant US-SUI-05, le 2026-10-12 (prompt 44, Temps 2)

**D-262** : `ServiceSuivi._session_cloturee()` retourne toujours `False` — l'annulation d'une non-exécution reste réversible sans condition tant qu'US-SES-09 (clôture de session, même sprint) n'existe pas. À compléter par US-SES-09 : prendre la ligne en paramètre, remonter à sa session, refuser l'annulation si elle est clôturée.

| Report | Objet | Story cible |
|---|---|---|
| D-262 | réversibilité de la non-exécution, conditionnée à la clôture de la session | US-SES-09 (sprint 4) |

Net : six reports ouverts avant US-SUI-05 (clôture du sprint 3), plus un nouveau — **sept ouverts** à ce jour.

### Recompte à la clôture d'US-SES-09, le 2026-10-19 (prompt 47, Temps 4)

Ferme : **D-262** — `ServiceSuivi._session_cloturee` lit désormais la vraie session via la brigade de la ligne et refuse l'annulation ET la déclaration d'une non-exécution sur une session clôturée (C4). Aucun report ne s'ouvre. Net : sept ouverts avant cette clôture, moins un fermé — **six ouverts**.

### Recompte à la clôture du sprint 4, prompt 49, Temps 5.2 (2026-10-20)

Vérification systématique des six reports ouverts à la clôture du sprint 3 (tableau ci-dessus), un par un, contre `DECISIONS.md` (D-259 à D-294) et `ECARTS-LIVRABLES-SPRINT-4.md` — pas une relecture de la seule tête de liste.

- **D-108** : **fermé**, mais jamais marqué dans ce fichier — `ResolveurVolumeRealiseBrigade` livré le 2026-10-13 avec US-SUI-01 (commit `987201c`, `heures-sprint-4.md` R6), corrigé ci-dessus.
- **D-133 / RG-64** : **fermé par décision, sans implantation** — D-288 (Temps 4c) puis D-293 (Temps 5.1) consignent la limite comme assumée, ligne corrigée ci-dessus.
- **Présélection (ECARTS 25)** : **fermé par décision, sans implantation** — D-290 (Temps 4a) mesure le coût (1 candidate perdue, aucune requête de plus), ligne corrigée ci-dessus.
- **D-182, D-212, D-215** : **toujours ouverts**, aucune mention dans `DECISIONS.md` ni `ECARTS-LIVRABLES-SPRINT-4.md` depuis la clôture du sprint 3 — confirmés orphelins, à arbitrer au backlog v10/v11 comme déjà noté.

**Net : trois reports ouverts à la clôture du sprint 4** (D-182, D-212, D-215), tous hors périmètre d'une story livrée, aucun n'appartenant au sprint 4 lui-même.

| Report | Objet | Destination |
|---|---|---|
| D-182 | mesure de l'écart de progression entre brigades | backlog v10, orphelin |
| D-212 | badge « à vérifier » après changement de date | backlog v10, orphelin |
| D-215 | badge de liste sur la complétude | backlog v10, orphelin |

Aucun nouveau report ne s'est ouvert pendant le sprint 4 au sens de ce tableau (les quatre décisions hors backlog du Temps 4 — D-288 à D-291 — et les trois de Temps 5.1 — D-292 à D-294 — ferment ou consignent, elles n'ouvrent rien de nouveau faute de story qui en dépendrait).

### Recompte du 25/10/2026 (prompt 50), d'après le backlog v11

Les trois reports comptés « orphelins » ci-dessus ne l'étaient pas : le
backlog v10 n'était simplement pas dans le dépôt au moment de ce recompte
(prompt 49) — exactement le défaut que corrige le Temps 1 du prompt 50
(copie du backlog dans le dépôt à chaque version, mesure v11, § 12).
Vérifié sur le texte intégral de `docs/livrables/
04_Backlog_produit_v11_2026-10-23.md` :

- **D-212** et **D-215** ne sont pas orphelins : ce sont les critères 2 et 1
  d'**US-EVAL-11** (« Suivre les épreuves à venir », Should, 3 pts),
  story nouvelle en version 10, en réserve — le backlog v11 le dit noir sur
  blanc (§ 9, note v11 : « les reports D-215... et D-212... sont exactement
  ses critères 1 et 2 »).
- **D-182** est classé **Won't** depuis le backlog v10 (§ 11.2, « hors
  périmètre de la version courante ») : « aucun livrable ne définit la
  mesure ni le seuil [...] le report D-182 est fermé par ce classement. »

**Net : aucun report orphelin.** La revue du sprint 4 (`REVUE-SPRINT-4.md`)
et le recompte ci-dessus en comptaient trois parce que le backlog n'était
pas dans le dépôt au moment où ils ont été écrits — voir l'addendum à
`REVUE-SPRINT-4.md` (prompt 50, Temps 5).

### Écart de numérotation, table de correspondance (proposition, backlog non touché)

| Code cité dans `DECISIONS.md` | Désigne réellement (`sprint-2.md`) |
|---|---|
| « US-PLAN-01 » (D-34) | US-PLAN-03 — Générer le programme hebdomadaire |
| « US-PLAN-03 » (D-39, D-45, D-51, D-54) | US-PLAN-04 — Garantir le respect des contraintes dures (selon le contexte — certaines citations « US-PLAN-03/04 » désignaient déjà les deux) |
| « US-PLAN-04 » (quelques citations) | US-PLAN-03 (cas inverse — l'inversion D-134 a permuté les usages au fil du sprint) |
| « US-PLAN-05 » (D-39 volet saisie) | Correct — sprint 3, saisie manuelle, non renommée |

Correction du backlog laissée au chef de projet (`.claude/rules` le réserve).

## Questions de terrain encore ouvertes

Aucune n'est bloquante. **Une question est refermée par le code pendant le
sprint 2** : le volume horaire hebdomadaire de référence (D-33) n'est plus
une valeur provisoire à confirmer — US-PLAN-12 (D-128) le calcule désormais
sur la grille horaire active, la question elle-même n'a plus d'objet.
**Une question ajoutée pendant le sprint 2** : celle sur l'existence d'un
troisième horaire, ci-dessous.

- Le document de progression réalisée est-il signé, et transmis à qui ?
- Le remplacement en urgence exige-t-il l'accord du directeur à chaque cas ?
- Un cours manqué est-il replacé ou seulement noté ? *(les deux sont prévus)*
- Frontière de périmètre avec l'écran d'affichage devant la direction
- Format réglementaire du procès-verbal et de la convocation *(risque R18)*
- **(Ajoutée au sprint 2, US-PLAN-12)** Existe-t-il au CIT un horaire autre
  que l'ordinaire et le Ramadan — horaire d'été, horaire de période
  d'examens, horaire de fin de stage ? Seules ces deux grilles sont relevées
  (mai et février respectivement) — rien n'affirme qu'elles couvrent l'année
  entière.
- **(Ajoutée et refermée le 2026-10-01, US-EVAL-01, prompt 35)** Un contrôle
  se tient-il sur un créneau libre, ou à la place d'une séance déjà
  programmée du module ? *Retenu : créneau libre (fiche CU-P6-01).*
- **(Ajoutée et refermée le 2026-10-01, US-EVAL-01, prompt 35)** La séance
  d'un contrôle compte-t-elle au volume horaire du module ? *Retenu : oui
  (A4, D-178) — conforme au terrain (« pendant ses créneaux ») et au
  précédent du projet de fin d'études.*
- Le seuil `SEUIL_ECART_VOLUME_REFERENTIEL_POURCENT` (D-33) reste provisoire
  (10 %), terrain non consulté — seule la moitié de D-33 a été refermée par
  US-PLAN-12, voir ci-dessus.

**(Ajoutées le 25/10/2026, prompt 50) Quatre valeurs par défaut, soumises
au commanditaire par le rapport d'avancement N°3, réponse attendue au
02/11 (registre v8, R1) :**
- Seuil d'admission à 10/20 (US-EVAL-07, V6, `SEUIL_ADMISSION_PROCES_VERBAL`).
- Note absente comptée zéro (US-EVAL-06, N6, `TRAITEMENT_ABSENCE_NOTE`).
- Ex aequo classés au même rang (US-EVAL-06, M6/M7, classement de compétition).
- Seuil de charge d'un instructeur à 24 h/semaine (US-INS-04, C2,
  `SEUIL_CHARGE_HEBDOMADAIRE_INSTRUCTEUR`, hypothèse jamais confirmée par
  le terrain depuis sa livraison).
