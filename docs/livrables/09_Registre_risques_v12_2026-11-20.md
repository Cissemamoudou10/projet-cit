**REGISTRE DES RISQUES ET OPPORTUNITÉS**

Projet de fin d’études · Système de gestion des activités de formation du CIT

*Livrable 5 / 6 — Phase 3 : Planification détaillée · Version 12 du 20 novembre 2026 · Remplace la version 11 du 18 novembre 2026 · Document vivant*

# **1. Méthode de cotation**

Chaque risque est coté sur deux axes notés de 1 à 4 : la probabilité d’occurrence et l’impact en cas de survenue. La criticité est leur produit. La méthode est inchangée depuis la version 1 ; seules les cotations, les mesures et le périmètre du registre évoluent. **Un registre cote ce qui est mesuré, non ce qui est présumé** : principe posé en version 2, appliqué dans les deux sens.

| **Niveau** | **Criticité** | **Interprétation** | **Traitement** |
| --- | --- | --- | --- |
| Critique | 12 à 16 | Menace directe l’atteinte des objectifs | Plan d’atténuation actif et suivi hebdomadaire |
| Élevé | 9 à 11 | Impact significatif sur le périmètre ou le délai | Plan d’atténuation défini, revue à chaque jalon |
| Modéré | 6 à 8 | Perturbation absorbable | Mesures préventives, surveillance périodique |
| Faible | 1 à 5 | Effet limité | Surveillance simple |

# **2. Historique des versions**

Les sections d’évolution des versions 2 à 7 sont conservées dans les versions archivées correspondantes. Le tableau ci-dessous en garde la trace ; seule l’évolution de la présente version est détaillée.

| **Version** | **Date** | **Occasion** | **Risques** | **Mouvements principaux** |
| --- | --- | --- | --- | --- |
| 1 | 27/07 | Phase 1 | 12 | Registre initial |
| 2 | 18/08 | Phase 3 | 17 | R8 critique ; R6 et R7 en baisse ; R13 à R17 nouveaux |
| 3 | 23/08 | Phase 4, réponses de terrain | 18 | R6 en hausse (résolution centre-entier) ; R18 nouveau |
| 4 | 30/08 | Clôture de la phase 4 | 19 | R19 nouveau (incohérence entre livrables) |
| 5 | 08/09 | Clôture du sprint 1 | 22 | R9 éteint ; R15 en baisse ; R20 à R22 nouveaux |
| 6 | 30/09 | Clôture du sprint 2 | 25 | R6 quasi éteint ; R8 en baisse ; R10 en hausse ; R23 à R25 nouveaux |
| 7 | 10/10 | Clôture du sprint 3, jalon J2 | 28 | R1 critique ; R5 et R23 en baisse ; R16 en hausse ; R26 à R28 nouveaux |
| 8 | 23/10 | Clôture du sprint 4, jalon J3 | 29 | R16 critique ; R26, R27, R6, R25, R8 éteints ; R29 nouveau |
| 9 | 08/11 | Recette de la phase 6 (cinq cahiers sur six prononcés) | 32 | Voir section 3 |
| 10 | 09/11 | Correction : séance avec les cellules planifiée | 32 | R29 n’est pas réalisé : de 8 à 6 ; R11 précisé. Voir section 3 bis |
| 11 | 18/11 | Clôture de la phase 6 : RECETTE-05 et C3 prononcés, code gelé | 32 | R29 réalisé ; R30 et R31 éteints ; deux leçons nouvelles. Voir section 3 ter |
| **12** | **20/11** | **Correction des rôles : il n’y a pas de commanditaire distinct** | **32** | **R1 et R18 reformulés, cotations inchangées. Voir section 3 quater** |

# **3. Évolutions depuis la version 8 — recette de la phase 6**

La recette a commencé le 29 octobre. Au 8 novembre, cinq cahiers sur six sont prononcés : RECETTE-00 (socle), 00 bis (planification de base), 01 (circuit de validation et planification), 02 (évaluations), 03 (suivi) et 04 (pilotage). RECETTE-05, transverse, est prévue le 13 novembre. **La recette a joué son rôle** : elle a trouvé une quarantaine d’anomalies, dont quatre exigences manquantes que ni les tests unitaires ni la conception n’avaient vues, et toutes sont corrigées et rejouées. La présente version éteint trois risques, en abaisse un, en relève cinq, réévalue R29 et en crée trois. Elle ouvre aussi une section de leçons apprises (section 6 bis).

