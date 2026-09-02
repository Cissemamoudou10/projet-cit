**DOSSIER DE CONCEPTION CONSOLIDÉ**

Synthèse de la phase 4 · Système de gestion des activités de formation du CIT

*Document de revue — Jalon J1 · Version 1 du 30 août 2026 · Lot WBS 4.5.1*

# 1. Objet de ce dossier

Ce document est présenté à la **revue de conception**, jalon J1, qui conditionne l'autorisation de passage au développement. Il ne remplace aucun des six livrables de la phase : il en donne la synthèse, expose les décisions structurantes avec leur origine, et énonce ce qui reste ouvert.

Il s'adresse à l'encadrant académique et au commanditaire, et sert de point d'entrée à la lecture des livrables détaillés.

**La décision attendue** est l'autorisation d'ouvrir le sprint 1 le 31 août. La section 9 en énonce les conditions.

# 2. Le projet en une page

| | |
| --- | --- |
| **Objet** | Système web unifié de gestion des activités de formation pour la Direction de Formation du CIT |
| **Binôme** | Lieutenant Mamoudou Cissé · Lieutenant Modibo Amadagaly Niangaly |
| **Commanditaire** | Colonel Janati Idrissi |
| **Périmètre** | Trois cellules : pédagogique, planification, examens |
| **Contrainte majeure** | Réseau interne militaire, aucune dépendance en ligne à l'exécution |
| **Dépôt du mémoire** | 5 décembre 2026, échéance externe non négociable |

**Six objectifs SMART.** Centraliser le référentiel de formation (OS1). Assister la génération du programme hebdomadaire (OS2). Gérer les évaluations et leurs circuits (OS3). Assurer la traçabilité entre le prescrit et le réalisé (OS4). Réduire d'au moins la moitié le temps de construction du programme (OS5). Suggérer un remplaçant en cas d'indisponibilité (OS6).

# 3. Ce que la phase 4 a produit

Six livrables, **177 pages**, **23 figures** produites en PlantUML et versionnées comme texte dans le dépôt.

| Livrable | Contenu | Version |
| --- | --- | --- |
| Cas d'utilisation détaillés | 57 cas d'utilisation, 65 règles métier, 6 diagrammes | v4 du 30/08 |
| Diagrammes de séquence | 4 scénarios principaux | v3 du 30/08 |
| Diagramme de classes du domaine | 30 classes, 12 énumérations, 5 vues thématiques | v4 du 30/08 |
| Note de choix d'implémentation | Traduction en schéma PostgreSQL | v3 du 30/08 |
| Dossier d'architecture | Architecture en couches, déploiement, choix documentaire | v2 du 30/08 |
| Maquettes | 5 wireframes des écrans structurants | v2 du 30/08 |

**Le modèle en chiffres.** 30 classes dont 2 classes d'association, 12 énumérations, 9 attributs dérivés jamais stockés, 6 contraintes portées en base et 7 en couche services, 65 règles métier numérotées dont 25 marquées structurantes.

**La démarche.** UML de bout en bout : le diagramme de classes tient lieu de modèle conceptuel unique, sans MCD ni MLD Merise. Le niveau logique est traité par une note de justification, non par un second modèle. Ce choix évite de maintenir deux représentations concurrentes d'un domaine qui a connu neuf itérations.

# 4. Ce que la phase a révélé

C'est le point le plus important de ce dossier, et il mérite d'être énoncé sans détour : **la phase 4 n'a pas seulement formalisé un modèle, elle l'a corrigé en profondeur.**

Sept échanges avec le chef de bureau pédagogique et l'analyse de **quatre progressions d'instruction réelles** — celles des 23, 24 et 25 février et du 7 mai 2026 — ont invalidé neuf points structurels issus des phases précédentes.

| Ce que les phases 1 à 3 tenaient pour acquis | Ce que le terrain a établi |
| --- | --- |
| Le programme est celui d'une brigade pour une semaine | Il couvre **le centre entier**. L'impression par journée est un format de sortie |
| Validation pédagogique puis affichage | Validation, puis **signature du directeur de la formation**, puis affichage |
| Trois types d'évaluation | **Deux** : formative et certificative. L'examen partiel est le contrôle sous un autre nom |
| Une évaluation porte sur une brigade | Son **périmètre est explicite** : une session ou une brigade, selon le sujet |
| Deux sujets pour tout examen | Deux pour le certificatif, **un seul** pour le formatif |
| La cellule examens choisit le sujet retenu | Une **commission d'examen** le choisit ; la cellule enregistre |
| Le classement s'établit au sein de la brigade | Au niveau de **la session**, tous stagiaires confondus |
| Une période de calendrier vise une cible | Elle vise **plusieurs sessions et plusieurs brigades**, indépendamment |
| La salle attitrée est choisie par la pédagogique | Par la **cellule planification**, détentrice du catalogue des lieux |

