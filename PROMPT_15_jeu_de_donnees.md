# Prompt Claude Code — 15 · Jeu de données de démonstration

> Sprint 1, ligne WBS 5.1.17. 4 h estimées. **Tâche, pas story.**
> Prérequis : les quinze stories du sprint 1 sont livrées.
> À coller dans une session neuve, après `/clear`.

---

Tu construis le **jeu de données de démonstration du sprint 1**. Il sert à trois
choses, et sa conception découle de ces trois usages :

1. **La recette manuelle** conduite par le binôme, dès aujourd'hui.
2. **La revue de sprint du 12 septembre**, devant les cellules.
3. **Le prototype du solveur**, qui a besoin de données réalistes pour être calibré.

Ce n'est pas un jeu de test unitaire : les tests ont leurs propres jeux, montés et
défaits à chaque exécution. Celui-ci est une **base peuplée, cohérente et
démontrable**.

---

# 1 · Trois règles absolues

## 1.1 · Aucune donnée réelle du CIT

Ni nom d'instructeur, ni matricule, ni intitulé de formation qui existerait
réellement. Les noms sont plausibles et inventés. Cette règle vaut depuis le premier
jour du projet et ne souffre aucune exception : le dépôt est versionné et sera lu.

## 1.2 · Le chargement passe par les services, pas par l'ORM

N'emploie ni `bulk_create`, ni `loaddata` sur des fixtures JSON, ni `Model.objects.create`
en direct.

**Charge chaque objet en appelant le service qui le gouverne**, avec un utilisateur
agissant explicite. Trois raisons :

- les règles métier sont exercées : si le jeu se charge, elles sont cohérentes ;
- le journal se peuple naturellement, ce qui donne du contenu à l'écran d'US-ADM-04 —
  autrement vide et indémontrable ;
- **le chargement devient un test d'intégration de bout en bout** de tout ce que le
  sprint a produit. C'est le seul endroit du projet où les quinze stories s'exécutent
  ensemble.

Seule exception admise : les comptes utilisateurs dans des états particuliers — § 3.1 —
qu'aucun service ne sait produire volontairement.

## 1.3 · Idempotence et réinitialisation

Commande d'administration `charger_jeu_demonstration`, avec un drapeau
`--reinitialiser` qui vide d'abord les données de démonstration.

Sans drapeau, une seconde exécution ne doit ni échouer ni dupliquer. Le binôme
rechargera plusieurs fois pendant la recette, après avoir cassé quelque chose
volontairement.

---

# 2 · Principe de conception : chaque critère doit être exerçable

Le jeu n'est pas un échantillon vraisemblable : c'est un **échantillon construit**.
Pour chaque critère d'acceptation des quinze stories, il doit exister dans les données
au moins un objet permettant de le vérifier — **y compris les cas de refus**.

Concrètement, cela veut dire que le jeu contient délibérément des situations
inconfortables : un compte verrouillé, une matière que personne ne peut enseigner, une
formation dont les volumes ne tombent pas juste. Ce ne sont pas des erreurs de saisie,
ce sont les cas que la recette doit pouvoir montrer.

---

# 3 · Le contenu, entité par entité

## 3.1 · Comptes — US-ADM-01, 02, 03

Sept comptes, un par situation à démontrer. Mot de passe commun, respectant les
validateurs de Django, consigné dans le compte rendu.

| Identifiant | Profil | État particulier | Sert à démontrer |
|---|---|---|---|
| `adm.demo` | Administrateur | — | Accès complet, gestion des comptes, journal |
| `ped.demo` | Cellule pédagogique | — | Écriture sur le référentiel |
| `pla.demo` | Cellule planification | — | Écriture sur les lieux, lecture du référentiel |
| `exa.demo` | Cellule examens | — | Lecture du référentiel, **aucun accès aux instructeurs** |
| `dir.demo` | Direction de Formation | — | Lecture partout, écriture nulle part |
| `ped.inactif` | Cellule pédagogique | **Désactivé** | Critère 3 d'US-ADM-02 |
| `ped.nouveau` | Cellule pédagogique | **Changement de mot de passe exigé** | L'intergiciel d'US-ADM-02 |

