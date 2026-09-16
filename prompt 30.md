# Prompt 30 — US-PLAN-04 · Garantir le respect des contraintes dures

Sprint 2, story 11 sur 12. Must, 8 points. Application `planification`, paquetage P5.

ORDRE MODIFIÉ : cette story passe AVANT US-PLAN-03. CU-P5-02 est un cas
d'utilisation INCLUS, appelé par la génération ; l'écrire après reviendrait à
coder les six contrôles dans la boucle de génération puis à tenter de les en
extraire. La note d'implémentation l'interdit nommément : « une duplication de
ces contrôles entre la génération et la saisie manuelle produirait mécaniquement
des divergences de comportement ». Consigne l'inversion dans `DECISIONS.md`.

## 0. Étape 0 — vérifications avant toute ligne de code

1. L'application `planification` existe-t-elle au squelette (sept applications,
   sprint 1) et figure-t-elle à `INSTALLED_APPS` ? Quelles dépendances
   `DEPENDANCES_AUTORISEES` lui accorde-t-il ? Elle doit pouvoir importer
   `referentiel`, `organisation` et `ressources` — c'est la couche la plus haute
   du graphe. Vérifie, complète si besoin, consigne.
2. Le point de résolution posé dans `noyau` à US-PLAN-12 pour le volume
   hebdomadaire de référence : signature et emplacement. Cette story ne s'en sert
   pas directement, mais elle suit le même motif si elle a besoin d'une donnée
   d'une autre couche.
3. Les modèles dont les six contraintes dépendent, avec leurs noms exacts :
   `ElementReferentiel` et `Prerequis` (`referentiel`), `Brigade`,
   `AffectationBrigade`, `Stagiaire` (`organisation`), `Instructeur`,
   `Qualification`, `IndisponibiliteInstructeur`, `Lieu`, `SalleAttitree`,
   `IndisponibiliteLieu`, `PeriodeCalendrier`, `GrilleHoraire`, `CreneauType`
   (`ressources`). Pour chacun : comment lit-on ce dont j'ai besoin ?
4. La propriété d'effectif réel d'une brigade posée à US-SES-06, et la propriété
   de capacité de salle attitrée posée à US-SES-03.
5. Le calcul de portée dérivée d'une `PeriodeCalendrier` posé à US-PLAN-01 :
   comment détermine-t-on qu'une période couvre une brigade donnée ?
6. Suite `pytest` verte avant de commencer.

## 1. Ce que porte cette story

Besoin BF-PLAN-04. Cas d'utilisation CU-P5-02, fiche détaillée, NATURE INCLUSE,
SANS ACTEUR PROPRE. Règles RG-34 à RG-39. Séquence SEQ-01. Classe CLS-04.

Critères d'acceptation du backlog v8, qui reprennent les six règles :

1. Un instructeur ne peut être affecté à deux séances simultanées, y compris sur
   des brigades différentes.
2. Un instructeur ne peut être affecté qu'à une matière pour laquelle il est
   qualifié.
3. Un lieu partagé ne peut accueillir deux séances simultanées relevant de
   brigades distinctes, sauf regroupement explicite.
4. La capacité du lieu est supérieure ou égale à l'effectif concerné.
5. Aucune séance n'est placée sur une période bloquée par le calendrier annuel ou
   sur une indisponibilité déclarée.
6. Le volume horaire programmé pour une matière n'excède pas le volume prescrit
   par le référentiel de la formation.
7. Une matière ne peut être programmée avant que ses matières prérequises aient
   été dispensées.

CETTE STORY NE LIVRE AUCUN ÉCRAN. Huit points, aucune vue, aucune adresse, donc
AUCUN TEST PAR LE CYCLE HTTP. La règle de couverture HTTP inscrite en définition
de fini au sprint 1 vise les stories qui livrent un écran ; elle ne s'applique
pas ici. Ne la contourne pas, constate qu'elle est hors sujet, et dis-le dans ton
compte rendu — c'est la première story du projet dans ce cas.

## 2. Les trois modèles du paquetage P5

Ils se posent ici, parce que le contrôleur ne peut rien vérifier sans eux. C'est
une charge déplacée depuis US-PLAN-03 ; signale-la dans ton relevé d'heures.

`ProgrammeHebdomadaire`, `Meta.db_table = "planification_programme_hebdomadaire"` :

