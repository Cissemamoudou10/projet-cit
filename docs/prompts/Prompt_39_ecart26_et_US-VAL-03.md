# Prompt 39 — Sprint 3 : correctif de l'écart 26, puis US-VAL-03

Phase 5, sprint 3. Deux temps, deux commits, **un seul rendu à la fin**.
- **Temps 1** — correctif de l'écart 26 (gardes de lecture), arbitrage rendu.
- **Temps 2** — **US-VAL-03 · Gérer les états du programme** · 5 points ·
  Must · RG-41, RG-42, RG-44 à RG-47 · CU-P5-11 · ETA-01.

**Règle de déroulement.** Tu ne t'arrêtes QUE sur les conditions d'arrêt
écrites dans ce prompt. Pour tout autre écart, tu tranches selon les trois
principes d'arbitrage du sprint 2, tu consignes ta décision dans
`DECISIONS.md`, et tu continues. Pas de question intermédiaire : tout va
dans le rendu final.

**Numéros de décision.** Ce prompt n'en cite aucun de mémoire : il désigne
les arbitrages par leur contenu. Pour chaque renvoi que tu écris, relis
l'entrée dans `DECISIONS.md` avant de citer son numéro.

---

## Temps 1 — Écart 26 : convention des gardes de lecture

Arbitrage rendu, à consigner en une décision qui ferme l'écart 26 :

1. **Convention.** Les écritures sont gardées dans les services. Les
   lectures sont gardées par la vue qui les expose. Une lecture porte sa
   propre garde dans le service dans deux cas seulement : (a) elle renvoie
   une donnée sensible au sens de BNF-02 (sujets aujourd'hui, notes au
   sprint 4), et elle journalise alors la consultation ; (b) elle produit un
   export. Les 11 lectures déjà gardées le restent.
2. **Exceptions corrigées.** `ServiceSujet.obtenir` : rendue privée si elle
   n'est appelée que de l'intérieur de `ServiceSujet`, sinon gardée par
   `evaluations_ecriture` ; aucun appelant ne lit une référence de sujet
   sans passer par `consulter`. `ServiceStagiaire.lister_pour_export` :
   garde de lecture, tests de refus en appel direct.
3. **Convention rendue mécanique.** Un test d'architecture prouve que
   chaque motif d'URL figure dans une table d'écrans gardés. S'il n'existe
   pas, écris-le : une vue ajoutée sans garde doit faire échouer la suite.

Commit : `fix(securite): gardes de lecture, convention écrite et vérifiée`.

---

## Temps 2 — US-VAL-03 : la machine à états du programme

### Ce que fait cette story, et ce qu'elle laisse aux suivantes

US-VAL-03 pose le **moteur** du circuit : les états, toutes les transitions
au niveau des services, les gardes, les contraintes en base, le journal,
l'affichage de l'état. Les **écrans** des actions arrivent avec leur story :
soumettre et retirer (US-VAL-01), valider et rejeter (US-VAL-02), signer et
afficher (US-VAL-04), annuler une validation et porter un avenant
(US-PLAN-05 et 09). Les stories suivantes deviennent ainsi des écrans
branchés sur un moteur déjà éprouvé — le choix fait au sprint 2 pour
US-PLAN-04 avant US-PLAN-03.

**Référence unique.** `docs/diagrammes/ETA-01_etats_programme.puml` et
`docs/conception/ETA-01_table_transitions.md`, du commit `bb1e419`. Les
onze arbitrages du prompt 34 (A1 à A11) s'appliquent tels qu'écrits.

**Retour des cellules.** Attendu le 5 octobre. Tu implantes la version par
défaut des quatre questions de la note. Si une réponse change le circuit,
la correction sera un prompt séparé ; pour la faciliter, la table des
transitions vit en UN seul endroit du code (point 2 ci-dessous), et
retirer une transition — le retrait de soumission T3, par exemple — doit se
réduire à retirer une ligne de cette table et ses tests.

### Critères d'acceptation (backlog v9, US-VAL-03)

