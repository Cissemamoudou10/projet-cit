# Prompt Claude Code — 14 · US-PLAN-02 · Gérer les lieux d'enseignement

> Sprint 1, ligne WBS 5.1.16. Must, 3 points, 3,9 h estimées.
> Prérequis : US-INS-02 est finie. **Dernière story du sprint 1.**
> À coller dans une session neuve, après `/clear`.

---

Nous développons **US-PLAN-02 — Gérer les lieux d'enseignement**, cas d'utilisation
**CU-P4-06**, fiche **générique plus écarts**.

Deux choses la distinguent des précédentes. L'acteur change : **c'est la cellule
planification qui écrit**, la pédagogie n'ayant que la lecture — l'inverse des deux
stories précédentes. Et elle emploie pour la première fois l'extension `btree_gist`
installée au socle, restée jusqu'ici sans usage.

Tu suis les huit étapes du workflow `/story`, avec arrêt obligatoire sur ma validation.

## Traçabilité

`BF-PLAN-02 → US-PLAN-02 → CU-P4-06 → RG-37 → CLS-04`

---

# 1 · Le besoin

*En tant que membre de la cellule planification, je veux gérer les lieux et leurs
capacités, afin de disposer d'un inventaire fiable pour les affectations.*

## Critères d'acceptation — backlog v7

1. Un lieu comporte un **intitulé, une capacité et une catégorie** : salle attitrable ou
   lieu partagé.
2. Les lieux partagés précisent leur type : **amphithéâtre, laboratoire ou salle
   spécialisée**.
3. Un lieu peut être **déclaré indisponible sur une période**.
4. Un lieu **affecté à une brigade ou à une séance ne peut être supprimé**.
5. La liste est **filtrable par catégorie, par capacité et par disponibilité**.

---

# 2 · Deux catégories ici, trois catégories là — ne les confonds pas

C'est le piège de cette story, et il est facile à ne pas voir.

**US-REF-04 a posé trois catégories** sur la matière : *salle attitrée de la brigade*,
*lieu partagé*, *aucun lieu requis*. Ce sont des **exigences** portées par une matière.

**US-PLAN-02 pose deux catégories** sur le lieu : *salle attitrable* et *lieu partagé*.
Ce sont des **propriétés** d'un objet physique.

Il n'y a pas de troisième catégorie de lieu, parce que *aucun lieu requis* ne désigne
rien de physique : une matière qui ne demande aucun lieu ne consomme aucune ressource,
et il n'existe pas de lieu nommé « aucun ». La place d'armes et les terrains de sport
n'entrent pas à l'inventaire.

**N'ajoute donc aucune valeur d'énumération pour les représenter**, et ne réutilise pas
l'énumération d'US-REF-04. Ce sont deux notions distinctes qui se ressemblent.

Le mot *attitrable* est le bon : le lieu **peut** être attitré à une brigade — il ne
l'est pas encore. L'attribution effective viendra avec les brigades, au sprint 2.

---

# 3 · Trois décisions déjà tranchées

## 3.1 · L'indisponibilité de lieu est une entité, et elle exerce enfin `btree_gist`

Le critère 3 demande de déclarer un lieu indisponible sur une période. C'est donc une
seconde entité, `IndisponibiliteLieu`, avec une période et un motif.

**Deux périodes d'indisponibilité d'un même lieu ne doivent pas se chevaucher.** Un
chevauchement n'est pas faux au sens strict — l'union des deux reste juste —, mais il
signale une double saisie, et il rendra illisible tout affichage de calendrier.

PostgreSQL sait l'interdire, par une **contrainte d'exclusion** sur le lieu et
l'intervalle. C'est exactement ce pour quoi le socle a installé `btree_gist`, et
**c'est son premier usage réel**.

Deux raisons de le faire ici plutôt que d'attendre. La contrainte est exprimable en SQL,
donc elle doit y être — c'est le principe du projet. Et surtout, **US-INS-03 posera la
même contrainte sur les indisponibilités d'instructeur au sprint 2** : la valider ici,
sur un cas simple, retire le doute avant qu'une story plus lourde en dépende.

Granularité horaire, comme pour les instructeurs : une salle peut être prise une
demi-journée.

## 3.2 · Le type de lieu partagé est conditionnel, et la condition va en base

Comme pour la catégorie de lieu du référentiel à US-REF-03 : le type — amphithéâtre,
laboratoire, salle spécialisée — est renseigné **si et seulement si** la catégorie vaut
*lieu partagé*.

Contrainte de vérification exprimant l'équivalence, nommée
`ck_lieu_type_partage_coherent`. Ni un `clean()`, ni un contrôle de formulaire : SQL sait
le dire.

Tu as déjà écrit exactement cette contrainte à US-REF-03. Reprends la même forme, pour
que les deux se lisent pareil.

## 3.3 · Le critère 4 se reporte deux fois

Les brigades appartiennent au paquetage P3, sprint 2. Les séances au paquetage P5,
sprint 3.

