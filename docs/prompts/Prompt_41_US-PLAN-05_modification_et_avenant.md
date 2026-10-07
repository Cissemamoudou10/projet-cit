# Prompt 41 — Sprint 3 : US-PLAN-05, modifier manuellement une affectation (avec l'avenant)

Phase 5, sprint 3. **US-PLAN-05** · Must · BF-PLAN-05 · CU-P5-03 · RG-34 à
RG-39, RG-41, RG-42 · CLS-05 (Avenant, § 6.6).
**Réestimée de 5 à 8 points** par décision du chef de projet : l'avenant
(BF-PLAN-05, CLS-05) n'était porté par aucune story, il rejoint celle-ci.
Le périmètre du sprint 3 passe de 47 à 50 points : inscris-le.

Un seul rendu à la fin. Arrêt sur les seules conditions écrites ici ; pour
tout autre écart, tu tranches selon les trois principes du sprint 2, tu
consignes, tu continues. Aucun numéro de décision cité de mémoire.

---

## 0. Préalables, sans arrêt

1. **Heures.** Première action du prompt, avant toute lecture : écris dans
   `heures-sprint-3.md` la ligne d'US-PLAN-05 avec l'heure de début. Les
   trois dernières stories n'ont pas eu d'heure de début : c'est la cause,
   le geste doit précéder le travail.
2. **Recette du sprint 2.** Pose l'étiquette `recette-sprint-2` sur
   `e05a1c3` (commit de clôture du sprint 2) si elle n'existe pas. La
   recette manuelle se jouera sur cette étiquette ; le développement
   continue sur `master` sans la perturber. Écris-le dans
   `JEU-RECETTE.md`.
3. **Noms dans les fixtures.** Remplace « Ziani » et « Kibour »
   (`app/planification/tests/conftest.py`) et tout autre nom de personne
   d'apparence réelle trouvé dans les fixtures et le jeu de recette par des
   noms manifestement inventés. Aucun doute ne doit subsister : un nom
   inventé ne coûte rien. Commit `test: noms de fixtures inventés`.
4. **Lecture seule** : la garde de modification de `ServiceCircuitProgramme`
   (son refus sur AFFICHÉ) ; les méthodes de la porte unique ; la présence
   d'une suppression de séance ; le champ `verrouillee`.

**Condition d'arrêt** : un chemin d'écriture de séance que tu devrais créer
hors de la porte unique. Toute opération de cette story passe par la porte.

---

## 1. Le besoin

| # | Critère | Source |
|---|---|---|
| C1 | Une séance peut être déplacée, son instructeur, son lieu ou sa matière modifiés | backlog c.1, CU-P5-03 |
| C2 | Toute modification passe par les six contraintes dures ; un refus nomme la contrainte | backlog c.2-3, E1 |
| C3 | Lieu devenu indisponible : substitution par un autre lieu conforme, ou bascule vers une activité sans lieu, **choisie par l'humain, jamais proposée d'office** | backlog c.4, A1, A2 |
| C4 | Une séance peut être ajoutée sur un créneau libre, ou supprimée | backlog c.5, A3, A4 |
| C5 | Une séance modifiée ou ajoutée à la main est **verrouillée** ; elle peut être déverrouillée | CU-P5-03 nominal, A5 |
| C6 | Une séance regroupée : avertissement que toutes ses brigades sont touchées, confirmation exigée | E3 |
| C7 | Programme **affiché** : la modification porte un **avenant** daté et motivé ; le programme reste affiché, validation et signature acquises | BF-PLAN-05, RG-42, CLS-05 § 6.6 |
| C8 | Programme **validé** : la planification peut annuler la validation (motif, confirmation), ce qui le ramène à brouillon ; jamais implicitement | RG-42, T9 |
| C9 | Programme soumis : refus, avec la marche à suivre | RG-41, E2 |

---

## 2. Arbitrages rendus

