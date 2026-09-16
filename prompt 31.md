# Prompt 31 — US-PLAN-03 · Générer le programme hebdomadaire du centre

Sprint 2, story 12 sur 12, la dernière. Must, 8 points. Application
`planification`, paquetage P5. Risque R6, criticité 9.

## 0. Étape 0 — vérifications avant toute ligne de code

1. US-PLAN-04 est-elle livrée, commitée, suite `pytest` verte ? Si non, arrête-toi
   et rends-m'en compte : cette story ne peut pas commencer sans le contrôleur.
2. `ServiceContraintes` : signature réelle de `verifier` et `verifier_lot`,
   structure du `Contexte`, forme d'une violation, et surtout —
   LE CONTEXTE ACCEPTE-T-IL DES SÉANCES PROVISOIRES, non encore écrites ? La
   génération gloutonne place une candidate, puis vérifie la suivante contre un
   état qui inclut ce placement. Si le chargeur de contexte ne sait pas recevoir
   d'ajouts provisoires, c'est une extension à faire DANS `ServiceContraintes`,
   jamais un contournement dans la stratégie. Dis-moi ce qu'il en est avant de
   coder.
3. `ServiceEcritureSeance` : signature, et ce qu'il vérifie. La génération écrit
   par lui, sans exception — c'est le garde mécanique posé à US-PLAN-04.
4. La sémantique d'ordre de `verifier_lot` telle que tu l'as implantée, et la
   distinction entre conflit avec l'existant et conflit avec une candidate
   antérieure du même lot.
5. `GrilleHoraire` active et ses créneaux, calcul de portée d'une
   `PeriodeCalendrier`, effectif réel d'une brigade, salle attitrée : noms exacts.
6. Le paramètre BNF-13 pour la borne de temps de génération existe-t-il ? Sinon,
   crée-le (§ 6).

## 1. Ce que porte cette story

Besoins BF-PLAN-03 et BF-PLAN-12. Cas d'utilisation CU-P5-01, fiche détaillée.
Règles RG-31, RG-32, RG-33, RG-33 bis. Séquence SEQ-01. Classe CLS-04.
Acteur : cellule planification.

Critères d'acceptation du backlog v8 :

1. La génération porte sur une semaine et une ou plusieurs brigades
   sélectionnées, appartenant le cas échéant à des sessions différentes.
2. La résolution tient compte des affectations existantes de toutes les sessions
   actives sur la semaine, quelle que soit l'étendue de la sélection.
3. Les matières dont le volume prescrit est épuisé ou dont les prérequis ne sont
   pas achevés sont écartées de la génération.
4. Chaque séance générée comporte une matière, un instructeur, un créneau et,
   lorsque la matière l'exige, un lieu partagé.
5. Les matières se déroulant en salle attitrée reprennent automatiquement la
   salle de la brigade.
6. Les matières ne requérant aucun lieu sont placées sans réservation.
7. La génération produit un programme à l'état brouillon.
8. Un compte rendu indique le nombre de séances placées et les éventuelles
   séances non placées avec leur motif.

## 2. Sélection libre, résolution centre-entier — et un seul programme par semaine

Deux choses à ne jamais confondre.

CE QUE L'ON ÉCRIT : les séances des brigades SÉLECTIONNÉES, et elles seules.
CE QUE L'ON LIT : les affectations existantes de TOUTES les sessions actives sur
la semaine, plus les séances verrouillées, quelle que soit la sélection.

C'est le critère 2 et l'enchaînement A1 : « sans cette portée, RG-34 n'est pas
vérifiable et le résultat dépend de l'ordre de traitement des sessions ». Un
instructeur affecté lundi matin à une brigade non sélectionnée doit être vu comme
occupé.

LE PIÈGE STRUCTUREL, à traiter avant tout le reste. `ProgrammeHebdomadaire` porte
une UNICITÉ sur le lundi de semaine : il existe AU PLUS UN programme par semaine,
et il couvre le centre entier (RG-33 bis). Donc :