**Trois risques éteints.** R10, la modélisation du circuit de validation : le circuit a été exercé de bout en bout en RECETTE-01 — soumission, retrait, rejet, reprise, validation, annulation, signature, affichage, avenant — et ses vingt-quatre contrôles sont conformes dès le premier passage. R15 et R21, l’accès au serveur du CIT et son environnement inconnu, n’ont plus d’objet : le déploiement de la phase 7 se fait sur une machine virtuelle isolée qui simule le serveur du centre (décision D-295).

**R2 — de 4 à 6 : l’écart entre besoins et fonctionnalités s’est produit, et a été rattrapé.** Quatre exigences manquaient au backlog : l’étalement d’une matière sur la session (RG-66), l’achèvement d’une matière dont le reste est inférieur à une séance (RG-39 a modifiée), l’interdiction de deux séances simultanées pour une brigade (RG-67) et le type de lieu comme contrainte dure. Toutes ont été découvertes par des scénarios de bout en bout, traitées et tracées au backlog v12. Le risque n’est pas éteint : la recette a été jouée par le binôme, et la séance avec les cellules n’aura lieu que le 16 novembre (R29).

**R7 — de 6 à 12, devenu critique : le mémoire.** Au 8 novembre, un seul chapitre sur cinq est rédigé, pour un dépôt le 4 décembre. Le binôme a gelé ses autres activités pour la semaine du 9 au 13 novembre. La matière existe — cahiers de recette, décisions, problèmes, revues de sprint — mais le temps de rédaction est désormais le chemin critique du projet.

**R13 — de 6 à 9 : les consignes de forme ne sont pas arrivées.** Le mail du 1er novembre au directeur (plan, modèle, volume, norme bibliographique, contribution individuelle, confidentialité) est sans réponse au 8 novembre. Le mémoire s’écrit sur un cadre provisoire, avec le risque de reprises de forme tardives.

**R11 — de 4 à 6 : les demandes d’évolution se sont multipliées en recette.** Suppression d’un brouillon, compte rendu persistant, déplacement le jour même, listes filtrées, tableau de bord d’accueil, identité visuelle, moyennes détaillées. Chacune a été arbitrée explicitement : retenue et tracée, ou reportée en perspective. Le mécanisme fonctionne, mais il consomme du temps à trois semaines du dépôt.

**R9 — de 3 à 6.** Le paquet hors ligne n’a pas été réinstallé depuis le 12 septembre, alors que le code a reçu une centaine de commits et de nouvelles dépendances. Le protocole sur machine isolée est à rejouer en phase 7.

**R1 — de 9 à 6.** L’encadrant académique n’a toujours pas répondu sur les valeurs par défaut, et la recette en a ajouté deux (coefficient d’étalement 1,5, dépassement de moins d’une séance). Mais plus rien n’attend sa réponse : toutes sont paramétrables, documentées comme hypothèses, et le mémoire les présentera ainsi.

**Trois risques nouveaux.** R30, la non-régression des corrections de fin de recette ; R31, le lot d’ergonomie du 12 novembre ; R32, la marge calendaire consommée.

# **3 bis. Correction de la version 10 — 9 novembre 2026**

La version 9 déclarait R29 réalisé, sous réserve de confirmation par l’étudiant. Celui-ci a précisé le 9 novembre qu’**une séance de recette avec les cellules aura lieu le lundi 16 novembre 2026**. R29 n’est donc pas réalisé : sa probabilité baisse de 4 à 2, puisque la séance est planifiée ; son impact passe de 2 à 3, parce qu’une séance tenue après le jalon C3 (13 novembre) peut produire des remarques à arbitrer en pleine rédaction du mémoire. Criticité : 6. R11 est précisé en conséquence.

Les échéances externes sont également précisées : **dépôt du mémoire entre le 1er et le 4 décembre**, **soutenance entre le 20 et le 25 décembre 2026**, et **rapport d’avancement à déposer le vendredi 13 novembre**, préparé le jeudi 12 au soir. Ce dépôt tombe le même jour que RECETTE-05, et la veille du jeudi est déjà occupée par le lot d’ergonomie : R32 (glissement du calendrier) est maintenu à 9.

# **3 ter. Clôture de la phase 6 — version 11, 18 novembre 2026**

