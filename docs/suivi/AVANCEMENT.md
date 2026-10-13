# Avancement général

*Récapitulatif court. Le détail vit dans les fichiers de sprint.*

**Dernière mise à jour :** 2 octobre 2026 (Prompt 37, US-EVAL-03) — C2 a
été prononcé le 30 septembre, en retard de quatre jours sur l'échéance du 26
septembre. Ne pas lire ce retard comme rétrodaté : le contenu technique du
sprint 2 était acquis le 26, mais ses éléments de pilotage (heures, clé de
conversion, reports vérifiés, risques) ne l'étaient pas — exactement le même
défaut qui avait déjà retardé le prononcé de C1. Voir
`docs/suivi/LECONS-SPRINT-2.md`, leçon 1. Sprint 3 engagé depuis le 28
septembre ; ETA-01 (diagramme d'états, 5.3.17) produit le 30/09, voir « Ce
qu'il faut surveiller » — R10. Cinq stories livrées (US-VAL-03 et US-EVAL-04 le 4 octobre, 5 pts chacune, machine à états du programme et organisation d'épreuve) : US-EVAL-01 (1er
octobre, 5 pts), US-EVAL-02 (2 octobre, 2 pts — date d'un examen final
imposée et projetée, jamais copiée) et US-EVAL-03 (2 octobre, 5 pts —
sujets d'examen, confidentialité par construction). Entre ces deux
dernières, un correctif de dette hors story (Temps 1, Prompt 37) a ajouté la
garde réelle qui manquait à la mesure de P-38 (0 point, voir
`docs/suivi/PROBLEMES.md`, P-39).

## Où nous en sommes

| Phase | Période | État |
|---|---|---|
| 1 — Initiation | 27/07 – 01/08 | Close |
| 2 — Spécification | 03/08 – 14/08 | Close |
| 3 — Planification détaillée | 17/08 – 20/08 | Close |
| 4 — Analyse et conception | 20/08 – 30/08 | **Close** — 7 livrables, 23 figures, jalon J1 franchi |
| 5 — Développement | 31/08 – 24/10 | **En cours** — sprint 2 clos (C2 prononcé le 30/09, en retard), sprint 3 démarré le 28/09, US-EVAL-01 (01/10), US-EVAL-02 et US-EVAL-03 (02/10) livrées |
| 6 — Tests et recette | 26/10 – 02/11 | À venir |
| 7 — Déploiement | 03/11 – 10/11 | À venir |
| 8 — Mémoire et soutenance | 11/11 – 25/12 | À venir |

## Sprints

| Sprint | Période | Stories | Points | Livrées | Jalon |
|---|---|---|---|---|---|
| 1 | 31/08 – 12/09 | 15 | 58 | 15 | C1 |
| 2 | 14/09 – 26/09 | 12 | 61 | **12** | **C2 — prononcé le 30/09, en retard** |
| 3 | 28/09 – 10/10 | 11 | 50 | 10 | J2 |
| 4 | 12/10 – 24/10 | 14 | 55 | 2 | J3 |
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
| Stories livrées | 39 / 52 planifiées | — |
| Points livrés | 176 / 224 planifiés | — |
| Vélocité mesurée | *toujours non mesurée de façon fiable* — une reconstitution existe (`docs/suivi/HEURES-SPRINT-2.md`), structurellement biaisée à la hausse (voir ce fichier) | à établir par un relevé contemporain, sprint 3 |
| Clé de conversion | 1,3 h/point, **non révisée** — aucune mesure fiable ne le justifie, voir `docs/suivi/HEURES-SPRINT-2.md` | recontrôler dès qu'un relevé contemporain existe sur 5-6 stories du sprint 3 |
| Marge avant dépôt | 14 jours ouvrés | ne pas entamer — intacte à ce jour, sprint 3 démarré à l'heure |

**Recalcul daté (2026-10-13, prompt 45, Temps 1.4).** Points livrés : 169
(avant le prompt 44) + 7 (US-SUI-05, 2 pts ; US-SUI-01, 5 pts) = **176**.
Dénominateur recalculé sur le périmètre v10 hors réserve : 263 − 39 = **224**
points, 61 − 9 = **52** stories (voir « Sprints » et `docs/suivi/reserve.md`
ci-dessus). Stories livrées : 15 (sprint 1) + 12 (sprint 2) + 10 (sprint 3,
ligne non revérifiée ici) + 2 (sprint 4, US-SUI-05/US-SUI-01) = **39**.

## Ce qu'il faut surveiller

**Échéance du 16 octobre — retour des cellules sur ETA-01 (R1, registre des
risques v7, prompt 44).** Numérotation du registre v7, distincte de « R10 »
ci-dessous (registre antérieur) — même sujet (retour des cellules sur
ETA-01) à rapprocher lors de la prochaine refonte du registre, pas assumé
identique sans vérification.

**Point de décision — mercredi 21 octobre au soir (sprint 4, prompt 44).**
Toute story *Should* du sprint 4 non commencée à cette date passe en
réserve, pour préserver la phase de tests qui commence le 26 octobre.

**Point de décision — mercredi 7 octobre au soir.** Tenu le 4 octobre, avant son échéance : US-VAL-01, US-VAL-02 et US-VAL-04 sont livrées (commits `335d257`, `c51b353` et le commit de clôture de US-VAL-04 ; le code de US-VAL-04 est porté par `335d257`, voir P-41). US-PLAN-06 reste au sprint 3.

**R6 — reclassé, ne relève plus de la faisabilité.** L'étude
(`etudes/solveur/RECOMMANDATION.md`, D-162) a levé la question de faisabilité
technique (résolution en < 1 s médiane sur la taille réelle). Reste un
arbitrage coût/bénéfice, tranché : heuristique gloutonne en production,
US-PLAN-08 déclassée en perspective d'évolution pour le sprint 4, sous deux
conditions cumulatives (périmètre *Must* entier livré, marge de 14 jours
ouvrés intacte). Détail : `docs/suivi/RISQUES-PROPOSITIONS-C2.md`.

**R9 — toujours éteint, une dette précisée.** Contenu technique acquis le
7 septembre, `openpyxl` ajouté et vérifié dans le paquet hors ligne le
12 septembre (D-99) sans rejeu complet du protocole VM depuis — dette
explicite, à rejouer avant le dépôt réel, pas à chaque dépendance pure
Python. `ortools` (étude du solveur) reste hors du paquet hors ligne (D-160),
sans objet tant que R6 reste déclassé.

**R19, cohérence documentaire — toujours actif, cause racine identifiée.**
Deux reports de critères (D-91, D-83) sont restés absents du tableau de
suivi pendant tout le sprint 2 malgré une demande explicite dans leur propre
décision. Ce n'est plus une hypothèse : voir la proposition de risque
« dispositif de pilotage non tenu » ci-dessous, qui en est la cause.

**Risque proposé — dispositif de pilotage non tenu (nouveau, à statuer par
le chef de projet).** Deux jalons consécutifs franchis sans leurs éléments
de pilotage. Probabilité élevée (deux occurrences sur deux), impact sur la
crédibilité du suivi en soutenance. Détail et mesure d'atténuation
proposée : `docs/suivi/RISQUES-PROPOSITIONS-C2.md`.

**R10 — diagramme produit, en attente de validation.** Mesure préventive
livrée le 30 septembre (`docs/diagrammes/ETA-01_etats_programme.puml`,
`docs/conception/ETA-01_table_transitions.md`, `ETA-01_audit_code.md`,
`ETA-01_note_cellules.md`) — retour demandé aux cellules pédagogique et
planification pour le **5 octobre**. Tant que la validation n'est pas
revenue, **US-VAL-01 et US-VAL-02 restent bloquées** (prescrit par le
prompt 34, § 7) : le circuit qu'elles implantent dépend des quatre questions
posées dans la note aux cellules (`ETA-01_note_cellules.md`, § « Quatre
questions »). Nuance à surveiller : Q3 porte sur T7/T8 (signature,
affichage), relevant d'US-VAL-04 plutôt que d'US-VAL-01/02 — un « non » sur
Q3 rouvrirait D-169 et l'acteur de US-VAL-04, pas seulement le circuit de
soumission/décision. Les arbitrages sans réponse conditionnelle (A1, A2, A6
à A10 — D-165, D-166, D-170, D-171, D-172, D-173) ne dépendent pas de ce
retour et peuvent être implantés sans attendre.

**Risque proposé — saturation des salles attitrées (nouveau, constat de
terrain).** 32 à 38 salles pour 30 à 35 brigades (`etudes/solveur/
HYPOTHESES.md`) : RG-14 proche de la saturation en permanence dans la
combinaison la plus défavorable. Pas un défaut logiciel — un constat que le
système rend visible en appliquant correctement une règle qui restait
implicite. Détail : `docs/suivi/RISQUES-PROPOSITIONS-C2.md`.

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
| **D-108** | A3 (volume horaire dispensé signalé à l'affectation) | US-SES-06 | US-SUI-01 (sprint 4) | **Ouvert — jamais ajouté à ce tableau avant le 2026-09-30** |
| D-119 | 4, RG-25 (indisponibilité, contrainte dure) | US-INS-03 | US-PLAN-04 (sprint 2) | Fermé le 2026-09-15 |
| D-119 | 5, pts 4-5 (séances impactées par une indisponibilité) | US-INS-03 | US-PLAN-09 (sprint 3) | **Fermé le 2026-10-07** — I2/C1 (D-257), `seances_impactees_par_indisponibilite` |
| D-119 | A3, A4 (restriction extension, séances passées) | US-INS-03 | sprint 3 | **Fermé le 2026-10-07** — I6 (D-253) : une extension relit le même sélecteur, les séances passées en sont exclues par construction |
| D-121 | 5, RG-38 (exclusion des périodes bloquantes) | US-PLAN-01 | US-PLAN-03/04 (sprint 2) | Fermé le 2026-09-15 |
| D-121 | E2 (période bloquante recouvrant des séances programmées) | US-PLAN-01 | US-PLAN-05 (sprint 3) | **Fermé le 2026-10-07, prompt 42 partie 1, par D-245** — ligne jamais mise à jour depuis, corrigée en reparcourant le sprint au prompt 43 |
| D-121 | A3 (séances redevenues programmables) | US-PLAN-01 | sprint 3 | **Fermé le 2026-10-07, prompt 42 partie 1, par D-246** — ligne jamais mise à jour depuis, corrigée en reparcourant le sprint au prompt 43 |
| D-133 | 6 (changer de grille active ne touche pas les séances passées) | US-PLAN-12 | US-PLAN-03 (sprint 2) | Fermé le 2026-09-16 |
| D-133 | RG-64 (relation facultative séance↔créneau type) | US-PLAN-12 | *aucune story assignée* | **Ouvert, orpheline** — dette explicite, à surveiller (personne n'est chargé de la refermer) |
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
| **Présélection** (ECARTS 25) | la présélection de génération (`construire_cases`) ignore les épreuves : une case sur le lieu d'une épreuve est engendrée puis refusée par RG-37 | US-EVAL-04 (A6) | *aucune story assignée* | **Dette technique, sprint 4** : l'issue est juste (aucune séance dans le lieu), mais la case est engendrée puis refusée ; mesurer le coût avant de modifier la présélection |
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
