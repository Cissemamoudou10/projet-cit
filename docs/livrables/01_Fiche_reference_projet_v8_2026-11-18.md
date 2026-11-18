# Fiche de référence du projet — PFE CIT

> **Document de référence permanent.** À conserver dans la base de connaissances du projet et à mettre à jour à chaque fin de phase et à chaque décision structurante. Il donne le contexte courant sans avoir à charger l'ensemble des livrables.
>
> **Version 8 — 18 novembre 2026** · Dernière mise à jour : phase 6 close (RECETTE-05 et jalon C3 prononcés le 18/11), code gelé à `recette-phase-6-c11`, séance avec les cellules non tenue (R29 réalisé), OS5 estimé, backlog v13, registre v11, chapitres 3 (v3) et 4 (v2)

---

## 1. Identité du projet

| | |
|---|---|
| **Objet** | Système web unifié de gestion des activités de formation pour la Direction de la formation du Centre d'instruction des transmissions (CIT), Maroc |
| **Binôme** | Lieutenant Mamoudou Cissé · Lieutenant Modibo Amadagaly Niangaly |
| **Commanditaire et encadrant entreprise** | Colonel Janati Idrissi — canal unique d'accès aux cellules |
| **Encadrant académique** | Point hebdomadaire ; relecture du mémoire. A validé le maintien de l'architecture monolithique le 22 octobre |
| **Source métier principale** | Le chef du bureau pédagogique. Les réponses de terrain doivent lui être attribuées dans le mémoire, non au binôme |
| **Période** | 27 juillet 2026 → 20-25 décembre 2026 |
| **Dépôt du mémoire** | **Entre le 1er et le 4 décembre 2026** (J4) — échéance externe ; on vise le **1er décembre**, la date exacte restant à confirmer |
| **Soutenance** | **Entre le 20 et le 25 décembre 2026** (J5) — date exacte à communiquer |
| **Rapport d'avancement** | **Vendredi 13 novembre 2026** — dépôt ; préparé le jeudi 12 au soir |

**Périmètre fonctionnel :** trois cellules de la Direction de la formation — pédagogique, planification, examens — et la direction elle-même. Référentiel de formation, sessions et brigades, instructeurs et qualifications, génération du programme hebdomadaire, validation croisée, évaluations, traçabilité prescrit/réalisé.

**Contrainte de déploiement :** réseau interne, **aucune dépendance en ligne à l'exécution** (BNF-06). **Déploiement sur une machine virtuelle isolée qui simule le serveur du centre, jamais sur un serveur du CIT** (D-295).

---

## 2. État courant

| Phase | Période | État |
|---|---|---|
| 1 à 4 — Initiation, spécification, planification, conception | 27/07 – 30/08 | Closes |
| 5 — Développement (4 sprints) | 31/08 – 24/10 | **Close** — 52 stories, 224 points, 100 % du périmètre planifié ; J3 atteint le 20/10 |
| 6 — Tests et recette | 26/10 – 18/11 | **Close** — six cahiers prononcés ; jalon C3 le 18/11 (prévu le 02/11) ; code gelé à `recette-phase-6-c11` (2 437 tests, 0 échec) |
| 7 — Déploiement et documentation | 18/11 – 27/11 | **Engagée** — réduite au nécessaire : VM, procédure de déploiement et de sauvegarde rejouée à la lettre (L7), manuel utilisateur, documentation technique en annexe |
| 8 — Mémoire et soutenance | 09/11 – 25/12 | **Engagée** — chapitres 2 et 3 rédigés (v1) ; semaine du 9 au 13/11 consacrée au mémoire |

### 2.1 État de la recette au 8 novembre 2026

| Cahier | Objet | Contrôles | Verdict |
|---|---|---|---|
| RECETTE-00 | Socle | 59 | Prononcée après rejeu |
| RECETTE-00 bis | Planification de base | 32 | Prononcée |
| RECETTE-01 | Circuit de validation et planification | 67 / 67 | Prononcée le 07/11 |
| RECETTE-02 | Évaluations | 55 C + 2 SO | Prononcée le 07/11 |
| RECETTE-03 | Suivi et traçabilité | 42 / 42 | Prononcée le 08/11 |
| RECETTE-04 | Pilotage | 27 / 27 | Prononcée le 08/11 |
| RECETTE-05 | Transverse (habilitations, journal, impressions, ergonomie, volumétrie, OS5) | 60 / 60 | Prononcée le 18/11 après le lot d'ergonomie (prompt 64) et une correction d'impression (prompt 65) |

