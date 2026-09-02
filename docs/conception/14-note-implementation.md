**NOTE DE CHOIX D'IMPLÉMENTATION**

Traduction du modèle du domaine en schéma PostgreSQL · Système de gestion des activités de formation du CIT

*Livrable 4 / 5 — Phase 4 : Analyse et conception · **Version 3 du 30 août 2026** · Lot WBS 4.3*

# 1. Objet et statut

## 1.1 Pourquoi cette note et non un MLD

La démarche du projet est UML de bout en bout : `CLS-00` tient lieu de modèle conceptuel unique, et il n'existe ni MCD ni MLD Merise. Le niveau logique est traité par la présente note, qui est une **justification et non un second modèle**.

La distinction n'est pas cosmétique. Un MLD serait un modèle concurrent : il faudrait le maintenir en cohérence avec le diagramme de classes à chaque évolution, sur un domaine qui a déjà connu sept itérations sous l'effet des entretiens de terrain. Cette note, elle, ne redit pas le modèle — elle **explique comment il descend en base** et quelles décisions cette descente impose.

Ce qu'elle contient : la correspondance des types, les règles de nommage, la traduction des classes d'association, le placement des contraintes, les index nécessaires, le traitement des attributs dérivés et les politiques de suppression. Ce qu'elle ne contient pas : la liste des attributs, qui figure dans `CLS-00`, ni le code des modèles Django, qui relève de la réalisation.

## 1.2 Ce qui fonde les choix

| Exigence | Effet sur l'implémentation |
| --- | --- |
| **BNF-11** — intégrité portée en base | Les contraintes exprimables en SQL y descendent, sans se contenter d'un contrôle applicatif |
| **BNF-06** — aucune dépendance en ligne | Toute extension PostgreSQL utilisée est installée avant isolement du poste |
| **BNF-04** — génération en moins de cinq minutes | Les index sont dimensionnés pour les lectures du moteur de génération |
| **BNF-14** — horodatage et auteur de toute saisie | Classe de base commune, portée par l'application technique `noyau` |
| **Couche services systématique** | Les contraintes non exprimables en SQL sont implantées une seule fois, en services |

**Le principe directeur : chaque contrainte est portée au niveau le plus bas où elle est exprimable.** En base quand SQL sait la dire, en couche services sinon, jamais dans l'interface seule. Une règle qui ne vit que dans un formulaire est contournée dès qu'une donnée entre par un autre chemin — import, interface de programmation, migration.

# 2. Conventions

## 2.1 Nommage

| Élément | Convention | Exemple |
| --- | --- | --- |
| Table | `snake_case`, préfixée par l'application, au singulier | `referentiel_element_referentiel` |
| Colonne | `snake_case`, sans préfixe de table | `volume_horaire_prescrit` |
| Clé étrangère | Nom de l'entité cible suivi de `_id` | `formation_id` |
| Index | `idx_` suivi de la table et des colonnes | `idx_seance_debut_fin` |
| Contrainte de vérification | `ck_` suivi de la table et de l'objet | `ck_evaluation_perimetre` |
| Contrainte d'unicité | `uq_` suivi de la table et des colonnes | `uq_grille_active` |
| Contrainte d'exclusion | `ex_` suivi de la table et de l'objet | `ex_indispo_chevauchement` |

Les noms sont en français, sans accents ni caractères spéciaux. C'est un choix cohérent avec BNF-08, qui impose la terminologie du CIT : un développeur qui lit `volume_horaire_prescrit` retrouve immédiatement le terme du glossaire, là où `prescribed_hours` imposerait une traduction mentale à chaque lecture.

## 2.2 Correspondance des types

| Type métier de `CLS-00` | Type PostgreSQL | Champ Django | Motif |
| --- | --- | --- | --- |
| texte court | `varchar(n)` | `CharField` | Longueur bornée pour les codes et désignations |
| texte long | `text` | `TextField` | Motifs, commentaires, libellés sans borne naturelle |
| entier | `integer` | `IntegerField` | Volumes horaires, effectifs, rangs |
| décimal | `numeric(5,2)` | `DecimalField` | **Jamais `float`** — voir ci-dessous |
| date | `date` | `DateField` | Dates de session, dates d'évaluation |
| heure | `time` | `TimeField` | Bornes des créneaux types, sans date |
| horodatage | `timestamptz` | `DateTimeField` | Toujours avec fuseau |
| booléen | `boolean` | `BooleanField` | |
| énumération | `varchar` + contrainte | `TextChoices` | Voir section 2.3 |

