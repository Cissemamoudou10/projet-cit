# Prompt 28 — US-PLAN-01 · Élaborer le calendrier académique annuel

Sprint 2, story 9 sur 12. Must, 8 points. Application `ressources`, paquetage P4.
La plus grosse story du sprint.

## 0. Étape 0 — vérifications et arbitrage avant toute ligne de code

1. POINT BLOQUANT. Lis le § 5.4 du diagramme de classes v4 (« La période de
   calendrier à cibles multiples ») et le critère 4 du backlog v8. Ils se
   contredisent, § 2 de ce prompt. NE CODE PAS la contrainte de chevauchement
   avant d'avoir rendu l'arbitrage par écrit et d'avoir mon accord.
2. `NatureEvenement` est marquée `<<paramétrable>>` dans CLS-03 : c'est une
   ENTITÉ, pas une énumération. Vérifie-le et mesure ce que cela ajoute (§ 3).
3. Le patron de gestion : `NatureEvenement` en relève-t-elle telle quelle, comme
   `TypeFormation` à US-REF-00 ? Cite le précédent.
4. Comment `IndisponibiliteInstructeur` (US-INS-03) exprime sa période et son
   non-chevauchement : `ExclusionConstraint` avec `btree_gist`, bornes
   semi-ouvertes, comportement retenu. Cette story pose un troisième modèle de
   période ; la cohérence de traitement des bornes n'est pas négociable.
5. `DEPENDANCES_AUTORISEES` : confirme `ressources` → `organisation`. Cette story
   pose la DEUXIÈME association traversant dans ce sens, après `SalleAttitree`.
   Si elle passe sans heurt, l'arbitrage d'US-SES-03 est confirmé par l'usage —
   dis-le, c'est un élément de soutenance.
6. Le domaine d'habilitation de la cellule planification, déjà employé pour les
   lieux et les indisponibilités.
7. Suite `pytest` verte avant de commencer.

## 1. Ce que porte cette story

Besoin BF-PLAN-01. Cas d'utilisation CU-P4-05. Règles RG-28, RG-29, RG-30 et
RG-30 bis. Séquence SEQ-01. Classe CLS-03.
Acteur : cellule planification.

Critères d'acceptation du backlog v8 :

1. Le calendrier couvre une année de formation et distingue les types de
   périodes : cours, conférences, visites, congés, examens, bivouacs et
   formations techniques.
2. Une période comporte un début et une fin exprimés avec une granularité
   horaire, permettant de couvrir aussi bien une conférence de deux heures qu'un
   bivouac d'une semaine.
3. Une période peut occuper une fraction de journée, le reste de la journée
   demeurant disponible pour d'autres séances.
4. Les périodes ne peuvent se chevaucher pour une même session. — VOIR § 2.
5. Les périodes bloquées sont exclues automatiquement lors de la génération du
   programme hebdomadaire. — REPORT, § 9.
6. Le calendrier est consultable sous forme de vue annuelle.

HORS PÉRIMÈTRE : les grilles horaires et les créneaux types (US-PLAN-12, même
sprint), la génération (US-PLAN-03), les contraintes dures (US-PLAN-04).

## 2. Le critère 4 contre le § 5.4 — arbitrage à rendre avant de coder

LE BACKLOG dit : « Les périodes ne peuvent se chevaucher pour une même session. »
LA FICHE, E1, dit : « Deux périodes bloquantes de MÊME PORTÉE se recouvrent :
refus avec désignation de la période en conflit. »
LE DIAGRAMME DE CLASSES v4, § 5.4, dit : « RG-29 s'assouplit : le
non-chevauchement ne peut plus se contrôler à portée égale, deux ensembles
pouvant se recouper partiellement. SEUL LE DOUBLON EXACT EST REFUSÉ ; toute autre
intersection donne un AVERTISSEMENT, les périodes se cumulant sans se
contredire. »

Les deux premiers supposent une portée unique et comparable. Le troisième
constate que la portée est un COUPLE D'ENSEMBLES, et qu'« une même session » ne
désigne plus rien d'univoque : une période ciblant les sessions A et B et une
autre ciblant B et C se recoupent sur B, partiellement, sans être en conflit.