**RECETTE-05 est prononcée le 18 novembre (60 contrôles sur 60), et avec elle le jalon C3** : les six cahiers sont prononcés, le code est gelé à l’étiquette `recette-phase-6-c11` (2 437 tests, 0 échec). Trois mouvements en découlent.

- **R29 est réalisé** : la séance de recette avec les cellules du 16 novembre n’a pas eu lieu. L’atténuation prévue s’applique : la limite est déclarée au cahier de recette et au mémoire, et une démonstration de l’application aux cellules est prévue hors recette, ses remarques étant traitées en perspective (R11). Conséquence directe : l’objectif OS5 n’a pas pu être mesuré avec la cellule ; il est **estimé** par le binôme (40 minutes au plus pour le centre entier, contre au moins une journée déclarée), et sera présenté comme une estimation.
- **R30 et R31 sont éteints** : RECETTE-05 a vérifié l’ensemble en transverse sans régression ; le lot d’ergonomie a été livré le 13 novembre, sa seule anomalie (menu du compte) corrigée le lendemain.
- **R32 est maintenu à 9** : C3 est prononcé le 18 novembre au lieu du 13, cinq jours de plus consommés par le lot d’ergonomie et un dernier lot de corrections d’impression. La date de dépôt n’est pas touchée.

# **3 quater. Correction des rôles — version 12, 20 novembre 2026**

La relecture du mémoire par le binôme a mis au jour une erreur présente depuis la phase 1. Les livrables décrivaient un « colonel commanditaire, encadrant entreprise et décideur, unique canal d’accès aux cellules », distinct de l’encadrant académique. L’étudiant a établi le 20 novembre que :

- le sujet a été proposé par **le centre**, qui est le commanditaire au sens de la gestion de projet ;

- le Colonel Janati Idrissi est **l’encadrant académique et le directeur de mémoire** du binôme ;

- **aucun canal unique d’accès aux cellules n’a existé** : le binôme les rencontrait librement et directement.

Conséquences sur le registre : R1 porte désormais sur l’encadrant académique, auquel les valeurs par défaut avaient été soumises ; sa cotation reste à 6. R18 ne prévoit plus de relecture « par le commanditaire ». Aucun autre risque n’est touché. Le risque de dépendance à un acteur unique, qui fondait R1 en phase 1, reposait sur une prémisse fausse : la ressource rare était la **disponibilité** des cellules, non leur **accès**.

**Leçon L9 — une prémisse posée en phase 1 doit être revalidée explicitement.** L’erreur a traversé quatre mois et une douzaine de livrables parce qu’aucune relecture ne remettait en cause l’identité des acteurs, considérée comme acquise. Elle a été trouvée par une question naïve de relecture (« de qui parles-tu ? »). Les livrables historiques concernés sont signalés par un erratum plutôt que réécrits.

# **4. Registre des risques actifs**