- générer pour les brigades A et B crée le programme de la semaine s'il n'existe
  pas, ou COMPLÈTE celui qui existe ;
- générer ensuite pour C et D AJOUTE des séances au MÊME programme, sans toucher
  à celles de A et B ;
- un générateur qui crée un programme à chaque appel violera l'unicité au second
  lancement — ou, s'il « corrige » en remplaçant, détruira le travail fait pour
  les autres brigades.

Écris ce point en tête de ta décision : c'est la conséquence directe de RG-33 bis
et le défaut le plus coûteux que cette story puisse produire.

RÉGÉNÉRATION (A3), chirurgicale :

- les séances des brigades SÉLECTIONNÉES et NON VERROUILLÉES sont supprimées puis
  reconstruites ;
- les séances VERROUILLÉES des brigades sélectionnées sont PRÉSERVÉES, qu'elles
  l'aient été manuellement ou parce qu'elles portent un contrôle programmé ;
- les séances des brigades NON sélectionnées ne sont jamais touchées, seulement
  lues comme contraintes.

Le tout en une seule transaction. Une régénération interrompue à mi-chemin
laisserait la semaine amputée.

CAS PARTICULIER DE LA SÉANCE REGROUPÉE : une séance portant des lignes de
plusieurs brigades, dont certaines sélectionnées et d'autres non. Décide et
justifie — je penche pour la préserver intégralement et le signaler au compte
rendu, la détruire partiellement n'ayant pas de sens. Le regroupement est
US-PLAN-06, sprint 3, mais la structure existe déjà et le cas peut survenir dès
qu'une séance verrouillée en porte une.

## 3. La stratégie de génération — interface dès maintenant

`ServiceGeneration` orchestre : charger le contexte, construire les candidates,
appeler une STRATÉGIE, écrire le résultat, produire le compte rendu.

La stratégie est derrière une interface. Une seule implantation aujourd'hui,
`StrategieGloutonne`. La seconde, `StrategieSolveur`, est US-PLAN-08, Should,
sprint 4, décidée au jalon J2 du 10 octobre.

POURQUOI UNE ABSTRACTION ICI ALORS QUE J'EN AI DÉCONSEILLÉ UNE AU PROMPT 27 pour
les modèles de période — écris-le, la question reviendra. Là-bas, trois cas se
RESSEMBLAIENT sans qu'on sache s'ils évolueraient ensemble. Ici, la seconde
implantation est DÉJÀ SPÉCIFIÉE — CU-P5-06 est formellement « extension de
CU-P5-01 » — et la comparaison des deux approches sur les mêmes données est un
livrable attendu du mémoire. On n'abstrait pas sur une ressemblance ; on abstrait
sur une variation connue.

Le choix de stratégie est un PARAMÈTRE BNF-13, jamais une branche de code. Même
avec une seule implantation disponible.

L'interface reçoit le contexte et les cases à pourvoir, et retourne des
placements retenus plus des non-placements motivés. Elle N'ÉCRIT RIEN : c'est
`ServiceGeneration` qui écrit, par `ServiceEcritureSeance`. Une stratégie qui
écrit ne peut pas être comparée à une autre sur les mêmes données.

## 4. L'heuristique gloutonne — l'ordre est l'algorithme

Déroulé :

1. projeter les créneaux types de la GRILLE ACTIVE sur les dates de la semaine ;
2. retirer ceux que le calendrier bloque, compte tenu de la portée de chaque
   période et de la brigade concernée — n'oublie pas les périodes de portée
   centre entier ;
3. déterminer, pour chaque brigade sélectionnée, les matières PROGRAMMABLES :
   prérequis achevés, volume prescrit non épuisé (critère 3) ;
