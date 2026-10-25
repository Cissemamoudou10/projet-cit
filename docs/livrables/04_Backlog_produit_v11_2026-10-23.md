**BACKLOG PRODUIT**

User stories et critères d’acceptation · Système de gestion des activités de formation du CIT

*Livrables 2 et 3 / 3 — Phase 2 · Version 11 du 23 octobre 2026 · Remplace la version 10 du 10 octobre 2026 · Artefact vivant*

# **1. Méthode**

Ce document constitue le backlog produit du projet. Il traduit les 61 besoins fonctionnels du cahier des charges en user stories, chacune assortie de ses critères d’acceptation.

## **1.1 Structure retenue**

| **Niveau** | **Contenu** | **Moment de définition** |
| --- | --- | --- |
| Epic | Un module fonctionnel du système | Phase 2 — présent document |
| User story | Un besoin utilisateur livrable et démontrable | Phase 2 — présent document |
| Tâche technique | Le découpage d’exécution d’une story | Sprint planning, au fil de l’eau |

| **Pourquoi les tâches techniques ne figurent pas ici** Le découpage en tâches d’une story dépend des choix de conception. Les définir dans le backlog produirait un document rapidement obsolète. Les tâches sont créées lors du sprint planning, pour les seules stories sélectionnées dans le sprint concerné. Cette approche applique le principe d’affinage progressif : le haut du backlog est détaillé, le bas reste volontairement grossier. |
| --- |

## **1.2 Format des user stories**

Chaque story suit le format « En tant que [rôle], je veux [action], afin de [bénéfice] » et respecte la règle de la **tranche verticale** : elle traverse toutes les couches de l’application — données, logique métier, présentation — et produit un résultat démontrable à un utilisateur du CIT.

## **1.3 Estimation**

Les stories sont estimées en **points de complexité** selon la suite de Fibonacci (1, 2, 3, 5, 8, 13). Cette échelle mesure une difficulté relative et non une durée absolue.

| **Points** | **Complexité** | **Caractérisation** |
| --- | --- | --- |
| 1 à 2 | Très faible | Opération simple sur une entité, sans règle métier particulière |
| 3 | Faible | Fonctionnalité classique avec quelques règles de gestion |
| 5 | Moyenne | Plusieurs entités concernées, règles métier ou interface élaborée |
| 8 | Élevée | Algorithme, workflow multi-états ou nombreuses interactions |
| 13 | Très élevée | Complexité algorithmique forte ; à découper si possible |

| **Clé de conversion et contrôle de cohérence — état au 23 octobre 2026, fin du développement** Le backlog totalise **263 points**, inchangé depuis la version 10. **Quatre sprints consécutifs ont livré cent pour cent de leur périmètre : 58 points sur 58, 61 sur 61, 50 sur 50, puis 55 sur 55.** L’estimation en points est validée par la mesure, et c’est désormais un résultat définitif : le développement est clos. La clé de conversion de 1,3 heure par point, en revanche, **ne sera jamais vérifiée par un relevé contemporain** : la colonne des heures humaines n’a été renseignée pour aucune des cinquante-deux stories livrées. Le relevé du sprint 4 mesure, comme celui du sprint 3, le temps de session de l’outil de développement, avec des interruptions non toujours notées. Le mémoire présentera donc l’estimation en points comme la seule mesure validée, et la clé de conversion comme une hypothèse de planification jamais vérifiée, avec la raison. Un relevé rétrospectif déclaratif reste possible, à condition d’être présenté comme tel. |
| --- |

## **1.4 Historique des versions**

Les encadrés d’évolution des versions 5 à 10 sont conservés dans les versions archivées correspondantes. Le tableau ci-dessous en garde la trace ; seule l’évolution de la présente version est détaillée.

| **Version** | **Date** | **Occasion** | **Périmètre** | **Principales évolutions** |
| --- | --- | --- | --- | --- |
| 5 | 14/08 | Clôture de la phase 2 | 57 stories · 245 pts | Backlog initial |
| 6 | 23/08 | Phase 4, réponses de terrain du 23 août | 58 · 247 | US-SUI-05 créée ; génération centre-entier (BF-PLAN-12) ; six stories précisées |
| 7 | 30/08 | Clôture de la phase 4 | 60 · 255 | US-PLAN-12 et US-SUI-06 créées ; deux types d’évaluation ; avenant annoncé sur US-PLAN-05 |
| 8 | 08/09 | Clôture du sprint 1 | 60 · 255 | Quatre stories précisées ; contradiction d’unicité tranchée sur US-REF-01 |
| 9 | 30/09 | Clôture du sprint 2 | 60 · 255 | Six stories précisées ; US-PLAN-08 déclassée ; trois principes d’arbitrage posés |
| 10 | 10/10 | Clôture du sprint 3, jalon J2 | 61 · 263 | Neuf stories réécrites ; US-PLAN-05 et US-VAL-05 réestimées ; US-EVAL-11 créée |
| **11** | **23/10** | **Clôture du sprint 4, jalon J3** | **61 · 263** | **Voir ci-dessous** |

| **Évolutions de la version 11 — clôture du sprint 4, jalon J3** La version 11 est la dernière version de développement du backlog : le sprint 4 a livré ses quatorze stories, cinquante-cinq points, et le jalon J3 a été atteint le 20 octobre, quatre jours avant son échéance. **Les cinquante-deux stories planifiées hors réserve sont livrées, soit 224 points sur 224.** Les neuf stories de la réserve, 39 points, ne sont pas développées : la phase 6 n’ouvre aucune story. **Aucune estimation n’est révisée, aucune story n’est créée ni retirée** : le périmètre reste de 61 stories et 263 points. **Quatorze stories sont précisées** pour décrire le comportement arbitré et livré, à partir des seize écarts consolidés dans le registre des écarts du sprint 4 et des décisions du sprint : US-REF-03, US-REF-09, US-SES-09, US-INS-04, US-PLAN-07, US-PLAN-08, US-PLAN-11, US-EVAL-07, US-EVAL-11, US-SUI-01, US-SUI-02, US-SUI-03, US-SUI-05 et US-SUI-06. Chaque précision est signalée par une note v11 sous la story concernée — pour US-PLAN-08 et US-SUI-05, dans le texte même —, et a été vérifiée à sa destination, critère par critère, conformément à la règle posée en version 10. **Trois corrections de fond.** Le critère 5 d’US-SUI-01 omettait deux profils, que la matrice d’habilitation désigne : il est corrigé, comme celui d’US-SUI-03, sur la même règle de précédent. US-REF-03 ne nommait ni le coefficient ni les deux poids, pourtant exigés par le calcul des moyennes : leur absence de critère explique qu’ils n’aient été implantés qu’au sprint 4. US-EVAL-07 confondait deux documents : le procès-verbal de fin de formation, qui porte la décision, et le procès-verbal d’une évaluation, qui n’en porte aucune. **Trois reports dits orphelins sont rangés.** D-212 et D-215, signalés sans story à la clôture du sprint 4, sont exactement les critères 2 et 1 d’US-EVAL-11, créée en version 10 pour les recevoir : ils ne sont pas orphelins mais en réserve avec elle. D-182 était déjà classé Won’t en version 10 (section 11.2). **Une demande d’évolution tranchée.** La séparation de l’application en un front-end et un back-end distincts, demandée par l’encadrant pendant le sprint 4, a fait l’objet d’une justification écrite ; l’encadrant a validé le maintien de l’architecture le 22 octobre. Elle est classée Won’t pour la version courante, comme perspective d’évolution (section 11.2). **Les travaux techniques hors backlog du sprint 4 sont tous clos** (section 11.1). **Ce que la version 11 ne modifie pas** : les estimations, les priorités et la clé de conversion (section 1.3). |
| --- |

# **2. Vue d’ensemble des epics**

| **Epic** | **Intitulé** | **Stories** | **Points** | **Priorité dominante** |
| --- | --- | --- | --- | --- |
| E1 | Administration et sécurité | 5 | 19 | Must |
| E2 | Référentiel de formation | 9 | 32 | Must |
| E3 | Sessions et brigades | 9 | 35 | Must |
| E4 | Instructeurs et qualifications | 4 | 16 | Must |
| E5 | Planification | 12 | 71 | Must et Should |
| E6 | Validation du programme | 5 | 20 | Must |
| E7 | Évaluations | 11 | 49 | Must |
| E8 | Suivi et traçabilité | 6 | 21 | Must et Should |
|  | Total | 61 | 263 |  |

## **2.1 État de livraison au 23 octobre 2026 — fin du développement**

| **Sprint** | **Période** | **Stories livrées** | **Points livrés** | **Jalon** |
| --- | --- | --- | --- | --- |
| 1 | 31/08 – 12/09 | 15 / 15 | 58 / 58 | C1 — prononcé le 12/09, sans mesure de vélocité |
| 2 | 14/09 – 26/09 | 12 / 12 | 61 / 61 | C2 — prononcé le 30/09, quatre jours de retard |
| 3 | 28/09 – 10/10 | 11 / 11 | 50 / 50 | J2 — tenu le 10/10, éléments de pilotage produits le même jour |
| 4 | 12/10 – 24/10 | 14 / 14 | 55 / 55 | J3 — atteint le 20/10, quatre jours d’avance ; étiquette `j3-fin-developpement` |
| **Cumul** | | **52 / 52** | **224 / 224** | Périmètre planifié hors réserve entièrement livré |
| Réserve | non engagée | 0 / 9 | 0 / 39 | Non développée : la phase 6 n’ouvre aucune story |

Les 194 points Must sont livrés depuis le 17 octobre, les 30 points Should du sprint 4 depuis le 20 octobre. Le plan des sprints et de la réserve est tenu au classeur de pilotage, seul document de référence pour l’ordonnancement. Le backlog porte les priorités et les estimations ; il n’affecte pas les stories aux sprints.