**M1 — Tout passe par la porte unique.** `ServiceEcritureSeance` gagne
`modifier_seance`, `supprimer_seance`, `deverrouiller_seance` ;
`creer_seance` sert l'ajout manuel. Chacune appelle la garde de modification
puis `ServiceContraintes` sur la séance résultante, et journalise.

**M2 — Le mode avenant est l'extension prévue de la garde.** Sur un
programme AFFICHÉ, la garde refuse aujourd'hui en indiquant « porter un
avenant ». Elle accepte désormais l'écriture quand l'appel porte un avenant
(motif non vide, nature). C'est la seule modification du moteur autorisée
par ce prompt. Sur les autres états, un avenant passé en argument est
refusé : l'avenant n'existe qu'après affichage.

**M3 — L'avenant.** Modèle `Avenant`, rattaché à la séance (CLS-05) :
`motif`, `nature` (choix : remplacement d'instructeur, changement de lieu,
bascule sans lieu, déplacement, changement de matière, ajout), `detail`
(texte généré par le service : ancienne et nouvelle valeur), auteur et
horodatage par la classe de base. Plusieurs avenants par séance. La nature
est stockée : c'est l'opération décidée, que les données de la séance ne
permettent plus de retrouver après coup. Contrainte en base : motif non
vide. CLS-05 porte `natureModification : texte` — écart à consigner.

**M4 — Pas de suppression sur un programme affiché.** Supprimer une séance
affichée effacerait l'avenant avec elle, et la trace avec lui. Une séance
affichée qui n'aura pas lieu relève de la **non-exécution** (sprint 4,
CLS-05 § 6.7 : l'avenant dit ce qui a changé, la non-exécution ce qui n'a
pas eu lieu). Refus avec ce message.

**M5 — Le déplacement reste dans la semaine.** Une séance change de créneau
dans son programme. Vers une autre semaine : suppression puis ajout, chaque
programme gardant son propre état. Refus explicite sinon.

**M6 — Une séance commencée ne se modifie plus.** Quel que soit l'état :
modifier le passé, c'est réécrire ce qui a eu lieu. Refus.

**M7 — Le verrou.** Modification et ajout manuels posent `verrouillee`
(CU-P5-03). Le déverrouillage la rend à la régénération. Une séance portant
une évaluation (contrôle) **ne se déverrouille pas et ne se supprime pas**
par cette story : elle peut être déplacée (la date de l'évaluation suit,
par construction), pas détachée de son évaluation.

**M8 — Suppression d'une évaluation (report de US-EVAL-01).** La porte ayant
désormais une suppression, `ServiceEvaluation.supprimer` est implantée : une
formative avec séance supprime l'évaluation puis sa séance par la porte
(garde comprise) ; une évaluation organisée ou dont un sujet est retenu est
refusée. Ferme le report correspondant.

**M9 — Bascule sans lieu (A2).** La matière de la séance devient un élément
dont la catégorie ne requiert aucun lieu, lieu vidé. Le système ne la
propose jamais : le formulaire offre la bascule comme un choix parmi
d'autres, sans la présélectionner.

**M10 — Annulation de validation (T9).** Bouton sur un programme validé,
pour la planification : motif obligatoire, confirmation, puis le moteur
exécute T9. L'écran de modification d'une séance d'un programme validé
renvoie à cette action.

**M11 — Reports à refermer par cette story.**
- prérequis exploités en saisie manuelle : la séance ajoutée ou modifiée
  passe par `ServiceContraintes`, qui les vérifie — prouve-le par un test ;
- période bloquante recouvrant des séances (D-121 E2) : la création d'une
  période bloquante énumère les séances recouvertes (sélecteur existant) et
  renvoie à leur modification manuelle ; l'arbitrage est humain ;
- séances redevenues programmables après suppression d'une période (D-121
  A3) : rien n'est restauré d'office ; régénération ou ajout manuel. Consigne
  la décision ;
- séance d'évaluation non déverrouillable, non supprimable (M7) ;
- suppression d'une évaluation (M8).

