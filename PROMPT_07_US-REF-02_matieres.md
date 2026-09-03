# Prompt Claude Code — 07 · US-REF-02 · Gérer le catalogue des matières

> Sprint 1, ligne WBS 5.1.8. Must, 3 points, 3,9 h estimées.
> Prérequis : US-REF-01 est finie.
> À coller dans une session neuve, après `/clear`.

---

Nous développons **US-REF-02 — Gérer le catalogue des matières**, cas d'utilisation
**CU-P2-03**, fiche **générique plus deux écarts**.

Troisième story bâtie sur `ServiceGestion`. Si tu écris du code qui n'a rien de propre
aux matières, il appartient au patron.

Tu suis les huit étapes du workflow `/story`, avec arrêt obligatoire sur ma validation.

## Traçabilité

`BF-REF-02 → US-REF-02 → CU-P2-03 → RG-05 → CLS-02`

---

# 1 · Le besoin

*En tant que membre de la cellule pédagogique, je veux gérer un catalogue de matières
indépendant des formations, afin qu'une même matière puisse servir plusieurs formations
sans double saisie.*

## Critères d'acceptation — backlog v7

1. Une matière est créée dans le catalogue **sans rattachement à une formation**.
2. L'intitulé d'une matière est **unique dans le catalogue**.
3. La fiche d'une matière indique **les formations qui l'utilisent** dans leur
   référentiel.
4. La liste des matières est **paginée et dotée d'une recherche par intitulé**.
5. Une matière **utilisée dans au moins un référentiel ne peut être supprimée**.
6. Toute modification d'une matière du catalogue est **répercutée pour l'ensemble des
   formations concernées**.

## Les deux écarts à la fiche générique

1. Le catalogue est **indépendant des formations** : une matière existe sans être
   rattachée à aucune.
2. La suppression est refusée si la matière figure **dans un référentiel ou dans une
   matrice de qualification**.

## Règle métier

**RG-05** — Aucune matière n'est jamais rattachée directement à une brigade ni à une
session. Ici, elle n'est même pas rattachée à une formation : le catalogue est
autonome, et c'est le référentiel d'US-REF-03 qui fera le lien.

---

# 2 · Le critère 6 ne demande aucun code — il interdit d'en écrire

*Toute modification d'une matière est répercutée pour l'ensemble des formations
concernées.* Il n'y a **aucun mécanisme de propagation à implanter**. Ce critère est
satisfait par construction si, et seulement si, le référentiel d'US-REF-03 **référence**
la matière au lieu d'en **recopier** l'intitulé.

Ce que tu fais ici : rien. Ce que tu ne fais surtout pas : dupliquer l'intitulé, en
prévoir une copie, ou ajouter un champ qui figerait la valeur au moment du
rattachement.

Consigne-le dans `docs/suivi/` comme contrainte pesant sur US-REF-03 : *le référentiel
référence la matière, il ne la recopie jamais*. C'est le genre de décision qu'on
retrouve violée trois sprints plus tard, quand quelqu'un a voulu « figer l'historique ».

---

# 3 · Ce qui n'appartient PAS à la matière

Deux pièges, tous deux ouverts par la rédaction du backlog.

## 3.1 · La catégorie de lieu requise n'est pas un attribut de la matière

US-REF-04 dit *une matière en lieu partagé précise le type attendu*. La fiche CU-P2-04
dit autre chose, et c'est elle qui fait foi : la catégorie de lieu se déclare **au
moment du rattachement**, sur le couple formation-matière, en même temps que le volume
horaire. CU-P2-05 est incluse dans CU-P2-04, pas dans CU-P2-03.

La raison est métier : la même matière peut exiger un amphithéâtre dans une formation
et aucun lieu dans une autre.

**Ne pose aucun champ de catégorie de lieu sur `Matiere`.** Il ira sur la classe
d'association d'US-REF-03.

## 3.2 · Les objectifs pédagogiques ne sont pas un champ

Ils forment une entité propre, portant libellé et ordre d'affichage — US-REF-05, ligne
5.1.11. Pas de champ texte, pas de liste, rien ici.

---

# 4 · Un arbitrage que je te demande de poser

**Un code court de matière.** Aucun livrable n'en prévoit. Mais la grille du programme
hebdomadaire, telle que la charte la définit, réserve **94 pixels par colonne de
groupe**. Aucun intitulé de matière n'y tiendra. Le sprint 3 aura donc besoin d'une
forme abrégée, et l'ajouter alors imposera une migration plus la saisie rétroactive de
tout le catalogue.

**Propose de l'ajouter maintenant** : champ court, facultatif, unique s'il est
renseigné. Le coût est de quelques lignes aujourd'hui, d'une demi-journée au sprint 3.

Pose la question dans ton plan, argumente, **et attends ma réponse**. C'est une
question pour le chef de bureau pédagogique : les matières du CIT ont peut-être déjà
des codes en usage, auquel cas il faut les reprendre et non les inventer.

---

# 5 · Deux critères non testables aujourd'hui

Les critères 3 et 5 supposent le référentiel, qui arrive avec US-REF-03, et la matrice
de qualification, qui arrive avec US-INS-02 — **toutes deux dans ce sprint**.

