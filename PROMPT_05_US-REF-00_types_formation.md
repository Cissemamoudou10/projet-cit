# Prompt Claude Code — 05 · US-REF-00 · Gérer les types de formation

> Sprint 1, ligne WBS 5.1.6. Must, 2 points, 2,6 h estimées.
> Prérequis : le paquetage P1 est complet — permissions, journal, habilitations.
> À coller dans une session neuve, après `/clear`.

---

Nous développons **US-REF-00 — Gérer les types de formation**, cas d'utilisation
**CU-P2-01**, premier du paquetage P2.

**Cette story vaut plus que son objet.** Le type de formation est l'entité la plus
simple du système : un intitulé, rien d'autre. Mais sa fiche de cas d'utilisation est
la **fiche générique de gestion**, celle que suivent aussi CU-P2-02, CU-P2-03,
CU-P2-06 et CU-P2-08. Ce que tu écris ici sera repris cinq fois. Tu écris donc un
**patron réutilisable** en même temps que la story.

Tu suis les huit étapes du workflow `/story`, avec arrêt obligatoire sur ma validation.

## Traçabilité

`BF-REF-08 → US-REF-00 → CU-P2-01 → fiche générique → CLS-02`

---

# 1 · Le besoin

*En tant que membre de la cellule pédagogique, je veux gérer les types de formation,
afin de classer les formations selon le public auquel elles s'adressent.*

## Critères d'acceptation — backlog v7

1. Un type de formation comporte un **intitulé unique** — par exemple officiers,
   sous-officiers, CAT-2.
2. Une formation est rattachée à **un type et un seul**.
3. Un type **utilisé par au moins une formation ne peut être supprimé**.
4. Les listes de formations sont **filtrables par type**.

**Les critères 2 et 4 ne sont pas testables ici** : l'entité Formation n'existe pas
encore, elle arrive avec US-REF-01. Cette story livre le côté qui lui revient — le
modèle et son unicité — et **US-REF-01 portera la vérification des critères 2 et 4**.
Consigne-le dans `docs/suivi/` : un critère reporté sans trace est un critère perdu.

## La fiche générique de gestion

**Consultation.** L'acteur accède à la liste ; le système la présente **paginée et
dotée d'une recherche** dès que le nombre d'éléments peut dépasser vingt (BNF-15) ;
l'acteur filtre, puis ouvre le détail.

**Création.** L'acteur demande la création ; le système présente le formulaire, **en
français et avec la terminologie en usage au CIT** (BNF-08) ; l'acteur saisit et
valide ; le système contrôle champs obligatoires, formats, unicité et règles propres ;
il enregistre, horodate, rattache à l'auteur et confirme.

**Modification.** Mêmes points, **l'ancienne valeur étant conservée au journal si
l'action est sensible**.

**Archivage.** L'acteur demande l'archivage ; le système vérifie qu'aucune dépendance
ne s'y oppose ; il demande une **confirmation explicite** (BNF-09) ; l'élément est
archivé : il n'apparaît plus dans les listes de sélection mais **demeure dans
l'historique et dans les données qui le référencent**.

## Les cinq exceptions communes

| Code | Comportement |
|---|---|
| **E1** | Champ obligatoire manquant ou format invalide → refus, message indiquant la cause **et l'action corrective attendue** (BNF-10) |
| **E2** | Violation d'unicité → refus **avec désignation de l'élément existant** |
| **E3** | Élément référencé → archivage ou suppression refusé, **avec énumération des éléments qui s'y opposent** |
| **E4** | Habilitation insuffisante → refus **sans divulguer l'existence de l'élément** (RG-02, BNF-01) |
| **E5** | Modification concurrente → le second agent est averti que la donnée a changé depuis son ouverture et **doit reprendre sa saisie** |

## La règle générale

**L'archivage remplace la suppression** dès qu'un élément est référencé par une donnée
historique. La suppression physique n'est offerte que pour des éléments **jamais
utilisés**. Elle vaut pour tout le système et découle de BNF-14 : un système dont on
peut effacer les éléments perd la capacité de rendre compte a posteriori.

---

# 2 · Six décisions déjà tranchées

## 2.1 · Tu écris un patron, pas seulement une story

Crée dans `app/noyau/services/gestion.py` une classe `ServiceGestion`, base des
services de gestion, portant le déroulement générique : lister avec pagination et
recherche, créer, modifier, archiver, désarchiver, supprimer si jamais référencé.
Les cinq exceptions y sont traitées une fois pour toutes.

Crée de même les gabarits génériques dans `app/noyau/templates/noyau/gestion/` :
liste, formulaire, dialogue de confirmation d'archivage. Ils prennent en paramètre les
colonnes, les filtres et les libellés.

`ServiceTypeFormation` en hérite et ne déclare que ce qui lui est propre. **Si tu te
surprends à écrire du code qui n'a rien de spécifique aux types de formation, il
appartient au patron.**