| **Réf.** | **Risque** | **P** | **I** | **Crit.** | **Prévention** | **Atténuation si survenue** |
| --- | --- | --- | --- | --- | --- | --- |
| **R16** | Déséquilibre de la maîtrise du système entre les deux équipiers, et absence de trace de la contribution de chacun | 4 | 3 | **12** | INCHANGÉ — CONSTATÉ. Le fichier `PORTEURS-RETROSPECTIF.md` existe depuis le 25 octobre (52 lignes, commits retrouvés), mais ses colonnes Porteur et Second sont **toujours vides**. **Avant la soutenance** : les remplir à deux, et répartir la rédaction du mémoire de façon lisible (proposition : chapitre 1 par le Lt Niangaly, chapitre 3 par le Lt Cissé, chapitre 4 par paquetage conduit) | Répartition de la soutenance par paquetage réellement conduit ; séances croisées de transfert ; préparation des questions du jury par les deux équipiers |
| **R19** | Incohérence entre livrables : une décision ou une correction portée dans un document et non dans les autres | 3 | 3 | **9** | Occurrences de la phase 6 : l’écran et le serveur appliquaient deux définitions du type de lieu ; le registre des écarts citait encore D-306, remplacée par D-309 ; le chapitre 2 du mémoire, écrit le 2 novembre, est dépassé sur quatre points (RG-64, nombre de règles, de contraintes et de stories). **Mesures** : une seule fonction partagée par l’écran et le serveur (prompt 62) ; backlog v12 et registre v9 déposés dans le dépôt et la base de connaissances ; **une passe unique de mise à jour du chapitre 2 après RECETTE-05** | Diagramme de classes mis en conformité avant le chapitre de conception |
| **R20** | Aucune procédure de sauvegarde définie ni attribuée pour les données de production | 3 | 3 | **9** | Procédure de sauvegarde et de restauration écrite et **essayée** au dossier d’exploitation pendant la phase 7 ; demande de désignation d’un responsable, d’une fréquence et d’un support à la direction, jointe au rapport d’avancement de fin octobre. Inchangé depuis la v5 : aucune action engagée | Reconstitution partielle depuis les documents papier des cellules ; sans sauvegarde, la perte des notes et procès-verbaux d’une session est définitive |
| **R1** | Indisponibilité prolongée de l’encadrant académique (directeur de mémoire) bloquant validations et arbitrages | 3 | 2 | **6** | EN BAISSE — plus rien n’attend sa réponse. Sept valeurs par défaut documentées comme hypothèses : seuil d’admission (10/20), absence comptée zéro, ex aequo au même rang, seuil de charge (24 h/semaine), seuil d’écart (10 %), coefficient d’étalement (1,5), dépassement de moins d’une séance | Présentées au mémoire comme hypothèses paramétrables, modifiables sans changer le code |
| **R32** | Marge calendaire consommée avant le dépôt | 3 | 3 | **9** | NOUVEAU. Le jalon C3, prévu le 2 novembre, est prononcé le 18 novembre : la marge de neuf jours ouvrés est consommée. **Plus aucune évolution après le 12 novembre** ; ordre des priorités : mémoire, puis phase 7 au strict nécessaire (déploiement sur la machine virtuelle, procédure, manuel) | Réduction de la phase 7 aux livrables exigés ; documentation technique en annexe du mémoire |
| **R23** | Dispositif de pilotage : mesure du temps humain jamais tenue | 4 | 2 | **8** | RÉALISÉ, DÉFINITIF — aucune heure humaine en 52 stories. **Un seul relevé rétrospectif déclaratif**, sur les quatre sprints, établi une fois par l’étudiant et présenté comme tel ; aucune reconstitution ligne par ligne | Le mémoire présente l’estimation en points comme la seule mesure validée (quatre sprints à 100 %) et la clé de conversion comme une hypothèse jamais vérifiée, avec la cause. Présenté ainsi, c’est défendable ; découvert par le jury, ça ne l’est pas |
| **R28** | Diffusion de données nominatives réelles dans les livrables | 2 | 4 | **8** | Dépôt vérifié ; jeux de recette entièrement fictifs. **À faire** : captures d’écran du mémoire prises sur le jeu `complet`, jamais sur des données réelles ; usage du logo de l’école dans l’application et les captures à faire confirmer par l’encadrant | Retrait immédiat du livrable diffusé ; remplacement ; signalement au commanditaire |
| **R3** | Rejet du système par la cellule planification, un outil étant déjà en service | 2 | 4 | **8** | Séance de recette avec la cellule (R29) ; mise en avant de ce que l’outil existant ne fait pas : validation croisée, rapprochement prescrit-réalisé, duplication, alertes | Recentrage de la présentation sur ces fonctions ; prise en main guidée par le manuel utilisateur |
| **R12** | Perte de données ou de code source | 2 | 4 | **8** | Versionnement Git avec dépôt distant ; étiquette `j3-fin-developpement` posée ; sauvegarde hebdomadaire du classeur et des livrables | Restauration depuis le dépôt distant ou l’étiquette |
| **R7** | Sous-estimation du temps de rédaction du mémoire | 3 | 4 | **12** | INCHANGÉ — CRITIQUE. Au 18 novembre : chapitre 2 (v1), chapitre 3 (v3) et chapitre 4 (v2) rédigés ; restent les chapitres 1 et 5, la mise à jour du chapitre 2, l’introduction, la conclusion et les annexes, avant une relecture du 23 au 27 novembre et un dépôt visé le 1er décembre. La phase 6 étant close, tout le temps disponible va au mémoire | Report des annexes secondaires ; dépôt dans la fenêtre du 1er au 4 décembre |
| **R4** | Non-conformité aux attentes du jury | 2 | 3 | **6** | Grille d’évaluation à demander à l’encadrant. **Ajout v8 : défense de l’architecture devant le jury**, demandée par l’encadrant — argumentaire et réponses préparés aux objections attendues (« pourquoi pas une architecture séparée ? », « pourquoi pas le solveur ? ») | Ajustement du mémoire et de la soutenance selon les retours |
| **R5** | Disponibilité du binôme non tenue, par périodes entières sans production | 2 | 3 | **6** | EN BAISSE — des stories livrées presque chaque jour au sprint 4. L’impact baisse avec la fin du développement ; il reste sur la recette et le mémoire. Seuil d’alerte maintenu à cinq jours ouvrés sans livrable | Réduction du périmètre de la recette aux critères Must, puis report des documents secondaires de la phase 7 |
| **R13** | Indisponibilité de l’encadrant académique aux points de passage obligés | 3 | 3 | **9** | EN HAUSSE — le mail du 1er novembre sur la forme du mémoire est sans réponse au 8 novembre. Relance écrite avec une réponse par défaut (cadre provisoire de la passation du 8 novembre : environ 80 pages, style IEEE, styles Word intégrés) | Mémoire produit dans le cadre provisoire, styles Word permettant de changer de modèle sans retoucher le texte |
| **R17** | Reprises non planifiées issues des retours de la démonstration J2 | 3 | 2 | **6** | Aucun retour de J2 n’est consigné, et la tenue de la démonstration devant les cellules n’est pas confirmée. **À établir par l’étudiant à l’ouverture de la phase 6** | Inscription des demandes au backlog en Won’t ; arbitrage explicite (R11) |
| **R18** | Format réglementaire des documents imprimables jamais communiqué | 3 | 2 | **6** | Gabarits paramétrables. Le texte des en-têtes et des mentions n’a été relu par personne du terrain : à relire par le binôme puis, si possible, par la Direction de la formation | Production sur gabarit standard présenté comme provisoire ; limite documentée au mémoire |
| **R22** | Défauts d’intégration entre présentation et services, non détectés par les tests | 3 | 2 | **6** | Survenu plusieurs fois en recette : impression (boutons visibles, orientation), séance hors grille invisible, type de lieu filtré à l’écran mais pas au serveur. Nouvelle occurrence en RECETTE-05 (l’impression reprenait boutons et historique), corrigée par une vue d’impression dédiée, vérifiée en navigateur réel (D-314). **Mesure appliquée** : tests en navigateur réel pour l’impression (D-301) ; une fonction unique partagée entre filtre d’écran et serveur | Recette manuelle de tous les documents imprimés (RECETTE-05) |
| **R24** | Saturation des salles attitrées : 32 à 38 salles pour 30 à 35 brigades | 3 | 2 | **6** | Vérification du ratio réel avant le déploiement. Inchangé : aucune action engagée | Regroupement de brigades et catégorie « sans lieu » ; au-delà, arbitrage de la direction |
| **R2** | Écart entre les besoins réels et les fonctionnalités développées | 2 | 3 | **6** | EN HAUSSE — survenu et rattrapé : quatre exigences manquantes découvertes par les scénarios de bout en bout de la recette, traitées et tracées au backlog v12 | Absorption sans refonte : chaque exigence est entrée comme règle de gestion et critère d’acceptation |
| **R11** | Évolution des besoins en cours de projet | 2 | 2 | **4** | EN BAISSE — **gel effectif le 18 novembre** (C3). Toutes les demandes de la recette ont été arbitrées : livrées (lot d’ergonomie, impression), ou reportées en perspective. Les remarques de la démonstration aux cellules seront consignées en perspective, sans retour dans le code | Toute demande nouvelle va aux perspectives du mémoire |
| **R14** | Concentration de la connaissance du cœur algorithmique sur un seul équipier | 2 | 2 | **4** | Lié à R16 : la génération et les contraintes sont à présenter par les deux équipiers lors des séances de transfert | Reprise sur la base de l’étude écrite et des décisions |
| **R9** | Échec du déploiement sur réseau isolé | 2 | 3 | **6** | EN HAUSSE — paquet non réinstallé depuis le 12 septembre, une centaine de commits et des dépendances ajoutées depuis. Protocole complet à rejouer sur la machine virtuelle de la phase 7 (D-295) | Reconstitution du paquet ; procédure du 7 septembre |

