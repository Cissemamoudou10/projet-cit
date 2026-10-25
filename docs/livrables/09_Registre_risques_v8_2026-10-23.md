**REGISTRE DES RISQUES ET OPPORTUNITÉS**

Projet de fin d’études · Système de gestion des activités de formation du CIT

*Livrable 5 / 6 — Phase 3 : Planification détaillée · Version 8 du 23 octobre 2026 · Remplace la version 7 du 10 octobre 2026 · Document vivant*

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
| **8** | **23/10** | **Clôture du sprint 4, jalon J3** | **29** | **Voir section 3** |

# **3. Évolutions depuis la version 7 — clôture du sprint 4, fin du développement**

Le sprint 4 a livré ses quatorze stories, cinquante-cinq points sur cinquante-cinq, et le jalon J3 a été atteint le 20 octobre, quatre jours avant son échéance, avec ses éléments de pilotage : revue, registre des écarts, propositions de risques, matrice de traçabilité. **Le développement est clos : 52 stories et 224 points livrés, cent pour cent du périmètre planifié hors réserve, sur quatre sprints.** Le profil de risque bascule en conséquence : les risques de développement s’éteignent, ceux de la recette, du déploiement et de la soutenance prennent leur place. La présente version éteint cinq risques, en abaisse quatre, en relève trois et en crée un.

**Cinq risques éteints.** R26, l’ordre de verrouillage du traitement en lot, est corrigé en ouverture du sprint (tri par programme, test de reproduction). R27, l’instabilité de la suite de tests, a trouvé sa cause : deux exécutions de la suite lancées en même temps sur la même base. Un verrou l’empêche désormais, et cinq exécutions complètes consécutives n’ont produit aucun échec. R6 et R25 sont éteints par le réexamen d’US-PLAN-08 tenu le 20 octobre, qui maintient le déclassement du solveur. R8, la sous-estimation de la charge de développement, n’a plus d’objet : quatre sprints ont livré tout leur périmètre.

**R16 — de 9 à 12, devenu critique : la trace s’est dégradée au lieu de se corriger.** La version 7 relevait ce risque sous condition, parce que le registre des décisions du sprint 3 attribuait toutes ses entrées au même équipier. La mesure demandée — établir et rendre visible la contribution de chacun — n’a pas été prise. Au sprint 4, la colonne des porteurs du suivi de sprint n’a pas été renseignée, et **35 des 36 décisions du sprint portent la mention « porteur non renseigné »**. Le dépôt ne montre plus un contributeur unique : il n’en montre plus aucun. La probabilité passe à 4 parce que c’est un constat. C’est désormais le risque dominant du projet : c’est une question de soutenance, et seul le binôme peut y répondre.

**R1 — de 12 à 9 : la décision prévue a été prise à son échéance.** Sans retour des cellules sur ETA-01 au 16 octobre, la décision a été consignée le jour même : les réponses par défaut font référence, et toute réponse ultérieure sera traitée comme une demande d’évolution. Le circuit n’est plus suspendu à une réponse. Le silence du commanditaire n’a pas cessé pour autant, et il pèse maintenant sur la recette (R29). En revanche, l’encadrant académique a répondu en quelques jours à une demande écrite et argumentée : ce canal fonctionne.

**R11 — une occurrence, traitée.** Pendant le sprint 4, l’encadrant a demandé de séparer l’application en un front-end et un back-end distincts. La demande arrivait pendant le dernier sprint de développement et aurait coûté un à deux mois. Elle a été traitée comme le prévoit ce risque : une justification écrite de l’architecture (déploiement hors ligne, surface d’exposition des données sensibles, calendrier), soumise à l’encadrant, qui a validé le maintien de l’architecture le 22 octobre. Il demande deux choses : consigner ce choix au mémoire, avec la couche de services comme point d’appui d’une évolution vers une interface de programmation, et se préparer à le défendre devant le jury. Ces deux demandes passent à R4.

