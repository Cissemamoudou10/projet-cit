# Prompt Claude Code — 13 · US-INS-02 · Établir la matrice de qualification

> Sprint 1, ligne WBS 5.1.15. Must, 5 points, 6,5 h estimées.
> Prérequis : US-INS-01 est finie ; le catalogue des matières existe depuis US-REF-02.
> À coller dans une session neuve, après `/clear`.

---

Nous développons **US-INS-02 — Établir la matrice de qualification**, cas d'utilisation
**CU-P4-02**, fiche **détaillée**.

C'est la donnée dont dépendra toute la planification : sans elle, aucune affectation
d'instructeur n'est vérifiable. RG-21 en fait une **contrainte dure**, contrôlée à la
génération, à la modification manuelle et au remplacement.

Tu suis les huit étapes du workflow `/story`, avec arrêt obligatoire sur ma validation.

## Traçabilité

`BF-INS-02 → US-INS-02 → CU-P4-02 → RG-21, RG-22 → SEQ-04 → CLS-04`

---

# 1 · Le besoin

*En tant que membre de la cellule pédagogique, je veux déclarer les matières du
catalogue que chaque instructeur est habilité à enseigner, afin que seules des
affectations valides soient possibles.*

## Critères d'acceptation — backlog v7

1. Une qualification associe un instructeur à une **matière du catalogue**,
   indépendamment des formations et des brigades.
2. Un instructeur peut être qualifié pour plusieurs matières, et une matière peut
   compter plusieurs instructeurs qualifiés.
3. La matrice est consultable **par instructeur et par matière**.
4. Une matière **sans aucun instructeur qualifié est signalée visuellement**.
5. La cellule planification **consulte la matrice sans pouvoir la modifier**.

## La fiche CU-P4-02

| | |
|---|---|
| **Déclencheur** | Arrivée d'un instructeur, ou révision périodique des habilitations |
| **Préconditions** | L'instructeur existe ; le catalogue des matières est alimenté |
| **Postcondition** | L'instructeur est associé aux matières qu'il est habilité à enseigner ; la génération du programme et la suggestion de remplaçant peuvent s'appuyer sur cette association |

**Scénario nominal**

1. La cellule pédagogique sélectionne un instructeur.
2. Le système présente les matières du catalogue et celles pour lesquelles l'instructeur
   est déjà qualifié.
3. La cellule pédagogique ajoute ou retire des qualifications.
4. Le système enregistre **et journalise chaque modification**.

**Enchaînements alternatifs**

- **A1 — Saisie par matière.** La cellule pédagogique part d'une matière et désigne les
  instructeurs qualifiés. **La matrice est symétrique et les deux entrées mènent à la
  même donnée.**
- **A2 — Consultation de la couverture.** Le système présente, pour un référentiel
  donné, les matières et le nombre d'instructeurs qualifiés pour chacune.

**Exceptions**

- **E1 — Retrait d'une qualification utilisée.** L'instructeur est affecté à des séances
  futures de cette matière : le système **refuse le retrait** et énumère les séances
  concernées, laissant le choix entre les réaffecter d'abord ou renoncer (RG-22).
- **E2 — Matière sans instructeur qualifié.** Le retrait laisserait une matière du
  référentiel d'une session en cours sans aucun instructeur qualifié : **avertissement
  explicite, sans blocage. C'est une décision de commandement, pas une erreur de
  saisie.**

**Règles métier**

| Code | Énoncé |
|---|---|
| **RG-21** | Un instructeur ne peut être affecté à une séance que s'il est qualifié pour la matière de cette séance. Règle **dure**, contrôlée à la génération, à la modification manuelle et au remplacement |
| **RG-22** | Une qualification ne peut être retirée tant que l'instructeur est affecté à des séances futures de la matière concernée |

---

# 2 · Le point de conception, cité tel quel

*La qualification associe un instructeur et une matière du **catalogue**, jamais un
instructeur et une matière d'un référentiel : un instructeur habilité pour une matière
l'est indépendamment de la formation dans laquelle elle est enseignée. Cette précision
évite une erreur de cardinalité qui multiplierait inutilement les enregistrements. Si le
terrain devait ultérieurement introduire un niveau d'habilitation ou une date de
validité, la classe d'association est le point d'extension naturel — aucune anticipation
n'est faite à ce stade.*

Trois conséquences que je veux voir tenues.

**Aucune clé étrangère vers `ElementReferentiel`.** Un test de non-présence le vérifie.
Le lier au référentiel multiplierait les enregistrements par le nombre de formations
employant la matière, et il faudrait ressaisir la qualification à chaque nouvelle
formation.

**Aucun niveau d'habilitation, aucune date de validité, aucun commentaire.** Le point de
conception dit explicitement qu'aucune anticipation n'est faite. Deux colonnes, c'est
tout. Si tu les juges utiles, propose-les dans ton plan — mais ne les écris pas.

