# Prompt Claude Code — 08 · US-REF-03 + US-REF-04 · Composer le référentiel d'une formation

> Sprint 1, lignes WBS 5.1.9 et 5.1.10. Must, **8 + 3 points**, 10,4 + 3,9 h estimées.
> Story la plus lourde de l'epic E2. **Binômage.**
> Prérequis : US-REF-02 est finie — le catalogue des matières existe.
> À coller dans une session neuve, après `/clear`.

---

Nous développons **US-REF-03 — Composer le référentiel d'une formation**, cas
d'utilisation **CU-P2-04**, fiche **détaillée**, et avec elle **US-REF-04 — Déclarer la
catégorie de lieu requise**, cas d'utilisation **CU-P2-05**.

Les deux ne se séparent pas : CU-P2-05 est **incluse** dans CU-P2-04, et la catégorie
de lieu se déclare au point 5 du scénario nominal, en même temps que le volume horaire.
Les traiter séparément imposerait de créer la table sans un champ obligatoire, puis de
le rajouter par migration.

Tu suis les huit étapes du workflow `/story`, avec arrêt obligatoire sur ma validation.

## Traçabilité

`BF-REF-03, BF-REF-04 → US-REF-03, US-REF-04 → CU-P2-04, CU-P2-05 → RG-05 à RG-08 → CLS-02`

---

# 1 · Le cœur du modèle métier

## 1.1 · Le point de conception qui commande tout

Le couple formation-matière porte un **volume horaire prescrit** et une **catégorie de
lieu requise**. Il constitue donc une **classe d'association** entre Formation et
Matière, et non une simple association plusieurs-à-plusieurs.

C'est cette classe que référenceront, plus tard, les séances programmées et le
rapprochement entre prescrit et réalisé. **Si elle est mal posée ici, les sprints 2 à 4
s'appuient sur du sable.** C'est la raison pour laquelle cette story vaut 8 points alors
qu'elle ne présente que deux écrans.

Nom retenu : `ElementReferentiel`, table `referentiel_element_referentiel`.

## 1.2 · Scénario nominal — CU-P2-04

1. La cellule pédagogique sélectionne une formation.
2. Le système présente le référentiel courant : matières rattachées, volume horaire
   prescrit de chacune, catégorie de lieu requise, et **le total des volumes**.
3. La cellule pédagogique recherche une matière dans le catalogue et la rattache.
4. Le système demande le volume horaire prescrit de cette matière **pour cette
   formation**.
5. La cellule pédagogique saisit le volume et déclare la catégorie de lieu requise —
   salle attitrée, lieu partagé ou aucun lieu — **ce qui exécute CU-P2-05**.
6. Le système enregistre, **recalcule le total et journalise** la modification.
7. Les points 3 à 6 sont répétés pour chaque matière du cursus.

## 1.3 · Enchaînements alternatifs

- **A1 — Matière absente du catalogue.** Au point 3, la matière est créée par CU-P2-03
  **sans quitter l'écran**, puis le déroulement reprend au point 4.
- **A2 — Modification d'un volume prescrit.** RG-08 s'applique avant enregistrement.
- **A3 — Retrait d'une matière.** RG-07 est vérifiée, puis le rattachement est retiré
  après **confirmation explicite** (BNF-09).
- **A4 — Duplication d'un référentiel existant.** *Confort de saisie, non exigé —*
  **hors périmètre**, ne l'implante pas.

## 1.4 · Exceptions

- **E1 — Matière déjà rattachée.** Refus du doublon, **et proposition de modifier le
  volume existant** (RG-06). Le message ne se contente pas de refuser : il offre la
  sortie.
- **E2 — Volume horaire non conforme.** Nul, négatif ou non numérique : refus **avec
  indication de l'intervalle attendu**.
- **E3 — Retrait impossible.** La matière est référencée par un prérequis, une
  évaluation ou une séance programmée : refus **avec énumération des éléments qui s'y
  opposent** (RG-07).

## 1.5 · Règles métier

