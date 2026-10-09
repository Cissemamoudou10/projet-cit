# Prompt 43 — Jalon J2 : démonstration de mi-parcours et clôture du sprint 3

Phase 5, fin du sprint 3. J2 a lieu **aujourd'hui, samedi 10 octobre**.
Deux parties, dans cet ordre de priorité. La partie A conditionne la
démonstration ; la partie B évite que J2 soit, comme C1 et C2, un jalon
atteint en contenu mais prononcé sans ses éléments de pilotage.

Règles inchangées : arrêt sur les seules conditions écrites ici ; aucun
numéro de décision cité de mémoire ; heure de début écrite dans
`heures-sprint-3.md` avant toute autre action. Un seul rendu à la fin.

---

## Partie A — La démonstration doit marcher

### A1. Le scénario

Un fil unique, joué de bout en bout, qui montre le cœur du sprint :

1. **Planification** — génère le programme d'une semaine.
2. **Examens** — crée un contrôle formatif : sa séance verrouillée apparaît
   au programme, marquée « Contrôle ».
3. **Planification** — soumet le programme.
4. **Pédagogique** — le voit dans sa page d'attente, le rejette avec motif.
5. **Planification** — lit le motif, modifie une séance (reprise
   implicite), resoumet.
6. **Pédagogique** — valide.
7. **Planification** — enregistre la signature du directeur, affiche.
8. **Planification** — enregistre une indisponibilité d'instructeur sur la
   semaine affichée : séances impactées listées ; remplacement par avenant ;
   le programme **reste affiché**, l'avenant visible.
9. **Examens** — crée un examen final : le jour se ferme au calendrier ;
   enregistre deux sujets, retient l'un ; organise l'épreuve ; imprime la
   convocation, sans sujet.
10. **Direction de Formation** — consulte le programme affiché et la
    convocation ; n'accède pas aux sujets (403).

### A2. Un test qui joue ce scénario

`tests/scenarios/test_demonstration_j2.py` : le fil A1 entier, **par le
cycle HTTP réel**, étape par étape, avec les comptes des cinq profils.
S'il passe, la démonstration ne cassera pas sur une règle.
**Condition d'arrêt** : s'il échoue sur une règle métier, montre-le avant
toute autre chose — c'est un défaut à corriger avant la démonstration.

### A3. Les données et les comptes

Une commande `preparer_demonstration`, sur une **base distincte** de celle
de la recette (qui se joue sur l'étiquette `recette-sprint-2` : ne pas la
toucher). Elle charge un centre réaliste, noms inventés, et un compte par
profil, et s'arrête au début de l'étape 1. Rejouable : elle remet la base de
démonstration à zéro à chaque appel, et refuse de s'exécuter sur une autre
base.

### A4. Le guide

`docs/demonstration/DEMO-J2.md` : pour chaque étape, le compte, l'écran,
le geste, ce que le jury doit voir, et la règle qu'elle illustre (RG-xx, en
une phrase). En tête : lancement du serveur, de la base de démonstration,
de la commande. En fin : trois questions probables du jury et leur réponse
courte — pourquoi un avenant plutôt qu'un retour à brouillon ; pourquoi les
sujets ne sont stockés que par référence ; pourquoi une projection plutôt
qu'une copie pour la date d'examen.

### A5. Stabilité

Lance deux fois la suite complète. Pour les interblocages PostgreSQL
observés au prompt 42 : cherche si un chemin pose `select_for_update` (les
transitions du circuit) dans un ordre de verrouillage différent d'un autre
chemin (génération, porte d'écriture, traitement en lot). **N'en corrige
rien aujourd'hui** : consigne le constat comme dette du sprint 4. Un ordre de
verrouillage incohérent serait un défaut réel en production, pas seulement
dans les tests.

Commit : `feat(demo): scénario J2, commande de préparation et guide`.

---

## Partie B — Les éléments de pilotage du sprint 3

1. **`docs/suivi/REVUE-SPRINT-3.md`** : stories livrées et points (périmètre
   50) ; jalon J2 ; reports ouverts au début et à la fin du sprint, avec leur
   liste, reparcourue dans `DECISIONS.md` en entier sur la plage du sprint
   (leçon 6 du sprint 2) ; plage des décisions ; nombre d'écarts consignés ;
   suite de tests au début et à la fin ; mesures de requêtes (41 → 47, et
   la cause de chaque pas) ; ce qui reste en dette pour le sprint 4.
2. **Heures** : consolide `heures-sprint-3.md` tel quel. Pour chaque
   élément : heures de session relevées, heures humaines si renseignées,
   lignes incomplètes **nommées comme telles**. Ne reconstitue rien.
   Calcule la vélocité en points ; ne révise pas la clé de conversion si les
   heures humaines manquent, et dis-le.
3. **`docs/suivi/LECONS-SPRINT-3.md`**, même gabarit que le sprint 2. Au
   moins : la garde à la porte unique a tenu face au premier appelant
   étranger (évaluations) ; les tests qui passaient pour une mauvaise
   raison, démasqués par un témoin (P-38, D3 d'US-EVAL-04) ; les erreurs de
   citation de décisions et leur cause ; la séparation moteur / écrans du
   circuit ; la mesure de R23, ce qui a tenu et ce qui n'a pas tenu.
4. **`docs/suivi/RISQUES-PROPOSITIONS-J2.md`** : propositions de cotation
   pour R10, R23 et le risque de capacité, et tout risque nouveau (dont
   l'interblocage de A5 et l'instabilité de la suite). Propositions
   seulement : le registre est tenu par le chef de projet.
5. `sprint-3.md` et `AVANCEMENT.md` à jour ; préparation de la
   démonstration cochée ; décision go/no-go marquée sans objet.

Commit : `chore(suivi): revue et leçons du sprint 3, propositions de risques`.

---

## Rendu final, en français, en une fois

Résultat du test de scénario ; les deux exécutions de la suite ; le constat
sur l'interblocage ; vélocité ; heures complètes et incomplètes ; ce que tu
n'as pas pu vérifier.