# **5. Risques éteints ou réalisés (versions 8 à 11)**

| **Réf.** | **Risque** | **Cotation finale** | **Motif de l’extinction** |
| --- | --- | --- | --- |
| R10 | Modélisation erronée du workflow de validation croisée | 1 × 3 | Circuit exercé de bout en bout en RECETTE-01 : vingt-quatre contrôles conformes au premier passage |
| R15 | Accès au poste de déploiement du CIT non obtenu à temps | 1 × 1 | Sans objet depuis D-295 : déploiement sur machine virtuelle isolée |
| R21 | Environnement du serveur cible inconnu | 1 × 1 | Sans objet depuis D-295 : l’environnement cible est la machine virtuelle construite par le binôme |
| R26 | Ordre de verrouillage non déterministe du traitement en lot | 1 × 2 | Corrigé en ouverture du sprint 4 (P-42) : tri explicite avant le verrou, test de reproduction |
| R27 | Instabilité de la suite de tests complète | 1 × 2 | Cause établie (P-51) : exécutions concurrentes sur la même base, désormais bloquées par un verrou. Cinq exécutions consécutives sans échec |
| R6 | Dérive de l’optimisation sous contraintes | 1 × 1 | Réexamen d’US-PLAN-08 tenu le 20 octobre (D-289) : déclassement maintenu, développement clos |
| R25 | Divergence entre deux stratégies de génération | 1 × 1 | Une seule stratégie existe et existera dans la version livrée |
| R8 | Sous-estimation de la charge de développement | 1 × 1 | Développement clos : 58, 61, 50 et 55 points livrés sur autant d’engagés |
| R29 | Recette conduite sans les utilisateurs des cellules | Réalisé (v11) | Séance du 16 novembre non tenue. Limite déclarée au cahier et au mémoire ; objectif OS5 estimé et non mesuré ; démonstration hors recette prévue |
| R30 | Régression introduite par les corrections de fin de recette | 1 × 3 (v11) | RECETTE-05 prononcée sans régression ; suite complète verte à chaque lot |
| R31 | Retard ou régression dus au lot d’ergonomie | 1 × 3 (v11) | Lot livré le 13 novembre ; une anomalie corrigée le 14 ; RECETTE-05 prononcée |

