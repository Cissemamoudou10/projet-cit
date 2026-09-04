# Prompt Claude Code — 12 · US-INS-01 · Gérer les instructeurs

> Sprint 1, ligne WBS 5.1.14. Must, 5 points, 6,5 h estimées.
> Prérequis : le paquetage P2 est clos. **Première story du paquetage P4 — Ressources.**
> À coller dans une session neuve, après `/clear`.

---

Nous développons **US-INS-01 — Gérer les instructeurs**, cas d'utilisation
**CU-P4-01**, fiche **générique plus écarts**.

C'est la première story de l'application `ressources`. Elle réutilise le patron
`ServiceGestion` écrit à US-REF-00 : si celui-ci est bien fait, cette story doit être
principalement du modèle et des écrans.

Tu suis les huit étapes du workflow `/story`, avec arrêt obligatoire sur ma validation.

## Traçabilité

`BF-INS-01 → US-INS-01 → CU-P4-01 → CLS-04`

---

# 1 · Le besoin

*En tant que membre de la cellule pédagogique, je veux gérer la fiche des instructeurs,
afin de disposer d'un annuaire fiable du corps enseignant.*

## Critères d'acceptation — backlog v7

1. La fiche comporte **identité, grade, spécialité et statut** : militaire du centre,
   vacataire ou civil.
2. Un instructeur peut être **archivé sans suppression**, afin de préserver l'historique
   des affectations.
3. La liste est **paginée et dotée d'une recherche par nom, prénom ou matricule**, avec
   **filtrage par statut et par spécialité**.
4. Un instructeur **affecté à un programme en cours ne peut être supprimé**.

---

# 2 · Un attribut que le critère 1 oublie et que le critère 3 exige

Le critère 1 énumère quatre éléments de fiche : identité, grade, spécialité, statut.
Le critère 3 demande une recherche **par matricule**.

**Le matricule n'est donc dans aucune énumération d'attributs, mais il est indispensable
au fonctionnement.** C'est une omission de rédaction, pas une ambiguïté : on ne cherche
pas sur un champ qui n'existe pas.

Ajoute-le. Et pose la question dans ton plan : **le matricule est-il unique, et
obligatoire ?** Ma position est qu'il l'est pour un militaire du centre, mais qu'un
vacataire ou un civil peut ne pas en avoir. Propose une règle qui tienne compte des
trois statuts, argumente en deux phrases, je tranche.

Consigne l'ajout dans `docs/suivi/` : le backlog devra mentionner le matricule au
critère 1.

---

# 3 · Trois décisions déjà tranchées

## 3.1 · Un instructeur n'est pas un utilisateur du système

C'est établi par les critères d'US-INS-03 : *l'instructeur ne dispose d'aucun accès au
système ; la saisie est effectuée par la cellule planification à partir d'une
transmission externe.*

Conséquence de modèle : **`Instructeur` ne porte aucune clé étrangère vers
`Utilisateur`**, et n'en héritera jamais. Ce sont deux notions étrangères l'une à
l'autre — l'une désigne quelqu'un qui enseigne, l'autre quelqu'un qui se connecte.

Un test de non-présence le vérifie. Sans lui, quelqu'un fera le rapprochement un jour,
« pour que les instructeurs puissent consulter leur emploi du temps », et fera basculer
le projet dans un périmètre explicitement exclu par la note de cadrage.

## 3.2 · Le statut est une énumération portée en base

Trois valeurs, et trois seulement : **militaire du centre, vacataire, civil**.
Contrainte de vérification nommée, comme pour le profil d'utilisateur à US-ADM-02.

Les libellés affichés emploient la terminologie du centre (BNF-08). Écris-les tels
qu'ils figurent au critère 1.

## 3.3 · Le critère 4 n'est pas testable, son mécanisme se pose quand même

Les séances et les programmes appartiennent au paquetage P5, sprint 3.

Reprends la méthode d'énumération des éléments bloquants, écrite depuis US-REF-01 et
enrichie à US-REF-06. Elle ne trouvera rien aujourd'hui. **US-INS-02 y ajoutera les
qualifications** — dans ce sprint — et **US-PLAN-03 les affectations**.

Consigne le report : *critère 4 d'US-INS-01, vérifié à US-PLAN-03*.