**La matrice est symétrique.** A1 n'est pas un second écran sur une seconde donnée : les
deux entrées manipulent la **même** table, dans les deux sens. Un test doit le prouver :
une qualification créée par l'entrée *instructeur* apparaît par l'entrée *matière*.

---

# 3 · Quatre décisions déjà tranchées

## 3.1 · Le retrait est une suppression réelle

Deuxième exception à la règle d'archivage, après les objectifs pédagogiques.

Une qualification retirée disparaît : rien ne la référence. Les séances déjà programmées
portent un instructeur et une matière, pas une qualification — l'historique ne passe pas
par elle. RG-22 protège l'intégrité en amont, en refusant le retrait tant qu'il
casserait une affectation.

Pas de mixin d'archivage. Suppression franche, avec confirmation (BNF-09). Consigne
l'exception et sa justification.

## 3.2 · E1 n'est pas testable, son mécanisme se pose quand même

Les séances arrivent au sprint 3. RG-22 ne peut donc rien refuser aujourd'hui.

Écris la vérification comme une méthode dédiée du service — *cette qualification est-elle
employée par des séances futures* — qui rend une liste vide aujourd'hui et que
**US-PLAN-03 remplira**. Le message d'E1 et son écran d'énumération sont écrits
maintenant ; seule la source de données manque.

Consigne le report : *E1 d'US-INS-02, vérifié à US-PLAN-03*.

## 3.3 · Un report se referme ici

US-REF-02, écart 2 : *la suppression d'une matière est refusée si elle figure dans un
référentiel ou dans une matrice de qualification.* La seconde source n'existait pas.

**Ajoute les qualifications à la méthode d'énumération des éléments bloquants de
`ServiceMatiere`.** Une matière pour laquelle un instructeur est qualifié ne peut plus
être supprimée du catalogue.

C'est le deuxième report refermé depuis le début du sprint. Dis-le-moi explicitement.

## 3.4 · E2 avertit, ne bloque jamais

*C'est une décision de commandement, pas une erreur de saisie.* La formule est du
dossier de conception ; elle décide du comportement.

Le retrait qui laisserait une matière sans instructeur qualifié **aboutit**. Un encadré
d'avertissement (§ 3.30) signale la conséquence, l'agent confirme, l'opération se fait.

Ne transforme pas cet avertissement en refus. Un système qui empêche le commandement de
prendre une décision qu'il assume est un système qu'on contourne.

---

# 4 · Étape 0 — Explorer

Lis `app/ressources/` — `Instructeur` et son service —, `app/referentiel/models.py` —
`Matiere` et sa méthode d'énumération des bloquants —, et `app/noyau/services/gestion.py`.

Dans `docs/charte/` : **3.08**, **3.11**, **3.12**, **3.13**, **3.23** pour les cases à
cocher, **3.29** pour le motif du badge, **3.30**, **3.32**, **3.35**, **3.39**.

Rends-moi ta lecture du § 2 en tes termes. Si tu décris une association vers le
référentiel plutôt que vers le catalogue, tout le reste sera faux.

# 5 · Étape 1 — Planifier. Attends ma validation.

Plan complet, et la structure retenue pour les deux entrées symétriques. **N'écris rien
avant mon accord.**

---

# 6 · Le modèle

`Qualification`, héritant de `ModeleHorodate`. **Pas du mixin d'archivage** — § 3.1.

| Attribut | Type | Contrainte |
|---|---|---|
| `instructeur` | clé étrangère `Instructeur` | Non nul, `CASCADE` |
| `matiere` | clé étrangère `Matiere` | Non nul, **`PROTECT`** |

`Meta.db_table = "ressources_qualification"`.

Contrainte `uq_qualification_instructeur_matiere`, portée en base : on ne déclare pas
deux fois la même habilitation.

Les deux `on_delete` diffèrent volontairement. Un instructeur supprimé — cas rare,
puisque l'archivage prévaut — emporte ses qualifications, qui n'ont pas de sens sans
lui. Une matière est **protégée** : c'est le § 3.3, et c'est ce qui referme le report
d'US-REF-02.

---

# 7 · Les écrans

## 7.1 · Ne construis pas une grille croisée

La tentation est d'afficher un tableau à double entrée, instructeurs en lignes et
matières en colonnes. **Ne le fais pas.** Avec cinquante instructeurs et cent matières,
la grille est illisible, inutilisable au clavier, et ingérable à l'impression.

Le critère 3 demande une consultation *par instructeur et par matière* : ce sont **deux
écrans à entrée simple**, pas une grille.

## 7.2 · Entrée par instructeur — le scénario nominal

Depuis la fiche d'instructeur, dont l'emplacement a été réservé à US-INS-01.

La liste des matières du catalogue, chacune avec une case à cocher (§ 3.23) marquant la
qualification. Recherche et filtre sur le catalogue (§ 3.11) : cent matières ne se
parcourent pas à l'œil.

