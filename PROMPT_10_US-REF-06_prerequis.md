# Prompt Claude Code — 10 · US-REF-06 · Déclarer les prérequis du référentiel

> Version 2. Sprint 1, ligne WBS 5.1.12. Must, 5 points, 6,5 h estimées.
> Prérequis : US-REF-05 est finie.
> À coller dans une session neuve, après `/clear`.

---

Nous développons **US-REF-06 — Déclarer les prérequis du référentiel**, cas
d'utilisation **CU-P2-07**, fiche **détaillée**.

**Cette story n'est pas une story de gestion.** Le patron `ServiceGestion` ne t'aidera
presque pas : il n'y a ni liste paginée, ni archivage, ni formulaire de saisie
classique. Il y a un graphe, une propriété à maintenir, et un algorithme.

C'est aussi la story que le dossier de conception cite pour justifier la règle
d'architecture imposant une couche services. Traite-la en conséquence : elle sera lue.

Tu suis les huit étapes du workflow `/story`, avec arrêt obligatoire sur ma validation.

## Traçabilité

`BF-REF-06 → US-REF-06 → CU-P2-07 → RG-09, RG-10 → SEQ-01 → CLS-02`

---

# 1 · Le besoin

*En tant que membre de la cellule pédagogique, je veux déclarer les prérequis entre
matières d'un référentiel, afin de garantir la progressivité de la formation.*

## Critères d'acceptation — backlog v7

1. Une matière du référentiel peut déclarer **une ou plusieurs matières prérequises au
   sein du même référentiel**.
2. Le système **détecte et refuse les dépendances circulaires**.
3. Les prérequis sont **exploitables comme contrainte dure lors de la génération du
   programme**.
4. Une **violation de prérequis lors d'une saisie manuelle est signalée
   explicitement**.

**Les critères 3 et 4 ne sont pas vérifiables dans cette story.** Ils décrivent le
comportement du moteur de génération et de la saisie manuelle du programme, tous deux
au **sprint 3**. Consigne-les dans `docs/suivi/` comme reportés vers **US-PLAN-04**
— contrôle des contraintes dures, RG-36 — et **US-PLAN-05**.

Ils ne sont pas sans effet ici pour autant : voir § 3.2 bis.

## La fiche

| | |
|---|---|
| **Acteur principal** | Cellule pédagogique |
| **Déclencheur** | Le référentiel d'une formation est composé et la progressivité doit être garantie |
| **Préconditions** | **Au moins deux matières** sont rattachées au référentiel de la formation |
| **Postcondition** | Le référentiel porte un graphe de prérequis **acyclique**, exploitable par la génération du programme |

**Scénario nominal**

1. La cellule pédagogique sélectionne le référentiel d'une formation.
2. Le système présente les matières du référentiel et les prérequis déjà déclarés.
3. La cellule pédagogique désigne une matière et lui déclare une ou plusieurs matières
   prérequises, **choisies parmi celles du même référentiel**.
4. Le système vérifie l'appartenance au même référentiel (RG-09) et l'absence de cycle
   (RG-10).
5. Le système enregistre le prérequis et présente le graphe mis à jour.

**Enchaînements alternatifs**

- **A1 — Suppression d'un prérequis.** Après confirmation, le lien est retiré. **Aucune
  vérification supplémentaire n'est requise : une suppression ne peut pas créer de
  cycle.**
- **A2 — Consultation de l'ordre de progression.** Le système présente **un ordre
  topologique admissible** des matières, qui servira de point de départ à la génération
  du programme.

**Exceptions**

- **E1 — Cycle détecté.** Refus, **et affichage de la chaîne de matières formant le
  cycle**. Signaler seulement l'erreur sans montrer le chemin rendrait la correction
  impraticable sur un référentiel de trente matières.
- **E2 — Matière hors référentiel.** Refus au titre de RG-09.
- **E3 — Auto-prérequis.** Une matière déclarée comme son propre prérequis : refus, cas
  particulier de RG-10.

**Règles métier**

| Code | Énoncé |
|---|---|
| **RG-09** | Un prérequis ne peut lier que deux matières appartenant au référentiel de la **même** formation |
| **RG-10** | Le graphe des prérequis d'un référentiel est **acyclique**. La propriété est vérifiée **à chaque ajout**, et non seulement à la génération du programme |

