# Sprint 4 — 12 – 24 octobre 2026

**Objectif.** Notes, moyennes, procès-verbaux. Suivi prescrit et réalisé,
progression réalisée. Correctif de dette P-42. Stories Should si la capacité
le permet.

**Périmètre (backlog v10).** 14 stories, 55 points — 25 Must, 30 Should.

**Jalon de sortie.** **J3 le 24 octobre** — fin de développement.

**Colonne Porteur.** Laissée vide à l'ouverture (mesure de R16) : à remplir
par l'étudiant. À partir du prompt 44, le champ « Auteur » d'une décision
nomme le porteur inscrit ici pour la story concernée ; si la colonne est
vide, la décision porte « porteur non renseigné ».

## Stories

Coche à la livraison : implantée, testée, relue par le sous-agent, commitée.

| Ordre | Élément | Points | Priorité | Porteur |
|---|---|---|---|---|
| 0 | Correctif P-42 et mesure de stabilité de la suite | — | — | |
| 1 | US-SUI-05 — Déclarer la non-exécution d'une séance | 2 | Must | |
| 2 | US-SUI-01 — Consulter le rapprochement prescrit et réalisé | 5 | Must | |
| 3 | US-SUI-06 — Éditer la progression réalisée hebdomadaire | 3 | Must | |
| 4 | US-EVAL-05 — Saisir et vérifier les notes | 5 | Must | |
| 5 | US-EVAL-06 — Calculer moyennes et classement | 5 | Must | |
| 6 | US-EVAL-07 — Générer les procès-verbaux de résultats | 5 | Must | |
| 7 | US-PLAN-07 — Signaler les écarts de volume horaire | 3 | Should | |
| 8 | US-VAL-05 — Consulter les programmes et l'historique des validations | 5 | Should | |
| 9 | US-SES-09 — Clôturer une session | 3 | Should | |
| 10 | US-SUI-02 — Être alerté des écarts significatifs | 3 | Should | |
| 11 | US-SUI-03 — Consulter le tableau de bord des formations | 5 | Should | |
| 12 | US-INS-04 — Consulter la charge d'un instructeur | 3 | Should | |
| 13 | US-REF-09 — Historiser les modifications du référentiel | 3 | Should | |

**Item 10 (US-SUI-02) — D-279 fermée par D-282 (prompt 48, Temps 0), livrée le 2026-10-19.** PLAN-07 (programmé, avant soumission) et SUI-02 (réalisé, en continu) mesurent deux volumes différents malgré le même vocabulaire RG-61 : la décoration du rapprochement d'US-SUI-01, ajoutée à tort sous PLAN-07, passe sous US-SUI-02, qui garde son périmètre propre au backlog — pas de fusion, pas de retrait. D-283 consigne un cas limite (A2) : le dépassement reste affiché même quand RG-39 le rend normalement impossible.
| 14 | US-PLAN-11 — Dupliquer un programme hebdomadaire | 5 | Should | |

Totaux : 14 stories, **55 points** — 25 Must, 30 Should.
**US-PLAN-08** (déclassée, voir risque R6) et **US-EVAL-11** (nouvelle en
v10) rejoignent la réserve — voir `docs/suivi/reserve.md`.

## Point de décision — mercredi 21 octobre au soir

Toute story **Should** non commencée à cette date passe en réserve, pour
préserver la phase de tests qui commence le 26 octobre (phase 6, cf.
`AVANCEMENT.md`).

## Tâches transverses

**Vérifié dans le dépôt le 25/10/2026 (prompt 50) — coché seulement ce
qu'un fichier prouve, cité à chaque fois.**

- [x] Gabarits des documents imprimables (procès-verbal, progression
      réalisée) — `GabaritDocument` (`app/administration/models.py:280`),
      `app/planification/templates/planification/pdf/progression_realisee.html`,
      `app/evaluations/templates/evaluations/pdf/proces_verbal.html`.
- [ ] Wireframes des écrans du paquetage Évaluations, non produits en phase 4
      — **toujours non faits**. `docs/conception/16-maquettes.md`, § 7, le
      dit lui-même : « Un sixième wireframe aurait été utile... à produire au
      sprint 4, avant la réalisation de ces écrans. » Les écrans Évaluations
      ont été livrés au sprint 3 sans ce wireframe, qui n'existe toujours
      nulle part dans `docs/`.
- [ ] Contrôle K3, point ouvert du sprint 1 (Prompt 19, bloc B) — **toujours
      en défaut, aggravé**. `docs/suivi/IMPRESSION-ANALYSE.md` (§ 7) mesure
      Instructeurs à 168 px de débordement (871 px de large, contre 33 px au
      sprint 1 — aggravé par US-INS-03) et Lieux à 74 px (777 px) ; le
      correctif envisagé (paysage) n'a jamais été implanté —
      `app/noyau/static/css/impression.css` ligne 16 fixe `size: A4
      portrait`, aucune règle paysage. Part au cahier de recette comme
      anomalie, non corrigé ici.

## Revue et rétrospective

- [ ] Heures réelles saisies dans le classeur de pilotage

  Non tenu — aucune heure humaine relevée (registre v8, R23, réalisé et
  définitif).
- [ ] Vélocité mesurée, clé de conversion révisée

  Non tenu — aucune heure humaine relevée (registre v8, R23, réalisé et
  définitif).
- [x] Registre des risques mis à jour — registre v8 du 23/10/2026, tenu
      hors dépôt (`docs/livrables/09_Registre_risques_v8_2026-10-23.md`).
- [x] `AVANCEMENT.md` mis à jour — prompt 50, Temps 2.

**(25/10/2026, prompt 50)** Attribution rétrospective des porteurs de ce sprint : `docs/suivi/PORTEURS-RETROSPECTIF.md`.