C'est un investissement : cette story coûtera plus que ses 2,6 heures. Il se
rembourse sur US-REF-01, US-REF-02, US-REF-05 et US-REF-07, qui suivent la même
fiche. Relève le temps passé séparément — sur le patron d'une part, sur la story de
l'autre. J'en ai besoin pour le jalon du 12 septembre.

## 2.2 · E5 se traite par `modifie_le`, sans champ supplémentaire

La détection de modification concurrente demande un jeton de version. `ModeleHorodate`
en fournit déjà un : `modifie_le`.

Le formulaire transporte la valeur lue à l'ouverture, dans un champ caché ; le service
compare avant d'écrire ; si elle diffère, il lève `ErreurModificationConcurrente` et
l'agent reprend sa saisie.

**La comparaison est faite dans le service, pas dans le formulaire** : le formulaire
ignore ce qui est en base au moment de l'écriture.

Le message dit ce qui s'est passé et **qui a modifié** — l'auteur est dans
`modifie_par`. Sur un centre où trois cellules travaillent sur les mêmes données,
savoir à qui parler vaut mieux que « la donnée a changé ».

## 2.3 · Archivage et suppression coexistent, et c'est délibéré

Deux actions distinctes, deux comportements :

| Action | Condition | Effet |
|---|---|---|
| **Archiver** | Toujours possible | Disparaît des listes de sélection, reste consultable et référencé |
| **Supprimer** | Seulement si **jamais référencé** | Disparaît définitivement |

Le critère 3 exige le refus de suppression d'un type utilisé. Porte-le **en base** par
`on_delete=PROTECT` sur la clé étrangère que posera US-REF-01, **et** dans le service
par un contrôle préalable qui produit le message d'E3 — l'énumération des éléments qui
s'y opposent. La contrainte protège, le service explique.

Le champ d'archivage vient du patron, pas du modèle de type : `archive`, booléen, et
`archive_le`. Toutes les entités de gestion en hériteront.

## 2.4 · Le filtrage par défaut masque les archivés

Une liste de sélection ne montre jamais un élément archivé ; une liste de consultation
le montre, signalé. Le patron porte les deux comportements, la vue choisit.

C'est la traduction directe de « n'apparaît plus dans les listes de sélection mais
demeure consultable ».

## 2.5 · Habilitation

Écriture : `referentiel_ecriture`, cellule pédagogique seule.
Lecture : `referentiel_lecture`, planification, examens, Direction de Formation.

`ServiceTypeFormation.DOMAINE = "referentiel"` — le test d'architecture posé par
US-ADM-03 l'exige.

E4 impose un refus **qui ne divulgue pas l'existence de l'élément**. Un refus sur une
fiche inexistante et un refus sur une fiche interdite doivent être indiscernables.

## 2.6 · La question du journal, que je tranche maintenant

RG-26 énumère cinq actions sensibles ; **les modifications du référentiel n'en font
pas partie**. Pourtant US-REF-09 — *Consulter l'historique des modifications*, Should,
sprint 4 — suppose que cet historique existe.

Si nous attendons le sprint 4 pour le décider, l'historique de tout ce qui aura été
créé d'ici là sera perdu, et il ne se reconstitue pas.

**Décision : les créations, modifications et archivages du référentiel sont
journalisés dès maintenant**, par `ServiceJournal`, avec la liste blanche de champs.
Le coût est nul aujourd'hui — le patron le fait une fois pour les cinq stories — et la
perte serait irrécupérable.

**C'est une extension de RG-26**, la troisième après le refus d'habilitation et la
consultation du journal. Consigne-la dans `docs/suivi/` avec les deux autres : je les
porterai ensemble au cahier des charges à la revue du 12 septembre.

---

# 3 · Étape 0 — Explorer

Lis `app/noyau/` en entier — services, pagination, habilitations, exceptions,
gabarits —, `app/administration/services/comptes.py` comme exemple de service de
gestion déjà écrit, et `app/referentiel/`, qui ne contient que sa structure.

Dans `docs/charte/` : **3.08**, **3.09**, **3.10**, **3.11**, **3.12**, **3.13**,
**3.17**, **3.24**, **3.25**, **3.32**, **3.39**, **3.40**.

**Rends-moi ce qui, dans `ServiceCompte`, est générique et devrait remonter dans
`ServiceGestion`.** US-ADM-02 a été écrite avant que le patron existe ; si des pans
entiers s'y retrouvent, dis-le — mais **ne reprends pas `ServiceCompte` dans cette
story**. Je déciderai à part.

# 4 · Étape 1 — Planifier. Attends ma validation.

Plan complet, avec la séparation nette entre ce qui va dans le patron et ce qui reste
propre au type de formation. **N'écris rien avant mon accord.**

---

# 5 · Le modèle

`app/referentiel/models.py` — `TypeFormation`, héritant de `ModeleHorodate` et du
mixin d'archivage.

