# Prompt Claude Code — 04 · US-ADM-04 · Journaliser les actions sensibles

> Sprint 1, ligne WBS 5.1.5. Must, 3 points, 3,9 h estimées.
> Prérequis : US-ADM-03 est finie — le catalogue des dix-huit permissions existe.
> À coller dans une session neuve, après `/clear`.

---

Nous développons **US-ADM-04 — Journaliser les actions sensibles**, cas d'utilisation
**CU-P1-03**. Tu suis les huit étapes du workflow `/story`, avec arrêt obligatoire sur
ma validation avant l'implantation.

Le modèle `EntreeJournal` et `ServiceJournal.enregistrer()` existent déjà : ils ont été
remontés dans US-ADM-01 parce que CU-P1-01 posait la journalisation en postcondition.
Cette story livre **l'écran de consultation, l'immuabilité portée en base, et les
filtres** — pas le modèle.

## Traçabilité

`BF-ADM-04 → US-ADM-04 → CU-P1-03 → RG-26, RG-27 → CLS-01`

---

# 1 · Le besoin

*En tant que responsable de la sécurité, je veux que les actions sensibles soient
journalisées, afin de pouvoir retracer toute modification critique.*

## Critères d'acceptation — backlog v7

1. Toute saisie ou modification de note est journalisée avec **auteur, date et valeur
   précédente**.
2. Toute validation ou tout rejet de programme est journalisé.
3. Toute sélection de sujet d'examen est journalisée.

*Les critères suivants du backlog n'ont pas pu être relus intégralement. Les exigences
de consultation et d'immuabilité sont donc reprises ci-dessous depuis CU-P1-03 et
RG-27, qui font foi.*

## CU-P1-03 · Consulter le journal des actions sensibles

| | |
|---|---|
| **Acteur principal** | Administrateur |
| **Déclencheur** | Vérification a posteriori : contestation d'une note, doute sur une validation, contrôle réglementaire |
| **Préconditions** | L'administrateur dispose d'une session ouverte |
| **Postcondition** | Aucune modification de données ; **la consultation elle-même est journalisée** |

**Scénario nominal**

1. L'administrateur accède au journal.
2. Le système présente les entrées les plus récentes, paginées.
3. L'administrateur filtre par **nature d'action, auteur, période ou objet concerné**.
4. Le système présente les entrées correspondantes : horodatage, auteur, nature de
   l'action, objet concerné, **valeur avant et après lorsque l'action est une
   modification**.

**A1 — Consultation ciblée depuis un objet.** L'administrateur accède au journal depuis
la fiche d'une évaluation ou d'un programme ; le filtre sur l'objet est présélectionné.

**E1 — Aucune entrée.** Le système l'indique explicitement **et rappelle les filtres
appliqués**.

## Règles et exigences

| Code | Énoncé |
|---|---|
| **RG-26** | Sont journalisées, avec auteur et horodatage : la saisie et la modification d'une note, la validation ou le rejet d'un programme, la sélection d'un sujet d'examen, la création et la modification d'un compte, l'authentification échouée |
| **RG-27** | Une entrée est **immuable** : ni modifiable ni supprimable par aucun profil, administrateur compris. **Portée en base** au titre de BNF-11, et non seulement par l'interface |
| **BNF-02** | Restriction de consultation |
| **BNF-11** | Intégrité portée en base |
| **BNF-15** | Pagination et recherche |

---

# 2 · Six décisions déjà tranchées

## 2.1 · L'immuabilité passe par les privilèges, pas par le code applicatif

C'est le cœur de cette story, et la seule ligne du schéma où la sécurité repose sur
les privilèges plutôt que sur une contrainte. Le socle a provisionné deux rôles :
`pfe_cit_migration`, propriétaire, et `pfe_cit_app`, restreint, avec lequel
l'application se connecte.

Migration SQL explicite et réversible :

```sql
REVOKE UPDATE, DELETE ON administration_entree_journal FROM pfe_cit_app;
```

`INSERT` et `SELECT` restent. Le rôle de migration conserve tous ses droits : c'est
assumé et documenté — sans quoi aucune évolution de schéma ne serait possible.

## 2.2 · Le test d'immuabilité ouvre sa propre connexion — et c'est le piège

La suite de tests s'exécute avec `pfe_cit_migration`, qui a le droit de modifier la
table. Un test écrit naïvement passerait donc **en prouvant le contraire de ce qu'il
prétend**.