# **3. Epic E1 — Administration et sécurité**

Cet epic constitue le socle du système : sans authentification ni gestion des droits, aucune autre fonctionnalité ne peut être livrée de façon sécurisée.

| **US-ADM-01** | **S’authentifier au système** | **Must** | 3 pts | BF-ADM-01 |
| --- | --- | --- | --- | --- |

*En tant qu’utilisateur d’une cellule, je veux m’authentifier par identifiant et mot de passe, afin d’accéder aux fonctionnalités correspondant à mon profil.*

**Critères d’acceptation :**

- Un utilisateur disposant d’identifiants valides accède à la page d’accueil correspondant à son profil.

- Un identifiant inexistant ou un mot de passe erroné produit un message d’erreur générique, sans préciser lequel des deux est invalide.

- Les mots de passe sont stockés sous forme de condensats ; aucun mot de passe n’apparaît en clair en base ni dans les journaux.

- Une session inactive pendant trente minutes est fermée automatiquement.

- La déconnexion est accessible depuis toute page.

| **US-ADM-02** | **Gérer les comptes utilisateurs** | **Must** | 5 pts | BF-ADM-02 |
| --- | --- | --- | --- | --- |

*En tant qu’administrateur, je veux créer, modifier et désactiver des comptes utilisateurs, afin de contrôler qui accède au système.*

**Critères d’acceptation :**

- L’administrateur crée un compte en renseignant identité, identifiant et profil.

- Un compte peut être désactivé sans être supprimé, afin de préserver l’historique des actions.

- Un compte désactivé ne peut plus s’authentifier.

- L’identifiant est unique ; toute tentative de doublon est refusée avec un message explicite.

- Seul un administrateur accède à cette fonctionnalité.

| **US-ADM-03** | **Restreindre l’accès selon le profil** | **Must** | 5 pts | BF-ADM-03 |
| --- | --- | --- | --- | --- |

*En tant que responsable de la sécurité, je veux que chaque utilisateur n’accède qu’aux fonctionnalités et données de son profil, afin de protéger les informations sensibles.*

**Critères d’acceptation :**

- Cinq profils sont définis : pédagogique, planification, examens, Direction de Formation et administrateur.

- Le profil Direction de Formation dispose d’un accès en lecture seule aux tableaux de bord et à la traçabilité, sans droit de modification.

- Un utilisateur de la cellule planification consulte le référentiel sans pouvoir le modifier.

- Un utilisateur de la cellule planification n’accède à aucune note ni résultat d’évaluation.

- Toute tentative d’accès à une ressource non autorisée renvoie un refus explicite et est journalisée.

- Les restrictions sont appliquées côté serveur et non uniquement par masquage de l’interface.

| **US-ADM-04** | **Journaliser les actions sensibles** | **Must** | 3 pts | BF-ADM-04 |
| --- | --- | --- | --- | --- |

*En tant que responsable de la sécurité, je veux que les actions sensibles soient journalisées, afin de pouvoir retracer toute modification critique.*

**Critères d’acceptation :**

- Toute saisie ou modification de note est journalisée avec auteur, date et valeur précédente.

- Toute validation ou tout rejet de programme est journalisé.

- Toute sélection de sujet d’examen est journalisée.

- Les entrées de journal ne peuvent être ni modifiées ni supprimées depuis l’interface.

- L’administrateur consulte le journal avec filtrage par utilisateur, par date et par type d’action.

| **US-ADM-05** | **Exposer une interface de consultation des données** | **Should** | 3 pts | BF-ADM-05 |
| --- | --- | --- | --- | --- |

*En tant qu’intégrateur d’un système tiers, je veux consulter les données principales par une interface de programmation, afin de permettre une exploitation externe ultérieure.*

**Critères d’acceptation :**

- Les ressources formations, matières, instructeurs et programmes sont exposées en lecture.

- L’accès requiert une authentification et respecte les mêmes restrictions de profil que l’interface web.

- Les réponses sont fournies au format JSON.

- Aucune opération d’écriture n’est exposée dans cette version.

# **4. Epic E2 — Référentiel de formation**

Cet epic établit la source unique de vérité du système. Le référentiel est défini au niveau de la formation : il rattache des matières issues d’un catalogue partagé, chacune avec son volume horaire prescrit, ses prérequis et la catégorie de lieu qu’elle requiert.

| **US-REF-00** | **Gérer les types de formation** | **Must** | 2 pts | BF-REF-08 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule pédagogique, je veux gérer les types de formation, afin de classer les formations selon le public auquel elles s’adressent.*

**Critères d’acceptation :**

- Un type de formation comporte un intitulé unique, par exemple officiers, sous-officiers ou CAT-2.

- Une formation est rattachée à un type et un seul.

- Un type utilisé par au moins une formation ne peut être supprimé.

- Les listes de formations sont filtrables par type.

| **US-REF-01** | **Gérer les formations** | **Must** | 3 pts | BF-REF-01 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule pédagogique, je veux créer, consulter, modifier et archiver une formation, afin de tenir à jour le catalogue des formations dispensées.*

**Critères d’acceptation :**

- La création d’une formation renseigne intitulé, spécialité, durée et type de formation.

- L’intitulé est unique au sein d’un type de formation : deux formations homonymes rattachées à des types différents sont légitimes.

- Une formation archivée n’apparaît plus dans les listes de sélection mais reste consultable.

- Une formation disposant de sessions ne peut être supprimée, que ces sessions soient ouvertes ou clôturées. Le refus est délibérément plus large que la formulation d’origine : supprimer une formation dont une session close porte l’historique d’instruction détruirait des données non reconstituables.

- Seule la cellule pédagogique dispose des droits de création et de modification.

| **US-REF-02** | **Gérer le catalogue des matières** | **Must** | 3 pts | BF-REF-02 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule pédagogique, je veux gérer un catalogue de matières indépendant des formations, afin qu’une même matière puisse servir plusieurs formations sans double saisie.*

**Critères d’acceptation :**

- Une matière est créée dans le catalogue sans rattachement à une formation.

- L’intitulé d’une matière est unique dans le catalogue.

- La fiche d’une matière indique les formations qui l’utilisent dans leur référentiel.

- La liste des matières est paginée et dotée d’une recherche par intitulé.

- Une matière utilisée dans au moins un référentiel ne peut être supprimée.

- Toute modification d’une matière du catalogue est répercutée pour l’ensemble des formations concernées.

| **US-REF-03** | **Composer le référentiel d’une formation** | **Must** | 8 pts | BF-REF-03 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule pédagogique, je veux composer le référentiel d’une formation à partir du catalogue des matières, afin de fixer le contenu et les volumes horaires du cursus.*

**Critères d’acceptation :**

- Le référentiel rattache une ou plusieurs matières du catalogue à une formation.

- Chaque rattachement porte un volume horaire prescrit propre à cette formation.

- Une même matière rattachée à deux formations peut porter des volumes horaires différents.

- Le volume horaire est renseigné en heures et doit être strictement positif.

- La somme des volumes horaires du référentiel est affichée et comparée à la durée de la formation ; un écart déclenche un avertissement non bloquant.

- Une matière référencée par un prérequis, une séance programmée ou une évaluation ne peut être retirée du référentiel ; le refus énumère les éléments qui s’y opposent.

- Chaque rattachement porte en outre un coefficient, strictement positif, et deux poids — formatif et certificatif —, positifs ou nuls et jamais nuls tous les deux. Leurs valeurs par défaut sont 1, 1 et 1 ; la cellule pédagogique les modifie sur le même écran que le volume horaire.

*Note v11 : critère ajouté. Le diagramme de classes portait ces trois valeurs depuis la phase 4 et le calcul des moyennes (US-EVAL-06) les exige ; faute de critère, elles n’ont été implantées qu’au sprint 4 (écart 4 du sprint 4).*

| **US-REF-04** | **Déclarer la catégorie de lieu requise par matière** | **Must** | 3 pts | BF-REF-04 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule pédagogique, je veux préciser le type de lieu que chaque matière nécessite, afin que la planification affecte les lieux appropriés.*

**Critères d’acceptation :**

- Trois catégories sont proposées : salle attitrée de la brigade, lieu partagé, aucun lieu requis.

- Une matière en lieu partagé précise le type attendu : amphithéâtre, laboratoire ou salle spécialisée.

- Les matières sans lieu requis, telles que l’ordre serré ou le sport, ne consomment aucune ressource de salle lors de la génération.

- La catégorie est exploitée comme contrainte par le moteur de génération.

| **US-REF-05** | **Associer des objectifs pédagogiques aux matières** | **Must** | 3 pts | BF-REF-05 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule pédagogique, je veux renseigner les objectifs pédagogiques de chaque matière, afin d’expliciter les compétences visées.*

**Critères d’acceptation :**

- Une matière du catalogue peut porter plusieurs objectifs pédagogiques.

- Chaque objectif comporte un libellé et un ordre d’affichage.

- Les objectifs sont consultables depuis la fiche de la matière et depuis le référentiel des formations qui l’utilisent.

- La suppression d’un objectif n’affecte pas la matière.

| **US-REF-06** | **Déclarer les prérequis d’un référentiel** | **Must** | 5 pts | BF-REF-06 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule pédagogique, je veux déclarer les prérequis entre matières d’un référentiel, afin que la progressivité de l’apprentissage soit garantie lors de la planification.*

**Critères d’acceptation :**

- Une matière du référentiel peut déclarer une ou plusieurs matières prérequises au sein du même référentiel.

- Le système détecte et refuse les dépendances circulaires.

- Les prérequis sont exploitables comme contrainte dure lors de la génération du programme.

- Une violation de prérequis lors d’une saisie manuelle est signalée explicitement.