**Décimal et non flottant, pour les notes et les coefficients.** Un flottant ne représente pas exactement 0,1 ; une moyenne pondérée calculée en flottant peut produire 11,999999 là où le calcul exact donne 12, et la mention change. Sur des notes qui fondent un certificat, c'est inacceptable. `numeric` calcule en décimal exact.

**Horodatage avec fuseau, systématiquement.** Le poste est en heure du Maroc, qui pratique un changement d'heure. Un horodatage sans fuseau produit une ambiguïté d'une heure deux fois par an, précisément sur des données de journal dont la valeur probante repose sur leur exactitude.

## 2.3 Les énumérations

Les douze énumérations de `CLS-00` sont implantées en `TextChoices` Django, stockées en `varchar`, avec une **contrainte de vérification en base** restreignant les valeurs admises.

Trois options existaient. Le type `enum` natif de PostgreSQL est le plus strict mais son évolution exige une migration lourde et son support par l'ORM est imparfait. Une table de référence par énumération est la plus souple mais multiplie les jointures pour des ensembles de trois à sept valeurs qui ne changeront pas. La solution retenue — chaîne contrainte — offre la vérification en base sans jointure ni migration structurelle.

Une exception : `NatureEvenement` **n'est pas une énumération** mais une table. Le terrain doit pouvoir ajouter une nature d'événement sans intervention sur le code, et chaque nature porte son effet par défaut. C'est une donnée de paramétrage, non un domaine de valeurs figé.

# 3. Correspondance des classes

Les trente classes du modèle donnent trente tables, réparties sur les six applications Django plus l'application technique.

| Application | Tables |
| --- | --- |
| `noyau` | *aucune table métier* — classe de base d'horodatage, mécanisme d'habilitation, gabarits |
| `administration` | `utilisateur`, `entree_journal` |
| `referentiel` | `type_formation`, `formation`, `matiere`, `element_referentiel`, `objectif_pedagogique`, `prerequis` |
| `organisation` | `session`, `brigade`, `stagiaire`, `affectation_brigade` |
| `ressources` | `instructeur`, `qualification`, `indisponibilite`, `lieu`, `grille_horaire`, `creneau_type`, `periode_calendrier`, `nature_evenement`, `periode_cible_session`, `periode_cible_brigade` |
| `planification` | `programme_hebdomadaire`, `seance`, `ligne_programme`, `non_execution` |
| `evaluations` | `evaluation`, `sujet`, `organisation_epreuve`, `surveillance`, `note`, `proces_verbal` |

**Trente classes, trente-trois tables.** Trois tables n'ont pas de classe correspondante : `prerequis`, qui matérialise l'association réflexive sur `element_referentiel`, et les deux tables de cibles de période. C'est le cas normal d'une association plusieurs-à-plusieurs sans attribut : elle ne mérite pas une classe dans le modèle conceptuel mais exige une table en base.

**Les habilitations reposent sur les groupes et permissions de Django.** Le profil demeure une énumération de cinq valeurs, mais les droits attachés à chaque profil sont portés par des groupes de permissions, modifiables par l'administrateur sans intervention sur le code (`RG-02 bis`). Le système est livré avec les cinq profils préconfigurés ; un ajustement ultérieur ne coûte qu'un paramétrage. Le mécanisme est natif au framework et son coût de mise en œuvre est marginal.

**`utilisateur` étend le modèle Django.** Django fournit un modèle d'utilisateur avec identifiant, empreinte de mot de passe, activation et dernière connexion. L'étendre plutôt que le remplacer donne gratuitement l'authentification, le hachage conforme à BNF-03 et la gestion de session. Les attributs propres au projet — grade, profil, compteur d'échecs, verrouillage — s'y ajoutent.

# 4. Les classes d'association

Les deux classes d'association du modèle sont le point où la traduction demande le plus d'attention.

## 4.1 ElementReferentiel

Table `element_referentiel`, portant `formation_id`, `matiere_id`, et les cinq attributs propres. **Unicité composite sur le couple** `(formation_id, matiere_id)` : c'est `RG-06`, une matière ne peut être rattachée qu'une fois au référentiel d'une formation.

**Une décision qui compte : la clé primaire est un identifiant technique, non le couple.** La clé composite serait plus « pure » conceptuellement, mais quatre autres tables référencent l'élément de référentiel — `seance`, `evaluation`, `designation_chef_module`, `objectif_pedagogique`. Une clé composite s'y propagerait en deux colonnes chacune, alourdissant les index et les jointures sans bénéfice. L'unicité du couple est garantie par une contrainte, ce qui suffit.

## 4.2 Qualification

