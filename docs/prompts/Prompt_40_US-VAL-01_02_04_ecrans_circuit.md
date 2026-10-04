# Prompt 40 — Sprint 3 : US-VAL-01, US-VAL-02, US-VAL-04 — les écrans du circuit

Phase 5, sprint 3. Trois stories, trois commits, **un seul rendu à la fin**.
Elles branchent des écrans sur le moteur posé par US-VAL-03 (`04c3465`) :
aucune ne touche à la table des transitions, aux gardes ni aux contraintes.

| Ordre | Story | Points | Transitions exposées |
|---|---|---|---|
| 1 | US-VAL-01 — Soumettre un programme à validation | 3 | T2 soumettre, T3 retirer |
| 2 | US-VAL-02 — Valider ou rejeter un programme | 5 | T4 valider, T5 rejeter, T6 reprendre (explicite) |
| 3 | US-VAL-04 — Empêcher l'affichage d'un programme non validé | 2 | T7 signature, T8 afficher |

**Règle de déroulement**, inchangée depuis le prompt 39 : arrêt sur les
seules conditions écrites ici ; pour tout autre écart, tu tranches selon les
trois principes du sprint 2, tu consignes, tu continues. Aucun numéro de
décision cité de mémoire : relis l'entrée avant de la citer.

**Condition d'arrêt unique** : si un écran exige de modifier
`ServiceCircuitProgramme`, sa table des transitions ou une garde, arrête-toi
et montre pourquoi. Le moteur est fini ; les écrans s'y branchent.

---

## 0. Préalables, sans arrêt

1. **Branche.** Toutes les stories du projet ont été commitées sur `master`.
   On continue ainsi. Corrige la règle de `CLAUDE.md` qui demande une branche
   par story pour qu'elle décrive la pratique réelle, dans le commit
   d'US-VAL-01. Ne déplace pas `04c3465`.
2. **Prompts.** Crée `docs/prompts/` et commite-y les fichiers de prompt non
   suivis (37, 38, 39, et celui-ci) : ils documentent la méthode et
   serviront au mémoire.
3. **Point d'accueil des écrans.** Il n'existe ni liste ni fiche de programme
   (écart 28) : la consultation de la semaine en tient lieu. Les actions des
   trois stories s'y affichent, selon l'état et le profil, à partir de la
   table des transitions — jamais d'une condition recodée dans le gabarit.

---

## 1. US-VAL-01 — Soumettre un programme à validation

| # | Critère (backlog v9) |
|---|---|
| C1 | Un programme à l'état brouillon peut être soumis |
| C2 | La soumission le fait passer à l'état soumis et le rend non modifiable par la planification |
| C3 | La cellule pédagogique est informée des programmes en attente de validation |
| C4 | Un programme déjà soumis ne peut être soumis à nouveau |

**Arbitrages.**
- **C3 s'entend dans l'application** (arbitrage A11 du prompt 34) : une page
  « Programmes en attente de validation » pour la cellule pédagogique —
  semaine, date de soumission, auteur —, et un compteur visible dans sa
  navigation. Une requête bornée pour la page, une pour le compteur.
- **Le retrait (T3)** s'expose ici, par un bouton sur un programme soumis,
  pour la planification. Si les cellules répondent « non » à la question Q1,
  il sera retiré par un correctif séparé.
- **Le bouton « Soumettre »** n'apparaît pas sur un programme vide ; s'il est
  forcé, le refus du moteur s'affiche.

**Tests HTTP (en plus de ceux listés pour US-VAL-01 dans
`ETA-01_table_transitions.md`)**
- POST de soumission par la planification : redirection, état SOUMIS, entrée
  de journal ; second POST : refus affiché, état inchangé
- le programme apparaît dans la page d'attente de la pédagogique, et le
  compteur vaut 1
- POST de retrait : état BROUILLON, programme retiré de la page d'attente
- POST de soumission par la pédagogique : 403
- page d'attente : nombre de requêtes identique avec 1 et 10 programmes

Commit : `feat(planification): US-VAL-01 soumettre un programme à validation`.

---

## 2. US-VAL-02 — Valider ou rejeter un programme

| # | Critère (backlog v9, lu selon l'arbitrage A2 du prompt 34) |
|---|---|
| C1 | La cellule pédagogique consulte le programme soumis avant décision |
| C2 | La validation le fait passer à l'état validé |
| C3 | Le rejet exige un motif et le fait passer à l'état **rejeté** ; la reprise le ramène à brouillon |
| C4 | Le motif de rejet est visible par la cellule planification |
| C5 | Seule la cellule pédagogique valide ou rejette |

