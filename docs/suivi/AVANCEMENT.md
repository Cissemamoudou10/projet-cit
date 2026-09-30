# Avancement général

*Récapitulatif court. Le détail vit dans les fichiers de sprint.*

**Dernière mise à jour :** 30 septembre 2026 (Prompt 34, ETA-01) — C2 a été
prononcé le même jour, en retard de quatre jours sur l'échéance du 26
septembre. Ne pas lire ce retard comme rétrodaté : le contenu technique du
sprint 2 était acquis le 26, mais ses éléments de pilotage (heures, clé de
conversion, reports vérifiés, risques) ne l'étaient pas — exactement le même
défaut qui avait déjà retardé le prononcé de C1. Voir
`docs/suivi/LECONS-SPRINT-2.md`, leçon 1. Sprint 3 engagé depuis le 28
septembre ; première tâche produite (ETA-01, diagramme d'états du programme,
5.3.17), voir « Ce qu'il faut surveiller » — R10.

## Où nous en sommes

| Phase | Période | État |
|---|---|---|
| 1 — Initiation | 27/07 – 01/08 | Close |
| 2 — Spécification | 03/08 – 14/08 | Close |
| 3 — Planification détaillée | 17/08 – 20/08 | Close |
| 4 — Analyse et conception | 20/08 – 30/08 | **Close** — 7 livrables, 23 figures, jalon J1 franchi |
| 5 — Développement | 31/08 – 24/10 | **En cours** — sprint 2 clos (C2 prononcé le 30/09, en retard), sprint 3 démarré le 28/09, aucune story engagée à ce jour |
| 6 — Tests et recette | 26/10 – 02/11 | À venir |
| 7 — Déploiement | 03/11 – 10/11 | À venir |
| 8 — Mémoire et soutenance | 11/11 – 25/12 | À venir |

## Sprints

| Sprint | Période | Stories | Points | Livrées | Jalon |
|---|---|---|---|---|---|
| 1 | 31/08 – 12/09 | 15 | 58 | 15 | C1 |
| 2 | 14/09 – 26/09 | 12 | 61 | **12** | **C2 — prononcé le 30/09, en retard** |
| 3 | 28/09 – 10/10 | 11 | 47 | 0 | J2 |
| 4 | 12/10 – 24/10 | 15 | 61 | 0 | J3 |
| Réserve | conditionnel | 7 | 28 | 0 | — |

**Périmètre total :** 60 stories, 255 points. 61 besoins fonctionnels. Sprint
2 : périmètre entier livré (12/12 stories, 61/61 points), plus l'étude de
faisabilité du solveur (Prompt 32, hors points chiffrés).

## Indicateurs

| Indicateur | Valeur | Cible |
|---|---|---|
| Stories livrées | 27 / 53 planifiées | — |
| Points livrés | 119 / 227 planifiés | — |
| Vélocité mesurée | *toujours non mesurée de façon fiable* — une reconstitution existe (`docs/suivi/HEURES-SPRINT-2.md`), structurellement biaisée à la hausse (voir ce fichier) | à établir par un relevé contemporain, sprint 3 |
| Clé de conversion | 1,3 h/point, **non révisée** — aucune mesure fiable ne le justifie, voir `docs/suivi/HEURES-SPRINT-2.md` | recontrôler dès qu'un relevé contemporain existe sur 5-6 stories du sprint 3 |
| Marge avant dépôt | 14 jours ouvrés | ne pas entamer — intacte à ce jour, sprint 3 démarré à l'heure |