ARBITRAGE QUE JE RECOMMANDE, à me faire confirmer avant de coder : appliquer le
§ 5.4. Refuser le seul DOUBLON EXACT — mêmes bornes, même ensemble de sessions,
même ensemble de brigades — et avertir sur toute autre intersection, sans
bloquer. Motif : c'est la seule règle exprimable sur le modèle réellement retenu,
et les deux autres formulations ont été écrites avant que les cibles multiples ne
soient tranchées.

ATTENTION AU RAISONNEMENT, il n'est pas celui des arbitrages précédents. Ici le
document le plus RÉCENT (backlog v8, 8 septembre) est le moins précis, et le plus
ancien (diagramme v4, 30 août) porte le raisonnement. Ce n'est donc pas la date
qui tranche, ni le rang du document : c'est qu'une règle doit être exprimable sur
le modèle qu'on implante. Écris-le en ces termes dans `DECISIONS.md` — trois
arbitrages backlog/livrable ont déjà été rendus dans ce sprint, et un lecteur
demandera selon quel principe.

Conséquence sur les livrables, ligne « Impact » : le critère 4 du backlog et E1
de la fiche sont à corriger par le chef de projet.

## 3. `NatureEvenement` — une entité, pas une énumération

CLS-03 la marque `<<paramétrable>>` : `libelle` et `effetParDefaut`. C'est une
table avec son écran de gestion, pas un `TextChoices`.

Cela ajoute à cette story l'équivalent d'US-REF-00 : un petit CRUD complet sous
le patron de gestion, plus un jeu de données de départ. Chiffre-le et dis-le-moi :
c'est une part non négligeable des 8 points, et elle n'apparaît dans aucun
intitulé.

Modèle `NatureEvenement`, `Meta.db_table = "ressources_nature_evenement"` :

- `libelle` — texte, unique, insensible à la casse (précédents D-21, D-26).
- `effet_par_defaut` — `EffetPeriode` : bloquant ou informatif.

Service sous le patron de gestion, `CHAMP_UNICITE = "libelle"`, même domaine que
le reste du calendrier. Suppression bloquée par `PROTECT` dès qu'une période
l'utilise, comme `TypeFormation` l'est par `Formation` (D-22).

Jeu de départ, chargé par une migration de données ou par la commande de
démonstration selon le précédent du projet — vérifie lequel. Les sept natures du
critère 1, avec leur effet par défaut d'après RG-29 : congés, examens et bivouacs
BLOQUANTS ; conférences et visites bloquantes pour les brigades concernées, donc
bloquantes par défaut également, leur portée limitant l'effet ; cours,
informative ; période de formation extérieure — décide et justifie.

POURQUOI « effet par défaut » ET NON « effet » : le § 5.4 est explicite, « l'effet
est DISSOCIÉ DE LA NATURE : chaque nature porte une valeur par défaut
SURCHARGEABLE événement par événement ». Un examen peut exceptionnellement être
informatif. La nature propose, la période dispose.

## 4. `PeriodeCalendrier` — le modèle

`app/ressources/models.py`, `Meta.db_table = "ressources_periode_calendrier"`.

D'après CLS-03 :

- `nature` — clé étrangère vers `NatureEvenement`, `on_delete=PROTECT`.
- `intitule` — texte, obligatoire.
- `debut`, `fin` — horodatages. RG-28, structurante : « la journée n'est pas
  l'unité du calendrier ». Bornes semi-ouvertes, cohérentes avec US-INS-03 (§ 0.4).
- `effet` — `EffetPeriode`, pré-rempli depuis `nature.effet_par_defaut` à la
  création, modifiable ensuite. STOCKÉ, parce que surchargeable.
- `sessions` — relation multiple vers `organisation.Session`, éventuellement vide.
- `brigades` — relation multiple vers `organisation.Brigade`, éventuellement vide.

INTERDIT — AUCUN CHAMP `portee`. Le diagramme le marque `/portee` et le § 5.4
explique pourquoi : « un attribut portee renseigné indépendamment des cibles
finirait par les contredire — dire "session" alors que l'ensemble est vide. Le
dériver supprime la classe entière de ces incohérences. »

La portée se CALCULE : les deux ensembles vides, c'est le centre entier ; sinon,
l'union des cibles déclarées. Expose-la en propriété lisible, jamais en colonne.
C'est le même interdit qu'à US-SES-01 pour le référentiel et qu'à US-SES-06 pour
l'effectif réel : le projet en compte maintenant trois, et c'est un point de
soutenance — neuf attributs dérivés identifiés au diagramme, jamais stockés.

