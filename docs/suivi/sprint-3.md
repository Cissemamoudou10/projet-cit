# Sprint 3 — 28 septembre – 10 octobre 2026

**Objectif.** Modification manuelle, regroupement, traitement des indisponibilités. Circuit de validation complet. Ouverture du paquetage Évaluations.

Ordre retenu : **ETA-01** (préalable, tâche 5.3.17) ; **US-EVAL-01 à 04**
(aucune dépendance sur le circuit de validation, peuvent démarrer sans
attendre le retour des cellules) ; **US-VAL-03, 01, 02, 04** (dans cet
ordre : US-VAL-03 pose la machine à états et la garde RG-41 que les trois
autres consomment) ; **US-PLAN-05, 06, 09** (modification manuelle et
regroupement doivent respecter la garde RG-41 posée par US-VAL-03, donc
après elle).

**Périmètre.** 11 stories, 47 points.

**Jalon de sortie.** **J2 le 10 octobre** — démonstration de mi-parcours et décision go/no-go sur l'optimisation (US-PLAN-08) — **sans objet, arbitrée au sprint 2 (D-164) : renoncement retenu, US-PLAN-08 déclassée en perspective d'évolution.**

## Stories

Coche à la livraison : implantée, testée, relue par le sous-agent, commitée,
ligne ajoutée au tableau Sprints d'`AVANCEMENT.md`, ligne ajoutée à
`heures-sprint-3.md` datée du jour (mesure corrective de R23, prompt 34).

- [x] **US-PLAN-05** — Modifier manuellement une affectation · 5 pts · Must
- [x] **US-PLAN-06** — Regrouper plusieurs brigades sur une même séance · 5 pts · Must
- [ ] **US-PLAN-09** — Traiter une indisponibilité déclarée · 5 pts · Must
- [x] **US-VAL-03** — Gérer les états du programme · 5 pts · Must
- [x] **US-VAL-01** — Soumettre un programme à validation · 3 pts · Must
- [x] **US-VAL-02** — Valider ou rejeter un programme · 5 pts · Must
- [x] **US-VAL-04** — Empêcher l'affichage d'un programme non validé · 2 pts · Must
- [x] **US-EVAL-01** — Créer une évaluation selon son type · 5 pts · Must
- [x] **US-EVAL-02** — Saisir la date d'un examen final · 2 pts · Must
- [x] **US-EVAL-03** — Enregistrer les sujets transmis et sélectionner celui retenu · 5 pts · Must
- [x] **US-EVAL-04** — Organiser une épreuve · 5 pts · Must

## Tâches transverses

- [ ] Préparation de la démonstration de mi-parcours
- [ ] Diagramme d'états ETA-01 (5.3.17) — produit le 30/09, soumis aux cellules le __, validé le __
- [x] Décision écrite go/no-go sur US-PLAN-08 — sans objet, arbitrée au sprint 2, D-164

## Revue et rétrospective

- [ ] Heures réelles saisies dans le classeur de pilotage
- [ ] Vélocité mesurée, clé de conversion révisée
- [ ] Registre des risques mis à jour
- [ ] `AVANCEMENT.md` mis à jour