- `lundi_de_semaine` — date, UNIQUE. « Un seul programme par semaine pour le
  centre » (note d'implémentation § 5.5). C'est RG-33 bis : le programme couvre
  LE CENTRE ENTIER pour une semaine, jamais une brigade.
- `etat` — `EtatProgramme`. Déclare l'énumération complète — brouillon, soumis,
  validé, affiché, rejeté — mais N'IMPLANTE PAS LA MACHINE À ÉTATS : c'est RG-44
  et US-VAL-03, sprint 3. Ici, seul `BROUILLON` est produit.
- `date_soumission`, `date_validation`, `motif_rejet`, `date_signature`,
  `signataire`, `date_affichage` — tous facultatifs, tous nuls à ce stade.
  Pose-les d'après CLS-04 pour éviter une migration de plus au sprint 3, mais
  n'écris aucune logique qui les renseigne.
- `valide_par` — clé étrangère facultative vers l'utilisateur.

Une contrainte de vérification garantissant que seule la valeur `BROUILLON` est
atteignable serait une erreur : elle casserait au sprint 3. Ne la pose pas.

`Seance`, `Meta.db_table = "planification_seance"` :

- `programme` — vers `ProgrammeHebdomadaire`, `CASCADE`. Composition stricte :
  une séance n'existe pas hors de son programme. Même dérogation motivée qu'à
  US-PLAN-12 pour `CreneauType`.
- `element_referentiel` — vers `ElementReferentiel`, `PROTECT`.
- `instructeur` — vers `Instructeur`, `PROTECT`. C'est ce `PROTECT` qui refermera
  D-45 et D-51 — voir § 9.
- `lieu` — vers `Lieu`, FACULTATIF, `PROTECT`. Facultatif parce que les matières
  déclarées sans lieu échappent au contrôle. Ce `PROTECT` referme le volet séance
  de D-54.
- `creneau_type` — vers `CreneauType`, FACULTATIF, `SET_NULL` ou `PROTECT` selon
  ce que tu justifies. RG-64 EXIGE qu'il soit facultatif : « une séance porte ses
  heures réelles et une référence FACULTATIVE au créneau type dont elle est
  issue ». Contrainte de conception consignée à US-PLAN-12 ; ne la trahis pas.
- `debut`, `fin` — horodatages. LES HEURES RÉELLES DE LA SÉANCE, jamais déduites
  du créneau type. Trois comportements en dépendent : une séance peut couvrir
  plusieurs créneaux consécutifs, être placée hors grille, et survivre sans
  changement à un changement de grille active.
- `verrouillee` — booléen. Une séance verrouillée est préservée par la
  régénération (A3 de CU-P5-01) ; les contrôles programmés le sont d'office
  (RG-52 bis). Pose le champ, n'écris pas la logique de régénération.

`LigneProgramme`, `Meta.db_table = "planification_ligne_programme"` :

- `seance` — vers `Seance`, `CASCADE`.
- `brigade` — vers `Brigade`, `PROTECT`.

RG-32, structurante : « le programme porte UNE LIGNE PAR BRIGADE, y compris
lorsque plusieurs brigades partagent la même séance ». C'est pour cela que la
brigade n'est pas un champ de `Seance` : une séance regroupée porte plusieurs
lignes. La structure du regroupement EXISTE DÈS CE MODÈLE, même si le cas
d'utilisation qui l'exploite est US-PLAN-06, sprint 3. Ne la simplifie pas « en
attendant » : tout le calcul de RG-34 en dépend (§ 4).

Unicité : `uq_ligne_programme_seance_brigade`, une brigade au plus une fois par
séance.

Attributs dérivés de CLS-04, JAMAIS STOCKÉS : `dureeHeures` et `estRegroupee` sur
la séance, `volumeCumule` sur la ligne. Le projet en compte désormais plus d'une
douzaine d'occurrences tenues ; un test doit constater l'absence des colonnes.

En base :

- `uq_programme_hebdomadaire_lundi` — unicité de la semaine.
- `ck_seance_bornes` — `fin > debut`.
- `ck_programme_lundi_est_un_lundi` si tu peux l'exprimer, sinon en services :
  `lundi_de_semaine` doit être un lundi. Sans ce contrôle, deux programmes de la
  même semaine coexisteront sous deux dates différentes et l'unicité ne
  protégera rien.

## 3. Le service — forme et contrat

`app/planification/services/contraintes.py`, `ServiceContraintes`. C'est l'un des
huit services métier nommés au dossier d'architecture ; il porte ce nom-là.

DEUX PROPRIÉTÉS NON NÉGOCIABLES :

- IL N'ÉCRIT RIEN. Jamais. C'est l'enchaînement A2 : « le contrôle est appelé pour
  tester une modification envisagée SANS L'APPLIQUER, ce qui permet de présenter
  le verdict à la cellule planification avant qu'elle ne confirme ». Un service de
  contrôle qui écrit ne peut plus servir à prévisualiser. Un test doit constater
  qu'aucun appel ne modifie la base.
- IL RETOURNE TOUTES LES VIOLATIONS, PAS LA PREMIÈRE. C'est E2, et la fiche dit
  pourquoi : « sans quoi la cellule planification corrigerait une contrainte pour
  en découvrir une autre à l'essai suivant ». Interdit donc de sortir au premier
  refus. Les six règles sont évaluées, toutes, et le verdict les porte toutes.

Contrat :

- une AFFECTATION CANDIDATE est un tuple brigade, élément de référentiel,
  créneau — début et fin réels —, instructeur, lieu éventuel ;
- `verifier(candidate, contexte)` renvoie un verdict : accepté, ou refusé avec la
  LISTE des violations. Chaque violation porte le CODE DE LA RÈGLE (RG-34 à
  RG-39) et le message désignant L'ÉLÉMENT EN CAUSE ;
- `verifier_lot(candidates, contexte)` — enchaînement A1 : un ensemble
  d'affectations soumis en une fois pendant une génération, avec le verdict de
  chacune. Ce n'est pas une boucle naïve sur `verifier` : les candidates du lot se
  contraignent MUTUELLEMENT — deux séances du même lot ne peuvent pas prendre le
  même instructeur au même créneau. Si tu traites le lot comme des vérifications
  indépendantes, la génération produira des programmes invalides et le défaut ne
  se verra qu'à la recette. C'est le point le plus subtil de cette story ;
  traite-le, teste-le, et dis-moi comment tu l'as résolu.

MESSAGES DE REFUS, exigence E1 : « le motif désigne LA RÈGLE VIOLÉE ET L'ÉLÉMENT
EN CAUSE — l'instructeur déjà affecté et la brigade concernée, le lieu occupé et
par qui, la matière prérequise non achevée. Un refus non motivé est
inexploitable. » Pas de « contrainte violée », pas de « affectation invalide ».
BNF-10 dans sa forme la plus exigeante du projet.

Performance : ce service sera appelé des centaines de fois par génération, sur le
périmètre du CENTRE ENTIER. Ne fais pas une requête par règle et par candidate.
Charge le contexte de la semaine une fois — séances existantes, indisponibilités,
périodes, qualifications, volumes déjà programmés — et évalue en mémoire. C'est
le risque R6, coté 9 : une implantation naïve donnera des temps qui feront croire
à l'infaisabilité du solveur alors que seul le contrôleur sera en cause.

## 4. Les six règles

RG-34 — UNICITÉ D'AFFECTATION DE L'INSTRUCTEUR, toutes brigades et TOUTES
SESSIONS confondues : pas deux séances distinctes sur des créneaux sécants.
EXCEPTION UNIQUE : la séance regroupée de RG-40 — une seule séance vue par
plusieurs brigades n'est pas deux affectations.
C'est pour cette exception que la règle ne descend pas en base : le contrôle porte
sur les SÉANCES, jamais sur les lignes. Si tu comptes les lignes, toute séance
regroupée sera refusée à tort. Teste les deux cas côte à côte.
Portée : toutes les sessions actives, pas seulement celles de la sélection. C'est
A1 de CU-P5-01 — « sans cette portée, RG-34 n'est pas vérifiable et le résultat
dépend de l'ordre de traitement des sessions ».

RG-35 — QUALIFICATION : l'instructeur est qualifié pour la MATIÈRE DU CATALOGUE,
jamais pour l'élément de référentiel. « L'habilitation est indépendante de la
formation », dit la note de CLS-03. Passe par la matière, pas par le couple
formation-matière.

RG-36 — DISPONIBILITÉ DE L'INSTRUCTEUR : aucun recouvrement avec une
indisponibilité déclarée. Attention aux bornes semi-ouvertes retenues à
US-INS-03 : une séance finissant à 12:00 et une indisponibilité commençant à
12:00 ne se recouvrent pas. Aligne-toi, ne réinvente pas.

RG-37 — LIEU : un lieu partagé n'accueille pas deux séances distinctes sur des
créneaux sécants, sauf regroupement ; sa capacité couvre l'effectif accueilli.
Trois sous-cas à distinguer explicitement :
- matière déclarée SANS LIEU : échappe entièrement au contrôle ;
- matière en SALLE ATTITRÉE : la salle de la brigade, dont l'exclusivité est déjà
  garantie par US-SES-03 — mais la capacité se revérifie ici sur l'effectif réel,
  qui a pu croître depuis l'attribution. C'est la limite consignée à US-SES-03,
  et c'est ici qu'elle se rattrape ;
- LIEU PARTAGÉ : occupation et capacité.
La capacité se compare à l'EFFECTIF RÉEL de la brigade (propriété d'US-SES-06), et
à la SOMME des effectifs en cas de regroupement. Une capacité NON RENSEIGNÉE
signifie « on ne sait pas », jamais « illimité » : la note de CLS-03 est
explicite. Décide et justifie — je recommande de ne pas refuser mais d'avertir,
puisque le refus dur a déjà été posé au moment de l'attribution d'une salle
attitrée ; mais argumente, le cas du lieu partagé sans capacité est différent.
Tiens compte du MODE DE PARTAGE : « un lieu séquentiel n'accueille les brigades
que l'une après l'autre, jamais ensemble » (RG-40). Le champ existe depuis
US-PLAN-02 ; s'il n'est exploité nulle part, c'est ici qu'il commence à l'être.