## Ce qu'il faut surveiller

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
| D-35 | 6/RG-07, source évaluation | US-REF-03 | sprint 4 | Ouvert |
| **D-23** | 4 (session bloque la suppression d'une formation) | US-REF-01 | US-SES-01 (sprint 2) | **Fermé — corrigé le 2026-09-30**, était marqué à tort « Ouvert ». `test_d1_formation_portant_une_session_ouverte_ne_peut_etre_supprimee`, `test_d2_meme_refus_par_le_vrai_cycle_http_...`, `test_d3_formation_portant_une_session_cloturee_est_aussi_protegee` (`app/organisation/tests/test_protection_formation.py`). Écart de libellé signalé : D-69 |
| D-34 | 3, 4 (catégorie de lieu au moteur) | US-REF-04 | moteur de génération (sprint 2) | Fermé le 2026-09-16 — `test_generation_lieux.py` |
| D-39 | 3, 4, volet moteur (prérequis exploités par le moteur) | US-REF-06 | moteur de génération (sprint 2) | Fermé le 2026-09-16 |
| D-39 | 3, 4, volet saisie manuelle | US-REF-06 | US-PLAN-05 (sprint 3) | Ouvert |
| D-45 | 4 (instructeur affecté à un programme en cours) | US-INS-01 | séance programmée (sprint 2) | Fermé le 2026-09-15 — `test_a9_suppression_instructeur_portant_une_seance_refusee` |
| D-51 | E1 (retrait de qualification, instructeur à séances futures) | US-INS-02 | séance programmée (sprint 2) | Fermé le 2026-09-15 — reconfirmé 2026-09-30 : `test_retrait_refuse_si_une_seance_future_existe` (`app/planification/tests/test_resolveur_qualification.py`) teste bien le RETRAIT de qualification, pas le `PROTECT` sur `Seance.instructeur` |
| D-54 | 4, volet brigade (lieu affecté à une brigade) | US-PLAN-02 | US-SES-03 (sprint 2) | Fermé le 2026-09-11 |
| D-54 | 4, volet séance (lieu affecté à une séance) | US-PLAN-02 | séance programmée (sprint 2) | Fermé le 2026-09-15 |
| **D-91** | R2-GEN-07 (salle attitrée reprise par défaut à la génération) | US-SES-03 | moteur de génération (sprint 2) | **Fermé — jamais ajouté à ce tableau avant le 2026-09-30**, découvert en relisant `DECISIONS.md` en entier. `test_d1_matiere_salle_attitree_reprend_la_salle_de_la_brigade` (`test_generation_lieux.py`) |
| **D-83** | R2-NRG-04/05 (brigade au programme en cours non supprimable) | US-SES-02 | séance programmée (sprint 2) | **Fermé le 2026-09-30** — mécanisme posé depuis US-PLAN-04 mais jamais testé par le vrai chemin de service jusqu'à ce jour ; comblé (voir ci-dessus) |
| **D-108** | A3 (volume horaire dispensé signalé à l'affectation) | US-SES-06 | US-SUI-01 (sprint 4) | **Ouvert — jamais ajouté à ce tableau avant le 2026-09-30** |
| D-119 | 4, RG-25 (indisponibilité, contrainte dure) | US-INS-03 | US-PLAN-04 (sprint 2) | Fermé le 2026-09-15 |
| D-119 | 5, pts 4-5 (séances impactées par une indisponibilité) | US-INS-03 | US-PLAN-09 (sprint 3) | Ouvert |
| D-119 | A3, A4 (restriction extension, séances passées) | US-INS-03 | sprint 3 | Ouvert |
| D-121 | 5, RG-38 (exclusion des périodes bloquantes) | US-PLAN-01 | US-PLAN-03/04 (sprint 2) | Fermé le 2026-09-15 |
| D-121 | E2 (période bloquante recouvrant des séances programmées) | US-PLAN-01 | US-PLAN-05 (sprint 3) | Ouvert |
| D-121 | A3 (séances redevenues programmables) | US-PLAN-01 | sprint 3 | Ouvert |
| D-133 | 6 (changer de grille active ne touche pas les séances passées) | US-PLAN-12 | US-PLAN-03 (sprint 2) | Fermé le 2026-09-16 |
| D-133 | RG-64 (relation facultative séance↔créneau type) | US-PLAN-12 | *aucune story assignée* | **Ouvert, orpheline** — dette explicite, à surveiller (personne n'est chargé de la refermer) |
| D-133 | refus de générer sans grille active (E6) | US-PLAN-12 | US-PLAN-03 (sprint 2) | Fermé le 2026-09-16 |
| **D-171** | RG-39 a) révisée (volume programmé compte aussi REJETÉ) | US-PLAN-04 (D-140) | US-VAL-03 (sprint 3) | **Ouvert — créé le 2026-09-30, prompt 34** |
| **D-172** | lecture du programme par la cellule pédagogique (`programme_validation_lecture`) | US-PLAN-03 (D-154) | US-VAL-02 (sprint 3) | **Ouvert — créé le 2026-09-30, prompt 34** |

### Compte final, vérifié le 2026-09-30

Recompté au prompt 34 : D-171 et D-172 (ci-dessus) s'ajoutent aux huit
reports déjà ouverts à la clôture du sprint 2 — **dix ouverts aujourd'hui**,
pas huit. Les deux tiennent à une révision (D-171 révise D-140) et à un
complément (D-172 complète D-154) rendus par ETA-01, pas à une décision
prise pendant le sprint 2 lui-même — ils s'ajoutent donc au compte du
sprint 2 sans le rouvrir.

| | Compte |
|---|---|
| **Ouverts aujourd'hui** | **10** : D-35(évaluation), D-39(saisie manuelle), D-119(pts 4-5), D-119(A3/A4), D-121(E2), D-121(A3), D-133(RG-64, orpheline), D-108, D-171, D-172 |
| **Refermés pendant le sprint 2** | **14** : D-23, D-34, D-35(séance), D-39(moteur), D-45, D-51, D-54(brigade), D-54(séance), D-91, D-83, D-119(RG-36), D-121(RG-38), D-133(constat d'absence), D-133(E6) |
| **Créés pendant le sprint 2** | **12** : D-91, D-83, D-108, D-119(×3), D-121(×3), D-133(×3) |
| **Créés pendant le sprint 3, à ce jour (prompt 34)** | **2** : D-171, D-172 |

**Écart avec le décompte donné en revue du sprint 1** (« neuf reports, trois
refermés, six des sept ouverts se referment au sprint 2 ») : ce chiffre
comptait par **décision** (15 décisions distinctes ouvrent un report), le
tableau ci-dessus compte par **critère/volet** (26 lignes) — deux unités
différentes, jamais comparables terme à terme. Le chiffre de revue était de
toute façon interne-incohérent (9 − 3 = 6, pas 7) ; à signaler en séance,
pas à corriger silencieusement a posteriori.

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
- Le seuil `SEUIL_ECART_VOLUME_REFERENTIEL_POURCENT` (D-33) reste provisoire
  (10 %), terrain non consulté — seule la moitié de D-33 a été refermée par
  US-PLAN-12, voir ci-dessus.