**Point de conception, cité tel quel.** *L'acyclicité ne peut être portée par une
contrainte de base de données ; elle relève de la couche services, ce qui illustre
l'utilité de la règle d'architecture imposant une couche services même pour des
opérations en apparence simples. Le contrôle est un parcours en profondeur sur un
graphe de quelques dizaines de sommets : le coût est négligeable et il n'est pas
nécessaire de le différer.*

**Exigences applicables** : BNF-10 — message indiquant l'action corrective —, BNF-12 —
logique en couche services.

---

# 2 · Ce qui va en base, ce qui va en services — et pourquoi la frontière tombe là

Le principe du projet est de porter chaque contrainte au niveau le plus bas où elle est
exprimable. Ici, la frontière passe au milieu de RG-10, et il faut savoir le dire.

| Contrainte | Niveau | Motif |
|---|---|---|
| Unicité du couple (matière, matière prérequise) | **Base** | Contrainte d'unicité ordinaire |
| Auto-prérequis interdit — E3 | **Base** | `CHECK (element_id <> element_prerequis_id)` : SQL sait comparer deux colonnes d'une même ligne |
| Appartenance au même référentiel — RG-09 | **Services** | Voir § 2.1 |
| Acyclicité — RG-10 | **Services** | Une propriété globale d'un graphe ne s'exprime pas ligne à ligne |

## 2.1 · RG-09 : un écart assumé au principe, à consigner

RG-09 *serait* exprimable en base : en dénormalisant la formation sur la table des
prérequis, puis en posant deux clés étrangères composées vers `(id, formation)` de
`ElementReferentiel`. C'est un procédé classique et parfaitement solide en PostgreSQL.

Mais **Django ne sait pas déclarer une clé étrangère composée** : il faudrait une
migration en SQL brut, avec un modèle dont l'ORM ignorerait la contrainte. Le coût en
lisibilité et en maintenance dépasse le gain.

**Décision : RG-09 vit en couche services.** Consigne-le dans `docs/suivi/` comme écart
assumé au principe, avec cette justification. C'est le genre de point qu'un jury
soulève, et il vaut mieux l'avoir écrit avant qu'on le demande.

---

# 3 · Trois décisions déjà tranchées

## 3.1 · La détection de cycle se fait avant l'écriture, par parcours en profondeur

Ajouter *A a pour prérequis B* crée un cycle si, et seulement si, **A est déjà
atteignable depuis B** dans le graphe existant. Le contrôle est donc un parcours en
profondeur depuis B, cherchant A.

Pas de calcul incrémental, pas de cache, pas de fermeture transitive stockée. Quelques
dizaines de sommets : la fiche le dit, le coût est négligeable.

**Le parcours retourne la chaîne**, pas un booléen. E1 exige d'afficher les matières
formant le cycle, dans l'ordre. Une fonction qui répond *vrai* ou *faux* ne permet pas
de tenir cette exigence, et il faudrait la réécrire.

## 3.2 · L'ordre topologique doit être déterministe

A2 demande *un* ordre admissible. Il en existe généralement plusieurs, et l'algorithme
de Kahn en choisit un selon l'ordre dans lequel il dépile les sommets sans prédécesseur.

**Impose une règle de départage explicite** — par exemple l'intitulé de la matière —
afin que deux exécutions sur les mêmes données rendent le même ordre. Sans cela, les
tests deviennent instables, et surtout la génération du sprint 3 produirait des
programmes différents à données identiques, ce qui serait incompréhensible pour la
cellule planification.

## 3.2 bis · Les deux fonctions de graphe seront appelées depuis un autre paquetage

C'est la conséquence directe des critères 3 et 4 reportés. Le moteur de génération du
sprint 3 devra, pour honorer RG-36, savoir répondre à deux questions : *dans quel ordre
les matières peuvent-elles être programmées* et *cette matière a-t-elle un prérequis non
encore achevé*. Ce sont exactement les deux fonctions que tu écris ici.

Écris-les donc comme des **fonctions de service pures, appelables depuis
`planification`** :

- elles prennent un référentiel ou un couple de matières en paramètre
- elles rendent une liste ou une chaîne
- elles n'écrivent rien, ne lèvent pas d'exception pour un cas normal, ne dépendent
  d'aucune requête HTTP ni d'aucun état d'écran