4. parcourir les cases dans l'ordre de priorité et, pour chacune, essayer les
   candidates dans l'ordre de préférence jusqu'à ce que `ServiceContraintes` en
   accepte une ;
5. case non pourvue si aucune ne passe, avec son motif.

L'ORDRE DE PRIORITÉ EST LE CŒUR DE LA STORY. Principe à appliquer : le plus
contraint d'abord. Une matière que deux instructeurs seulement savent enseigner,
ou qui exige un lieu rare, se place avant une matière que tout le monde peut
donner n'importe où. L'inverse remplit les créneaux avec le facile et laisse le
difficile sans place.

Critères de tri à combiner, dans cet ordre de poids :
- nombre d'instructeurs qualifiés et disponibles pour la matière, croissant ;
- rareté du lieu requis ;
- volume restant à programmer rapporté au temps restant dans la session,
  décroissant — une matière en retard passe avant une matière confortable.

DÉTERMINISME OBLIGATOIRE. Deux lancements sur les mêmes données produisent le
même programme. Tout tri doit avoir un départage stable en dernier recours —
identifiant, désignation — jamais l'ordre naturel d'une requête sans `order_by`.
Même exigence qu'à US-SES-06 pour la proposition de répartition, et pour la même
raison : une proposition qui change à chaque essai est inexploitable.

Le choix de l'instructeur, à contraintes égales, suit la charge d'enseignement
courante croissante. C'est le premier critère non éliminatoire de RG-43, déjà
arbitré pour les remplaçants ; le réemployer ici évite deux règles de préférence
divergentes dans le même système.

INTERDITS :

- RG-33, structurante : « la génération NE CHERCHE JAMAIS À ALIGNER LES
  PROGRESSIONS des brigades d'une même session. Le décalage est une contrainte
  métier à préserver. » Aucun mécanisme qui synchroniserait deux brigades, aucun
  tri qui rapprocherait leurs avancements. Un test doit le prouver : deux
  brigades d'une même session, l'une en avance, génèrent des programmes
  différents sans convergence.
- Aucune contrainte dure évaluée dans la stratégie. Toutes passent par
  `ServiceContraintes`. Si tu écris quelque part « si l'instructeur est déjà
  pris », tu viens de créer la divergence que US-PLAN-04 existe pour empêcher.
- Aucun retour en arrière. Une heuristique gloutonne ne revient pas sur ses
  placements ; c'est sa limite assumée, et c'est ce que le solveur viendra peut-
  être corriger. Ne bricole pas un demi-retour-arrière : il serait ni explicable
  ni comparable.

A4 — SÉANCE SUR PLUSIEURS CRÉNEAUX. Le modèle le permet : la séance porte ses
heures réelles et aucune référence à un créneau type. La génération, elle, produit
UNE SÉANCE PAR CRÉNEAU. Consigne ce choix : fusionner des créneaux consécutifs
est une optimisation de confort qui complique l'heuristique sans rien changer au
volume programmé, et le cas reste servi par la saisie manuelle (US-PLAN-05) et,
le cas échéant, par le solveur.

A5 — CRÉNEAU VIDE. Présenté comme tel, avec la mention AD/GROUPEMENT à
l'affichage, conformément à l'usage du centre. Ce n'est pas une séance : rien
n'est écrit en base pour un créneau vide.

## 5. Les lieux — critères 4, 5 et 6

Trois cas, déterminés par la catégorie de lieu requise déclarée sur l'élément de
référentiel (US-REF-04) :

- SALLE ATTITRÉE : la séance reprend AUTOMATIQUEMENT la salle de la brigade
  (critère 5). Pas de recherche, pas de choix. Si la brigade n'a pas de salle
  attitrée, la case n'est pas pourvue et le motif le dit clairement — c'est un
  défaut de préparation, pas un échec de génération.
- LIEU PARTAGÉ : recherche d'un lieu libre, de capacité suffisante, de mode de
  partage compatible. `ServiceContraintes` tranche ; la stratégie propose.