| Code | Énoncé |
|---|---|
| **RG-05** | Le référentiel appartient à la formation. Aucune matière n'est jamais rattachée à une brigade ni à une session : **toutes les brigades d'une session suivent le référentiel de la formation de cette session** |
| **RG-06** | Une matière ne peut être rattachée qu'**une seule fois** au référentiel d'une formation donnée |
| **RG-07** | Une matière ne peut être **retirée** si elle est référencée par un prérequis, une séance programmée ou une évaluation |
| **RG-08** | Le volume horaire prescrit est **propre au couple** formation-matière. La même matière peut porter des volumes différents dans deux formations. Il est **strictement positif** |

## 1.6 · Critères d'acceptation — US-REF-03

1. Le référentiel rattache une ou plusieurs matières du catalogue à une formation.
2. Chaque rattachement porte un volume horaire prescrit propre à cette formation.
3. Une même matière rattachée à deux formations peut porter des volumes différents.
4. Le volume est renseigné **en heures** et doit être strictement positif.
5. La somme des volumes est **affichée et comparée à la durée de la formation** ; un
   écart déclenche un **avertissement non bloquant**.
6. Une matière déjà programmée dans une session en cours ne peut être retirée.

## 1.7 · Critères d'acceptation — US-REF-04

1. Trois catégories : **salle attitrée de la brigade, lieu partagé, aucun lieu requis**.
2. Une matière en lieu partagé précise le type attendu : **amphithéâtre, laboratoire ou
   salle spécialisée**.
3. Les matières sans lieu requis — ordre serré, sport — **ne consomment aucune
   ressource de salle** lors de la génération.
4. La catégorie est **exploitée comme contrainte par le moteur de génération**.

Les critères 3 et 4 d'US-REF-04 décrivent le comportement du moteur, qui appartient au
**sprint 3**. Cette story pose la donnée qu'il consommera ; elle ne peut pas les
vérifier. Consigne-les comme reportés vers US-PLAN-01.

---

# 2 · Le trou que je te demande de signaler, pas de combler seul

**Le critère 5 d'US-REF-03 n'est pas implémentable en l'état.**

Il demande de comparer la somme des volumes — **en heures** — à la durée de la formation
— **en semaines**, arbitrage retenu à US-REF-01. Rien, dans aucun livrable, ne dit
combien d'heures d'instruction compte une semaine au CIT.

La grille horaire, qui porterait cette réponse, appartient au paquetage P4 et arrive au
**sprint 2**.

**Ce que tu fais :** un paramètre nommé dans `config/settings/base.py`, au titre de
BNF-13 — volume horaire hebdomadaire de référence —, avec une valeur provisoire
explicitement commentée comme *à confirmer auprès du chef de bureau pédagogique*. Le
service le lit, ne le code jamais en dur.

**Ce que tu consignes dans `docs/suivi/` :** la question pour le terrain, et le fait que
la grille horaire du sprint 2 devra remplacer ce paramètre. Un paramètre provisoire qui
n'est pas signalé devient définitif.

L'avertissement est **non bloquant** : il informe, il n'empêche jamais d'enregistrer.
Emploie l'encadré d'avertissement (§ 3.30), jamais un refus.

---

# 3 · Quatre décisions déjà tranchées

## 3.1 · La classe d'association et ses contraintes

| Attribut | Type | Contrainte |
|---|---|---|
| `formation` | clé étrangère | Non nul, `CASCADE` — un référentiel n'existe pas sans sa formation |
| `matiere` | clé étrangère | Non nul, **`PROTECT`** — c'est le critère 5 d'US-REF-02 |
| `volume_horaire_prescrit` | entier, en heures | **Strictement positif** |
| `categorie_lieu` | énumération à trois valeurs | Non nul |
| `type_lieu_partage` | énumération à trois valeurs, nullable | Renseigné **si et seulement si** la catégorie est *lieu partagé* |

Contraintes portées **en base**, nommées :

- `uq_element_referentiel_formation_matiere` — RG-06
- `ck_element_referentiel_volume_positif` — RG-08
- `ck_element_referentiel_type_lieu_coherent` — la cohérence entre catégorie et type