**Trois notions sont apparues** qui ne figuraient dans aucun document antérieur. La **grille horaire** et ses créneaux types, révélés par la comparaison de deux progressions aux horaires différents — l'horaire ordinaire et celui du Ramadan. La **déclaration de non-exécution**, qui referme l'objectif OS4. Et l'**avenant**, qui permet d'ajuster un programme affiché sans annuler la validation de toute la semaine.

**Une notion a été supprimée.** La modalité d'enseignement, introduite pour rendre licite un volume nul dans le cas du projet de fin d'études. Le terrain a établi que le PFE est un module enseigné comme les autres, avec volume horaire décompté à chaque apparition dans la progression. Sans cas d'usage, l'attribut a été retiré.

**Ces corrections sont intervenues avant tout développement.** Découvertes au sprint 4, elles auraient coûté une réécriture du modèle de données, une migration et une reprise des écrans. C'est le bénéfice direct d'une phase de conception menée avec le terrain plutôt que sur documents.

# 5. Les décisions structurantes

Neuf décisions gouvernent le modèle. Leur remise en cause l'invaliderait.

**Le référentiel appartient à la formation, jamais à la brigade.** Toutes les brigades d'une session suivent le même référentiel ; seul l'ordre de déroulement diffère. Le couple formation-matière est une **classe d'association** portant le volume prescrit, le coefficient, la catégorie de lieu requise et les deux poids d'évaluation. C'est le pivot du modèle, référencé par les séances, les évaluations et le suivi.

**Le décalage des progressions entre brigades est une contrainte à préserver**, non une anomalie à corriger. Il sert l'optimisation de l'emploi des instructeurs, et le générateur ne doit jamais chercher à l'aligner.

**La séance se distingue de la ligne de programme.** La séance est l'événement d'enseignement ; la ligne rattache une séance à une brigade. Une séance regroupée porte plusieurs lignes : la charge de l'instructeur n'est comptée qu'une fois, le volume l'est pour chaque brigade. Sans cette distinction, la charge serait surévaluée et le générateur verrait un conflit là où il n'y en a pas.

**La résolution de la génération est centre-entier.** La sélection est libre — une session ou plusieurs — mais la résolution tient compte des affectations de toutes les sessions actives. Sans cette portée, l'unicité d'affectation de l'instructeur n'est pas vérifiable et le programme obtenu dépend de l'ordre de traitement des sessions.

**Aucun affichage sans validation pédagogique et signature du directeur.** C'est la règle centrale de la validation croisée et le cœur de la valeur ajoutée organisationnelle : la planification élabore, la pédagogique valide, le directeur signe.

**Après affichage, l'ajustement porte un avenant**, sans faire retomber le programme à brouillon. Le programme couvrant le centre, une absence sur une seule séance aurait sinon annulé la validation de toute la semaine et exigé une nouvelle signature — procédure qui aurait été contournée dès la première semaine.

**La constatation se fait par exception.** Une séance d'un programme affiché est réputée exécutée ; seule la non-exécution se déclare, avec motif. Une constatation systématique aurait représenté une vingtaine de saisies hebdomadaires par brigade pour signaler deux anomalies.

**La grille horaire active est désignée, non déduite.** Le passage à l'horaire de Ramadan est une décision de commandement, non une conséquence d'une date. La grille contraint ce que la génération propose, jamais ce que la saisie manuelle décide.

**Trois grandeurs sont dérivées et ne sont jamais stockées** : le volume restant d'une matière, l'écart entre prescrit et programmé, la charge d'un instructeur. Les stocker créerait trois occasions de divergence entre une valeur enregistrée et la réalité qu'elle prétend décrire.

# 6. Architecture et implémentation

**Trois couches, dépendances strictement descendantes.** Présentation, services, domaine. Aucune couche n'appelle celle du dessus. Aucune règle métier dans la présentation : une règle qui ne vit que dans un formulaire est contournée dès qu'une donnée entre par un autre chemin.