- SANS LIEU : la séance est placée sans réservation (critère 6), `lieu` nul.

Ceci referme D-34 : « contrainte de catégorie de lieu au moteur ». Prouve-le par
un test des trois cas, pas par une déclaration.

## 6. Les exceptions

E1 — AUCUN CRÉNEAU OUVERT, semaine entièrement bloquée : le système l'indique
SANS PRODUIRE DE PROGRAMME. N'écris pas un `ProgrammeHebdomadaire` vide : il
occuperait l'unicité de la semaine et la génération suivante croirait devoir le
compléter.

E2 — AUCUNE MATIÈRE PROGRAMMABLE : énumérer les matières et LE MOTIF DE BLOCAGE
de chacune — volume épuisé, prérequis inachevé et lequel.

E3 — AUCUN INSTRUCTEUR QUALIFIÉ DISPONIBLE. Le motif porte la matière, LA LISTE
DES INSTRUCTEURS QUALIFIÉS, et LA CAUSE D'INDISPONIBILITÉ DE CHACUN — déjà affecté
à telle brigade, indisponibilité déclarée du tant au tant. C'est le vrai coût du
compte rendu et la partie la plus utile de la story : « aucun instructeur
disponible » ne dit pas quoi corriger, la liste nominative si.

E4 — AUCUN LIEU PARTAGÉ DISPONIBLE : signaler le conflit et proposer soit un
autre créneau de la semaine où le lieu est libre, soit le report de la matière.
Une proposition, pas une action.

E5 — DÉPASSEMENT DU TEMPS. BNF-04 borne à cinq minutes. Le système retourne LA
MEILLEURE SOLUTION ADMISSIBLE OBTENUE, en signalant l'interruption. IL NE RETOURNE
JAMAIS RIEN.
Avec une heuristique gloutonne le dépassement est improbable — le temps est
proportionnel au nombre de cases. IMPLANTE LA BORNE QUAND MÊME : elle appartient
à l'interface de stratégie, elle sera indispensable au solveur, et elle protège
d'un défaut qui ferait boucler la génération. Borne en paramètre BNF-13, jamais
en dur.

E6 — AUCUNE GRILLE ACTIVE : génération impossible, message renvoyant vers la
gestion des grilles. Ceci referme le report posé à US-PLAN-12.

## 7. Le compte rendu — le livrable visible

Critère 8. Il porte :

- le nombre de séances placées, par brigade ;
- les cases non pourvues, avec pour chacune le créneau, la brigade, et LE MOTIF
  DÉTAILLÉ selon le § 6 ;
- les matières écartées d'emblée, avec leur motif (critère 3) ;
- le volume programmé et le volume restant PAR MATIÈRE ET PAR BRIGADE — c'est le
  point 6 du scénario nominal, et c'est ce que la cellule pédagogique lira ;
- les séances verrouillées préservées ;
- le cas échéant, la mention d'interruption pour dépassement de temps.

DISTINGUE, dans les motifs de non-placement, le conflit avec une séance
EXISTANTE du conflit avec une candidate PLACÉE PLUS TÔT DANS LA MÊME GÉNÉRATION.
Les deux appellent des actions différentes : la première se corrige en amont, la
seconde signale une tension de ressource que l'ordre de priorité n'a pas su
résoudre. C'est la distinction demandée à US-PLAN-04 ; sers-t'en ici.

Le compte rendu n'est PAS enregistré en base : c'est un résultat d'exécution,
présenté à l'écran et imprimable. La journalisation, elle, retient l'acte de
génération avec la semaine, les brigades sélectionnées, le nombre de séances
créées et supprimées, et l'auteur — le compte, pas le détail.

## 8. RG-31 et RG-32

RG-31 : la génération produit un BROUILLON. Elle ne diffuse rien, ne soumet rien,
ne valide rien, ne notifie personne. Aucun passage d'état.

