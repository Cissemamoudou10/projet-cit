# Avancement général

*Récapitulatif court. Le détail vit dans les fichiers de sprint.*

**Dernière mise à jour :** 8 septembre 2026 — contenu technique du jalon C1 acquis le 7 septembre ; le jalon lui-même se prononce le 12

## Où nous en sommes

| Phase | Période | État |
|---|---|---|
| 1 — Initiation | 27/07 – 01/08 | Close |
| 2 — Spécification | 03/08 – 14/08 | Close |
| 3 — Planification détaillée | 17/08 – 20/08 | Close |
| 4 — Analyse et conception | 20/08 – 30/08 | **Close** — 7 livrables, 23 figures, jalon J1 franchi |
| 5 — Développement | 31/08 – 24/10 | **En cours** — sprint 1 |
| 6 — Tests et recette | 26/10 – 02/11 | À venir |
| 7 — Déploiement | 03/11 – 10/11 | À venir |
| 8 — Mémoire et soutenance | 11/11 – 25/12 | À venir |

## Sprints

| Sprint | Période | Stories | Points | Livrées | Jalon |
|---|---|---|---|---|---|
| 1 | 31/08 – 12/09 | 15 | 58 | 15 | C1 |
| 2 | 14/09 – 26/09 | 12 | 61 | 0 | C2 |
| 3 | 28/09 – 10/10 | 11 | 47 | 0 | J2 |
| 4 | 12/10 – 24/10 | 15 | 61 | 0 | J3 |
| Réserve | conditionnel | 7 | 28 | 0 | — |

**Périmètre total :** 60 stories, 255 points. 61 besoins fonctionnels.

## Indicateurs

| Indicateur | Valeur | Cible |
|---|---|---|
| Stories livrées | 15 / 53 planifiées | — |
| Points livrés | 58 / 227 planifiés | — |
| Vélocité mesurée | *non mesurée* | à établir au sprint 1 |
| Clé de conversion | 1,3 h par point | **à réviser sur la vélocité réelle** |
| Marge avant dépôt | 14 jours ouvrés | ne pas entamer |

## Ce qu'il faut surveiller

**R6, criticité 9.** La génération résout sur le périmètre du centre entier : les
variables couvrent toutes les brigades de toutes les sessions actives. Le
prototype du sprint 2 doit être dimensionné en conséquence, sinon il valide une
faisabilité qui n'est pas celle du système réel.

**R9, test hors ligne — contenu technique acquis le 7 septembre, jalon non
encore franchi.** Réussi sur VM Debian 12 isolée, avant l'échéance du
12 septembre : pile conteneurisée (Docker Engine, images, moteur),
migrations, tri accentué réel, rendu PDF, redémarrage résilient. WeasyPrint
≥ 53 ne dépend plus de Cairo/GDK-PixBuf (D-60) — le repli ReportLab envisagé
n'a pas été nécessaire. Détail complet : `docs/suivi/INSTALLATION-HORS-LIGNE.md`.
**Le jalon C1, lui, ne se prononce que le 12 septembre** : il exige aussi les
heures réelles et la révision de la clé de conversion (§ Indicateurs
ci-dessus), qui n'ont pas encore eu lieu — le contenu technique acquis ne
suffit pas à lui seul à le déclarer franchi.

**R19, cohérence documentaire.** Toute décision prise en développement qui
s'écarte de la conception doit entrer dans `DECISIONS.md` le jour même.

## État consolidé des reports de critères — premier point de la revue du 26 septembre