| # | Critère |
|---|---|
| C1 | Cinq états : brouillon, soumis, validé, rejeté, affiché |
| C2 | Les transitions sont exactement celles d'ETA-01, T1 à T10 |
| C3 | Toute transition non autorisée est refusée, avec un message qui nomme la règle et, quand elle existe, la marche à suivre |
| C4 | L'état est visible sur la liste des programmes et sur leur détail |
| C5 | Les actions possibles dépendent de l'état et du profil |

### 0. Vérifications préalables — lecture seule

1. Champs de `ProgrammeHebdomadaire` contre le § 4.3 de la table des
   transitions : l'audit d'ETA-01 les a dits présents ; vérifie, ajoute
   seulement ce qui manque.
2. **Tous** les chemins qui écrivent OU SUPPRIMENT des séances et des lignes
   de programme : la porte unique (`creer_seance`, `creer_seances`,
   `inserer_seance_de_controle`), et la suppression des séances non
   verrouillées dans la régénération chirurgicale. Ouvre les fichiers.
3. Le domaine d'habilitation `programme_validation` : nom exact des
   permissions, groupes qui les portent.
4. Le filtre de `regles_volume` qui exclut les programmes rejetés, et tout
   calcul qui le partage (prérequis compris).
5. **Condition d'arrêt** : un chemin d'écriture ou de suppression de séance
   qui ne passe ni par la porte unique ni par la génération. La garde d'état
   ne couvrirait pas ce chemin : montre-le-moi.

### 1. Arbitrages rendus pour cette story

**V1 — Un seul service porte les transitions.** `ServiceCircuitProgramme`,
dans `planification`. Chaque transition est une méthode (`soumettre`,
`retirer_soumission`, `valider`, `rejeter`, `reprendre`,
`enregistrer_signature`, `afficher`, `annuler_validation`). Aucune autre
écriture de l'état nulle part : un test d'architecture interdit toute
affectation du champ d'état hors de ce service.

