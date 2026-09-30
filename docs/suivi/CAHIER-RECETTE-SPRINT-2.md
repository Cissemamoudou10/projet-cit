# Cahier de recette — Sprint 2

**Projet.** Création des activités du CIT (Activités pédagogiques, programmation
des cours et séances d'instruction) — Centre d'instruction des transmissions.

**Périmètre.** Les douze stories du sprint 2 : US-SES-01 à US-SES-07,
US-INS-03, US-PLAN-01, US-PLAN-12, US-PLAN-04, US-PLAN-03.

**Version de référence.** Backlog produit v8, cahier des charges v8, fiches de
cas d'utilisation v4, diagramme de classes v4, note d'implémentation v3.

**Date de rédaction.** _____________  **Recetteur.** _____________

---

## 1. Objet et portée

Ce cahier vérifie que le périmètre livré au sprint 2 satisfait les critères
d'acceptation du backlog, les enchaînements et exceptions des fiches de cas
d'utilisation, et les règles de gestion associées.

**Il est construit à partir des spécifications, non du code.** C'est une
exigence de méthode : un cahier de recette rédigé depuis l'implantation vérifie
ce qui a été fait, non ce qui était demandé, et ne trouve donc jamais un besoin
oublié. Un contrôle qui ne correspond à aucun écran existant n'est pas une
erreur de ce cahier — c'est un écart à consigner.

### Ce qui n'est pas dans le périmètre

Le périmètre du sprint 1 — authentification, habilitations, journal, référentiel
de formation, instructeurs, qualifications, lieux — a fait l'objet de sa propre
recette, le 4 septembre 2026, 115 contrôles, sept écarts majeurs refermés. Il
n'est pas rejoué ici.

En revanche, les **points de jonction** entre les deux périmètres sont contrôlés,
au titre de la non-régression : le sprint 2 pose des contraintes nouvelles sur
des objets du sprint 1 — une formation ne se supprime plus si elle porte une
session, un lieu ne se supprime plus s'il est attitré ou affecté, une
qualification voit son retrait contraint. Ces contrôles figurent au § 8.

### Ce qui n'est pas contrôlable à ce stade

Certains critères d'acceptation du sprint 2 ont été formellement reportés à une
story ultérieure, faute du modèle qu'ils supposent. Ils sont recensés au § 10 et
**ne sont pas comptés dans le résultat de la recette** : les déclarer « non
testés » sans les distinguer des contrôles échoués fausserait le dépouillement.

---

## 2. Méthode et conventions

### Mode opératoire

Chaque contrôle s'exécute **par l'interface**, dans un navigateur, avec le profil
indiqué. Jamais par la console d'administration, jamais par un appel de service :
la recette vérifie le système tel que l'utilisateur le rencontre. C'est la leçon
du sprint 1, où cinq des sept écarts majeurs venaient de contrôles qui ne
traversaient pas le cycle web réel.

### Notation

| Code | Signification |
|---|---|
| **C** | Conforme — le résultat observé correspond à l'attendu |
| **NC** | Non conforme — écart constaté |
| **B** | Bloqué — le contrôle n'a pas pu être exécuté (dépendance en échec) |
| **SO** | Sans objet — le contrôle ne s'applique pas dans cette version |

### Sévérité d'un écart

| Niveau | Définition | Effet sur la recette |
|---|---|---|
| **Majeur** | Une règle de gestion est violée, une donnée est perdue ou corrompue, une habilitation est contournée, ou un critère d'acceptation n'est pas tenu | Bloque le prononcé de la recette |
| **Mineur** | Libellé, ergonomie, message imprécis, mise en page — sans effet sur la donnée ni sur la règle | N'empêche pas le prononcé, entre au reste à faire |

### Traçabilité

Chaque contrôle porte une référence : critère d'acceptation (`crit. n`), règle de
gestion (`RG-nn`), exception ou enchaînement de fiche (`E1`, `A2`), besoin non
fonctionnel (`BNF-nn`). Un contrôle sans référence est un contrôle inventé : il
n'en figure aucun dans ce cahier.

### Anomalies

Tout `NC` donne lieu à une fiche d'anomalie (modèle au § 12), reportée dans
`docs/suivi/PROBLEMES.md` avec son code de contrôle.

---

## 3. Environnement

| Élément | Valeur | Vérifié |
|---|---|---|
| Version applicative / commit | | ☐ |
| Base de données | PostgreSQL, extension `btree_gist` présente | ☐ |
| Mode d'exécution | conteneurisé, image de production | ☐ |
| Navigateur | | ☐ |
| Données | jeu de recette du § 4, chargé sur base vierge | ☐ |
| Date système | cohérente (contrôles de périodes passées/futures) | ☐ |

---

## 4. Jeu de données de recette

À constituer **avant** le premier contrôle, sur base vierge. Le jeu est
volontairement petit : il doit tenir dans une journée d'exécution manuelle et
rester lisible à l'œil.

### 4.1 Comptes

| Compte | Profil |
|---|---|
| `u_ped` | Cellule pédagogique |
| `u_plan` | Cellule planification |
| `u_exa` | Cellule examens |
| `u_df` | Direction de la formation |
| `u_adm` | Administrateur |

### 4.2 Référentiel (périmètre sprint 1, à saisir en préalable)

| Objet | Contenu |
|---|---|
| Types de formation | `TF1` Formation initiale · `TF2` Formation de spécialité |
| Formations | `F1` Exploitant radio (TF1) · `F2` Chef de poste (TF2) · `F3` Formation archivée (TF1, **archivée**) · `F4` Formation sans référentiel (TF1) |
| Matières | `M1` (salle attitrée) · `M2` (lieu partagé) · `M3` (sans lieu) · `M4` (salle attitrée) · `M5` (salle attitrée) |
| Référentiel `F1` | M1 = 20 h · M2 = 10 h · M3 = 10 h |
| Référentiel `F2` | M4 = 10 h · M5 = 10 h, **M4 prérequis de M5** |
| Référentiel `F3` | M1 = 10 h |
| Référentiel `F4` | **vide** |
| Instructeurs | `I1` qualifié M1, M2, M3 · `I2` qualifié M1 · `I3` qualifié M2 · `I4` qualifié M1, **archivé** · `I5` qualifié M4, M5 |
| Lieux | `L1` salle attitrée, cap. 20 · `L2` salle attitrée, cap. 15 · `L3` salle attitrée, **capacité non renseignée** · `L4` lieu partagé simultané, cap. 30 · `L5` lieu partagé séquentiel, cap. 30 · `L6` salle attitrée, **archivé** |

### 4.3 Périmètre sprint 2, constitué au fil des contrôles

Les sessions, brigades, stagiaires, périodes de calendrier et grilles horaires
sont créés **par les contrôles eux-mêmes**. Ne les préchargez pas : leur création
est précisément ce qui est recetté.

Exception : les deux grilles horaires livrées en données de départ (Ordinaire
active, Ramadan inactive) doivent être présentes avant le § 7.

---

## 5. Paquetage Organisation — sessions, brigades, stagiaires

### 5.1 US-SES-01 · Ouvrir une session de formation

Profil : `u_ped` sauf indication contraire.

| Code | Contrôle | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|
| R2-SES01-01 | Créer une session sur `F1`, du 05/10 au 20/12, effectif attendu 40 | Session créée, état **ouverte**, rattachée à `F1` | crit. 1 | ☐ | |
| R2-SES01-02 | Ouvrir la fiche de la session créée | Le référentiel de `F1` y est présenté (matières et volume total) | crit. 2 | ☐ | |
| R2-SES01-03 | Modifier le volume prescrit de `M1` dans le référentiel de `F1` (40 h au lieu de 20), revenir sur la fiche de session | La session affiche la **nouvelle** valeur — le référentiel est lu, jamais recopié | crit. 2, RG-05 | ☐ | |
| R2-SES01-04 | Remettre `M1` à 20 h | Valeur rétablie | — | ☐ | |
| R2-SES01-05 | Créer une seconde session sur `F1`, du 05/01 au 20/03 | Acceptée — deux sessions d'une même formation coexistent | crit. 3 | ☐ | |
| R2-SES01-06 | Créer une troisième session sur `F1`, du 01/12 au 28/02 (chevauche les deux précédentes) | **Acceptée** — le chevauchement n'est pas opposé | A1 | ☐ | |
| R2-SES01-07 | Supprimer la session du contrôle 06 | Supprimée | — | ☐ | |
| R2-SES01-08 | Créer une session sur `F3` (formation archivée) | **Refus**, message nommant la formation et l'action corrective | crit. 4 | ☐ | |
| R2-SES01-09 | Créer une session sur `F4` (référentiel vide) | **Refus**, message renvoyant vers la composition du référentiel | E4 | ☐ | |
| R2-SES01-10 | Créer une session dont la date de fin précède la date de début | **Refus** | E1 | ☐ | |
| R2-SES01-11 | Créer une session dont la date de fin **égale** la date de début | **Refus** | E1 | ☐ | |
| R2-SES01-12 | Créer une session avec un effectif attendu de 0, puis de −5 | **Refus** dans les deux cas | E3 | ☐ | |
| R2-SES01-13 | Créer une session sur `F1` du 05/10 au 12/10 (période très courte au regard du volume prescrit) | Session **créée**, avec un **avertissement** sur l'incompatibilité durée / volume — jamais un refus | E2, RG-65 | ☐ | |
| R2-SES01-14 | Créer deux sessions sur `F1` à des dates arbitraires sans rythme régulier | Acceptées — aucune périodicité n'est imposée | crit. 5 | ☐ | |
| R2-SES01-15 | Créer une seconde session sur `F1` portant le **même intitulé** qu'une existante | Comportement conforme à la règle d'unicité retenue ; noter lequel | D. unicité | ☐ | |
| R2-SES01-16 | Lister les sessions, filtrer par formation puis par état | Filtres opérants | BNF-15 | ☐ | |
| R2-SES01-17 | Créer plus de vingt sessions, ou vérifier sur le volume existant | Pagination active au-delà du seuil | BNF-15 | ☐ | |

### 5.2 US-SES-02 · Constituer les brigades d'une session

Session de travail : celle du contrôle R2-SES01-01 (`F1`, effectif attendu 40).

| Code | Contrôle | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|
| R2-SES02-01 | Ouvrir la fiche de session : consulter l'emplacement Brigades | Accessible, la session n'ayant encore aucune brigade est **signalée** | crit. 2 | ☐ | |
| R2-SES02-02 | Créer la brigade `EXP1`, effectif 20 | Créée, rattachée à la session | crit. 1, 3 | ☐ | |
| R2-SES02-03 | Observer l'indicateur d'écart après cette première brigade | Écart affiché (20 sur 40 attendus), **sans blocage** | crit. 4, RG-15 | ☐ | |
| R2-SES02-04 | Créer la brigade `EXP2`, effectif 20 | Créée ; l'écart tombe à zéro et l'indicateur le montre | crit. 4 | ☐ | |
| R2-SES02-05 | Créer la brigade `EXP3`, effectif 10 (somme 50 > 40 attendus) | **Acceptée**, avec avertissement de dépassement | crit. 4, RG-15 | ☐ | |
| R2-SES02-06 | Supprimer `EXP3` | Supprimée | — | ☐ | |
| R2-SES02-07 | Créer une brigade `exp1` (même désignation, casse différente) dans la **même** session | **Refus**, brigade existante désignée | D. unicité | ☐ | |
| R2-SES02-08 | Créer une brigade `EXP1` dans une **autre** session | **Acceptée** | D. unicité | ☐ | |
| R2-SES02-09 | Créer une brigade avec effectif 0, puis −3 | **Refus** dans les deux cas | crit. 3 | ☐ | |
| R2-SES02-10 | Créer une brigade **sans** saisir d'effectif | Refus ; **aucune valeur par défaut n'est proposée** — le système ne calcule pas la répartition | RG-12 | ☐ | |
| R2-SES02-11 | Supprimer `EXP2`, puis tenter de supprimer `EXP1` (dernière brigade) | Première suppression acceptée ; seconde **refusée**, message nommant l'action corrective | crit. 2 | ☐ | |
| R2-SES02-12 | Recréer `EXP2` | Créée | — | ☐ | |
| R2-SES02-13 | Sur une session **déjà commencée** (date de début passée), créer une brigade | Acceptée, avec **avertissement** de démarrage en décalage | A3, RG-16 | ☐ | |
| R2-SES02-14 | Tenter de supprimer la session portant `EXP1` et `EXP2` | **Refus**, brigades énumérées | PROTECT | ☐ | |
| R2-SES02-15 | Vérifier que la couleur de l'indicateur d'écart est doublée d'un mot | Mot présent, pas de couleur seule | charte | ☐ | |

### 5.3 US-SES-03 · Affecter une salle attitrée à chaque brigade

Profil : **`u_plan`** — c'est le point à ne pas rater de cette story.

| Code | Contrôle | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|
| R2-SES03-01 | Avec `u_ped`, chercher la commande d'affectation d'une salle attitrée | **Absente ou refusée** — la cellule pédagogique n'attribue pas les salles | matrice | ☐ | |
| R2-SES03-02 | Avec `u_plan`, chercher la commande de création d'une brigade | **Absente ou refusée** — la planification ne constitue pas les brigades | matrice | ☐ | |
| R2-SES03-03 | Avec `u_plan`, attribuer `L1` (cap. 20) à `EXP1` (effectif 20) | **Acceptée** — capacité égale à l'effectif | crit. 2, RG-13 | ☐ | |
| R2-SES03-04 | Attribuer `L2` (cap. 15) à `EXP2` (effectif 20) | **Refus**, avec l'écart chiffré dans le message | crit. 2, E1 | ☐ | |
| R2-SES03-05 | Attribuer `L3` (capacité non renseignée) à `EXP2` | Comportement conforme à la décision retenue ; noter lequel et vérifier que le message nomme la salle | RG-13 | ☐ | |
| R2-SES03-06 | Attribuer `L6` (archivé) à `EXP2` | **Refus** | — | ☐ | |
| R2-SES03-07 | Attribuer `L4` (lieu partagé) à `EXP2` comme salle attitrée | **Refus** — un lieu partagé n'est pas attribuable à demeure | catégorie | ☐ | |
| R2-SES03-08 | Attribuer `L1` (déjà attitrée à `EXP1`) à une brigade d'une session dont la période **chevauche** | **Refus**, brigade occupante, session et période nommées | crit. 3, E2, RG-14 | ☐ | |
| R2-SES03-09 | Attribuer `L1` à une brigade d'une session dont la période est **disjointe** | **Acceptée** | RG-14 | ☐ | |
| R2-SES03-10 | Sur une session en cours, remplacer la salle attitrée d'une brigade par une salle occupée sur une période **déjà écoulée** | **Acceptée** — seule la période restante compte | A2 | ☐ | |
| R2-SES03-11 | Vérifier le journal après le contrôle 10 | Ancienne et nouvelle salle enregistrées | A2 | ☐ | |
| R2-SES03-12 | Retirer la salle attitrée d'une brigade | Acceptée — une brigade sans salle est un état transitoire légitime | — | ☐ | |
| R2-SES03-13 | Déclarer une indisponibilité sur `L1` recouvrant la session, puis l'attribuer | **Acceptée** avec avertissement énumérant les périodes | avertissement | ☐ | |
| R2-SES03-14 | Sur la fiche de `L1`, consulter les brigades auxquelles il est attitré | Liste présente, avec session et période | lisibilité | ☐ | |
| R2-SES03-15 | Tenter de supprimer `L1`, attitré à une brigade | **Refus**, brigades énumérées | D-54 | ☐ | |

### 5.4 US-SES-04 · Consulter la composition d'une session

| Code | Contrôle | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|
| R2-SES04-01 | Avec `u_ped`, ouvrir la fiche de composition | Brigades, effectifs et salles attitrées présentés | crit. 1 | ☐ | |
| R2-SES04-02 | Consulter le référentiel appliqué depuis cette fiche | Accessible | crit. 2 | ☐ | |
| R2-SES04-03 | Vérifier le taux d'occupation de `EXP1` (effectif 20, salle cap. 20) | **100 %** | écart CU | ☐ | |
| R2-SES04-04 | Consulter une brigade **sans** salle attitrée | Mention explicite, **pas de case vide ni de zéro** | écart CU | ☐ | |
| R2-SES04-05 | Porter l'effectif de `EXP1` à 25 (salle cap. 20), revenir sur la fiche | Taux > 100 %, **signalé**, avec les deux nombres | limite US-SES-03 | ☐ | |
| R2-SES04-06 | Remettre `EXP1` à 20 | Rétabli | — | ☐ | |
| R2-SES04-07 | Ouvrir la fiche avec `u_plan` | Accès accordé | crit. 3 | ☐ | |
| R2-SES04-08 | Ouvrir la fiche avec `u_exa` | Accès accordé | crit. 3 | ☐ | |
| R2-SES04-09 | Ouvrir la fiche avec **`u_df`** | **Accès accordé** — l'omission de la Direction de la formation au critère 3 est un écart de rédaction du backlog | matrice, D-44 | ☐ | |
| R2-SES04-10 | Avec `u_df`, chercher une commande d'écriture sur cette fiche | **Aucune**, pas même grisée | crit. 3 | ☐ | |
| R2-SES04-11 | Avec `u_ped`, vérifier la présence du lien vers l'écran des brigades | Présent | navigation | ☐ | |
| R2-SES04-12 | Avec `u_df`, vérifier l'absence de ce lien | Absent | navigation | ☐ | |
| R2-SES04-13 | Imprimer la fiche (aperçu) | Aucune colonne de donnée masquée, colonne Actions masquée, pas de débordement latéral | D-63, K3 | ☐ | |

### 5.5 US-SES-05 · Enregistrer les stagiaires d'une session

| Code | Contrôle | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|
| R2-SES05-01 | Saisir un stagiaire à la main : matricule, nom, prénom, grade, unité | Créé, rattaché à la session | crit. 1, 2 | ☐ | |
| R2-SES05-02 | Saisir un second stagiaire avec le **même matricule** dans la même session | **Refus**, doublon désigné | crit. 6, RG-17 | ☐ | |
| R2-SES05-03 | Saisir le même matricule en **casse différente** | **Refus** | RG-17 | ☐ | |
| R2-SES05-04 | Saisir le même matricule dans une **autre** session | **Accepté** | RG-17 | ☐ | |
| R2-SES05-05 | Saisir un stagiaire en omettant l'unité d'origine | Refus, champ nommé | crit. 1 | ☐ | |
| R2-SES05-06 | Télécharger le modèle de fichier | Téléchargement effectif, en-têtes en français | crit. 4 | ☐ | |
| R2-SES05-07 | Déposer le **modèle vide** à l'import | Accepté, zéro ligne, aucune erreur | crit. 4 | ☐ | |
| R2-SES05-08 | Importer un CSV de 10 lignes valides — **étape d'analyse** | Compte rendu annonçant 10 lignes valides, **et aucun stagiaire créé à ce stade** | crit. 5 | ☐ | |
| R2-SES05-09 | Confirmer l'import | Les 10 stagiaires créés | RG-18 | ☐ | |
| R2-SES05-10 | Importer un fichier XLSX de 5 lignes valides | Analyse puis confirmation conformes | crit. 3 | ☐ | |
| R2-SES05-11 | Importer un CSV contenant des noms accentués, encodé UTF-8 avec BOM | Accents corrects, aucune substitution | robustesse | ☐ | |
| R2-SES05-12 | Importer le même fichier encodé CP1252 | Accents corrects | robustesse | ☐ | |
| R2-SES05-13 | Importer un CSV à séparateur virgule, puis à point-virgule | Les deux acceptés | robustesse | ☐ | |
| R2-SES05-14 | Importer un fichier dont les colonnes sont dans un **ordre différent** | Accepté, identification par en-tête | robustesse | ☐ | |
| R2-SES05-15 | Importer un fichier **sans** la colonne matricule | **Refus global**, colonne manquante nommée, aucun import partiel | crit. 5, E2 | ☐ | |
| R2-SES05-16 | Importer un fichier dont la ligne 12 a un matricule vide | Ligne **12** signalée, motif explicite, les autres restent importables | crit. 5 | ☐ | |
| R2-SES05-17 | Importer un fichier contenant deux fois le même matricule | Ligne signalée et exclue, les autres importables | E4 | ☐ | |
| R2-SES05-18 | Importer un fichier contenant un matricule **déjà en base** | Signalé comme déjà présent et **ignoré**, message **distinct** du contrôle 17 | A2 | ☐ | |
| R2-SES05-19 | Importer un fichier dont **toutes** les lignes sont en anomalie | Compte rendu présenté, **confirmation impossible** | E3 | ☐ | |
| R2-SES05-20 | Déposer un fichier d'un format non reconnu (PDF renommé en .csv) | Refus propre, rappel du format, renvoi vers le modèle — **aucune trace technique brute** | E1 | ☐ | |
| R2-SES05-21 | Consulter le journal après un import réussi | Entrée portant le **nombre** de lignes, **aucune identité de stagiaire** | données nominatives | ☐ | |
| R2-SES05-22 | Radier un stagiaire : motif et date | Stagiaire **conservé**, marqué radié | A4 | ☐ | |
| R2-SES05-23 | Radier sans motif, puis sans date | Refus dans les deux cas | cohérence | ☐ | |
| R2-SES05-24 | Filtrer la liste : actifs / radiés / tous | Trois résultats distincts | A4 | ☐ | |
| R2-SES05-25 | Comparer les commandes **Supprimer** et **Radier** | Libellés distincts, confirmations distinctes, aucune confusion possible | BNF-09 | ☐ | |
| R2-SES05-26 | Dé-radier un stagiaire (ou constater que ce n'est pas offert) | Conforme à la décision retenue ; noter laquelle | A4 | ☐ | |
| R2-SES05-27 | Supprimer un stagiaire sans affectation ni note | Accepté | — | ☐ | |

### 5.6 US-SES-06 · Affecter les stagiaires aux brigades

Session de travail : `F1`, brigades `EXP1` (20) et `EXP2` (20), au moins 45
stagiaires enregistrés.

| Code | Contrôle | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|
| R2-SES06-01 | Lancer la proposition de répartition | Proposition affichée, **et aucune affectation enregistrée à ce stade** | crit. 1 | ☐ | |
| R2-SES06-02 | Vérifier la répartition proposée sur 40 stagiaires, brigades déclarées 20 et 20 | **20 / 20** — remplissage séquentiel jusqu'à l'effectif déclaré, pas d'équilibrage | crit. 1, RG-12 | ☐ | |
| R2-SES06-03 | Relancer la proposition sans rien changer | **Résultat identique** — déterminisme | crit. 1 | ☐ | |
| R2-SES06-04 | Proposer avec 45 stagiaires pour 40 places | Le surplus reste **non affecté**, aucune brigade dépassée, aucune brigade créée | crit. 1, 5, RG-12 | ☐ | |
| R2-SES06-05 | Vérifier que les stagiaires **radiés** ne figurent pas dans la proposition | Absents | A4 | ☐ | |
| R2-SES06-06 | Déplacer manuellement un stagiaire d'une brigade à l'autre dans la proposition | Possible — la proposition est intégralement modifiable | crit. 2 | ☐ | |
| R2-SES06-07 | Valider la proposition | Affectations enregistrées | crit. 1 | ☐ | |
| R2-SES06-08 | Affecter un stagiaire **déjà affecté** dans la session | **Refus**, brigade actuelle nommée, **déplacement proposé** | crit. 4, E2, RG-20 | ☐ | |
| R2-SES06-09 | Affecter un stagiaire **radié** | Refus | — | ☐ | |
| R2-SES06-10 | Affecter un stagiaire portant l'effectif réel au-delà de la **capacité de la salle** | **Refus**, marge restante chiffrée | crit. 3, E1, RG-19 | ☐ | |
| R2-SES06-11 | Affecter un stagiaire portant l'effectif réel **exactement** à la capacité | **Accepté** | RG-19 | ☐ | |
| R2-SES06-12 | Affecter un stagiaire au-delà de l'**effectif déclaré** de la brigade, salle assez grande | **Accepté avec avertissement** — déclaratif, pas physique | crit. 3, RG-65 | ☐ | |
| R2-SES06-13 | Affecter un stagiaire à une brigade **sans salle attitrée** | Accepté avec avertissement | — | ☐ | |
| R2-SES06-14 | Valider alors que des stagiaires restent non affectés | Possible, avertissement, **stagiaires énumérés** | crit. 5, E3 | ☐ | |
| R2-SES06-15 | Consulter la liste des stagiaires non affectés | Présentée séparément | crit. 5 | ☐ | |
| R2-SES06-16 | Déplacer un stagiaire d'`EXP1` vers `EXP2` en cours de session | Ancienne affectation **fermée** à la date d'effet, nouvelle **ouverte** — jamais deux ouvertes | A2, RG-20 | ☐ | |
| R2-SES06-17 | Vérifier l'avertissement au moment du déplacement | Mention des évaluations et de la progression rattachées au parcours | A2 | ☐ | |
| R2-SES06-18 | Consulter l'historique des affectations du stagiaire déplacé | Deux lignes, dates cohérentes, une seule ouverte | RG-20 | ☐ | |
| R2-SES06-19 | Vérifier l'effectif réel d'`EXP1` et d'`EXP2` après le déplacement | L'un décroît, l'autre croît | crit. 3 | ☐ | |
| R2-SES06-20 | Radier un stagiaire affecté, vérifier l'effectif réel de sa brigade | Décroît d'une unité | CLS-00 | ☐ | |
| R2-SES06-21 | Vérifier l'effectif réel sur l'écran des brigades **et** sur la fiche de composition | Présent aux **deux** endroits | emplacements réservés | ☐ | |
| R2-SES06-22 | Affecter un stagiaire après la date de début de la session | Accepté, avec signalement d'affectation tardive | A3 | ☐ | |

### 5.7 US-SES-07 · Consulter la liste des stagiaires

| Code | Contrôle | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|
| R2-SES07-01 | Consulter la liste au niveau de la **session** | Tous les stagiaires, affectés ou non | crit. 1 | ☐ | |
| R2-SES07-02 | Filtrer par **brigade** | Seuls ses stagiaires | crit. 1 | ☐ | |
| R2-SES07-03 | Filtrer sur « non affectés » | Seuls ceux sans affectation ouverte | crit. 1 | ☐ | |
| R2-SES07-04 | Consulter un stagiaire déplacé (R2-SES06-16) | Il apparaît sous sa brigade **courante**, jamais l'ancienne | crit. 1 | ☐ | |
| R2-SES07-05 | Rechercher par nom, prénom, puis matricule | Les trois opérants | crit. 2 | ☐ | |
| R2-SES07-06 | Rechercher un nom accentué **sans** les accents | Trouvé | crit. 2 | ☐ | |
| R2-SES07-07 | Vérifier le tri par nom avec des noms commençant par É, E, A | Ordre alphabétique correct | tri accentué | ☐ | |
| R2-SES07-08 | Exporter en CSV | Fichier produit, colonnes conformes | crit. 3 | ☐ | |
| R2-SES07-09 | Ouvrir le CSV exporté dans un tableur | Accents **corrects** | robustesse | ☐ | |
| R2-SES07-10 | Exporter en XLSX | Fichier produit, lisible | crit. 3 | ☐ | |
| R2-SES07-11 | Exporter avec un filtre de brigade actif | L'export respecte le filtre | crit. 3 | ☐ | |
| R2-SES07-12 | Exporter avec le filtre « actifs » puis « tous » | Comptes **différents** | crit. 3 | ☐ | |
| R2-SES07-13 | Examiner le **nom** du fichier exporté | Porte session, filtre et date ; ni espace, ni accent | contexte | ☐ | |
| R2-SES07-14 | Vérifier le rappel du filtre à l'écran | En toutes lettres, au-dessus du tableau | contexte | ☐ | |
| R2-SES07-15 | **Aller-retour** : redéposer le fichier exporté à l'import d'une autre session | Toutes les lignes acceptées sans retouche | réimportabilité | ☐ | |
| R2-SES07-16 | Consulter le journal après un export | Entrée portant session, filtre, **nombre** de lignes — **aucune identité** | données nominatives | ☐ | |
| R2-SES07-17 | Avec `u_exa` : atteindre la liste, la filtrer par brigade, l'exporter | Les trois possibles | crit. 4 | ☐ | |
| R2-SES07-18 | Imprimer la liste (aperçu) | Filtre rappelé sur le papier, pas de débordement | K3 | ☐ | |

---

## 6. Paquetage Ressources — indisponibilités

### 6.1 US-INS-03 · Enregistrer les indisponibilités transmises

Profil : **`u_plan`**.

| Code | Contrôle | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|
| R2-INS03-01 | Avec `u_plan`, enregistrer une indisponibilité pour `I1`, du 10/11 08:00 au 12/11 18:00, motif mission | Enregistrée | crit. 2 | ☐ | |
| R2-INS03-02 | Consulter l'auteur de la saisie | L'**agent connecté**, jamais l'instructeur | crit. 3, RG-23 | ☐ | |
| R2-INS03-03 | Chercher un écran de déclaration en libre-service pour un instructeur | **Aucun** | crit. 1 | ☐ | |
| R2-INS03-04 | Avec `u_ped`, enregistrer une indisponibilité | **Refusé** | matrice | ☐ | |
| R2-INS03-05 | Avec `u_plan`, modifier un instructeur ou une qualification | **Refusé** | matrice | ☐ | |
| R2-INS03-06 | Avec `u_exa`, consulter la liste des indisponibilités et la filtrer par instructeur | **Accordé** | matrice | ☐ | |
| R2-INS03-07 | Avec `u_exa`, ouvrir la fiche d'un instructeur | **Refusé** | matrice | ☐ | |
| R2-INS03-08 | Enregistrer une indisponibilité dont la fin précède le début | Refus | E1 | ☐ | |
| R2-INS03-09 | Enregistrer une indisponibilité d'une **demi-journée** (14:00–18:00) | Acceptée — granularité horaire | RG-28 | ☐ | |
| R2-INS03-10 | Enregistrer deux indisponibilités le même jour, matin puis après-midi, heures disjointes | **Les deux acceptées** | RG-28 | ☐ | |
| R2-INS03-11 | Enregistrer pour `I1` une période du 11/11 au 14/11 (chevauche R2-INS03-01) | **Fusion proposée**, bornes résultantes et périodes absorbées présentées, **rien d'écrit avant confirmation** | E2, RG-24 | ☐ | |
| R2-INS03-12 | Confirmer la fusion | Une seule période subsiste, du 10/11 au 14/11 | RG-24 | ☐ | |
| R2-INS03-13 | Consulter le journal après la fusion | Bornes et motif des périodes **absorbées** conservés | traçabilité | ☐ | |
| R2-INS03-14 | Enregistrer une période entièrement contenue dans une existante | Signalée comme **sans effet**, pas enregistrée en double | RG-24 | ☐ | |
| R2-INS03-15 | Fusion de deux périodes de **motifs différents** | Comportement conforme à la décision retenue ; noter lequel | RG-24 | ☐ | |
| R2-INS03-16 | Enregistrer une période sécante pour un **autre** instructeur | Acceptée | RG-24 | ☐ | |
| R2-INS03-17 | Enregistrer une indisponibilité **entièrement passée** | **Acceptée**, sans avertissement ni refus | A4 | ☐ | |
| R2-INS03-18 | Consulter les indisponibilités passées | Conservées et consultables, distinguées des futures | crit. 6 | ☐ | |
| R2-INS03-19 | Enregistrer une indisponibilité pour `I4` (archivé) | Refus | — | ☐ | |
| R2-INS03-20 | Supprimer une indisponibilité | Acceptée, journalisée | A2 | ☐ | |
| R2-INS03-21 | Prolonger une indisponibilité en modifiant sa borne de fin | Acceptée | A3 | ☐ | |

---

## 7. Paquetage Ressources — calendrier et grilles

### 7.1 US-PLAN-12 · Grilles horaires et grille active

Profil : **`u_plan`**.

| Code | Contrôle | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|
| R2-P12-01 | Consulter les grilles livrées en données de départ | **Ordinaire** et **Ramadan** présentes, Ordinaire active | données | ☐ | |
| R2-P12-02 | Vérifier les créneaux de la grille Ordinaire | 08:00–09:45 · 10:10–12:00 · 13:00–14:15 · 14:40–16:00 | données | ☐ | |
| R2-P12-03 | Vérifier les créneaux de la grille Ramadan | 08:30–09:50 · 10:00–11:20 · 11:30–12:50 · 13:10–14:30 | données | ☐ | |
| R2-P12-04 | Vérifier samedi et dimanche sur la grille Ordinaire | **Aucun créneau**, et la grille reste valide et activable | crit. 2, A4 | ☐ | |
| R2-P12-05 | Créer une grille `Essai`, y ajouter deux créneaux le lundi qui **se recouvrent** | Refus, créneau en conflit désigné avec ses heures | crit. 2 | ☐ | |
| R2-P12-06 | Ajouter deux créneaux **contigus** (fin de l'un = début du suivant) | **Acceptés** | bornes | ☐ | |
| R2-P12-07 | Ajouter un créneau dont l'heure de fin précède l'heure de début | Refus | cohérence | ☐ | |
| R2-P12-08 | Ajouter deux créneaux de même rang le même jour | Refus | unicité | ☐ | |
| R2-P12-09 | Ajouter des créneaux de mêmes heures sur **deux jours différents** | Acceptés | portée | ☐ | |
| R2-P12-10 | Créer une grille `Vide` sans aucun créneau, puis tenter de l'activer | **Refus** | crit. 5, E3 | ☐ | |
| R2-P12-11 | Activer la grille Ramadan | Confirmation demandée, **nommant la grille désactivée** | crit. 3, BNF-09 | ☐ | |
| R2-P12-12 | Après activation, vérifier l'état des deux grilles | **Une seule active** | crit. 3, RG-62 | ☐ | |
| R2-P12-13 | Consulter la date et l'agent d'activation | Renseignés | crit. 4, RG-63 | ☐ | |
| R2-P12-14 | Vérifier la date de dernière activation de la grille **désactivée** | **Conservée** | RG-63 | ☐ | |
| R2-P12-15 | Consulter le volume hebdomadaire affiché pour la grille active | Cohérent avec la somme des créneaux (30 h pour l'Ordinaire) | § 7 prompt 29 | ☐ | |
| R2-P12-16 | Grille Ramadan active : ouvrir une session très courte au regard du volume prescrit | L'avertissement de durée s'appuie sur le volume **de la grille Ramadan**, pas sur 30 h | remboursement D-33 | ☐ | |
| R2-P12-17 | Réactiver la grille Ordinaire | Rétablie | — | ☐ | |
| R2-P12-18 | Dupliquer la grille Ordinaire sous un nouvel intitulé | Copie inactive, tous les créneaux dupliqués, originale inchangée | A3 | ☐ | |
| R2-P12-19 | Supprimer une grille **jamais activée** | Acceptée | crit. 5 | ☐ | |
| R2-P12-20 | Supprimer une grille **déjà activée** par le passé | **Refus**, renvoi vers la clôture/l'archivage | crit. 5 | ☐ | |
| R2-P12-21 | Supprimer ou archiver la grille **active** | Refus dans les deux cas | E2 | ☐ | |
| R2-P12-22 | Archiver une grille inactive, puis tenter de l'activer | Archivage accepté, activation **refusée** | crit. 5 | ☐ | |
| R2-P12-23 | Créer une période de calendrier « Ramadan », vérifier la grille active | **Inchangée** — aucune bascule automatique | RG-63 | ☐ | |
| R2-P12-24 | Imprimer la fiche d'une grille (aperçu) | Semaine type lisible, pas de débordement | K3 | ☐ | |

### 7.2 US-PLAN-01 · Calendrier académique annuel

Profil : **`u_plan`**.

| Code | Contrôle | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|
| R2-P01-01 | Consulter les natures d'événement livrées | Cours, conférence, visite, formation extérieure, congé, examen, bivouac | crit. 1 | ☐ | |
| R2-P01-02 | Créer une nature d'événement avec un libellé existant (casse différente) | Refus | unicité | ☐ | |
| R2-P01-03 | Supprimer une nature utilisée par une période | **Refus**, périodes énumérées | PROTECT | ☐ | |
| R2-P01-04 | Créer une période « Congé annuel », du 20/12 au 05/01, **sans cible** | Créée ; portée affichée **« centre entier »** | crit. 1, 2 | ☐ | |
| R2-P01-05 | Créer une conférence de **deux heures** un mardi matin | Créée sans traitement particulier | crit. 2, A1 | ☐ | |
| R2-P01-06 | Créer une seconde période l'après-midi du même mardi, heures disjointes | **Acceptée** — le reste de la journée demeure disponible | crit. 3 | ☐ | |
| R2-P01-07 | Créer une période ciblant **une seule brigade** | Créée ; portée affichée en toutes lettres | A2, RG-30 | ☐ | |
| R2-P01-08 | Créer une période ciblant **deux sessions** | Créée ; portée correcte | CLS-03 | ☐ | |
| R2-P01-09 | Créer une période ciblant à la fois une session et une brigade | Acceptée | CLS-03 | ☐ | |
| R2-P01-10 | Créer un **doublon exact** — mêmes bornes, mêmes cibles | **Refus**, période en conflit désignée | § 5.4 CLS v4 | ☐ | |
| R2-P01-11 | Créer une période de mêmes bornes mais de **cibles différentes** | **Acceptée avec avertissement** | § 5.4 CLS v4 | ☐ | |
| R2-P01-12 | Créer une période de cibles identiques et de bornes **partiellement sécantes** | **Acceptée avec avertissement** | § 5.4 CLS v4 | ☐ | |
| R2-P01-13 | Créer une période ciblant les sessions A et B, sécante d'une période ciblant B et C | **Acceptée avec avertissement** nommant l'intersection | § 5.4 CLS v4 | ☐ | |
| R2-P01-14 | Créer un examen et **surcharger** son effet en informatif | Accepté ; la nature n'est pas modifiée | effet dissocié | ☐ | |
| R2-P01-15 | Créer une période ciblant une session, avec des bornes **hors** des dates de cette session | **Acceptée avec avertissement** | E3 | ☐ | |
| R2-P01-16 | Ouvrir une nouvelle session, puis consulter le calendrier | La session apparaît en bande **sans qu'aucune période n'ait été créée** | RG-30 bis | ☐ | |
| R2-P01-17 | Modifier les dates de cette session | La bande se déplace ; aucune période touchée | RG-30 bis | ☐ | |
| R2-P01-18 | Consulter la vue annuelle | Les douze mois, périodes repérables, effet doublé d'un mot | crit. 6, D-63 | ☐ | |
| R2-P01-19 | Consulter la vue de détail hebdomadaire ou mensuelle | Granularité horaire visible — la conférence de deux heures occupe deux heures | crit. 2 | ☐ | |
| R2-P01-20 | Filtrer le calendrier sur **une session donnée** | Périodes la ciblant **et** périodes de portée centre entier | RG-38 | ☐ | |
| R2-P01-21 | Supprimer une cible d'une période (la session ciblée) | La période ne bascule **jamais** silencieusement en portée centre entier | § 5.4 CLS v4 | ☐ | |
| R2-P01-22 | Imprimer la vue annuelle, en portrait puis en paysage | Noter le format naturel et tout débordement | K3 | ☐ | |

---

## 8. Paquetage Planification — contraintes et génération

Les six contraintes dures d'US-PLAN-04 n'ont pas d'écran propre : elles se
constatent **à travers le compte rendu de génération**, qui doit nommer la règle
violée et l'élément en cause. C'est la seule voie de recette disponible avant la
saisie manuelle du sprint 3, et elle suffit.

### 8.1 Préparation

Constituer, avant les contrôles : deux sessions actives sur la semaine du
**9 au 13 novembre 2026**, `F1` avec `EXP1` et `EXP2`, `F2` avec `CDP1` ;
salles attitrées attribuées ; stagiaires affectés ; grille Ordinaire active ;
aucune période bloquante sauf mention contraire.

### 8.2 US-PLAN-03 et US-PLAN-04 · Génération et contraintes dures

Profil : **`u_plan`**.

| Code | Contrôle | Résultat attendu | Trace | Rés. | Obs. |
|---|---|---|---|---|---|
| R2-GEN-01 | Écran de lancement : choisir la semaine et sélectionner `EXP1` et `EXP2` | Sélection possible ; grille active indiquée | crit. 1 | ☐ | |
| R2-GEN-02 | Sélectionner des brigades de **deux sessions différentes** | Possible | crit. 1 | ☐ | |
| R2-GEN-03 | Lancer la génération sur `EXP1` et `EXP2` | Programme créé à l'état **brouillon** | crit. 7, RG-31 | ☐ | |
| R2-GEN-04 | Lancer ensuite la génération sur `CDP1`, **même semaine** | Le **même** programme est complété ; les séances d'`EXP1` et `EXP2` **intactes** | RG-33 bis | ☐ | |
| R2-GEN-05 | Vérifier qu'il n'existe qu'**un seul** programme pour cette semaine | Un seul | RG-33 bis | ☐ | |
| R2-GEN-06 | Consulter le programme | **Une ligne par brigade** | RG-32 | ☐ | |
| R2-GEN-07 | Vérifier une séance de `M1` (salle attitrée) | La salle **de la brigade** est reprise automatiquement | crit. 5 | ☐ | |
| R2-GEN-08 | Vérifier une séance de `M3` (sans lieu) | Placée **sans** réservation de lieu | crit. 6 | ☐ | |
| R2-GEN-09 | Vérifier une séance de `M2` (lieu partagé) | Un lieu partagé libre est affecté | crit. 4 | ☐ | |
| R2-GEN-10 | Vérifier chaque séance générée | Matière, instructeur et créneau présents | crit. 4 | ☐ | |
| R2-GEN-11 | Consulter le compte rendu | Nombre de séances placées, et non placées avec motif | crit. 8 | ☐ | |
| R2-GEN-12 | Vérifier le volume programmé et restant par matière et par brigade | Présents et exacts | scénario nominal | ☐ | |
| R2-GEN-13 | Épuiser le volume de `M1` pour `EXP1`, relancer | `M1` **écartée**, motif « volume épuisé » | crit. 3, RG-39 | ☐ | |
| R2-GEN-14 | Générer pour `CDP1` (`F2`, `M4` prérequis de `M5`), volume de `M4` non atteint | `M5` **écartée**, motif nommant `M4` | crit. 3, RG-39 | ☐ | |
| R2-GEN-15 | Rendre `I1` seul qualifié pour `M2`, l'occuper au même créneau sur une autre brigade | Case non pourvue, motif nommant l'instructeur et la brigade occupante | RG-34 | ☐ | |
| R2-GEN-16 | Vérifier que la résolution tient compte des **brigades non sélectionnées** | L'instructeur occupé sur une brigade non sélectionnée est vu comme occupé | crit. 2, A1 | ☐ | |
| R2-GEN-17 | Déclarer une indisponibilité sur `I1` couvrant la semaine, relancer | Aucune séance ne lui est affectée ; motif nommant la période | RG-36, crit. 4 US-INS-03 | ☐ | |
| R2-GEN-18 | Occuper `L4` (lieu partagé) sur un créneau par une autre brigade | Pas de seconde séance simultanée ; motif nommant l'occupant | RG-37 | ☐ | |
| R2-GEN-19 | Porter l'effectif d'une brigade au-delà de la capacité de son lieu partagé | Refus ou case non pourvue, écart chiffré | RG-37 | ☐ | |
| R2-GEN-20 | Créer une période **bloquante** de portée centre entier sur le mardi, relancer | **Aucune séance** le mardi | RG-38, crit. 5 US-PLAN-01 | ☐ | |
| R2-GEN-21 | Créer une période bloquante ciblant **`EXP1` seule**, relancer | `EXP1` bloquée, `EXP2` **programmée normalement** | RG-30, RG-38 | ☐ | |
| R2-GEN-22 | Créer une période **informative** sur un créneau, relancer | Les séances sont placées normalement | RG-38 | ☐ | |
| R2-GEN-23 | Bloquer la semaine entière, relancer | Indication claire, **et aucun programme créé** | E1 | ☐ | |
| R2-GEN-24 | Archiver ou désactiver toutes les grilles, relancer | **Refus**, renvoi vers la gestion des grilles | E6 | ☐ | |
| R2-GEN-25 | Créer une situation sans aucun instructeur qualifié disponible pour une matière | Motif nommant la matière, **la liste des instructeurs qualifiés et la cause propre à chacun** | E3 | ☐ | |
| R2-GEN-26 | Créer une situation sans lieu partagé disponible | Proposition d'un autre créneau ou d'un report | E4 | ☐ | |
| R2-GEN-27 | Relancer la génération **deux fois** sur les mêmes données | Programme **identique** — déterminisme | § 4 prompt 31 | ☐ | |
| R2-GEN-28 | Régénérer sur `EXP1` et `EXP2` seules | Leurs séances non verrouillées refaites ; celles de `CDP1` **intactes** | A3 | ☐ | |
| R2-GEN-29 | Verrouiller une séance d'`EXP1`, régénérer | La séance verrouillée est **préservée** et signalée au compte rendu | A3 | ☐ | |
| R2-GEN-30 | Vérifier la confirmation avant régénération | Nomme les brigades et le nombre de séances à supprimer | BNF-09 | ☐ | |
| R2-GEN-31 | Observer deux brigades d'une même session à des avancements différents | Aucun rapprochement de leurs progressions | RG-33 | ☐ | |
| R2-GEN-32 | Vérifier un créneau non pourvu à l'affichage du programme | Mention **AD/GROUPEMENT** | A5 | ☐ | |
| R2-GEN-33 | Vérifier que le programme reste en brouillon | Aucune diffusion, aucun passage d'état, aucune notification | RG-31 | ☐ | |
| R2-GEN-34 | Mesurer le temps d'une génération sur le jeu de recette | Bien en deçà de cinq minutes ; noter la valeur | BNF-04 | ☐ | |
| R2-GEN-35 | Consulter le journal après génération | Semaine, brigades, comptes, auteur — **pas le détail des séances** | § 7 prompt 31 | ☐ | |
| R2-GEN-36 | Imprimer le programme, portrait puis paysage | Noter le format naturel et tout débordement | RG-33 bis, K3 | ☐ | |

---

## 9. Contrôles transverses

### 9.1 Habilitations

Pour chaque ligne : ouvrir l'écran avec le profil, tenter une lecture puis une
écriture.

| Code | Écran | `u_ped` | `u_plan` | `u_exa` | `u_df` | `u_adm` | Rés. |
|---|---|---|---|---|---|---|---|
| R2-HAB-01 | Sessions | écriture | lecture | lecture | lecture | **aucun** | ☐ |
| R2-HAB-02 | Brigades | écriture | lecture | lecture | lecture | **aucun** | ☐ |
| R2-HAB-03 | Stagiaires | écriture | lecture | lecture | lecture | **aucun** | ☐ |
| R2-HAB-04 | Affectation aux brigades | écriture | lecture | lecture | lecture | **aucun** | ☐ |
| R2-HAB-05 | Salles attitrées | lecture | **écriture** | lecture | lecture | **aucun** | ☐ |
| R2-HAB-06 | Indisponibilités d'instructeurs | lecture | **écriture** | lecture | lecture | **aucun** | ☐ |
| R2-HAB-07 | Calendrier et natures d'événement | lecture | **écriture** | lecture | lecture | **aucun** | ☐ |
| R2-HAB-08 | Grilles horaires et activation | lecture | **écriture** | lecture | lecture | **aucun** | ☐ |
| R2-HAB-09 | Génération du programme | lecture | **écriture** | lecture | lecture | **aucun** | ☐ |

| Code | Contrôle complémentaire | Attendu | Rés. |
|---|---|---|---|
| R2-HAB-10 | Avec chaque profil, examiner le menu de navigation | Les rubriques accessibles y figurent ; celles qui ne le sont pas en sont absentes | ☐ |
| R2-HAB-11 | Avec `u_df`, parcourir tous les écrans du sprint 2 | Aucune commande d'écriture nulle part | ☐ |
| R2-HAB-12 | Se déconnecter et appeler directement une adresse d'écriture | Redirection vers l'authentification, aucune action exécutée | ☐ |

### 9.2 Journal

| Code | Contrôle | Attendu | Rés. |
|---|---|---|---|
| R2-JOU-01 | Vérifier qu'une entrée existe pour chaque création, modification et suppression effectuée pendant la recette | Présentes, avec auteur et horodatage | ☐ |
| R2-JOU-02 | Tenter de modifier ou supprimer une entrée de journal, avec chaque profil | **Impossible** pour tous, administrateur compris | ☐ |
| R2-JOU-03 | Rechercher une identité de stagiaire dans le journal | **Absente** des entrées d'import et d'export | ☐ |

### 9.3 Non-régression sur le périmètre du sprint 1

Le sprint 2 pose des contraintes nouvelles sur des objets du sprint 1. Ces
contrôles vérifient qu'elles s'appliquent **et** que rien d'autre n'a bougé.

| Code | Contrôle | Attendu | Trace | Rés. |
|---|---|---|---|---|
| R2-NRG-01 | Supprimer une formation portant une session **ouverte** | **Refus**, sessions énumérées | D-23 | ☐ |
| R2-NRG-02 | Supprimer une formation portant une session **clôturée** ou ancienne | Refus également — noter le comportement | D-23 | ☐ |
| R2-NRG-03 | Supprimer un lieu attitré à une brigade | **Refus**, brigades énumérées | D-54 | ☐ |
| R2-NRG-04 | Supprimer un lieu affecté à une séance générée | **Refus**, séances énumérées | D-54 | ☐ |
| R2-NRG-05 | Supprimer un instructeur affecté à une séance générée | **Refus** | D-45 | ☐ |
| R2-NRG-06 | Retirer une qualification à un instructeur affecté à une séance **future** sur cette matière | Comportement conforme à la décision retenue ; noter lequel | D-51, RG-22 | ☐ |
| R2-NRG-07 | Supprimer une matière utilisée par un référentiel | Refus (comportement du sprint 1 inchangé) | D-30 | ☐ |
| R2-NRG-08 | Créer, modifier et supprimer une formation, une matière, un instructeur, un lieu | Fonctionnement inchangé | sprint 1 | ☐ |
| R2-NRG-09 | Composer un référentiel, déclarer un prérequis | Fonctionnement inchangé | sprint 1 | ☐ |

### 9.4 Impression

| Code | Écran | Format naturel | Débordement mesuré | Rés. |
|---|---|---|---|---|
| R2-IMP-01 | Fiche de composition de session | | | ☐ |
| R2-IMP-02 | Liste des stagiaires | | | ☐ |
| R2-IMP-03 | Fiche de grille horaire | | | ☐ |
| R2-IMP-04 | Vue annuelle du calendrier | | | ☐ |
| R2-IMP-05 | Programme hebdomadaire | | | ☐ |

Rappel du point ouvert du sprint 1 : les écrans Instructeurs (33 px) et Lieux
(74 px) débordaient encore en portrait au 8 septembre. Les mesures ci-dessus
complètent le lot des gabarits imprimables du sprint 4.

---

## 10. Contrôles non réalisables — critères reportés

Ces critères appartiennent au périmètre du sprint 2 mais supposent un modèle
livré ultérieurement. Ils sont **exclus du dépouillement** et deviendront
exécutables aux dates indiquées.

| Story | Critère reporté | Refermé par | Contrôlable à partir de |
|---|---|---|---|
| US-SES-02 | crit. 5 — brigade dont le programme est en cours non supprimable | US-PLAN-03/04 | **Vérifiable ici** : voir R2-NRG-04/05 pour le mécanisme équivalent |
| US-SES-03 | crit. 4 — salle attitrée reprise par défaut à la génération | US-PLAN-03 | **Vérifiable ici** : R2-GEN-07 |
| US-INS-03 | crit. 5 — alerte signalant les séances concernées par une indisponibilité | US-PLAN-09 (sprint 3) | sprint 3 |
| US-PLAN-01 | E2 — période bloquante recouvrant des séances programmées | US-PLAN-05/09 (sprint 3) | sprint 3 |
| US-PLAN-01 | A3 — séances redevenues programmables à la suppression d'une période | US-PLAN-05/09 (sprint 3) | sprint 3 |
| US-PLAN-12 | crit. 6 — changer de grille ne modifie pas les séances passées | constat d'absence | **Vérifiable ici** : R2-P12-25 ci-dessous |

| Code | Contrôle ajouté | Attendu | Rés. |
|---|---|---|---|
| R2-P12-25 | Générer un programme, activer la grille Ramadan, reconsulter le programme | **Aucune séance déplacée**, heures réelles conservées | ☐ |

---

## 11. Dépouillement

### 11.1 Récapitulatif

| Section | Contrôles | C | NC majeur | NC mineur | B | SO |
|---|---|---|---|---|---|---|
| 5.1 US-SES-01 | 17 | | | | | |
| 5.2 US-SES-02 | 15 | | | | | |
| 5.3 US-SES-03 | 15 | | | | | |
| 5.4 US-SES-04 | 13 | | | | | |
| 5.5 US-SES-05 | 27 | | | | | |
| 5.6 US-SES-06 | 22 | | | | | |
| 5.7 US-SES-07 | 18 | | | | | |
| 6.1 US-INS-03 | 21 | | | | | |
| 7.1 US-PLAN-12 | 24 | | | | | |
| 7.2 US-PLAN-01 | 22 | | | | | |
| 8.2 Génération et contraintes | 36 | | | | | |
| 9.1 Habilitations | 12 | | | | | |
| 9.2 Journal | 3 | | | | | |
| 9.3 Non-régression | 9 | | | | | |
| 9.4 Impression | 5 | | | | | |
| 10 Contrôle ajouté | 1 | | | | | |
| **Total** | **260** | | | | | |

### 11.2 Décision de recette

| | |
|---|---|
| Date d'exécution | |
| Recetteur | |
| Taux de conformité | ___ / 260 |
| Écarts majeurs | |
| Écarts mineurs | |

☐ **Recette prononcée** — aucun écart majeur, les écarts mineurs entrent au
reste à faire

☐ **Recette prononcée sous réserve** — écarts majeurs corrigés et recontrôlés
avant le _____________

☐ **Recette refusée** — écarts majeurs bloquants, nouvelle recette après
correction

**Observations :**

---

## 12. Fiche d'anomalie (modèle)

| Champ | Valeur |
|---|---|
| Code du contrôle | R2-___-__ |
| Date de constat | |
| Profil utilisé | |
| Écran | |
| Comportement attendu | |
| Comportement observé | |
| Étapes de reproduction | |
| Sévérité | ☐ majeur ☐ mineur |
| Règle ou critère violé | |
| Code `PROBLEMES.md` | P-__ |
| Correction apportée | |
| Recontrôle | ☐ C ☐ NC — date : |

---

## 13. Ce que cette recette ne couvre pas

À dire explicitement au jury plutôt qu'à laisser découvrir :

- le périmètre du sprint 1, recetté séparément le 4 septembre 2026 ;
- les critères reportés du § 10, non exécutables avant le sprint 3 ;
- la tenue en charge : le jeu de recette compte trois brigades, le centre en
  compte trente à trente-cinq. Les mesures de performance relèvent des mesures
  de référence consolidées, pas de cette recette ;
- l'installation hors ligne, couverte par son propre protocole
  (`INSTALLATION-HORS-LIGNE.md`, validé le 7 septembre 2026) ;
- la sécurité au-delà des habilitations applicatives.