La dernière est une contrainte de vérification exprimant l'équivalence : le type est
renseigné exactement quand la catégorie vaut *lieu partagé*. Ni un `clean()`, ni un
contrôle de formulaire : SQL sait le dire, donc SQL le dit.

Les deux `on_delete` diffèrent volontairement. Supprimer une formation emporte son
référentiel, qui n'a pas de sens sans elle. Supprimer une matière est **interdit** dès
qu'un référentiel l'emploie : c'est un objet du catalogue partagé.

## 3.2 · Le référentiel référence la matière, il ne la recopie jamais

Contrainte posée à US-REF-02, rappelée ici parce que c'est le moment où elle se viole :
**aucun champ d'`ElementReferentiel` ne duplique l'intitulé, le code ou quoi que ce soit
de la matière.** Le critère 6 d'US-REF-02 en dépend entièrement.

Un test de non-présence le vérifie.

## 3.3 · RG-07 s'énumère, et deux de ses trois sources n'existent pas

Prérequis : US-REF-06, **ce sprint**. Séances programmées : sprint 3. Évaluations :
sprint 4.

Reprends la méthode d'énumération des éléments bloquants écrite à US-REF-01 et
US-REF-02. Elle ne trouve rien aujourd'hui ; chaque story concernée y ajoutera une
ligne. Le critère 6 d'US-REF-03 — *matière déjà programmée dans une session en cours* —
est reporté vers **US-PLAN**.

C'est le septième report du paquetage. Ils devront tous être repris avant la clôture.

## 3.4 · A1 se fait dans un dialogue, sans quitter l'écran

*Sans quitter l'écran* est une exigence de la fiche, pas un confort : la cellule
pédagogique compose un cursus de trente matières, et sortir de l'écran à chaque manque
lui ferait perdre son travail en cours.

Boîte de dialogue native (§ 3.32), **appelant le service de création de matière
d'US-REF-02** — tu ne réécris pas la création, tu la réutilises. Au retour, la matière
est présélectionnée et le déroulement reprend au point 4.

Aucun script : `<dialog>` avec l'attribut `open`, ouvert par le serveur, comme la charte
le prescrit.

---

# 4 · Étape 0 — Explorer

Lis `app/referentiel/` en entier, `app/noyau/services/gestion.py`, et les méthodes
d'énumération des bloquants déjà écrites.

Relis la fiche CU-P2-04 dans `docs/conception/` — c'est une fiche détaillée, et je veux
que tu l'aies lue et non résumée depuis ce prompt.

**Rends-moi ta lecture du point de conception sur la classe d'association**, en tes
termes. Si elle est fausse, tout le reste le sera.

# 5 · Étape 1 — Planifier. Attends ma validation.

Plan complet, la structure exacte des deux énumérations, et le nom du paramètre du § 2.
**N'écris rien avant mon accord.**

---

# 6 · Les écrans

## 6.1 · Composition du référentiel — l'écran principal

Accessible depuis la fiche de formation, dont l'emplacement a été réservé à US-REF-01.

**Tableau éditable en ligne** (§ 3.16) : une ligne par matière rattachée, le volume
modifiable sur place avec son unité accolée, la catégorie de lieu en liste déroulante,
le type de lieu partagé apparaissant seulement quand il a un sens, et le bouton de
retrait (§ 3.40).

Modifier un volume sur place, c'est A2. Retirer une ligne, c'est A3, avec confirmation
(§ 3.32) et BNF-09.

**Rattachement d'une matière** — barre de recherche sur le catalogue, n'offrant que les
matières non archivées et **pas encore rattachées** : c'est E1 évité par construction,
mais E1 doit exister quand même, pour la voie directe.

**Total et écart** — bloc de statistique (§ 3.35) portant la somme des volumes, et
encadré d'avertissement (§ 3.30) quand l'écart avec la durée dépasse le seuil. Le seuil
est un paramètre, pas un littéral.

## 6.2 · Détail des trois catégories

| Catégorie | Sens | Conséquence, sprint 3 |
|---|---|---|
| **Salle attitrée** | La brigade a sa salle pour la session | Aucune ressource à arbitrer |
| **Lieu partagé** | Amphithéâtre, laboratoire ou salle spécialisée | Arbitrage séance par séance |
| **Aucun lieu** | Place d'armes, sport, plein air | Ne consomme **aucune** ressource de salle |

