# Prompt 55 — État `complet` : référentiel épuisé, W+1 impossible à générer

**Contexte.** RECETTE-01 a été lancée le 01/11 au soir sur `recette-phase-6-c3`, état `complet` fraîchement chargé (W0 = semaine du 26/10). Au contrôle **R01-VAL03-03** (« Générer W+1 pour EXP1, EXP2 et CDP1 : le programme existant est complété »), la génération donne **0 séance placée, 60 non placées**.

Le compte rendu (fourni en pièce jointe par le recetteur) montre que **l'application a raison** (RG-39 respectée). C'est le **jeu de données** qui est en cause : l'historique chargé a presque entièrement consommé le volume prescrit de S1 et S2.
- Écartées d'emblée, volume déjà atteint : M1 (40 h) et M2 (30 h) pour EXP1 et EXP2 ; M4 (10 h) pour CDP1.
- Toutes les autres séances refusées par RG-39, avec 1 h ou moins de reste : M6 « atteindrait 40,17 à 40,75 h » sur 40 ; M9 « 21,00 à 21,58 h » sur 20 ; M3 « 20,25 à 20,83 h » sur 20 ; M5 pour CDP1.
- M8 écartée pour prérequis M6 non achevé : **c'est voulu** (R01-VAL03-05).

C'est le même défaut que celui corrigé pour l'état `volume` au prompt 51 bis : un référentiel épuisé par l'historique. Il n'avait pas été vu sur `complet`, car rien ne vérifiait qu'une semaine future se génère. RECETTE-01 est suspendue.

**Ne touche pas à l'application.** Ce prompt ne modifie que le chargeur de l'état `complet`, sa vérification et sa documentation.

---

## Temps 0 — Relevé d'heure

Une ligne dans `docs/suivi/heures-phase-6.md`.

## Temps 1 — Mesurer avant de corriger

Sur l'état `complet` chargé, donne pour chaque brigade (EXP1, EXP2, CDP1) et chaque matière de son référentiel : prescrit, programmé jusqu'à W0, réalisé, reste. Dis d'où vient la consommation : sur combien de semaines d'historique, et à quelle densité. Confirme que `--verifier` ne contient aucun contrôle de génération d'une semaine future.

## Temps 2 — Recalibrer

**Objectif.** Une fois `complet` chargé, les semaines **W+1, W+2 et W+3** doivent pouvoir se générer avec des séances réelles pour chaque brigade et chaque matière du référentiel, **sauf M8**, écartée par son prérequis. Les cahiers génèrent W+1 et W+2 (RECETTE-01, RECETTE-03) et dupliquent vers W+2 et W+3 (RECETTE-04).

**Ce qui ne doit pas bouger**, car les cahiers s'y réfèrent. Par ordre de préférence, réduis donc l'historique (sa durée ou sa densité) plutôt que de changer le référentiel :

| Invariant | Utilisé par |
|---|---|
| Volumes prescrits de F6 et F2 inchangés, en particulier M6 = 40 h et M7 = 30 h | R04-REF09-01, R04-PLAN07-03 |
| M6 **réalisé < 40 h** après W0, donc M8 toujours écartée pour prérequis | R01-VAL03-05, R01-PLAN09-08, R03-SUI01-10 |
| W-2, W-1, W0 affichés, avec leurs états, dates de transition et chronologie simulée | R01-VAL03-01, R04-VAL05-02 |
| Séance regroupée **pk = 3** (M2, EXP1 + EXP2, I1, L9, mardi de W-1) et séance **pk = 95** (M6, EXP1, deux avenants en W0) : **mêmes clés primaires** | R03, R04 |
| W+1 en brouillon avec la seule séance du contrôle E2 (M2, EXP2, mercredi 08:00, verrouillée) | R01-VAL03-03 |
| Contrôles E1, E5 (W-1), non-exécutions, bivouac de EXP2 en W+2, congé en W+3, S3 terminée sans programme | R01 à R04 |
| E2 porte sur M2 : M2 doit **garder du reste** pour EXP1 et EXP2 | R01, R02 |

Si un invariant est impossible à tenir avec la réduction de l'historique, **arrête-toi** et propose le changement minimal. Je mettrai alors les cahiers à jour.

## Temps 3 — Garde-fou

Ajoute à `--verifier` de l'état `complet` une **génération à blanc de W+1**, dans une transaction annulée, sans rien écrire. Elle doit placer **au moins une séance par brigade et par matière**, M8 exceptée, et M8 doit apparaître écartée pour prérequis. Fais de même pour `socle-planif`. Les deux rapports donnent le nouveau total de contrôles.

## Temps 4 — Contrôle, documentation, étiquette

1. Recharge `complet` et `socle-planif` dans une base de test, pas dans `pfe_cit_recette`, et donne les deux rapports de `--verifier`.
2. Liste **chaque contrôle des cahiers RECETTE-01 à 05** dont le résultat attendu pourrait changer avec le recalibrage : chiffres de réalisé, d'écarts, de charge… (par exemple R03-SUI01, R04-PLAN07, R04-INS04). Pour chacun, la valeur nouvelle si elle est connue.
3. Mets à jour `JEUX-DE-DONNEES-PHASE-6.md` et consigne dans `PROBLEMES.md` : constat, cause, correction, et la leçon (aucun contrôle ne vérifiait qu'une semaine future se génère).
4. Suite complète, **seule sur la machine** (P-51).
5. Commit, étiquette **`recette-phase-6-c4`**. Les précédentes ne bougent pas.
6. Clôture la ligne d'heures.

## Rendu attendu

- Le tableau du Temps 1, avant puis après.
- Ce qui a été réduit, et pourquoi.
- Les invariants : tous tenus, ou l'écart proposé.
- Les rapports de `--verifier`, le nouveau nombre de tests.
- La liste des contrôles de cahier impactés.