Cocher crée, décocher retire — avec la confirmation d'E1 et l'avertissement d'E2 le cas
échéant.

## 7.3 · Entrée par matière — A1

Depuis la fiche de la matière, dont l'emplacement a été réservé à US-REF-02.

Symétrique : la liste des instructeurs non archivés, avec la même case à cocher. **La
même donnée, l'autre sens.**

## 7.4 · Couverture — A2

Pour un référentiel donné : ses matières, et le nombre d'instructeurs qualifiés pour
chacune. Tableau dense (§ 3.08), avec un bloc de statistique (§ 3.35) portant le nombre
de matières non couvertes.

**Critère 4 — signalement visuel.** Une matière à zéro instructeur qualifié est marquée.
Emploie le motif du § 3.29 et **double la couleur d'un mot** conformément au § 1.2 : ce
tableau sera imprimé en monochrome, et une couleur seule ne dirait rien.

**Attention aux requêtes.** Compter les instructeurs qualifiés matière par matière dans
une boucle produit une requête par ligne. Emploie une agrégation en une seule requête.
Sur cent matières, la différence est visible ; sur le poste du CIT, elle sera pénible.

Le signalement du critère 4 apparaît aussi sur l'écran de composition du référentiel
d'US-REF-03 : une matière sans instructeur qualifié doit s'y voir. Ajoute-le.

`npm run css:build` avant les tests d'interface.

---

# 8 · Tests

## Le modèle et la symétrie

| Test | Vérifie |
|---|---|
| Une qualification lie un instructeur à une **matière du catalogue** | Critère 1 |
| `Qualification` ne porte aucune clé vers `ElementReferentiel` | § 2 |
| Elle ne porte **ni niveau, ni date de validité, ni commentaire** | § 2 |
| Un instructeur qualifié pour plusieurs matières | Critère 2 |
| Une matière comptant plusieurs instructeurs | Critère 2 |
| Doublon → refus **en base** | § 6 |
| **Créée par l'entrée instructeur, visible par l'entrée matière** | A1, § 2 |
| **Créée par l'entrée matière, visible par l'entrée instructeur** | A1, § 2 |
| Suppression d'une matière qualifiée → refus | § 3.3, US-REF-02 écart 2 |
| Suppression d'un instructeur → ses qualifications disparaissent | `CASCADE` |

## Le déroulement

| Test | Vérifie |
|---|---|
| Ajout et retrait journalisés | Nominal, point 4 |
| Retrait laissant une matière sans instructeur → **aboutit**, avec avertissement | E2, § 3.4 |
| La méthode de vérification d'E1 existe et rend une liste vide | § 3.2 |
| Couverture : le compte par matière est exact | A2 |
| Le compte s'obtient **sans requête par ligne** | § 7.4 |
| Matière à zéro instructeur signalée, **et par un mot, pas seulement par une couleur** | Critère 4, charte § 1.2 |
| Le signalement apparaît aussi sur l'écran de composition du référentiel | § 7.4 |

## Habilitation

| Test | Vérifie |
|---|---|
| Cellule pédagogique écrit | Matrice § 11.2 |
| **Cellule planification lit, ne modifie pas** | Critère 5 |
| Direction de Formation lit | Matrice § 11.2 |
| Cellule examens : aucun accès | Matrice § 11.2, remontée d'US-INS-01 |

## Non-régression

La suite complète des douze stories précédentes passe sans modification.

---

# 9 · Vérification et livraison

- Les quinze tests d'architecture passent
- `ruff check` et `ruff format --check` propres
- Migration unique et réversible, `makemigrations --check --dry-run` muet
- `npm run css:build` rejoué
- Relecture par le sous-agent `relecteur-conception`
- `docs/suivi/` : l'exception à la règle d'archivage, **la fermeture du report
  d'US-REF-02**, le report d'E1 vers US-PLAN-03, le temps réel passé
- Commit portant la ligne de traçabilité

---

# 10 · Hors périmètre

- Les indisponibilités → **US-INS-03**, sprint 2
- La charge d'un instructeur → **US-INS-04**, Should, sprint 4
- Le contrôle de RG-21 à l'affectation → **US-PLAN-04**, sprint 2. Cette story pose la
  donnée ; le contrôle est ailleurs
- Le classement des remplaçants → **US-PLAN-10**, Could
- Niveau d'habilitation, date de validité : explicitement écartés par le point de
  conception

# 11 · Définition de fini

Les cinq critères sont couverts par un test nommé ou consignés comme reportés, la
qualification est prouvée liée au catalogue et non au référentiel, la symétrie des deux
entrées est prouvée dans les deux sens, le retrait laissant une matière découverte
aboutit avec avertissement, la couverture se calcule sans requête par ligne, le report
d'US-REF-02 est refermé, et la suite complète des stories précédentes passe sans
modification.

Commence par l'étape 0.