**Arbitrages.**
- **Lecture du programme par la cellule pédagogique** (arbitrage A8 du
  prompt 34, qui tranche D-154) : elle reçoit la permission de lecture du
  programme, tous états. Applique-la par le mécanisme existant de la matrice
  (`administration/constantes.py` et ce qui la charge), et mets à jour les
  tests de la matrice. Écart à porter : la matrice § 11.2 du livrable.
- **La décision porte sur le centre entier** : une seule action sur la
  semaine, jamais par brigade.
- **Le motif reste visible** à la planification sur la consultation, à l'état
  rejeté puis après la reprise, jusqu'à la soumission suivante.
- **La reprise explicite (T6)** s'expose ici, par un bouton « Reprendre en
  correction » sur un programme rejeté, pour la planification. La reprise
  implicite existe déjà par la garde.

**Tests HTTP**
- GET de la consultation d'un programme soumis par la pédagogique : 200
- POST de validation par la pédagogique : état VALIDÉ, validateur et date
  enregistrés, programme sorti de la page d'attente
- POST de validation par la planification : 403, état inchangé
- POST de rejet sans motif, puis avec un motif fait de blancs : message
  d'erreur, état inchangé
- POST de rejet avec motif, puis GET par la planification : motif lisible
- POST de reprise : état BROUILLON, motif toujours affiché ; nouvelle
  soumission : motif effacé
- la cellule examens et la Direction de Formation ne voient aucun bouton de
  décision

Commit : `feat(planification): US-VAL-02 valider ou rejeter un programme`.

---

## 3. US-VAL-04 — Empêcher l'affichage d'un programme non validé

| # | Critère (backlog v9) |
|---|---|
| C1 | L'action d'affichage n'est proposée que sur un programme validé dont la signature a été enregistrée |
| C2 | La signature est manuscrite, hors système : le système enregistre sa date et le nom du signataire |
| C3 | Un affichage d'un programme non validé ou non signé est refusé côté serveur ; le contrôle est porté en base |
| C4 | Le passage à l'état affiché est journalisé avec son auteur et sa date |

C3 en base et C4 sont déjà tenus par le moteur : tu les prouves par le cycle
HTTP, tu ne les réimplantes pas.

**Arbitrages.**
- **Deux actions distinctes** pour la planification sur un programme validé :
  « Enregistrer la signature » (formulaire : date, nom du signataire,
  réenregistrable tant que non affiché), puis « Afficher », proposée
  seulement une fois la signature enregistrée.
- **Un programme affiché** porte sur la consultation la mention de sa
  validation et de sa signature (qui, quand) : c'est ce qui le rend
  opposable.

**Tests HTTP**
- programme validé sans signature : bouton « Afficher » absent ; POST forgé
  quand même : refus, état inchangé
- POST de signature avec une date antérieure à la validation, puis future :
  deux refus affichés
- POST de signature valide, puis d'affichage : état AFFICHÉ, entrée de
  journal avec auteur et date, mentions de validation et de signature
  affichées
- POST de signature sur un programme affiché : refus
- POST d'affichage par la pédagogique : 403

Commit : `feat(planification): US-VAL-04 signature et affichage du programme`.

---

## 4. Suivi et clôture, pour chacune des trois stories

- `DECISIONS.md` : ce que tu as tranché, numéroté au moment de l'écrire.
- Reports : D-172 (lecture de la pédagogique) se ferme avec US-VAL-02.
  Recompte.
- `ECARTS-LIVRABLES-SPRINT-3.md` : la matrice § 11.2 (lecture du programme
  par la pédagogique), et ce que tu as tranché seul.
- Définition de fini à chaque story : case cochée, ligne au tableau des
  sprints, ligne d'heures avec heure de début et de fin relevées au moment
  même.
- `AVANCEMENT.md`, point de décision du 7 octobre : s'il est tenu (les trois
  stories livrées), écris-le ; US-PLAN-06 reste alors au sprint 3.

## 5. Rendu final, en français, en une fois

Totaux de `pytest` complet et `tests/architecture -q` ; mesures de
requêtes si elles bougent ; décisions écrites ; reports ouverts et fermés ;
ce que tu as tranché seul ; ce que tu n'as pas pu vérifier.
Relecture `relecteur-conception` avant chacun des trois commits.