---

# 4 · Deux remontées sur la matrice d'habilitation

Elles ne bloquent pas cette story. Je te demande de les **poser dans ton compte rendu**,
pas de les résoudre.

## 4.1 · La cellule examens n'a aucun accès au domaine des instructeurs

La matrice § 11.2 donne, pour le domaine *Instructeurs et qualifications* : écriture à
la cellule pédagogique, lecture à la planification et à la Direction de Formation,
**rien à la cellule examens**.

Or CU-P6-04, *Organiser une épreuve*, dont l'acteur principal est la cellule examens,
exige de désigner des surveillants — et RG-53 précise que les surveillants sont des
instructeurs référencés.

**La cellule examens devra donc lire l'annuaire des instructeurs au sprint 4, et la
matrice le lui interdit.** Deux issues possibles : ajouter la lecture à la matrice, ou
considérer que la désignation d'un surveillant passe par un autre chemin. C'est un
arbitrage, pas une correction évidente.

Applique la matrice telle qu'elle est — elle fait foi — et signale le point.

## 4.2 · La spécialité apparaît maintenant sur deux entités

`Formation` porte une spécialité depuis US-REF-01, en texte libre, sur proposition
restée sans arbitrage. `Instructeur` en porte une aussi, et le critère 3 exige de
**filtrer** dessus.

Filtrer sur un texte libre est fragile : une faute de frappe crée une valeur fantôme
dans la liste de filtres, et personne ne la retrouve.

**Pour cette story, garde le texte libre**, et construis la liste de filtres à partir
des valeurs distinctes réellement enregistrées. Mais signale que la question posée à
US-REF-01 devient plus pressante : **s'agit-il de la même nomenclature pour les deux
entités ?** Si oui, elle mérite une table de référence.

---

# 5 · Étape 0 — Explorer

Lis `app/noyau/services/gestion.py` et les gabarits génériques, `app/ressources/` —
qui ne contient que sa structure —, et `app/referentiel/models.py` comme exemple
d'application du patron.

Dans `docs/charte/` : **3.08**, **3.10**, **3.11**, **3.12**, **3.13**, **3.17**,
**3.20**, **3.24**, **3.25**, **3.29** pour le motif du badge, **3.32**, **3.39**,
**3.40**.

Rends-moi ce que le patron te donne, et ce qu'il te manque pour une première story hors
du paquetage référentiel. **Si le patron ne s'applique pas proprement à une autre
application, c'est un défaut de conception et je veux le savoir maintenant** — quatre
stories du sprint 2 en dépendent.

# 6 · Étape 1 — Planifier. Attends ma validation.

Plan complet, plus ta proposition sur le matricule du § 2. **N'écris rien avant mon
accord.**

---

# 7 · Le modèle

`Instructeur`, héritant de `ModeleHorodate` et du mixin d'archivage.

| Attribut | Type | Contrainte |
|---|---|---|
| `nom` | `CharField` | Non vide |
| `prenom` | `CharField` | Non vide |
| `matricule` | `CharField` | Voir § 2 |
| `grade` | `CharField` | Non vide |
| `specialite` | `CharField` | Texte libre — § 4.2 |
| `statut` | énumération à trois valeurs | Non nul |
| `archive`, `archive_le` | Du mixin | |

`Meta.db_table = "ressources_instructeur"`.

Contraintes portées **en base**, nommées :

- `ck_instructeur_statut` — les trois valeurs admises
- la contrainte d'unicité du matricule, selon l'arbitrage du § 2

`ServiceInstructeur.DOMAINE = "instructeurs"` — le test d'architecture posé à US-ADM-03
l'exige, et c'est la première fois qu'il s'applique hors du référentiel. Vérifie que le
domaine figure bien au catalogue des dix-huit permissions.

---

# 8 · Les écrans

Bâtis sur les gabarits génériques.

**Liste** — tableau dense (§ 3.08), pagination (§ 3.10). Colonnes : matricule, grade,
nom et prénom, spécialité, statut, état.

Recherche sur **nom, prénom et matricule** — les trois, c'est le critère 3.

Filtres (§ 3.11) sur le **statut** et la **spécialité**, avec jetons (§ 3.12). Le filtre
de spécialité se construit à partir des valeurs distinctes enregistrées — § 4.2.