| **US-REF-07** | **Consulter le référentiel depuis les autres cellules** | **Must** | 2 pts | BF-REF-07 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule planification ou examens, je veux consulter le référentiel en lecture seule, afin de disposer d’une information fiable sans risquer de l’altérer.*

**Critères d’acceptation :**

- Les formations, matières, volumes horaires et prérequis sont consultables par les cellules planification et examens ainsi que par la direction de formation, conformément à la matrice d’habilitation.

- Aucun bouton de création, de modification ou de suppression n’est accessible à ces profils.

- Une tentative de modification par appel direct est refusée côté serveur.

- Toute modification du référentiel par la cellule pédagogique est immédiatement visible par les autres cellules.

| **US-REF-09** | **Historiser les modifications du référentiel** | **Should** | 3 pts | BF-REF-09 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule pédagogique, je veux consulter l’historique des modifications du référentiel, afin de retracer l’évolution des cursus.*

**Critères d’acceptation :**

- Toute création, modification ou archivage est enregistré avec auteur et date.

- L’historique d’une formation, d’une matière, d’un référentiel ou d’un prérequis est consultable depuis sa fiche. Il suit l’objet même après un renommage.

- Les valeurs antérieures des champs modifiés sont conservées, notamment les volumes horaires.

- L’historique est consultable mais non modifiable.

- L’historique commence à la mise en service de la fonction : aucune modification antérieure n’est reconstituée.

*Note v11 : le prérequis, l’identité stable après renommage et l’absence de reprise rétroactive décrivent le comportement livré (décisions D-286 et D-287).*

# **5. Epic E3 — Sessions et brigades**

Cet epic gère l’exécution datée du référentiel. Une session est l’ouverture d’une formation pour une période donnée ; elle se découpe en brigades selon l’effectif des stagiaires et la capacité des salles disponibles.

| **US-SES-01** | **Ouvrir une session de formation** | **Must** | 5 pts | BF-SES-01 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule pédagogique, je veux ouvrir une session pour une formation, afin d’organiser une promotion sur une période déterminée.*

**Critères d’acceptation :**

- Une session est rattachée à une formation et porte une date de début, une date de fin et un effectif attendu.

- Le référentiel de la formation est repris automatiquement par la session.

- Plusieurs sessions d’une même formation peuvent coexister sur des périodes différentes.

- Une session ne peut être ouverte sur une formation archivée.

- Les formations ouvertes sur ordre sont créées de la même façon, sans périodicité imposée.

| **US-SES-02** | **Constituer les brigades d’une session** | **Must** | 5 pts | BF-SES-02 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule pédagogique, je veux créer les brigades d’une session, afin de répartir l’effectif en groupes compatibles avec la capacité des salles.*

**Critères d’acceptation :**

- Les brigades sont saisies manuellement : le système enregistre la répartition décidée sans la calculer.

- Toute session comporte au minimum une brigade.

- Chaque brigade porte un intitulé et un effectif.

- La somme des effectifs des brigades est comparée à l’effectif de la session ; un écart est signalé.

- Une brigade dont le programme est en cours ne peut être supprimée.

| **US-SES-03** | **Affecter une salle attitrée à chaque brigade** | **Must** | 3 pts | BF-SES-03 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule planification, je veux attribuer une salle à chaque brigade pour la durée de la session, afin qu’elle y tienne ses cours ordinaires.*

**Critères d’acceptation :**

- Une salle attitrée est affectée à une brigade pour toute la durée de la session.

- La capacité de la salle doit être supérieure ou égale à l’effectif de la brigade ; le cas contraire est refusé.

- Une salle attitrée ne peut être affectée simultanément à deux brigades dont les sessions se chevauchent.

- La salle attitrée est utilisée par défaut pour toutes les matières ne requérant pas de lieu particulier.

| **US-SES-04** | **Consulter la composition d’une session** | **Must** | 3 pts | BF-SES-04 |
| --- | --- | --- | --- | --- |

*En tant que membre d’une cellule, je veux consulter la répartition d’une session en brigades, afin de connaître les effectifs et les salles concernées.*

**Critères d’acceptation :**

- La fiche de session présente ses brigades, leurs effectifs et leurs salles attitrées.

- Le référentiel appliqué à la session est consultable depuis cette fiche.

- La vue est accessible aux trois cellules et à la Direction de la formation, en lecture pour la planification, les examens et la Direction de la formation.

- La fiche présente le taux d’occupation de chaque brigade, rapport de son effectif à la capacité de sa salle attitrée. Une brigade sans salle attitrée, une salle sans capacité renseignée et un taux supérieur à cent pour cent sont signalés explicitement, jamais rendus par une case vide.

| **US-SES-05** | **Enregistrer les stagiaires d’une session** | **Must** | 5 pts | BF-SES-05 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule pédagogique, je veux enregistrer les stagiaires d’une session, individuellement ou par import d’un fichier, afin de disposer de la liste nominative nécessaire aux évaluations.*

**Critères d’acceptation :**

- Un stagiaire comporte une identité, un matricule et une unité d’origine, et est rattaché à une session.

- L’enregistrement peut se faire manuellement, stagiaire par stagiaire.

- Un fichier tabulaire au format CSV ou Excel peut être importé pour créer l’ensemble des stagiaires d’une session.

- Le format attendu des colonnes est documenté et un modèle de fichier est téléchargeable.

- Les lignes comportant une erreur sont signalées avec leur numéro et le motif ; aucun import partiel n’est effectué tant que les erreurs subsistent.

- Le matricule est unique au sein d’une session ; les doublons sont détectés à l’import.

- Un stagiaire qui quitte la formation est radié, avec un motif et une date : il n’est jamais supprimé, ses évaluations éventuelles étant conservées. Radier et supprimer sont deux actions distinctes, aux libellés et aux confirmations distincts.

| **US-SES-06** | **Affecter les stagiaires aux brigades** | **Must** | 5 pts | BF-SES-06 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule pédagogique, je veux répartir les stagiaires entre les brigades d’une session, afin de constituer les groupes qui suivront les enseignements.*

**Critères d’acceptation :**

- Le système propose une répartition automatique remplissant les brigades successivement jusqu’à leur effectif déclaré.

- La répartition proposée est intégralement modifiable : un stagiaire peut être déplacé d’une brigade à une autre.

- L’effectif réel de chaque brigade est comparé à deux plafonds de nature différente, qui appellent deux traitements distincts. La capacité de la salle attitrée est un fait physique : son dépassement est REFUSÉ, avec indication de la marge restante. L’effectif déclaré de la brigade est une valeur prévisionnelle : son dépassement donne lieu à un AVERTISSEMENT et n’empêche jamais l’affectation.

- Un stagiaire ne peut être affecté qu’à une seule brigade au sein d’une session.

- Les stagiaires non affectés sont listés séparément.

| **US-SES-07** | **Consulter la liste des stagiaires** | **Must** | 3 pts | BF-SES-07 |
| --- | --- | --- | --- | --- |

*En tant que membre d’une cellule, je veux consulter les stagiaires d’une session ou d’une brigade, afin de connaître les effectifs réels.*

**Critères d’acceptation :**

- La liste est consultable au niveau de la session et au niveau de chaque brigade.

- Une recherche par nom, prénom ou matricule est disponible.

- La liste est exportable au format tabulaire.

- La cellule examens y accède en lecture pour la saisie des notes.

| **US-SES-08** | **Désigner les chefs de module** | **Should** | 3 pts | BF-SES-08 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule pédagogique, je veux désigner un chef de module pour chaque matière d’une session, afin d’identifier le responsable pédagogique de la matière.*

**Critères d’acceptation :**

- Un chef de module est désigné par matière et par session, parmi les instructeurs.

- La désignation porte sur une matière du catalogue, indépendamment de la formation et de la session. Elle est datée, et l’instructeur désigné doit être qualifié pour la matière.

- Le chef de module figure sur la fiche de la matière au sein de la session.

- Une matière peut rester sans chef de module désigné.

*Note v10 : le premier et le troisième critère de la version 9 répétaient tous deux l’exigence de qualification ; le doublon est retiré, sans changement de sens.*

| **US-SES-09** | **Clôturer une session** | **Should** | 3 pts | BF-SES-09 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule pédagogique, je veux clôturer une session achevée, afin de la retirer des vues courantes tout en conservant son historique.*

**Critères d’acceptation :**

- Une session clôturée n’apparaît plus dans les listes de sélection actives.

- Ses brigades, programmes et résultats restent consultables.

- La clôture est enregistrée avec son auteur et sa date.

- Une session comportant des évaluations non finalisées ne peut être clôturée. Une évaluation est finalisée lorsque ses notes sont verrouillées par un procès-verbal ; le refus énumère les évaluations en cause.

- Après la clôture, la déclaration et l’annulation d’une non-exécution sont refusées sur les séances de la session.

- Aucune réouverture n’est offerte : une clôture erronée se corrige hors de l’interface. C’est une limite assumée.

*Note v11 : précisions issues de la livraison (décisions D-262, fermée, et D-281).*

# **6. Epic E4 — Instructeurs et qualifications**

Cet epic fournit la matrice de qualification, contrainte déterminante de l’affectation.

| **US-INS-01** | **Gérer les instructeurs** | **Must** | 5 pts | BF-INS-01 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule pédagogique, je veux gérer la fiche des instructeurs, afin de disposer d’un annuaire fiable du corps enseignant.*

**Critères d’acceptation :**

- La fiche comporte identité, grade, matricule, spécialité et statut : militaire du centre, vacataire ou civil. Le matricule est obligatoire et unique pour un militaire du centre, facultatif pour un vacataire ou un civil.

- Un instructeur peut être archivé sans suppression, afin de préserver l’historique des affectations.

- La liste des instructeurs est paginée et dotée d’une recherche par nom, prénom ou matricule, avec filtrage par statut et par spécialité.

