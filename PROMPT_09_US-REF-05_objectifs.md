# Prompt Claude Code — 09 · US-REF-05 · Associer des objectifs pédagogiques aux matières

> Sprint 1, ligne WBS 5.1.11. Must, 3 points, 3,9 h estimées.
> Prérequis : US-REF-03 et US-REF-04 sont finies.
> À coller dans une session neuve, après `/clear`.

---

Nous développons **US-REF-05 — Associer des objectifs pédagogiques aux matières**, cas
d'utilisation **CU-P2-06**, fiche **générique**, sans écart.

Quatrième et dernière story bâtie sur `ServiceGestion`. Elle devrait être la plus
courte du paquetage. Si elle ne l'est pas, c'est que le patron ne tient pas ses
promesses — et je veux le savoir.

Tu suis les huit étapes du workflow `/story`, avec arrêt obligatoire sur ma validation.

## Traçabilité

`BF-REF-05 → US-REF-05 → CU-P2-06 → CLS-02`

---

# 1 · Le besoin

*En tant que membre de la cellule pédagogique, je veux renseigner les objectifs
pédagogiques de chaque matière, afin d'expliciter les compétences visées.*

## Critères d'acceptation — backlog v7

1. Une matière du catalogue peut porter **plusieurs** objectifs pédagogiques.
2. Chaque objectif comporte un **libellé** et un **ordre d'affichage**.
3. Les objectifs sont consultables **depuis la fiche de la matière et depuis le
   référentiel des formations qui l'utilisent**.
4. **La suppression d'un objectif n'affecte pas la matière.**

---

# 2 · Deux décisions de modèle, et la seconde est le seul vrai piège

## 2.1 · L'objectif appartient à la matière, jamais au référentiel

Le critère 3 le dit sans le dire : les objectifs sont consultables *depuis le
référentiel des formations qui l'utilisent*, au pluriel. Un objectif est donc rattaché
à la **matière du catalogue**, et se trouve visible dans toutes les formations qui
l'emploient.

Ce n'est pas une commodité : une matière décrit une compétence, et cette compétence ne
change pas selon la formation qui la dispense. Ce qui change d'une formation à l'autre,
c'est le volume horaire et la catégorie de lieu — et ceux-là vivent bien sur la classe
d'association d'US-REF-03.

**Aucune clé étrangère vers `Formation` ni vers `ElementReferentiel`.** Un test de
non-présence le vérifie.

## 2.2 · L'ordre d'affichage, et pourquoi une contrainte d'unicité naïve casse

L'ordre est un entier, unique au sein d'une matière. Poser
`UniqueConstraint(fields=["matiere", "ordre"])` paraît évident et **rend tout
réordonnancement impossible**.

Échanger les positions 2 et 3 demande deux écritures. Après la première, deux objectifs
portent le même ordre, et la contrainte rejette la transaction avant que la seconde
écriture ne rétablisse la cohérence. Le contournement habituel — passer par une valeur
temporaire, ou renuméroter toute la liste à chaque déplacement — est du bricolage que
l'on retrouve trois ans plus tard.

**PostgreSQL sait faire mieux.** Déclare la contrainte comme *différée* :
`UniqueConstraint(..., deferrable=Deferrable.DEFERRED)`. Elle n'est alors vérifiée qu'au
moment de valider la transaction, et non à chaque écriture. Les deux mises à jour de
l'échange se font sans conflit, et la cohérence reste garantie à la sortie.

C'est un cas d'école pour votre note d'implémentation : la contrainte reste portée en
base — donc infranchissable — tout en autorisant l'état transitoire qu'exige
l'opération métier.

Deux conséquences à assumer dans le code :

- l'échange **doit** se dérouler dans une transaction explicite, sans quoi le report ne
  sert à rien
- les trous dans la numérotation sont permis. Supprimer l'objectif numéro 2 sur cinq ne
  renumérote rien : l'ordre sert à trier, pas à compter

## 2.3 · Ici, la suppression est réelle — et c'est la première fois

Depuis le début du projet, la règle est *l'archivage remplace la suppression*. Elle
découle de BNF-14 : un système dont on peut effacer les éléments perd la capacité de
rendre compte.

**Un objectif pédagogique fait exception**, et le critère 4 l'énonce : sa suppression
n'affecte pas la matière. Rien ne le référence — ni séance, ni évaluation, ni
qualification. Il n'y a donc aucune intégrité historique à préserver.

**N'emploie pas le mixin d'archivage sur cette entité.** Suppression franche, avec
confirmation explicite au titre de BNF-09 — la confirmation reste due, c'est une action
irréversible.

Consigne l'exception dans `docs/suivi/` : c'est le genre d'écart à une règle générale
qu'un jury demande de justifier, et la justification tient en une phrase.

---

# 3 · Étape 0 — Explorer

Lis `app/referentiel/` en entier, en particulier `Matiere` et `ElementReferentiel`,
`app/noyau/services/gestion.py`, et l'écran de composition du référentiel écrit à
US-REF-03.

Dans `docs/charte/` : **3.15** (ligne de détail dépliable), **3.16** (tableau éditable
en ligne), **3.22** (zone de texte), **3.32** (dialogue), **3.40** (bouton d'action de
ligne).