**R23 — de 9 à 8, réalisé et définitif.** Le développement est clos sans qu’une seule heure humaine ait été relevée en cinquante-deux stories. La mesure ajoutée en version 7 — écrire la ligne au moment de transmettre le prompt — n’a pas été appliquée. Le risque n’est plus de manquer une mesure à venir : il porte sur la manière dont le mémoire présentera son absence. L’impact baisse parce qu’il ne touche plus le pilotage, seulement la crédibilité d’un chiffre ; la probabilité est à 4 parce que c’est un fait.

**R22 — de 4 à 6 : un défaut d’intégration que les tests ne pouvaient pas voir.** L’exemplaire réel du programme hebdomadaire, produit à la clôture, déborde de la page A4 dès le troisième créneau. Aucun test automatisé ne juge une mise en page imprimée. C’est la première anomalie de la recette.

**R15 — de 4 à 6.** La demande d’accès au poste de déploiement du CIT est prévue au rapport d’avancement de fin octobre, et la phase de déploiement commence le 3 novembre. La marge entre les deux a disparu.

**Un risque nouveau : R29 — recette sans les utilisateurs des cellules, coté 9.** La phase 6 doit vérifier le système contre ses critères d’acceptation et ses objectifs SMART. Les cellules n’ont répondu à aucune sollicitation écrite depuis le 30 septembre, et la tenue de la démonstration de J2 devant elles n’est toujours pas confirmée. Une recette jouée par le seul binôme vérifie que le système fait ce qui est écrit, mais pas qu’il convient à ceux qui l’utiliseront.

# **4. Registre des risques actifs**