RG-32, structurante : UNE LIGNE PAR BRIGADE, y compris pour une séance partagée.
La structure existe depuis US-PLAN-04 ; ici elle se remplit. L'affichage du
programme se fait par brigade, et une séance regroupée apparaît dans le programme
de chacune.

## 9. Écrans

Rubrique Planification, domaine de la cellule planification.

- ÉCRAN DE LANCEMENT : choix de la semaine, sélection des brigades — présentées
  par session, avec la possibilité d'en choisir de plusieurs sessions (critère 1).
  Indication de la grille active et du programme déjà existant pour cette semaine
  s'il y en a un, avec le nombre de séances par brigade : l'agent doit savoir
  qu'il complète ou qu'il régénère AVANT de lancer.
- CONFIRMATION avant régénération, nommant les brigades dont les séances non
  verrouillées vont être supprimées et leur nombre (BNF-09).
- COMPTE RENDU (§ 7).
- CONSULTATION DU PROGRAMME de la semaine : grille hebdomadaire, une ligne par
  brigade, créneaux vides portant AD/GROUPEMENT. Filtre par brigade et par
  session.

IMPRESSION. RG-33 bis : « le programme couvre le centre entier pour une semaine.
L'IMPRESSION PAR JOURNÉE EST UN FORMAT DE SORTIE. » Autrement dit, ne modélise
rien par journée : c'est une mise en page. Mesure la largeur imprimable, portrait
et paysage, et reporte-la dans `IMPRESSION-ANALYSE.md` — le programme
hebdomadaire est le document le plus large du système et probablement le second,
après le calendrier annuel, dont le paysage est le format naturel.

Aucune action d'écriture sur la séance depuis ces écrans : modifier une
affectation est US-PLAN-05, sprint 3.

## 10. Performance et risque R6

Mesure, sur un jeu représentatif — plusieurs sessions actives, une dizaine de
brigades, une semaine complète — et reporte dans ton compte rendu :

- le temps total de génération ;
- le nombre de requêtes SQL, qui doit être BORNÉ et indépendant du nombre de
  cases : le contexte se charge une fois ;
- le nombre d'appels à `ServiceContraintes` ;
- le taux de remplissage obtenu, c'est-à-dire la proportion de cases pourvues.

Ces quatre chiffres sont la ligne de base à laquelle le prototype du solveur sera
comparé au jalon C2, puis la décision d'US-PLAN-08 au jalon J2. Sans eux, la
comparaison n'a pas de référence et le prototype ne prouve rien.

N'importe `ortools` nulle part. Le prototype vit hors de l'application, dans son
propre dossier d'étude, avec ses propres dépendances, exclu du paquet de
déploiement et de `test_dependances.py`. Cette story ne le touche pas.

## 11. Ce que cette story referme

Six reports. VÉRIFIE CHACUN PAR UN TEST — D-50 a déclaré refermé un report qui
ne l'était pas, et il a fallu quatre jours pour s'en apercevoir.

- D-34, critères 3 et 4 d'US-REF-04 : contrainte de catégorie de lieu exploitée
  par le moteur. § 5.
- D-39, critères 3 et 4 d'US-REF-06 : prérequis exploités par le moteur.
  Critère 3.
- D-35, volet séance : source des prérequis pour la séance.
- Critère 5 d'US-PLAN-01 : périodes bloquantes exclues à la génération.
- E6 et le refus de générer sans grille active, reporté à US-PLAN-12.
- Critère 6 d'US-PLAN-12 : changer de grille active ne modifie pas les séances
  passées. Report dont la fermeture consiste à CONSTATER qu'aucun code ne le fait :
  un test qui change la grille active et vérifie qu'aucune séance existante n'a
  bougé.

Restent ouverts : E2 et A3 d'US-PLAN-01 (séances impactées par une période
bloquante, vers US-PLAN-05 et US-PLAN-09), et l'état de D-51 selon ce que tu as
tranché à US-PLAN-04.