- Un instructeur affecté à un programme en cours ne peut être supprimé.

| **US-INS-02** | **Établir la matrice de qualification** | **Must** | 5 pts | BF-INS-02 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule pédagogique, je veux déclarer les matières du catalogue que chaque instructeur est habilité à enseigner, afin que seules des affectations valides soient possibles.*

**Critères d’acceptation :**

- Une qualification associe un instructeur à une matière du catalogue, indépendamment des formations et des brigades.

- Un instructeur peut être qualifié pour plusieurs matières et une matière peut compter plusieurs instructeurs qualifiés.

- La matrice est consultable par instructeur et par matière.

- Une matière sans aucun instructeur qualifié est signalée visuellement.

- La cellule planification consulte la matrice sans pouvoir la modifier.

| **US-INS-03** | **Enregistrer les indisponibilités transmises** | **Must** | 3 pts | BF-INS-03 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule planification, je veux enregistrer les périodes d’indisponibilité qu’un instructeur m’a transmises hors système, afin qu’il ne soit pas affecté sur ces créneaux.*

**Critères d’acceptation :**

- L’instructeur ne dispose d’aucun accès au système : la saisie est effectuée par la cellule planification à partir d’une transmission externe.

- Une indisponibilité comporte une date de début, une date de fin et un motif.

- La saisie est horodatée et rattachée à l’utilisateur qui l’effectue, et non à l’instructeur concerné.

- Les indisponibilités sont prises en compte comme contrainte lors de la génération du programme.

- Une indisponibilité déclarée sur un créneau déjà affecté déclenche une alerte signalant les séances concernées, dont le traitement relève d’US-PLAN-09.

- Les indisponibilités passées sont conservées à des fins d’historique.

| **US-INS-04** | **Consulter la charge d’un instructeur** | **Should** | 3 pts | BF-INS-04 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule planification, je veux consulter la charge d’enseignement d’un instructeur sur une période, afin d’équilibrer les affectations.*

**Critères d’acceptation :**

- La charge est exprimée en heures sur une période sélectionnable.

- Le détail par matière est consultable.

- Les instructeurs sont comparables entre eux sur la même période.

- Une charge dépassant un seuil paramétrable est signalée. Le seuil s’exprime en heures par semaine et se compare à la moyenne hebdomadaire de la période ; sa valeur par défaut, 24 heures, est une hypothèse à confirmer avec le terrain.

- Une séance regroupant plusieurs brigades n’est comptée qu’une fois.

- Les surveillances d’épreuve sont présentées à part et ne s’ajoutent pas à la charge d’enseignement.

*Note v11 : seuil et surveillances précisés à la livraison ; la valeur de 24 heures figure aux questions de terrain.*

# **7. Epic E5 — Planification**

Cet epic constitue le cœur métier du système et concentre la complexité algorithmique du projet. Chaque brigade disposant d’une salle attitrée, l’arbitrage porte principalement sur les instructeurs et sur l’accès aux lieux partagés.

| **US-PLAN-01** | **Élaborer le calendrier académique annuel** | **Must** | 8 pts | BF-PLAN-01 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule planification, je veux construire le calendrier annuel, afin de fixer le cadre dans lequel s’inscrivent les programmes hebdomadaires.*

**Critères d’acceptation :**

- Le calendrier couvre une année de formation et distingue les types de périodes : cours, conférences, visites, congés, examens, bivouacs et formations techniques.

- Une période comporte un début et une fin exprimés avec une granularité horaire, permettant de couvrir aussi bien une conférence de deux heures qu’un bivouac d’une semaine.

- Une période peut occuper une fraction de journée, le reste de la journée demeurant disponible pour d’autres séances.

- Une période cible un ensemble de sessions et un ensemble de brigades, l’un et l’autre pouvant être vides, auquel cas elle porte sur le centre entier. Seul le DOUBLON EXACT — mêmes bornes et mêmes ensembles de cibles — est refusé. Toute autre intersection donne lieu à un avertissement, les périodes se cumulant sans se contredire.

- Les périodes bloquées sont exclues automatiquement lors de la génération du programme hebdomadaire.

- La création d’une période bloquante qui recouvre des séances déjà programmées énumère ces séances, chacune avec un accès à sa modification. Le système ne les déplace ni ne les supprime : l’arbitrage est humain. La suppression d’une période ne restaure d’office aucune séance.

- Le calendrier est consultable sous forme de vue annuelle ; les dates des sessions et les jours d’examen final y sont projetés depuis leur source, jamais recopiés en période.

| **US-PLAN-02** | **Gérer les lieux d’enseignement** | **Must** | 3 pts | BF-PLAN-02 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule planification, je veux gérer les lieux et leurs capacités, afin de disposer d’un inventaire fiable pour les affectations.*

**Critères d’acceptation :**

- Un lieu comporte un intitulé, une capacité et une catégorie : salle attitrable ou lieu partagé.

- Les lieux partagés précisent leur type : amphithéâtre, laboratoire ou salle spécialisée.

- Un lieu peut être déclaré indisponible sur une période.

- Un lieu affecté à une brigade ou à une séance ne peut être supprimé.

- La liste des lieux est filtrable par catégorie, par capacité et par disponibilité.

| **US-PLAN-12** | **Gérer les grilles horaires et désigner la grille active** | **Must** | 5 pts | BF-PLAN-13 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule planification, je veux définir plusieurs grilles horaires et désigner celle qui est active, afin que la génération propose les créneaux réellement en vigueur.*

**Critères d’acceptation :**

- Une grille est un ensemble de créneaux types, définis par un jour de semaine, un rang, une heure de début et une heure de fin.

- Les créneaux d’un même jour ne se recouvrent pas ; un jour sans créneau est non programmable par défaut, sans être interdit.

- Plusieurs grilles coexistent ; une seule est active à la fois, et l’activation d’une grille désactive la précédente.

- L’activation est datée et rattachée à l’agent qui la décide ; elle n’est jamais déduite du calendrier.

- Une grille en service se clôture, elle ne se supprime pas ; une grille sans créneau ne peut être activée.

- Changer de grille active ne modifie pas les séances passées, qui portent leurs heures réelles.

| **US-PLAN-03** | **Générer le programme hebdomadaire du centre** | **Must** | 8 pts | BF-PLAN-03, 12 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule planification, je veux générer le programme d’une semaine pour les brigades que je sélectionne, afin de disposer d’une proposition d’affectation sans saisie manuelle exhaustive.*

**Critères d’acceptation :**

- La génération porte sur une semaine et une ou plusieurs brigades sélectionnées, appartenant le cas échéant à des sessions différentes. Le programme est unique pour la semaine et couvre le centre entier : une génération sur une sélection le complète, elle ne le remplace pas.

- La résolution tient compte des affectations existantes de toutes les sessions actives sur la semaine, quelle que soit l’étendue de la sélection, ainsi que des épreuves organisées.

- Les matières dont le volume prescrit est épuisé ou dont les prérequis ne sont pas achevés sont écartées de la génération.

- Chaque séance générée comporte une matière, un instructeur, un créneau et, lorsque la matière l’exige, un lieu partagé.

- Les matières se déroulant en salle attitrée reprennent automatiquement la salle de la brigade.

- Les matières ne requérant aucun lieu sont placées sans réservation.

- Les séances verrouillées — saisies ou modifiées à la main, ou portant une évaluation — sont conservées par une régénération.

- La génération est refusée sur un programme soumis, validé ou affiché ; sur un programme rejeté, elle le ramène d’abord à l’état brouillon.

- Un compte rendu indique le nombre de séances placées et les éventuelles séances non placées avec leur motif.

| **US-PLAN-04** | **Garantir le respect des contraintes dures** | **Must** | 8 pts | BF-PLAN-04 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule planification, je veux que le système empêche toute affectation invalide, afin de garantir un programme exécutable.*

**Critères d’acceptation :**

- Un instructeur ne peut être affecté à deux séances simultanées, y compris sur des brigades différentes, ni à une séance pendant une épreuve qu’il surveille.

- Un instructeur ne peut être affecté qu’à une matière pour laquelle il est qualifié.

- Un lieu partagé ne peut accueillir deux séances simultanées relevant de brigades distinctes, sauf regroupement explicite, ni une séance pendant une épreuve qui s’y tient.

- La capacité du lieu est supérieure ou égale à l’effectif concerné.

- Aucune séance n’est placée sur une période bloquée par le calendrier annuel, sur un jour d’examen final dont le périmètre couvre la brigade, ou sur une indisponibilité déclarée.

- Le volume horaire programmé pour une matière n’excède pas le volume prescrit par le référentiel de la formation. Tous les programmes de la brigade comptent, quel que soit leur état, rejetés compris.

- Une matière ne peut être programmée avant que ses matières prérequises aient été dispensées.

- Ces contrôles s’appliquent à tous les chemins d’écriture d’une séance, sans exception : génération, saisie manuelle, regroupement, traitement d’une indisponibilité, insertion d’un contrôle.

| **US-PLAN-05** | **Modifier manuellement une affectation** | **Must** | 8 pts | BF-PLAN-05 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule planification, je veux ajuster manuellement une séance, afin de traiter les situations que la génération automatique ne couvre pas.*

**Réestimée de 5 à 8 points en version 10** : la story porte désormais l’avenant, exigé par BF-PLAN-05 depuis la version 7 du cahier des charges et annoncé en version 7 du backlog sans jamais atteindre ses critères.

**Critères d’acceptation :**

- Une séance peut être déplacée au sein de sa semaine, son instructeur, son lieu ou sa matière modifiés. Une séance déjà commencée n’est plus modifiable.

- Toute modification est soumise aux contraintes dures ; un refus nomme la contrainte concernée.