**Sept applications Django** — six portant les entités métier, une technique sans entité propre. Leur ordre de dépendance est exactement celui du découpage en sprints arrêté en phase 3, ce qui confirme que le découpage de réalisation suit la structure du domaine.

**La couche services systématique trouve sa justification a posteriori.** Sur treize contraintes recensées, six descendent en base et **sept ne le peuvent pas** : acyclicité d'un graphe, conditionnalité au type, comparaison à une grandeur dérivée, exception du regroupement, portée dérivée, agrégat, unicité remontant trois niveaux de relations. Sans couche services, elles seraient dispersées entre vues et formulaires, avec la certitude de divergences.

**Une implantation unique des contraintes dures.** Le service de contrôle est appelé par la génération, la modification manuelle, le regroupement et la duplication. Un programme généré et un programme saisi obéissent aux mêmes règles.

**Deux décisions techniques tranchées.** La bibliothèque de génération documentaire est **WeasyPrint**, retenue parce que le gabarit y est une donnée — un modèle Django et une feuille de style — et non du code : un écart de format réglementaire ne coûte qu'un changement de gabarit. Repli sur ReportLab si ses dépendances natives résistent au test hors ligne du 12 septembre. Et les **habilitations reposent sur les groupes et permissions Django**, configurables par l'administrateur sans modification du code.

# 7. Traçabilité

La chaîne est établie et vérifiable de bout en bout :

`OSn → BF-xxx → US-xxx → CU-Pn-xx → RG-xx → SEQ-xx → CLS-xx`

Les 59 besoins fonctionnels du cahier des charges v6 sont couverts par 57 cas d'utilisation ; les deux besoins sans cas d'utilisation sont des exigences transversales, traitées par une règle métier et par un diagramme d'états.

**Trois ruptures subsistent, et nous les signalons plutôt que de les laisser découvrir.**

| Élément | Manque | Origine |
| --- | --- | --- |
| Gestion des grilles horaires | Ni besoin ni user story | Notion révélée par les progressions d'instruction, postérieurement au cahier des charges |
| Édition de la progression réalisée | Ni besoin ni user story | Révélée par l'échange de terrain du 26 août |
| BF-SUI-05, déclaration de non-exécution | Besoin créé, fiche de cas d'utilisation manquante | Créé en v6 du cahier des charges |

Ces trois manques procèdent d'une même cause : le terrain a livré des informations après la clôture de la phase 2. **Ils seront refermés avant le sprint 2** dans le cahier des charges v7, le backlog v7 et une version 5 des cas d'utilisation. Estimation cumulée : 8 points, tous en priorité Must.

Nous n'avons pas modifié le backlog pendant la phase 4, conformément à la consigne de l'encadrant académique du 26 août.

# 8. Risques et points ouverts

## 8.1 Évolution des risques

| Réf. | Objet | Évolution |
| --- | --- | --- |
| **R6** | Dérive de l'optimisation sous contraintes | **6 → 9, élevé.** La résolution centre-entier multiplie les variables de décision par le nombre de sessions simultanées |
| **R18** | Format réglementaire des documents jamais communiqué | **Créé, coté 6.** Le format de la progression d'instruction est désormais connu ; celui du procès-verbal et de la convocation ne l'est pas |
| R9 | Échec de l'installation hors ligne | Inchangé. Le choix de WeasyPrint y ajoute une dépendance native ; test au jalon C1 |
| R2 | Écart entre besoins et fonctionnalités | Inchangé, mais le dispositif de prévention a démontré son efficacité : neuf corrections avant tout développement |

**Le traitement de R6 est engagé.** Le prototype exploratoire du solveur démarre à l'ouverture du sprint 1 et sera **dimensionné sur plusieurs sessions simultanées** : validé sur une seule, il attesterait d'une faisabilité qui n'est pas celle du système réel. Le repli heuristique demeure inscrit aux critères d'acceptation et l'optimisation reste de priorité Should : le système livré ne dépend pas de l'issue de ce risque.

## 8.2 Questions de terrain encore ouvertes

Trois, aucune bloquante pour le développement. Le document de fin de semaine est-il signé, et transmis à qui ? Le remplacement en urgence exige-t-il l'accord du directeur à chaque cas, ou seulement à la consolidation ? Un cours manqué est-il replacé ou seulement noté — l'hypothèse retenue offrant les deux possibilités, une réponse contraire ne ferait que retirer une option.