Les risques conservent leur numérotation d’origine pour préserver la traçabilité entre les versions. R29 est nouveau en version 8 ; R30 à R32 en version 9.

# **6. Analyse des risques dominants**

| **R7 — Le mémoire (criticité 12, critique)** Le produit est prêt avant le texte qui le présente. Quatre chapitres sur cinq restent à écrire, et le jury jugera d’abord le mémoire. **Ce qui rend le délai tenable :** la matière est déjà écrite ailleurs — décisions, problèmes, revues de sprint, cahiers de recette — et le cadre est fixé par la passation du 8 novembre (plan, volume, règles d’écriture). **Mesure :** un chapitre par jour du 9 au 13 novembre, chacun envoyé à l’encadrant dès qu’il est prêt ; aucune évolution du produit après le 12 novembre. |
| --- |

| **R16 — Contribution de chaque équipier (criticité 12, critique)** Le fichier d’attribution rétrospective existe, mais ses colonnes de porteurs sont vides. C’est toujours le seul risque qu’un jury vérifiera en ouvrant le dépôt, et le seul qui touche la note individuelle. **Mesure :** remplir les porteurs à deux avant la soutenance, et faire de la répartition du mémoire une preuve lisible de la contribution de chacun. |
| --- |

| **R32 et R13 — Le calendrier et les consignes (criticité 9)** La marge est consommée et le cadre de forme n’est pas confirmé. Les deux se traitent ensemble : écrire maintenant dans le cadre provisoire, avec des styles Word qui permettent de changer de modèle sans retoucher le texte, et relancer le directeur avec une réponse par défaut. |
| --- |

# **6 bis. Leçons apprises de la recette**

