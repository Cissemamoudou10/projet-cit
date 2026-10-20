# Propositions pour le registre des risques — jalon J3

Prompt 49, Temps 6. Même principe que `RISQUES-PROPOSITIONS-J2.md` : ce
document **ne modifie pas** le registre — il propose seulement, le report
dans le registre reste au chef de projet.

## R10 — Diagramme d'états ETA-01, validation des cellules toujours en attente

| | Au 10 octobre (J2) | Au 20 octobre (J3) |
|---|---|---|
| Probabilité | Inchangée au mieux, plus probablement en hausse | **Matérialisée en partie, jamais tranchée** — D-268 (2026-10-16) consigne qu'une seconde échéance est passée sans réponse ; le projet a choisi de trancher et continuer plutôt que d'attendre indéfiniment |
| Impact | US-VAL-01/02/04 + US-PLAN-05/06/09 construites sur les réponses par défaut | **En forte hausse** — le sprint 4 entier (toutes les stories Suivi et Évaluations) s'est construit par-dessus ce même circuit, sans qu'aucune des quatre questions originelles n'ait reçu de réponse différente de celle retenue par défaut. Une divergence sur une seule question referait désormais la quasi-totalité du périmètre livré (194 + 61 points) |
| Criticité | À revoir à la hausse | **Élevée, assumée** — D-268 documente explicitement le choix de ne plus attendre ; le risque n'est plus « en sommeil », il est sciemment porté jusqu'à la fin du développement |
| Mesure d'atténuation | Solliciter une réponse explicite avant toute story du sprint 4 qui en dépend | **Proposée** : solliciter une dernière fois avant la phase 6 (recette) — un retour négatif découvert pendant la recette coûterait plus cher qu'un retour négatif découvert maintenant, le développement étant clos |

## R23 — Mesure des heures réelles et de la vélocité

| | Au sprint 3 (J2) | Au sprint 4 (J3) |
|---|---|---|
| Probabilité | Partiellement tenue — heure de début relevée depuis le prompt 41 | **Inchangée** — `heures-sprint-4.md` tient la même discipline (33 lignes), mais la colonne « heures humaines » reste vide sur toutes les lignes, comme annoncé par la règle du registre v7 elle-même (remplie par l'étudiant, jamais par l'outil) |
| Impact | Vélocité partiellement mesurable sur cinq lignes fiables | **Inchangé pour les heures humaines** — toujours aucune mesure sur quatorze stories de plus ; **deux anomalies nouvelles** signalées dans `REVUE-SPRINT-4.md` (deux outliers de durée sans explication, une session de 33 h sans pause notée) qui, si elles s'avéraient des oublis de relevé plutôt que des faits réels, affaibliraient encore la fiabilité de l'échantillon |
| Criticité | Toujours élevée pour la clé de conversion | **Inchangée, et désormais définitive** — le développement est clos (J3), aucune session future ne viendra enrichir l'échantillon avant la phase 6 ; la clé de conversion (1,3 h/point) reste non révisée faute de mesure fiable, et le restera pour tout le reste du projet sauf relevé rétrospectif explicite |
| Mesure d'atténuation | Rappel dans la définition de fini de chaque story | **Proposée, nouvelle** : si la vélocité réelle doit un jour être connue (mémoire, phase 8), le seul chemin qui reste est un relevé rétrospectif déclaratif de l'étudiant sur l'ensemble des quatre sprints — à faire une fois, plutôt que de continuer à espérer un relevé contemporain qui n'est jamais venu en quatre sprints |

## Risque de capacité — Saturation des salles attitrées

**Inchangé depuis la proposition du 26 septembre.** Aucune story du sprint 4
ne touche aux salles attitrées ni à leur ratio avec les brigades. Rien de
nouveau à proposer — la mesure d'atténuation (vérifier le ratio réel au
CIT avant déploiement) reste à engager en phase 7.

## RISQUE FERMÉ — Ordre de verrouillage non déterministe du traitement en lot (US-PLAN-09)

**Proposé au J2, fermé au sprint 4.** P-42 (le lot d'US-PLAN-09 pouvait
verrouiller plusieurs programmes dans un ordre non garanti par Django) a
été corrigé en ouverture du sprint 4 (prompt 44, Temps 0+1, commit
`4eebeae`) : `_verrouiller_programmes_par_ordre_croissant`
(`planification/services/indisponibilite.py`), tri explicite avant tout
verrou, test de reproduction (`test_p42_verrouillage_lot.py`, échec vérifié
réel sans le tri, rétabli après correctif). Cinq exécutions complètes et
consécutives de la suite, à l'ouverture du sprint, n'ont plus reproduit
l'interblocage. **Rien à proposer** : risque clos, pas seulement atténué.

## RISQUE FERMÉ — Instabilité de la suite complète sous exécution prolongée

**Proposé au J2, cause identifiée et corrigée au sprint 4, prompt 49
(Temps 2).** La cause réelle, cherchée dès le J2 sans être trouvée alors,
est établie à ce prompt : **deux exécutions indépendantes de la suite
lancées en même temps sur la même base** provoquent un blocage PostgreSQL
(*deadlock*) lors de la création concurrente des groupes d'habilitation par
les fixtures — un défaut de méthode d'exécution, jamais un défaut du code
applicatif ni une fragilité intrinsèque de l'environnement (P-51,
`docs/suivi/PROBLEMES.md`). Corrigé par un verrou de fichier
(`conftest.py::_poser_verrou`, session-scoped) qui refuse de démarrer une
seconde exécution plutôt que de laisser PostgreSQL trancher — avec une
exception explicite pour un sous-processus pytest légitime
(`test_jeu_recette_depot.py`, via une variable d'environnement héritée).

**Mesuré à ce prompt (Temps 3)** sur une machine effectivement isolée,
rien d'autre en cours : voir `docs/suivi/MESURES-REFERENCE.md`, section
« Stabilité de la suite — clôture J3 » pour le détail des cinq exécutions
et le résultat de `pytest -m pdf`. **Rien à proposer au-delà de la mesure
déjà faite** : la cause est connue, le correctif est en place et vérifié,
ce n'est plus un risque à surveiller mais un problème résolu et documenté
(P-51).

## Point de méthode — concurrence avec un travail hors suite sur la même machine

**Constat de ce prompt, à signaler sans en faire un risque de registre.**
Pendant la préparation de cette clôture, une exécution de la mesure de
stabilité (Temps 3) a été lancée pendant qu'un autre script du même prompt
construisait l'état de démonstration sur une base DISTINCTE
(`pfe_cit_demo_j2`, jamais `test_pfe_cit`) : la suite a néanmoins affiché
une cascade d'échecs en cours d'exécution, tous liés à une connexion dans
un état de transaction corrompu. Diagnostic : une session `pytest` isolée,
interrompue sans laisser `conftest.py` nettoyer son verrou (process tué de
l'extérieur), a laissé un verrou périmé qui a bloqué les tentatives
suivantes jusqu'à sa suppression manuelle — comportement attendu du verrou
P-51 lui-même, pas un nouveau défaut. **Leçon retenue, pas un risque** :
sur cette machine de développement, une mesure de stabilité doit tourner
seule, sans AUCUNE autre commande touchant une base PostgreSQL en
parallèle, y compris sur une base distincte — un verrou périmé issu d'une
interruption externe reste le symptôme le plus probable d'un échec massif
inattendu, à vérifier en premier (`pfe_cit_pytest_en_cours_*.lock` dans le
répertoire temporaire) avant de soupçonner le code.