Ajoute un huitième compte **verrouillé** — compteur d'échecs au seuil, déverrouillage
dans le futur —, ou fais en sorte que la recette puisse le produire en trois tentatives.
Dis-moi laquelle des deux voies tu retiens.

**Peuple le journal** : quelques authentifications échouées, quelques créations et
modifications de comptes, un refus d'habilitation. Sans cela l'écran d'US-ADM-04 est
vide et la recette ne peut rien en montrer.

## 3.2 · Types de formation — US-REF-00

Quatre : `Officiers`, `Sous-officiers`, `CAT-2`, et un quatrième **archivé**, pour
montrer qu'un archivé disparaît des listes de sélection sans disparaître de la
consultation.

## 3.3 · Formations — US-REF-01

Cinq, dont trois construites pour démontrer un point précis.

| Intitulé | Type | Durée | Point démontré |
|---|---|---|---|
| Formation initiale | Officiers | 20 sem. | — |
| **Formation initiale** | **Sous-officiers** | 24 sem. | **Même intitulé, type différent → l'écart 1 de CU-P2-02** |
| Perfectionnement radio | CAT-2 | 8 sem. | — |
| Spécialisation chiffre | Officiers | 6 sem. | **Volumes en écart avec la durée → avertissement non bloquant, critère 5 d'US-REF-03** |
| Stage transmissions | CAT-2 | 4 sem. | **Archivée** |

Les deux premières sont le cœur de la démonstration : elles prouvent que l'unicité
retenue est celle de la fiche, pas celle du backlog.

## 3.4 · Matières — US-REF-02

Douze au catalogue, réparties ainsi :

- **huit** rattachées à au moins un référentiel ;
- **une** rattachée à **deux formations avec des volumes différents** — critère 3
  d'US-REF-03 ;
- **une** rattachée à un référentiel mais **sans aucun instructeur qualifié** —
  critère 4 d'US-INS-02 ;
- **une** rattachée à rien du tout : elle doit pouvoir être supprimée, toutes les
  autres non ;
- **une archivée**.

Intitulés plausibles pour un centre de transmissions : procédures radio, chiffre et
sécurité, topographie, réseaux de campagne, entretien du matériel, ordre serré,
éducation physique, transmissions de données, protection électronique, secourisme,
règlement de discipline, anglais technique.

## 3.5 · Composition des référentiels — US-REF-03 et 04

Chaque formation non archivée reçoit **cinq à huit matières**. Les trois catégories de
lieu doivent apparaître, et les trois types de lieu partagé aussi :

- plusieurs matières en **salle attitrée** ;
- au moins une par type de **lieu partagé** — amphithéâtre, laboratoire, salle
  spécialisée ;
- au moins deux **sans lieu requis** — ordre serré, éducation physique.

Les volumes tombent juste pour trois formations et **délibérément faux** pour
*Spécialisation chiffre*, § 3.3.

## 3.6 · Objectifs pédagogiques — US-REF-05

- une matière portant **quatre objectifs** aux ordres 1 à 4 : c'est sur elle que la
  recette exercera l'échange de positions et la contrainte différée ;
- deux matières portant un ou deux objectifs ;
- les autres sans aucun objectif.

## 3.7 · Prérequis — US-REF-06

Dans le référentiel de *Formation initiale — Officiers*, une chaîne de trois :
**procédures radio → transmissions de données → protection électronique**, plus un lien
latéral pour que l'ordre topologique ne soit pas trivial.

Le référentiel de *Perfectionnement radio* **n'a aucun prérequis** : il sert à montrer
l'écran d'orientation quand il n'y a rien à afficher.

Ne charge évidemment aucun cycle — la recette en créera un à la main pour voir le refus
et la chaîne affichée.

## 3.8 · Instructeurs — US-INS-01

Dix, couvrant les trois statuts :