RG-38 — CRÉNEAU OUVERT : aucune période bloquante du calendrier dont LA PORTÉE
COUVRE LA BRIGADE. Utilise le calcul de portée dérivée d'US-PLAN-01 (§ 0.5).
N'oublie pas les périodes de portée CENTRE ENTIER : elles couvrent toutes les
brigades, et les omettre serait un défaut invisible jusqu'à la recette. Une
période INFORMATIVE ne bloque rien.
Cette règle ferme le critère 5 d'US-PLAN-01 et le critère 4 d'US-INS-03 — voir § 9.

RG-39 — VOLUME ET PRÉREQUIS. Deux volets, et DEUX DÉFINITIONS À ARBITRER, que
personne n'a tranchées :

  (a) QUE COMPTE LE « VOLUME PROGRAMMÉ » ? Les séances de tous les programmes, y
  compris les brouillons, ou seulement celles des programmes validés ou affichés ?
  Compter les brouillons fait qu'un brouillon abandonné bloque le volume ;
  ne pas les compter fait qu'une génération peut dépasser le prescrit sans le
  voir. Je penche pour compter tous les programmes non rejetés, et surtout pour
  EXCLURE DU DÉCOMPTE le programme en cours d'évaluation — sans quoi une
  régénération verrait ses propres séances comme un dépassement. Décide,
  justifie, teste les deux cas.

  (b) QU'EST-CE QU'UN PRÉREQUIS « ACHEVÉ » ? Le backlog dit « avant que ses
  matières prérequises aient été DISPENSÉES ». Dispensé renvoie au volume
  RÉALISÉ, qui n'existera qu'au sprint 4 avec RG-60 — « programmes affichés moins
  non-exécutions déclarées ». Définition opératoire provisoire à retenir : le
  volume PROGRAMMÉ de la matière prérequise pour cette brigade atteint son volume
  prescrit. Consigne-la comme provisoire, rattache le remplacement à US-SUI-01 et
  RG-60, exactement comme D-33 l'avait fait pour le volume hebdomadaire — et note
  que celui-là vient d'être remboursé à US-PLAN-12, ce qui montre que ces dettes
  se referment quand on les écrit.
  Lis les prérequis par `Prerequis` et le contrôle explicite posés à US-REF-06
  (D-40), sans réimplanter la traversée du graphe.