Table `qualification`, portant `instructeur_id`, `matiere_id` et la date d'acquisition facultative. Unicité composite sur le couple. Ici aucune table ne référence la qualification : la clé composite serait tenable, mais l'homogénéité prime — toutes les tables du schéma portent un identifiant technique.

## 4.3 Prerequis

Table `prerequis`, portant deux clés étrangères vers `element_referentiel` — l'élément cible et l'élément requis. Unicité composite, et **contrainte de vérification interdisant qu'un élément soit son propre prérequis**.

L'acyclicité du graphe, elle, ne descend pas en base : voir section 6.

# 5. Contraintes portées en base

Six des treize contraintes recensées au diagramme de classes s'expriment en SQL.

## 5.1 Contraintes de vérification

**Exclusivité du périmètre d'évaluation.** `evaluation` porte `session_id` et `brigade_id`, tous deux facultatifs, avec une contrainte imposant qu'exactement un des deux soit renseigné :

> `ck_evaluation_perimetre` : `(session_id IS NOT NULL) <> (brigade_id IS NOT NULL)`

C'est la traduction directe de la décision du 25 août. Sans elle, une évaluation orpheline ou doublement rattachée deviendrait possible dès qu'une donnée entrerait par un autre chemin que le formulaire.

**Nature du surveillant.** Même construction sur `surveillance` : soit `instructeur_id`, soit `nom_libre`, jamais les deux, jamais aucun.

**Cohérence des intervalles.** Sur `session`, `indisponibilite`, `periode_calendrier`, `seance` et `creneau_type` : la borne de fin est strictement postérieure à la borne de début.

**Domaines de valeurs.** Une contrainte par énumération, restreignant la colonne aux valeurs admises.

**Volume prescrit strictement positif** sur `element_referentiel`, conformément à `RG-08` rétablie après la suppression de la modalité d'enseignement.

## 5.2 Index uniques partiels

Trois règles s'expriment par un index unique portant une condition — construction propre à PostgreSQL, plus économe qu'un déclencheur.

**Une seule grille active.** `uq_grille_active` sur `grille_horaire`, unique sur une constante, restreint aux lignes où `active` est vrai. Toute tentative d'activer une seconde grille échoue en base. C'est `RG-62`.

**Un seul sujet retenu par évaluation.** `uq_sujet_retenu` sur `sujet`, unique sur `evaluation_id`, restreint aux lignes où `retenu` est vrai. C'est `RG-50`.

**Une seule affectation ouverte par stagiaire.** `uq_affectation_ouverte` sur `affectation_brigade`, unique sur `stagiaire_id`, restreint aux lignes où `date_fin` est nulle. C'est `RG-20`, et c'est ce qui permet d'historiser les changements de brigade sans perdre l'invariant.

## 5.3 Contrainte d'exclusion

**Non-chevauchement des indisponibilités d'un même instructeur.** `RG-24` porte sur des intervalles de temps, que ni une unicité ni une vérification simple ne savent exprimer. PostgreSQL offre la construction exacte :

> `ex_indispo_chevauchement` : contrainte d'exclusion garantissant que deux lignes de même `instructeur_id` n'ont pas d'intervalles `[debut, fin)` sécants.

**Elle exige l'extension `btree_gist`**, qui permet de combiner l'égalité sur l'instructeur et le recouvrement sur l'intervalle dans un même index. C'est une extension standard de PostgreSQL, mais elle doit être **installée avant l'isolement du poste** au titre de BNF-06 : elle est à ajouter à la liste des dépendances de déploiement.

## 5.4 Immuabilité du journal

`RG-27` interdit toute modification et toute suppression d'une entrée de journal, y compris par l'administrateur. Une règle applicative ne suffit pas : le rôle de connexion de l'application doit se voir **révoquer les droits de mise à jour et de suppression** sur la table `entree_journal`, l'insertion seule restant permise.

C'est le seul endroit du schéma où la sécurité repose sur les privilèges plutôt que sur une contrainte. C'est aussi ce qui donne au journal sa valeur probante : une trace qu'on peut effacer ne prouve rien.

## 5.5 Unicités composites

`brigade` porte une unicité sur la désignation **au sein du type de formation**, et non globalement. Les progressions d'instruction montrent `EXP1` et `EXP2` dans deux blocs de type différent : une unicité globale produirait des refus injustifiés. La contrainte remonte donc par la session et la formation jusqu'au type, ce qui impose de dénormaliser le type sur la brigade ou de porter la vérification en services. **Choix retenu : en services**, la dénormalisation créant une redondance qu'il faudrait maintenir.