Reprends la méthode d'énumération des éléments bloquants. Elle ne trouvera rien
aujourd'hui ; **US-SES-02 y ajoutera les brigades attitrées** et **US-PLAN-03 les
séances**.

Consigne les deux reports séparément : ils se referment à des moments différents.

---

# 4 · Un arbitrage que je te demande de poser

**Filtrer « par disponibilité » suppose une date.** Le critère 5 l'exige sans dire par
rapport à quand : un lieu n'est pas disponible dans l'absolu, il l'est à un moment.

Trois lectures possibles : disponible aujourd'hui, disponible sur une période saisie par
l'agent, ou simplement *ne portant aucune indisponibilité future*.

**Propose la deuxième**, avec la date du jour comme valeur par défaut : c'est la seule
qui serve réellement la cellule planification, qui cherche une salle pour une semaine
donnée. Argumente en deux phrases, je tranche.

---

# 5 · Étape 0 — Explorer

Lis `app/ressources/` en entier, `app/noyau/services/gestion.py`, la migration
`0001_extensions` du socle, et la contrainte de cohérence écrite à US-REF-03.

Dans `docs/charte/` : **3.08**, **3.10**, **3.11**, **3.12**, **3.13**, **3.17**,
**3.18** pour la capacité, **3.19** pour les bornes de période, **3.20**, **3.24**,
**3.25**, **3.29**, **3.32**, **3.39**, **3.40**.

**Vérifie et rends-moi** que l'extension `btree_gist` est bien présente dans la base de
développement et que la migration du socle l'a posée. Si elle manque, arrête-toi : le
reste en dépend.

# 6 · Étape 1 — Planifier. Attends ma validation.

Plan complet, la forme exacte de la contrainte d'exclusion, et ta proposition sur le § 4.
**N'écris rien avant mon accord.**

---

# 7 · Le modèle

## 7.1 · `Lieu`

Héritant de `ModeleHorodate` et du mixin d'archivage.

| Attribut | Type | Contrainte |
|---|---|---|
| `intitule` | `CharField` | **Unique** |
| `capacite` | entier positif | **Strictement positive** |
| `categorie` | énumération à deux valeurs | Non nul — § 2 |
| `type_partage` | énumération à trois valeurs, nullable | Renseigné **si et seulement si** la catégorie vaut *lieu partagé* |

`Meta.db_table = "ressources_lieu"`.

Contraintes portées **en base**, nommées : `uq_lieu_intitule`,
`ck_lieu_capacite_positive`, `ck_lieu_type_partage_coherent`.

La capacité strictement positive n'est pas une coquetterie : RG-37 comparera l'effectif
d'une brigade à cette valeur, et une capacité nulle produirait un lieu que rien ne peut
jamais occuper, sans que personne comprenne pourquoi.

## 7.2 · `IndisponibiliteLieu`

| Attribut | Type | Contrainte |
|---|---|---|
| `lieu` | clé étrangère `Lieu` | Non nul, `CASCADE` |
| `debut`, `fin` | date-heure | `fin` strictement postérieure à `debut` |
| `motif` | texte | Non vide |

`Meta.db_table = "ressources_indisponibilite_lieu"`.

Contraintes en base :

- `ck_indispo_lieu_periode` — la fin après le début
- `ex_indispo_lieu_chevauchement` — **contrainte d'exclusion** interdisant deux périodes
  qui se recouvrent pour le même lieu, § 3.1

La migration qui pose la contrainte d'exclusion **déclare une dépendance explicite sur
`("noyau", "0001_extensions")`** : c'est la règle inscrite dans `.claude/rules/migrations.md`
au socle. Sans elle, l'ordre d'exécution sur une base neuve n'est pas garanti, et la
migration échouera au déploiement au CIT — jamais en développement.

---

# 8 · Les écrans

Bâtis sur les gabarits génériques.

**Liste** — tableau dense (§ 3.08), pagination (§ 3.10). Colonnes : intitulé, catégorie,
type, capacité, état de disponibilité, état d'archivage.

Filtres (§ 3.11) avec jetons (§ 3.12) : **catégorie**, **capacité minimale** — champ
numérique, pas une liste —, et **disponibilité** selon l'arbitrage du § 4.

**Badge de catégorie** — motif du § 3.29, couleur **doublée d'un mot** (charte § 1.2).

**Formulaire** — deux colonnes (§ 3.24) : *Identification* — intitulé, capacité — et
*Nature* — catégorie, type. Champ numérique à unité accolée (§ 3.18) pour la capacité,
l'unité étant la place. Le champ *type* n'apparaît que pour un lieu partagé.

**Fiche** — le lieu, ses indisponibilités en tableau, et un emplacement réservé pour les
brigades attitrées, **vide jusqu'au sprint 2**.

**Déclaration d'indisponibilité** — bornes de période (§ 3.19), motif en zone de texte
(§ 3.22). Un chevauchement refusé produit un message d'erreur nommant **la période
existante** qui s'y oppose : « indisponible » sans dire depuis quand est inexploitable.

