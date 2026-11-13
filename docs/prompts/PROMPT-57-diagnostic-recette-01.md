# Prompt 57 — Diagnostic des anomalies de RECETTE-01 (lecture seule)

**Contexte.** RECETTE-01 a été jouée les 03 et 04/11 sur `recette-phase-6-c4`, état `complet` chargé le 03/11 (W0 = semaine du 02/11, W+1 = 09/11, W+2 = 16/11). **Le circuit de validation est entièrement conforme** : soumission, décision, signature, affichage, journal et habilitations, soit 24 contrôles sur 24. Le cahier est néanmoins **refusé**, à cause de 11 anomalies dans la génération, la modification manuelle, le regroupement et le traitement d'une indisponibilité.

Dépose d'abord dans `docs/recette/` le fichier fourni `RECETTE-01-CIRCUIT.md` (résultats remplis).

**Ce prompt est un diagnostic. Ne modifie aucun fichier de code, de test ou de données.** Le recetteur va jouer RECETTE-02 pendant ce temps, sur la même machine, avec `runserver` : **aucun `pytest`, aucune migration, aucune remise à zéro de base**. Lis le code. Si tu dois interroger une base, fais-le **en lecture seule sur `pfe_cit_recette`** (aucune écriture, aucun DDL), ou crée une base de diagnostic à part, sans jamais toucher `pfe_cit_recette`.

---

## Les anomalies

Pour chacune : **la cause exacte dans le code** (fichier, fonction), la **règle ou le critère** concerné, ta **qualification proposée** (NC majeur, NC mineur, défaut de données, ou comportement conforme mal compris par le cahier), et **la correction proposée avec son estimation**.