| Attribut | Type | Contrainte |
|---|---|---|
| `intitule` | `CharField` | **Unique**, non vide |
| `archive` | booléen | Du mixin |
| `archive_le` | date-heure, nullable | Du mixin |

`Meta.db_table = "referentiel_type_formation"` — le nom par défaut de Django violerait
la convention de nommage.

**L'unicité est portée en base**, contrainte nommée `uq_type_formation_intitule`. Le
message d'E2 remonte de la contrainte, pas d'un contrôle préalable : entre la
vérification et l'écriture, un autre agent peut avoir créé le même intitulé.

Question à trancher dans ton plan : l'unicité est-elle sensible à la casse ? Deux
types nommés *Officiers* et *officiers* doivent-ils coexister ? Propose, argumente en
deux phrases, je tranche.

---

# 6 · Les écrans

Trois, tous construits sur les gabarits génériques.

**Liste** — tableau dense (§ 3.08), tri (§ 3.09), pagination (§ 3.10), recherche sur
l'intitulé, filtre archivé / actif (§ 3.11) avec jetons (§ 3.12), état vide (§ 3.13).
Une colonne indique le nombre de formations rattachées : **elle sera vide jusqu'à
US-REF-01**, prévois-la sans la remplir.

**Formulaire** — un seul champ. Emploie tout de même le formulaire à deux colonnes
(§ 3.24) réduit à une, et le pied de formulaire (§ 3.25) sans brouillon.

**Confirmation d'archivage** — boîte de dialogue (§ 3.32), BNF-09. Elle énonce ce que
l'archivage fait et ne fait pas : disparition des listes de sélection, maintien dans
l'historique.

Navigation : la rubrique *Référentiel* apparaît, filtrée par `a_permission`.

`npm run css:build` avant les tests d'interface.

---

# 7 · Tests

## Le patron — dans `app/noyau/tests/`

Teste `ServiceGestion` **sur un modèle de test dédié**, pas sur `TypeFormation` : un
patron testé à travers un seul usage n'est pas un patron.

| Test | Vérifie |
|---|---|
| Liste paginée au-delà de vingt éléments | BNF-15 |
| Recherche restreint le résultat | BNF-15 |
| Les archivés sont masqués des listes de sélection, visibles en consultation | § 2.4 |
| Champ obligatoire manquant → refus avec cause et action corrective | E1 |
| Violation d'unicité → refus désignant l'élément existant | E2 |
| Élément référencé → archivage refusé, éléments opposants énumérés | E3 |
| Habilitation insuffisante → refus indiscernable d'une absence | E4 |
| `modifie_le` obsolète → `ErreurModificationConcurrente`, auteur nommé | E5 |
| Deux écritures concurrentes : la seconde échoue, la première tient | E5 |

## La story

| Test | Vérifie |
|---|---|
| Intitulé unique imposé **en base**, en contournant l'ORM | Critère 1 |
| Création, modification, archivage journalisés | § 2.6 |
| Un type archivé reste consultable | Règle générale |
| Cellule pédagogique écrit ; planification, examens, Direction lisent seulement | § 2.5 |
| `DOMAINE` déclaré | Test d'architecture |

Le premier de ces tests écrit **directement en base**, sans passer par `full_clean` :
un test qui passe par la validation Python ne prouve rien sur la contrainte.

## Non-régression

La suite complète des quatre stories du paquetage P1 passe sans modification.

---

# 8 · Vérification et livraison

- Les quinze tests d'architecture passent
- `ruff check` et `ruff format --check` propres
- Migration unique et réversible, `makemigrations --check --dry-run` muet
- `npm run css:build` rejoué
- Relecture par le sous-agent `relecteur-conception`
- `docs/suivi/` : le report des critères 2 et 4 vers US-REF-01, l'extension de RG-26
  au référentiel, l'arbitrage sur la casse, **le temps passé séparé entre patron et
  story**, et ce que `ServiceCompte` gagnerait à reprendre du patron
- Commit portant la ligne de traçabilité

---

# 9 · Hors périmètre

- L'entité Formation et sa clé étrangère vers le type → **US-REF-01**
- Le filtre par type sur les listes de formations → **US-REF-01**, critère 4
- La reprise de `ServiceCompte` sur le patron → décision séparée
- L'écran d'historique des modifications → **US-REF-09**, Should, sprint 4. Cette
  story alimente le journal, elle ne l'affiche pas

# 10 · Définition de fini

L'intitulé est unique par contrainte en base, les cinq exceptions communes sont
implantées dans le patron et testées sur un modèle dédié, l'archivage et la
suppression coexistent avec leurs conditions propres, la modification concurrente est
détectée sans champ supplémentaire, les modifications du référentiel sont journalisées,
les deux critères non testables sont consignés comme reportés, et le temps est relevé
séparément pour le patron et pour la story.

Commence par l'étape 0.