Le test doit ouvrir une **connexion explicite avec `pfe_cit_app`** et vérifier que
`UPDATE` et `DELETE` y sont refusés au niveau de PostgreSQL. Vérifie que la
configuration de test permet une seconde connexion, et si elle ne le permet pas,
signale-le plutôt que de contourner.

C'est le seul test de cette story qui prouve réellement RG-27.

## 2.3 · Aucune écriture au-delà de l'insertion

`ServiceJournal` n'expose ni modification ni suppression. Aucune vue, aucune URL,
aucun formulaire. Le modèle ne définit aucune méthode d'édition.

Trois barrières indépendantes : le service, l'absence de chemin d'interface, les
privilèges en base. Seule la troisième compte vraiment ; les deux autres évitent de
la découvrir en production.

## 2.4 · La consultation se journalise une fois par requête

CU-P1-03 pose que la consultation elle-même est journalisée. Une entrée **par
requête**, pas par ligne affichée ni par filtre appliqué. Elle enregistre les filtres
utilisés, pas le contenu retourné.

Sans cette précision, une page de vingt entrées en produirait vingt et une, et le
journal doublerait de volume à chaque lecture.

## 2.5 · La nature de l'action est une énumération complète dès maintenant

RG-26 énumère cinq natures. Trois concernent des objets qui n'existent pas encore —
notes, programmes, sujets. Déclare néanmoins **l'énumération complète**, pour que les
stories des sprints 2 à 4 n'aient qu'à s'y rattacher.

Deux natures s'ajoutent, qui ne figurent pas dans RG-26 :

- le **refus d'habilitation**, introduit par US-ADM-03 au titre de son critère 5
- la **consultation du journal**, exigée par la postcondition de CU-P1-03

**Signale-les dans `docs/suivi/`** : ce sont deux extensions de RG-26 que je porterai
au cahier des charges. Une nature journalisée sans règle d'origine est une rupture de
traçabilité.

## 2.6 · Ce qui est enregistré est choisi, jamais copié en bloc

`valeur_avant` et `valeur_apres` reçoivent une **liste blanche de champs déclarée par
le service appelant**, jamais une sérialisation complète de l'objet.

La raison est concrète : sérialiser un `Utilisateur` entier ferait entrer le condensat
du mot de passe dans une table conçue pour être lue par un administrateur, et
violerait BNF-03 par ricochet. Un test doit l'interdire explicitement.

---

# 3 · Étape 0 — Explorer

Lis `app/administration/models.py` (`EntreeJournal`),
`app/administration/services/journal.py`, `app/noyau/habilitations.py`,
`app/noyau/pagination.py`, la migration des rôles du socle, et
`config/settings/test.py`.

Dans `docs/charte/` : **3.08** (tableau dense), **3.09** (tri), **3.10** (pagination),
**3.11** (barre de filtres), **3.12** (jeton de filtre actif), **3.13** (état vide),
**3.15** (ligne de détail dépliable), **3.19** (plage horaire, pour les bornes de
période).

Rends-moi l'état du modèle et du service, et **dis-moi si la configuration de test
autorise une seconde connexion sous un rôle distinct**. Cette réponse conditionne § 2.2.

# 4 · Étape 1 — Planifier. Attends ma validation.

Plan complet, plus l'énumération des natures d'action et la structure retenue pour
`valeur_avant` / `valeur_apres`. **N'écris rien avant mon accord.**

---

# 5 · Le modèle et sa migration

Complète `EntreeJournal` si les champs de CU-P1-03 y manquent : horodatage, auteur,
nature, objet concerné — type et identifiant —, valeur avant, valeur après.

L'objet concerné se désigne par un couple *type d'objet* / *identifiant*, non par une
clé étrangère : les objets journalisés appartiennent à six applications, dont cinq
n'existent pas, et une clé étrangère les rendrait toutes dépendantes de
`administration`, à rebours du sens des couches.

**Index.** Le journal est la seule table du système qui croît sans borne. Pose au
minimum un index sur l'horodatage décroissant, et un index composé sur les colonnes de
filtre — nature, auteur. Sans eux, la pagination se dégradera au bout de quelques
mois, et le CIT n'aura personne pour diagnostiquer une requête lente.