Un test doit constater l'absence de la colonne, comme à US-SES-06 : ça ne se voit
pas autrement.

`on_delete` des cibles : la relation multiple ne propose pas `PROTECT`. Décide
explicitement ce qui se passe quand une session ciblée est supprimée — la période
perd-elle cette cible et devient-elle par là même de portée « centre entier », ce
qui serait un élargissement silencieux et dangereux ? Traite le cas : une session
ne devrait pas pouvoir être supprimée tant qu'une période la cible, ou bien la
période doit être supprimée avec sa dernière cible. Argumente et teste.

En base :

- `ck_periode_calendrier_bornes` — `fin > debut`.
- Refus du DOUBLON EXACT (§ 2) : les bornes se contraignent en base, les
  ensembles de cibles non — une unicité portant sur deux relations multiples ne
  s'exprime pas en SQL. Le contrôle est donc en COUCHE SERVICES, et il s'ajoute
  au décompte tenu depuis le début du sprint. Dis où en est ce décompte.

## 5. RG-30 bis — les sessions sont projetées, jamais saisies

« Les dates des sessions sont projetées depuis Session, jamais saisies au
calendrier. Sans cette règle, le même fait serait enregistré à deux endroits et
diverge au premier report — c'est le défaut le plus courant des calendriers
d'établissement. »

Le calendrier a donc DEUX COUCHES :

- les SESSIONS, affichées en bandes de durée, lues depuis `organisation.Session`,
  en lecture seule, sans qu'aucune `PeriodeCalendrier` ne leur corresponde ;
- les ÉVÉNEMENTS, enregistrés comme périodes.

INTERDIT — aucune création automatique de période à l'ouverture d'une session,
aucune synchronisation, aucun rattrapage. Un test doit le prouver : ouvre une
session, vérifie qu'aucune `PeriodeCalendrier` n'est apparue.

Les bandes de session se lisent par la relation, sans import de `organisation`
dans le code de `ressources`... vérifie la méthode D-52 : ici c'est `ressources`
qui dépend de `organisation`, donc l'import est autorisé dans ce sens. Confirme-le
au § 0.5 plutôt que de le supposer.

## 6. La vue annuelle — le vrai coût de cette story

Le critère 6 demande une vue annuelle ; la charte exclut tout framework
JavaScript. Rendu serveur, HTML et CSS.

Le piège : une année à granularité horaire, ce sont plus de huit mille heures. Ne
tente pas une grille annuelle horaire — elle serait illisible et impossible à
imprimer.

Découpage que je recommande, à confirmer ou à discuter :

- VUE ANNUELLE — douze mois, chaque jour portant un marqueur par période qui le
  recoupe, coloré selon l'effet et TOUJOURS doublé d'un mot ou d'un sigle (D-63).
  Les bandes de session en surimpression ou en bandeau. C'est une vue de
  repérage : elle montre QUAND, pas COMBIEN D'HEURES.
- VUE MENSUELLE ou HEBDOMADAIRE — le détail horaire, où RG-28 devient visible :
  une conférence de deux heures y occupe deux heures, et le reste de la journée
  reste vide (critère 3).
- FICHE D'UNE PÉRIODE — bornes, nature, effet, cibles, portée dérivée en toutes
  lettres : « centre entier » ou « sessions X et Y, brigade Z ».

Filtres : année, nature, effet, et surtout CIBLE — voir le calendrier d'une
session ou d'une brigade est le besoin réel de la cellule planification, et c'est
ce que le moteur consommera au sprint 3.

L'ANNÉE DE FORMATION : le critère 1 dit « une année de formation ». Va-t-elle de
janvier à décembre, ou suit-elle un cycle de formation ? Rien ne le dit. Ne
fabrique pas d'entité « année » : filtre par bornes de date, avec le mois de
début d'année en paramètre BNF-13, comme les paramètres de D-33 — jamais en dur.
Et pose la question de terrain : quelle est la borne de l'année de formation au
CIT ?

Impression : cette vue sera affichée et imprimée. Mesure la largeur imprimable en
portrait ET en paysage, et reporte les deux dans `IMPRESSION-ANALYSE.md`. Une vue
annuelle est le premier écran du projet dont le paysage est probablement le
format naturel ; si c'est le cas, dis-le, c'est une information utile au lot des
gabarits imprimables du sprint 4.

## 7. Les exceptions et enchaînements