## 5. Le garde mécanique — « sans exception » doit être vérifié

La fiche dit : « le service de contrôle est unique et L'ENSEMBLE DES CHEMINS
D'AFFECTATION Y PASSE, SANS EXCEPTION ». Une phrase pareille ne vaut rien si rien
ne la vérifie. Le sprint 1 l'a appris à ses dépens avec les refus d'habilitation :
36 manquants, découverts par un inventaire, refermés par un test de garde
mécanique inscrit en définition de fini.

Fais la même chose ici :

- toute création ou modification de `Seance` et de `LigneProgramme` passe par UN
  SEUL service d'écriture, qui appelle `ServiceContraintes` avant d'écrire ;
- un TEST D'ARCHITECTURE vérifie qu'aucun autre module du projet n'instancie ni
  ne sauvegarde directement `Seance` ou `LigneProgramme` — hors ce service, les
  migrations, et les fabriques de test. Sur le modèle de
  `test_aucune_vue_n_importe_un_modele`.
- inscris la règle en définition de fini dans `.claude/rules`, comme la règle de
  couverture HTTP l'a été au bloc C du Prompt 19.

Sans ce garde, US-PLAN-03 puis US-PLAN-05 écriront des séances par un chemin
parallèle, et on le découvrira à la recette du sprint 3.