| **Réf.** | **Risque** | **P** | **I** | **Crit.** | **Prévention** | **Atténuation si survenue** |
| --- | --- | --- | --- | --- | --- | --- |
| **R16** | Déséquilibre de la maîtrise du système entre les deux équipiers, et absence de trace de la contribution de chacun | 4 | 3 | **12** | EN HAUSSE — CONSTATÉ. 35 décisions sur 36 du sprint 4 sans porteur. **Avant la fin de la phase 6 (2 novembre)** : renseigner la colonne des porteurs des quatre sprints, par une note datée qui la déclare rétrospective, sans réécrire les lignes ; répartir la recette par paquetage, chaque équipier jouant les scénarios de ce qu’il a conduit | Répartition de la soutenance par paquetage réellement conduit ; séances croisées de transfert avant la soutenance, chacun présentant à l’autre ses paquetages ; préparation des questions du jury sur l’ensemble du système par les deux équipiers |
| **R29** | Recette conduite sans les utilisateurs des cellules : conformité vérifiée, adéquation non vérifiée | 3 | 3 | **9** | NOUVEAU. Demander dès l’ouverture de la phase 6, par l’intermédiaire du commanditaire, une séance de recette d’une heure avec la cellule planification et la cellule pédagogique, avant le 30 octobre, sur des scénarios préparés et un jeu de données fictif. Demande écrite, avec une date proposée et une réponse par défaut | Recette conduite par le binôme dans le rôle de chaque profil, sur les mêmes scénarios ; la limite est déclarée au cahier de recette et au mémoire. Démonstration finale au commanditaire, ses remarques consignées et arbitrées au titre de R11 |
| **R19** | Incohérence entre livrables : une décision ou une correction portée dans un document et non dans les autres | 3 | 3 | **9** | Vérification à la destination, maintenue. Occurrences du sprint 4 détectées avant tout effet : une décision corrigeant à tort une citation juste (D-273, révisée), un tableau d’avancement daté du 2 octobre en tête mais à jour en corps, un sprint compté à dix stories au lieu de onze, deux reports déclarés orphelins alors qu’une story de la réserve les portait. **Mesure ajoutée : le backlog est déposé dans le dépôt à chaque version**, pour que la traçabilité critère → test se lise sur le texte des critères | Seize écarts consolidés au sprint 4, dont neuf entre le diagramme de classes et le code : **diagramme mis en conformité avant la rédaction du chapitre de conception du mémoire** |
| **R10** | Modélisation erronée du workflow de validation croisée du programme | 3 | 3 | **9** | Décision du 16 octobre (D-268) : le circuit construit sur les réponses par défaut fait référence. Table des transitions unique, contrôlée contre ETA-01 par un test. **Le circuit sera exercé de bout en bout pendant la recette**, si possible devant une cellule (R29) | Correction localisée dans la table ; toute divergence signalée après le 16 octobre est une demande d’évolution (R11), arbitrée explicitement, et non une correction due |
| **R20** | Aucune procédure de sauvegarde définie ni attribuée pour les données de production | 3 | 3 | **9** | Procédure de sauvegarde et de restauration écrite et **essayée** au dossier d’exploitation pendant la phase 7 ; demande de désignation d’un responsable, d’une fréquence et d’un support à la direction, jointe au rapport d’avancement de fin octobre. Inchangé depuis la v5 : aucune action engagée | Reconstitution partielle depuis les documents papier des cellules ; sans sauvegarde, la perte des notes et procès-verbaux d’une session est définitive |
| **R1** | Indisponibilité prolongée du commanditaire bloquant validations et arbitrages | 3 | 3 | **9** | EN BAISSE — décision consignée à l’échéance (D-268), le développement n’attend plus de réponse. Questions toujours groupées, avec réponse par défaut : cinq questions de terrain en attente (préparation de la semaine suivante avant affichage, traitement de l’absence, seuil d’admission, règle d’égalité, seuil de charge des instructeurs) | Valeurs par défaut documentées comme hypothèses au mémoire ; toute réponse tardive est une évolution (R11) |
| **R23** | Dispositif de pilotage : mesure du temps humain jamais tenue | 4 | 2 | **8** | RÉALISÉ, DÉFINITIF — aucune heure humaine en 52 stories. **Un seul relevé rétrospectif déclaratif**, sur les quatre sprints, établi une fois par l’étudiant et présenté comme tel ; aucune reconstitution ligne par ligne | Le mémoire présente l’estimation en points comme la seule mesure validée (quatre sprints à 100 %) et la clé de conversion comme une hypothèse jamais vérifiée, avec la cause. Présenté ainsi, c’est défendable ; découvert par le jury, ça ne l’est pas |
| **R28** | Diffusion de données nominatives réelles dans les livrables | 2 | 4 | **8** | Dépôt vérifié ; les exemplaires PDF de démonstration sont produits sur données fictives. **Reste à faire avant la rédaction du mémoire** : vérifier les livrables tenus hors du dépôt, en priorité les maquettes en traitement de texte | Retrait immédiat du livrable diffusé ; remplacement ; signalement au commanditaire |
| **R3** | Rejet du système par la cellule planification, un outil étant déjà en service | 2 | 4 | **8** | Séance de recette avec la cellule (R29) ; mise en avant de ce que l’outil existant ne fait pas : validation croisée, rapprochement prescrit-réalisé, duplication, alertes | Recentrage de la présentation sur ces fonctions ; prise en main guidée par le manuel utilisateur |
| **R12** | Perte de données ou de code source | 2 | 4 | **8** | Versionnement Git avec dépôt distant ; étiquette `j3-fin-developpement` posée ; sauvegarde hebdomadaire du classeur et des livrables | Restauration depuis le dépôt distant ou l’étiquette |
| **R7** | Sous-estimation du temps de rédaction du mémoire | 2 | 3 | **6** | Rédaction des chapitres indépendants du code dès la phase 6 : introduction, état de l’art, méthode. Matière disponible : étude du solveur, leçons et revues des quatre sprints, registres des décisions, des problèmes et des écarts. **Chapitre d’architecture demandé par l’encadrant** : la justification écrite adressée à l’encadrant en est la base | Priorité absolue du mémoire sur toute autre activité après la phase 7 ; relecture par chapitres (R13) |
| **R4** | Non-conformité aux attentes du jury | 2 | 3 | **6** | Grille d’évaluation à demander à l’encadrant. **Ajout v8 : défense de l’architecture devant le jury**, demandée par l’encadrant — argumentaire et réponses préparés aux objections attendues (« pourquoi pas une architecture séparée ? », « pourquoi pas le solveur ? ») | Ajustement du mémoire et de la soutenance selon les retours |
| **R5** | Disponibilité du binôme non tenue, par périodes entières sans production | 2 | 3 | **6** | EN BAISSE — des stories livrées presque chaque jour au sprint 4. L’impact baisse avec la fin du développement ; il reste sur la recette et le mémoire. Seuil d’alerte maintenu à cinq jours ouvrés sans livrable | Réduction du périmètre de la recette aux critères Must, puis report des documents secondaires de la phase 7 |
| **R13** | Indisponibilité de l’encadrant académique aux points de passage obligés | 2 | 3 | **6** | EN BAISSE — réponse argumentée en quelques jours, validation le 22 octobre. Relecture du mémoire à fixer en novembre ; chapitres envoyés 48 h avant | Dépôt sur la base de la relecture croisée du binôme |
| **R15** | Accès au poste de déploiement du CIT non obtenu à temps | 3 | 2 | **6** | EN HAUSSE — demande au rapport d’avancement de fin octobre, alors que le déploiement commence le 3 novembre. La porter dès l’ouverture de la phase 6 | Déploiement sur machine virtuelle reproduisant l’environnement cible, éprouvé le 7 septembre |
| **R17** | Reprises non planifiées issues des retours de la démonstration J2 | 3 | 2 | **6** | Aucun retour de J2 n’est consigné, et la tenue de la démonstration devant les cellules n’est pas confirmée. **À établir par l’étudiant à l’ouverture de la phase 6** | Inscription des demandes au backlog en Won’t ; arbitrage explicite (R11) |
| **R18** | Format réglementaire des documents imprimables jamais communiqué | 3 | 2 | **6** | Gabarits paramétrables. Le texte des en-têtes et des mentions n’a été relu par personne du terrain : à relire par le binôme puis, si possible, par le commanditaire pendant la recette | Production sur gabarit standard présenté comme provisoire ; limite documentée au mémoire |
| **R22** | Défauts d’intégration entre présentation et services, non détectés par les tests | 3 | 2 | **6** | EN HAUSSE — programme hebdomadaire imprimé illisible au-delà de deux créneaux, invisible aux tests automatisés. **La recette manuelle couvre tous les documents imprimés et exportés** | Anomalie n° 1 du cahier de recette : mise en page paysage, ou impression par journée (D-155) si elle ne suffit pas |
| **R21** | Environnement du serveur cible inconnu | 2 | 3 | **6** | Question portée au rapport d’avancement ; paquet constitué par un script rejouable | Reconstitution du paquet pour la distribution réelle, une demi-journée |
| **R24** | Saturation des salles attitrées : 32 à 38 salles pour 30 à 35 brigades | 3 | 2 | **6** | Vérification du ratio réel avant le déploiement. Inchangé : aucune action engagée | Regroupement de brigades et catégorie « sans lieu » ; au-delà, arbitrage de la direction |
| **R2** | Écart entre les besoins réels et les fonctionnalités développées | 1 | 4 | **4** | Recette sur les critères d’acceptation ; séance avec les cellules (R29) | Absorption d’un écart sans refonte structurelle |
| **R11** | Évolution des besoins en cours de projet | 2 | 2 | **4** | Une occurrence au sprint 4 — séparation front-end / back-end — traitée par justification écrite et validée par l’encadrant le 22 octobre. Toute demande nouvelle passe par un arbitrage explicite | Inscription au backlog en Won’t pour la version courante, avec sa justification |
| **R14** | Concentration de la connaissance du cœur algorithmique sur un seul équipier | 2 | 2 | **4** | Lié à R16 : la génération et les contraintes sont à présenter par les deux équipiers lors des séances de transfert | Reprise sur la base de l’étude écrite et des décisions |
| **R9** | Échec du déploiement sur réseau isolé | 1 | 3 | **3** | Dette : protocole complet sur machine isolée à rejouer en phase 7, le paquet n’ayant pas été réinstallé depuis le 12 septembre malgré les dépendances ajoutées | Reconstitution du paquet ; procédure du 7 septembre |

