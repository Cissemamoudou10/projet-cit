# Prompt Claude Code — 06 · US-REF-01 · Gérer les formations

> Sprint 1, ligne WBS 5.1.7. Must, 3 points, 3,9 h estimées.
> Prérequis : US-REF-00 est finie — `ServiceGestion` et les gabarits génériques
> existent, ainsi que `TypeFormation`.
> À coller dans une session neuve, après `/clear`.

---

Nous développons **US-REF-01 — Gérer les formations**, cas d'utilisation **CU-P2-02**,
fiche **générique plus trois écarts**.

Le patron `ServiceGestion` a été écrit pour cette story autant que pour la précédente.
**Si tu écris ici du code qui n'a rien de propre aux formations, c'est que le patron
est incomplet** — remonte-le plutôt que de le dupliquer, et dis-le-moi.

Tu suis les huit étapes du workflow `/story`, avec arrêt obligatoire sur ma validation.

## Traçabilité

`BF-REF-01 → US-REF-01 → CU-P2-02 → RG-05 → CLS-02`

---

# 1 · Le besoin

*En tant que membre de la cellule pédagogique, je veux créer, consulter, modifier et
archiver une formation, afin de tenir à jour le catalogue des formations dispensées.*

## Critères d'acceptation — backlog v7

1. La création d'une formation renseigne **intitulé, spécialité, durée et type de
   formation**.
2. L'intitulé est unique.
3. Une formation archivée **n'apparaît plus dans les listes de sélection mais reste
   consultable**.
4. Une formation disposant de **sessions ouvertes** ne peut être supprimée.
5. Seule la cellule pédagogique dispose des droits de création et de modification.

## Deux critères hérités d'US-REF-00

Reportés lors de la story précédente, ils se vérifient ici :

- Une formation est rattachée à **un type et un seul**.
- Les listes de formations sont **filtrables par type**.

## Les trois écarts à la fiche générique

1. **L'intitulé est unique au sein d'un type de formation.**
2. Le rattachement à un type est **obligatoire**.
3. **L'archivage remplace la suppression dès qu'une session a été ouverte** sur la
   formation.

## Règle métier

**RG-05** — Le référentiel appartient à la formation. Aucune matière n'est jamais
rattachée directement à une brigade ni à une session. Cette story ne l'implante pas,
mais elle en pose le porteur : c'est la formation, et rien d'autre, qui portera le
référentiel en US-REF-03.

---

# 2 · Trois arbitrages qui me reviennent — tu les poses, tu ne les tranches pas

## 2.1 · Une contradiction entre deux livrables

Le backlog v7 dit *l'intitulé est unique*. La fiche des cas d'utilisation v4 dit
*l'intitulé est unique au sein d'un type de formation*. Les deux documents portent la
même date. Ce n'est pas une nuance : l'un interdit deux formations homonymes dans tout
le centre, l'autre les autorise dès lors qu'elles s'adressent à des publics différents.

**Implante la version de la fiche** — unicité du couple type-intitulé, contrainte
composite nommée `uq_formation_type_intitule` — parce qu'elle est la plus précise, et
parce qu'une *formation initiale* pour officiers et une *formation initiale* pour
sous-officiers sont deux objets légitimes.

**Consigne l'écart dans `docs/suivi/`** : le backlog devra être corrigé, ou l'arbitrage
inversé. Je tranche avec le chef de bureau pédagogique.

## 2.2 · L'unité de la durée n'est écrite nulle part

Aucun livrable ne dit si la durée d'une formation s'exprime en semaines, en jours ou en
heures. Elle n'est pas dérivable : le volume horaire prescrit appartient au référentiel,
et les dates appartiennent à la session.

**Propose la semaine**, entier strictement positif, cohérente avec le programme
hebdomadaire qui est l'unité de travail du centre. Nomme le champ de façon à ce que
l'unité soit lisible sans documentation, et affiche-la dans le formulaire.

Signale-le : c'est une question pour le terrain, pas pour nous.

## 2.3 · La spécialité n'est pas définie

Est-ce un texte libre ou une valeur d'une liste fermée ? Aucun livrable ne l'établit,
et aucune entité *spécialité* n'existe au diagramme de classes.

**Retiens le texte libre** pour cette story. Une énumération inventée maintenant serait
fausse, et une entité créée sans besoin alourdirait le modèle. Signale la question.

Attention à ne pas confondre : la spécialité qualifie la formation, **pas la brigade**.
La brigade est un outil de séparation des effectifs, jamais une spécialité pédagogique.

---

# 3 · Deux décisions déjà tranchées

## 3.1 · Le critère 4 n'est pas testable, et son mécanisme se pose quand même

Les sessions appartiennent au paquetage P3, sprint 2. On ne peut donc ni créer une
session ouverte, ni vérifier qu'elle bloque la suppression.

Ce qui se fait maintenant : le service expose une méthode qui **énumère les éléments
s'opposant à la suppression** — c'est déjà ce qu'exige E3 de la fiche générique. Elle
ne consulte aujourd'hui que le référentiel, et **US-SES-01 y ajoutera les sessions**.

Écris-la de façon à ce que l'ajout soit une ligne, pas une reprise. Et consigne le
report dans `docs/suivi/` : *critère 4 d'US-REF-01, vérifié à US-SES-01*.

## 3.2 · Le type est protégé en base