---

## 3. Contraintes en base

| Contrainte | Contenu |
|---|---|
| `ck_avenant_motif_non_vide` | motif non vide après suppression des blancs |
| `ck_avenant_nature_connue` | nature parmi les choix de M3 |

Hors base : avenant seulement sur une séance d'un programme affiché (état
sur une autre table), séance non commencée, déplacement dans la semaine.
Services, testés.

---

## 4. Cas de test attendus

**A — Modification (service)**
- A1 déplacement, changement d'instructeur, de lieu, de matière sur un brouillon : admis, séance verrouillée, journal
- A2 chacune des six contraintes violée par une modification : refus nommant la contrainte
- A3 ajout sur créneau libre : admis, verrouillé ; sur créneau occupé : refus
- A4 suppression sur un brouillon : admise, volume programmé de la matière diminué d'autant
- A5 déverrouillage puis régénération : la séance peut être remplacée
- A6 séance regroupée sans confirmation : refus avec la liste des brigades ; avec : admis
- A7 déplacement vers une autre semaine : refus (M5)
- A8 modification d'une séance commencée : refus (M6)
- A9 bascule sans lieu : matière sans lieu requis, lieu vide, admis ; matière exigeant un lieu sans lieu : refus

**B — États**
- B1 soumis : refus avec « retirer la soumission »
- B2 validé : refus avec « annuler la validation » ; annulation (motif, confirmation) puis modification : admis
- B3 affiché sans avenant : refus ; avec avenant : admis, programme toujours AFFICHÉ, validation et signature intactes, avenant enregistré avec nature et détail
- B4 avenant passé sur un brouillon : refus (M2)
- B5 suppression sur un affiché : refus renvoyant à la non-exécution (M4)
- B6 rejeté : reprise implicite puis modification, journal dans cet ordre

**C — Base** — deux `IntegrityError` (motif vide, nature inconnue).

**D — Évaluations**
- D1 séance de contrôle : déverrouillage et suppression directe refusés ; déplacement admis, date de l'évaluation suivie
- D2 suppression d'une formative avec séance : évaluation et séance supprimées
- D3 suppression d'une évaluation organisée, ou à sujet retenu : refus

**E — Reports** — un test par report refermé (M11).

**F — Cycle HTTP réel**
- F1 POST de modification par la planification sur un brouillon : redirection, nouvelle valeur affichée, marque de verrou
- F2 POST violant une contrainte : message nommant la contrainte, rien en base
- F3 POST sur un affiché sans motif d'avenant : refus ; avec : avenant visible sur la consultation
- F4 POST d'annulation de validation sans motif : refus ; avec : état BROUILLON
- F5 POST de modification par la pédagogique : 403
- F6 POST de bascule sans lieu : aucune option présélectionnée dans le formulaire servi par le GET précédent (M9)

**G — Architecture** — la porte unique reste la seule voie d'écriture et de
suppression (test existant, à étendre aux nouvelles méthodes) ; requêtes de
référence et P-38 verts.

---

## 5. Suivi et clôture, dans le même passage

`DECISIONS.md` (M1 à M11) ; reports refermés et recompte ;
`ECARTS-LIVRABLES-SPRINT-3.md` : CLS-05 (`natureModification` en texte libre,
ici un choix stocké), CU-P5-03 E2 (« faire rejeter » n'est plus une issue
pour un programme validé : c'est l'annulation), backlog v9 (avenant absent
d'US-PLAN-05, estimation 5 → 8) ; définition de fini avec heure de fin
relevée au commit ; `AVANCEMENT.md` : périmètre du sprint 3 à 50 points.

Commit : `feat(planification): US-PLAN-05 modification manuelle et avenant`.

## 6. Rendu final, en français, en une fois

Totaux de tests ; requêtes si elles bougent ; décisions ; reports ouverts et
fermés ; ce que tu as tranché seul ; ce que tu n'as pas pu vérifier.