| **N°** | **Constat** | **Cause profonde** | **Leçon** |
| --- | --- | --- | --- |
| L1 | Quatre exigences manquantes trouvées en recette, aucune par les tests unitaires | Les tests unitaires vérifient une règle à la fois ; les défauts naissaient de l’interaction entre deux brigades, plusieurs semaines ou deux règles | Une recette sur jeu de données réaliste et une **simulation d’une session entière par le vrai générateur** sont indispensables pour un problème d’ordonnancement |
| L2 | Un recalibrage du jeu de données a failli masquer deux défauts applicatifs | Le premier réflexe face à un résultat aberrant a été de corriger les données | **Diagnostiquer avant de corriger** : recouper le compte rendu avec les chiffres, brigade par brigade |
| L3 | Une règle vérifiée par l’écran seul était contournable (RG-05, type de lieu) | Deux implantations d’une même règle, à l’écran et au service | **Une règle, une seule fonction**, appelée par le serveur sur tous les chemins ; l’écran ne fait que la refléter |
| L4 | Des défauts d’impression invisibles aux tests | Un test de gabarit ne rend pas la page | Tester le rendu dans un **navigateur réel** (D-301) |
| L5 | Des contrôles de recette mal formulés ont coûté des allers-retours | Cahiers écrits avant de connaître le comportement fin (ex. : mot « contrôle » à double sens, dates figées) | Rédiger les contrôles en **notation relative (W0, W+1)**, désigner les objets par leur description et non par leur clé, relire chaque cahier avec le recetteur |
| L6 | L’assistant de code a deux fois levé un garde-fou ou restreint une règle pour faire passer des tests | Optimisation locale de l’outil | Interdire explicitement la modification des permissions, et **exiger la justification de toute restriction de portée** (D-306 corrigée par D-309) |
| L7 | La commande documentée de chargement du jeu volumineux a échoué deux fois (rôle de base, dépendance manquante) | La procédure avait été écrite, mais jamais rejouée telle qu’écrite (P-83) | **Une procédure n’est prouvée qu’une fois rejouée à la lettre**, par quelqu’un qui ne l’a pas écrite — à appliquer à la procédure de déploiement de la phase 7 |
| L8 | L’objectif OS5 n’a pu être qu’estimé | Sa mesure dépendait d’une séance avec la cellule, programmée en fin de recette et non tenue | **Mesurer un objectif chiffré au plus tôt**, avec une branche de repli jouée sans attendre la séance externe |
| L9 | Une erreur sur l’identité des acteurs a traversé tous les livrables depuis la phase 1 (colonel « commanditaire, canal unique » au lieu de l’encadrant académique ; accès en réalité direct aux cellules) | Prémisse de cadrage jamais revalidée, recopiée de livrable en livrable | **Revalider explicitement les prémisses de la phase 1 à chaque grande relecture** ; erratum pour les livrables figés |

# **7. Registre des opportunités**

| **Réf.** | **Opportunité** | **Bénéfice attendu** | **Action pour la concrétiser** |
| --- | --- | --- | --- |
| O1 | Marge calendaire avant le dépôt du 4 décembre | Absorption des aléas sans réduction du périmètre | **Consommée** par la recette (C3 du 2 au 13 novembre) ; voir R32 |
| O11 | **Validation écrite de l’architecture par l’encadrant** | Argument de soutenance : un choix d’architecture contesté, défendu par écrit et validé, avec ses raisons | **Nouvelle.** Reprendre la justification écrite adressée à l’encadrant au chapitre d’architecture ; présenter la couche de services comme point d’appui d’une évolution vers une interface de programmation |
| O12 | **Matrice de traçabilité critères → tests** | Base du cahier de recette et preuve de la chaîne exigence → story → test, que le jury vérifie | **Nouvelle.** Inventaire produit à J3 ; à compléter en phase 6 sur le texte intégral du backlog v11 (une quinzaine de critères non identifiés) |
| O4 | Circuit de validation croisée | Différenciateur fort : une véritable dimension de système d’information | Concrétisée ; validée par défaut le 16 octobre ; à exercer à la recette |
| O8 | Chapitre de mémoire sur l’ordonnancement sous contraintes | Différenciateur académique : une décision de renoncement argumentée par la mesure | Matière archivée ; le réexamen du 20 octobre en ferme le récit |
| O13 | **Chapitre de recette du mémoire** | Démontrer la qualité de la démarche par des faits : une quarantaine d’anomalies trouvées, corrigées, rejouées et tracées, dont quatre exigences manquantes | **Nouvelle.** Matière : six cahiers, `PROBLEMES.md` (P-53 à P-80), `DECISIONS.md` (D-298 à D-311), leçons de la section 6 bis |
| O9 | Chapitre de méthode sur la vérification | Des garanties affirmées puis démenties par la mesure, détectées et corrigées : peu de mémoires peuvent le montrer | Matière enrichie au sprint 4 : la correction d’une décision juste, l’historique perdu au renommage, la garde d’écran contournable par un appel direct, le blocage expliqué au lieu d’être relancé |
| O10 | Scénario de démonstration automatisé | La soutenance rejoue un scénario sans risque de casser sur une règle | Étendre le scénario de J2 aux évaluations et au suivi du sprint 4 pendant la phase 6 ; le rejouer avant la soutenance |
| O2 | Existence d’un outil de planification en service | Référence fonctionnelle ; analyse comparative pour l’objectif OS5 | Obtenir un accès en consultation |
| O3 | Documents formalisés détenus par les cellules | Matière pour les gabarits | Partiellement fermée pour motif de confidentialité ; non bloquante (R18) |
| O5 | Besoins confirmés par entretiens et guide officiel | Analyse de l’existant défendable | Tracer chaque exigence à sa source dans le mémoire |
| O6 | Levier de capacité | — | **Close** : le développement s’est achevé sans l’activer |
| O7 | Prototype du solveur avancé | — | Concrétisée et close en version 6 |