## 8.3 Décisions de conception assumées

Huit choix n'ont pas été validés par le terrain et sont signalés comme tels : la fusion des indisponibilités qui se chevauchent, le non-rétablissement des remplacements après annulation d'une indisponibilité, le refus de retirer une qualification utilisée, l'avertissement plutôt que le blocage sur un sujet unique, les paramètres de verrouillage de compte, le rattachement des objectifs pédagogiques, l'avenant non soumis à validation, et le caractère facultatif de la capacité d'un lieu.

Ils sont défendables un par un, et le sont d'autant mieux qu'ils sont énoncés.

## 8.4 Périmètre à clarifier

Le programme est affiché sur un écran devant la direction de la formation. Le cahier des charges exclut le portail de consultation pour instructeurs et stagiaires ; un affichage public en lecture seule n'est pas un portail, mais la frontière doit être tracée explicitement.

# 9. Ce que la revue doit décider

**La décision principale :** autoriser l'ouverture du sprint 1 le 31 août.

Les conditions en sont réunies. Le modèle de données est verrouillé et n'a plus de question ouverte l'affectant. L'architecture est arrêtée, les choix technologiques tranchés. Les six livrables sont cohérents entre eux, ce qu'un contrôle outillé a vérifié sur trois critères — vocabulaire, règles métier, synchronisation des figures.

**Trois points sur lesquels nous souhaitons un avis.**

Le report des mises à jour documentaires des phases antérieures après la revue est-il acceptable ? Nous avons délibérément gardé la cohérence *au sein* de la phase 4 plutôt que de propager les corrections en continu vers le cahier des charges et le backlog, pour ne pas écrire deux fois les mêmes choses.

Le relèvement de R6 à 9 appelle-t-il une mesure supplémentaire ? Nous estimons que le prototype dimensionné et le repli heuristique suffisent.

Le traitement des trois ruptures de traçabilité avant le sprint 2, plutôt qu'immédiatement, est-il tenable ?

# 10. Suite immédiate

| Échéance | Objet |
| --- | --- |
| 31 août | Ouverture du sprint 1 · démarrage du prototype du solveur |
| Début septembre | Cahier des charges v7, backlog v7, registre v4, fiche de référence v4 |
| 12 septembre | **Jalon C1** — fin du sprint 1, premier point de vérité : heures réelles, vélocité, **test d'installation hors ligne** |
| 26 septembre | Fin du sprint 2 · restitution du prototype du solveur |
| 10 octobre | **Jalon J2** — démonstration de mi-parcours et décision go/no-go sur l'optimisation |
| 24 octobre | **Jalon J3** — fin de développement |
| 5 décembre | Dépôt du mémoire |

**Le jalon C1 est le premier point de vérité du projet.** Il donnera la vélocité réelle, permettra de réviser la clé de conversion de 1,3 heure par point, et tranchera par le test l'incertitude sur les dépendances natives de WeasyPrint — donc l'éventuel recours à une conteneurisation.

# 11. Annexe — inventaire des figures

| Code | Objet |
| --- | --- |
| `UC-01` à `UC-06` | Cas d'utilisation par paquetage |
| `SEQ-01` | Génération du programme hebdomadaire |
| `SEQ-02` | Validation croisée, signature et affichage |
| `SEQ-03` | Circuit d'évaluation |
| `SEQ-04` | Traitement d'une indisponibilité |
| `CLS-00` | Diagramme de classes complet — **fait foi**, annexe A3 paysage |
| `CLS-01` à `CLS-05` | Vues thématiques par paquetage |
| `ARC-01` | Architecture en couches |
| `ARC-02` | Déploiement |
| `MAQ-01` à `MAQ-05` | Wireframes des écrans structurants |

Le diagramme d'états du programme, `ETA-01`, est reporté au sprint 2 conformément au cadrage de la phase.

Les 23 sources sont versionnées sous `docs/diagrammes/` et rendues par une commande unique, en SVG pour le mémoire et en PNG pour les supports de présentation.

---

*Document de revue — jalon J1, version 1 du 30 août 2026. Lot WBS 4.5.1. Synthétise les six livrables de la phase 4 et les décisions de terrain des 23, 25, 26 et 30 août 2026.*