Concrètement : **elles ne sont pas des méthodes privées du service des prérequis**, et
encore moins des fonctions internes à une vue. Si le moteur du sprint 3 doit les
recopier ou les réécrire, la story aura été manquée sans que rien ne le signale — et
c'est le genre de duplication qui produit deux comportements divergents six mois plus
tard.

Le sens des couches est respecté : `planification` dépend de `referentiel`, jamais
l'inverse. Tu n'anticipes rien du moteur, tu rends seulement consommable ce que tu
écris.

Un test le vérifie : les deux fonctions sont importées **depuis l'extérieur du module
des prérequis** et appelées sans aucun contexte d'écran.

## 3.3 · Aucun dessin de graphe

La charte interdit tout script. Dessiner un graphe côté serveur, en SVG positionné,
serait un travail de plusieurs heures sans rapport avec la valeur métier.

Le graphe se présente en **deux tableaux** : les matières avec leurs prérequis directs,
et l'ordre topologique en liste numérotée. C'est ce dont la cellule pédagogique a
besoin pour vérifier une progression, et c'est ce que le programme consommera.

Si tu juges qu'une représentation par niveaux apporterait beaucoup, **propose-la dans
ton plan sans l'implanter**. Je tranche.

---

# 4 · Étape 0 — Explorer

Lis `app/referentiel/` en entier, en particulier `ElementReferentiel`, l'écran de
composition d'US-REF-03, et la méthode d'énumération des éléments bloquants écrite
depuis US-REF-01.

Relis la fiche CU-P2-07 dans `docs/conception/`.

Rends-moi ta formulation de la condition de cycle — en une phrase, avant tout code. Si
elle est fausse, la story l'est.

# 5 · Étape 1 — Planifier. Attends ma validation.

Plan complet : la structure du modèle, la signature des deux fonctions de graphe, la
règle de départage du § 3.2. **N'écris rien avant mon accord.**

---

# 6 · Le modèle

`Prerequis`, héritant de `ModeleHorodate`. Pas d'archivage : A1 pose une suppression
franche, avec confirmation.

| Attribut | Type | Contrainte |
|---|---|---|
| `element` | clé étrangère `ElementReferentiel` | Non nul, `CASCADE` — la matière qui exige |
| `element_prerequis` | clé étrangère `ElementReferentiel` | Non nul, `CASCADE` — la matière exigée |

`Meta.db_table = "referentiel_prerequis"`.

Contraintes portées en base, nommées :

- `uq_prerequis_couple` — unicité du couple
- `ck_prerequis_non_reflexif` — les deux colonnes diffèrent, c'est E3

`CASCADE` des deux côtés : retirer une matière du référentiel emporte les liens qui la
concernent. C'est cohérent avec RG-07, qui **refuse** ce retrait tant que des liens
existent — la cascade n'est qu'un filet, le refus est la règle.

**Et c'est ici que RG-07 trouve sa première source réelle.** Depuis US-REF-01, la
méthode d'énumération des éléments bloquants ne trouvait rien. Ajoute-lui les
prérequis : une matière qui en exige d'autres, ou qui est exigée, ne peut être retirée
du référentiel. C'est le premier des reports consignés qui se referme — dis-le-moi
explicitement dans ton compte rendu.

---

# 7 · Les écrans

Accessible depuis l'écran de composition du référentiel d'US-REF-03.

**Contrôle de précondition** : au moins deux matières rattachées. Sinon, état vide
(§ 3.13) expliquant qu'il faut d'abord composer le référentiel, avec le lien pour y
aller. Pas un message d'erreur : une orientation.

**Tableau des prérequis** (§ 3.08) : une ligne par matière du référentiel, ses
prérequis directs en seconde colonne sous forme de jetons (§ 3.12) retirables, et une
action d'ajout par ligne.

**Ajout** : liste déroulante (§ 3.20) n'offrant que les matières du **même
référentiel**, moins la matière elle-même, moins celles déjà déclarées. C'est E2 et E3
évités par construction — **mais les deux exceptions doivent exister quand même**, pour
la voie directe.

**Ordre de progression** (A2) : liste numérotée, dans un onglet ou un bloc distinct
(§ 3.42). Un encadré (§ 3.30) rappelle qu'il s'agit d'**un** ordre admissible parmi
d'autres, et non d'une prescription.

