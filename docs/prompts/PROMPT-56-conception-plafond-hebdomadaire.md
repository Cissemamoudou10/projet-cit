# Prompt 56 — Conception d'un plafond hebdomadaire par matière (sans code)

**Contexte.** Défauts 1 et 2 de RG-39 corrigés (volume compté par matière et par brigade, séances verrouillées du programme évalué comprises). Le chargeur `complet` ne pré-génère plus W+1 (seule la réservation de E2 reste) ; vérification 47/47.

Ta mesure montre un autre écart. Sur la session S1 (11,6 semaines), **M7 est consommée à 98 % et M9 à 99 % dès W-2 à W0**, tandis que M1 et M3 sont presque vierges. Aucune règle (RG-34 à RG-39) ne limite le volume placé par semaine. `_ratio_urgence` ne fait qu'ordonner les candidates d'un même créneau. Le générateur respecte sa spécification, mais le résultat ne correspond pas à une progression d'instruction réelle. C'est une **exigence manquante découverte en recette**. Le chef de projet a décidé de la traiter maintenant, **en temps limité à une journée**.

**Ne code rien.** Propose la conception, puis attends la validation.

---

## La règle proposée

Plafond hebdomadaire **par matière et par brigade** = (volume restant ÷ nombre de semaines restantes de la session de la brigade) × coefficient, **arrondi au créneau supérieur**. Coefficient paramétrable, **1,5 par défaut**. Le plafond est **recalculé à chaque génération** à partir du reste à faire : une matière en retard voit son plafond augmenter d'elle-même. Jamais un plafond figé en début de session.

## Ce que j'attends

1. **Insertion** : où, dans `ServiceGeneration.generer`, `generation/candidats.py` et `generation/tri.py`. Le plafond est-il une contrainte de la génération seulement, ou aussi de la modification manuelle, de la substitution (US-PLAN-09) et de la duplication (US-PLAN-11) ? Ma position : **génération seulement**. Une modification humaine n'est pas plafonnée, au plus signalée. Dis si tu vois une raison contraire.
2. **Coefficient** : où le stocker, qui peut le modifier (profil, écran), comment la modification est journalisée. Sa valeur par défaut est une **hypothèse à faire valider par le terrain**.
3. **Semaines restantes** : comment tu les comptes. Une semaine entièrement bloquée pour la brigade (congé centre entier, bivouac) compte-t-elle ? Que se passe-t-il pour la dernière semaine de la session, avec un diviseur à 1, et après la fin de la session ?
4. **Créneaux libérés** : ils doivent revenir aux autres matières candidates (M1, M3 notamment). Ce n'est que si **aucune** candidate ne peut les prendre qu'ils restent vides, avec un motif lisible dans le compte rendu (« plafond hebdomadaire atteint »), regroupé comme les autres motifs (C3 du prompt 53).
5. **Séances épinglées et avenants** (pk = 3, pk = 95, E1, E2, E5, séances verrouillées à la main) : jamais retirées ni bloquées par le plafond. Comptent-elles **dans** le plafond de leur semaine ? Ma position : oui, elles consomment le plafond, mais ne sont jamais refusées par lui. Dis si tu vois un problème.
6. **Prérequis** : M8 ne peut commencer qu'après l'achèvement de M6 (au sens du réalisé). Si le plafond étale M6 sur toute la session, M8 ne tient plus avant la fin. **Simule ce cas sur S1** (M6 40 h, M8 20 h, 11,6 semaines) et propose une règle, par exemple : pour une matière qui en conditionne une autre, le nombre de semaines restantes est compté jusqu'à la date au plus tard qui laisse le temps à la matière dépendante.
7. **Échelonnement entre brigades** : vérifie qu'il est préservé.
8. **Jeu `complet`** : le chargeur construit W-2 à W0 avec le générateur lui-même. Avec le plafond, l'historique sera moins dense. Confirme que les invariants du prompt 55 tiennent toujours (pk = 3, pk = 95, E1/E2/E5, avenants, M6 réalisé < 40 h, volumes prescrits inchangés). Sinon, dis lesquels bougent.
9. **Tests** : les tests existants impactés, les nouveaux tests (calcul du plafond, recalcul hebdomadaire, redistribution des créneaux, épinglées hors refus, prérequis, motif au compte rendu).
10. **Recette à rejouer** : liste les contrôles de RECETTE-00 bis, section 4 (génération), dont le résultat peut changer. RECETTE-00 ne génère rien et n'est pas concernée.
11. **Estimation** en heures, implémentation, tests, documentation et recalibrage compris. **Si elle dépasse une journée, arrête-toi** : on basculera sur l'autre option (limite assumée, en perspective).

J'attends ton retour avant tout développement.