- En cas d’indisponibilité imprévue d’un lieu, la séance peut être basculée vers un autre lieu conforme ou vers une activité ne requérant aucun lieu. Cette bascule est une décision humaine : le système ne la propose jamais d’office.

- Une séance peut être ajoutée sur un créneau libre, ou supprimée ; la suppression diminue d’autant le volume programmé de la matière.

- Une séance modifiée ou ajoutée à la main est verrouillée et identifiable dans le programme ; elle peut être déverrouillée pour redevenir remplaçable par une régénération. La séance d’un contrôle ne peut être ni déverrouillée ni supprimée par ce biais.

- La modification d’une séance regroupant plusieurs brigades exige une confirmation, après énumération des brigades concernées.

- Sur un programme **soumis**, la modification est refusée et le système indique de retirer la soumission.

- Sur un programme **validé**, la modification exige d’abord l’annulation de la validation, motivée et confirmée, qui ramène le programme à l’état brouillon et impose une nouvelle soumission. Aucune annulation n’est implicite.

- Sur un programme **affiché**, la modification ou l’ajout portent un **avenant** daté, motivé et typé ; le programme reste affiché, la validation et la signature demeurent acquises. La suppression d’une séance affichée est refusée : une séance qui n’a pas lieu relève de la non-exécution (US-SUI-05).

| **US-PLAN-06** | **Regrouper plusieurs brigades sur une même séance** | **Must** | 5 pts | BF-PLAN-06 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule planification, je veux regrouper plusieurs brigades sur une même séance en lieu partagé, afin d’organiser conférences et activités communes.*

**Critères d’acceptation :**

- Plusieurs brigades peuvent être associées à une même séance se tenant en lieu partageable simultanément ; seules les brigades pour lesquelles la matière est programmable sur ce créneau sont proposées.

- Chaque brigade concernée conserve une ligne distincte sur le programme, rattachée à la séance commune.

- La charge de l’instructeur n’est comptabilisée qu’une seule fois pour l’ensemble du regroupement, et le regroupement n’est pas un conflit d’affectation.

- La somme des effectifs des brigades regroupées ne peut excéder la capacité du lieu ; le refus indique l’écart.

- Chaque brigade ajoutée est soumise aux contraintes dures qui la concernent : volume, prérequis, disponibilité sur le créneau.

- Le retrait d’une brigade supprime sa ligne et libère son créneau ; il ne crée jamais de séance autonome, qui aurait le même instructeur au même créneau. La dissolution d’un regroupement est une suite de retraits.

- Plusieurs brigades accueillies successivement dans un même lieu ne forment pas un regroupement mais des séances distinctes, comptées séparément dans la charge.

- Sur un programme affiché, l’association d’une brigade porte un avenant ; le retrait est refusé et relève de la non-exécution.

| **US-PLAN-07** | **Signaler les écarts de volume horaire** | **Should** | 3 pts | BF-PLAN-07 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule planification, je veux être alerté des écarts entre volume prescrit et volume programmé, afin de corriger avant validation.*

**Critères d’acceptation :**

- Pour chaque matière, le volume prescrit par le référentiel et le volume programmé cumulé sont affichés.

- Un écart supérieur à un seuil paramétrable est signalé visuellement.

- Le signalement distingue les sous-programmations des sur-programmations.

- L’indicateur est consultable avant soumission du programme à validation.

- La sous-programmation n’est signalée qu’après la date de fin de la session ; avant, la matière est présentée « en cours ». Le seuil est exprimé en pourcentage du volume prescrit, 10 % par défaut.

*Note v11 : sans la première précision, toute matière en cours de session paraîtrait sous-programmée (décision D-278). L’indicateur compare le volume **programmé** ; l’alerte sur le volume **réalisé** relève d’US-SUI-02 (décision D-282).*

| **US-PLAN-08** | **Optimiser l’affectation sous contraintes** | **Should — déclassée** | 8 pts | BF-PLAN-08 |
| --- | --- | --- | --- | --- |

| **Déclassée en perspective d’évolution — décision du 30 septembre 2026, inchangée en version 10** L’étude de faisabilité conduite au sprint 2 établit que le solveur est techniquement réalisable, mais que son gain réel — deux à trois créneaux d’écart de charge — est disproportionné à son coût : cent dix mégaoctets de dépendance, jusqu’à trois gigaoctets de mémoire par résolution, un défaut mémoire natif constaté, et un second corps de code à maintenir en miroir du service de contraintes. **Cette story n’est pas retirée du backlog** : elle reste de priorité Should et ses critères demeurent valides. Elle sera réexaminée à la clôture du sprint 4 sous deux conditions cumulatives — périmètre *Must* entièrement livré et marge de quatorze jours ouvrés avant dépôt intacte. La seconde condition n’est plus remplie depuis le 30 septembre, la marge étant de neuf jours : sauf reconstitution de la marge, le réexamen conclura au maintien du déclassement. **Réexamen tenu le 20 octobre, à la clôture du sprint 4 : déclassement maintenu** (décision D-289), la condition de marge n’étant pas remplie. US-PLAN-08 sera présentée au mémoire comme perspective d’évolution, avec l’étude de faisabilité. |
| --- |

*En tant que membre de la cellule planification, je veux que le système propose une affectation optimisée pour l’ensemble des brigades, afin d’obtenir des programmes équilibrés sans arbitrage manuel prolongé.*

**Critères d’acceptation :**

- Le problème est modélisé sous forme de contraintes et résolu par un solveur, en traitant simultanément les brigades qui partagent instructeurs et lieux partagés.

- Les contraintes dures sont toutes respectées ou l’absence de solution est signalée explicitement.

- Les contraintes souples sont pénalisées : déséquilibre de charge entre instructeurs, dispersion des séances d’une même matière, interruptions dans la journée. Le décalage volontaire des séquences entre brigades est préservé et non corrigé.

- La résolution s’achève en moins de cinq minutes pour une semaine complète, toutes brigades confondues.

- En cas d’échec ou de dépassement du temps imparti, le système bascule sur la génération heuristique et le signale à l’utilisateur.

- La solution proposée reste modifiable manuellement.

| **US-PLAN-09** | **Traiter une indisponibilité déclarée** | **Must** | 5 pts | BF-PLAN-09 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule planification, je veux traiter les séances impactées par une indisponibilité d’instructeur, afin de rétablir un programme exécutable.*

**Critères d’acceptation :**

- La déclaration d’une indisponibilité liste immédiatement les séances non commencées qu’elle affecte, toutes brigades confondues, avec l’état du programme de chacune. La liste reste consultable ensuite, et toute extension de la période la recalcule.

- Pour chaque séance, trois voies sont proposées : remplacer l’instructeur, substituer une autre matière, ou déprogrammer.

- Le remplacement ne propose que des instructeurs qualifiés pour la matière et libres sur le créneau : ni indisponibles, ni déjà en séance, ni surveillants d’une épreuve sécante.

- La substitution place une autre matière du référentiel, dans le respect des prérequis et du volume prescrit.

- Les séances d’une même matière peuvent être traitées en lot avec un même remplaçant, après confirmation globale. Le lot est tout ou rien : si une seule séance est refusée, aucune n’est modifiée et le refus nomme la séance et la contrainte.

- Le traitement suit l’état du programme : sur un programme soumis, il renvoie au retrait de la soumission ; sur un programme validé, à l’annulation de la validation ; sur un programme affiché, le remplacement et la substitution portent un avenant et le programme reste affiché, la déprogrammation étant refusée au profit de la non-exécution.

- Une séance déjà commencée ne relève pas de ce traitement mais de la non-exécution.

- Toute résolution est soumise au contrôle des contraintes dures.

| **US-PLAN-10** | **Suggérer un remplaçant** | **Could** | 5 pts | BF-PLAN-10 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule planification, je veux obtenir une liste ordonnée de remplaçants lorsqu’un instructeur devient indisponible, afin de réagir rapidement.*

**Critères d’acceptation :**

- Pour une séance donnée, le système propose les instructeurs qualifiés et disponibles sur le créneau.

- La liste est ordonnée selon un score combinant qualification, charge courante et disponibilité.

- Les critères de pondération du score sont paramétrables sans modification du code.

- La sélection d’un remplaçant met à jour la séance après contrôle des contraintes.

- L’absence de remplaçant disponible est signalée explicitement.

*Note v10 : la liste non ordonnée des remplaçants éligibles est déjà livrée par US-PLAN-09. La présente story n’ajoute que le classement et son paramétrage.*

| **US-PLAN-11** | **Dupliquer un programme hebdomadaire** | **Should** | 5 pts | BF-PLAN-11 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule planification, je veux dupliquer un programme existant vers une autre semaine, afin de gagner du temps sur les semaines qui se ressemblent.*

**Critères d’acceptation :**

- La duplication reporte les séances sur les créneaux équivalents de la semaine cible.

- Le programme dupliqué est créé à l’état brouillon et demeure modifiable. Une semaine cible dont le programme est soumis, validé ou affiché ne peut recevoir de duplication.

- L’ensemble des contraintes dures est vérifié sur la semaine cible : disponibilité des instructeurs, des lieux partagés, périodes bloquées, jours d’examen, épreuves organisées et volumes horaires prescrits.

- Les séances non reportables sont écartées et listées avec le motif du refus.

- Le volume horaire cumulé après duplication est comparé au volume prescrit ; tout dépassement est signalé.

- La duplication peut porter sur une ou plusieurs brigades simultanément.

- Les séances d’un contrôle et les séances déclarées non exécutées ne sont pas dupliquées ; elles figurent dans la liste des séances écartées. Les séances dupliquées ne sont pas verrouillées : une régénération peut les remplacer.

*Note v11 : précisions issues de la livraison.*

# **8. Epic E6 — Validation du programme**