Donne le compte final du tableau des reports pour la revue du 26 septembre, à
partir du compte vérifié sur le code dans `AVANCEMENT.md`. C'est le premier point
de l'ordre du jour, et l'écart avec le chiffre annoncé à la revue précédente doit
être expliqué, pas corrigé en silence.

## 12. Tests attendus

Groupe A — portée et unicité du programme

A1. Génération sur deux brigades d'une semaine vierge : un programme créé, ses
    séances rattachées aux bonnes brigades, état BROUILLON.
A2. Génération sur deux autres brigades de la MÊME semaine : le MÊME programme
    est complété, les séances des premières brigades intactes. Test du § 2 ;
    c'est celui qui attrape le défaut structurel.
A3. Aucune violation de l'unicité `lundi_de_semaine` après plusieurs générations.
A4. Critère 2 : un instructeur affecté à une brigade NON sélectionnée est vu
    comme occupé. Test de la résolution centre-entier.
A5. Brigades de DEUX SESSIONS différentes dans la même sélection — accepté.

Groupe B — régénération

B1. Régénération sur une sélection : séances non verrouillées des brigades
    sélectionnées supprimées et reconstruites.
B2. Séances VERROUILLÉES des brigades sélectionnées préservées.
B3. Séances des brigades NON sélectionnées intactes.
B4. Transaction : échec au milieu d'une régénération, vérifie que rien n'a été
    supprimé ni créé.
B5. Séance regroupée à cheval sur une brigade sélectionnée et une non
    sélectionnée : le comportement retenu au § 2, testé et signalé au compte
    rendu.

Groupe C — heuristique

C1. Déterminisme : deux générations sur les mêmes données produisent exactement
    le même programme.
C2. Ordre de priorité : une matière à deux instructeurs qualifiés est placée
    avant une matière à dix, sur un jeu construit pour que l'ordre inverse
    échoue. Test de la règle du plus contraint d'abord.
C3. RG-33 : deux brigades d'une même session à des avancements différents —
    aucun rapprochement de leurs progressions. Nomme le test pour que la règle
    structurante soit lisible.
C4. Critère 3 : matière au volume épuisé écartée ; matière à prérequis inachevé
    écartée ; les deux motifs distincts au compte rendu.
C5. Choix d'instructeur à contraintes égales : celui dont la charge courante est
    la plus faible.
C6. Aucune contrainte dure n'est évaluée hors de `ServiceContraintes` — test
    d'architecture ou revue explicite, dis comment tu t'en assures.

Groupe D — lieux

D1. Matière en salle attitrée : la séance reprend la salle de la brigade, sans
    recherche.
D2. Brigade sans salle attitrée, matière l'exigeant : case non pourvue, motif
    explicite.
D3. Matière en lieu partagé : lieu libre et de capacité suffisante retenu.
D4. Matière sans lieu : séance placée, `lieu` nul.
D5. Les trois cas dans une même génération.

Groupe E — exceptions

E1. Semaine entièrement bloquée : indication, ET AUCUN programme créé en base.
    Les deux assertions.
E2. Aucune matière programmable : énumération avec motif par matière.
E3. Aucun instructeur disponible : le motif porte la matière, la liste NOMINATIVE
    des instructeurs qualifiés et la cause propre à chacun. Vérifie le CONTENU,
    pas la présence d'un message.
E4. Aucun lieu partagé libre : proposition d'un autre créneau ou du report.
E5. Borne de temps : avec une borne fixée très bas, la génération s'interrompt et
    retourne les placements déjà obtenus, jamais rien. Signalement présent.
E6. Aucune grille active : génération refusée, renvoi vers la gestion des grilles.

Groupe F — compte rendu

F1. Nombre de séances placées par brigade, exact.
F2. Volume programmé et volume restant par matière et par brigade, exacts.
F3. Un non-placement dû à une séance EXISTANTE et un non-placement dû à une
    candidate PLACÉE PLUS TÔT portent des motifs distincts et reconnaissables.