## 6. Ce que cette story ne fait pas

- AUCUN ÉCRAN, aucune adresse, aucune permission nouvelle. Le service est appelé
  par d'autres cas d'utilisation, jamais par un utilisateur.
- AUCUNE GÉNÉRATION. Ni sélection de semaine, ni projection de créneaux, ni
  boucle de placement, ni compte rendu : c'est US-PLAN-03.
- AUCUNE MACHINE À ÉTATS du programme : RG-41 et RG-44, US-VAL-03, sprint 3.
- AUCUN REGROUPEMENT : US-PLAN-06, sprint 3. La STRUCTURE le permet, le cas
  d'utilisation ne s'écrit pas ici.
- AUCUNE OPTIMISATION : US-PLAN-08, Should, sprint 4, décision go/no-go au jalon
  J2. Le prototype CP-SAT est une tâche transverse parallèle, pas cette story.
  N'importe `ortools` nulle part.

## 7. Le prototype du solveur — ce que cette story lui doit

Le prototype CP-SAT tourne en parallèle et doit être dimensionné sur plusieurs
sessions simultanées. Les six règles que tu écris ici sont exactement celles qu'il
devra modéliser.

Rends donc, en plus du code, UNE DESCRIPTION DES SIX CONTRAINTES SOUS FORME
EXPLOITABLE PAR UN MODÈLE CP-SAT : pour chacune, les variables de décision
concernées, la forme de la contrainte — exclusion mutuelle, domaine restreint,
somme bornée —, et sa portée. Une page suffit, dans
`docs/suivi/CONTRAINTES-SOLVEUR.md`.

Ce n'est pas du zèle : le prototype doit être restitué au jalon C2 du
26 septembre avec la réévaluation de R6, et il ne vaudra rien s'il modélise des
contraintes différentes de celles que le système applique.

## 8. Tests attendus

Pas de cycle HTTP (§ 1). En revanche, la couverture des six règles doit être
EXHAUSTIVE : c'est l'unique implantation, et rien d'autre ne la rattrapera.

Groupe A — modèles

A1. Unicité de `lundi_de_semaine` : deux programmes la même semaine — refus, par
    insertion directe en base.
A2. `lundi_de_semaine` qui n'est pas un lundi — refus.
A3. `ck_seance_bornes`, par insertion directe.
A4. Une séance portant DEUX lignes de programme — acceptée. C'est la structure du
    regroupement, elle doit exister dès maintenant.
A5. Unicité ligne : la même brigade deux fois sur une séance — refus.
A6. `creneau_type` nul — accepté. RG-64.
A7. `lieu` nul — accepté. Matière sans lieu.
A8. Aucune colonne `duree_heures`, `est_regroupee`, `volume_cumule` en base.
A9. `PROTECT` : suppression d'un instructeur, d'un lieu, d'un élément de
    référentiel, d'une brigade portant une séance — refus avec énumération.

Groupe B — RG-34

B1. Deux séances distinctes, même instructeur, créneaux sécants, brigades
    différentes — REFUS.
B2. Idem, brigades de DEUX SESSIONS différentes — REFUS. Test central : c'est le
    « toutes sessions confondues » qui fonde la portée centre-entier.