`stagiaire` porte une unicité sur `(session_id, matricule)` — `RG-17`.

`programme_hebdomadaire` porte une unicité sur le lundi de semaine : un seul programme par semaine pour le centre.

# 6. Contraintes portées en couche services

Sept contraintes ne descendent pas en base, et il faut savoir pourquoi.

| Contrainte | Motif de non-descente |
| --- | --- |
| Acyclicité du graphe des prérequis (`RG-10`) | Propriété de graphe : aucune construction SQL déclarative ne l'exprime |
| Deux sujets si certificative, un si formative (`RG-50`) | Conditionnelle au type, portant sur un agrégat de lignes filles |
| Capacité du lieu supérieure à l'effectif (`RG-13`, `RG-19`, `RG-37`) | L'effectif est **dérivé** : il n'existe pas de colonne à comparer |
| Unicité d'affectation de l'instructeur (`RG-34`) | L'exception de la séance regroupée l'exclut d'une contrainte d'exclusion |
| Créneau non bloqué par une période (`RG-38`) | Dépend de la portée, elle-même dérivée des cibles |
| Volume programmé n'excédant pas le prescrit (`RG-39`) | Porte sur une somme de lignes filles |
| Désignation de brigade unique par type de formation | Remonte trois niveaux de relations |

**Ces sept contraintes justifient à elles seules la couche services systématique** décidée en phase 3. Sans elle, elles seraient dispersées dans les vues et les formulaires, avec la certitude de divergences : un programme généré et un programme saisi n'obéiraient plus aux mêmes règles.

Le service de contrôle des contraintes dures — `CU-P5-02` — est l'implantation unique des six règles `RG-34` à `RG-39`, appelé par la génération, la modification manuelle, le regroupement et la duplication.

# 7. Les attributs dérivés

Les neuf attributs dérivés de `CLS-00` **ne donnent aucune colonne**. Trois techniques sont disponibles et le choix se fait par mesure, non par principe.

| Technique | Usage | Coût |
| --- | --- | --- |
| Propriété calculée en Python | Grandeur portant sur un objet unique — durée d'une séance, portée d'une période | Nul en base, une requête par objet |
| Agrégat annoté dans la requête | Grandeur portant sur une collection — volume programmé, charge d'un instructeur | Une seule requête pour l'ensemble |
| Vue matérialisée | Grandeur coûteuse et lue plus souvent qu'écrite | Rafraîchissement à gérer |

**Décision : commencer par les deux premières, mesurer, n'introduire une vue matérialisée que si un temps de réponse le justifie.** Une vue matérialisée introduite par précaution ajoute une donnée à rafraîchir et une occasion de divergence — précisément ce que la règle des grandeurs dérivées cherche à éviter.

Le seul candidat plausible est le rapprochement prescrit-réalisé consulté sur une session entière, qui agrège les séances de toutes les brigades sur toutes les matières. Il sera mesuré au sprint 4, sur le jeu de données de test.

# 8. Index

Les index ne sont pas ajoutés par précaution mais déduits des lectures que les cas d'utilisation imposent.

## 8.1 Index dictés par la génération

`SEQ-01` établit que le moteur lit, pour une semaine donnée, **toutes les séances de toutes les sessions actives**. C'est la lecture la plus lourde du système et elle conditionne BNF-04.

| Index | Table | Colonnes | Lecture servie |
| --- | --- | --- | --- |
| `idx_seance_debut_fin` | `seance` | `date_heure_debut`, `date_heure_fin` | Séances d'une semaine |
| `idx_seance_instructeur_debut` | `seance` | `instructeur_id`, `date_heure_debut` | Unicité d'affectation, charge |
| `idx_seance_lieu_debut` | `seance` | `lieu_id`, `date_heure_debut` | Occupation des lieux |
| `idx_ligne_brigade` | `ligne_programme` | `brigade_id` | Programme d'une brigade |
| `idx_indispo_instructeur` | `indisponibilite` | `instructeur_id`, `date_heure_debut` | Disponibilité d'un instructeur |
| `idx_periode_debut_fin` | `periode_calendrier` | `date_heure_debut`, `date_heure_fin` | Périodes couvrant une semaine |

L'index d'exclusion sur `indisponibilite` sert également les recherches de chevauchement, sans index supplémentaire.

## 8.2 Index dictés par le suivi

| Index | Table | Colonnes |
| --- | --- | --- |
| `idx_seance_element` | `seance` | `element_referentiel_id` |
| `idx_note_evaluation` | `note` | `evaluation_id` |
| `idx_note_stagiaire` | `note` | `stagiaire_id` |
| `idx_journal_horodatage` | `entree_journal` | `horodatage` décroissant |
| `idx_journal_objet` | `entree_journal` | `objet_type`, `objet_identifiant` |