| N° | Contrôle | Constat du recetteur |
|---|---|---|
| A1 | R01-VAL03-03, PLAN05-15 | Après la génération de W+1 pour EXP1, EXP2 et CDP1, **la séance du contrôle E2 (mercredi 11/11, EXP2, verrouillée) n'apparaît pas** sur le programme. Le chargeur l'avait créée (« E2 créée (séance verrouillée, 2026-11-11) »). Le 01/11, avant les prompts 55 et 56, elle était visible après génération. Dis si elle existe encore en base, à quel programme elle est rattachée, et si la génération l'a supprimée, ignorée ou masquée. US-PLAN-03 c.7 |
| A2 | R01-VAL02-06 | Un déplacement saisi à **14:45–16:00** le vendredi (le créneau de la grille est 14:40–16:00) est **accepté sans message**, mais la séance **n'apparaît plus** sur le programme. Ressaisi à 14:40, il s'affiche. Où va une séance hors grille ? Est-elle encore prise en compte par les contraintes (instructeur, lieu, volume) ? |
| A3 | R01-PLAN05-06 | Volume de M1 pour EXP1 affiché vers **23/40** avant l'ajout d'une séance ; après l'ajout, l'écran affiche **« 2/20 »**. 20 h est le prescrit de M1 dans **F1**, alors que EXP1 suit **F6** (M1 = 40 h). Hypothèse : l'indicateur choisit l'élément de référentiel par la **matière seule**, pas par (formation de la brigade, matière). Même famille de défaut que le défaut 1 du prompt 55. Cherche **toutes** les recherches d'`ElementReferentiel` par matière seule |
| A4 | R01-PLAN05-08 | En modification manuelle, **tous les lieux sont acceptés** sauf un lieu déjà occupé : **L1, salle attitrée d'une autre brigade**, n'est pas refusé. Attendu : catégorie conforme exigée, salle attitrée d'une autre brigade refusée. US-PLAN-05 c.3, RG-32 |
| A5 | R01-PLAN05-14 | Sur un programme affiché, **aucun moyen d'ouvrir une séance** : seulement « Modifier » et « Brigade » ; « Modifier » ne montre pas l'avenant (remplacement I6 → I8 posé par le chargeur). Où les avenants sont-ils consultables aujourd'hui ? US-PLAN-05 c.9 |
| A6 | R01-PLAN06-01, 02 | Regroupement, sur W+2 : **toutes les brigades sont proposées**, CDP1 comprise (M2 hors de son référentiel). Et **quelle que soit la brigade**, l'association est refusée par « RG-37 : L5 est déjà occupé le 17/11 14:40–16:00 par EXP1 », ou « L1 … 13:00–14:15 par EXP1 ». **La séance semble entrer en conflit avec sa propre occupation du lieu.** Le refus de capacité attendu (35 > 30 en L4) n'apparaît jamais. US-PLAN-06 c.1, c.4, RG-37, RG-40 |
| A7 | R01-PLAN09-07 | Sur une séance d'un programme affiché, « déprogrammer » est absent, ce qui est correct. Mais rien ne renvoie vers la **déclaration de non-exécution**. US-PLAN-09 c.6, BNF-10 |
| A8 | R01-PLAN09-08 | En substitution (séance de I1 en W+2, brouillon), **toutes les matières et tous les instructeurs sont proposés**, M8 comprise. Attendu : seulement les matières du référentiel de la brigade qui respectent prérequis et volume. Dis aussi si le **serveur refuse** un choix invalide (M8, instructeur non qualifié) une fois soumis. Ça décide de la sévérité. US-PLAN-09 c.4 |
| A10 | R01-PLAN06-07 | **Aucune séance regroupée visible en W-1**, alors que le chargeur l'a créée (« Séance M2 d'EXP1 et EXP2 réservée, regroupée dans L9 (2026-10-27) ») et a déclaré une non-exécution sur sa ligne EXP2. Comme E2 (A1), c'est une séance **posée avant la génération** de sa semaine. Vérifie aussi E1 et E5 (W-1). Cause commune avec A1 probable : la génération ou l'affichage perd-il les séances réservées ? |
| A11 | R01-PLAN09-11 | Le refus « La modification d'une séance n'est pas possible sur un programme soumis. Retirez la soumission (T3)… » propose un lien **« Y aller »** qui mène à une **erreur HTTP 405**. Probablement un lien GET vers une vue POST seule. Cherche les autres liens « Y aller » du même type |
| A9 | R01-PLAN09-09 | Le **traitement en lot** regroupe toutes les séances de l'indisponibilité, toutes semaines confondues (W+1 affiché et W+2 brouillon). On ne peut pas traiter « les séances de M1 de I1 en W+2 » seules. Que dit la spécification (US-PLAN-09 c.5, CU-P4-03) sur la composition du lot ? Le refus de l'ensemble, si le remplaçant est occupé sur une séance, est-il implanté ? |

## Demande d'ergonomie E1 (à estimer, pas à décider)

Le recetteur demande, dans les formulaires d'ajout et de modification d'une séance :
- des **listes filtrées** : instructeurs qualifiés pour la matière choisie, matières du référentiel de la brigade, lieux compatibles avec la matière ;
- le **choix du créneau dans la grille active** (liste ou petite fenêtre), au lieu de saisir des heures. Ça supprimerait aussi la cause de A2.

Estime ces deux points séparément et dis ce que le projet a déjà (sélecteurs, grille) pour les construire.

## Deux points du chargement du 03/11

- **B1.** « AVERTISSEMENT : aucun créneau libre cette semaine pour EXP1 — avenant "déplacement" non posé ». RECETTE-03 en a besoin (R03-SUI01-05, R03-SUI06-03). Propose une correction du chargeur qui pose l'avenant de façon fiable.
- **B2.** Avertissements `RuntimeWarning: DateTimeField PeriodeCalendrier.debut received a naive datetime` pendant la génération. D'où viennent-ils, et y a-t-il un risque de décalage d'une heure sur une période bloquante ?

## Rendu attendu

1. Un tableau A1 à A11, puis E1, B1 et B2 : cause, qualification proposée, correction, estimation en heures.
2. Les anomalies qui ont **une cause commune**.
3. Un **ordre de correction** proposé, et le total estimé.
4. Les contrôles d'autres cahiers (RECETTE-02 à 05) que ces défauts risquent de toucher.

Ne corrige rien : j'arbitre d'abord.