E1 — chevauchement : traité au § 2.
E3 — période hors des dates de la session ciblée : AVERTISSEMENT, sans blocage.
Implantable dès maintenant, `Session` existe. Septième usage du mécanisme
d'avertissement.
A1 — période de moins d'une journée : « la granularité horaire est native et non
un cas particulier ». Aucun code spécifique ; un test qui le prouve.
A2 — période ciblant une seule brigade : ne bloque pas les créneaux des autres.
Aucun code aujourd'hui — l'effet du blocage appartient au moteur — mais la cible
doit être enregistrée correctement, et c'est testable.
A4 — report d'une période : traité comme suppression puis déclaration. Rien à
coder de spécifique.

## 8. Habilitations

Domaine de la planification, celui des lieux, indisponibilités et calendrier.
Planification en écriture ; pédagogique, examens, Direction de Formation en
lecture ; administrateur aucun accès. Vérifie contre la matrice § 11.2.

`NatureEvenement` relève du même domaine : c'est un paramétrage du calendrier.

## 9. Ce que cette story referme, ce qu'elle reporte

REFERME — aucun report ouvert du tableau.

REPORTE — trois, à consigner sur le modèle de D-23 :

- CRITÈRE 5 et RG-38 : exclusion automatique des périodes bloquantes à la
  génération. Vers US-PLAN-03 et US-PLAN-04, même sprint.
- E2 : période bloquante recouvrant des séances programmées, énumération et
  arbitrage explicite, aucune déprogrammation sans décision de l'utilisateur.
  Vers US-PLAN-03 puis US-PLAN-05.
- A3 : à la suppression d'une période, énumérer les séances qui redeviennent
  programmables. Même destination.

Le compte du tableau des reports monte encore. Donne-le, à partir du compte
vérifié sur le code dans `AVANCEMENT.md`, et non de celui annoncé en revue. Et
dis en une phrase ce qui reste OBSERVABLE de cette story une fois les reports
retirés : un calendrier saisissable, consultable et imprimable, dont l'effet sur
la programmation ne se verra qu'au sprint 3.

## 10. Tests attendus

Groupe A — `NatureEvenement`

A1. CRUD nominal sous le patron, journalisé.
A2. Unicité du libellé, casse indifférente.
A3. Suppression bloquée par `PROTECT` dès qu'une période l'utilise, énumération
    des opposants, ET par le vrai cycle HTTP depuis l'écran de suppression.
A4. Les sept natures du critère 1 sont présentes après chargement initial, avec
    leur effet par défaut.

Groupe B — période, modèle et bornes

B1. Création nominale, journalisée, `effet` pré-rempli depuis la nature.
B2. Surcharge de l'effet : un examen déclaré informatif est enregistré comme tel,
    la nature n'étant pas modifiée. Test du § 3.
B3. Bornes : `fin` antérieure, puis égale au début — refus, vérifié aussi par
    insertion directe en base.
B4. A1 : période de deux heures un mardi matin — enregistrée, sans traitement
    particulier.
B5. Critère 3 : deux périodes le même jour, matin et après-midi, heures
    disjointes — acceptées toutes deux.
B6. Bornes contiguës — comportement identique à celui retenu pour
    `IndisponibiliteInstructeur` (§ 0.4). Si les deux divergent, c'est un défaut,
    signale-le.

Groupe C — cibles et portée dérivée

C1. Aucune cible : la portée dérivée vaut « centre entier ».
C2. Deux sessions ciblées : portée dérivée cohérente, libellée en toutes lettres.
C3. Sessions ET brigades ciblées simultanément — accepté, portée dérivée correcte.
C4. AUCUNE COLONNE `portee` n'existe en base. Vérifie-le explicitement.
C5. Suppression d'une session ciblée : le comportement retenu au § 4, testé. En
    particulier, vérifie qu'une période ne bascule JAMAIS silencieusement en
    portée « centre entier » par disparition de sa dernière cible.

Groupe D — chevauchement, selon l'arbitrage du § 2

D1. Doublon exact — mêmes bornes, mêmes ensembles de cibles — REFUSÉ, période en
    conflit désignée.
D2. Mêmes bornes, ensembles de cibles différents — ACCEPTÉ avec avertissement.
D3. Cibles identiques, bornes partiellement sécantes — ACCEPTÉ avec
    avertissement.