F4. Le compte rendu n'est pas enregistré en base.
F5. La journalisation porte semaine, brigades, comptes et auteur — pas le détail
    des séances.

Groupe G — cycle HTTP réel

G1. Chemin nominal, profil planification : GET de l'écran de lancement, POST de
    génération, compte rendu rendu à l'écran, séances en base.
G2. POST de régénération avec confirmation, nommant les brigades concernées.
G3. Consultation du programme : une ligne par brigade, créneaux vides portant
    AD/GROUPEMENT réellement présents dans la réponse. Leçon de P-25.
G4. Refus d'habilitation sur les adresses d'écriture : pédagogique, examens,
    Direction de Formation, administrateur.
G5. Lecture accordée aux quatre profils habilités.
G6. Test de garde du sprint 1 : passe sans modification.
G7. Navigation : les écrans sont atteignables pour un profil planification.

Groupe H — fermeture des reports

Un test nommé par report du § 11, y compris celui qui CONSTATE qu'un changement
de grille active ne déplace aucune séance existante.

Groupe I — architecture et performance

I1. `tests/architecture` en entier.
I2. Toute écriture de séance passe par `ServiceEcritureSeance` — le garde de
    US-PLAN-04 doit couvrir la génération.
I3. Nombre de requêtes SQL borné et indépendant du nombre de cases.
I4. Aucune classe au-delà de 200 lignes. La stratégie gloutonne est le candidat
    évident ; sépare la construction des candidates, le tri et la boucle de
    placement.

## 13. Définition de fini

Implanté, testé, relu par le sous-agent, commité. Suite `pytest` complète verte.
Génération lancée RÉELLEMENT dans un navigateur sur un jeu de démonstration
comportant plusieurs sessions, avec au moins un créneau non pourvu pour vérifier
le compte rendu à l'œil. Mesures du § 10 reportées. Mesure d'impression reportée.
`DECISIONS.md` à jour le jour même. Case cochée dans `docs/suivi/sprint-2.md`,
sprint 2 clos.

## 14. Ce que tu ne touches pas

Le backlog, le cahier des charges, le registre des risques, le diagramme de
classes.

`ServiceContraintes` : sauf pour l'extension du contexte provisoire (§ 0.2), qui
se fait DANS ce service et non à côté.

US-PLAN-05 (modification manuelle), US-PLAN-06 (regroupement), US-PLAN-08
(optimisation), US-VAL-01 à 04 (validation). Aucune anticipation, aucun import
d'`ortools`, aucun code d'optimisation « qui servira ».

Le prototype du solveur : hors application, dossier d'étude séparé, hors paquet
de déploiement.

## 15. Ce que tu me rends

- La réponse au § 0.2 sur le contexte provisoire, et comment tu l'as traitée.
- La règle de priorité retenue, énoncée en cinq lignes lisibles par un
  non-informaticien. Elle ira telle quelle dans le mémoire.
- Le comportement retenu pour la séance regroupée à cheval (§ 2).
- Les quatre mesures du § 10.
- Le décompte final du tableau des reports, avec le test qui prouve chaque
  fermeture.
- Les entrées `DECISIONS.md` : un seul programme par semaine et ce qu'en implique
  la génération partielle, régénération chirurgicale, interface de stratégie et
  pourquoi l'abstraction se justifie ici, une séance par créneau plutôt que
  fusion (A4), borne de temps en paramètre.
- Le compte des tests par groupe et le total de la suite.
- Le temps réellement passé, à la demi-heure près. DOUZIÈME ET DERNIÈRE MESURE DU
  SPRINT : avec les onze précédentes, la clé de conversion doit être tranchée
  pour les 169 points restants, et c'est une condition de franchissement du jalon
  C2 du 26 septembre.