Les libellés affichés emploient la terminologie du centre (BNF-08). Écris-les tels
qu'ils figurent ci-dessus.

`npm run css:build` avant les tests d'interface.

---

# 7 · Tests

## Le modèle et ses contraintes

| Test | Vérifie |
|---|---|
| Une matière rattachée deux fois à la même formation → refus **en base** | RG-06 |
| La même matière dans deux formations, volumes différents → accepté | RG-08, critère 3 |
| Volume nul ou négatif → refus **en base** | RG-08, critère 4 |
| Catégorie *lieu partagé* sans type → refus **en base** | § 3.1 |
| Catégorie *aucun lieu* avec un type renseigné → refus **en base** | § 3.1 |
| Suppression d'une matière rattachée → refus | US-REF-02 critère 5 |
| Suppression d'une formation → son référentiel disparaît | § 3.1 |
| `ElementReferentiel` ne duplique aucun attribut de `Matiere` | § 3.2 |

Les cinq premiers écrivent **directement en base**, en contournant l'ORM. Un test qui
passe par `full_clean` ne prouve rien sur une contrainte.

## Le déroulement

| Test | Vérifie |
|---|---|
| Rattachement, volume, catégorie enregistrés et total recalculé | Nominal, points 5 et 6 |
| Chaque rattachement est journalisé | Point 6 |
| Doublon → refus **proposant la modification du volume existant** | E1 |
| Volume non conforme → refus **indiquant l'intervalle attendu** | E2 |
| Retrait → confirmation demandée avant exécution | A3, BNF-09 |
| Retrait d'une matière bloquée → énumération des opposants | E3, RG-07 |
| Création d'une matière depuis le dialogue, puis reprise au point 4 | A1 |
| Le dialogue appelle le service d'US-REF-02, sans le réécrire | § 3.4 |

## Le total et l'écart

| Test | Vérifie |
|---|---|
| Le total est la somme des volumes | Critère 5 |
| Écart au-delà du seuil → avertissement affiché | Critère 5 |
| L'avertissement **n'empêche pas** l'enregistrement | Critère 5 |
| Le paramètre de conversion est lu, non codé en dur | BNF-13, § 2 |

## Habilitation et non-régression

Cellule pédagogique écrit ; planification, examens et Direction lisent seulement.
La suite complète des sept stories précédentes passe sans modification.

---

# 8 · Vérification et livraison

- Les quinze tests d'architecture passent
- `ruff check` et `ruff format --check` propres
- Migration unique et réversible, `makemigrations --check --dry-run` muet
- `npm run css:build` rejoué
- Relecture par le sous-agent `relecteur-conception`
- `docs/suivi/` : le paramètre provisoire du § 2 et sa question pour le terrain, les
  reports vers US-PLAN-01 et US-REF-06, le temps réel passé, **séparé entre US-REF-03 et
  US-REF-04** — les deux lignes du classeur doivent pouvoir être renseignées
- Commit portant la ligne de traçabilité des deux stories

---

# 9 · Hors périmètre

- **A4, duplication d'un référentiel** : marquée *non exigée par le cahier des charges*
- Les prérequis entre matières → **US-REF-06**
- Les objectifs pédagogiques → **US-REF-05**
- Le comportement du moteur de génération face aux catégories de lieu → **sprint 3**
- Les lieux réels — salles, amphithéâtres — → **US-LIE-01**, ce sprint. Ici, on déclare
  une **catégorie requise**, jamais un lieu

# 10 · Définition de fini

La classe d'association porte volume et catégorie, les quatre règles RG-05 à RG-08 sont
implantées et les contraintes exprimables en SQL le sont, les trois exceptions et les
trois enchaînements alternatifs retenus sont exercés, le total et l'avertissement non
bloquant fonctionnent sur un paramètre lu et non codé, aucun attribut de matière n'est
dupliqué, le trou du § 2 est signalé sans être comblé en silence, et le temps est
relevé séparément pour les deux stories.

Commence par l'étape 0.