B3. Une SÉANCE REGROUPÉE portant trois lignes de brigades — ACCEPTÉE. Nomme-le de
    façon que l'exception soit lisible.
B4. Créneaux contigus, fin de l'une égale au début de l'autre — accepté.
B5. Séances du même instructeur sur des créneaux disjoints — accepté.

Groupe C — RG-35

C1. Instructeur non qualifié — refus, matière et instructeur nommés.
C2. Instructeur qualifié pour la matière du catalogue, via une AUTRE formation —
    ACCEPTÉ. La qualification est indépendante de la formation.

Groupe D — RG-36

D1. Séance recouvrant une indisponibilité — refus, période nommée.
D2. Bornes semi-ouvertes : séance finissant quand l'indisponibilité commence —
    accepté. Aligné sur US-INS-03.
D3. Indisponibilité d'un AUTRE instructeur — sans effet.

Groupe E — RG-37

E1. Lieu partagé occupé par une séance d'une autre brigade, créneau sécant —
    refus, séance occupante et brigade nommées.
E2. Capacité insuffisante pour l'effectif réel — refus, écart chiffré.
E3. Capacité EXACTEMENT égale à l'effectif — accepté. Décalage d'une unité.
E4. Matière SANS LIEU — aucun contrôle de lieu, accepté même si tous les lieux
    sont occupés.
E5. Salle attitrée dont la capacité est devenue insuffisante après croissance de
    l'effectif — détecté ici. C'est le rattrapage de la limite consignée à
    US-SES-03 ; nomme le test en conséquence.
E6. Capacité non renseignée — le comportement retenu au § 4, testé.
E7. Mode de partage séquentiel : deux brigades sur le même lieu au même créneau —
    refus même en cas de regroupement demandé.
E8. Regroupement sur un lieu simultané, capacité couvrant la SOMME des effectifs —
    accepté ; capacité insuffisante pour la somme — refus.

Groupe F — RG-38

F1. Séance sur une période bloquante de portée CENTRE ENTIER — refus.
F2. Séance sur une période bloquante ciblant SA session — refus.
F3. Séance sur une période bloquante ciblant SA brigade — refus.
F4. Séance sur une période bloquante ciblant UNE AUTRE brigade — ACCEPTÉE. C'est
    tout l'objet de RG-30 et l'exemple « EXAMIN FIN STAGE CAT/1 » du terrain.
F5. Période INFORMATIVE recouvrant le créneau — accepté.
F6. Recouvrement partiel de la période et du créneau — refus.

Groupe G — RG-39

G1. Volume programmé atteignant exactement le prescrit — une séance de plus est
    refusée, volumes chiffrés dans le message.
G2. Volume restant suffisant — accepté.
G3. Le programme EN COURS D'ÉVALUATION n'est pas compté contre lui-même
    (régénération). Test du point (a) du § 4.
G4. Le comportement retenu pour les brouillons, testé dans les deux sens.
G5. Prérequis non achevé — refus, matière prérequise nommée.
G6. Prérequis achevé — accepté.
G7. Matière sans prérequis — accepté sans contrôle.

Groupe H — contrat du service

H1. `verifier` N'ÉCRIT RIEN : compte les objets avant et après, sur un cas
    accepté ET sur un cas refusé.
H2. VIOLATIONS MULTIPLES : une candidate violant quatre règles retourne QUATRE
    violations, pas une. Test de E2 ; c'est celui qui tombe si quelqu'un ajoute
    un retour anticipé au premier refus.
H3. Chaque violation porte le code de règle et nomme l'élément en cause. Vérifie
    le CONTENU des messages, pas seulement leur présence.
H4. `verifier_lot` : deux candidates du lot prenant le même instructeur au même
    créneau — la seconde est refusée. Le test le plus important de la story ;
    sans lui, la génération produira des programmes invalides.
H5. `verifier_lot` : deux candidates compatibles — les deux acceptées.
H6. Performance : sur un jeu représentatif — plusieurs sessions, une dizaine de
    brigades, une semaine complète —, mesure le nombre de requêtes SQL d'un
    `verifier_lot`. Il doit être borné et indépendant du nombre de candidates.
    Reporte le chiffre ; il servira à l'analyse de R6.

Groupe I — garde mécanique et architecture

I1. Le test d'architecture du § 5 : aucun module hors le service d'écriture
    n'instancie ni ne sauvegarde `Seance` ou `LigneProgramme`.
