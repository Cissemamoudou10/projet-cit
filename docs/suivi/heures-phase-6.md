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
| 2026-10-27 | Prompt 51 — Temps 3 (jeu volumineux, chargeurs) et Temps 4 (documentation `complet` et volumineux) | *à saisir* | 21:08 | *à saisir le jour même par l'étudiant* | *à saisir* | Jeu volumineux écrit, testé à échelle réduite (3 brigades) puis chargé réellement à pleine échelle (32 brigades, conteneur `python:3.14-slim-bookworm`, base `pfe_cit_volume`) : 64,51 s, `--verifier` 17/17, BNF-04/05 largement tenus (détail `MESURES-REFERENCE.md`). Un bug réel trouvé par ce chargement et corrigé : `charger_etat_volume` appelait `initialiser_grilles_horaires` avant la création des comptes (RG-63), invisible des tests unitaires qui n'empruntent jamais l'orchestration complète. Calibrage recalé sur `etudes/solveur/HYPOTHESES.md` (80 instructeurs, 15 sessions actives), consigné dans `JEUX-DE-DONNEES-PHASE-6.md`, pas dans `DECISIONS.md` (erreur de calibrage, pas une décision). État `complet` documenté depuis un chargement réel sur `pfe_cit_recette` (73/73 puis 47/47 contrôles conformes) ; un écart réel relevé (avenant « déplacement » posé le vendredi plutôt que le jeudi, repli déjà prévu dans le code). Relecture `relecteur-conception` (aucun contournement de service) ; quatre commits séparés (chargeurs volumineux, documentation `complet`, correction de l'orchestration, mesures pleine échelle) ; étiquette `recette-phase-6` posée sur le commit de correction. |