# **5. Risques éteints en version 8**

| **Réf.** | **Risque** | **Cotation finale** | **Motif de l’extinction** |
| --- | --- | --- | --- |
| R26 | Ordre de verrouillage non déterministe du traitement en lot | 1 × 2 | Corrigé en ouverture du sprint 4 (P-42) : tri explicite avant le verrou, test de reproduction |
| R27 | Instabilité de la suite de tests complète | 1 × 2 | Cause établie (P-51) : exécutions concurrentes sur la même base, désormais bloquées par un verrou. Cinq exécutions consécutives sans échec |
| R6 | Dérive de l’optimisation sous contraintes | 1 × 1 | Réexamen d’US-PLAN-08 tenu le 20 octobre (D-289) : déclassement maintenu, développement clos |
| R25 | Divergence entre deux stratégies de génération | 1 × 1 | Une seule stratégie existe et existera dans la version livrée |
| R8 | Sous-estimation de la charge de développement | 1 × 1 | Développement clos : 58, 61, 50 et 55 points livrés sur autant d’engagés |

Les risques conservent leur numérotation d’origine pour préserver la traçabilité entre les versions. R29 est nouveau en version 8.

# **6. Analyse des risques dominants**

| **R16 — Contribution de chaque équipier (criticité 12, critique)** La version 7 posait la question : le dépôt montre-t-il une trace incomplète ou une répartition abandonnée ? Le sprint 4 n’a pas répondu ; il a effacé la question, puisque ses décisions ne portent plus aucun auteur. **Pourquoi c’est le risque dominant :** tous les autres risques actifs ont une mesure en cours ou une limite déclarée. Celui-ci est le seul dont la réponse est entièrement entre les mains du binôme, le seul qu’un jury vérifiera en ouvrant le dépôt, et le seul qui touche la note individuelle de chacun. **Mesure, avant le 2 novembre :** une note datée dans chaque suivi de sprint, déclarée rétrospective, qui attribue chaque story à son porteur réel ; aucune ligne existante n’est réécrite. Puis la recette et la soutenance réparties selon cette attribution. Un dépôt qui dit honnêtement « attribution reconstituée le 30 octobre » vaut mieux qu’un dépôt muet. |
| --- |