**Cycle détecté** (E1) : encadré d'erreur affichant la chaîne, matière par matière,
dans l'ordre du cycle. Le message indique l'action corrective (BNF-10) : quel lien
retirer pour rompre la chaîne.

**Suppression** (A1) : confirmation par dialogue (§ 3.32), BNF-09.

`npm run css:build` avant les tests d'interface.

---

# 8 · Tests

## Le graphe — dans les tests de service, sans navigateur

| Test | Vérifie |
|---|---|
| Ajout simple entre deux matières du même référentiel | Nominal |
| Cycle direct A→B puis B→A → refus | RG-10 |
| Cycle indirect A→B→C puis C→A → refus | RG-10 |
| **Le refus rend la chaîne complète, dans l'ordre** | E1 |
| Auto-prérequis → refus **en base** | E3 |
| Matière d'un autre référentiel → refus | RG-09, E2 |
| Couple déjà déclaré → refus **en base** | § 6 |
| Suppression d'un lien : aucun contrôle déclenché | A1 |
| Ordre topologique : les prérequis précèdent toujours | A2 |
| **Le même graphe rend deux fois le même ordre** | § 3.2 |
| Graphe sans aucun lien → ordre par la règle de départage | § 3.2 |
| Graphe à trente sommets : le contrôle reste immédiat | Point de conception |
| **Les deux fonctions sont appelables depuis l'extérieur du module, sans contexte d'écran** | § 3.2 bis |

Le quatrième test est le plus important de la story. Un contrôle qui refuse sans
montrer le chemin satisfait RG-10 et échoue à E1 — et c'est E1 qui rend l'outil
utilisable.

Le dixième garde contre une régression silencieuse : si quelqu'un remplace un
parcours ordonné par un parcours sur un ensemble non ordonné, tout continue de
fonctionner sauf la reproductibilité, et personne ne le voit avant le sprint 3.

## L'intégration

| Test | Vérifie |
|---|---|
| Retrait d'une matière liée par un prérequis → refus, liens énumérés | RG-07 |
| Suppression d'un `ElementReferentiel` → ses liens disparaissent | `CASCADE` |
| Moins de deux matières → écran d'orientation, pas d'erreur | Précondition |
| La liste déroulante n'offre ni la matière elle-même, ni les autres référentiels | § 7 |
| Ajout et suppression journalisés | Extension de RG-26 |
| Cellule pédagogique écrit ; les trois autres lisent seulement | RG-02 |

## Non-régression

La suite complète des neuf stories précédentes passe sans modification.

---

# 9 · Vérification et livraison

- Les quinze tests d'architecture passent
- `ruff check` et `ruff format --check` propres. Attention à la limite de 40 lignes par
  fonction : le parcours et le tri topologique doivent tenir, ou être découpés
  proprement
- Migration unique et réversible, `makemigrations --check --dry-run` muet
- `npm run css:build` rejoué
- Relecture par le sous-agent `relecteur-conception`
- `docs/suivi/` : l'écart assumé du § 2.1, la règle de départage retenue, **la fermeture
  du premier report RG-07**, **le report des critères 3 et 4 vers US-PLAN-04 et
  US-PLAN-05**, la signature exacte des deux fonctions de graphe pour que le sprint 3
  les retrouve, le temps réel passé
- Commit portant la ligne de traçabilité

---

# 10 · Hors périmètre

- La consultation par les autres cellules → **US-REF-07**
- L'exploitation des prérequis comme contrainte dure par le moteur de génération →
  **US-PLAN-04**, sprint 3, RG-36. Critère 3, reporté
- Le signalement d'une violation de prérequis en saisie manuelle → **US-PLAN-05**,
  sprint 3. Critère 4, reporté
- Tout dessin de graphe → § 3.3
- Les prérequis entre formations ou entre sessions : n'existent pas au modèle

# 11 · Définition de fini

Les deux règles sont implantées au niveau juste — unicité et non-réflexivité en base,
appartenance et acyclicité en services —, la détection de cycle rend la chaîne et non
un booléen, l'ordre topologique est déterministe et prouvé reproductible, l'écart
assumé sur RG-09 est consigné avec sa justification, le report RG-07 est refermé, et la
suite complète des stories précédentes passe sans modification.

Commence par l'étape 0.