Neuf reports de critères d'acceptation sont consignés dans `docs/suivi/DECISIONS.md`
(un report = un critère qui suppose un modèle hors périmètre de la story qui
l'a rencontré, réputé refermé automatiquement dès que le modèle manquant
existe — jamais supposé, toujours revérifié : voir la leçon de P-25).
Revérifié le 2026-09-08 sur le code réel, pas sur la déclaration des décisions
elles-mêmes. **Mise à jour du 2026-09-08, en fin de journée** : le premier
volet de D-30 (critère 3, ci-dessous « Ouvert ») a été corrigé dans le lot de
clôture du sprint 1 — traité comme une correction rattachée au report, pas
comme une story (le chef de projet l'a explicitement refusée en ce sens) —
voir P-25 (`docs/suivi/PROBLEMES.md`) et D-64 (`docs/suivi/DECISIONS.md`).
**Deux reports sont donc désormais entièrement refermés (D-22, D-30)**, un
partiellement (D-35).

| Report | Critère(s) | Story d'origine | Referme (prévu) | État vérifié le 2026-09-08 |
|---|---|---|---|---|
| D-22 | 2, 4 (type de la formation) | US-REF-00 | US-REF-01 | **Fermé** — `Formation.type_formation` en `PROTECT`, filtre par type (`CHAMPS_FILTRABLES`) confirmés dans le code |
| D-30 | 3 (fiche affiche les formations utilisatrices) | US-REF-02 | US-REF-03 | **Fermé le 2026-09-08** — `ServiceMatiere.formations_utilisatrices`, corrigé dans le lot de clôture (D-64) — c'était P-25, ouvert de 2026-09-04 à 2026-09-08 |
| D-30 | 5 (suppression bloquée) | US-REF-02 | US-REF-03 / US-INS-02 | **Fermé** — `Qualification.matiere`/`ElementReferentiel.matiere` en `PROTECT`, deux tests confirmés (D-50) |
| D-35 | 6 / RG-07, source prérequis | US-REF-03 | US-REF-06 | **Fermé** — `Prerequis`, contrôle explicite (D-40) |
| D-35 | 6 / RG-07, sources séance et évaluation | US-REF-03 | sprint 2 (séance) / sprint 4 (évaluation) | Ouvert |
| D-23 | 4 (session ouverte bloque la suppression) | US-REF-01 | US-SES-01 (sprint 2) | Ouvert — `Session` n'existe pas encore |
| D-34 | 3, 4 (contrainte de catégorie de lieu au moteur) | US-REF-04 | moteur de génération (sprint 2) | Ouvert |
| D-39 | 3, 4 (prérequis exploités par le moteur / signalés en saisie) | US-REF-06 | moteur de génération / saisie manuelle (sprint 2/3) | Ouvert |
| D-45 | 4 (instructeur affecté à un programme en cours) | US-INS-01 | séance programmée (sprint 2) | Ouvert |
| D-51 | E1 (instructeur affecté à des séances futures) | US-INS-02 | séance programmée (sprint 2) | Ouvert |
| D-54 | 4, volet brigade (lieu affecté à une brigade) | US-PLAN-02 | US-SES-02 (sprint 2) | Ouvert |
| D-54 | 4, volet séance (lieu affecté à une séance) | US-PLAN-02 | séance programmée (sprint 2) | Ouvert |

**Écart avec le décompte donné en revue** (« neuf reports, trois refermés,
six des sept ouverts se referment au sprint 2 ») : la vérification sur le code
ne confirme qu'**une** fermeture complète (D-22) et **deux** fermetures
partielles (un volet de D-30, un volet de D-35) — pas trois fermetures
entières. Le chiffre « sept ouverts » de la revue est lui-même incohérent
avec « neuf... trois refermés » (9 − 3 = 6, pas 7). À signaler en revue plutôt
qu'à corriger silencieusement ici : seul le compte ci-dessus, vérifié sur le
code, doit servir de référence au 26 septembre.

**Écart de numérotation à signaler, non corrigé ici** (hors périmètre —
`.claude/rules` réserve le backlog au chef de projet) : plusieurs reports
(D-34, D-39, D-45, D-51, D-54) citent des codes de story (« US-PLAN-01 »,
« US-PLAN-03 », « US-PLAN-04 », « US-PLAN-05 ») qui ne correspondent plus à
la numérotation actuelle de `docs/suivi/sprint-2.md` — par exemple, la
« US-PLAN-01 » citée pour le moteur de génération (D-34) y désigne en
réalité « Élaborer le calendrier académique annuel » ; le moteur de
génération porte aujourd'hui le code US-PLAN-03. Les correspondances
fonctionnelles ci-dessus (colonne « Referme ») sont établies par la
description du besoin, pas par le code de story cité dans `DECISIONS.md` —
à faire arbitrer par le chef de projet avant le 26 septembre.

## Questions de terrain encore ouvertes

Aucune n'est bloquante.

- Le document de progression réalisée est-il signé, et transmis à qui ?
- Le remplacement en urgence exige-t-il l'accord du directeur à chaque cas ?
- Un cours manqué est-il replacé ou seulement noté ? *(les deux sont prévus)*
- Frontière de périmètre avec l'écran d'affichage devant la direction
- Format réglementaire du procès-verbal et de la convocation *(risque R18)*