| **R29 — Recette sans utilisateurs (criticité 9, nouveau)** Le projet a toujours obtenu les cellules par des entretiens, jamais par une validation écrite à échéance. La recette est un troisième type de demande : une heure de présence, sur un scénario préparé. **Ce qui la rend obtenable :** une demande précise — une date, une durée, deux cellules, un déroulé écrit — transmise par le commanditaire, avec une réponse par défaut. **Ce qui la rend nécessaire :** les objectifs SMART mesurent un usage, pas seulement une conformité. Sans séance, le mémoire devra dire que l’adéquation au besoin a été vérifiée par entretiens et démonstration, et la conformité par la recette. C’est une limite défendable si elle est écrite d’avance. |
| --- |

| **R1 et R10 — Le circuit de validation (criticité 9 chacun, en voie de clôture)** Les deux risques n’attendent plus de réponse pour avancer : la décision du 16 octobre a fait des réponses par défaut la référence. Ce qui reste est une exposition : si une cellule, à la recette, conteste le circuit, la réponse est déjà écrite — c’est une évolution, arbitrée, et non un défaut. **Les deux risques s’éteindront à la fin de la phase 6**, avec ou sans séance de recette, la limite étant alors consignée. |
| --- |

| **R23 — Les heures humaines (criticité 8, réalisé)** Le registre a relevé ce risque à chaque version depuis la version 6, avec une mesure nouvelle à chaque fois. Aucune n’a été appliquée sur la seule partie qui revenait à l’étudiant. **Ce qui est encore possible :** un relevé rétrospectif unique, déclaratif, présenté comme tel au mémoire. **Ce qui ne l’est plus :** une mesure contemporaine. Le mémoire a un meilleur argument que la clé de conversion : quatre sprints consécutifs livrés à cent pour cent de leur estimation en points. C’est cet argument qu’il faut mettre en avant ; l’absence de mesure horaire en est la limite déclarée. |
| --- |

# **7. Registre des opportunités**