`on_delete=PROTECT` sur la clé étrangère vers `TypeFormation`. C'est la contrainte qui
rend vrai le critère 3 d'US-REF-00 — *un type utilisé par au moins une formation ne
peut être supprimé* —, jusqu'ici sans porteur.

Le service double la contrainte par un contrôle qui produit le message d'E3, avec
l'énumération des formations concernées. La contrainte protège, le service explique.

**Le rattachement est obligatoire** : champ non nul, écart 2.

---

# 4 · Étape 0 — Explorer

Lis `app/noyau/services/gestion.py` et les gabarits génériques, `app/referentiel/` en
entier, et la note d'implémentation, section sur la correspondance des types.

Rends-moi **ce que le patron couvre déjà et ce qu'il te manque**. Cette réponse
m'intéresse plus que la story elle-même : elle dit si l'investissement d'US-REF-00
porte.

# 5 · Étape 1 — Planifier. Attends ma validation.

Plan complet, plus tes propositions sur les trois arbitrages du § 2. **N'écris rien
avant mon accord.**

---

# 6 · Le modèle

`Formation`, héritant de `ModeleHorodate` et du mixin d'archivage.

| Attribut | Type | Contrainte |
|---|---|---|
| `intitule` | `CharField` | Unique **avec** le type |
| `specialite` | `CharField` | Texte libre — § 2.3 |
| `duree_semaines` | entier positif | Strictement positif, contrainte de vérification — § 2.2 |
| `type_formation` | clé étrangère | **Non nul**, `PROTECT` |

`Meta.db_table = "referentiel_formation"`.

Contraintes portées **en base**, nommées :

- `uq_formation_type_intitule` — unicité du couple
- `ck_formation_duree_positive` — durée strictement positive

La durée nulle ou négative se refuse au niveau de PostgreSQL, pas seulement dans un
`clean()`. Le test devra l'écrire directement en base pour le prouver.

---

# 7 · Les écrans

Bâtis sur les gabarits génériques. Ce qui s'ajoute :

**Liste** — filtre par type (§ 3.11) avec jetons (§ 3.12) : c'est le critère hérité
d'US-REF-00. Colonnes : intitulé, type, spécialité, durée, état. Recherche sur
l'intitulé et la spécialité.

**Formulaire** — quatre champs, formulaire à deux colonnes (§ 3.24) : *Identification*
— intitulé, spécialité — et *Rattachement* — type, durée. Liste déroulante (§ 3.20)
pour le type, **n'offrant que les types non archivés**. Champ numérique à unité
accolée (§ 3.18) pour la durée, l'unité étant affichée.

**Détail** — la formation, son type, et un emplacement pour son référentiel, qui reste
vide jusqu'à US-REF-03. Prévois-le sans le remplir.

**Liste des types** — la colonne *nombre de formations rattachées*, laissée vide à
US-REF-00, se remplit maintenant. Ne l'oublie pas : c'est le genre de reste qui
survit jusqu'à la soutenance.

`npm run css:build` avant les tests d'interface.

---

# 8 · Tests

| Test | Vérifie |
|---|---|
| Deux formations de même intitulé dans **deux types différents** → acceptées | Écart 1 |
| Deux formations de même intitulé dans **le même type** → refus désignant l'existante | Écart 1, E2 |
| L'unicité est imposée **en base**, en contournant l'ORM | § 6 |
| Création sans type → refus | Écart 2 |
| Durée nulle ou négative → refus **en base** | § 6 |
| Suppression d'un type portant une formation → refus, formations énumérées | US-REF-00 critère 3 |
| Formation archivée : absente des listes de sélection, présente en consultation | Critère 3 |
| La liste se filtre par type | Critère hérité d'US-REF-00 |
| La liste déroulante n'offre pas les types archivés | § 7 |
| Cellule pédagogique écrit ; les trois autres profils lisent seulement | Critère 5 |
| Création, modification, archivage journalisés | Extension de RG-26 |
| Modification concurrente détectée | E5 |
| La colonne *nombre de formations* du type est exacte | § 7 |

## Non-régression

La suite complète des cinq stories précédentes passe sans modification. Si les tests
d'US-REF-00 échouent après une remontée de code dans le patron, **c'est la remontée
qui est fautive**.

---

# 9 · Vérification et livraison

- Les quinze tests d'architecture passent
- `ruff check` et `ruff format --check` propres
- Migration unique et réversible, `makemigrations --check --dry-run` muet
- `npm run css:build` rejoué
- Relecture par le sous-agent `relecteur-conception`
- `docs/suivi/` : les trois arbitrages du § 2, le report du critère 4 vers US-SES-01,
  ce qui a été remonté dans le patron, le temps réel passé
- Commit portant la ligne de traçabilité

---

# 10 · Hors périmètre

- Le référentiel de la formation — matières, volumes, catégories de lieu →
  **US-REF-03**
- Les prérequis → **US-REF-06**
- Les sessions et le blocage de suppression qu'elles entraînent → **US-SES-01**,
  sprint 2
- La duplication d'un référentiel existant → Could, non planifiée
- L'historique des modifications → **US-REF-09**, Should

# 11 · Définition de fini

Les cinq critères d'acceptation et les deux critères hérités sont couverts par un test
nommé, l'unicité composite et la durée positive sont portées en base et prouvées en
contournant l'ORM, le type est protégé contre la suppression, les trois arbitrages sont
posés et consignés sans être tranchés, le critère 4 est reporté avec sa trace, et la
suite complète des stories précédentes passe sans modification.

Commence par l'étape 0.