I2. Toute écriture de séance passe par `ServiceContraintes` : vérifie qu'une
    tentative d'écriture violant une règle est refusée par le chemin de service.
I3. `tests/architecture` en entier, dépendances de `planification` comprises.
I4. Aucune classe au-delà de 200 lignes. Six règles dans un seul objet vont
    dépasser : découpe une règle par module ou par méthode dédiée avant d'y
    arriver.

## 9. Ce que cette story referme

Quatre reports du tableau suivi en revue se referment ici, par la seule existence
des modèles et des règles. VÉRIFIE CHACUN PAR UN TEST, jamais par déclaration —
D-50 a déclaré refermé un report qui ne l'était pas, et il a fallu quatre jours et
un lot de clôture pour s'en apercevoir.

- D-45, critère 4 d'US-INS-01 : « un instructeur affecté à un programme en
  cours ne peut être supprimé ». Le `PROTECT` sur `Seance.instructeur`.
- D-51, E1 d'US-INS-02 : « retrait de qualification impossible si séances
  futures » (RG-22). ATTENTION, le `PROTECT` NE SUFFIT PAS : il protège
  l'instructeur, pas la qualification. Retirer une qualification alors que des
  séances futures l'exploitent demande un contrôle explicite dans le service de
  qualification. Écris-le, ou dis clairement que le report reste ouvert — ne le
  déclare pas refermé par confusion avec D-45.
- D-54, volet séance : « un lieu affecté à une séance ne peut être supprimé ».
  Le `PROTECT` sur `Seance.lieu`.
- Critère 5 d'US-PLAN-01 et critère 4 d'US-INS-03 : périodes bloquantes et
  indisponibilités prises en compte comme contraintes. RG-38 et RG-36.

Restent ouverts et ne se referment PAS ici : D-34 et D-39 (contrainte de
catégorie de lieu et prérequis exploités par le moteur — la génération, donc
US-PLAN-03), D-35 volet séance, E2 et A3 d'US-PLAN-01.

Donne le compte à jour du tableau, à partir du compte vérifié sur le code dans
`AVANCEMENT.md` et non de celui annoncé en revue. C'est le premier point de
l'ordre du jour du 26 septembre.

## 10. Définition de fini

Implanté, testé, relu par le sous-agent, commité. Suite `pytest` complète verte.
Pas de vérification navigateur : aucun écran. `docs/suivi/CONTRAINTES-SOLVEUR.md`
produit (§ 7). Règle du garde mécanique inscrite dans `.claude/rules`.
`DECISIONS.md` à jour le jour même. Cases d'US-PLAN-04 cochées dans
`docs/suivi/sprint-2.md`, avec mention de l'inversion d'ordre.

## 11. Ce que tu ne touches pas

Le backlog, le cahier des charges, le registre des risques, le diagramme de
classes.

Les six règles elles-mêmes : elles sont marquées « Dure — contrainte » au tableau
des règles, et le livrable dit que les règles structurantes « proviennent du
terrain et ne doivent jamais être réinterprétées ». Si l'une te paraît fausse,
écris-le, ne l'ajuste pas.

## 12. Ce que tu me rends

- Comment tu as résolu la contrainte mutuelle des candidates d'un même lot (§ 3).
  C'est le point technique central de la story.
- Les deux arbitrages du § 4 : périmètre du volume programmé, définition
  opératoire du prérequis achevé.
- Le comportement retenu pour un lieu partagé sans capacité renseignée.
- Le nombre de requêtes SQL mesuré au test H6.
- Le décompte exact des reports refermés, avec le test qui le prouve pour chacun,
  et l'état de D-51 en particulier.
- `CONTRAINTES-SOLVEUR.md`.
- Les entrées `DECISIONS.md` : inversion de l'ordre des stories et pourquoi,
  `CASCADE` en composition stricte, structure du regroupement posée d'avance,
  définition provisoire du prérequis achevé et sa dette rattachée à RG-60, garde
  mécanique et sa règle.
- Le compte des tests par groupe et le total de la suite.
- Le temps réellement passé, à la demi-heure près, EN SIGNALANT la part qui
  relève des modèles déplacés depuis US-PLAN-03. Sans cette ventilation, les deux
  dernières mesures du sprint seront ininterprétables.