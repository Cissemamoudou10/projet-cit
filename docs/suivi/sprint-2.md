# Sprint 2 — 14 – 26 septembre 2026

**Objectif.** Sessions, brigades et stagiaires. Calendrier annuel, grilles horaires. Première génération du programme et contraintes dures. **Le prototype du solveur démarre en parallèle, dimensionné sur plusieurs sessions simultanées.**

**Périmètre.** 12 stories, 61 points.

**Jalon de sortie.** **C2 le 26 septembre** — restitution du prototype du solveur, réévaluation du risque R6.

## Stories

Coche à la livraison : implantée, testée, relue par le sous-agent, commitée.

- [x] **US-SES-01** — Ouvrir une session de formation · 5 pts · Must
- [x] **US-SES-02** — Constituer les brigades d'une session · 5 pts · Must
- [x] **US-SES-03** — Affecter une salle attitrée à chaque brigade · 3 pts · Must
- [x] **US-SES-04** — Consulter la composition d'une session · 3 pts · Must
- [x] **US-SES-05** — Enregistrer les stagiaires d'une session · 5 pts · Must
- [x] **US-SES-06** — Affecter les stagiaires aux brigades · 5 pts · Must
- [x] **US-SES-07** — Consulter la liste des stagiaires · 3 pts · Must
- [x] **US-INS-03** — Enregistrer les indisponibilités transmises · 3 pts · Must
- [x] **US-PLAN-01** — Élaborer le calendrier académique annuel · 8 pts · Must
- [x] **US-PLAN-03** — Générer le programme hebdomadaire d'une brigade · 8 pts · Must
  *(titre du backlog non mis à jour après RG-33 bis — le programme couvre le centre entier, pas une brigade ; voir DECISIONS.md, D-146 et suivantes)*
- [x] **US-PLAN-04** — Garantir le respect des contraintes dures · 8 pts · Must
  *(implantée avant US-PLAN-03, inversion d'ordre imposée par le prompt — CU-P5-02 est un cas d'utilisation inclus, appelé par la génération ; voir DECISIONS.md, D-134)*
- [x] **US-PLAN-12** — Gérer les grilles horaires et désigner la grille active · 5 pts · Must

## Tâches transverses

- [x] **Prototype du solveur CP-SAT**, sur plusieurs sessions simultanées —
  étude rendue (Prompt 32), GO CONDITIONNEL puis renoncement arbitré pour
  US-PLAN-08 (D-162, `docs/suivi/RISQUES-PROPOSITIONS-C2.md`). Détail :
  `etudes/solveur/RECOMMANDATION.md`
- [ ] Diagramme d'états du programme (`ETA-01`), reporté de la phase 4 —
  **non produit ce sprint, reporté explicitement au sprint 3** : US-VAL-03
  le rend nécessaire (machine à états de `ProgrammeHebdomadaire`)

## Revue et rétrospective

- [x] Heures réelles saisies — reconstitution, pas un relevé contemporain
  (aucun n'a été tenu) : `docs/suivi/HEURES-SPRINT-2.md`
- [x] Vélocité mesurée, clé de conversion révisée — **non révisée** :
  aucune mesure fiable ne le justifie, voir `docs/suivi/HEURES-SPRINT-2.md`
  pour le détail et la recommandation
- [x] Registre des risques — propositions rédigées, pas le registre lui-même
  (réservé au chef de projet) : `docs/suivi/RISQUES-PROPOSITIONS-C2.md`
- [x] `AVANCEMENT.md` mis à jour — 2026-09-30, en retard de quatre jours sur
  C2 (26 septembre), assumé explicitement, non rétrodaté