**V2 — La table des transitions est une donnée.** Une constante unique
(état de départ, événement) → (état d'arrivée, permission requise, gardes).
Toutes les méthodes la consultent ; aucune ne recode sa propre condition
d'état. Un test lit `ETA-01_table_transitions.md` et vérifie que la matrice
admis/refusé du document est identique à celle de la constante : le
document et le code ne peuvent plus diverger sans faire échouer la suite.

**V3 — Une garde de modification, appelée par tous les chemins.**
`ServiceCircuitProgramme.garde_modification(programme, agissant)` est
appelée par la porte unique et par l'étape de suppression de la
régénération, avant toute écriture. Elle :
- laisse passer BROUILLON ;
- sur REJETÉ, exécute la reprise implicite (T6) et la journalise, puis
  laisse passer ;
- sur SOUMIS, refuse en indiquant « retirer la soumission » ;
- sur VALIDÉ, refuse en indiquant « annuler la validation » — jamais
  d'annulation implicite ;
- sur AFFICHÉ, refuse en indiquant « porter un avenant ». Le mode avenant
  arrive avec US-PLAN-05 ; d'ici là, un programme affiché est
  intouchable.
L'insertion d'un contrôle par la cellule examens passe par cette garde
comme les autres écritures, sans code supplémentaire dans `evaluations`.

**V4 — Les transitions sont sérialisées.** Chaque transition verrouille la
ligne du programme (`select_for_update`) dans sa transaction, puis relit
l'état. Deux validations simultanées, ou une soumission concurrente d'une
génération, ne peuvent pas produire un état incohérent.

**V5 — Habilitations.** T2, T3, T6, T7, T8, T9 : `programme_ecriture`
(planification). T4, T5 : la permission d'écriture du domaine
`programme_validation` (pédagogique). Aucune autre. La lecture du programme
par la cellule pédagogique arrive avec US-VAL-02.

**V6 — Le journal porte toutes les transitions.** Une nature de journal
pour les transitions du programme : auteur, horodatage, état de départ,
état d'arrivée, motif quand il y en a. La reprise implicite (T6) a la même
entrée qu'une reprise explicite, avec la mention de son déclencheur.

**V7 — Le volume programmé compte les programmes rejetés.** Révision du
filtre de `regles_volume` et de tout calcul qui le partage, conformément à
l'arbitrage A7 du prompt 34 : aucun état n'exprime l'abandon. Le report
correspondant se ferme ici.

**V8 — L'état est affiché partout où le programme l'est.** Liste, détail,
et écran de lancement de la génération : un programme non modifiable y est
signalé avant le lancement, et le bouton de génération indique pourquoi il
est indisponible.

### 2. Contraintes en base

Les huit contraintes du § 4.3 de `ETA-01_table_transitions.md`. Ajoute
celles qui manquent (l'audit en a compté sept), chacune avec son test
d'écriture directe qui attend `IntegrityError`.

### 3. Fichiers

- `app/planification/services/circuit.py` — `ServiceCircuitProgramme`, table des transitions
- `app/planification/services/ecriture.py` — appel de la garde
- module de la génération (suppression des séances) — appel de la garde
- `app/planification/services/regles_volume.py` — révision du filtre
- migration des contraintes, et des champs manquants s'il y en a
- gabarits : liste, détail, écran de lancement
- tests

### 4. Cas de test attendus

**A — Oracle des transitions (service)** — les 55 cas de la table, chacun
sous le nom inscrit dans `ETA-01_table_transitions.md`, paramétrés depuis
la constante de V2. Plus le test de concordance document / constante.

**B — Base** — huit tests `IntegrityError`, un par contrainte.

**C — Garde de modification (V3)**
- C1 `creer_seance` sur un programme SOUMIS, VALIDÉ, AFFICHÉ : trois refus, chacun avec sa marche à suivre
- C2 génération sur une semaine SOUMISE : refus, aucune séance créée ni supprimée
- C3 génération sur une semaine REJETÉE : état BROUILLON après coup, séances créées, journal portant la reprise PUIS la génération
- C4 insertion d'un contrôle par la cellule examens dans un programme SOUMIS : refus ; dans un programme REJETÉ : reprise implicite, puis insertion
- C5 la régénération d'un programme VALIDÉ ne supprime aucune séance

**D — Habilitations** — chaque transition refusée aux profils non
autorisés, en appel direct au service.

**E — Concurrence (V4)** — deux validations du même programme dans deux
transactions : une seule réussit, l'autre est refusée sur l'état relu.

**F — Volume (V7)** — un programme rejeté compte au volume programmé ; une
génération sur une autre semaine qui l'aurait dépassé est refusée.

**G — Cycle HTTP réel**
- G1 GET de la liste et du détail : l'état est affiché (C4)
- G2 POST de génération sur une semaine SOUMISE : refus affiché, aucune séance en base
- G3 GET de l'écran de lancement sur une semaine VALIDÉE : le motif d'indisponibilité est affiché

**H — Architecture**
- H1 aucune affectation du champ d'état hors de `ServiceCircuitProgramme`
- H2 aucune écriture ni suppression de séance hors de la porte unique et de la génération, et ces deux chemins appellent la garde
- H3 mesures de référence et test P-38 verts ; constante mise à jour avec note datée si le nombre de requêtes bouge

### 5. Suivi et clôture — dans le même passage

- `DECISIONS.md` : V1 à V8, numérotées au moment de les écrire.
- Reports : fermés — révision du volume des rejetés (V7), insertion d'un
  contrôle refusée hors brouillon (C4) ; recompte.
- `ETA-01_table_transitions.md` : ajoute la ligne de l'insertion d'un
  contrôle, si elle manque.
- `ECARTS-LIVRABLES-SPRINT-3.md` : ce que tu as tranché seul.
- Définition de fini : case cochée, ligne au tableau des sprints, ligne
  d'heures.
- `AVANCEMENT.md`, « Ce qu'il faut surveiller » : point de décision du
  **mercredi 7 octobre au soir** — si US-VAL-01, 02 et 04 ne sont pas
  livrées, US-PLAN-06 passe au sprint 4.

### 6. Rendu final, en français, en une fois

`pytest` complet et `tests/architecture -q` avec l'écart à 1 674 ; § 0 ;
requêtes avant et après ; décisions écrites ; reports ouverts et fermés ;
ce que tu as tranché seul ; ce que tu n'as pas pu vérifier.
Relecture `relecteur-conception` avant le commit :
`feat(planification): US-VAL-03 machine à états du programme`.
