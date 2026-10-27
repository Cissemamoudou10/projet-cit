# Heures réelles de la phase 6

Même gabarit que `docs/suivi/heures-sprint-4.md`. Règle inchangée : une ligne
par tâche, ajoutée à sa clôture, jamais reconstituée après coup ; l'heure de
début est notée avant d'ouvrir le premier fichier de la tâche, l'heure de fin
au moment de conclure.

**Règle du registre v7 (R23), inchangée depuis le prompt 44** : la colonne
« heures humaines » est remplie par l'étudiant au moment où il transmet le
prompt, avec l'heure de transmission — l'outil ne la remplit jamais.

| Date | Élément | Heure de début | Heure de fin | Heures humaines | Points | Commentaire |
|---|---|---|---|---|---|---|
| 2026-10-25 | Prompt 50 — Clôture documentaire du J3, ouverture de la phase 6 | 17:56 | 19:37 | *à saisir le jour même par l'étudiant* | 0 (suivi, aucun point) | Travail de suivi uniquement, aucun fichier sous `app/` modifié, aucun test relancé. Commit de clôture : celui qui porte ce prompt lui-même — hash non citable à l'intérieur du commit qui le crée, voir `git log` (même limite que la ligne US-REF-09 de `heures-sprint-4.md`, « commit à suivre »). |
| 2026-10-26 → 2026-10-27 | Prompt 51 — Jeux de données de la phase 6, Temps 0 à 2 (socle inchangé, script de remise à zéro, état `complet`) | 14:24 (26/10) | 14:05 (27/10) | *à saisir le jour même par l'étudiant* | *à saisir* | Session interrompue puis reprise le lendemain (pause demandée). État `complet` opérationnel et vérifié (47/47 contrôles), déterminisme et garde-fous testés. En cours de route : le paquet `jeu_recette` tout entier (socle et complet) a dû être déplacé de `planification` vers `evaluations` — `planification` n'a pas le droit d'importer `evaluations`, et l'état `complet` crée des évaluations (D-297). Commit à suivre. |
| 2026-10-27 | Prompt 51 — Temps 3 (jeu volumineux, chargeurs écrits et testés à échelle réduite) et Temps 4, partie `complet` (`JEUX-DE-DONNEES-PHASE-6.md` rédigé d'après un chargement réel) | *à saisir* | *à saisir* | *à saisir le jour même par l'étudiant* | *à saisir* | Jeu volumineux : référentiel, ressources, organisation, calendrier, évaluations, programmes — testés sur un sous-ensemble de 3 brigades (32 visées) ; le chargement pleine échelle (conteneur, mesures BNF-04/05) reste à faire, hors de ce commit. Calibrage recalé sur `etudes/solveur/HYPOTHESES.md` (80 instructeurs, 15 sessions actives), consigné dans `JEUX-DE-DONNEES-PHASE-6.md`, pas dans `DECISIONS.md` (erreur de calibrage, pas une décision). Documentation de l'état `complet` rédigée depuis un chargement réel sur `pfe_cit_recette` (73/73 et 47/47 contrôles conformes) ; un écart réel relevé (avenant « déplacement » posé le vendredi plutôt que le jeudi, repli déjà prévu dans le code). |