Cet epic matérialise le circuit de validation croisée identifié sur le terrain : le programme élaboré par la planification est validé par la cellule pédagogique, signé par le directeur de la formation, puis affiché. **La machine à états qui fait foi est le diagramme ETA-01** (cinq états, dix transitions T1 à T10), produit le 30 septembre 2026 et soumis aux cellules. Les critères ci-dessous en sont la traduction ; en cas d’écart, ETA-01 l’emporte.

| **US-VAL-01** | **Soumettre un programme à validation** | **Must** | 3 pts | BF-VAL-01 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule planification, je veux soumettre un programme achevé à la cellule pédagogique, afin d’obtenir son approbation avant diffusion.*

**Critères d’acceptation :**

- Un programme à l’état brouillon et comportant au moins une séance peut être soumis.

- La soumission fait passer le programme à l’état soumis et le rend non modifiable par la planification.

- La cellule pédagogique est informée dans l’application : une page présente les programmes en attente de décision, avec la semaine, la date de soumission et son auteur, et un compteur est visible dans sa navigation.

- Un programme déjà soumis ne peut être soumis à nouveau.

- Tant qu’aucune décision n’est rendue, la planification peut retirer la soumission ; le programme redevient brouillon.

| **US-VAL-02** | **Valider ou rejeter un programme** | **Must** | 5 pts | BF-VAL-02 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule pédagogique, je veux valider ou rejeter un programme soumis, afin de garantir sa conformité au référentiel.*

**Critères d’acceptation :**

- La cellule pédagogique consulte le programme avant décision ; elle lit les programmes de toutes les semaines, quel que soit leur état.

- La décision porte sur le programme du centre entier, jamais brigade par brigade.

- La validation fait passer le programme à l’état validé, avec le nom du validateur et la date.

- Le rejet exige un motif et fait passer le programme à l’état **rejeté**. La reprise en correction — explicite, ou par la première modification d’une séance — le ramène à l’état brouillon.

- Le motif de rejet est visible par la cellule planification, à l’état rejeté puis après la reprise, jusqu’à la soumission suivante.

- Seule la cellule pédagogique dispose de ce droit.

| **US-VAL-03** | **Gérer les états du programme** | **Must** | 5 pts | BF-VAL-03 |
| --- | --- | --- | --- | --- |

*En tant qu’utilisateur du système, je veux que l’état de chaque programme soit explicite, afin de savoir où il en est dans le circuit.*

**Critères d’acceptation :**

- Cinq états sont définis : brouillon, soumis, validé, rejeté et affiché.

- Les transitions autorisées sont celles du diagramme ETA-01 : création en brouillon ; soumission ; retrait de la soumission ; validation ; rejet ; reprise en correction ; enregistrement de la signature ; affichage ; annulation de la validation ; avenant sur un programme affiché, qui n’en change pas l’état. Un programme affiché ne revient jamais à l’état brouillon.

- Toute transition non autorisée est refusée, avec un message qui nomme la règle et, lorsqu’elle existe, la marche à suivre.

- L’état courant est visible partout où le programme est présenté, et à l’écran de lancement de la génération, qui indique pourquoi la génération est indisponible le cas échéant.

- Les droits d’action dépendent de l’état et du profil de l’utilisateur.

- Chaque transition est journalisée avec son auteur, sa date, l’état de départ, l’état d’arrivée et le motif éventuel.

| **US-VAL-04** | **Empêcher l’affichage d’un programme non validé** | **Must** | 2 pts | BF-VAL-04 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule pédagogique, je veux qu’aucun programme non validé ne puisse être affiché, afin de préserver la conformité de la formation dispensée.*

**Critères d’acceptation :**

- L’action d’affichage n’est proposée que sur un programme validé dont la signature du directeur de la formation a été enregistrée.

- La signature est manuscrite et demeure hors système : la cellule planification en enregistre la date et le nom du signataire. La date ne peut être antérieure à la validation ni future ; l’enregistrement peut être corrigé tant que le programme n’est pas affiché.

- Une tentative d’affichage d’un programme non validé ou non signé est refusée côté serveur ; le contrôle est porté en base.

- Le passage à l’état affiché est journalisé avec son auteur et sa date. Le programme affiché porte la mention de sa validation et de sa signature.

| **US-VAL-05** | **Consulter les programmes et l’historique des validations** | **Should** | 5 pts | BF-VAL-05, BF-VAL-03 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule pédagogique ou planification, je veux retrouver les programmes de toutes les semaines et l’historique de leur circuit, afin de suivre les échanges entre cellules.*

**Réestimée de 3 à 5 points en version 10** : elle reçoit la liste des programmes toutes semaines confondues. Le critère 4 d’US-VAL-03 supposait une liste et une fiche de programme qu’aucune story ne portait ; la consultation de la semaine en tient lieu depuis le sprint 3.

**Critères d’acceptation :**

- Une liste présente les programmes de toutes les semaines, avec leur état, filtrable par état et par période, et donne accès à chaque programme.

- Chaque changement d’état est présenté avec son auteur, sa date et son motif éventuel.

- L’historique est consultable depuis le programme.

- Les cycles de rejet et de resoumission successifs sont visibles dans l’ordre chronologique.

# **9. Epic E7 — Évaluations**

Cet epic couvre les **deux** circuits d’évaluation identifiés lors de l’entretien avec la cellule examens — formative et certificative —, ainsi que les exigences de confidentialité qui les accompagnent. *La version 9 annonçait trois circuits : correction de terrain du 25 août, jamais reportée dans cette introduction.*

| **US-EVAL-01** | **Créer une évaluation selon son type** | **Must** | 5 pts | BF-EVAL-01 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule examens, je veux créer une évaluation rattachée à un module du référentiel en précisant son type et son périmètre, afin que le circuit approprié lui soit appliqué.*

**Critères d’acceptation :**

- Deux types sont proposés : **formative** — contrôle, également appelé examen partiel — et **certificative** — examen final. Aucun troisième type n’existe.

- Une évaluation porte sur un seul module du référentiel de la formation concernée, et sur un périmètre explicite : une brigade, ou la session entière. Exactement un des deux rattachements est renseigné ; la contrainte est portée en base.

- Le type propose un périmètre par défaut — brigade pour la formative, session pour la certificative — que la cellule examens peut modifier avant l’enregistrement. Un périmètre session donne lieu à un avertissement rappelant que le sujet sera commun aux brigades.

- Une évaluation formative datée du jour ou d’une date future insère une séance verrouillée au programme de la semaine, soumise aux contraintes dures ; un créneau occupé est refusé avec son motif. La séance est signalée comme un contrôle dans le programme.

- Une évaluation formative peut être déclarée après coup, à une date passée, par exception et avec un motif obligatoire ; elle ne donne alors lieu à aucune séance.

- Une évaluation certificative porte une date ni passée ni hors des bornes de la session, et ne donne lieu à aucune séance.

- Le type détermine les champs obligatoires et les actions disponibles : sujets et organisation matérielle pour la certificative, sujet unique pour la formative.

- Le type et le périmètre ne sont plus modifiables après création ; une erreur se corrige par suppression et recréation, possible tant que l’évaluation n’est ni organisée ni dotée d’un sujet retenu.

| **US-EVAL-02** | **Saisir la date d’un examen final** | **Must** | 2 pts | BF-EVAL-02 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule examens, je veux enregistrer la date d’examen final fixée par le 3ᵉ bureau, afin qu’elle s’impose au calendrier.*

**Critères d’acceptation :**

- La date d’une évaluation certificative est identifiée partout comme imposée par le 3ᵉ bureau. Le système la subit : il n’en propose ni n’en conteste l’opportunité.

- Seule la cellule examens la modifie. Toute modification exige un motif mentionnant la notification du 3ᵉ bureau, et est journalisée avec l’ancienne et la nouvelle date. Un examen dont la date est passée ne change plus de date.

- Le jour d’examen est fermé à la programmation pour les brigades du périmètre, y compris une brigade constituée après la saisie. Ce blocage est obtenu par projection de la date de l’évaluation, sans création de période au calendrier : la date n’existe qu’à un seul endroit.

- Les séances déjà programmées sur ce jour pour ces brigades sont signalées à la saisie et à chaque modification de la date. Elles ne sont jamais supprimées d’office.

- Le jour d’examen apparaît sur les vues annuelle et mensuelle du calendrier.

| **US-EVAL-03** | **Enregistrer les sujets transmis et sélectionner celui retenu** | **Must** | 5 pts | BF-EVAL-03 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule examens, je veux enregistrer les sujets que l’instructeur m’a transmis hors système puis la décision de la commission sur celui retenu, afin de limiter les risques de divulgation.*

**Critères d’acceptation :**

- L’instructeur ne dispose d’aucun accès au système : les sujets sont transmis hors système et saisis par la cellule examens.

- Le système n’enregistre qu’une **référence** de chaque sujet, jamais son contenu.

- Une évaluation certificative porte au plus deux sujets, dont un seul est retenu ; ces deux limites sont garanties en base. Une évaluation formative porte un sujet unique, sans mécanisme de sélection.

- Le sujet retenu est une décision de la commission d’examen, acteur extérieur au système : la cellule examens l’enregistre, horodatée et rattachée à l’agent qui la saisit. Une certificative dotée d’un seul sujet admet une sélection après avertissement et confirmation explicite.

- Le changement du sujet retenu est admis avant l’épreuve, avec un motif mentionnant la décision de la commission ; à partir du jour de l’épreuve, la sélection et son changement sont refusés.

- Les sujets ne sont accessibles qu’à la cellule examens, sur un écran dédié refusé à tout autre profil, Direction de Formation comprise. Chaque consultation est journalisée, et le journal désigne un sujet par son rang, jamais par sa référence.