**Ce que la recette a appris.** Une quarantaine d'anomalies trouvées, toutes corrigées et rejouées (prompts 53 à 63, étiquettes `recette-phase-6` à `recette-phase-6-c9`). **Quatre exigences manquantes**, découvertes par les scénarios de bout en bout et invisibles aux tests unitaires : l'étalement hebdomadaire d'une matière (RG-66), l'achèvement d'une matière dont le reste est inférieur à une séance (RG-39 a modifiée), l'interdiction de deux séances simultanées pour une brigade (RG-67), le type de lieu comme contrainte dure. Trois jeux de données de recette (`socle`, `socle-planif`, `complet`) et un jeu de volumétrie (`volume` : 80 instructeurs, 793 stagiaires).

### 2.2 Points ouverts au 8 novembre 2026

- **Mémoire** : chapitre 2 (v1, 02/11), chapitre 3 Conception (v3, 12/11), chapitre 4 Réalisation (v2, 12/11) rédigés ; restent les chapitres 1 et 5, la mise à jour du chapitre 2, l'introduction, la conclusion, les annexes et les captures d'écran — risque R7, critique. Fichiers dans `C:\Users\cisse\dev\MVP\Projet_CIT\memoire`.
- **Contribution de chaque équipier** : colonnes Porteur et Second de `PORTEURS-RETROSPECTIF.md` toujours vides (R16, critique).
- **Sept valeurs par défaut** à présenter comme hypothèses : seuil d'admission 10/20, absence comptée zéro, ex aequo au même rang, seuil de charge 24 h/semaine, seuil d'écart 10 %, coefficient d'étalement 1,5, dépassement de moins d'une séance.
- **Lot d'ergonomie** : livré le 13/11 (prompt 64), avec le coefficient du plafond transmis en production ; corrections d'impression et rubriques repliables le 17/11 (prompt 65, D-314).
- **Phase 7, à ne pas oublier** : sauvegarde et restauration de la base (volume `donnees_pfe_cit`, `pg_dump` hors du volume) dans la procédure de déploiement ; reprises différées des livrables de conception (section dédiée).
- **Séance avec les cellules du 16/11 non tenue** (R29 réalisé) : limite déclarée au mémoire ; démonstration prévue hors recette, remarques en perspective (R11). **OS5 estimé** par le binôme : 10 min au plus (3 brigades), 40 min au plus (32 brigades), contre au moins une journée déclarée — présenté comme une estimation.
- **Procédure de sauvegarde** non définie (R20).
- **Retours de J2** jamais consignés (R17) : à clore en le déclarant.
- **Diagramme de classes** à mettre en conformité avec le modèle implanté avant le chapitre de conception (R19).

---

## 3. Glossaire métier

Ces définitions sont issues des itérations du modèle sous l'effet des entretiens de terrain et du guide officiel. **Elles ne doivent pas être réinterprétées.**