- six **militaires du centre**, avec matricule ;
- deux **vacataires** ;
- un **civil** ;
- un **archivé**.

Grades variés, spécialités prises dans un petit ensemble cohérent — transmissions,
chiffre, électronique, sport, langues — afin que le filtre par spécialité montre
plusieurs valeurs sans être un fouillis.

## 3.9 · Qualifications — US-INS-02

Couverture **volontairement partielle** :

- la plupart des matières comptent **deux à quatre** instructeurs qualifiés ;
- **une matière n'en compte aucun** — critère 4, signalement visuel ;
- **une matière n'en compte qu'un seul** : c'est elle qui montrera l'avertissement d'E2
  quand la recette retirera sa dernière qualification ;
- **un instructeur n'est qualifié pour rien**, pour montrer une fiche vide.

## 3.10 · Lieux — US-PLAN-02

| Type | Nombre | Capacités |
|---|---|---|
| Salles attitrables | 5 | 20, 25, 25, 30, 32 |
| Amphithéâtre | 1 | 150 |
| Laboratoire | 2 | 16, 18 |
| Salle spécialisée | 2 | 12, 24 |
| Archivé | 1 | — |

Les capacités variées servent le filtre par capacité minimale du critère 5.

**Indisponibilités** — sur un même lieu, trois périodes qui prouvent la contrainte
d'exclusion sans la violer :

- une **passée**, close ;
- une **future** ;
- une **contiguë** à la précédente, qui commence exactement quand l'autre finit. Elle
  doit être acceptée : c'est le cas limite que la recette vérifiera.

Un second lieu porte une période **qui recouvre celle du premier** — sur un lieu
différent, donc admise. Elle prouve que la contrainte porte bien sur le couple lieu et
période, non sur la période seule.

---

# 4 · Dates

Toutes les dates se calculent **par rapport à la date d'exécution**, jamais en dur.

Une date écrite en dur fait vieillir le jeu : les indisponibilités « futures »
deviennent passées, et la démonstration du 12 septembre ne montrerait plus ce qu'elle
doit montrer.

Le passé est à quelques semaines, le futur à quelques semaines aussi, la période
contiguë s'appuyant sur la fin exacte de la précédente.

---

# 5 · Ce que tu me rends

En plus du code :

**Un compte rendu de chargement** — nombre d'objets créés par entité, temps
d'exécution, et **la liste des règles métier effectivement exercées** pendant le
chargement. C'est cette liste qui fait du jeu un test d'intégration.

**Le mot de passe commun** et le tableau des sept comptes.

**Un fichier `docs/suivi/JEU-DEMONSTRATION.md`** décrivant le contenu, et surtout
**quel objet sert à démontrer quel critère**. Sans cette table, personne ne saura dans
six mois pourquoi une matière n'a aucun instructeur qualifié, et quelqu'un « corrigera »
l'anomalie.

**Signale-moi tout critère d'acceptation du sprint que le jeu ne permet pas
d'exercer.** C'est le point le plus important de ton compte rendu : un critère non
couvert par le jeu de démonstration est un critère que la revue du 12 ne pourra pas
montrer.

---

# 6 · Vérification

- La commande s'exécute sur une base vide, puis une seconde fois sans erreur ni doublon
- `--reinitialiser` remet dans l'état initial
- Les quinze tests d'architecture et la suite complète passent toujours
- `ruff check` et `ruff format --check` propres
- Aucune donnée réelle, vérifié par relecture
- Le journal contient des entrées de plusieurs natures

---

# 7 · Hors périmètre

- Sessions, brigades, stagiaires : paquetage P3, sprint 2
- Calendrier et grilles horaires : sprint 2
- Séances et programmes : sprint 3
- Évaluations : sprint 4
- Toute donnée destinée au prototype du solveur : elle viendra du même jeu, enrichi au
  sprint 2 des brigades et des créneaux

Commence par me proposer le plan de chargement et l'ordre des appels de service.
N'écris rien avant mon accord.