- Une épreuve peut être organisée avant la sélection du sujet ; elle n’est **prête** qu’avec un sujet retenu. *La version 9 interdisait d’organiser sans sujet sélectionné : appliquée à la lettre, la règle obligeait à arrêter le sujet dès la réservation des salles et allongeait d’autant la période d’exposition au risque de divulgation, contre l’objet même de la story.*

| **US-EVAL-04** | **Organiser une épreuve** | **Must** | 5 pts | BF-EVAL-04 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule examens, je veux organiser matériellement une épreuve certificative, afin qu’elle se déroule dans de bonnes conditions.*

**Critères d’acceptation :**

- L’épreuve porte un créneau horaire unique dans sa date, commun à toutes les brigades : l’épreuve est simultanée.

- Pour chaque brigade du périmètre, l’organisation affecte un ou plusieurs lieux, chacun avec l’effectif attendu de la brigade qui y compose et ses surveillants. Une épreuve pratique peut se tenir sans lieu ; ses surveillants restent obligatoires.

- Un lieu affecté est disponible sur le créneau — ni indisponible, ni occupé par une séance, ni par une autre épreuve — et de capacité suffisante ; un refus nomme l’occupant ou l’écart de capacité.

- Un surveillant est soit un instructeur référencé, soit une personne extérieure au système désignée par son seul nom. Le contrôle de disponibilité ne s’applique qu’aux surveillants référencés.

- Une fois l’épreuve organisée, ses lieux et ses surveillants référencés sont fermés à la programmation des séances sur le créneau.

- L’organisation se saisit par étapes. Elle est **complète** lorsque chaque brigade du périmètre est organisée, que la somme des effectifs attendus égale son effectif réel et que chaque lieu a ses surveillants ; l’épreuve est **prête** lorsqu’elle est complète et dotée d’un sujet retenu. Ces deux états sont calculés : une radiation de stagiaire rend une organisation incomplète.

- L’organisation est modifiable jusqu’au début de l’épreuve. Un changement de date imposé par le 3ᵉ bureau revérifie l’organisation et en signale les conflits, sans être refusé.

- Une convocation récapitulative est consultable et imprimable, lisible par la Direction de Formation ; elle ne porte aucune mention de sujet.

| **US-EVAL-05** | **Saisir et vérifier les notes** | **Must** | 5 pts | BF-EVAL-05 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule examens, je veux saisir les notes des stagiaires, afin de constituer les résultats de la formation.*

**Critères d’acceptation :**

- La saisie s’effectue par évaluation, pour l’ensemble des stagiaires du périmètre de l’évaluation — brigade ou session —, tels qu’enregistrés dans la session.

- Une note est comprise entre zéro et la note maximale définie pour l’évaluation.

- Une note absente est distinguée d’une note nulle.

- Une double vérification est proposée avant enregistrement définitif.

- Toute modification ultérieure d’une note est journalisée avec sa valeur précédente.

- Seule la cellule examens accède à la saisie des notes. Les notes sont des données sensibles : leur consultation est journalisée.

*Note v10 : le premier critère visait « la brigade concernée » ; depuis la version 7, une évaluation peut porter sur la session entière. Le dernier critère reprend l’exigence BNF-02 du cahier des charges, que le backlog ne citait pas.*

| **US-EVAL-06** | **Calculer moyennes et classement** | **Must** | 5 pts | BF-EVAL-06 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule examens, je veux que le système calcule les moyennes et le classement, afin d’établir les résultats sans calcul manuel.*

**Critères d’acceptation :**

- La moyenne par stagiaire est calculée selon les coefficients définis par matière au référentiel de sa formation.

- Le coefficient d’un module est propre au couple formation-matière : la même matière peut porter des coefficients différents dans deux formations.

- Un second niveau de pondération s’applique à l’intérieur d’un module : le poids de chaque type d’évaluation dans la note du module.

- Les deux niveaux de coefficients sont paramétrables sans modification du code.

- Le classement est établi au niveau de la session, tous stagiaires confondus. Le rang au sein de la brigade demeure calculable si le procès-verbal le demande.

- Les cas d’égalité sont traités selon une règle explicite et documentée.

- Une note manquante empêche le calcul et est signalée.

| **US-EVAL-07** | **Générer les procès-verbaux de résultats** | **Must** | 5 pts | BF-EVAL-07 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule examens, je veux générer le procès-verbal des résultats, afin de disposer du document officiel de sanction de la formation.*

**Critères d’acceptation :**

- Le procès-verbal de fin de formation, unique pour la session (RG-59 bis), présente la liste des stagiaires de toutes ses brigades, leurs moyennes, leur rang et leur décision. Sa génération exige que toutes les notes soient complètes ; les manquants sont énumérés par module et par brigade.

- La décision distingue les admis des ajournés selon un seuil paramétrable, 10 sur 20 par défaut.

- Le procès-verbal d’une évaluation présente, pour chaque stagiaire de son périmètre, la note de cette seule évaluation — sur sa note maximale et ramenée sur 20 —, l’absence le cas échéant et le rang. Il ne porte aucune décision d’admission.

- La génération d’un procès-verbal verrouille les notes qu’il porte.

- Le document est exportable dans un format imprimable.

- La génération est journalisée avec auteur et date.

- Un procès-verbal généré ne peut être modifié ; toute correction donne lieu à une nouvelle version.

*Note v11 : la version 10 ne distinguait pas les deux documents de la fiche CU-P6-07. La décision d’admission sanctionne la formation et n’existe qu’au procès-verbal de fin de formation (décision D-277).*

| **US-EVAL-08** | **Gérer les sessions de rattrapage** | **Should** | 3 pts | BF-EVAL-08 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule examens, je veux organiser les rattrapages des stagiaires ajournés, afin de leur permettre de valider leur formation.*

**Critères d’acceptation :**

- Les stagiaires ajournés sont identifiés automatiquement à partir des résultats.

- Une session de rattrapage est créée pour une ou plusieurs matières.

- Les notes de rattrapage sont saisies séparément des notes de première session.

- La règle de prise en compte de la note de rattrapage est paramétrable.

- Les résultats après rattrapage font l’objet d’un procès-verbal distinct.

| **US-EVAL-09** | **Archiver les résultats** | **Should** | 3 pts | BF-EVAL-09 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule examens, je veux archiver les résultats et procès-verbaux, afin de respecter les obligations de conservation.*

**Critères d’acceptation :**

- Les résultats d’une formation achevée sont archivés en bloc.

- Les données archivées restent consultables mais ne sont plus modifiables.

- L’accès aux archives est restreint à la cellule examens et journalisé.

- La date d’archivage et son auteur sont enregistrés.

| **US-EVAL-10** | **Gérer les tests d’admission aux stages** | **Could** | 8 pts | BF-EVAL-10 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule examens, je veux gérer les tests d’admission aux stages, afin de sélectionner les candidats sur des critères tracés.*

**Critères d’acceptation :**

- Un candidat au test est enregistré sans être stagiaire du centre.

- Une session de test comporte des épreuves, une date et un seuil d’admission.

- Les notes des candidats sont saisies et la décision d’admission calculée selon le seuil.

- La liste des admis est exportable.

- Un candidat admis peut être converti en stagiaire d’une formation.

| **US-EVAL-11** | **Suivre les épreuves à venir** | **Should** | 3 pts | BF-EVAL-03, BF-EVAL-04 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule examens, je veux voir d’un coup d’œil quelles épreuves à venir ne sont pas prêtes, afin de traiter les retards avant le jour de l’épreuve.*

**Story nouvelle en version 10.** Elle recueille deux signalements reportés à la livraison d’US-EVAL-04, faute de place dans son estimation. US-EVAL-04 calcule déjà la complétude et l’état « prêt » au détail de chaque évaluation ; la présente story les porte dans la liste.

*Note v11 : les reports D-215 (badge de liste sur la complétude) et D-212 (mention « à vérifier » après un changement de date) sont exactement ses critères 1 et 2. Signalés « orphelins » à la clôture du sprint 4, ils sont en réserve avec elle.*

**Critères d’acceptation :**

- La liste des épreuves à venir indique pour chacune si elle est complète et si elle est prête, d’après les règles d’US-EVAL-04.

- Une épreuve dont la date a changé après sa dernière organisation porte la mention « à vérifier », jusqu’à une nouvelle vérification de l’organisation.

- La liste est filtrable sur les épreuves non prêtes.

- L’affichage de la liste ne consulte aucun sujet et ne crée aucune entrée de consultation des sujets.

# **10. Epic E8 — Suivi et traçabilité**

Cet epic répond à la limite de traçabilité identifiée dans l’analyse de l’existant : le rapprochement entre ce qui est prescrit et ce qui est effectivement dispensé.

| **US-SUI-01** | **Consulter le rapprochement prescrit et réalisé** | **Must** | 5 pts | BF-SUI-01 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule pédagogique, je veux comparer le volume prescrit et le volume réalisé par brigade et par matière, afin de vérifier la conformité de la formation dispensée.*

**Critères d’acceptation :**

- Pour chaque brigade et chaque matière du référentiel, trois volumes sont présentés : prescrit, programmé et réalisé.

- Le volume réalisé est calculé à partir des séances des programmes affichés, diminué du volume des séances déclarées non exécutées au titre de US-SUI-05. Une séance portant un avenant compte au réalisé.

- L’écart est exprimé en heures et en pourcentage.

- La vue est filtrable par formation, par session, par brigade et par période.

- Les données sont consultables par la cellule pédagogique, la cellule planification, la cellule examens et la Direction de Formation, conformément à la matrice d’habilitation.

*Note v11 : la version 10 omettait la planification et les examens ; la matrice d’habilitation fait foi (décision D-265, écart 2 du sprint 4).*

- L’affectation d’un stagiaire à une brigade signale le volume déjà dispensé à cette brigade.