Deux migrations distinctes : les champs et index d'une part, la révocation des
privilèges d'autre part. La seconde ne doit pas être rejouée par mégarde avec la
première.

---

# 6 · L'écran de consultation

Réservé à l'administrateur — permission `administration_lecture`, contrôlée **dans le
service**.

Tableau dense (§ 3.08), tri sur l'horodatage (§ 3.09), pagination (§ 3.10).

**Barre de filtres** (§ 3.11) : nature d'action, auteur, période — deux bornes —,
objet concerné. Jetons de filtre actif (§ 3.12), pour que l'administrateur voie
toujours ce qu'il regarde.

**Valeur avant et après** : elles ne tiennent pas dans une colonne. Emploie la ligne de
détail dépliable (§ 3.15), qui se déplie sans script.

**E1 — aucune entrée** : état vide (§ 3.13) **rappelant les filtres appliqués**. Un
« aucun résultat » sans rappel des filtres laisse croire que le journal est vide, ce
qui, sur un outil de contrôle, est une conclusion coûteuse.

**A1 — accès ciblé depuis un objet** : les fiches d'évaluation et de programme
n'existent pas encore. Livre le **contrat d'adresse** — les paramètres de requête qui
présélectionnent le filtre sur l'objet — et documente-le dans `docs/suivi/` pour que
les stories des sprints 3 et 4 s'y rattachent sans le réinventer.

---

# 7 · Tests

## Immuabilité — RG-27

| Test | Vérifie |
|---|---|
| `UPDATE` refusé sous `pfe_cit_app` | § 2.1, § 2.2 |
| `DELETE` refusé sous `pfe_cit_app` | § 2.1, § 2.2 |
| `INSERT` et `SELECT` restent possibles | Non-régression |
| La migration de révocation est réversible | Déploiement |
| `ServiceJournal` n'expose aucune méthode d'écriture hors insertion | § 2.3 |
| Aucune URL ni vue de modification ou de suppression n'existe | § 2.3 |

## Contenu

| Test | Vérifie |
|---|---|
| Une modification enregistre auteur, date, valeur précédente | Critère 1 |
| Seuls les champs de la liste blanche sont enregistrés | § 2.6 |
| Aucun condensat de mot de passe n'entre au journal | § 2.6, BNF-03 |
| L'énumération couvre les cinq natures de RG-26 plus les deux extensions | § 2.5 |

## Consultation

| Test | Vérifie |
|---|---|
| Un non-administrateur → refus | BNF-02 |
| Une consultation produit **une seule** entrée | § 2.4 |
| Vingt entrées affichées → une entrée de consultation, pas vingt et une | § 2.4 |
| Chaque filtre restreint effectivement le résultat | CU-P1-03, point 3 |
| Filtre sans résultat → état vide rappelant les filtres | E1 |
| Le contrat d'adresse présélectionne le filtre sur l'objet | A1 |
| Au-delà de vingt entrées → paginé | BNF-15 |

## Non-régression

La suite complète des trois stories précédentes passe sans modification.

---

# 8 · Vérification et livraison

- Les quinze tests d'architecture passent
- `ruff check` et `ruff format --check` propres
- Deux migrations distinctes, réversibles, `makemigrations --check --dry-run` muet
- `npm run css:build` rejoué
- Relecture par le sous-agent `relecteur-conception`
- `docs/suivi/` : les deux natures d'action hors RG-26, le contrat d'adresse d'A1, la
  réponse sur la seconde connexion de test, le temps réel passé
- Commit portant la ligne de traçabilité

---

# 9 · Hors périmètre

- Journalisation des notes, programmes et sujets : les objets n'existent pas. Cette
  story livre l'énumération et le mécanisme ; **chaque story concernée s'y rattachera**
- Durée de conservation et purge du journal : relève de la réglementation, non traitée
- Export du journal → US-SUI-04, priorité Could
- Interface de programmation → US-ADM-05, priorité Should

# 10 · Définition de fini

L'immuabilité est prouvée par un test s'exécutant sous le rôle applicatif et non sous
celui des migrations, la consultation est filtrée et paginée, une consultation produit
une entrée et une seule, aucun mot de passe ni condensat n'entre au journal, les deux
natures hors RG-26 sont consignées pour report au cahier des charges, et la suite
complète des trois stories précédentes passe sans modification.

Commence par l'étape 0.