D4. Intersection partielle des ensembles — période ciblant les sessions A et B
    contre période ciblant B et C, bornes sécantes — ACCEPTÉ avec avertissement
    nommant l'intersection. C'est le cas que le § 5.4 décrit et que le critère 4
    ne sait pas exprimer ; nomme le test pour que ce soit lisible.
D5. Deux périodes bloquantes de portées disjointes, bornes sécantes — acceptées
    sans avertissement.

Groupe E — RG-30 bis

E1. L'ouverture d'une session ne crée AUCUNE période de calendrier.
E2. La vue annuelle affiche les bandes de session, lues depuis `Session`.
E3. Modifier les dates d'une session déplace sa bande, sans qu'aucune période
    n'ait été touchée. Test de la projection.

Groupe F — E3 et avertissements

F1. Période ciblant une session, bornes hors des dates de cette session —
    ACCEPTÉE avec avertissement.
F2. Période ciblant deux sessions dont une seule est concernée par les bornes —
    avertissement nommant laquelle.

Groupe G — cycle HTTP réel

G1. Chemin nominal, profil planification, sur chaque adresse d'écriture :
    natures, périodes, cibles, suppression.
G2. Vue annuelle, vue de détail, fiche de période : 200 et contenu réellement
    présent, portée en toutes lettres comprise.
G3. Les avertissements des groupes D et F sont RÉELLEMENT visibles dans la
    réponse HTTP. Leçon de P-25.
G4. Filtre par cible : le calendrier d'une session donnée ne montre que les
    périodes qui la concernent, périodes de portée « centre entier » incluses.
    Test important — l'oubli des périodes centre serait un défaut invisible
    jusqu'au sprint 3.
G5. Refus d'habilitation sur chaque adresse d'écriture : pédagogique, examens,
    Direction de Formation, administrateur.
G6. Lecture accordée aux quatre profils habilités.
G7. Test de garde du sprint 1 : cette story ajoute beaucoup d'adresses
    d'écriture. Il doit passer sans modification.
G8. Navigation : les écrans sont atteignables, la rubrique apparaît pour les
    profils habilités.

Groupe H — architecture

`tests/architecture` en entier. Le sens `ressources` → `organisation` est
exercé une deuxième fois : si le test passe, l'arbitrage d'US-SES-03 est confirmé
par l'usage. Dis-le. Aucune classe au-delà de 200 lignes — les vues calendaires
sont le candidat évident, découpe avant d'y arriver.

## 11. Définition de fini

Implanté, testé, relu par le sous-agent, commité. Suite `pytest` complète verte.
Vue annuelle et vue de détail regardées RÉELLEMENT dans un navigateur, avec une
année portant au moins : une session, une période centre, une période ciblant une
brigade, et une conférence de deux heures. Mesures d'impression portrait et
paysage reportées. `DECISIONS.md` à jour le jour même. Case cochée dans
`docs/suivi/sprint-2.md`.

## 12. Ce que tu ne touches pas

Le backlog, le cahier des charges, le registre des risques, le diagramme de
classes. Les corrections du § 2 s'écrivent en « Impact sur les livrables ».

`Session` et `Brigade` : aucune colonne ajoutée. Les cibles vivent du côté de la
période.

US-PLAN-12, US-PLAN-03, US-PLAN-04 : aucune anticipation. En particulier, aucune
méthode « créneau ouvert ou fermé » qui servirait au moteur — c'est RG-38, et
c'est US-PLAN-04.

## 13. Ce que tu me rends

- L'arbitrage du § 2, rédigé, AVANT de coder la contrainte.
- Le chiffrage de ce que `NatureEvenement` ajoute à la story (§ 3).
- Ton découpage de vues retenu (§ 6) et pourquoi.
- Le comportement retenu à la suppression d'une cible (§ 4).
- Les entrées `DECISIONS.md` : arbitrage du chevauchement et le principe qui le
  fonde, portée dérivée, effet dissocié de la nature, projection des sessions,
  borne de l'année de formation en paramètre et question de terrain associée,
  les trois reports.
- Le décompte à jour des contraintes en couche services et du tableau des
  reports.
- Les mesures d'impression.
- Le compte des tests par groupe et le total de la suite.
- Le temps réellement passé, à la demi-heure près. Neuvième mesure, première sur
  une story à 8 points : c'est celle qui dira si la clé tient sur les grosses
  stories, où elle compte le plus — il en reste deux à 8 points dans ce sprint.