- Le prérequis d’une matière est réputé achevé lorsque son volume **réalisé** atteint le volume prescrit. Jusqu’à cette story, la définition provisoire repose sur le volume programmé ; la présente story la remplace.

| **US-SUI-02** | **Être alerté des écarts significatifs** | **Should** | 3 pts | BF-SUI-02 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule pédagogique, je veux être alerté lorsqu’un écart devient significatif, afin d’intervenir avant la fin de la formation.*

**Critères d’acceptation :**

- Un seuil d’alerte est paramétrable, exprimé en pourcentage du volume prescrit.

- Les matières dépassant le seuil apparaissent dans une liste d’alertes.

- L’alerte distingue les retards des dépassements.

- L’alerte disparaît lorsque l’écart repasse sous le seuil.

- En cours de session, le retard se mesure par rapport au volume programmé déjà échu, soit les séances terminées des programmes affichés ; à la fin de la session, par rapport au volume prescrit. Le dépassement se mesure toujours par rapport au prescrit, et reste signalé même lorsque les contraintes dures le rendent normalement impossible.

- Le nombre d’alertes est visible dans la navigation de la cellule pédagogique.

*Note v11 : sans référence échue, toute matière en cours paraîtrait en retard. L’alerte porte sur le volume **réalisé**, l’indicateur d’US-PLAN-07 sur le volume **programmé**, par une seule fonction de statut (décisions D-282 et D-283).*

| **US-SUI-03** | **Consulter le tableau de bord des formations** | **Should** | 5 pts | BF-SUI-03 |
| --- | --- | --- | --- | --- |

*En tant que membre de la Direction de Formation, je veux consulter l’avancement des brigades en cours de formation, afin de disposer d’une vision d’ensemble.*

**Critères d’acceptation :**

- Le tableau de bord présente pour chaque brigade en cours — brigade d’une session non clôturée dont la période couvre la date du jour — son taux d’avancement horaire, rapport du volume réalisé au volume prescrit.

- Le nombre de matières achevées, en cours et non commencées est indiqué. Une matière est achevée lorsque son volume réalisé atteint le volume prescrit, selon la règle même du prérequis achevé.

- Les brigades présentant des alertes sont mises en évidence.

- L’accès est ouvert aux profils qui lisent le suivi selon la matrice d’habilitation : Direction de Formation, cellules pédagogique, planification et examens.

*Note v11 : même correction que le critère 5 d’US-SUI-01 (décision D-284).*

| **US-SUI-04** | **Exporter les données de suivi** | **Could** | 3 pts | BF-SUI-04 |
| --- | --- | --- | --- | --- |

*En tant que membre de la Direction de Formation, je veux exporter les données de suivi aux formats CSV et PDF, afin de les retraiter ou de les diffuser.*

**Critères d’acceptation :**

- Les données du tableau de bord sont exportables au format CSV pour retraitement.

- Une version PDF mise en page est disponible pour diffusion.

- L’export respecte les filtres appliqués à l’écran.

- L’export est journalisé.

| **US-SUI-05** | **Déclarer la non-exécution d’une séance** | **Must** | 2 pts | BF-SUI-05 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule planification, je veux déclarer qu’une séance planifiée n’a pas été exécutée, afin que le volume réalisé reflète ce qui a effectivement été dispensé.*

**Critères d’acceptation :**

- Une séance appartenant à un programme affiché est réputée exécutée par défaut : seule la non-exécution se déclare.

- La déclaration porte sur une séance passée et comporte un motif obligatoire. Pour une séance regroupée, elle porte sur la ligne d’une brigade, une seule brigade pouvant avoir manqué la séance.

- Le volume de la séance déclarée non exécutée est retranché du volume réalisé de la matière pour la brigade concernée.

- La déclaration est réversible tant que la session n’est pas clôturée. Après la clôture, ni la déclaration ni l’annulation ne sont admises.

- La déclaration est journalisée avec son auteur et son horodatage.

- La saisie relève de la cellule planification, sur signalement de l’instructeur ou du chef de module.

| **US-SUI-06** | **Éditer la progression réalisée hebdomadaire** | **Must** | 3 pts | BF-SUI-06 |
| --- | --- | --- | --- | --- |

*En tant que membre de la cellule planification, je veux éditer en fin de semaine un document de progression réalisée, afin de rendre compte de ce qui a effectivement été dispensé.*

**Critères d’acceptation :**

- Le document présente, pour chaque brigade et chaque matière, le volume programmé de la semaine et le volume effectivement dispensé.

- Il détaille les écarts : séances non exécutées avec leur motif, séances reportées, avenants portés en cours de semaine avec leur nature et leur motif.

- Une séance reportée puis tenue n’apparaît pas comme un écart : le volume réalisé est inchangé. Une séance reportée est une séance déplacée au sein de sa semaine par un avenant de nature « déplacement » ; un report vers une autre semaine se lit comme une non-exécution suivie d’une séance ajoutée la semaine suivante. Aucune entité « report » n’existe.

- L’édition est refusée pour une semaine dont le programme n’est pas affiché. Plusieurs éditions d’une même semaine sont conservées, la plus récente fait foi.

- Le document est intégralement calculé ; aucune donnée n’y est saisie deux fois.

- Le système enregistre la date d’édition et l’agent qui l’a produit ; s’il est signé, la date et le nom du signataire sont enregistrés.

- Le document est produit à partir d’un gabarit paramétrable.

*Note v11 : le vocabulaire de la « séance reportée » est précisé pour que le mémoire ne laisse pas supposer une classe qui n’existe pas (écart 3 du sprint 4).*

# **11. Hors backlog**

## **11.1 Travaux techniques du sprint 4 — état à la clôture**

Ces travaux ne sont pas des user stories : ils ne produisent aucun résultat démontrable à une cellule. Tous sont clos à la clôture du sprint 4.

| **Travail** | **Origine** | **État au 23 octobre 2026** |
| --- | --- | --- |
| Ordre de verrouillage du traitement en lot | Problème P-42 | **Corrigé** en ouverture du sprint 4 : tri par programme avant l’écriture, test de reproduction |
| Stabilité de la suite de tests | Revue du sprint 3 | **Mesurée** : cinq exécutions complètes consécutives, aucun échec. La cause des échecs antérieurs est établie — deux exécutions concurrentes sur la même base (P-51) — et bloquée par un verrou |
| Présélection de la génération | Écart 25 du sprint 3 | **Mesurée, non modifiée** (D-290) : une candidate inutile, aucune requête supplémentaire. Dette assumée, sans échéance |
| Impression du programme hebdomadaire | Décision D-155 | **Exemplaire produit** (D-291) : le programme déborde de la page A4 dès le troisième créneau. Traité en phase 6 comme anomalie de recette, et non comme story |
| Relation facultative séance ↔ créneau type (RG-64) | Décision D-133 | **Limite consignée** (D-288) : aucun comportement observable n’en dépend |

## **11.2 Hors périmètre de la version courante (Won’t)**

| **Élément** | **Origine** | **Motif** |
| --- | --- | --- |
| Mesure de l’écart de progression entre les brigades d’une même session, à la création d’une évaluation de périmètre session | Fiche CU-P6-01, E2 ; décision D-182 | Aucun livrable ne définit la mesure ni le seuil. Un avertissement systématique, non bloquant, est en place depuis US-EVAL-01. Perspective d’évolution, à reprendre si le terrain fixe un critère. Le report D-182 est fermé par ce classement |
| Séparation de l’application en un front-end et un back-end distincts, communiquant par une interface de programmation | Demande de l’encadrant pendant le sprint 4 ; maintien de l’architecture validé par l’encadrant le 22 octobre 2026 | Déploiement hors ligne, réduction de la surface d’exposition des notes et des sujets, calendrier restant. La couche de services, indépendante de l’interface, est le point d’appui d’une évolution vers une interface de programmation : à présenter comme telle au mémoire, à la demande de l’encadrant |

## **11.3 Annexe historique — proposition de découpage de la phase 2**

| **Statut — PÉRIMÉE, conservée pour l’historique** Le découpage en cinq sprints proposé en phase 2 a été remplacé dès la phase 3 par le découpage en quatre sprints et une réserve arrêté au classeur de pilotage et au WBS, seul document de référence pour l’ordonnancement. Il figure dans les versions archivées 5 à 9 de ce backlog et n’est plus reproduit ici. |
| --- |

# **12. Modalités de mise à jour**

Ce backlog constitue un artefact vivant et l’unique source de vérité du périmètre à réaliser.

- **À chaque sprint planning** : sélection des stories, découpage en tâches techniques, estimation affinée si nécessaire.

- **À chaque revue de sprint** : clôture des stories terminées, réévaluation des priorités, ajout des stories nouvellement identifiées, report des écarts consolidés.

- **Toute correction annoncée dans un encadré d’évolution est vérifiée à sa destination**, critère par critère, avant la diffusion de la version. Mesure ajoutée en version 10, après la découverte de deux corrections de la version 7 annoncées et jamais portées.

- **Affinage progressif** : les critères d’acceptation des stories du sprint suivant sont revus et complétés avant chaque planification.

- **Copie dans le dépôt** : chaque version est déposée dans le dépôt de développement, pour que la traçabilité critère → test s’établisse sur le texte intégral des critères. Mesure ajoutée en version 11 : à la clôture du sprint 4, la matrice de traçabilité a dû reconstituer les critères à partir des noms de tests, faute de backlog dans le dépôt.

- **Version unique** : toute modification donne lieu à une nouvelle version datée remplaçant la précédente. Aucune version parallèle ne doit circuler.

*Artefact vivant — version 11 du 23 octobre 2026. Remplace la version 10 du 10 octobre 2026. Intègre la clôture du sprint 4, le jalon J3, les seize écarts entre livrables du sprint 4 et la validation du maintien de l’architecture par l’encadrant.*
