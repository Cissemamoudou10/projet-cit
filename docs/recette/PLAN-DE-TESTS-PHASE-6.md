# Plan de tests — Phase 6

**Projet.** Création des activités du CIT (Activités pédagogiques, programmation des cours et séances d'instruction) — Centre d'instruction des transmissions.

**Livrable.** 6.1 du WBS — Plan de tests : tests d'intégration, tests fonctionnels fondés sur les critères d'acceptation, tests de non-régression.

**Version.** 1 du 26 octobre 2026. **Période couverte.** Du 26 octobre au jalon C3, le **2 novembre 2026**.

**Référence.** Backlog produit v11 (23/10), cahier des charges v8, cas d'utilisation v4, registre des risques v8, étiquette git `j3-fin-developpement`.

---

## 1. Pourquoi un plan de tests distinct des cahiers

Le plan dit **comment** la recette est conduite : le découpage, les données, l'ordre, les critères de décision. Les cahiers disent **quoi** vérifier, contrôle par contrôle. Si on mélange les deux, chaque cahier redéfinit ses propres règles, et la recette de la cellule examens finit par ne pas obéir aux mêmes conventions que celle de la planification. Le plan est écrit une fois et chaque cahier y renvoie.

Deux principes méthodologiques tiennent tout l'ensemble :

1. **Les cahiers sont construits à partir des spécifications, jamais à partir du code.** Un cahier rédigé depuis l'implantation vérifie ce qui a été fait, pas ce qui était demandé, et il ne trouve donc jamais un besoin oublié. C'était déjà la règle du cahier du sprint 2. Elle est reprise ici.
2. **La recette s'exécute par l'interface**, dans un navigateur, avec le profil indiqué. Jamais par la console d'administration, jamais par un appel de service. C'est la leçon du sprint 1 : cinq des sept écarts majeurs venaient de contrôles qui ne traversaient pas le cycle web réel.

## 2. Ce que la phase 6 vérifie, à trois niveaux

| Niveau | Question | Où on y répond |
|---|---|---|
| **Tests unitaires et d'intégration** | Le code fait-il ce que ses tests disent ? | Suite automatisée : 2 261 tests, cinq exécutions sans échec au J3. Elle est **rejouée une fois** en ouverture de phase 6 sur l'étiquette de recette, sans rien écrire de nouveau (§ 8.1). |
| **Tests fonctionnels** | Chaque critère d'acceptation du backlog v11 est-il tenu, vu par l'utilisateur ? | Les six cahiers de recette (§ 3) |
| **Objectifs SMART** | Le système atteint-il ce que la phase 1 avait promis ? | La synthèse finale (§ 9), qui s'appuie sur les cahiers, la mesure OS5 et les mesures du jeu volumineux |

Les tests automatisés ne remplacent pas la recette, et l'inverse non plus. Le registre v8 (R22) en donne la preuve : le programme hebdomadaire imprimé déborde de la page A4, et aucun des 2 261 tests ne pouvait le voir.

## 3. Découpage : six cahiers indépendants

| Cahier | Périmètre | Stories | Jeu de départ | Volume visé |
|---|---|---|---|---|
| **RECETTE-00 — Socle** | Non-régression des sprints 1 et 2 : petite recette de base | 27 stories, en échantillon | `socle` | 75 contrôles |
| **RECETTE-01 — Circuit et ajustements** | Validation croisée et modifications du programme | US-VAL-01 à 04, US-PLAN-05, 06, 09 | `complet` | ≈ 55 |
| **RECETTE-02 — Évaluations** | Du choix du type au procès-verbal | US-EVAL-01 à 07 | `complet` | ≈ 60 |
| **RECETTE-03 — Suivi et clôture** | Prescrit, programmé et réalisé ; clôture d'une session | US-SUI-01, 02, 03, 05, 06, US-SES-09 | `complet` | ≈ 45 |
| **RECETTE-04 — Pilotage de la planification** | Écarts, duplication, historiques, charge | US-PLAN-07, 11, US-VAL-05, US-INS-04, US-REF-09 | `complet` | ≈ 35 |
| **RECETTE-05 — Transverse et bout en bout** | Habilitations croisées, journal, documents imprimés, scénario de bout en bout, mesure OS5 | Toutes, sous l'angle transverse | `complet` puis `volume` | ≈ 40 |

**Pourquoi six cahiers et pas un seul ?**
- Chacun **se joue seul**, sur une base remise à zéro en une commande. Un contrôle qui échoue dans RECETTE-02 ne bloque pas RECETTE-03.
- Chacun **se répartit** entre les deux équipiers selon le paquetage qu'il a conduit (§ 7). C'est la mesure que demande le registre v8 pour R16.
- Chacun **se prononce séparément** : un cahier peut être conforme alors qu'un autre attend une correction.

**Ce qui les rend cohérents entre eux :**
- un **plan unique** (ce document) et une **convention de codes unique** (§ 5) ;
- un **jeu de recette unique**, chargé à deux niveaux (§ 4). Les mêmes objets — `u_ped`, `F6`, `EXP1`, `S1`, `I8` — portent les mêmes noms dans tous les cahiers ;
- une **fiche d'anomalie unique**, et un seul registre des anomalies, `PROBLEMES.md`, avec un code par anomalie ;
- **RECETTE-00 vient en premier.** Un défaut du socle (habilitations, référentiel, génération) fausserait toutes les recettes suivantes : il faut le trouver avant.

## 4. Jeux de données

Trois jeux distincts, chacun sur **sa propre base**. Ils ne coexistent jamais : le chargeur refuse de s'exécuter sur une base qui contient des comptes qu'il n'a pas créés lui-même. C'est le garde-fou déjà en place depuis le sprint 2.

| Jeu | Base | Contenu | Sert à |
|---|---|---|---|
| **Recette — état `socle`** | `pfe_cit_recette` | Le jeu actuel (`JEU-RECETTE.md`) : cinq comptes, TF1-TF2, F1 à F4, M1 à M5, I1 à I5, lieux, grilles horaires | RECETTE-00 |
| **Recette — état `complet`** | `pfe_cit_recette` | Le socle, plus une formation riche (F6), trois sessions, des brigades, des stagiaires, quatre semaines de programmes dans des états variés, des évaluations, des non-exécutions et des avenants. Tout est daté **par rapport au jour du chargement** | RECETTE-01 à 05 |
| **Volumineux** | `pfe_cit_volume` | Le CIT à sa taille réelle : 30 à 35 brigades, plusieurs centaines de stagiaires, des semaines de programmes. **Indépendant des recettes** | Voir l'étendue de l'application, mesurer les performances (BNF-04, BNF-05, BNF-15), préparer la démonstration de soutenance |

Le contenu exact de l'état `complet` et du jeu volumineux est livré par le prompt 51, dans `docs/recette/JEUX-DE-DONNEES-PHASE-6.md`. **Les cahiers RECETTE-01 à 05 sont rédigés après ce document, à partir de ce qui a réellement été chargé**, et non de ce qui était prévu. Sinon, un contrôle viserait un objet qui n'existe pas.

**Remise à zéro.** Un script unique recrée la base vierge, applique les migrations, initialise les habilitations, les gabarits et les grilles, puis charge l'état demandé :

```powershell
.\outils\recette\reinitialiser_base_recette.ps1 -Etat socle     # avant RECETTE-00
.\outils\recette\reinitialiser_base_recette.ps1 -Etat complet   # avant chacun des cahiers 01 à 05
```

**Toutes les données sont fictives**, et les noms de personnes sont manifestement inventés (registre v8, R28).

## 5. Conventions

### Codes des contrôles

`R0n-DOMAINE-nn`. Exemples : `R00-ADM-03`, `R02-EVAL05-12`, `R05-IMP-04`. Le code « R2-… » reste réservé au cahier de recette du sprint 2, qui est conservé comme référence (§ 10).

### Notation

| Code | Signification |
|---|---|
| **C** | Conforme |
| **NC** | Non conforme : écart constaté, fiche d'anomalie obligatoire |
| **B** | Bloqué : le contrôle n'a pas pu être exécuté parce qu'une dépendance a échoué |
| **SO** | Sans objet dans cette version (limite assumée et consignée) |

### Sévérité

| Niveau | Définition | Effet |
|---|---|---|
| **Majeur** | Une règle de gestion est violée, une donnée est perdue ou corrompue, une habilitation est contournée, ou un critère d'acceptation Must n'est pas tenu | Bloque le prononcé du cahier |
| **Mineur** | Libellé, ergonomie, message imprécis, mise en page sans effet sur la donnée ni sur la règle | N'empêche pas le prononcé ; entre au reste à faire |

### Traçabilité

Chaque contrôle cite sa source : un critère du backlog v11 (`US-xxx c.n`, numéroté dans l'ordre d'apparition), une règle de gestion (`RG-nn`), un enchaînement de fiche (`CU-Pn-xx A2`, `E1`) ou un besoin non fonctionnel (`BNF-nn`). Un contrôle sans source est un contrôle inventé : il n'y en a aucun.

Chaque cahier se termine par sa **matrice critère → contrôle**. Elle complète `TRACABILITE.md` (critère → test automatisé) : ensemble, les deux donnent la chaîne complète exigée par les instructions du projet, **besoin → story → critère → test automatisé → contrôle de recette**.

### Anomalies

Tout NC donne une fiche (modèle en annexe de chaque cahier), reportée dans `docs/suivi/PROBLEMES.md` avec le code du contrôle. Un correctif passe par un prompt Claude Code, comme en développement. Le contrôle est ensuite **rejoué**, et le résultat du rejeu est inscrit à côté du premier, jamais à sa place.

## 6. Environnement

| Élément | Valeur |
|---|---|
| Version | Étiquette `recette-phase-6`, posée par le prompt 51 sur le commit qui suit les chargeurs. Le développement des correctifs continue sur `master` et chaque correctif est rejoué sur une nouvelle étiquette `recette-phase-6-cN` |
| Lancement | `python app\manage.py runserver --settings=config.settings.recette` (jeu volumineux : `config.settings.volume`) |
| Base | PostgreSQL 16 en conteneur, `btree_gist` présente |
| PDF | Les documents PDF se vérifient sur l'**image de production en conteneur**, WeasyPrint ne s'exécutant pas sous Windows (P-44) |
| Navigateur | À noter dans chaque cahier |
| Date système | Notée en tête de chaque cahier : l'état `complet` est daté par rapport au jour de son chargement |

## 7. Répartition entre les équipiers

Chaque cahier est joué par l'équipier qui a **conduit** le paquetage, puis relu par l'autre. C'est la mesure de R16 au registre v8 : la recette montre la maîtrise de chacun, et la relecture croisée prépare les questions du jury sur le paquetage de l'autre.

La répartition se lit dans `docs/suivi/PORTEURS-RETROSPECTIF.md`, une fois les colonnes Porteur et Second remplies. **Il faut la remplir avant d'exécuter RECETTE-01** : sinon, la répartition de la recette serait elle aussi arbitraire.

| Cahier | Recetteur | Relecteur |
|---|---|---|
| RECETTE-00 | *à remplir* | *à remplir* |
| RECETTE-01 | *à remplir* | *à remplir* |
| RECETTE-02 | *à remplir* | *à remplir* |
| RECETTE-03 | *à remplir* | *à remplir* |
| RECETTE-04 | *à remplir* | *à remplir* |
| RECETTE-05 | **les deux** | — |

## 8. Ordre et calendrier

| Date | Activité |
|---|---|
| Lun 26/10 | Plan de tests, RECETTE-00, prompt 51 (jeux de données) |
| Mar 27/10 | Exécution de RECETTE-00 ; suite automatisée rejouée sur l'étiquette ; rédaction de RECETTE-01 à 05 sur le jeu réellement chargé |
| Mer 28/10 | Exécution de RECETTE-01 et 02 ; premiers correctifs |
| Jeu 29/10 | **Séance avec les cellules, si le Colonel l'accorde** : circuit de validation (RECETTE-01) et mesure OS5 avec la cellule planification. Sinon, exécution de RECETTE-03 |
| Ven 30/10 | Exécution de RECETTE-03 et 04 ; correctifs |
| Sam 31/10 | Exécution de RECETTE-05 (transverse, bout en bout, jeu volumineux) ; rejeu des NC corrigés |
| Lun 02/11 | Dépouillement, synthèse des objectifs SMART, **prononcé de C3** |

Il n'y a aucun battement dans ce calendrier. **S'il faut couper, on coupe dans l'ordre suivant** : les contrôles des stories Should de RECETTE-04, puis le bout en bout de RECETTE-05, jamais un contrôle Must. C'est la règle MoSCoW du projet, appliquée à la recette.

### 8.1 Suite automatisée

Elle est rejouée une seule fois en ouverture, sur l'étiquette `recette-phase-6`, seule sur la machine (leçon P-51 : aucune autre commande ne doit toucher PostgreSQL en même temps). On y ajoute `pytest -m pdf` dans le conteneur. Le résultat est consigné dans `MESURES-REFERENCE.md`. On n'écrit aucun test nouveau pendant la recette, **sauf** un test de reproduction attaché à chaque anomalie majeure corrigée.

## 9. Critères de décision

### Prononcé d'un cahier

Un cahier est **prononcé** quand aucun NC majeur ne reste ouvert. Il est **prononcé sous réserve** si un NC majeur est corrigé mais pas encore rejoué. Il est **refusé** dans les autres cas.

### Prononcé de C3 — 2 novembre

Les critères sont repris du WBS et du classeur :

1. Tous les critères d'acceptation des stories **Must** sont passés : C, ou SO justifié.
2. Aucune anomalie bloquante ouverte (KPI K10 = 0).
3. La **mesure OS5** est réalisée, avec la cellule planification ou, à défaut, avec la limite déclarée (§ 9.2).
4. Les six cahiers sont prononcés, au moins sous réserve.

### 9.1 Vérification des objectifs SMART

| Objectif | Mesure prévue en phase 1 | Où elle se lit |
|---|---|---|
| Principal | Les trois cellules sont couvertes ; les besoins Must sont satisfaits | Les six cahiers ; 194 points Must livrés |
| OS1 — Référentiel centralisé | Formations et matières consultables, sans double saisie | RECETTE-00 ; RECETTE-05 (lecture croisée par les quatre profils) |
| OS2 — Génération assistée | Un programme complet généré sans violation de contrainte dure, puis validé avant affichage | RECETTE-00 (génération) ; RECETTE-01 (circuit) ; jeu volumineux (32 brigades) |
| OS3 — Évaluations | Notes et résultats produits pour une formation test ; accès restreint. *OS3 annonçait trois circuits : le terrain en a établi deux le 25 août, et l'écart se déclare tel quel* | RECETTE-02 |
| OS4 — Prescrit et réalisé | L'écart est calculé et affiché pour chaque matière, avec une alerte | RECETTE-03 |
| OS5 — Gain de temps | Une même semaine test construite par le système et par la méthode actuelle. Point de départ déclaré : « au moins une journée ». Cible : moins de deux heures | RECETTE-05 (§ 9.2) |
| OS6 — Suggestion de remplaçant | Une liste ordonnée de remplaçants | **SO** : US-PLAN-10 (Could) est en réserve. La liste non ordonnée des remplaçants éligibles est livrée par US-PLAN-09 (RECETTE-01) |

### 9.2 La mesure OS5 et sa limite

La mesure demandée en phase 1 compare deux temps : celui du système et celui de la méthode actuelle, sur la même semaine. **Le temps de la méthode actuelle n'a jamais été chronométré** (point ouvert depuis la phase 2). Deux issues :

- **La séance du 29/10 a lieu.** La cellule planification construit la même semaine test avec ses outils, chronomètre en main, pendant que le binôme la construit avec le système. C'est la mesure prévue.
- **La séance n'a pas lieu.** Le binôme mesure seulement le temps du système, de la sélection des brigades jusqu'à un programme soumis, sur le jeu `complet` puis sur le jeu volumineux. Ce temps est comparé au point de départ **déclaré** (« au moins une journée »), et non à un temps mesuré. Le mémoire le présente comme tel : un objectif atteint au regard d'une référence déclarative, jamais comme un gain mesuré.

## 10. Ce que cette phase ne refait pas

- **La recette du sprint 1** (4 septembre, 115 contrôles, sept écarts majeurs refermés) n'est pas rejouée. RECETTE-00 en reprend un échantillon au titre de la non-régression.
- **Le cahier du sprint 2** (260 contrôles, dont l'exécution était « en cours » au 30/09 sans dépouillement consigné) n'est pas rejoué en entier. Il reste la référence détaillée du sprint 2. RECETTE-00 le **remplace pour le prononcé** par un échantillon couvrant chaque story. Le mémoire doit le dire ainsi : le cahier détaillé a été écrit et partiellement exécuté, et la non-régression finale s'est faite par échantillon.
- **Les stories de la réserve** (9 stories, 39 points) : non développées, donc non recettées.
- **La tenue en charge au-delà de la taille réelle du centre** : le jeu volumineux s'arrête à la taille du CIT (§ 4).
- **L'installation hors ligne** : elle relève de la phase 7 (déploiement sur machine virtuelle, D-295).
- **La sécurité au-delà des habilitations applicatives.**

---

*Plan de tests — version 1 du 26 octobre 2026. Lot WBS 6.1.*