**Archivage** — dialogue de confirmation (§ 3.32), BNF-09.

`npm run css:build` avant les tests d'interface.

---

# 9 · Tests

## Le modèle

| Test | Vérifie |
|---|---|
| Création avec intitulé, capacité, catégorie | Critère 1 |
| Intitulé dupliqué → refus **en base** | § 7.1 |
| Capacité nulle ou négative → refus **en base** | § 7.1 |
| Catégorie *lieu partagé* sans type → refus **en base** | Critère 2, § 3.2 |
| Catégorie *salle attitrable* avec un type → refus **en base** | § 3.2 |
| L'énumération de catégorie compte **deux** valeurs, pas trois | § 2 |
| Elle n'est pas celle d'US-REF-04 | § 2 |

## L'indisponibilité et la contrainte d'exclusion

| Test | Vérifie |
|---|---|
| Déclaration d'une période sur un lieu | Critère 3 |
| Fin antérieure au début → refus **en base** | § 7.2 |
| **Deux périodes qui se recouvrent sur le même lieu → refus en base** | § 3.1 |
| Deux périodes **contiguës** sans recouvrement → acceptées | § 3.1 |
| Deux périodes qui se recouvrent sur **deux lieux différents** → acceptées | § 3.1 |
| Le message d'erreur nomme la période existante | § 8 |
| Suppression d'un lieu → ses indisponibilités disparaissent | `CASCADE` |

Les trois tests d'exclusion doivent écrire **directement en base**, en contournant l'ORM.
Le test des périodes contiguës est celui qu'on oublie : une contrainte mal écrite refuse
aussi les périodes qui se touchent sans se recouvrir, et la cellule planification ne
peut plus déclarer deux indisponibilités successives.

## La liste et l'habilitation

| Test | Vérifie |
|---|---|
| Filtre par catégorie | Critère 5 |
| Filtre par capacité minimale | Critère 5 |
| Filtre par disponibilité, selon l'arbitrage du § 4 | Critère 5 |
| Liste paginée au-delà de vingt lieux | BNF-15 |
| La méthode d'énumération des bloquants existe et ne trouve rien | Critère 4, § 3.3 |
| **Cellule planification écrit** | Matrice § 11.2 |
| **Cellule pédagogique lit seulement** | Matrice § 11.2 |
| Examens et Direction de Formation lisent seulement | Matrice § 11.2 |
| Création, modification, archivage journalisés | Extension de RG-26 |
| `DOMAINE` déclaré et présent au catalogue | Test d'architecture |

Les deux tests d'habilitation en gras sont l'inverse des deux stories précédentes. Écris
-les explicitement : c'est le genre d'inversion qu'on reproduit par habitude et qu'on ne
voit qu'en recette.

## Non-régression

La suite complète des treize stories précédentes passe sans modification.

---

# 10 · Vérification et livraison

- Les quinze tests d'architecture passent
- `ruff check` et `ruff format --check` propres
- Migration unique et réversible, **dépendant explicitement de `noyau.0001_extensions`**
- `makemigrations --check --dry-run` muet
- `npm run css:build` rejoué
- Relecture par le sous-agent `relecteur-conception`
- `docs/suivi/` : l'arbitrage du § 4, les deux reports du § 3.3, **la confirmation que
  `btree_gist` fonctionne**, le temps réel passé
- Commit portant la ligne de traçabilité

---

# 11 · Fin du sprint 1

Cette story close, les quinze stories du sprint sont livrées. **Rends-moi un état
complet des reports** consignés depuis US-REF-00 : lesquels sont refermés, lesquels
restent ouverts, vers quelle story chacun pointe. Il alimentera la revue du 12
septembre.

---

# 12 · Hors périmètre

- L'attribution d'une salle attitrée à une brigade → **US-SES-02**, sprint 2
- L'affectation d'un lieu partagé à une séance → **US-PLAN-03**, sprint 3
- Le contrôle de RG-37 — lieu disponible et capacité suffisante → **sprint 3**. Cette
  story pose la donnée, le contrôle est ailleurs
- Les indisponibilités d'instructeur → **US-INS-03**, sprint 2, même mécanisme
- Le calendrier académique → **US-PLAN-01**, sprint 2
- La substitution de salle en cas d'indisponibilité imprévue : **décision humaine que le
  système enregistre sans l'automatiser**, sprint 3

# 13 · Définition de fini

Les cinq critères sont couverts par un test nommé ou consignés comme reportés, les deux
catégories de lieu sont distinctes de celles du référentiel et prouvées telles, la
cohérence du type est portée en base, la contrainte d'exclusion refuse les
chevauchements et accepte les périodes contiguës, l'inversion des habilitations est
testée explicitement, l'état des reports du sprint est rendu, et la suite complète des
stories précédentes passe sans modification.

Commence par l'étape 0.