Comme pour US-REF-01, le service expose la méthode qui **énumère les éléments
s'opposant à la suppression**. Elle ne trouve rien aujourd'hui. US-REF-03 y ajoutera
les référentiels, US-INS-02 les qualifications. Écris-la pour que chaque ajout soit une
ligne.

La fiche de la matière prévoit l'emplacement de la liste des formations utilisatrices,
vide pour l'instant. Prévois-le sans le remplir.

Consigne les deux reports dans `docs/suivi/`. Ce sont les cinquième et sixième depuis
le début du paquetage ; ils devront tous être vérifiés avant la clôture du sprint.

---

# 6 · Étape 0 — Explorer

Lis `app/noyau/services/gestion.py`, `app/referentiel/` en entier, et la méthode
d'énumération des éléments bloquants écrite à US-REF-01.

Rends-moi, en une phrase, ce que cette story ajoute au patron — si elle n'y ajoute
rien, c'est bon signe et je veux le savoir.

# 7 · Étape 1 — Planifier. Attends ma validation.

Plan complet, plus ta proposition sur le code court du § 4. **N'écris rien avant mon
accord.**

---

# 8 · Le modèle

`Matiere`, héritant de `ModeleHorodate` et du mixin d'archivage.

| Attribut | Type | Contrainte |
|---|---|---|
| `intitule` | `CharField` | **Unique dans tout le catalogue** |
| `code` | `CharField` court, nullable | Unique si renseigné — **sous réserve du § 4** |

`Meta.db_table = "referentiel_matiere"`.

**Aucune clé étrangère vers `Formation`.** C'est l'écart 1, et c'est ce qui distingue
un catalogue d'une liste par formation. Un test doit le vérifier explicitement : si
quelqu'un ajoute ce lien plus tard, la story est morte sans que rien ne le signale.

Contrainte `uq_matiere_intitule`, portée en base. À la différence de la formation,
l'unicité est **globale** : il n'y a pas de contexte pour la restreindre.

Reprends l'arbitrage sur la casse tranché à US-REF-00 — la même règle s'applique, sans
quoi le catalogue et les types se comporteraient différemment sans raison.

---

# 9 · Les écrans

Bâtis sur les gabarits génériques.

**Liste** — tableau dense (§ 3.08), pagination (§ 3.10), recherche par intitulé
(§ 3.11). C'est le critère 4, littéralement.

**Formulaire** — un ou deux champs. Aucune liste déroulante de formation : le
formulaire ne doit offrir **aucun moyen de rattacher la matière à quoi que ce soit**.

**Fiche** — l'emplacement des formations utilisatrices, vide, et celui des objectifs
pédagogiques, vide aussi. Deux réserves, deux commentaires renvoyant aux stories qui
les rempliront.

**Confirmation d'archivage** (§ 3.32), BNF-09.

`npm run css:build` avant les tests d'interface.

---

# 10 · Tests

| Test | Vérifie |
|---|---|
| Création sans aucune formation → acceptée | Critère 1, écart 1 |
| `Matiere` ne porte **aucune** clé étrangère vers `Formation` | Écart 1 |
| Intitulé dupliqué → refus désignant l'existante | Critère 2, E2 |
| L'unicité est imposée **en base**, en contournant l'ORM | § 8 |
| Liste paginée au-delà de vingt matières | Critère 4 |
| Recherche par intitulé | Critère 4 |
| La méthode d'énumération des bloquants existe et ne trouve rien | Critères 3 et 5, § 5 |
| Matière archivée : absente des listes de sélection, présente en consultation | Règle générale |
| Cellule pédagogique écrit ; les trois autres lisent seulement | RG-02 |
| Création, modification, archivage journalisés | Extension de RG-26 |
| Modification concurrente détectée | E5 |
| Aucun champ de catégorie de lieu sur le modèle | § 3.1 |

L'avant-dernier et le dernier test sont des tests de **non-présence**. Ils paraissent
inutiles aujourd'hui ; ils servent le jour où quelqu'un ajoutera le champ par commodité.

## Non-régression

La suite complète des six stories précédentes passe sans modification.

---

# 11 · Vérification et livraison

- Les quinze tests d'architecture passent
- `ruff check` et `ruff format --check` propres
- Migration unique et réversible, `makemigrations --check --dry-run` muet
- `npm run css:build` rejoué
- Relecture par le sous-agent `relecteur-conception`
- `docs/suivi/` : l'arbitrage sur le code court, la contrainte pesant sur US-REF-03,
  les reports des critères 3 et 5, le temps réel passé
- Commit portant la ligne de traçabilité

---

# 12 · Hors périmètre

- Le rattachement d'une matière à une formation, le volume horaire, la catégorie de
  lieu → **US-REF-03** et **US-REF-04**
- Les objectifs pédagogiques → **US-REF-05**
- Les prérequis → **US-REF-06**
- La matrice de qualification des instructeurs → **US-INS-02**
- Toute propagation de modification : elle n'existe pas, voir § 2

# 13 · Définition de fini

Les six critères sont couverts par un test nommé ou consignés comme reportés avec leur
story de vérification, le catalogue est prouvé indépendant par un test de non-présence
de clé étrangère, l'unicité est portée en base, aucun champ de catégorie de lieu ni
d'objectif n'a été ajouté à la matière, l'arbitrage sur le code court est posé sans
être tranché, et la suite complète des stories précédentes passe sans modification.

Commence par l'étape 0.