| Terme | Définition retenue |
|---|---|
| **Type de formation** | Catégorie servant à classer les formations |
| **Formation** | Cursus identifié par son intitulé, sa spécialité et sa durée, rattaché à un type |
| **Matière** | Élément d'un **catalogue indépendant des formations** |
| **Référentiel** | Matières rattachées à une formation, chacune avec un volume prescrit, un coefficient et deux poids propres à cette formation. Le référentiel appartient à la formation, **jamais à la brigade** (RG-05) |
| **Session** | Instance datée d'une formation |
| **Brigade** | **Outil de séparation d'effectifs, non spécialité pédagogique.** Toutes les brigades d'une session suivent le même référentiel. Constitution manuelle |
| **Progression décalée** | Décalage volontaire des progressions entre brigades : **contrainte métier à préserver** |
| **Salle attitrée** | Salle fixe d'une brigade pour toute la session |
| **Lieu partagé** | Amphithéâtre, laboratoire, salle spécialisée — arbitré séance par séance. **Mode simultané** (plusieurs brigades ensemble, dans la limite de la capacité) ou **séquentiel** (une brigade à la fois). Une matière exige un **type** de lieu partagé : c'est une contrainte dure |
| **Sans lieu** | Place d'armes, sport, plein air |
| **Séance / ligne de programme** | La séance est l'événement d'enseignement ; la ligne la rattache à une brigade. Une séance porte une à plusieurs lignes |
| **Séance regroupée** | Plusieurs brigades sur une séance, en lieu simultané. Charge de l'instructeur comptée **une fois**, volume compté **pour chaque brigade** |
| **Grille horaire / créneau type** | Squelette de la semaine ; une seule grille active. Depuis D-310, **la saisie manuelle choisit aussi un créneau de la grille** |
| **Résolution centre-entier** | La génération tient compte de toutes les sessions actives de la semaine |
| **Plafond hebdomadaire** | Volume maximal d'une matière placé par semaine et par brigade par la génération automatique : reste à faire ÷ semaines restantes × coefficient (1,5), recalculé chaque semaine (RG-66) |
| **Déclaration par exception** | Une séance d'un programme affiché est réputée exécutée ; seule la non-exécution se déclare |
| **Avenant** | Trace datée, motivée et typée d'une modification après affichage. Visible sur la séance et dans la liste du programme |
| **Évaluation formative** | Le contrôle : un sujet, périmètre brigade, séance insérée au programme |
| **Évaluation certificative** | L'examen final : date du 3ᵉ bureau, deux sujets dont un retenu par la commission d'examen, périmètre session |
| **Programmé échu** | Volume des séances déjà terminées des programmes affichés, à l'instant du calcul : référence du retard en cours de session |
| **Progression réalisée** | Document hebdomadaire de ce qui a été dispensé, intégralement calculé |