| **Réf.** | **Opportunité** | **Bénéfice attendu** | **Action pour la concrétiser** |
| --- | --- | --- | --- |
| O1 | Marge calendaire avant le dépôt du 5 décembre | Absorption des aléas sans réduction du périmètre | **Neuf jours ouvrés intacts, plus trois jours d’avance gagnés à J3** (21 au 23 octobre), employés à la clôture et au démarrage de la recette. Seuil d’alerte à 7 |
| O11 | **Validation écrite de l’architecture par l’encadrant** | Argument de soutenance : un choix d’architecture contesté, défendu par écrit et validé, avec ses raisons | **Nouvelle.** Reprendre la justification écrite adressée à l’encadrant au chapitre d’architecture ; présenter la couche de services comme point d’appui d’une évolution vers une interface de programmation |
| O12 | **Matrice de traçabilité critères → tests** | Base du cahier de recette et preuve de la chaîne exigence → story → test, que le jury vérifie | **Nouvelle.** Inventaire produit à J3 ; à compléter en phase 6 sur le texte intégral du backlog v11 (une quinzaine de critères non identifiés) |
| O4 | Circuit de validation croisée | Différenciateur fort : une véritable dimension de système d’information | Concrétisée ; validée par défaut le 16 octobre ; à exercer à la recette |
| O8 | Chapitre de mémoire sur l’ordonnancement sous contraintes | Différenciateur académique : une décision de renoncement argumentée par la mesure | Matière archivée ; le réexamen du 20 octobre en ferme le récit |
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
| Critique | 1 | R16 | Hebdomadaire |
| Élevé | 5 | R29, R19, R10, R20, R1 | À chaque jalon |
| Modéré | 14 | R23, R28, R3, R12, R7, R4, R5, R13, R15, R17, R18, R22, R21, R24 | Périodique |
| Faible | 4 | R2, R11, R14, R9 | Surveillance simple |
| Éteints | 5 | R26, R27, R6, R25, R8 | Archivés |
| **Total** | **29** | **dont 1 nouveau en v8 : R29** | **—** |

**Mouvements de la version 8 :** cinq extinctions (R26, R27, R6, R25, R8) ; quatre baisses (R1 de 12 à 9, R23 de 9 à 8, R5 de 8 à 6, R13 de 9 à 6) ; trois hausses (R16 de 9 à 12, R22 de 4 à 6, R15 de 4 à 6) ; une occurrence traitée (R11) ; un risque nouveau (R29).

**Conclusion.** Le profil de risque change de nature pour la cinquième fois, et plus nettement que jamais : **le produit n’est plus un risque**. Quatre sprints livrés à cent pour cent, une suite de plus de deux mille tests stable, un jalon tenu en avance. Ce qui reste est en aval du code — la recette avec des utilisateurs absents, le déploiement sur un poste pas encore obtenu, le mémoire — et en amont de la soutenance : **la contribution visible de chaque équipier**. C’est le seul risque critique, et le seul que personne d’autre que le binôme ne peut traiter.

# **9. Modalités de mise à jour**

- À chaque fin de phase : révision des cotations, clôture des risques éteints, ajout des risques nouvellement identifiés.

- À chaque anomalie de recette résolue : consignation de la cause profonde, de la mesure appliquée et de son efficacité, au titre des leçons apprises.

- À chaque jalon : revue complète des risques de criticité supérieure ou égale à 9 avec l’encadrant.

- **Réévaluations programmées :** R16 au 2 novembre, après l’attribution des porteurs ; R29, R1 et R10 à la fin de la phase 6 ; R17 dès que la tenue de J2 est établie ; R22 après correction de l’anomalie d’impression ; R15, R20, R21, R9 et R24 pendant la phase 7 ; R28 avant la rédaction du chapitre de conception ; R7, R4 et R13 à chaque envoi de chapitre.

- Version unique : ce document est la seule source de vérité du registre. Toute modification donne lieu à une version datée qui remplace la précédente dans les connaissances du projet.

*Document vivant — version 8 du 23 octobre 2026. Remplace la version 7 du 10 octobre 2026. Intègre la clôture du sprint 4, le jalon J3 et la validation du maintien de l’architecture par l’encadrant.*