Les clés étrangères reçoivent un index par défaut sous Django ; ceux listés ici sont les index composites qui n'existent pas automatiquement.

# 9. Politiques de suppression

Le modèle applique une règle générale : **l'archivage remplace la suppression** dès qu'un élément est référencé par une donnée historique. Cela se traduit en trois politiques.

| Politique | Application | Exemples |
| --- | --- | --- |
| **Interdiction** | Par défaut, sur toute clé étrangère vers une entité de référence | Formation, matière, instructeur, lieu, session, brigade |
| **Cascade** | Composition stricte : l'élément fils n'a aucun sens sans son père | `creneau_type` → `grille_horaire` · `ligne_programme` → `seance` · `sujet` → `evaluation` · `surveillance` → `organisation_epreuve` |
| **Mise à nul** | Référence facultative dont la disparition n'invalide pas le porteur | `seance` → `creneau_type` · `seance` → `evaluation` |

`avenant` et `non_execution` suivent la cascade : ils n'ont aucun sens sans la séance ou la ligne de programme qui les porte.

**L'interdiction est le défaut, et c'est délibéré.** Une cascade posée par commodité efface silencieusement des données dont personne n'avait mesuré la portée : supprimer une formation ne doit jamais emporter ses sessions, ses brigades et les notes de ses stagiaires. Le refus force à traiter explicitement chaque cas, ce qui est le comportement attendu d'un système dont la traçabilité est une exigence.

Les entités porteuses d'un indicateur d'archivage — formation, matière, instructeur, lieu — ne sont supprimables que si elles n'ont jamais été utilisées.

# 10. Migrations et jeu de données

## 10.1 Migrations

Les migrations Django sont **versionnées dans le dépôt** et jamais modifiées après avoir été appliquées ailleurs que sur un poste de développement. Les contraintes qui n'ont pas d'expression déclarative dans l'ORM — index uniques partiels, contrainte d'exclusion, révocation de privilèges sur le journal — sont écrites en SQL explicite dans une migration dédiée, commentée et réversible.

L'extension `btree_gist` fait l'objet d'une migration initiale distincte, exécutée avant celle qui pose la contrainte d'exclusion.

## 10.2 Jeu de données de test

Le jeu de test doit couvrir les cas que le modèle a été construit pour absorber, faute de quoi les contraintes ne seront jamais exercées.

| Situation à représenter | Ce qu'elle vérifie |
| --- | --- |
| Trois sessions simultanées de formations différentes | Résolution centre-entier, `RG-34` |
| Une session à trois brigades, progressions décalées | `RG-16`, `RG-33` |
| Une séance regroupant deux brigades en lieu partagé | `RG-40` |
| Une séance regroupant trois brigades sans lieu | Correction du 26 août |
| Une séance couvrant deux créneaux consécutifs | `RG-64` |
| Une séance hors grille, un samedi | `RG-64` |
| Deux grilles horaires, une active | `RG-62` |
| Une période visant deux sessions et une brigade | `RG-30` |
| Le PFE évalué en formatif dans une formation, en certificatif dans une autre | Double pondération |
| Une évaluation certificative de périmètre session, trois salles | `RG-53 bis` |
| Un surveillant extérieur au système | `RG-53` |
| Une non-exécution déclarée | `RG-60` |

**Règle absolue : aucune donnée réelle du CIT.** Pas de liste nominative, pas de sujet d'examen, pas de nom d'instructeur. Les jeux de test sont entièrement fictifs. Un fichier poussé une fois demeure dans l'historique Git même après suppression.

# 11. Ce que cette note ne tranche pas

**Le dimensionnement.** Le nombre de sessions simultanées, de brigades et d'instructeurs du CIT n'est pas connu avec précision. Les index proposés sont dictés par la forme des requêtes, non par des volumétries mesurées. Ils seront réévalués au sprint 2, sur le jeu de test dimensionné pour le prototype du solveur.

**La stratégie de sauvegarde**, qui relève du dossier de déploiement et non de la conception.

**Le choix de la bibliothèque de génération PDF**, lot 4.2.3, à trancher avant le 26 août au soir. Elle devra embarquer ses polices et ne dépendre d'aucune ressource en ligne, conformément à BNF-06.

---

*Livrable 4 / 5 de la phase 4 — version 3 du 30 août 2026. Tâche WBS 4.3. Traduit `CLS-00` version 4 du 30 août 2026.*