# **8. Synthèse**

| **Niveau** | **Nombre** | **Références** | **Suivi** |
| --- | --- | --- | --- |
| Critique | 2 | R16, R7 | Quotidien jusqu’au dépôt |
| Élevé | 4 | R19, R20, R13, R32 | À chaque jalon |
| Modéré | 13 | R23, R28, R3, R12, R4, R5, R17, R18, R22, R24, R1, R2, R9 | Périodique |
| Faible | 2 | R14, R11 | Surveillance simple |
| Éteints ou réalisés | 11 | R29 réalisé, R30, R31 (v11) ; R10, R15, R21 (v9) ; R26, R27, R6, R25, R8 (v8) | Archivés |
| **Total** | **32** | **21 actifs, aucun nouveau en v11** | **—** |

**Mouvements de la version 12 :** aucune cotation modifiée ; R1 et R18 reformulés (rôles corrigés) ; une leçon nouvelle (L9).

**Mouvements de la version 11 :** une réalisation (R29) ; deux extinctions (R30, R31) ; une baisse (R11 de 6 à 4) ; deux leçons nouvelles (L7, L8).

**Mouvements de la version 9 :** trois extinctions (R10, R15, R21) ; une baisse (R1 de 9 à 6) ; cinq hausses (R7 de 6 à 12, R13 de 6 à 9, R2 de 4 à 6, R11 de 4 à 6, R9 de 3 à 6) ; une réévaluation de R29 (de 9 à 8, puis de 8 à 6 en v10, voir section 3 bis) ; trois risques nouveaux.

**Conclusion.** Le produit a passé l’épreuve de la recette : six cahiers prononcés, toutes les anomalies corrigées et rejouées, code gelé le 18 novembre. Les risques ont quitté le code pour se concentrer sur **le temps** — un mémoire aux quatre cinquièmes à écrire en trois semaines — et sur **la contribution visible de chacun**. Ce sont les deux seuls risques critiques, et le binôme est seul à pouvoir les traiter.

# **9. Modalités de mise à jour**

- À chaque fin de phase : révision des cotations, clôture des risques éteints, ajout des risques nouvellement identifiés.

- À chaque anomalie de recette résolue : consignation de la cause profonde, de la mesure appliquée et de son efficacité, au titre des leçons apprises.

- À chaque jalon : revue complète des risques de criticité supérieure ou égale à 9 avec l’encadrant.

- **Réévaluations programmées :** R7, R13 et R32 chaque jour jusqu’au dépôt ; R16 avant la soutenance ; R20 et R9 pendant la phase 7 (procédure de déploiement et de sauvegarde rejouée à la lettre, L7) ; R17 à clore en déclarant l’absence de retours consignés de J2 ; R20, R9 et R24 pendant la phase 7 ; R28 avant les captures d’écran du mémoire.

- Version unique : ce document est la seule source de vérité du registre. Toute modification donne lieu à une version datée qui remplace la précédente dans les connaissances du projet.

*Document vivant — version 12 du 20 novembre 2026. Remplace la version 11 du 18 novembre 2026. Correction des rôles (centre commanditaire, encadrant académique et directeur de mémoire, accès direct aux cellules) ; leçon L9.*