**Badge de statut** — la charte n'en propose pas pour cette notion. Compose-le sur le
motif du § 3.29, et **double la couleur d'un mot** conformément au § 1.2 : les trois
statuts doivent se distinguer à l'impression monochrome.

**Formulaire** — deux colonnes (§ 3.24) : *Identité* — nom, prénom, matricule, grade —
et *Rattachement* — spécialité, statut. Liste déroulante (§ 3.20) pour le statut.

**Fiche** — l'instructeur, et deux emplacements réservés, **vides pour l'instant** : ses
qualifications, que remplira US-INS-02 dans ce sprint, et ses indisponibilités, que
remplira US-INS-03 au sprint 2. Prévois-les, ne les remplis pas.

**Archivage** — dialogue de confirmation (§ 3.32), BNF-09. Le message énonce ce que
l'archivage préserve : l'historique des affectations, littéralement le critère 2.

Navigation : la rubrique *Ressources* apparaît, filtrée par `a_permission`.

`npm run css:build` avant les tests d'interface.

---

# 9 · Tests

| Test | Vérifie |
|---|---|
| Création avec les six attributs | Critère 1, § 2 |
| Statut hors des trois valeurs → refus **en base** | § 3.2 |
| Matricule : la règle retenue au § 2, imposée **en base** | § 2 |
| Recherche par nom, par prénom, **et par matricule** | Critère 3 |
| Filtre par statut ; filtre par spécialité | Critère 3 |
| Le filtre de spécialité n'offre que les valeurs enregistrées | § 4.2 |
| Liste paginée au-delà de vingt instructeurs | Critère 3, BNF-15 |
| Instructeur archivé : absent des listes de sélection, présent en consultation | Critère 2 |
| L'archivage ne supprime rien | Critère 2 |
| La méthode d'énumération des bloquants existe et ne trouve rien | Critère 4, § 3.3 |
| **`Instructeur` ne porte aucune clé étrangère vers `Utilisateur`** | § 3.1 |
| Cellule pédagogique écrit ; planification et Direction lisent | Matrice § 11.2 |
| **Cellule examens : aucun accès, ni lecture ni écriture** | Matrice § 11.2, et § 4.1 |
| Création, modification, archivage journalisés | Extension de RG-26 |
| Modification concurrente détectée | E5 |
| `DOMAINE` déclaré et présent au catalogue | Test d'architecture |

L'avant-dernier test de la liste est celui du § 4.1 : il **doit** passer aujourd'hui, et
il faudra le changer si l'arbitrage ouvre l'accès à la cellule examens. Écris-le en le
commentant, pour qu'on sache pourquoi il existe le jour où il devra tomber.

## Non-régression

La suite complète des onze stories précédentes passe sans modification.

---

# 10 · Vérification et livraison

- Les quinze tests d'architecture passent
- `ruff check` et `ruff format --check` propres
- Migration unique et réversible, `makemigrations --check --dry-run` muet
- `npm run css:build` rejoué
- Relecture par le sous-agent `relecteur-conception`
- `docs/suivi/` : l'arbitrage sur le matricule, les deux remontées du § 4, le report du
  critère 4, **ce que le patron a couvert hors du paquetage référentiel**, le temps réel
- Commit portant la ligne de traçabilité

---

# 11 · Hors périmètre

- La matrice de qualification → **US-INS-02**, ligne suivante du sprint
- Les indisponibilités → **US-INS-03**, sprint 2
- La consultation de la charge d'un instructeur → **US-INS-04**, Should, sprint 4
- Le blocage de suppression par une affectation → **US-PLAN-03**, sprint 3
- Tout accès de l'instructeur au système : **exclu du périmètre du projet** par la note
  de cadrage

# 12 · Définition de fini

Les quatre critères sont couverts par un test nommé ou consignés comme reportés, le
matricule est ajouté et sa règle tranchée, le statut est contraint en base, l'instructeur
est prouvé étranger au modèle d'utilisateur, la cellule examens est prouvée sans accès,
les deux remontées du § 4 sont consignées sans être résolues, et la suite complète des
stories précédentes passe sans modification.

Commence par l'étape 0.