**Deux types d'évaluation, jamais trois.** L'« examen partiel » est le contrôle sous un autre nom. *(La version 5 de cette fiche présentait encore « trois circuits d'évaluation » : correction.)*

**Chaîne du modèle :** `Type de formation → Formation → Session → Brigade → Stagiaire`

---

## 4. Décisions structurantes

Les décisions des versions 1 à 5 restent valides : démarche UML sans MCD Merise ; couche de services systématique ; constitution manuelle des brigades ; contrôleur des contraintes avant la génération ; porte d'écriture unique des séances ; aucun attribut dérivé stocké ; sens unique des dépendances entre applications ; programme hebdomadaire du centre entier ; ajustement après affichage par avenant ; deux types d'évaluation ; classement au niveau de la session ; WeasyPrint ; habilitations configurables ; PlantUML. **Décisions ajoutées depuis la version 5 :**

| Décision | Motif |
|---|---|
| **Machine à états ETA-01** : cinq états, transitions T1 à T10 ; réponses par défaut font référence (D-268) | Le circuit n'attend plus la réponse des cellules ; toute divergence ultérieure est une évolution |
| **Solveur CP-SAT maintenu en perspective** (D-289, réexamen du 20/10) | Condition de marge non remplie ; présenté au mémoire comme décision mesurée |
| **Monolithe Django maintenu** contre la demande de séparation front-end / back-end | Validé par l'encadrant le 22/10 : déploiement hors ligne, surface d'exposition des notes et sujets, calendrier. La couche de services est le point d'appui d'une future interface de programmation |
| **Déploiement sur machine virtuelle isolée** (D-295) | Aucun accès à un serveur du CIT ; la VM simule l'environnement cible |
| **Recette en six cahiers et quatre jeux de données** | Cahiers écrits depuis les spécifications, joués par l'interface ; jeux chargés par les services, dates relatives à la semaine courante |
| **Le volume se compte par matière et par brigade**, séances verrouillées comprises (D-302) | Deux brigades d'une session se volaient leur budget |
| **Plafond hebdomadaire RG-66** (D-303), génération seulement | Exigence manquante : une matière s'épuisait en trois semaines sur douze |
| **Dépassement de moins d'une séance** (RG-39 a modifiée, D-304), décision du chef de projet | Sinon une matière ne s'achève jamais et bloque ses dépendantes |
| **RG-67 : une brigade, une séance à la fois** (D-305) ; **RG-05 dans le contrôleur** (D-309) ; **type de lieu, contrainte dure** (prompt 62) | Une règle, une seule fonction, appliquée par le serveur sur tous les chemins |
| **Saisie manuelle par créneau de la grille** (D-310, RG-64 amendée) | Une séance hors grille devenait invisible |
| **Dépassement d'une matière signalé même en cours de session** (D-311) | Un réalisé supérieur au prescrit est un fait certain |
| **Gel des évolutions après le lot d'ergonomie du 12 novembre** | Marge calendaire consommée (R32) |

---

## 5. Choix techniques

| Couche | Technologie |
|---|---|
| Backend | Python, Django 5 — trois couches, services systématiques, sept applications |
| Frontend | Gabarits Django, Tailwind CSS précompilé ; filtrage de listes côté client sans aller-retour |
| Base de données | PostgreSQL 16 (btree_gist) — intégrité portée en base |
| Génération | **Heuristique gloutonne constructive**, contrôleur unique des contraintes dures, plafond hebdomadaire. OR-Tools CP-SAT étudié, non intégré |
| Tests | pytest — **environ 2 400 tests**, dont tests d'architecture ; tests d'impression en navigateur réel (Playwright, dépendance de test seulement, D-301) |
| Documents | WeasyPrint (conteneur sous Windows) |
| Déploiement | Pile conteneurisée, paquet hors ligne ; cible : machine virtuelle isolée |
| Outillage | Git ; assistant de code piloté par prompts, règles de projet et relecteur de conception — à présenter avec transparence au mémoire |

**Budget d'acquisition : nul.**

---

## 6. Chiffres clés

| | |
|---|---|
| Périmètre | 61 besoins fonctionnels, 17 non fonctionnels · **65 stories, 276 points** (backlog v13) · **56 stories et 237 points livrés** ; réserve de 9 stories et 39 points non développée |
| Développement | 52 stories, 224 points livrés en quatre sprints, **100 % à chaque sprint** (58, 61, 50, 55) |
| Règles de gestion | 65 en phase 4, **67 et plus** après la recette (RG-66, RG-67, RG-39 a modifiée, RG-64 amendée) |
| Recette | Six cahiers, environ 280 contrôles ; une quarantaine d'anomalies corrigées ; décisions D-298 à D-311, problèmes P-53 à P-80 |
| Performance mesurée | Génération d'une semaine sur le jeu de volumétrie : 7,8 s ; affichage d'un programme : moins de 0,5 s |
| Clé de conversion | 1,3 h par point — **jamais vérifiée** ; l'estimation en points est la seule mesure validée |
| Marge | **Consommée** : C3 du 02/11 au 18/11 (R32) ; date de dépôt inchangée |
| Risques | **32** au registre v11, dont 21 actifs ; 2 critiques (**R7** mémoire, **R16** contribution de chacun) ; 4 élevés (R19, R20, R13, R32) ; R29 réalisé |

**Objectifs SMART :** OS1 centraliser le référentiel · OS2 assister la génération du programme · OS3 gérer les évaluations · OS4 tracer le prescrit et le réalisé · OS5 réduire le temps de construction du programme (cible ≥ 50 %, mesure en RECETTE-05) · OS6 suggérer un remplaçant. **Bilan au 18/11** : objectif principal et OS1 à OS4 atteints ; OS5 atteint **sur estimation** (non chronométré, séance non tenue) ; OS6 sans objet (US-PLAN-10 en réserve).

---

## 7. Jalons

| Code | Jalon | Prévu | État |
|---|---|---|---|
| J1 | Revue de conception | 29/08 | Franchi le 30/08 |
| C1 | Fin du sprint 1 | 12/09 | Prononcé le 12/09 |
| C2 | Fin du sprint 2 | 26/09 | Prononcé le 30/09 |
| J2 | Démonstration de mi-parcours | 10/10 | Tenu le 10/10 |
| J3 | Fin de développement | 24/10 | **Atteint le 20/10**, quatre jours d'avance |
| C3 | Recette validée | 02/11 | **Prononcé le 18/11** |
| C4 | Système déployé sur la VM, bilan de clôture | 10/11 | **Replanifié au 20/11** |
| J4 | Dépôt du mémoire | **01/12 → 04/12** | Échéance externe ; cible 01/12 |
| J5 | Soutenance | **20/12 → 25/12** | Échéance externe, date exacte à communiquer |

---

## 8. Artefacts et où les trouver

### Dans la base de connaissances
Note de cadrage · Objectifs SMART · Parties prenantes · Cahier des charges v8 · **Backlog produit v13** · **Registre des risques v11** · Étude de faisabilité · WBS, Gantt, allocation et KPIs, plan de communication · les sept livrables de la phase 4 · **les cahiers de recette prononcés et le plan de tests** · la passation du mémoire · la présente fiche.

> **Ce qui ne va jamais dans la base de connaissances** : le classeur de pilotage et les fichiers de suivi du dépôt (`AVANCEMENT.md`, `DECISIONS.md`, `PROBLEMES.md`, `ECARTS-*.md`). Ils se lisent directement dans le dépôt, désormais accessible à la discussion.

**Remplacements à opérer au 8 novembre 2026**

| Sort | Entre |
|---|---|
| `claude/04_Backlog_produit_v12_2026-11-08.md` | `claude/04_Backlog_produit_v13_2026-11-18.md` |
| `claude/09_Registre_risques_v8_2026-10-23.md` | `claude/09_Registre_risques_v9_2026-11-08.md` |
| `01_Fiche_reference_projet_v5_2026-09-30.md` | `claude/01_Fiche_reference_projet_v6_2026-11-08.md` |

**Reprises différées, à traiter avant le mémoire** : diagramme de classes (modèle réellement implanté, écarts des sprints 2 à 4 et de la phase 6) ; cas d'utilisation (RG-66, RG-67, RG-64 amendée, RG-39 a) ; dossier d'architecture (compte des contraintes). Sources : `docs/suivi/ECARTS-LIVRABLES-*.md`.

---

## 9. Règles de travail

- Anticipation des sollicitations externes : 3 semaines pour les cellules (via le colonel), 1 semaine pour le commanditaire, 2 jours ouvrés pour l'encadrant.
- Toute décision structurante est datée, écrite et rattachée au document qu'elle modifie.
- MoSCoW comme variable d'ajustement : on retire des Could puis des Should, jamais de la qualité ni du temps de rédaction.
- **Diagnostiquer avant de corriger** ; une règle, une seule fonction ; aucune modification des permissions de l'assistant de code par lui-même.
- Le terrain fait foi ; à défaut, la valeur retenue est présentée comme hypothèse.

---

## 10. Suivi des mises à jour

| Version | Date | Modification |
|---|---|---|
| 1 | 18/08/2026 | Création à la clôture de la phase 3 |
| 2 | 20/08/2026 | Point ouvert sur le format réglementaire des documents |
| 3 | 23/08/2026 | Réponses de terrain du 23 août ; huit termes, cinq décisions |
| 4 | 30/08/2026 | Clôture de la phase 4 |
| 5 | 30/09/2026 | Clôture du sprint 2, jalon C2 |
| 6 | 08/11/2026 | Développement clos (J3) ; recette de la phase 6, cinq cahiers prononcés ; déploiement sur VM (D-295) ; backlog v12 (65 stories, 276 points) ; registre v9 (32 risques) ; douze décisions ajoutées ; glossaire corrigé (deux types d'évaluation, modes de partage, plafond hebdomadaire) ; dépôt du mémoire au 4 décembre |
| 7 | 09/11/2026 | Échéances précisées (dépôt 1er-4/12, soutenance 20-25/12, rapport d'avancement 13/11) ; séance avec les cellules le 16/11 (R29 non réalisé) ; registre v10 ; chapitre 3 rédigé ; dossier memoire créé sur le poste |
| **8** | **18/11/2026** | **Phase 6 close : RECETTE-05 (60/60) et C3 prononcés, code gelé ; lot d'ergonomie livré ; R29 réalisé ; OS5 estimé ; backlog v13 ; registre v11** |
