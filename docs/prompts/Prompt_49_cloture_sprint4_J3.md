# Prompt 49 — Clôture du sprint 4, préparation du jalon J3

Phase 5, fin du sprint 4. Les 14 stories du sprint sont livrées (55 points sur
55), quatre jours avant le jalon J3 du 24 octobre. Ce prompt n'ouvre **aucune
story**. Il corrige un défaut, mesure, tranche les travaux hors backlog,
consolide la documentation et prépare la phase 6. **Un seul rendu à la fin.**

Règles inchangées : arrêt sur les seules conditions écrites ici ; pour le reste,
tu tranches selon les trois principes d'arbitrage, tu consignes, tu continues ;
aucun numéro de décision cité de mémoire ; heure de début écrite avant toute
autre action ; auteur des décisions = porteur inscrit dans `sprint-4.md`.

---

## Temps 1 — D-285 est à revoir : l'historique ne doit pas se perdre au renommage

Une formation ou une matière renommée perd son historique, puisque celui-ci est
filtré sur la valeur lisible de l'objet. Or le renommage est précisément une
modification qu'US-REF-09 doit retracer : une limite qui touche l'objet même de
la story n'est pas acceptable.

D-15 interdit une clé étrangère, pas une identité stable.
1. Ajoute au journal une identité technique de l'objet : son type et sa clé
   primaire, en champs texte, sans clé étrangère. D-15 reste donc respectée.
   Elle est renseignée pour toute nouvelle entrée qui vise un objet ;
   l'historique filtre sur elle.
2. Les entrées antérieures restent telles quelles : D-286 exclut déjà la
   reprise rétroactive, et l'historique commence à la livraison d'US-REF-09.
   Si des entrées de l'historique du référentiel existent déjà, vérifie
   qu'elles sont toujours affichées.
3. Test : renommer une formation, puis une matière ; l'historique de chacune
   montre l'ancien et le nouvel intitulé.
4. Écris une décision qui révise D-285.

Commit : `fix(administration): identité stable des objets du journal`.

---

## Temps 2 — Le blocage PostgreSQL ne s'écarte pas en relançant

Un échec par blocage (*deadlock*) a été vu une fois, puis écarté en relançant.
Établis sa cause avant toute mesure.
- Si deux exécutions de la suite tournaient en même temps sur la même base, ce
  n'est pas un défaut : consigne-le et ajoute une protection, par exemple une
  base de test propre à chaque exécution, ou un refus de démarrer si une autre
  exécution est en cours.
- S'il est survenu dans une exécution unique, c'est le même genre de défaut que
  P-42 : cherche le chemin qui verrouille plusieurs lignes dans un ordre non
  garanti, corrige le code et consigne-le comme problème.

---

## Temps 3 — Mesure de stabilité de la suite

C'est le travail hors backlog demandé avant J3, et jamais fait. Après les temps
1 et 2, lance **cinq exécutions complètes et successives** de la suite, sur la
machine au repos, sans rien d'autre en cours. Relève pour chacune : la durée,
le nombre de tests passés, ignorés et échoués, et le nom de tout test échoué.
Puis lance `pytest -m pdf` une fois dans le conteneur.

Consigne les résultats dans `MESURES-REFERENCE.md`. Si un test échoue au moins
une fois, il fait l'objet d'un problème consigné avec sa cause. Ne le classe
pas « intermittent » sans cause.

---

## Temps 4 — Les travaux hors backlog sont tranchés

| Travail | Décision |
|---|---|
| Présélection de la génération (écart 25 du sprint 3) | **Mesurer seulement.** Compte, sur le jeu de démonstration, les créneaux présélectionnés puis refusés par une épreuve organisée, et le coût en requêtes. Aucune modification avant J3, quel que soit le résultat : consigne la mesure. |
| Impression par journée (D-155) | **Pas d'implantation sans regard humain.** Produis dans `docs/demonstration/exemplaires/` un PDF du programme hebdomadaire du jeu de démonstration et un de la convocation d'épreuve. L'étudiant jugera de leur lisibilité en A4 ; la décision viendra après. |
| RG-64 (relation séance ↔ créneau type, D-133) | **Limite consignée.** Elle n'est portée par aucune story depuis le sprint 2, et aucun comportement observable n'en dépend. Écris la décision et la limite. |
| US-PLAN-08 (solveur) | **Réexamen tenu, déclassement maintenu.** La condition de marge de 14 jours ouvrés avant dépôt n'est pas remplie. Écris la décision. |

---

## Temps 5 — Passage documentaire

1. **Le diagramme de classes face au code.** Dresse la liste complète des
   divergences entre `docs/conception/13-diagramme-classes.md` et les modèles
   implantés, dans les deux sens : un élément au diagramme absent du code, un
   élément du code absent du diagramme. Annote le diagramme : chaque
   divergence est soit portée au diagramme, soit consignée comme écart avec son
   sort. Les trois écarts du prompt 47 en font partie.
2. **Reports.** Vérifie qu'aucun report de décision n'est resté ouvert. Si
   c'est le cas, liste-les avec leur destination.
3. **`AVANCEMENT.md`** : 52 stories et 224 points livrés au total, avec le
   sprint 4 à 14 stories sur 14 et 55 points sur 55. Vérifie ces chiffres par
   recomptage, ne les recopie pas.

---

## Temps 6 — Revue du sprint 4

Produis, sur le modèle de ceux du sprint 3 :
- **`REVUE-SPRINT-4.md`** : périmètre engagé et livré, stories par jour de
  livraison (burndown réel), décisions du sprint, problèmes, mesures (requêtes,
  stabilité), relevé des heures de l'outil, et état de la colonne des heures
  humaines, qui est **constaté, pas complété**. Ce qui a bien marché, ce qui a
  coûté, ce qui se répète.
- **`ECARTS-LIVRABLES-SPRINT-4.md`** consolidé : chaque écart avec le livrable
  visé (backlog, cas d'utilisation, diagramme de classes, cahier des charges,
  maquettes) et la correction attendue. Distingue ceux qui visent le backlog,
  pour la version 11.
- **`RISQUES-PROPOSITIONS-J3.md`** : les risques techniques que tu observes, à
  ouvrir, réévaluer ou éteindre, avec leur justification. Ce sont des
  propositions : le registre reste tenu hors du dépôt.

---

## Temps 7 — Préparer la phase 6

**`docs/suivi/TRACABILITE.md`** : pour chacune des 52 stories livrées, ses
critères d'acceptation numérotés (backlog v10, ou réécrits par décision), et
les fichiers et noms de tests qui couvrent chaque critère. Un critère non
couvert par un test automatisé est marqué **« recette manuelle »**. Ne crée
aucun test à cette étape : c'est un inventaire, et la phase 6 partira de là.

---

## Clôture

La suite et l'architecture sont vertes, la stabilité est mesurée, et tous les
documents sont commités. Pose alors l'étiquette git **`j3-fin-developpement`**
sur le dernier commit.

Rendu final, en français, en une fois :
- la correction de D-285 ;
- la cause du blocage ;
- les cinq exécutions (tableau) et `pytest -m pdf` ;
- les quatre décisions hors backlog et la mesure de la présélection ;
- les divergences du diagramme de classes, avec leur nombre et leur sort ;
- les reports ;
- les chemins des trois documents de revue et de `TRACABILITE.md`, avec le
  nombre de critères en recette manuelle ;
- ce que tu as tranché seul ;
- ce que tu n'as pas pu vérifier.