**Rends-moi ce que le patron te donne gratuitement sur cette story.** C'est la dernière
occasion de mesurer le retour de l'investissement fait à US-REF-00, avant la revue du
sprint.

# 4 · Étape 1 — Planifier. Attends ma validation.

Plan complet, avec la mécanique de réordonnancement et la façon dont tu ouvres la
transaction. **N'écris rien avant mon accord.**

---

# 5 · Le modèle

`ObjectifPedagogique`, héritant de `ModeleHorodate`. **Pas du mixin d'archivage** —
voir § 2.3.

| Attribut | Type | Contrainte |
|---|---|---|
| `matiere` | clé étrangère | Non nul, `CASCADE` |
| `libelle` | texte | Non vide |
| `ordre` | entier positif | Unique **par matière**, contrainte **différée** |

`Meta.db_table = "referentiel_objectif_pedagogique"`.

`CASCADE` est cohérent : un objectif n'a aucun sens sans sa matière, et la suppression
d'une matière est de toute façon déjà bloquée dès qu'un référentiel l'emploie.

Contraintes portées en base, nommées :

- `uq_objectif_matiere_ordre` — unicité différée
- `ck_objectif_libelle_non_vide` — un libellé vide passerait la validation d'un
  `CharField` sans `blank=False` mal réglé ; la base tranche

---

# 6 · Les écrans

## 6.1 · Sur la fiche de la matière — édition

L'emplacement a été réservé à US-REF-02, il se remplit maintenant.

Tableau éditable en ligne (§ 3.16) : le libellé modifiable sur place, deux boutons
d'action de ligne (§ 3.40) pour monter et descendre, un pour supprimer. Zone de texte
(§ 3.22) pour un libellé long. Confirmation de suppression par dialogue (§ 3.32).

Monter et descendre sont des soumissions de formulaire, **sans script** — chaque
échange déclenche la transaction du § 2.2.

## 6.2 · Sur le référentiel — consultation seule

Critère 3. L'écran de composition d'US-REF-03 porte déjà une ligne de détail dépliable
(§ 3.15) prévue pour les prérequis et les instructeurs qualifiés. **Ajoute-y les
objectifs**, en lecture seule.

Aucune action de modification depuis le référentiel : les objectifs appartiennent au
catalogue, on les modifie depuis la matière. Sinon deux chemins d'écriture
coexisteraient sur la même donnée, et l'un des deux finirait par oublier une règle.

`npm run css:build` avant les tests d'interface.

---

# 7 · Tests

| Test | Vérifie |
|---|---|
| Une matière porte plusieurs objectifs | Critère 1 |
| Libellé et ordre sont obligatoires ; libellé vide refusé **en base** | Critère 2 |
| Deux objectifs de même ordre sur la même matière → refus | § 2.2 |
| Deux objectifs de même ordre sur **deux matières** → accepté | § 2.2 |
| **Échange de deux positions dans une transaction → réussit** | § 2.2 |
| Le même échange hors transaction → échoue | § 2.2 |
| Suppression d'un objectif : la matière et ses autres objectifs intacts | Critère 4 |
| Suppression du numéro 2 sur cinq : aucune renumérotation | § 2.2 |
| Suppression d'une matière → ses objectifs disparaissent | `CASCADE` |
| Les objectifs sont visibles depuis le référentiel de **chaque** formation utilisatrice | Critère 3 |
| Aucune action d'écriture n'est offerte depuis l'écran de référentiel | § 6.2 |
| `ObjectifPedagogique` ne porte aucune clé vers `Formation` ni `ElementReferentiel` | § 2.1 |
| L'entité **n'a pas** de champ d'archivage | § 2.3 |
| Création, modification, suppression journalisées | Extension de RG-26 |
| Cellule pédagogique écrit ; les trois autres lisent seulement | RG-02 |

Le cinquième et le sixième forment une paire : le second prouve que le premier ne
réussit pas par accident. Si l'échange hors transaction réussit aussi, la contrainte
n'est pas différée — elle est absente.

## Non-régression

La suite complète des huit stories précédentes passe sans modification.

---

# 8 · Vérification et livraison

- Les quinze tests d'architecture passent
- `ruff check` et `ruff format --check` propres
- Migration unique et réversible ; **vérifie que la contrainte différée figure bien dans
  le SQL produit** par `sqlmigrate`, et rends-le-moi
- `npm run css:build` rejoué
- Relecture par le sous-agent `relecteur-conception`
- `docs/suivi/` : l'exception à la règle d'archivage et sa justification, le retour du
  patron, le temps réel passé
- Commit portant la ligne de traçabilité

---

# 9 · Hors périmètre

- Les prérequis entre matières → **US-REF-06**
- La consultation par les autres cellules → **US-REF-07**
- Le rattachement d'un objectif à une évaluation → non prévu au cahier des charges
- Toute pondération, tout niveau taxonomique : le critère 2 énonce deux attributs, pas
  trois

# 10 · Définition de fini

Les quatre critères sont couverts par un test nommé, l'ordre est unique par matière et
la contrainte est différée — prouvée par la paire de tests transaction / hors
transaction et visible dans le SQL de migration —, la suppression est réelle et
justifiée comme exception à la règle d'archivage, les objectifs sont visibles en lecture
seule depuis le référentiel, et la suite complète des stories précédentes passe sans
modification.

Commence par l'étape 0.
